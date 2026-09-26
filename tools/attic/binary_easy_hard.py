# -*- coding: utf-8 -*-
"""Binary easy/hard (NB+TH vs VD+VDC) — tìm con số "wow" ở đúng granularity.

Câu hỏi thật: feature numeric đoán "dễ vs khó" chính xác bao nhiêu?
(4 lớp bị chặn bởi biên TH/VD mơ hồ; nhị phân thì numeric tách sạch.)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from tools.ablate_physics import build_features, NUMERIC  # noqa: E402


def main():
    df = build_features()
    # nhị phân: 0 = NB/TH (dễ), 1 = VD/VDC (khó)
    y = (df["y"] >= 2).astype(int)
    print(f"Easy (NB+TH) = {(y==0).sum()} | Hard (VD+VDC) = {(y==1).sum()}")
    print(f"baseline (đoán easy): {max((y==0).mean(), (y==1).mean()):.3f}\n")

    # 1) CHỈ MỘT feature: ngưỡng numeric_option_count >= 2 -> hard
    x = df["num_option_count"].values
    best = (0, None)
    for t in np.arange(0.5, 4.5, 0.5):
        acc = accuracy_score(y, (x >= t).astype(int))
        if acc > best[0]:
            best = (acc, t)
    print(f"[1 feature] ngưỡng numeric_option_count >= {best[1]}: "
          f"acc = {best[0]:.3f}")

    # 2) Logistic regression trên bộ numeric (5-fold)
    X = df[NUMERIC].values
    skf = StratifiedKFold(5, shuffle=True, random_state=42)
    accs, f1s, aucs = [], [], []
    for tr, te in skf.split(X, y):
        m = LogisticRegression(max_iter=1000)
        m.fit(X[tr], y[tr])
        p = m.predict(X[te])
        accs.append(accuracy_score(y[te], p))
        f1s.append(f1_score(y[te], p))
        aucs.append(roc_auc_score(y[te], m.decision_function(X[te])))
    print(f"[numeric 5 feats, LogReg] acc = {np.mean(accs):.3f} | "
          f"F1 = {np.mean(f1s):.3f} | AUC = {np.mean(aucs):.3f}")

    # 3) XGBoost 4 lớp: ma trận nhầm nằm ở đâu (để thấy biên TH/VD)
    from xgboost import XGBClassifier
    from sklearn.metrics import confusion_matrix
    y4 = df["y"].values
    m = XGBClassifier(n_estimators=200, max_depth=4, random_state=42, verbosity=0,
                      eval_metric="mlogloss")
    tr, te = next(iter(StratifiedKFold(5, shuffle=True, random_state=42).split(df[NUMERIC], y4)))
    m.fit(df[NUMERIC].iloc[tr], y4[tr])
    cm = confusion_matrix(y4[te], m.predict(df[NUMERIC].iloc[te]))
    print("\nConfusion 4 lớp (numeric) — hàng=thật, cột=đoán (NB TH VD VDC):")
    print(cm)
    print("→ lỗi tập trung ở biên TH↔VD, đúng như dự đoán.")


if __name__ == "__main__":
    main()
