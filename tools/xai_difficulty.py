# -*- coding: utf-8 -*-
"""XAI GIẢI THÍCH ĐỘ KHÓ — pipeline 5 bước, dẫn bằng CAN THIỆP chứ không bằng quy kết.

Vì sao không dùng thẳng SHAP: trong chính bộ dữ liệu này, tương quan giữa
"SHAP gán bao nhiêu cho một trục" và "can thiệp lên trục đó làm dự đoán đổi bao
nhiêu" là rho = -0,043 / -0,090 / -0,051 / +0,005 (đều n.s.). Quy kết và phản
ứng thật gần như độc lập. Nên lời giải thích ở đây được dựng từ can thiệp.

  B1  CHỨNG CHỈ TRỤC           quần thể — trục nào ĐƯỢC PHÉP nêu tên
  B2  CAN THIỆP TỪNG CÂU       sửa 1 phương án thật, lặp R lần, đo |Δ E[y]|
  B3  NGƯỠNG NHIỄU RIÊNG CÂU   nhánh giả dược trên CHÍNH câu đó → sàn nhiễu
  B4  QUY KẾT CÓ KIỂM CHỨNG    (B2 − B3) chuẩn hoá; SHAP chỉ để đối chiếu
  B5  PHÁT NGÔN                lời tiếng Việt + quyền nói KHÔNG QUY ĐƯỢC

  --validate   kiểm tra chéo: chia R lần lặp làm hai nửa, hỏi xem lời giải
               thích có LẶP LẠI được không, và SHAP có dự báo được phản ứng
               thật ở nửa còn lại không.

Chạy:
    python tools/xai_difficulty.py --step 1 --subject physics
    python tools/xai_difficulty.py --step 2 --subject physics --n 5
    python tools/xai_difficulty.py --step 5 --subject history_gv --n 3
    python tools/xai_difficulty.py --validate --subject physics --n 120
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.stats import spearmanr, ttest_rel

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

LEVEL_VN = ["Nhận biết", "Thông hiểu", "Vận dụng", "Vận dụng cao"]

# Hai trục can thiệp được BẰNG VĂN BẢN. Mỗi trục có nhánh can thiệp và nhánh
# đối chứng KHỚP của riêng nó — đối chứng phải giống can thiệp ở mọi mặt trừ
# đúng cái mình muốn đo, nếu không thì hiệu số vô nghĩa.
AXES = {
    "BỀ MẶT": {
        "arms": {"numeric": ["num_down", "num_up"],
                 "verbosity": ["len_down", "len_up"]},
        "control": "placebo",
        "means": {"numeric": "số phương án có chứa con số",
                  "verbosity": "độ dài / lượng chữ của phương án"},
    },
    "TRI THỨC": {
        "arms": {"numeric": ["kg_near", "kg_far"],
                 "verbosity": ["kg_near", "kg_far"]},
        "control": "placebo_ent",
        "means": {"numeric": "khoảng cách trên đồ thị tri thức giữa nhiễu và đáp án",
                  "verbosity": "khoảng cách trên đồ thị tri thức giữa nhiễu và đáp án"},
    },
}
PROMISE = {"num_down": -1, "num_up": +1, "len_down": -1, "len_up": +1,
           "kg_near": +1, "kg_far": -1, "placebo": 0, "placebo_ent": 0}


def entropy(p):
    p = np.clip(np.asarray(p, float), 1e-12, 1.0)
    return float(-(p * np.log(p)).sum() / np.log(len(p)))


def load_json(path):
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# ======================================================================
# B1 — CHỨNG CHỈ TRỤC
# ======================================================================
SANITY_PATH = f"docs/xai_sanity{cv.BACKEND_SUFFIX}.json"
MIN_PERM = 20      # dưới 20 mô hình xáo thì p hoán vị không thể < 0,05

# CỔNG ĐANG DÙNG cho lời giải thích từng câu — "arms" (THEO NHÁNH), chốt
# 11/09/2026 sau kiểm tra tỉnh táo (tools/xai_sanity.py, K = 39):
#   legacy  một nhánh bất kỳ, Wilcoxon + đúng hướng — cấp chứng chỉ cho 30/39
#           (Lý), 27/39 (Sử) mô hình học trên NHÃN XÁO → không đủ làm cổng.
#   iut     mọi nhánh của trục đạt hiệu chỉnh — định ra trước khi chạy K = 39;
#           cấp nhầm 0/39 nhưng môn Lý mất chứng chỉ, môn Sử chỉ đạt 1/4 seed.
#   arms    chỉ những NHÁNH đạt hiệu chỉnh ở MỌI seed đã chạy mới được góp vào
#           lời giải thích; trục được nêu tên khi có ít nhất một nhánh như vậy.
#           Chọn SAU khi thấy số — phải khai báo như vậy khi viết. Cấp nhầm từng
#           nhánh 0–1/39. Kết quả: Lý chỉ `num_down`, Sử chỉ `len_down`.
# Cả ba phán quyết đều được tính và trả về ở mọi lần gọi certificate().
GATE = "arms"


def certificate(subject: str, cf: dict | None = None,
                null: dict | None = None) -> dict:
    """Trục nào đã CHỨNG MINH được là lay chuyển dự đoán ở mức quần thể.

    Một trục chỉ được phép xuất hiện trong lời giải thích từng câu nếu ở đây
    nó vượt được nhánh ĐỐI CHỨNG KHỚP của chính nó. Đây là cái cổng: nó ngăn
    hệ thống nói "câu này khó vì tri thức" khi trục tri thức chưa bao giờ
    chứng minh được là có tác dụng.

    Ba phán quyết, tính ở mọi lần gọi (xem `tools/xai_sanity.py`):
      certified_legacy  ÍT NHẤT MỘT nhánh (1) vượt đối chứng khớp ở p < 0,05
                        (Wilcoxon ghép cặp) và (2) dịch ĐÚNG HƯỚNG đã hứa TRƯỚC
                        khi đo. Luật gốc — TRƯỢT kiểm tra tỉnh táo.
      certified_arms    các nhánh đạt (1) + (2) + (3): hiệu ứng theo hướng hứa
                        lớn hơn hiệu ứng của mô hình học trên NHÃN XÁO, ở p
                        hoán vị < 0,05.
      certified_iut     MỌI nhánh của trục nằm trong certified_arms.
      gated_arms        certified_arms còn đạt ở MỌI seed của kiểm tra tỉnh
                        táo (chỉ tính khi đọc file chuẩn) — cổng "arms" dùng.
    `certified` = phán quyết của cổng đang dùng (hằng `GATE`).

    `cf` cho trước → chấm trên kết quả phản thực đó thay vì file chuẩn của môn.
    `null` = {nhánh: [chênh-đối-chứng của các mô hình nhãn xáo]}; None → đọc
    từ docs/xai_sanity.json nếu có; {} hoặc < MIN_PERM mô hình → bỏ điều (3).
    """
    if cf is None:
        cf = load_json(cv.out_path(subject, "counterfactual_validity"))
    if not cf:
        return {}
    robust = None       # nhánh đạt ở MỌI seed — chỉ có nghĩa với file chuẩn
    if null is None:
        try:
            san = (load_json(SANITY_PATH) or {}).get(subject, {})
        except Exception:
            san = {}
        null = san.get("null", {})
        robust = san.get("robust_arms")
    arms, surf = cf["arms"], cv.SUBJECTS[subject]["surface"]
    out = {"n_items": cf["n_items"], "axes": {}, "calibrated": False}
    for name, spec in AXES.items():
        rows = []
        for a in spec["arms"][surf]:
            if a not in arms:
                continue
            r = arms[a]
            d, p = r.get("vs_control_diff"), r.get("vs_control_p")
            # (1)+(2): hướng được hứa TRƯỚC khi đo, không chọn sau khi thấy số
            wil = bool(p is not None and p < 0.05 and d is not None
                       and np.sign(d) == r["promise"])
            nl = null.get(a) or []
            p_perm = None
            if len(nl) >= MIN_PERM and d is not None:
                t = r["promise"] * d
                p_perm = (1 + sum(r["promise"] * x >= t for x in nl)) / (len(nl) + 1)
                out["calibrated"] = True
            ok = wil and (p_perm < 0.05 if p_perm is not None else True)
            rows.append({"arm": a, "n": r["n"], "promise": r["promise"],
                         "delta": r["delta_mean"], "vs_control": d, "p": p,
                         "p_perm": p_perm, "n_perm": len(nl),
                         "agree": r["direction_agreement"],
                         "control": r.get("control_arm", spec["control"]),
                         "ok_wilcoxon": wil, "ok": bool(ok)})
        legacy = any(r["ok_wilcoxon"] for r in rows)
        iut = bool(rows) and all(r["ok"] for r in rows)
        c_arms = [r["arm"] for r in rows if r["ok"]]
        # cổng "arms": nhánh phải đạt ở lần chạy này VÀ ở mọi seed kiểm tra tỉnh táo
        g_arms = [a for a in c_arms if robust is None or a in robust]
        out["axes"][name] = {
            "arms": rows,
            "certified_legacy": legacy,
            "certified_iut": iut,
            "certified_arms": c_arms,
            "gated_arms": g_arms,
            "certified": {"legacy": legacy, "iut": iut,
                          "arms": bool(g_arms)}[GATE],
            "means": spec["means"][surf]}
    out["gate"] = GATE
    fa = arms.get("faithfulness", {})
    out["faithfulness"] = {k: {"rho": v["spearman"], "p": v["p"]}
                           for k, v in fa.items()}
    out["shap_kg_share"] = arms.get("attribution", {}).get("kg_share")
    return out


def print_certificate(subject, cert):
    cfg = cv.SUBJECTS[subject]
    print("=" * 78)
    print(f"B1 · CHỨNG CHỈ TRỤC — môn {subject} | nhãn {cfg.get('label_by','?')}")
    print("=" * 78)
    if not cert:
        print("  chưa có counterfactual_validity — chạy tool đó trước.")
        return
    print(f"  {cert['n_items']} câu · mỗi can thiệp thay ĐÚNG MỘT phương án nhiễu")
    print("  bằng một nhiễu THẬT lấy từ câu khác, rồi đo E[y] dịch bao nhiêu MỨC.")
    print(f"  cổng đang dùng: {cert.get('gate')} "
          f"({'đã' if cert.get('calibrated') else 'CHƯA'} hiệu chỉnh bằng mô hình "
          f"nhãn xáo — xem tools/xai_sanity.py)")
    for name, ax in cert["axes"].items():
        mark = "ĐẠT" if ax["certified"] else "KHÔNG ĐẠT"
        if ax["certified"] and cert.get("gate") == "arms":
            mark += " — chỉ nhánh " + ", ".join(ax["gated_arms"])
        print(f"\n  ── trục {name}  [{mark}]")
        print(f"     đo bằng: {ax['means']}")
        print(f"     {'nhánh':13s}{'n':>6s}{'hứa':>5s}{'Δ E[y]':>10s}"
              f"{'vượt đối chứng':>17s}{'p':>10s}{'p hoán vị':>11s}"
              f"{'đúng hướng':>12s}")
        for r in ax["arms"]:
            vc = "n/a" if r["vs_control"] is None else f"{r['vs_control']:+.4f}"
            pp = "n/a" if r["p"] is None else f"{r['p']:.2g}"
            pq = "n/a" if r.get("p_perm") is None else f"{r['p_perm']:.3f}"
            print(f"     {r['arm']:13s}{r['n']:6d}{r['promise']:+5d}"
                  f"{r['delta']:+10.4f}{vc:>17s}{pp:>10s}{pq:>11s}"
                  f"{r['agree']:11.1%}")
    print("\n  ĐỌC THẾ NÀO: cột có nghĩa là 'vượt đối chứng', không phải Δ E[y].")
    print("  Thay một phương án bao giờ cũng làm dự đoán nhúc nhích; phải trừ đi")
    print("  nhánh giả dược (thay phương án nhưng KHÔNG đụng vào trục) thì phần")
    print("  còn lại mới là tác dụng của trục.")
    if cert.get("faithfulness"):
        print("\n  ── vì sao KHÔNG dẫn bằng SHAP")
        print(f"     {'nhánh can thiệp':17s}{'rho(SHAP, phản ứng thật)':>27s}{'p':>9s}")
        for k, v in cert["faithfulness"].items():
            print(f"     {k:17s}{v['rho']:+27.3f}{v['p']:9.3f}")
        print("     Quy kết SHAP gần như KHÔNG dự báo được phản ứng thật của chính")
        print("     mô hình đó. Nên từ B2 trở đi, lời giải thích dựng từ can thiệp.")


# ======================================================================
# B0 — bối cảnh dùng chung cho B2..B5
# ======================================================================
class Ctx:
    def __init__(self, subject, seed):
        cfg = cv.SUBJECTS[subject]
        self.subject, self.cfg, self.seed = subject, cfg, seed
        self.surf = cfg["surface"]
        self.surf_cols = cv.SURFACE_COLS[self.surf]
        # cols = đầu vào của MÔ HÌNH (backend văn bản gắn thêm cột số hiệu văn
        # bản); surf_cols + KG_COLS vẫn là bộ cột DIỄN GIẢI ĐƯỢC, dùng cho
        # blame_columns và quy kết theo khối.
        self.cols = cv.model_cols(self.surf)
        self.eng = OntologyEngine.for_subject(cv.ontology_of(subject))
        self.fz = cv.Featurizer(self.eng, self.surf)
        self.items = cv.load_items(subject)
        self.y = np.array([cfg["label_map"][q[cfg["label_field"]]]
                           for q in self.items])
        self.feats = [self.fz(q["stem"], q["correct"], q["distractors"])
                      for q in self.items]
        self.X = pd.DataFrame(self.feats)[self.cols]
        self.model_of = cv.fit_out_of_fold(self.X, self.y, seed, self.cols)
        self.hops = cv.all_pairs_hops(self.eng)
        self.pool = cv.DonorPool(self.items, self.fz)
        self.curis = [{e.uri for e in self.fz.entities(q["correct"])}
                      for q in self.items]
        self.index = {q["id"]: i for i, q in enumerate(self.items)}

    def ey(self, i, rows):
        """E[y] cho một loạt hàng đặc trưng, dùng ĐÚNG mô hình out-of-fold của câu i.

        Quan trọng: câu i chưa từng nằm trong tập huấn luyện của mô hình đó,
        nên phản ứng đo được không phải là mô hình đang nhớ lại chính nó.
        """
        p = self.model_of[i].predict_proba(pd.DataFrame(rows)[self.cols])
        return p @ np.arange(p.shape[1])


# ======================================================================
# B2 + B3 — can thiệp từng câu, và sàn nhiễu của chính câu đó
# ======================================================================
def control_at(ctx: Ctx, q, qi: int, slot: int, rng, need_entity: bool):
    """ĐỐI CHỨNG GHÉP CẶP — thay ĐÚNG ô mà can thiệp vừa động vào.

    Vì sao cần: nhánh `num_up` thay ô KHÔNG CÓ SỐ đầu tiên, còn nhánh giả dược
    dựng sẵn trong counterfactual_validity luôn thay ô số 0. Nếu hai ô đó khác
    nhau thì sàn nhiễu đang đo ở một CHỖ KHÁC với chỗ can thiệp, và hiệu số
    mất nghĩa. Ở đây donor đối chứng khớp cả vị trí, cả độ dài, cả việc có số
    hay không — chỉ khác đúng thuộc tính đang muốn đo.
    """
    d = q["distractors"][slot]
    cands = ctx.pool.candidates(
        has_num=bool(cv.NUM_RE.search(d)), length=len(d), tol=cv.LEN_TOL,
        exclude_owner=qi, uris=set(ctx.pool.by_uri) if need_entity else None)
    if not cands:
        return None
    new_d = list(q["distractors"])
    new_d[slot] = ctx.pool.donors[rng.choice(cands)]["text"]
    return new_d


def probe_item(ctx: Ctx, i: int, reps: int, seed: int) -> dict:
    """Lặp `reps` lần mỗi nhánh, mỗi lần một donor khác, mỗi lần kèm ĐỐI CHỨNG.

    Vì sao phải lặp: một lần thay phương án là MỘT mẫu ngẫu nhiên trong vô số
    cách thay. Không lặp thì đo được sự may rủi của một donor cụ thể, không
    phải sức nặng của trục.

    Trả về mỗi nhánh một danh sách CẶP {delta, delta_ctrl}: can thiệp và đối
    chứng cùng ô, cùng câu, cùng lần rút — nên hiệu số bên trong cặp đã tự
    khử mọi thứ riêng của câu và của ô đó.
    """
    q = ctx.items[i]
    rng = random.Random(seed * 1000003 + i)
    base = float(ctx.ey(i, [ctx.feats[i]])[0])
    arm_names = []
    for spec in AXES.values():
        arm_names += spec["arms"][ctx.surf]
    arms = {a: [] for a in dict.fromkeys(arm_names)}
    need_ent = {a: (spec["control"] == "placebo_ent")
                for spec in AXES.values() for a in spec["arms"][ctx.surf]}
    rows, tags = [], []
    for a in arms:
        for _ in range(reps):
            r = cv.make_counterfactual(a, q, i, ctx.pool, ctx.hops,
                                       ctx.curis[i], rng)
            if r is None:
                continue
            new_d, slot, donor = r
            ctl = control_at(ctx, q, i, slot, rng, need_ent[a])
            if ctl is None:
                continue
            rows.append(ctx.fz(q["stem"], q["correct"], new_d))
            tags.append((a, donor, slot, "t"))
            rows.append(ctx.fz(q["stem"], q["correct"], ctl))
            tags.append((a, ctl[slot], slot, "c"))
    if not rows:
        return {"base": base, "arms": arms, "n_probe": 0}
    ey = ctx.ey(i, rows)
    b = ctx.feats[i]
    pend = {}
    for (a, donor, slot, kind), e, f in zip(tags, ey, rows):
        if kind == "t":
            # dcol: Δ của TỪNG CỘT — để B4b truy ra cột nào chịu trách nhiệm,
            # thay vì chỉ nói được tên khối
            pend[a] = {"delta": float(e - base), "donor": donor, "slot": slot,
                       "dcol": {c: float(f[c] - b[c]) for c in ctx.cols
                                if not c.startswith("__")}}
        else:
            rec = pend.pop(a)
            rec["delta_ctrl"] = float(e - base)
            arms[a].append(rec)
    return {"base": base, "arms": arms, "n_probe": len(rows)}


def allowed_arms(surf: str, cert: dict, name: str) -> list[str]:
    """Nhánh của trục `name` được phép góp vào lời giải thích TỪNG CÂU.

    Cổng "arms": chỉ các nhánh đã qua chứng chỉ hiệu chỉnh ở mọi seed — một
    chiều chưa chứng minh được thì không được góp vào lời giải thích, kể cả khi
    chiều kia của cùng trục đã đạt. Cổng khác: mọi nhánh của trục (như cũ).
    """
    arms = AXES[name]["arms"][surf]
    if (cert or {}).get("gate") == "arms":
        ok = set(cert.get("axes", {}).get(name, {}).get("gated_arms", []))
        return [a for a in arms if a in ok]
    return list(arms)


def axis_scores(ctx: Ctx, probe: dict, half=None, cert=None) -> dict:
    """Gộp nhánh thành điểm số cho từng TRỤC, đã trừ sàn nhiễu riêng của câu.

    raw   = |Δ| trung bình khi can thiệp lên trục
    floor = |Δ| trung bình của nhánh giả dược KHỚP  (B3)
    net   = raw − floor, chặn dưới ở 0
    share = net chuẩn hoá theo tổng các trục

    half=0/1 → chỉ dùng một nửa số lần lặp (dùng cho kiểm tra chéo --validate).
    cert cho trước → trục đã đạt chứng chỉ chỉ gộp các nhánh được phép
    (`allowed_arms`); trục chưa đạt nhánh nào vẫn gộp mọi nhánh — nó không được
    nêu tên, nhưng dòng "CÓ lay chuyển mà trượt chứng chỉ" vẫn cần số của nó.
    Không truyền cert (kiểm tra chéo) → mọi nhánh, như cũ.
    """
    def pick(lst):
        return lst if half is None else lst[half::2]

    out = {}
    for name, spec in AXES.items():
        ds, cs, dirs = [], [], []
        use = spec["arms"][ctx.surf]
        if cert is not None:
            use = allowed_arms(ctx.surf, cert, name) or use
        for a in use:
            for d in pick(probe["arms"].get(a, [])):
                ds.append(d["delta"])
                cs.append(d["delta_ctrl"])
                dirs.append(1.0 if np.sign(d["delta"]) == PROMISE[a] else 0.0)
        raw = float(np.mean(np.abs(ds))) if ds else 0.0
        floor = float(np.mean(np.abs(cs))) if cs else 0.0
        # kiểm định GHÉP CẶP: mỗi can thiệp so với đối chứng CÙNG Ô của nó
        pval = float("nan")
        if len(ds) >= 3:
            diff = np.abs(ds) - np.abs(cs)
            if float(np.std(diff)) > 1e-12:
                pval = float(ttest_rel(np.abs(ds), np.abs(cs)).pvalue)
        out[name] = {"raw": raw, "floor": floor, "net": max(0.0, raw - floor),
                     "n": len(ds), "signed": float(np.mean(ds)) if ds else 0.0,
                     "dir_ok": float(np.mean(dirs)) if dirs else float("nan"),
                     "n_ctrl": len(cs), "p": pval, "arms_used": list(use)}
    tot = sum(v["net"] for v in out.values())
    for v in out.values():
        v["share"] = (v["net"] / tot) if tot > 1e-9 else float("nan")
    return out


# ======================================================================
# B4 — quy kết SHAP, CHỈ để đối chiếu
# ======================================================================
def shap_shares(ctx: Ctx, i: int) -> dict:
    row = pd.DataFrame([ctx.feats[i]])[ctx.cols]
    if cv.IS_TEXT:
        # Mô hình tuyến tính: quy kết tính thẳng từ hệ số (xem text_backend).
        # Thêm khối VĂN BẢN — phần quyết định KHÔNG đến từ cột viết tay nào.
        g = ctx.model_of[i].contrib_rows(
            row, {"BỀ MẶT": ctx.surf_cols, "TRI THỨC": cv.KG_COLS})
        a = {"BỀ MẶT": float(g["BỀ MẶT"][0]), "TRI THỨC": float(g["TRI THỨC"][0]),
             "VĂN BẢN": float(g["__text__"][0])}
        tot = sum(a.values()) + 1e-12
        return {k: {"abs": v, "share": v / tot} for k, v in a.items()}
    c = ctx.model_of[i].get_booster().predict(xgb.DMatrix(row),
                                              pred_contribs=True)
    if c.ndim == 2:
        c = c[None, :, :]
    c = c[0]
    idx = {"BỀ MẶT": [ctx.cols.index(x) for x in ctx.surf_cols],
           "TRI THỨC": [ctx.cols.index(x) for x in cv.KG_COLS]}
    a = {k: float(np.abs(c[:, v].sum(axis=1)).mean()) for k, v in idx.items()}
    tot = sum(a.values()) + 1e-12
    return {k: {"abs": v, "share": v / tot} for k, v in a.items()}


# ======================================================================
# B5 — PHÁT NGÔN
# ======================================================================
def verdict_of(entropy_h, scores, cert):
    """Quy tắc phát ngôn — cố tình có đường thoát "KHÔNG QUY ĐƯỢC".

    Một hệ giải thích mà câu nào cũng giải thích được là một hệ không kiểm
    chứng được. Ở đây một trục chỉ được nêu tên khi qua ĐỦ BA cửa:
      (1) đạt chứng chỉ ở B1   — trục có thật ở mức quần thể
      (2) p < 0,05 ở B2 vs B3  — trục lay chuyển được CHÍNH câu này
      (3) net >= 0,02 mức      — mức dịch chuyển đủ lớn để đáng nói
    """
    named, unmeasured = [], []
    for name, s in scores.items():
        if s["n"] == 0:
            unmeasured.append(name)     # KHÔNG ĐO ĐƯỢC, khác với ĐO RỒI KHÔNG THẤY
            continue
        ok_cert = cert.get("axes", {}).get(name, {}).get("certified", False)
        if ok_cert and s["p"] == s["p"] and s["p"] < 0.05 and s["net"] >= 0.02:
            named.append((s["net"], name, s))
    named.sort(reverse=True)
    if entropy_h >= 0.80:
        return "KHÔNG KẾT LUẬN", named, "dự đoán quá bất định để giải thích"
    if not named:
        why = "không trục nào lay chuyển được câu này quá mức nhiễu"
        if unmeasured:
            why = ("chỉ đo được " + ", ".join(
                n for n in scores if n not in unmeasured) +
                   "; trục " + ", ".join(unmeasured) +
                   " KHÔNG dựng được phản thực ở nhánh được phép dùng")
        return "KHÔNG QUY ĐƯỢC", named, why
    if len(named) == 1 or named[0][0] > 2 * named[1][0]:
        return "QUY ĐƯỢC", named, f"trục {named[0][1]} trội hẳn"
    return "QUY ĐƯỢC (chia)", named, "hai trục cùng có phần"


def blame_columns(ctx, probe, axis_name, top=2, arms=None):
    """Trong một trục, CỘT nào thật sự chịu trách nhiệm cho dịch chuyển dự đoán.

    Hai tình huống, phải phân biệt vì đọc khác nhau:

    (a) cột xê dịch KHÁC NHAU giữa các lần can thiệp (ví dụ độ dài phương án,
        phụ thuộc donor bốc được) — đo được ĂN KHỚP bằng tương quan hạng giữa
        Δcột và Δdự đoán. Đây là bằng chứng mạnh: cột xê dịch nhiều thì dự đoán
        cũng xê dịch nhiều.

    (b) cột xê dịch ĐỀU NHƯ NHAU mỗi lần (ví dụ "số phương án có số" luôn +1
        khi thêm một nhiễu có số) — phương sai bằng 0 nên KHÔNG có tương quan
        để đo. Chỉ nói được "đây là cột đã xê dịch", không nói được nó ăn khớp
        tới đâu. Báo cáo phải ghi rõ là ca này, đừng để người đọc tưởng là (a).

    Vẫn là quan sát trên can thiệp thật, không suy từ cấu trúc cây như SHAP.
    """
    spec = AXES[axis_name]
    recs = []
    for arm in (arms or spec["arms"][ctx.surf]):
        recs += [r for r in probe["arms"].get(arm, []) if "dcol" in r]
    if len(recs) < 6:
        return []
    dy = np.array([r["delta"] - r.get("delta_ctrl", 0.0) for r in recs])
    cols = ctx.surf_cols if axis_name == "BỀ MẶT" else cv.KG_COLS
    out = []
    for c in cols:
        dc = np.array([r["dcol"][c] for r in recs])
        mag = float(np.mean(np.abs(dc)))
        if mag < 1e-9:
            continue                      # cột không hề xê dịch → không liên quan
        if np.std(dc) < 1e-9:
            out.append((0.5, c, None, None, mag, "đều"))   # ca (b)
            continue
        r = spearmanr(dc, dy)
        if r.statistic != r.statistic:
            continue
        out.append((1.0 + abs(r.statistic), c, float(r.statistic),
                    float(r.pvalue), mag, "ăn khớp"))       # ca (a)
    out.sort(reverse=True, key=lambda t: (t[0], t[4]))
    return out[:top]


def explain(ctx, i, cert, reps, seed, show_steps=True):
    q = ctx.items[i]
    proba = ctx.model_of[i].predict_proba(
        pd.DataFrame([ctx.feats[i]])[ctx.cols])[0]
    ey = float(proba @ np.arange(len(proba)))
    H = entropy(proba)
    probe = probe_item(ctx, i, reps, seed)
    scores = axis_scores(ctx, probe, cert=cert)
    sh = shap_shares(ctx, i)
    v, named, why = verdict_of(H, scores, cert)

    print("=" * 78)
    print(f"[{q['id']}]  {q['stem'][:96]}")
    print(f"  đáp án: {q['correct'][:78]}")
    print("-" * 78)
    print(f"  dự đoán {LEVEL_VN[int(np.argmax(proba))]} · E[y]={ey:.2f} · "
          f"bất định {H:.2f} · nhãn thật {q[ctx.cfg['label_field']]}")

    if show_steps:
        print(f"\n  B2+B3 · CAN THIỆP {reps} lần mỗi nhánh, trên chính câu này")
        print(f"    {'nhánh':13s}{'n':>4s}{'|Δ| can thiệp':>15s}"
              f"{'|Δ| đối chứng':>16s}{'Δ có dấu':>12s}{'đúng hướng':>13s}")
        for name, spec in AXES.items():
            for a in spec["arms"][ctx.surf]:
                recs = probe["arms"].get(a, [])
                if not recs:
                    print(f"    {a:13s}{0:4d}       — không dựng được phản thực")
                    continue
                d = np.array([r["delta"] for r in recs])
                c = np.array([r["delta_ctrl"] for r in recs])
                ok = np.mean(np.sign(d) == PROMISE[a])
                print(f"    {a:13s}{len(d):4d}{np.abs(d).mean():15.4f}"
                      f"{np.abs(c).mean():16.4f}{d.mean():+12.4f}{ok:12.0%}")

    print("\n  B4 · QUY KẾT CÓ KIỂM CHỨNG")
    print(f"    {'trục':11s}{'|Δ| trục':>10s}{'sàn nhiễu':>11s}{'còn lại':>10s}"
          f"{'p':>9s}{'tỉ trọng':>10s}   {'SHAP nói':>9s}")
    for name, s in scores.items():
        pp = "  n/a" if s["p"] != s["p"] else f"{s['p']:.3f}"
        shp = f"{sh[name]['share']:.0%}"
        tr = "  n/a" if s["share"] != s["share"] else f"{s['share']:.0%}"
        print(f"    {name:11s}{s['raw']:10.4f}{s['floor']:11.4f}{s['net']:10.4f}"
              f"{pp:>9s}{tr:>10s}   {shp:>9s}")

    print(f"\n  B5 · KẾT LUẬN: {v} — {why}")
    for net, name, s in named:
        cd = ctx.cfg["surface"]
        print(f"    • trục {name} [nhánh {', '.join(s['arms_used'])}]: sửa "
              f"{AXES[name]['means'][cd]} làm dự đoán dịch {net:.3f} mức")
        print(f"      trên mức nhiễu (p={s['p']:.3f}); hướng khớp lời hứa "
              f"{s['dir_ok']:.0%} số lần")
        for _ar, c, rho, pv, mag, kind in blame_columns(
                ctx, probe, name, arms=s["arms_used"]):
            if kind == "ăn khớp":
                print(f"      └ cột {c}: xê dịch ĂN KHỚP với dự đoán, "
                      f"rho={rho:+.2f} (p={pv:.2g}), |Δ| TB {mag:.3f}")
            else:
                print(f"      └ cột {c}: xê dịch ĐỀU {mag:.2f} mỗi lần can thiệp "
                      f"— không đo được mức ăn khớp")
    unmeas = [n for n, s2 in scores.items() if s2["n"] == 0]
    if unmeas:
        print(f"    ! trục {', '.join(unmeas)} KHÔNG đo được ở câu này — không có")
        print("      donor hợp lệ để dựng phản thực. Đây là 'chưa biết', KHÔNG")
        print("      phải 'đã kiểm tra và thấy không có tác dụng'.")
    if v == "KHÔNG QUY ĐƯỢC" and not unmeas:
        print("    Mô hình vẫn xếp mức được, nhưng KHÔNG trục nào chịu trách")
        print("    nhiệm — độ khó câu này nằm ngoài hai trục đang đo.")
    # Trục CÓ lay chuyển câu này nhưng TRƯỢT chứng chỉ ở B1: phải nói ra, không
    # được lặng lẽ bỏ. Mô hình vẫn dùng khối đó — chỉ là không dùng theo nghĩa
    # mà giả thuyết gán cho nó.
    for name, s2 in scores.items():
        cert_ok = cert.get("axes", {}).get(name, {}).get("certified", False)
        if (not cert_ok and s2["p"] == s2["p"] and s2["p"] < 0.05
                and s2["net"] >= 0.02):
            print(f"    ◦ trục {name} CÓ lay chuyển câu này ({s2['net']:.3f} mức, "
                  f"p={s2['p']:.3f}) nhưng KHÔNG")
            print(f"      được nêu làm nguyên nhân: ở B1 trục này trượt chứng chỉ "
                  f"(hướng ngược/không có ý nghĩa).")
            print(f"      Mô hình vẫn dùng khối đặc trưng đó, nhưng như một dấu "
                  f"hiệu KHÁC với ý nghĩa được gán")
            print(f"      cho nó — hướng khớp lời hứa chỉ {s2['dir_ok']:.0%} số lần.")
    for name, s in scores.items():
        if sh[name]["share"] > 0.5 and (s["share"] != s["share"]
                                        or s["share"] < 0.25):
            print(f"    ⚠ SHAP dành {sh[name]['share']:.0%} cho trục {name} "
                  f"nhưng can thiệp lên trục đó không lay chuyển câu này.")
    print()
    return {"id": q["id"], "ey": ey, "H": H, "verdict": v,
            "scores": scores, "shap": {k: v2["share"] for k, v2 in sh.items()}}


# ======================================================================
# KIỂM TRA CHÉO — lời giải thích có LẶP LẠI được không
# ======================================================================
def group_shapley(ctx: Ctx, i: int, bg: pd.DataFrame) -> dict:
    """Biến thể SHAP CÔNG BẰNG NHẤT với phép can thiệp — để phép so không bị
    bắt bẻ là "chọn nhầm loại SHAP".

    `shap_shares` (TreeSHAP qua pred_contribs) khác can thiệp ở hai chỗ: nó quy
    kết LỀ LOG-ODDS của từng lớp, còn can thiệp đo E[y]; và nó đi theo đường
    trong cây (path-dependent), không can thiệp lên đặc trưng. Ở đây tính ĐÚNG
    giá trị Shapley cho HAI người chơi — khối BỀ MẶT và khối TRI THỨC — trên
    chính E[y], theo nghĩa can thiệp: khối vắng mặt lấy giá trị của các câu nền
    `bg`. Hai người chơi thì Shapley tính chính xác, không phải xấp xỉ.
    """
    x = ctx.X.iloc[i]
    S, K = list(ctx.surf_cols), list(cv.KG_COLS)

    def v(keep):
        rows = bg.copy()
        for c in keep:
            rows[c] = x[c]
        return float(ctx.ey(i, rows).mean())

    if cv.IS_TEXT:
        # BA người chơi: BỀ MẶT, TRI THỨC và VĂN BẢN (vector PhoBERT). Vắng mặt
        # khối văn bản = lấy văn bản của câu nền, đúng nghĩa can thiệp như hai
        # khối kia. Ba người chơi thì Shapley vẫn tính chính xác (6 hoán vị).
        import text_backend as tb
        T = [tb.TID_COL]
        v0 = v([])
        vS, vK, vT = v(S), v(K), v(T)
        vSK, vST, vKT = v(S + K), v(S + T), v(K + T)
        vAll = v(S + K + T)
        return {
            "BỀ MẶT": (2 * (vS - v0) + (vSK - vK) + (vST - vT)
                       + 2 * (vAll - vKT)) / 6,
            "TRI THỨC": (2 * (vK - v0) + (vSK - vS) + (vKT - vT)
                         + 2 * (vAll - vST)) / 6,
            "VĂN BẢN": (2 * (vT - v0) + (vST - vS) + (vKT - vK)
                        + 2 * (vAll - vSK)) / 6,
        }
    v0, vS, vK, vSK = v([]), v(S), v(K), v(S + K)
    return {"BỀ MẶT": 0.5 * ((vS - v0) + (vSK - vK)),
            "TRI THỨC": 0.5 * ((vK - v0) + (vSK - vS))}


def validate(ctx, n, reps, seed):
    """Chia số lần lặp làm hai nửa độc lập (donor khác nhau).

    Hỏi hai câu:
      (a) ĐỘ LẶP LẠI  — ước lượng ở nửa A có dự báo được nửa B không? Nếu
          không thì lời giải thích chỉ là nhiễu, dù nghe rất hợp lý.
      (b) SO VỚI SHAP — SHAP tất định nên "lặp lại" hoàn hảo, nhưng nó có dự
          báo được phản ứng THẬT ở nửa B không? Đây mới là phép so công bằng.

    Trần cho (b): nửa B là phép đo CÓ NHIỄU, độ tin cậy ρ(A,B). Theo lý thuyết
    đo lường cổ điển, một đại lượng KHÔNG nhiễu tương quan tối đa với nửa B là
    √ρ(A,B) — không phải ρ(A,B). Lấy ρ(A,B) làm trần thì nghiêng có lợi cho
    SHAP. Độ tin cậy của lời giải thích dùng ĐỦ R lần lặp là Spearman–Brown
    2ρ/(1+ρ).
    """
    rs = np.random.default_rng(seed)
    picks = sorted(rs.choice(len(ctx.items), size=min(n, len(ctx.items)),
                             replace=False).tolist())
    bg = ctx.X.sample(n=min(200, len(ctx.X)), random_state=seed)
    cA, cB, cS, cG, kept = [], [], [], [], []
    for i in picks:
        pr = probe_item(ctx, i, reps, seed)
        if pr["n_probe"] < 2 * reps:
            continue
        a, b = axis_scores(ctx, pr, half=0), axis_scores(ctx, pr, half=1)
        s = shap_shares(ctx, i)
        g = group_shapley(ctx, i, bg)
        cA.append(a["BỀ MẶT"]["net"] - a["TRI THỨC"]["net"])
        cB.append(b["BỀ MẶT"]["net"] - b["TRI THỨC"]["net"])
        cS.append(s["BỀ MẶT"]["abs"] - s["TRI THỨC"]["abs"])
        cG.append(abs(g["BỀ MẶT"]) - abs(g["TRI THỨC"]))
        kept.append(i)
    cA, cB, cS, cG = map(np.array, (cA, cB, cS, cG))
    # Mô hình nền `emb` không nhận cột luật tay nào, nên ĐỘ NGHIÊNG theo quy kết
    # (bề mặt − tri thức) là hằng số 0 ở mọi câu: không còn đại lượng nào để
    # tương quan. Đó là ca GIỚI HẠN của đường cong — câu hỏi "quy kết có dự báo
    # được can thiệp không" thôi đặt ra được, chứ không phải trả lời là "không".
    # Ghi ra None kèm lý do, đừng để NaN lọt vào file kết quả.
    undef = [n for n, c in (("shap", cS), ("groupshap", cG))
             if np.allclose(c, c[0])] if len(cA) else []
    r_rel = spearmanr(cA, cB)
    r_shap = spearmanr(cS, cB) if "shap" not in undef else None
    r_gsh = spearmanr(cG, cB) if "groupshap" not in undef else None
    rel = float(r_rel.statistic)
    ceil = float(np.sqrt(rel)) if rel > 0 else float("nan")
    sb = float(2 * rel / (1 + rel))

    # khoảng tin cậy bootstrap theo CÂU; seed tách riêng để không đụng dãy ngẫu
    # nhiên của phép đo chính (các khoá cũ trong JSON giữ nguyên giá trị)
    bs = np.random.default_rng(seed + 1)
    boot = {"rel": [], "shap": [], "groupshap": [],
            "frac_shap": [], "frac_groupshap": []}
    m = len(kept)
    for _ in range(2000):
        ix = bs.integers(0, m, m)
        rr = spearmanr(cA[ix], cB[ix]).statistic
        r1 = np.nan if "shap" in undef else spearmanr(cS[ix], cB[ix]).statistic
        r2 = (np.nan if "groupshap" in undef
              else spearmanr(cG[ix], cB[ix]).statistic)
        c = np.sqrt(rr) if rr > 0 else np.nan
        boot["rel"].append(rr)
        boot["shap"].append(r1)
        boot["groupshap"].append(r2)
        boot["frac_shap"].append(r1 / c)
        boot["frac_groupshap"].append(r2 / c)
    ci = {}
    for k, v in boot.items():
        v = np.asarray(v, dtype=float)
        ci[k] = (None if np.all(np.isnan(v))
                 else [float(np.nanpercentile(v, 2.5)),
                       float(np.nanpercentile(v, 97.5))])
    f1 = None if r_shap is None else float(r_shap.statistic / ceil)
    f2 = None if r_gsh is None else float(r_gsh.statistic / ceil)

    print("=" * 78)
    print(f"KIỂM TRA CHÉO — môn {ctx.subject} | {m} câu | {reps} lần/nhánh")
    print("=" * 78)
    print("  Đại lượng so sánh: ĐỘ NGHIÊNG của câu = (còn lại trục BỀ MẶT) −")
    print("  (còn lại trục TRI THỨC). Dương = câu này nhạy với bề mặt hơn.")
    print()
    print(f"  (a) can thiệp nửa A → nửa B            : rho = {rel:+.3f} "
          f"[{ci['rel'][0]:+.3f}; {ci['rel'][1]:+.3f}]  (p = {r_rel.pvalue:.2g})")
    print(f"      độ tin cậy khi dùng đủ R lần lặp (Spearman–Brown) = {sb:.3f}")
    print(f"      TRẦN cho mọi đại lượng dự báo nửa B = √rho = {ceil:.3f}")
    def _line(tag, r, key):
        if r is None:
            print(f"  {tag}: KHÔNG ĐỊNH NGHĨA ĐƯỢC — quy kết cho mọi khối đặt "
                  f"tên được đều bằng 0 (mô hình nền không dùng cột luật tay).")
            return
        print(f"  {tag}: rho = {r.statistic:+.3f} "
              f"[{ci[key][0]:+.3f}; {ci[key][1]:+.3f}]  (p = {r.pvalue:.2g})")
    _line("(b) SHAP cây (log-odds, path-dep.) → B ", r_shap, "shap")
    _line("(c) Shapley khối trên E[y] (can thiệp)→B", r_gsh, "groupshap")
    print()
    if f1 is None and f2 is None:
        print("  So với trần √rho: không tính được — xem hai dòng trên.")
    else:
        fmt = lambda f, k: ("—" if f is None else
                            f"{f:.0%} [{ci[k][0]:.0%}; {ci[k][1]:.0%}]")
        print(f"  So với trần √rho: SHAP cây với tới {fmt(f1, 'frac_shap')}, "
              f"Shapley khối {fmt(f2, 'frac_groupshap')}.")
    have = [f for f in (f1, f2) if f is not None]
    best = max(have) if have else None
    sig = any(r.pvalue < 0.05 for r in (r_shap, r_gsh) if r is not None)
    if best is None:
        print("  ⇒ Ở mô hình nền này KHÔNG CÒN quy kết nào để kiểm: toàn bộ quyết")
        print("    định nằm trong khối văn bản không đặt tên được. Đây là ca giới")
        print("    hạn, không phải kết quả âm.")
    elif rel <= 0.3:
        print("  ⚠ Ước lượng từng câu CHƯA ổn định ở số lần lặp này — tăng --reps,")
        print("    hoặc chỉ báo cáo ở mức NHÓM câu, đừng báo cáo từng câu.")
    elif sig and best < 0.5:
        print("  ⇒ Quy kết bắt được MỘT PHẦN phản ứng thật, nhưng phần bỏ sót lớn hơn")
        print("    phần bắt được — ở CẢ biến thể công bằng nhất — và nó không tự nói")
        print("    mình đang ở đâu trên thang đó. Can thiệp tự mang sai số của nó.")
    elif sig:
        print("  ⇒ Biến thể quy kết tốt nhất bắt được PHẦN LỚN tín hiệu — ở môn này")
        print("    phép so KHÔNG ủng hộ luận điểm 'quy kết không khớp can thiệp'.")
    else:
        print("  ⇒ Cả hai biến thể quy kết đều KHÔNG dự báo được phản ứng thật ở nửa B.")
    return {"n": m, "reps": reps,
            "rho_split_half": rel,
            "p_split_half": float(r_rel.pvalue),
            "rho_shap_vs_intervention":
                None if r_shap is None else float(r_shap.statistic),
            "p_shap_vs_intervention":
                None if r_shap is None else float(r_shap.pvalue),
            # thêm 09/2026 — các khoá phía trên giữ nguyên nghĩa và giá trị
            "reliability_full_spearman_brown": sb,
            "ceiling_sqrt": ceil,
            "frac_ceiling_shap": f1,
            "rho_groupshap_vs_intervention":
                None if r_gsh is None else float(r_gsh.statistic),
            "p_groupshap_vs_intervention":
                None if r_gsh is None else float(r_gsh.pvalue),
            "frac_ceiling_groupshap": f2,
            "attribution_undefined": undef,
            "ci95": ci, "n_boot": 2000, "n_background": int(len(bg)),
            "items": [ctx.items[i]["id"] for i in kept],
            "tilt": {"A": cA.tolist(), "B": cB.tolist(), "shap": cS.tolist(),
                     "groupshap": cG.tolist()}}


# ======================================================================
# ĐỘ PHỦ — trục nào đo được ở bao nhiêu câu
# ======================================================================
def coverage(ctx, seed: int) -> dict:
    """Không phải câu nào cũng dựng được phản thực cho mọi nhánh.

    `num_down` cần câu có sẵn một nhiễu chứa số; `kg_near` cần trong kho donor
    có nhiễu chứa thực thể cách đáp án đúng 1 hop. Câu không dựng được thì phán
    quyết đúng là "chưa biết", KHÔNG phải "đã kiểm tra và không thấy tác dụng" —
    nên tỉ lệ này phải được báo cáo kèm mọi kết luận từng câu.
    """
    rng = random.Random(seed)
    arms = []
    for spec in AXES.values():
        arms += spec["arms"][ctx.surf]
    n = len(ctx.items)
    cnt = {a: 0 for a in arms}
    axis_any = {name: 0 for name in AXES}
    for i, q in enumerate(ctx.items):
        got = {}
        for a in arms:
            r = cv.make_counterfactual(a, q, i, ctx.pool, ctx.hops,
                                       ctx.curis[i], rng)
            ok = r is not None
            if ok:   # phải dựng được CẢ đối chứng ghép cặp mới tính là đo được
                ok = control_at(ctx, q, i, r[1], rng,
                                a in AXES["TRI THỨC"]["arms"][ctx.surf]) is not None
            got[a] = ok
            cnt[a] += ok
        for name, spec in AXES.items():
            axis_any[name] += any(got[a] for a in spec["arms"][ctx.surf])
    print("=" * 78)
    print(f"ĐỘ PHỦ CAN THIỆP — môn {ctx.subject} | {n} câu")
    print("=" * 78)
    for a in arms:
        print(f"  {a:13s} dựng được {cnt[a]:5d} / {n} = {cnt[a]/n:6.1%}")
    print()
    for name in AXES:
        print(f"  trục {name:10s} đo được ở {axis_any[name]:5d} / {n} "
              f"= {axis_any[name]/n:6.1%}")
    print()
    print("  Với phần còn lại, phán quyết đúng là 'chưa biết'. Và tập đo được")
    print("  trục TRI THỨC là tập câu CÓ nhắc thực thể trong ontology, tức đã")
    print("  lệch về phía câu bám sát chương trình — kết luận về trục đó chỉ có")
    print("  giá trị trên tập ấy, không suy rộng ra cả bộ.")
    return {"subject": ctx.subject, "n_items": n, "seed": seed,
            "by_arm": {a: cnt[a] / n for a in arms},
            "by_axis": {k: v / n for k, v in axis_any.items()},
            "counts": {a: cnt[a] for a in arms}}


# ======================================================================
# KHAI THÁC — lời giải thích có dùng được vào việc gì không
# ======================================================================
def selective(ctx, cert, n, reps, seed):
    """Lớp giải thích có phải là cơ chế BIẾT-KHI-NÀO-MÌNH-KHÔNG-BIẾT không?

    Đây là cách đo TÍNH HỮU DỤNG mà không cần người: nếu những câu hệ nói
    "KHÔNG QUY ĐƯỢC" đúng là những câu mô hình hay sai, thì lời giải thích
    không còn là đồ trang trí — nó là một tín hiệu dùng được để TỪ CHỐI trả lời.

    Đối chứng bắt buộc: entropy của dự đoán. Entropy có sẵn, không tốn gì để
    tính. Nếu entropy một mình đã làm tốt bằng thì lớp giải thích KHÔNG thêm
    được gì, và phải nói thẳng như vậy.
    """
    rs = np.random.default_rng(seed)
    picks = sorted(rs.choice(len(ctx.items), size=min(n, len(ctx.items)),
                             replace=False).tolist())
    rows = []
    for i in picks:
        proba = ctx.model_of[i].predict_proba(
            pd.DataFrame([ctx.feats[i]])[ctx.cols])[0]
        ey = float(proba @ np.arange(len(proba)))
        H = entropy(proba)
        pr = probe_item(ctx, i, reps, seed)
        if pr["n_probe"] < 2 * reps:
            continue
        sc = axis_scores(ctx, pr, cert=cert)
        verdict, named, _ = verdict_of(H, sc, cert)
        rows.append({
            "i": i, "H": H, "ey": ey, "y": int(ctx.y[i]),
            "pred": int(np.argmax(proba)),
            "correct": int(np.argmax(proba) == ctx.y[i]),
            "abserr": abs(ey - ctx.y[i]),
            "strength": float(named[0][0]) if named else 0.0,
            "verdict": verdict,
            "named": bool(named)})
    df = pd.DataFrame(rows)
    N = len(df)

    print("=" * 78)
    print(f"KHAI THÁC · TỪ CHỐI CÓ CHỌN LỌC — môn {ctx.subject} | {N} câu | "
          f"{reps} lần/nhánh")
    print("=" * 78)
    print("  Câu hỏi: chỗ lời giải thích bó tay có phải chỗ mô hình hay sai không?")
    print()
    print(f"  {'phán quyết':22s}{'n':>6s}{'đúng mức':>11s}{'|sai lệch|':>13s}")
    for v, g in df.groupby("verdict"):
        print(f"  {v:22s}{len(g):6d}{g.correct.mean():10.1%}{g.abserr.mean():13.3f}")
    a = df[df.named]
    b = df[~df.named]
    if len(a) and len(b):
        d = a.correct.mean() - b.correct.mean()
        boot = np.array([
            (rs.choice(a.correct.values, len(a)).mean()
             - rs.choice(b.correct.values, len(b)).mean()) for _ in range(4000)])
        lo, hi = np.percentile(boot, [2.5, 97.5])
        print()
        print(f"  quy được ({len(a)}) so với không quy được ({len(b)}): "
              f"{d:+.1%} độ chính xác, KTC95 [{lo:+.1%}, {hi:+.1%}]")

    # ---- đường cong độ phủ ↔ độ chính xác, ba cách xếp hạng ----
    z = lambda v: (v - v.mean()) / (v.std() + 1e-12)
    rankers = {
        "entropy (đối chứng)": -df.H.values,
        "sức giải thích": df.strength.values,
        "cả hai": (z(df.strength) - z(df.H)).values,
    }
    print()
    print("  ĐƯỜNG CONG ĐỘ PHỦ ↔ ĐỘ CHÍNH XÁC (giữ lại k% câu tự tin nhất)")
    covs = [1.0, 0.8, 0.6, 0.4, 0.2]
    print("  " + f"{'cách xếp hạng':22s}" +
          "".join(f"{int(c*100):>9d}%" for c in covs))
    for nm, sc in rankers.items():
        order = np.argsort(-sc)
        cells = []
        for c in covs:
            k = max(3, int(round(c * N)))
            cells.append(df.correct.values[order[:k]].mean())
        print("  " + f"{nm:22s}" + "".join(f"{v:9.1%} " for v in cells))

    # ---- có thêm gì so với entropy không: xét TRONG từng tầng entropy ----
    print()
    print("  SỨC GIẢI THÍCH CÓ THÊM GÌ NGOÀI ENTROPY? (xét trong từng tầng entropy)")
    df["tier"] = pd.qcut(df.H, 3, labels=["H thấp", "H vừa", "H cao"],
                         duplicates="drop")
    strata = {}
    for t, g in df.groupby("tier", observed=True):
        if g.strength.nunique() < 3:
            continue
        r = spearmanr(g.strength, g.correct)
        strata[str(t)] = {"n": int(len(g)), "rho": float(r.statistic),
                          "p": float(r.pvalue)}
        print(f"    {str(t):10s} n={len(g):4d}   rho(sức giải thích, đúng mức) = "
              f"{r.statistic:+.3f}  (p={r.pvalue:.2g})")
    # ---- CƠ CHẾ: vì sao sức giải thích lại đi NGƯỢC với độ đúng ----
    r_sh = spearmanr(df.strength, df.H)
    r_se = spearmanr(df.strength, df.abserr)
    print()
    print("  CƠ CHẾ — sức giải thích thật ra đang đo cái gì")
    print(f"    rho(sức giải thích, entropy)      = {r_sh.statistic:+.3f} "
          f"(p={r_sh.pvalue:.2g})")
    print(f"    rho(sức giải thích, |sai lệch|)   = {r_se.statistic:+.3f} "
          f"(p={r_se.pvalue:.2g})")
    if r_sh.statistic > 0.15 and r_sh.pvalue < 0.05:
        print("    ⇒ Câu DỄ giải thích cũng là câu mô hình BẤT ĐỊNH. Hợp lý: cả hai")
        print("      cùng phản ánh việc câu nằm gần ranh giới quyết định — gần ranh")
        print("      giới thì một sửa đổi nhỏ cũng lay chuyển được (nên 'giải thích")
        print("      được'), mà dự đoán cũng vì thế kém chắc.")
        if abs(r_se.statistic) < 0.1 or r_se.pvalue >= 0.05:
            print("      NHƯNG sức giải thích KHÔNG tương quan với độ lớn sai lệch")
            print("      (xem dòng trên). Nên phát biểu đúng chỉ là: sức giải thích là")
            print("      một BẢN SAO NHIỄU của entropy, không mang thêm tín hiệu —")
            print("      CHƯA đủ căn cứ nói nó có hại, chỉ đủ nói nó không thêm gì.")
        else:
            print("      Và nó đi cùng chiều với sai lệch, nên dùng nó để từ chối thì")
            print("      từ chối nhầm hướng.")

    sig = [v for v in strata.values() if v["p"] < 0.05 and v["rho"] > 0]
    print()
    if sig:
        print("  ⇒ Sức giải thích còn dự báo được độ đúng NGAY CẢ khi entropy đã cố")
        print("    định. Lớp giải thích thêm được tín hiệu mà entropy không có.")
    else:
        print("  ⇒ Trong từng tầng entropy, sức giải thích KHÔNG còn dự báo được độ")
        print("    đúng. Nghĩa là phần nó bắt được, entropy đã bắt rồi — lớp giải")
        print("    thích KHÔNG thêm tín hiệu dùng để từ chối. Phải nói thẳng điều này.")
    return {"subject": ctx.subject, "n": int(N), "reps": reps, "seed": seed,
            "by_verdict": {str(v): {"n": int(len(g)),
                                    "acc": float(g.correct.mean()),
                                    "abserr": float(g.abserr.mean())}
                           for v, g in df.groupby("verdict")},
            "named_vs_not": ({"delta_acc": float(d),
                              "ci": [float(lo), float(hi)]}
                             if len(a) and len(b) else None),
            "curve": {nm: [float(df.correct.values[np.argsort(-sc)][
                :max(3, int(round(c * N)))].mean()) for c in covs]
                      for nm, sc in rankers.items()},
            "coverages": covs,
            "within_entropy_strata": strata,
            "mechanism": {"rho_strength_entropy": float(r_sh.statistic),
                          "p_strength_entropy": float(r_sh.pvalue),
                          "rho_strength_abserr": float(r_se.statistic),
                          "p_strength_abserr": float(r_se.pvalue)},
            "rows": df.drop(columns=["tier"]).to_dict("records")}


# ======================================================================
# KHAI THÁC · LỜI KHUYÊN SỬA ĐỀ — sửa tối thiểu gì thì hệ xếp lại mức
# ======================================================================
def arm_axis(ctx, arm):
    for name, spec in AXES.items():
        if arm in spec["arms"][ctx.surf]:
            return name
    return "?"


def recourse_item(ctx, i, reps, seed, cert=None):
    """Tìm sửa đổi TỐI THIỂU, hợp lệ về văn bản, làm hệ xếp lại mức.

    Khác với B4 (đo trục nào nặng), đây trả lời câu giáo viên thật sự hỏi:
    "muốn câu này thành Thông hiểu thì phải sửa gì". Mọi sửa đổi đều thay đúng
    MỘT phương án nhiễu bằng một nhiễu THẬT lấy từ câu khác, nên đề sau khi sửa
    vẫn là đề đọc được.

    CẢNH BÁO phải đi kèm mọi lần dùng: đây là sửa đổi làm MÔ HÌNH xếp lại mức,
    không phải bằng chứng học sinh sẽ thấy khác. Nó là gợi ý để người soạn đề
    xem lại, không phải kết luận.
    """
    q = ctx.items[i]
    rng = random.Random(seed * 7919 + i)
    base_p = ctx.model_of[i].predict_proba(
        pd.DataFrame([ctx.feats[i]])[ctx.cols])[0]
    L0 = int(np.argmax(base_p))
    ey0 = float(base_p @ np.arange(len(base_p)))
    arms = []
    for spec in AXES.values():
        arms += spec["arms"][ctx.surf]
    rows, tags = [], []
    for a in arms:
        for _ in range(reps):
            r = cv.make_counterfactual(a, q, i, ctx.pool, ctx.hops,
                                       ctx.curis[i], rng)
            if r is None:
                continue
            new_d, slot, donor = r
            rows.append(ctx.fz(q["stem"], q["correct"], new_d))
            tags.append((a, slot, donor))
    if not rows:
        return {"i": i, "L0": L0, "ey0": ey0, "n_try": 0, "moves": []}
    proba = ctx.model_of[i].predict_proba(pd.DataFrame(rows)[ctx.cols])
    ey = proba @ np.arange(proba.shape[1])
    lab = proba.argmax(axis=1)
    moves = []
    for (a, slot, donor), L1, e1 in zip(tags, lab, ey):
        if int(L1) != L0:
            ax = arm_axis(ctx, a)
            ok = (bool((cert or {}).get("axes", {}).get(ax, {}).get("certified"))
                  and a in allowed_arms(ctx.surf, cert or {}, ax))
            moves.append({"arm": a, "axis": ax, "certified": ok,
                          "slot": int(slot), "donor": donor,
                          "to": int(L1), "d_ey": float(e1 - ey0)})
    moves.sort(key=lambda m: abs(m["d_ey"]))
    return {"i": i, "id": q["id"], "L0": L0, "ey0": ey0,
            "n_try": len(rows), "moves": moves}


def recourse(ctx, n, reps, seed, one=None, cert=None):
    rs = np.random.default_rng(seed)
    picks = ([one] if one is not None else
             sorted(rs.choice(len(ctx.items), size=min(n, len(ctx.items)),
                              replace=False).tolist()))
    print("=" * 78)
    print(f"KHAI THÁC · LỜI KHUYÊN SỬA ĐỀ — môn {ctx.subject} | "
          f"{len(picks)} câu | {reps} lần/nhánh")
    print("=" * 78)
    print("  Câu hỏi: thay ĐÚNG MỘT phương án nhiễu bằng một nhiễu THẬT của câu")
    print("  khác — có làm hệ xếp lại mức không, và rẻ nhất là thay cái nào?")
    print()
    agg, det = {"down": 0, "up": 0, "any": 0, "n": 0}, []
    for i in picks:
        r = recourse_item(ctx, i, reps, seed, cert)
        if r["n_try"] == 0:
            continue
        agg["n"] += 1
        ok_moves = [m for m in r["moves"] if m["certified"]]
        no_moves = [m for m in r["moves"] if not m["certified"]]
        down = [m for m in ok_moves if m["to"] < r["L0"]]
        up = [m for m in ok_moves if m["to"] > r["L0"]]
        agg["down"] += bool(down)
        agg["up"] += bool(up)
        agg["any"] += bool(r["moves"])
        det.append({"id": r["id"], "L0": r["L0"], "n_try": r["n_try"],
                    "rate": len(r["moves"]) / r["n_try"],
                    "cheapest_down": down[0] if down else None,
                    "cheapest_up": up[0] if up else None,
                    "n_uncertified_moves": len(no_moves)})
        if one is not None or len(picks) <= 3:
            q = ctx.items[i]
            print(f"  [{r['id']}] {q['stem'][:88]}")
            print(f"    hệ đang xếp: {LEVEL_VN[r['L0']]} (E[y]={r['ey0']:.2f}) · "
                  f"thử {r['n_try']} sửa đổi, {len(r['moves'])} cái đổi được mức")
            for lbl, cand in (("HẠ mức", down), ("NÂNG mức", up)):
                if not cand:
                    print(f"    {lbl:9s}: không sửa đổi đơn lẻ nào QUA CỔNG B1 "
                          f"làm được")
                    continue
                m = cand[0]
                print(f"    {lbl:9s}: thay phương án #{m['slot']+1} bằng "
                      f"“{m['donor'][:56]}”")
                print(f"    {'':9s}  → {LEVEL_VN[m['to']]} "
                      f"(E[y] đổi {m['d_ey']:+.2f}) · nhánh {m['arm']}")
            if no_moves:
                m = no_moves[0]
                print(f"    (bỏ qua {len(no_moves)} sửa đổi đổi được mức nhưng đi "
                      f"qua nhánh {m['arm']} (trục {m['axis']}) — nhánh này")
                print(f"     CHƯA đạt chứng chỉ ở B1, nên không được dùng làm lời "
                      f"khuyên sửa đề.)")
            print()
    if agg["n"]:
        print(f"  TRÊN {agg['n']} CÂU")
        print(f"    sửa được xuống mức thấp hơn : {agg['down']/agg['n']:6.1%}")
        print(f"    sửa được lên mức cao hơn    : {agg['up']/agg['n']:6.1%}")
        print(f"    sửa được theo hướng nào đó  : {agg['any']/agg['n']:6.1%}")
        rates = np.array([d["rate"] for d in det])
        print(f"    tỉ lệ sửa đổi thành công    : {rates.mean():6.1%} trung bình")
    print()
    print("  ⚠ ĐỌC ĐÚNG: đây là sửa đổi làm MÔ HÌNH xếp lại mức, KHÔNG phải bằng")
    print("    chứng học sinh sẽ thấy câu dễ/khó đi. Dùng làm gợi ý cho người soạn")
    print("    đề xem lại, không dùng làm kết luận. Giá trị của nó phụ thuộc vào")
    print("    chương 'lời giải thích có đáng tin không' — nếu phần đó không qua")
    print("    thì phần này cũng không.")
    return {"subject": ctx.subject, "n": agg["n"], "reps": reps, "seed": seed,
            "editable_down": agg["down"] / agg["n"] if agg["n"] else None,
            "editable_up": agg["up"] / agg["n"] if agg["n"] else None,
            "editable_any": agg["any"] / agg["n"] if agg["n"] else None,
            "items": det}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="physics", choices=sorted(cv.SUBJECTS))
    ap.add_argument("--step", default="all", choices=["1", "2", "4", "5", "all"])
    ap.add_argument("--id", default=None)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--reps", type=int, default=24)   # 12 THIẾU LỰC: phán quyết lật
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--recourse", action="store_true",
                    help="sửa tối thiểu gì thì hệ xếp lại mức")
    ap.add_argument("--selective", action="store_true",
                    help="lời giải thích có dùng để TỪ CHỐI trả lời được không")
    ap.add_argument("--coverage", action="store_true",
                    help="tỉ lệ câu dựng được phản thực, theo nhánh và theo trục")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cert = certificate(args.subject)
    if args.step == "1":
        print_certificate(args.subject, cert)
        return

    ctx = Ctx(args.subject, args.seed)
    if args.coverage:
        res = coverage(ctx, args.seed)
        if args.out:
            Path(args.out).write_text(
                json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    if args.recourse:
        one = ctx.index.get(args.id) if args.id else None
        res = recourse(ctx, args.n, args.reps, args.seed, one,
                       certificate(args.subject))
        if args.out:
            Path(args.out).write_text(
                json.dumps(res, ensure_ascii=False, indent=2, default=float),
                encoding="utf-8")
        return
    if args.selective:
        res = selective(ctx, certificate(args.subject), args.n, args.reps,
                        args.seed)
        if args.out:
            Path(args.out).write_text(
                json.dumps(res, ensure_ascii=False, indent=2, default=float),
                encoding="utf-8")
        return
    if args.validate:
        res = validate(ctx, args.n, args.reps, args.seed)
        if args.out:
            Path(args.out).write_text(
                json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    if args.step == "all":
        print_certificate(args.subject, cert)
        print()
    if args.id:
        if args.id not in ctx.index:
            sys.exit(f"không tìm thấy id {args.id}")
        picks = [ctx.index[args.id]]
    else:
        rs = np.random.default_rng(args.seed)
        picks = sorted(rs.choice(len(ctx.items),
                                 size=min(args.n, len(ctx.items)),
                                 replace=False).tolist())
    print(f"GIẢI THÍCH ĐỘ KHÓ — môn {args.subject} · {len(ctx.items)} câu · "
          f"ontology {len(ctx.eng)} thực thể · {args.reps} lần can thiệp/nhánh")
    print()
    out = [explain(ctx, i, cert, args.reps, args.seed,
                   show_steps=args.step in ("2", "all"))
           for i in picks]
    if args.out:
        Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2,
                                             default=float), encoding="utf-8")


if __name__ == "__main__":
    main()
