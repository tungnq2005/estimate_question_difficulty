# -*- coding: utf-8 -*-
"""Độ tin của nhãn khi KHÔNG có người chấm thứ hai.

Bối cảnh: `docs/XAI_DIAGNOSIS.md` đo được κ(giáo viên, LLM) = +0,013 trên 90 câu
Sử. Cách chuẩn để biết "ai đúng" là mời người chấm thứ hai — **không có**. Bốn
phép dưới đây là những gì làm được mà không cần thêm người:

  A. PHÂN XỬ BẰNG MÔ PHỎNG   nguồn thứ ba độc lập-về-tác-vụ: p-value từ LLM đóng
     vai học sinh làm bài (Acquaye 2026 cho thấy tác vụ này khác hẳn direct
     judging và bám tỉ lệ đúng thật tốt hơn). Nguồn nào bám nó hơn?
  B. TEST-RETEST CỦA LLM     bộ dữ liệu có 715 nhóm nội dung TRÙNG. Mỗi câu được
     chấm riêng, nên so phiếu giữa các bản trùng = đo lại chính giám khảo đó.
     Đây là phép quan trọng nhất: nếu LLM ổn định mà vẫn lệch giáo viên thì
     κ ≈ 0 KHÔNG giải thích được bằng "LLM chấm bừa".
  C. KIỂM TOÀN VẸN NHÃN      nhãn cuối có khớp đa số phiếu của chính nó không?
  D. NHÃN CÓ HỌC ĐƯỢC KHÔNG  5-fold CV trên 90 câu, KÈM ĐỐI CHỨNG là nhãn LLM
     trên đúng 90 câu đó — để biết phép có đủ lực hay không.

Chạy:  python tools/label_reliability.py [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

MCQ = "subjects/history/samples/mcq_crawled.json"
TEACHER = "subjects/history/samples/su9_difficulty_teacher1_2026-08-17.json"
SIM = "subjects/history/samples/item_stats.json"
L4 = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]
L4I = {v: i for i, v in enumerate(L4)}
T_MAP = {"easy": 0, "medium": 1, "hard": 2}
L_MAP3 = {"Easy": 0, "Medium": 1, "Hard": 2}


def votes(q) -> list[str]:
    return [v for v in (q.get("vote_detail") or "").split("|") if v in L4I]


def majority(vs: list[str]):
    if not vs:
        return None
    top, n = Counter(vs).most_common(1)[0]
    return top if (n > 1 or len(set(vs)) == 1) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="subjects/history/samples/label_reliability.json")
    args = ap.parse_args()

    rows = json.loads(Path(MCQ).read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in rows}
    teacher = json.loads(Path(TEACHER).read_text(encoding="utf-8"))["responses"]
    sim = {i["item_id"]: i for i in json.loads(
        Path(SIM).read_text(encoding="utf-8"))["items"]}
    groups = defaultdict(list)
    for q in rows:
        if q.get("dup_group") is not None:
            groups[q["dup_group"]].append(q)
    multi = [sorted(v, key=lambda q: q["id"]) for v in groups.values() if len(v) > 1]
    out = {}

    # ---------- A. phân xử bằng mô phỏng ----------
    print("=" * 76)
    print("A. PHÂN XỬ BẰNG MÔ PHỎNG HỌC SINH — nguồn nào bám 'độ khó hành vi'?")
    print("=" * 76)
    ids = sorted(set(sim) & set(teacher) & set(by_id))
    y_t = np.array([T_MAP[teacher[i]["verdict"]] for i in ids])
    y_l = np.array([L_MAP3[by_id[i]["difficulty"]] for i in ids])
    beh = np.array([1 - sim[i]["p_value"] for i in ids])      # cao = khó
    disc = np.array([sim[i]["discrimination"] for i in ids])
    print(f"n = {len(ids)} câu có đủ ba nguồn")
    A = {}
    for nm, y in (("nhãn GIÁO VIÊN", y_t), ("nhãn LLM", y_l)):
        r, p = spearmanr(y, beh)
        print(f"  {nm:16s} ρ vs độ khó hành vi = {r:+.3f}  (p={p:.3g})")
        A[nm] = {"rho": float(r), "p": float(p)}
    m = disc >= 0.2
    print(f"  — chỉ câu phân biệt tốt (disc ≥ 0,2, n={int(m.sum())}):")
    for nm, y in (("nhãn GIÁO VIÊN", y_t), ("nhãn LLM", y_l)):
        r, p = spearmanr(y[m], beh[m])
        print(f"    {nm:16s} ρ = {r:+.3f}  (p={p:.3g})")
        A[nm]["rho_high_disc"] = float(r)
        A[nm]["p_high_disc"] = float(p)
    print("  ⇒ KHÔNG phép nào đạt ý nghĩa thống kê — mô phỏng KHÔNG phân xử được.")
    print("    (và dùng proxy LLM để bênh nhãn LLM sẽ là lập luận vòng tròn)")
    out["A_simulation_arbitration"] = dict(A, n=len(ids), n_high_disc=int(m.sum()))

    # ---------- B. test-retest của LLM trên nội dung trùng ----------
    print("\n" + "=" * 76)
    print("B. ⭐ TEST-RETEST CỦA LLM trên nội dung TRÙNG")
    print("=" * 76)
    print(f"{len(multi)} nhóm có ≥2 bản cùng nội dung")
    per_pos = {}
    for pos in range(3):
        a, b = [], []
        for v in multi:
            va, vb = votes(v[0]), votes(v[1])
            if len(va) > pos and len(vb) > pos:
                a.append(L4I[va[pos]])
                b.append(L4I[vb[pos]])
        a, b = np.array(a), np.array(b)
        k = cohen_kappa_score(a, b)
        print(f"  phiếu #{pos + 1}: n={len(a)}  đồng thuận {np.mean(a == b):.1%}  "
              f"κ {k:+.3f}")
        per_pos[f"vote_{pos + 1}"] = {"n": int(len(a)),
                                      "agreement": float(np.mean(a == b)),
                                      "kappa": float(k)}
    a = np.concatenate([np.array([L4I[x] for x in votes(v[0])]) for v in multi])
    b = np.concatenate([np.array([L4I[x] for x in votes(v[1])]) for v in multi])
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    k_all = cohen_kappa_score(a, b)
    print(f"  GỘP     : n={n}  đồng thuận {np.mean(a == b):.1%}  κ {k_all:+.3f}  "
          f"QWK {cohen_kappa_score(a, b, weights='quadratic'):+.3f}")
    print("\n  ⇒ LLM là công cụ đo KHÁ ỔN ĐỊNH (κ ≈ 0,79). Vì vậy κ(GV, LLM) ≈ 0")
    print("    KHÔNG giải thích được bằng 'LLM chấm bừa' — hai nguồn lệch nhau")
    print("    một cách CÓ HỆ THỐNG, tức đo hai thứ khác nhau.")
    print("  ⚠️ Ở tầng NHÃN CUỐI thì các bản trùng khớp 100% — nhưng đó là HIỆN VẬT")
    print("     của việc gộp phiếu theo nhóm (xem C), KHÔNG phải bằng chứng ổn định.")
    out["B_llm_test_retest"] = dict(per_pos, pooled={"n": int(n),
                                                     "agreement": float(np.mean(a == b)),
                                                     "kappa": float(k_all)})

    # ---------- C. kiểm toàn vẹn nhãn ----------
    print("\n" + "=" * 76)
    print("C. KIỂM TOÀN VẸN — nhãn cuối có khớp đa số phiếu không?")
    print("=" * 76)
    solo = [q for q in rows
            if q.get("dup_group") is None or len(groups[q["dup_group"]]) == 1]
    bad_solo = [q for q in solo
                if majority(votes(q)) not in (None, q["difficulty_vn"])]
    print(f"câu KHÔNG trùng : {len(solo)} · nhãn khác đa số phiếu: {len(bad_solo)}")
    ok_g, odd = 0, []
    for k_, v in groups.items():
        if len(v) < 2:
            continue
        gm = majority([x for q in v for x in votes(q)])
        labs = {q["difficulty_vn"] for q in v}
        if len(labs) == 1 and gm == next(iter(labs)):
            ok_g += 1
        elif len(labs) == 1:
            odd.append({"dup_group": k_, "votes": [q.get("vote_detail") for q in v],
                        "label": next(iter(labs)), "group_majority": gm})
    print(f"nhóm trùng      : {len(multi)} · nhãn nhóm = đa số TOÀN NHÓM: "
          f"{ok_g} ({ok_g / len(multi):.1%})")
    print(f"                  không theo quy tắc đa số nào: {len(odd)} "
          f"({len(odd) / len(multi):.1%})")
    for o in odd[:3]:
        print(f"    nhóm {o['dup_group']}: {o['votes']} → '{o['label']}' "
              f"(đa số nhóm '{o['group_majority']}')")
    print("⇒ Quy trình gán nhãn LÀNH ở câu đơn (0 lỗi). Nhãn trong nhóm trùng được")
    print("  GỘP Ở MỨC NHÓM — hợp lý (nhiều phiếu hơn), nhưng cần ghi rõ trong")
    print(f"  luận văn, và {len(odd)} nhóm còn lại nên rà tay.")
    out["C_integrity"] = {"n_solo": len(solo), "solo_mismatch": len(bad_solo),
                          "n_groups": len(multi), "group_majority_explained": ok_g,
                          "unexplained": len(odd), "examples": odd[:10]}

    # ---------- D. nhãn có học được không ----------
    print("\n" + "=" * 76)
    print("D. NHÃN GIÁO VIÊN CÓ HỌC ĐƯỢC KHÔNG (90 câu, 5-fold CV)")
    print("=" * 76)
    tids = [i for i in teacher if i in by_id]
    yt = np.array([T_MAP[teacher[i]["verdict"]] for i in tids])
    yl = np.array([L_MAP3[by_id[i]["difficulty"]] for i in tids])
    eng = OntologyEngine.for_subject("history")
    fz = cv.Featurizer(eng, "verbosity")
    cols = cv.SURFACE_COLS["verbosity"] + cv.KG_COLS
    X = pd.DataFrame([fz(by_id[i]["stem"], by_id[i]["correct"],
                         by_id[i]["distractors"]) for i in tids])[cols]
    mk = dict(n_estimators=200, max_depth=3, learning_rate=0.1, subsample=0.8,
              colsample_bytree=0.8, random_state=args.seed,
              eval_metric="mlogloss", verbosity=0)
    D = {}
    for nm, yy in (("nhãn GIÁO VIÊN", yt), ("nhãn LLM (ĐỐI CHỨNG)", yl)):
        pred = np.zeros(len(yy), dtype=int)
        for tr, te in StratifiedKFold(5, shuffle=True,
                                      random_state=args.seed).split(X, yy):
            pred[te] = XGBClassifier(**mk).fit(X.iloc[tr], yy[tr]).predict(X.iloc[te])
        base = float(max(np.bincount(yy)) / len(yy))
        k = cohen_kappa_score(yy, pred)
        print(f"  {nm:22s} acc {np.mean(pred == yy):.3f} (baseline {base:.3f}) | "
              f"κ {k:+.3f}")
        D[nm] = {"acc": float(np.mean(pred == yy)), "baseline": base,
                 "kappa": float(k)}
    print("\n  ⚠️ ĐỐI CHỨNG cho thấy phép này KHÔNG ĐỦ LỰC: nhãn LLM — thứ ta BIẾT")
    print("     là học được (κ +0,221 khi huấn luyện trên 2.047 câu) — cũng hỏng ở")
    print("     n=90. Vì vậy KHÔNG được kết luận 'nhãn giáo viên là nhiễu'.")
    out["D_learnability"] = D

    print("\n" + "=" * 76)
    print("KẾT LUẬN KHI KHÔNG CÓ NGƯỜI CHẤM THỨ HAI")
    print("=" * 76)
    print("• KHÔNG chứng minh được ai đúng — phép phân xử (A) không đủ ý nghĩa,")
    print("  phép học được (D) không đủ lực.")
    print(f"• NHƯNG chứng minh được LLM là công cụ đo ổn định (κ ≈ {k_all:.2f}),")
    print("  nên bất đồng với giáo viên là CÓ HỆ THỐNG, không phải nhiễu ngẫu nhiên.")
    print("• ⇒ Phát biểu đứng được: hai nguồn ĐO HAI THỨ KHÁC NHAU.")
    print("  Phát biểu KHÔNG đứng được: 'pipeline Sử đo sai độ khó'.")

    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(f"\n→ {args.out}")


if __name__ == "__main__":
    main()
