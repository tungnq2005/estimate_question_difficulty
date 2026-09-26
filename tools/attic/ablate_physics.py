# -*- coding: utf-8 -*-
"""Ablation công bằng cho KG trên 1539 câu Lý (nhãn NB/TH/VD/VDC).

Trả lời câu hỏi: KG có giá trị BIÊN nào trên numeric không, và trong-nhóm
câu tính toán (VD vs VDC) KG có phân biệt được không.

Feature set:
  numeric = 4 feature numeric_features.py + numeric_option_count (proxy mạnh)
  kg      = entity match + prereq depth (correct/distractors/max)

Đánh giá: XGBoost 4 lớp, 5-fold CV -> QWK (quadratic kappa) + macro-F1 + acc.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, f1_score, accuracy_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from shared.mcq.numeric_features import compute_numeric_features  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

LEVEL = {"NB": 0, "TH": 1, "VD": 2, "VDC": 3}
NUM_RE = re.compile(r"\d")


def build_features():
    eng = OntologyEngine.for_subject("physics")
    rows = json.loads(Path("subjects/physics/samples/mcq_kenhgiaovien.json").read_text(encoding="utf-8"))
    recs = []
    for q in rows:
        y = LEVEL[q["difficulty"]]
        stem, correct = q["stem"], q["correct"]
        dist = q["distractors"]
        opts = [correct] + dist
        ents = [eng.extract_entities_from_text(o) for o in opts]
        stem_ents = eng.extract_entities_from_text(stem)

        numf = compute_numeric_features(stem, correct, dist, stem_ents, eng)

        dc = [eng.prerequisite_depth(e.uri) for e in ents[0]]
        dd = [eng.prerequisite_depth(e.uri) for e in ents[1:] for e in e]
        recs.append({
            "y": y,
            # numeric (5)
            "num_answer_present": numf["numeric_answer_present"],
            "num_mag_ratio": numf["numeric_magnitude_ratio_to_correct"],
            "num_recip_swap": numf["numeric_reciprocal_swap_match"],
            "num_formula_family": numf["numeric_same_formula_family"],
            "num_option_count": sum(1 for o in opts if NUM_RE.search(o)),
            # kg (6)
            "kg_entity_match_coverage": sum(1 for e in ents if e) / 4,
            "kg_num_correct": len(ents[0]),
            "kg_num_distractor": sum(len(e) for e in ents[1:]) / 3,
            "kg_prereq_correct": sum(dc) / len(dc) if dc else 0.0,
            "kg_prereq_distractor": sum(dd) / len(dd) if dd else 0.0,
            "kg_prereq_max": max(dc + dd) if (dc + dd) else 0.0,
        })
    return pd.DataFrame(recs)


NUMERIC = ["num_answer_present", "num_mag_ratio", "num_recip_swap",
           "num_formula_family", "num_option_count"]
KG = ["kg_entity_match_coverage", "kg_num_correct", "kg_num_distractor",
      "kg_prereq_correct", "kg_prereq_distractor", "kg_prereq_max"]


def cv_eval(X, y):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    qwk, f1, acc = [], [], []
    for tr, te in skf.split(X, y):
        m = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                          subsample=0.8, colsample_bytree=0.8, random_state=42,
                          eval_metric="mlogloss", verbosity=0)
        m.fit(X.iloc[tr], y[tr])
        p = m.predict(X.iloc[te])
        qwk.append(cohen_kappa_score(y[te], p, weights="quadratic"))
        f1.append(f1_score(y[te], p, average="macro"))
        acc.append(accuracy_score(y[te], p))
    return np.mean(qwk), np.mean(f1), np.mean(acc)


def main():
    df = build_features()
    y = df["y"].values
    print(f"{len(df)} câu | phân bố: " + str(dict(pd.Series(y).value_counts().sort_index())))
    print(f"\n{'feature set':16s} {'QWK':>7s} {'macro-F1':>9s} {'acc':>7s}")

    configs = [("numeric", NUMERIC), ("kg", KG), ("numeric+kg", NUMERIC + KG)]
    results = {}
    for name, cols in configs:
        qwk, f1, acc = cv_eval(df[cols], y)
        results[name] = (qwk, f1, acc)
        print(f"{name:16s} {qwk:7.3f} {f1:9.3f} {acc:7.3f}")

    # baseline: luôn đoán lớp đông nhất (TH)
    maj = pd.Series(y).value_counts().idxmax()
    base_acc = (y == maj).mean()
    print(f"\nbaseline (đoán lớp đông nhất): acc={base_acc:.3f}")

    # ===== (2) Trong-nhóm: VD vs VDC, KG có phân biệt được không =====
    print("\n===== TRONG-NHÓM: VD vs VDC (đều là câu tính toán) =====")
    sub = df[df["y"].isin([2, 3])].copy()
    sub["bin"] = (sub["y"] == 3).astype(int)  # 0=VD, 1=VDC
    print(f"VD={sum(sub['bin']==0)}, VDC={sum(sub['bin']==1)}")
    for c in KG + NUMERIC:
        corr = sub["bin"].corr(sub[c], method="spearman")
        print(f"  {c:26s} Spearman vs VD/VDC = {corr:+.3f}")
    # XGBoost kg-only dự đoán VD vs VDC (binary)
    qwk, f1, acc = cv_eval(sub[KG], sub["bin"].values)
    print(f"  XGBoost KG-only (VD vs VDC): QWK={qwk:.3f} F1={f1:.3f} acc={acc:.3f} "
          f"(baseline đoán VD={max((sub['bin']==0).mean(), (sub['bin']==1).mean()):.3f})")


if __name__ == "__main__":
    main()
