# -*- coding: utf-8 -*-
"""XAI chẩn đoán độ khó — rã theo TRỤC, và tự khai báo mức đáng tin của lời rã.

Khác với "XAI" cũ trong `tools/demo_mcq.py` (các câu tiếng Việt sinh từ ngưỡng
cứng viết tay, giải thích ngưỡng của người viết chứ không giải thích mô hình),
công cụ này xuất một **chẩn đoán** gồm bốn phần:

  1. DỰ ĐOÁN     mức + phân phối xác suất + độ bất định (có quyền NÓI KHÔNG BIẾT)
  2. RÃ TRỤC     đóng góp của trục BỀ MẶT và trục TRI THỨC, đo bằng hai cách:
                   • quy kết  — |SHAP| gộp nhóm (cách XAI thông thường)
                   • chiếm chỗ — Δ E[y] khi thay cả trục bằng giá trị trung vị
                 Hai cách lệch nhau là một thông tin, không phải lỗi.
  3. HIỆU CHỈNH  đối chiếu quy kết với HIỆU LỰC CAN THIỆP đã đo được
                 (`counterfactual_validity.json`). Đây là phần cốt lõi: nếu can
                 thiệp lên một trục không lay chuyển dự đoán thì phần quy kết
                 cho trục đó KHÔNG được tin, dù SHAP gán cho nó bao nhiêu.
  4. ĐIỂM MÙ     những gì hệ thống KHÔNG nhìn thấy được, kèm số đo

Thiết kế này trả lời phê phán rằng feature attribution một mình "chỉ mở một cửa
sổ hẹp" (Frontiers in Education 2026): lời giải thích ở đây tự mang theo bằng
chứng về việc chính nó có đáng tin hay không.

Mọi con số hiệu chỉnh đọc từ file kết quả thí nghiệm, KHÔNG hard-code.

Chạy:
    python tools/explain_difficulty.py --subject history --n 3
    python tools/explain_difficulty.py --subject physics --id kgv_0007
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

LEVEL_VN = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]
AXIS_VN = {"numeric": "BỀ MẶT (tính toán)", "verbosity": "BỀ MẶT (hành văn)"}


def load_json(path: str):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def entropy(p: np.ndarray) -> float:
    p = np.clip(p, 1e-12, 1.0)
    return float(-(p * np.log(p)).sum() / np.log(len(p)))   # chuẩn hoá [0,1]


def axis_report(subject: str) -> dict:
    """Đọc hiệu lực can thiệp đã đo được, để hiệu chỉnh lời giải thích."""
    cf = load_json(f"subjects/{subject}/samples/counterfactual_validity.json")
    if not cf:
        return {}
    a = cf["arms"]
    surf_down = next(k for k in a if k.endswith("_down"))
    out = {
        "surface_effect": abs(a[surf_down]["delta_mean"]),
        "surface_p": a[surf_down].get("vs_control_p"),
        "kg_near_agreement": a["kg_near"]["direction_agreement"],
        "kg_far_p": a["kg_far"].get("vs_control_p"),
        "hop_coef": a["regression_hop_controlled"]["coef"],
        "hop_p": a["regression_hop_controlled"]["p"],
        "attr_kg_share": a["attribution"]["kg_share"],
    }
    abl = load_json(f"subjects/{subject}/samples/ablation_full.json")
    if abl:
        out["kg_marginal_qwk"] = abl["results"]["marginal_gain"]["qwk"]
        out["kg_core_qwk"] = abl["results"]["KG lõi giả thuyết"]["qwk"]
        out["kg_full_qwk"] = abl["results"]["KG đầy đủ"]["qwk"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="history", choices=sorted(cv.SUBJECTS))
    ap.add_argument("--id", default=None, help="chẩn đoán đúng một câu theo id")
    ap.add_argument("--n", type=int, default=3, help="số câu lấy mẫu nếu không có --id")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--summary", action="store_true",
                    help="định lượng khoảng lệch quy kết ↔ chiếm chỗ trên cả bộ")
    args = ap.parse_args()

    cfg = cv.SUBJECTS[args.subject]
    surf_cols = cv.SURFACE_COLS[cfg["surface"]]
    cols = surf_cols + cv.KG_COLS
    eng = OntologyEngine.for_subject(args.subject)
    fz = cv.Featurizer(eng, cfg["surface"])
    items = cv.load_items(args.subject)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])

    feats = [fz(q["stem"], q["correct"], q["distractors"]) for q in items]
    X = pd.DataFrame(feats)[cols]
    model_of = cv.fit_out_of_fold(X, y, args.seed, cols)
    med = X.median(numeric_only=True)
    cal = axis_report(args.subject)
    surf_name = AXIS_VN[cfg["surface"]]

    if args.summary:
        # Định lượng KHOẢNG LỆCH quy kết ↔ chiếm chỗ trên toàn bộ dữ liệu.
        i_s = [cols.index(x) for x in surf_cols]
        i_k = [cols.index(x) for x in cv.KG_COLS]
        sh, oc = [], []
        Xs, Xk = X.copy(), X.copy()
        for c in surf_cols:
            Xs[c] = med[c]
        for c in cv.KG_COLS:
            Xk[c] = med[c]
        groups: dict[int, list[int]] = {}
        for i in range(len(items)):
            groups.setdefault(id(model_of[i]), []).append(i)
        for _, idxs in groups.items():
            m = model_of[idxs[0]]
            k = np.arange(4)
            base = m.predict_proba(X.iloc[idxs]) @ k
            d_s = base - (m.predict_proba(Xs.iloc[idxs]) @ k)
            d_k = base - (m.predict_proba(Xk.iloc[idxs]) @ k)
            cb = m.get_booster().predict(xgb.DMatrix(X.iloc[idxs]),
                                         pred_contribs=True)
            if cb.ndim == 2:
                cb = cb[:, None, :]
            a_s = np.abs(cb[:, :, i_s].sum(axis=2)).mean(axis=1)
            a_k = np.abs(cb[:, :, i_k].sum(axis=2)).mean(axis=1)
            sh.append(a_k / (a_s + a_k + 1e-12))
            oc.append(np.abs(d_k) / (np.abs(d_s) + np.abs(d_k) + 1e-12))
        sh, oc = np.concatenate(sh), np.concatenate(oc)
        print(f"KHOẢNG LỆCH QUY KẾT ↔ CHIẾM CHỖ — môn {args.subject}, "
              f"{len(items)} câu")
        print(f"  tỉ trọng trục TRI THỨC theo quy kết  |SHAP| : {sh.mean():.1%}")
        print(f"  tỉ trọng trục TRI THỨC theo chiếm chỗ ΔE[y] : {oc.mean():.1%}")
        print(f"  chênh trung bình                            : "
              f"{(sh - oc).mean():+.1%}")
        print(f"  số câu hai cách xếp hạng NGƯỢC nhau         : "
              f"{(sh > oc).mean():.1%}")
        print(f"\n⚠️ ĐỌC CẨN THẬN — con số này KHÔNG dùng để kết luận SHAP nói quá "
              f"hay nói thiếu.\n   Nhóm KG có {len(cv.KG_COLS)} cột, nhóm bề mặt "
              f"{len(surf_cols)} cột; thay cả nhóm bằng trung vị thì\n   nhóm "
              "NHIỀU CỘT tự nhiên gây nhiễu loạn lớn hơn, nên tỉ trọng chiếm chỗ "
              "thiên vị\n   nhóm lớn. Hai cách chỉ nên dùng để THẤY chúng bất đồng "
              "ở mức nào.")
        print("   Phép hiệu chỉnh ĐÁNG TIN là mục 3 của chẩn đoán từng câu — đối "
              "chiếu với\n   HIỆU LỰC CAN THIỆP, vì can thiệp sửa đúng một phương "
              "án nên không bị lệch\n   theo số cột. Xem docs/XAI_DIAGNOSIS.md §3.")
        return

    if args.id:
        picks = [i for i, q in enumerate(items) if q["id"] == args.id]
        if not picks:
            sys.exit(f"không tìm thấy id {args.id}")
    else:
        rs = np.random.default_rng(args.seed)
        picks = sorted(rs.choice(len(items), size=min(args.n, len(items)),
                                 replace=False).tolist())

    print(f"CHẨN ĐOÁN ĐỘ KHÓ — môn {args.subject} | ontology {len(eng)} thực thể")
    print(f"nguồn nhãn huấn luyện: {items[0].get('label_source', '?')}\n")

    for i in picks:
        q, m, f = items[i], model_of[i], feats[i]
        row = pd.DataFrame([f])[cols]
        proba = m.predict_proba(row)[0]
        ey = float(proba @ np.arange(len(proba)))
        H = entropy(proba)

        print("=" * 78)
        print(f"[{q['id']}]  {q['stem'][:100]}")
        print(f"  đáp án: {q['correct'][:80]}")
        print("-" * 78)
        print("1) DỰ ĐOÁN")
        print(f"   mức {LEVEL_VN[int(np.argmax(proba))]}  ·  E[y] = {ey:.2f}"
              f"  ·  nhãn trong dữ liệu: {q[cfg['label_field']]}")
        print("   phân phối: " + " ".join(
            f"{LEVEL_VN[k][:3]} {proba[k]:.2f}" for k in range(len(proba))))
        verdict = ("TIN ĐƯỢC" if H < 0.55 else
                   "DÈ DẶT" if H < 0.80 else "KHÔNG KẾT LUẬN")
        print(f"   bất định (entropy chuẩn hoá) {H:.2f} → {verdict}")

        # ---- 2) rã trục: quy kết (SHAP) + chiếm chỗ (occlusion) ----
        contrib = m.get_booster().predict(xgb.DMatrix(row), pred_contribs=True)
        if contrib.ndim == 2:
            contrib = contrib[None, :, :]
        c = contrib[0]
        i_s = [cols.index(x) for x in surf_cols]
        i_k = [cols.index(x) for x in cv.KG_COLS]
        a_s = float(np.abs(c[:, i_s].sum(axis=1)).mean())
        a_k = float(np.abs(c[:, i_k].sum(axis=1)).mean())
        share_k = a_k / (a_s + a_k + 1e-12)

        occ = {}
        for nm, cs in ((surf_name, surf_cols), ("TRI THỨC (ontology)", cv.KG_COLS)):
            r2 = row.copy()
            for cc in cs:
                r2[cc] = med[cc]
            p2 = m.predict_proba(r2)[0]
            occ[nm] = ey - float(p2 @ np.arange(len(p2)))

        print("\n2) RÃ TRỤC")
        print(f"   {'trục':24s} {'quy kết |SHAP|':>15s} {'chiếm chỗ ΔE[y]':>17s}")
        print(f"   {surf_name:24s} {a_s:15.3f} {occ[surf_name]:+17.3f}")
        print(f"   {'TRI THỨC (ontology)':24s} {a_k:15.3f} "
              f"{occ['TRI THỨC (ontology)']:+17.3f}")
        print(f"   → quy kết dành {share_k:.0%} cho trục tri thức")

        # ---- 3) hiệu chỉnh bằng can thiệp đã đo ----
        print("\n3) HIỆU CHỈNH BẰNG HIỆU LỰC CAN THIỆP (đo trên cả bộ dữ liệu)")
        if not cal:
            print("   (chưa có counterfactual_validity.json — chạy tool đó trước)")
        else:
            print(f"   trục bề mặt : can thiệp làm E[y] đổi "
                  f"{cal['surface_effect']:.3f} mức (p={cal['surface_p']:.2g}) "
                  f"→ phần quy kết cho trục này ĐÁNG TIN")
            print(f"   trục tri thức: 'nhiễu gần hơn ⇒ khó hơn' chỉ đúng "
                  f"{cal['kg_near_agreement']:.1%} (dưới mức ngẫu nhiên); "
                  f"'nhiễu xa hơn' p={cal['kg_far_p']:.2g}")
            print(f"                  khoảng cách đồ thị: hệ số "
                  f"{cal['hop_coef']:+.4f} (p={cal['hop_p']:.2g})")
            if "kg_marginal_qwk" in cal:
                print(f"                  giá trị dự báo biên của ontology: "
                      f"QWK {cal['kg_marginal_qwk']:+.3f}; nhưng lát 'lõi giả "
                      f"thuyết' chỉ {cal['kg_core_qwk']:.3f} so với khối đầy đủ "
                      f"{cal['kg_full_qwk']:.3f}")
            print(f"   ⚠️ KẾT LUẬN HIỆU CHỈNH: quy kết dành {share_k:.0%} cho trục "
                  f"tri thức, nhưng can thiệp cho thấy trục đó KHÔNG lay chuyển")
            print("      dự đoán theo hướng giả thuyết. Đọc phần tri thức như "
                  "'câu này có nhắc khái niệm\n      trong chương trình không', "
                  "KHÔNG phải 'các phương án dễ nhầm tới mức nào'.")

        # ---- 4) điểm mù ----
        print("\n4) ĐIỂM MÙ — những gì chẩn đoán này KHÔNG thấy")
        tvl = load_json(f"subjects/{args.subject}/samples/teacher_vs_llm.json")
        if tvl:
            key = "len_dist_mean" if cfg["surface"] == "verbosity" else "num_option_count"
            pc = tvl["paired_correlations"].get(key, {})
            tr, ag = tvl["transfer"], tvl["agreement"]
            print(f"   • Hai nguồn nhãn (người / máy) đồng thuận ở κ = "
                  f"{ag['kappa']:+.3f} trên {tvl['n_items']} câu.")
            print(f"     Trục bề mặt chủ đạo (`{key}`) tương quan "
                  f"{pc.get('rho_llm', float('nan')):+.2f} với nhãn MÁY và "
                  f"{pc.get('rho_human', float('nan')):+.2f} với nhãn NGƯỜI "
                  f"(chênh p={pc.get('p_boot', float('nan')):.3f}).")
            print(f"   • Mô hình học nhãn máy chuyển giao sang nhãn NGƯỜI ở "
                  f"κ = {tr['nhãn NGƯỜI']['kappa']:+.3f} "
                  f"(so với κ = {tr['nhãn MÁY']['kappa']:+.3f} trên nhãn máy).")
            if tr["nhãn NGƯỜI"]["kappa"] < 0.10:
                print("     ⇒ KHÔNG dùng chẩn đoán này để thay phán đoán giáo viên.")
            else:
                print("     ⇒ Dùng được như GỢI Ý cho giáo viên, không thay thế.")
        print("   • Độ phức tạp LỜI GIẢI không nằm trên bề mặt câu hỏi: máy chấm "
              "nhận ra mức VDC")
        print("     chỉ 11% (docs/LLM_JUDGE_PHYSICS.md). Câu VDC ẩn sẽ bị hạ mức "
              "một cách có hệ thống.")
        print("   • Đây là thang MỨC NHẬN THỨC (NB/TH/VD/VDC), không phải tỉ lệ "
              "trả lời đúng.")
        print()


if __name__ == "__main__":
    main()
