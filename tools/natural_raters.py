# -*- coding: utf-8 -*-
"""Người chấm TỰ NHIÊN — đo độ tin cậy nhãn GIÁO VIÊN mà không cần tuyển ai.

(Khác `tools/label_reliability.py`: công cụ đó đo độ ổn định của nhãn LLM —
test-retest trên nhóm trùng của bộ Sử crawl. Công cụ này đo nhãn GIÁO VIÊN.)

Cùng một câu (câu dẫn, bộ phương án, đáp án y hệt sau chuẩn hoá) xuất hiện hai
lần trong ngân hàng đề và được gán nhãn riêng ở mỗi lần. Mỗi cặp như vậy là một
lần QUY TRÌNH GÁN NHÃN tự chấm lại chính nó.

Ba câu hỏi, đều trên CÙNG một tập câu:
  (1) người–người : hai lần gán nhãn cho cùng một câu khớp nhau tới đâu
  (2) máy–người   : mô hình khớp với từng lần gán nhãn tới đâu. Mô hình chia lát
                    THEO NHÓM câu dẫn, nên không bản sao nào vừa học vừa kiểm.
                    Đây là phép so chuẩn của chấm tự động: máy–người đặt cạnh
                    người–người, trên cùng các câu.
  (3) trần        : một mô hình hoàn hảo cũng chỉ đạt ≈ √(người–người)

Khoảng tin cậy: bootstrap theo NHÓM câu dẫn (một câu lặp ba lần tạo ba cặp
không độc lập), 2.000 lần, seed cố định.

Phụ: cặp ĐỒNG DẠNG — câu dẫn giống hệt nhau khi che các con số (cùng một khuôn
bài, khác số liệu). Mức nhận thức không nên đổi khi chỉ đổi số, nên đây là một
phép đo độ tin cậy kiểu "đề song song". Báo cáo RIÊNG, không gộp.

Chạy:  python tools/natural_raters.py
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import GroupKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

SEED = 42
N_BOOT = 2000
OUT = f"docs/natural_raters{cv.BACKEND_SUFFIX}.json"


def norm(t):
    return re.sub(r"[^0-9a-zà-ỹA-ZÀ-Ỹ]+", " ", (t or "").lower()).strip()


def key_of(q):
    """Khoá 'câu y hệt': câu dẫn + đáp án + TẬP phương án (bỏ qua thứ tự)."""
    opts = tuple(sorted([norm(q["correct"])] +
                        [norm(d) for d in (q.get("distractors") or [])]))
    return norm(q["stem"]), norm(q["correct"]), opts


def mask_num(t):
    return re.sub(r"\d+", "#", t)


def kappa(a, b, weights=None):
    if len(set(a) | set(b)) < 2:
        return float("nan")
    return float(cohen_kappa_score(a, b, weights=weights))


def human_human(pairs, tier=False):
    """Đối xứng: thứ tự hai lần gán nhãn là tuỳ ý nên tính cả hai chiều."""
    f = (lambda v: int(v >= 2)) if tier else (lambda v: v)
    a = [f(p["la"]) for p in pairs] + [f(p["lb"]) for p in pairs]
    b = [f(p["lb"]) for p in pairs] + [f(p["la"]) for p in pairs]
    return kappa(a, b, None if tier else "quadratic")


def machine_human(pairs, tier=False):
    f = (lambda v: int(v >= 2)) if tier else (lambda v: v)
    m = [f(p["pred"]) for p in pairs] * 2
    h = [f(p["la"]) for p in pairs] + [f(p["lb"]) for p in pairs]
    return kappa(m, h, None if tier else "quadratic")


def grouped_oof(subject):
    """Dự đoán out-of-fold, chia lát THEO NHÓM câu dẫn (cùng tham số XGBoost
    với `cv.fit_out_of_fold`) — bản sao luôn nằm cùng lát."""
    cfg = cv.SUBJECTS[subject]
    eng = OntologyEngine.for_subject(cv.ontology_of(subject))
    fz = cv.Featurizer(eng, cfg["surface"])
    items = cv.load_items(subject)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    cols = cv.model_cols(cfg["surface"])
    X = pd.DataFrame([fz(q["stem"], q["correct"], q["distractors"])
                      for q in items])[cols]
    groups = np.array([norm(q["stem"]) for q in items])
    if cv.IS_TEXT:
        import text_backend as tb
        return items, y, tb.grouped_fit(X, y, groups, SEED, cols)
    pred = np.zeros(len(y), dtype=int)
    for tr, te in GroupKFold(n_splits=5).split(X, y, groups):
        m = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                          subsample=0.8, colsample_bytree=0.8,
                          random_state=SEED, eval_metric="mlogloss",
                          verbosity=0)
        m.fit(X.iloc[tr], y[tr])
        pred[te] = m.predict_proba(X.iloc[te]).argmax(axis=1)
    return items, y, pred


def boot(pairs, fns, rng):
    clusters = sorted({p["g"] for p in pairs})
    by = defaultdict(list)
    for p in pairs:
        by[p["g"]].append(p)
    out = {k: [] for k in fns}
    for _ in range(N_BOOT):
        pick = rng.choice(len(clusters), size=len(clusters), replace=True)
        sample = [p for c in pick for p in by[clusters[c]]]
        for k, f in fns.items():
            out[k].append(f(sample))
    return {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))]
            for k, v in out.items()}


def analyse(subject, rng):
    cfg = cv.SUBJECTS[subject]
    lf, lm = cfg["label_field"], cfg["label_map"]
    raw = [q for q in json.loads(Path(cfg["path"]).read_text(encoding="utf-8"))
           if q.get(lf) in lm]
    items, y, pred = grouped_oof(subject)
    pred_of = {}
    for q, p in zip(items, pred):
        pred_of.setdefault(key_of(q), int(p))

    by = defaultdict(list)
    for q in raw:
        by[norm(q["stem"])].append(q)
    pairs = []
    for g, qs in by.items():
        for a, b in itertools.combinations(qs, 2):
            if key_of(a) != key_of(b):
                continue
            pairs.append({"g": g, "la": lm[a[lf]], "lb": lm[b[lf]],
                          "pred": pred_of.get(key_of(a)),
                          "cross_page": a.get("source") != b.get("source")})
    P = [p for p in pairs if p["pred"] is not None]

    fns = {
        "hh": lambda s: human_human(s),
        "mh": lambda s: machine_human(s),
        "diff": lambda s: machine_human(s) - human_human(s),
        "hh_tier": lambda s: human_human(s, tier=True),
        "mh_tier": lambda s: machine_human(s, tier=True),
    }
    point = {k: f(P) for k, f in fns.items()}
    ci = boot(P, fns, rng)

    # đồng dạng: che số trong câu dẫn thì giống nhau, nhưng câu dẫn gốc khác nhau
    iso_by = defaultdict(list)
    for q in raw:
        iso_by[mask_num(norm(q["stem"]))].append(q)
    iso = []
    for g, qs in iso_by.items():
        for a, b in itertools.combinations(qs, 2):
            if norm(a["stem"]) != norm(b["stem"]):
                iso.append({"g": g, "la": lm[a[lf]], "lb": lm[b[lf]]})
    iso_res = None
    if len(iso) >= 10:
        iso_res = {"pairs": len(iso), "clusters": len({p["g"] for p in iso}),
                   "hh": human_human(iso),
                   "agree": float(np.mean([p["la"] == p["lb"] for p in iso])),
                   "ci": boot(iso, {"hh": lambda s: human_human(s)}, rng)["hh"]}

    overall = kappa(list(y), list(pred), "quadratic")
    res = {
        "label_by": cfg.get("label_by"), "n_items_model": len(items),
        "model_grouped_qwk_all_items": overall,
        "pairs_all": len(pairs), "pairs_with_pred": len(P),
        "clusters": len({p["g"] for p in P}),
        "cross_page_pairs": int(sum(p["cross_page"] for p in P)),
        "agree_hh": float(np.mean([p["la"] == p["lb"] for p in P])),
        "agree_mh": float(np.mean([p["pred"] == p["la"] for p in P] +
                                  [p["pred"] == p["lb"] for p in P])),
        "qwk_human_human": point["hh"], "qwk_machine_human": point["mh"],
        "diff_machine_minus_human": point["diff"],
        "kappa2_human_human": point["hh_tier"],
        "kappa2_machine_human": point["mh_tier"],
        "ceiling_sqrt_hh": float(np.sqrt(max(point["hh"], 0.0))),
        "ci95": ci, "n_boot": N_BOOT, "isomorphic": iso_res,
    }

    print("=" * 78)
    print(f"NGƯỜI CHẤM TỰ NHIÊN — môn {subject} | nhãn: {cfg.get('label_by')}")
    print("=" * 78)
    print(f"  cặp câu y hệt: {len(pairs)} (có dự đoán: {len(P)}; "
          f"{res['clusters']} nhóm; {res['cross_page_pairs']} cặp khác trang)")
    print(f"  {'':24s}{'4 mức QWK':>22s}{'2 tầng κ':>22s}{'khớp':>8s}")
    print(f"  {'người–người':24s}{point['hh']:>8.3f} [{ci['hh'][0]:+.2f}; {ci['hh'][1]:+.2f}]"
          f"{point['hh_tier']:>8.3f} [{ci['hh_tier'][0]:+.2f}; {ci['hh_tier'][1]:+.2f}]"
          f"{res['agree_hh']:>8.1%}")
    print(f"  {'máy–người (cùng câu)':24s}{point['mh']:>8.3f} [{ci['mh'][0]:+.2f}; {ci['mh'][1]:+.2f}]"
          f"{point['mh_tier']:>8.3f} [{ci['mh_tier'][0]:+.2f}; {ci['mh_tier'][1]:+.2f}]"
          f"{res['agree_mh']:>8.1%}")
    print(f"  chênh máy − người (QWK): {point['diff']:+.3f} "
          f"[{ci['diff'][0]:+.3f}; {ci['diff'][1]:+.3f}]")
    print(f"  trần mô hình hoàn hảo ≈ √(người–người) = {res['ceiling_sqrt_hh']:.3f}")
    print(f"  (tham chiếu: mô hình trên TOÀN bộ {len(items)} câu, chia lát theo nhóm: "
          f"QWK {overall:.3f})")
    lo, hi = ci["diff"]
    if lo <= 0 <= hi:
        print("  ⇒ Máy và một lần gán nhãn khác KHÔNG phân biệt được về độ khớp với")
        print("    nhãn: khoảng tin cậy của chênh lệch chứa 0.")
    elif hi < 0:
        print("  ⇒ Máy khớp nhãn KÉM hơn một lần gán nhãn khác (khoảng tin cậy < 0).")
    else:
        print("  ⇒ Máy khớp nhãn HƠN một lần gán nhãn khác (khoảng tin cậy > 0).")
    if iso_res:
        print(f"  phụ — cặp ĐỒNG DẠNG (chỉ khác số liệu): {iso_res['pairs']} cặp, "
              f"QWK {iso_res['hh']:.3f} [{iso_res['ci'][0]:+.2f}; {iso_res['ci'][1]:+.2f}], "
              f"khớp {iso_res['agree']:.1%}")
    print()
    return res


def main():
    rng = np.random.default_rng(SEED)
    res = {s: analyse(s, rng) for s in ["physics", "history_gv"]}
    Path(OUT).write_text(json.dumps(res, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"→ {OUT}")


if __name__ == "__main__":
    main()
