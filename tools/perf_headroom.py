# -*- coding: utf-8 -*-
"""Còn bao nhiêu HIỆU NĂNG bỏ trên bàn — đo trước, rồi hãy quyết có đổi không.

Nhãn NB/TH/VD/VDC là thang CÓ THỨ TỰ, nhưng `fit_out_of_fold` đang học nó bằng
XGBoost multiclass — tức coi 4 mức là 4 lớp rời rạc, không biết VD gần VDC hơn
là gần NB. Trong khi chỉ số chính lại là QWK, thứ phạt theo BÌNH PHƯƠNG khoảng
cách. Đây là chỗ lệch giữa hàm mất mát và thước đo, và nó thường tốn vài điểm
QWK.

So sáu cấu hình trên CÙNG 5 lát, CÙNG seed, CÙNG bộ đặc trưng:

  A  multiclass                       (đang dùng)
  B  multiclass + cân trọng số lớp    (chữa lệch phân bố, VDC chỉ 14%)
  C  hồi quy + làm tròn 0,5/1,5/2,5   (thứ tự, ngưỡng ngây thơ)
  D  hồi quy + ngưỡng khớp phân vị    (thứ tự, ngưỡng học từ TẬP HUẤN LUYỆN)
  E  D + tinh chỉnh siêu tham số

Cả sáu chạy trên đúng bộ 15 cột mà lớp giải thích đang dùng. `cv.Featurizer`
không sinh cột nào ngoài bộ này — bộ 40 cột của `operation_axis.py` là featurizer
khác, và phần lớn cột ở đó (độ dài câu dẫn, vết giải LLM) nằm NGOÀI hai trục can
thiệp được, nên không dùng cho lớp giải thích.

Ngưỡng ở D/E học TỪ PHÂN BỐ NHÃN CỦA LÁT HUẤN LUYỆN rồi mới áp lên lát kiểm —
không nhìn nhãn kiểm, nên không rò rỉ.

Chạy:  python tools/perf_headroom.py --subject physics
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, f1_score, roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from xgboost import XGBClassifier, XGBRegressor

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402


def cuts_from_quantiles(y_train, pred_test):
    """Ngưỡng cắt sao cho PHÂN BỐ mức dự đoán khớp phân bố nhãn tập huấn luyện.

    Không nhìn nhãn của tập kiểm — chỉ nhìn phân bố lớp ở tập huấn luyện, thứ
    vốn đã biết trước khi dự đoán.
    """
    props = np.array([(y_train == k).mean() for k in range(4)])
    q = np.cumsum(props)[:-1]
    return np.quantile(pred_test, q)


def to_level(pred, cuts):
    return np.digitize(pred, cuts)


def metrics(y, lvl, score_high):
    return {
        "qwk": float(cohen_kappa_score(y, lvl, weights="quadratic")),
        "auc_high": float(roc_auc_score((y >= 2).astype(int), score_high)),
        "macro_f1": float(f1_score(y, lvl, average="macro")),
        "acc": float((y == lvl).mean()),
        "recall_vdc": float((lvl[y == 3] == 3).mean()) if (y == 3).any() else 0.0,
        "recall_vd": float((lvl[y == 2] == 2).mean()) if (y == 2).any() else 0.0,
    }


def run_config(X, y, seed, kind, weighted=False, cuts="round", params=None,
               groups=None):
    # groups=None → chia lát như hiện tại. groups cho trước → mọi câu TRÙNG NHAU
    # buộc nằm cùng một lát, nên bản sao không thể vừa huấn luyện vừa kiểm.
    skf = (StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
           if groups is None else GroupKFold(n_splits=5))
    lvl = np.zeros(len(y), dtype=int)
    hi = np.zeros(len(y))
    P = dict(n_estimators=200, max_depth=4, learning_rate=0.1, subsample=0.8,
             colsample_bytree=0.8, random_state=seed, verbosity=0)
    P.update(params or {})
    for tr, te in skf.split(X, y, groups):
        if kind == "clf":
            m = XGBClassifier(eval_metric="mlogloss", **P)
            w = None
            if weighted:
                cnt = np.bincount(y[tr], minlength=4).astype(float)
                w = (len(tr) / (4 * cnt))[y[tr]]
            m.fit(X.iloc[tr], y[tr], sample_weight=w)
            pr = m.predict_proba(X.iloc[te])
            lvl[te] = pr.argmax(axis=1)
            hi[te] = pr[:, 2:].sum(axis=1)
        else:
            m = XGBRegressor(objective="reg:squarederror", **P)
            m.fit(X.iloc[tr], y[tr])
            p = m.predict(X.iloc[te])
            hi[te] = p
            c = (np.array([0.5, 1.5, 2.5]) if cuts == "round"
                 else cuts_from_quantiles(y[tr], p))
            lvl[te] = to_level(p, c)
    return metrics(y, lvl, hi)


def load(subject, full=False):
    cfg = cv.SUBJECTS[subject]
    eng = OntologyEngine.for_subject(cv.ontology_of(subject))
    fz = cv.Featurizer(eng, cfg["surface"])
    items = cv.load_items(subject)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    cols = cv.SURFACE_COLS[cfg["surface"]] + cv.KG_COLS
    feats = [fz(q["stem"], q["correct"], q["distractors"]) for q in items]
    X = pd.DataFrame(feats)
    return (X if full else X[cols]), y, len(cols)


def leak_check(subject, seed):
    """Bản sao có đang vừa nằm ở tập huấn luyện vừa nằm ở tập kiểm không?

    Bộ Sử có sẵn `dup_group`/`is_canonical` và đang lọc. Bộ Lý KHÔNG có hai
    trường đó, nên chưa ai kiểm. Nếu có rò rỉ thì mọi con số của môn Lý đang
    CAO HƠN thực tế — và tối ưu thêm trên nền đó là tối ưu nhầm chỗ.
    """
    import re
    from collections import Counter, defaultdict
    cfg = cv.SUBJECTS[subject]
    items = cv.load_items(subject)
    X, y, _ = load(subject)

    def norm(t):
        return re.sub(r"[^0-9a-zà-ỹA-ZÀ-Ỹ]+", " ", (t or "").lower()).strip()

    key = [norm(q["stem"]) for q in items]
    idx = {}
    groups = np.zeros(len(items), dtype=int)
    for i, k in enumerate(key):
        groups[i] = idx.setdefault(k, len(idx))
    sizes = Counter(groups.tolist())
    multi = {g for g, c in sizes.items() if c > 1}
    n_dup = sum(sizes[g] for g in multi)

    # trong nhóm trùng câu dẫn: đáp án có giống nhau không, nhãn có giống nhau không
    by = defaultdict(list)
    for i, g in enumerate(groups):
        by[g].append(i)
    same_ans = same_lab = 0
    for g in multi:
        ii = by[g]
        same_ans += len({norm(items[i]["correct"]) for i in ii}) == 1
        same_lab += len({int(y[i]) for i in ii}) == 1

    print("=" * 78)
    print(f"KIỂM RÒ RỈ BẢN SAO — môn {subject} | {len(items)} câu")
    print("=" * 78)
    print(f"  nhóm trùng câu dẫn (chuẩn hoá) : {len(multi)} nhóm, "
          f"{n_dup} câu ({n_dup/len(items):.1%})")
    if multi:
        print(f"  trong đó cùng ĐÁP ÁN           : {same_ans}/{len(multi)} nhóm")
        print(f"  trong đó cùng NHÃN             : {same_lab}/{len(multi)} nhóm")
        print("  (cùng câu dẫn + cùng đáp án + cùng nhãn = bản sao thật; khác đáp")
        print("   án = câu khác nhau tình cờ chung câu dẫn, KHÔNG phải rò rỉ)")
    a_rnd = run_config(X, y, seed, "clf")
    a_grp = run_config(X, y, seed, "clf", groups=groups)
    print()
    print(f"  {'chia lát':34s}{'QWK':>8s}{'AUC cao':>9s}{'acc':>8s}")
    print(f"  {'hiện tại (phân tầng ngẫu nhiên)':34s}{a_rnd['qwk']:8.3f}"
          f"{a_rnd['auc_high']:9.3f}{a_rnd['acc']:8.3f}")
    print(f"  {'bản sao buộc cùng lát':34s}{a_grp['qwk']:8.3f}"
          f"{a_grp['auc_high']:9.3f}{a_grp['acc']:8.3f}")
    d = a_grp["qwk"] - a_rnd["qwk"]
    print(f"  {'chênh':34s}{d:+8.3f}{a_grp['auc_high']-a_rnd['auc_high']:+9.3f}"
          f"{a_grp['acc']-a_rnd['acc']:+8.3f}")
    print()
    if abs(d) < 0.02:
        print("  ⇒ KHÔNG có rò rỉ đáng kể. Số hiện tại đứng được.")
    else:
        print("  ⇒ CÓ chênh. Số hiện tại được bản sao đỡ một phần — phải báo cáo")
        print("    theo cách chia lát có nhóm, hoặc lọc bản sao như bộ Sử.")
    return {"n_groups_dup": len(multi), "n_items_dup": int(n_dup),
            "frac_dup": float(n_dup / len(items)),
            "same_answer_groups": int(same_ans), "same_label_groups": int(same_lab),
            "random_split": a_rnd, "grouped_split": a_grp,
            "delta_qwk": float(d)}


GRID = [
    dict(max_depth=3, n_estimators=400, learning_rate=0.05),
    dict(max_depth=4, n_estimators=400, learning_rate=0.05),
    dict(max_depth=6, n_estimators=300, learning_rate=0.05,
         min_child_weight=5),
    dict(max_depth=5, n_estimators=600, learning_rate=0.03,
         min_child_weight=3, reg_lambda=2.0),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="both")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--leak", action="store_true",
                    help="kiểm bản sao có rò rỉ giữa tập huấn luyện và kiểm không")
    ap.add_argument("--out", default="docs/perf_headroom.json")
    a = ap.parse_args()
    subs = (["physics", "history_gv"] if a.subject == "both" else [a.subject])
    out = {}
    if a.leak:
        res = {s_: leak_check(s_, a.seed) for s_ in subs}
        Path("docs/leak_check.json").write_text(
            json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
        print("→ docs/leak_check.json")
        return
    for sub in subs:
        X, y, ncol = load(sub)
        print("=" * 78)
        print(f"HEADROOM — môn {sub} | {len(y)} câu | {ncol} cột (bộ XAI đang dùng)")
        print("=" * 78)
        res = {}
        res["A · multiclass (đang dùng)"] = run_config(X, y, a.seed, "clf")
        res["B · multiclass + cân lớp"] = run_config(X, y, a.seed, "clf",
                                                     weighted=True)
        res["C · hồi quy + làm tròn"] = run_config(X, y, a.seed, "reg",
                                                   cuts="round")
        res["D · hồi quy + ngưỡng phân vị"] = run_config(X, y, a.seed, "reg",
                                                         cuts="quantile")
        best, bq = None, -9
        for g in GRID:
            r = run_config(X, y, a.seed, "reg", cuts="quantile", params=g)
            if r["qwk"] > bq:
                best, bq = (g, r), r["qwk"]
        res["E · D + tinh chỉnh"] = best[1]
        hdr = f"  {'cấu hình':30s}{'QWK':>8s}{'AUC cao':>9s}{'macroF1':>9s}" \
              f"{'acc':>7s}{'recVD':>7s}{'recVDC':>8s}"
        print(hdr)
        base = res["A · multiclass (đang dùng)"]
        for k, v in res.items():
            mark = "" if k.startswith("A") else f"  ({v['qwk']-base['qwk']:+.3f})"
            print(f"  {k:30s}{v['qwk']:8.3f}{v['auc_high']:9.3f}"
                  f"{v['macro_f1']:9.3f}{v['acc']:7.3f}{v['recall_vd']:7.3f}"
                  f"{v['recall_vdc']:8.3f}{mark}")
        print(f"\n  siêu tham số tốt nhất: {best[0]}")
        d_qwk = res["E · D + tinh chỉnh"]["qwk"] - base["qwk"]
        d_auc = res["E · D + tinh chỉnh"]["auc_high"] - base["auc_high"]
        print(f"  ĐÁNH ĐỔI: QWK {d_qwk:+.3f} nhưng AUC tầng cao {d_auc:+.3f}.")
        if d_qwk > 0 and d_auc < -0.01:
            print("  Hai thước đo BẤT ĐỒNG về việc thế nào là tốt hơn: hồi quy có")
            print("  thứ tự xếp hạng 4 mức khớp hơn, nhưng multiclass tách tầng cao")
            print("  tốt hơn. Không cấu hình nào thắng cả hai — phải chọn theo việc")
            print("  định dùng con số vào đâu.")
        b = res["B · multiclass + cân lớp"]
        print(f"  Cấu hình B giữ nguyên kiến trúc multiclass (nên predict_proba,")
        print(f"  entropy, SHAP và pipeline can thiệp không đổi bản chất): "
              f"QWK {b['qwk']-base['qwk']:+.3f}, "
              f"AUC {b['auc_high']-base['auc_high']:+.3f}, "
              f"recall VDC {base['recall_vdc']:.3f} → {b['recall_vdc']:.3f}.")
        out[sub] = {"n": int(len(y)), "n_cols": ncol,
                    "best_params": best[0], "results": res}
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2),
                           encoding="utf-8")
    print(f"\n→ {a.out}")


if __name__ == "__main__":
    main()
