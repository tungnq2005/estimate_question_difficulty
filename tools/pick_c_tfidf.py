# -*- coding: utf-8 -*-
"""Chọn C cho mô hình nền TF-IDF — MỘT LẦN, trên nhãn THẬT, rồi đóng đinh.

Vì sao phải có file này thay vì dùng LogisticRegressionCV: loạt kiểm tra tỉnh
táo huấn luyện 39 mô hình trên NHÃN XÁO và so chúng với mô hình nhãn thật. Nếu
C được dò lại ở mỗi lần chạy thì mỗi mô hình được chỉnh riêng cho dữ liệu của
nó — mô hình nhãn xáo cũng vậy — và phép so mất nghĩa. Nên C phải là một hằng
số chọn một lần, ghi vào `text_backend.C_TFIDF`, và dùng y hệt ở mọi lần chạy.

Đây đúng là luật đã dùng cho `C_LR` của mô hình PhoBERT.

Chạy:  python tools/pick_c_tfidf.py
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import StratifiedKFold

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
import text_backend as tb  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

# Lưới đã dò: 1 / 4 / 16 / 64 / 256. Cực đại nằm TRONG lưới ở C = 16
# (trung bình hai môn 0,4478 · 0,4675 · 0,4798 · 0,4715 · 0,4597),
# nên không phải giá trị mép — đó là lý do phải nới lưới lần hai.
GRID = [1.0, 4.0, 16.0, 64.0, 256.0]
SEED = 42


def load(subject):
    cfg = cv.SUBJECTS[subject]
    eng = OntologyEngine.for_subject(cv.ontology_of(subject))
    fz = cv.Featurizer(eng, cfg["surface"])
    items = cv.load_items(subject)
    cols = cv.SURFACE_COLS[cfg["surface"]] + cv.KG_COLS
    X = pd.DataFrame([fz(q["stem"], q["correct"], q["distractors"])
                      for q in items])
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    return X, y, cols


def qwk_at(C, X, y, cols):
    tb.C_TFIDF = C
    pred = np.zeros(len(y), dtype=int)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED).split(X, y):
        m = tb._fit_fold(X, y, tr, cols)
        pred[te] = m.predict_proba(X.iloc[te]).argmax(axis=1)
    return float(cohen_kappa_score(y, pred, weights="quadratic"))


def main():
    if not tb.USE_TFIDF:
        sys.exit("chạy với QDE_BACKEND=tfidf")
    res = {}
    for subject in ("physics", "history_gv"):
        X, y, cols = load(subject)
        res[subject] = {C: qwk_at(C, X, y, cols) for C in GRID}
        for C, q in res[subject].items():
            print(f"{subject:12s} C={C:5.1f}  QWK {q:.4f}", flush=True)
    avg = {C: float(np.mean([res[s][C] for s in res])) for C in GRID}
    best = max(avg, key=avg.get)
    print("\ntrung bình hai môn: " +
          "  ".join(f"C={C:g} → {q:.4f}" for C, q in avg.items()))
    print(f"→ chọn C_TFIDF = {best:g}  (ghi vào tools/text_backend.py)")


if __name__ == "__main__":
    main()
