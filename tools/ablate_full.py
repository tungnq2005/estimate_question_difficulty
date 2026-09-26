# -*- coding: utf-8 -*-
"""Ablation với khối KG ĐẦY ĐỦ — thay cho tools/ablate_physics.py.

Vì sao cần: `ablate_physics.py` dùng khối KG chỉ gồm entity coverage / số thực
thể / độ sâu tiên quyết. Nó KHÔNG có `kad_path_distance_mean`, `jaccard_kg_*`,
`rsi_dc` — tức ba đại lượng vận hành hoá **chính giả thuyết gốc** của đề tài
(Vinu 2015: độ khó = độ tương tự giữa đáp án đúng và nhiễu), dù `shared/mcq/`
đã viết sẵn cả ba. Kết luận "KG thêm ~0 giá trị biên" trong
`docs/PHYSICS_EXPERIMENT.md` §5 vì thế chưa kiểm đúng thứ nó định bác.

Công cụ này chạy cùng một ablation cho CẢ HAI môn, tách khối KG thành ba lát để
thấy phần nào của ontology thật sự đóng góp:

    bề mặt              trục bề mặt của môn (Lý: numeric · Sử: hành văn)
    KG (khối cũ)        đúng khối của ablate_physics.py — để so sánh lịch sử
    KG lõi giả thuyết   path distance + jaccard_kg + rsi_dc (Vinu)
    KG đầy đủ           10 cột
    bề mặt + KG đầy đủ  giá trị BIÊN thật của ontology

Chạy:  python tools/ablate_full.py [--subject physics|history|both] [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

KG_OLD = ["kg_entity_match_coverage", "kg_num_correct", "kg_num_distractor",
          "kg_prereq_correct", "kg_prereq_distractor"]
KG_CORE = ["kad_path_distance_mean", "jaccard_kg_max", "jaccard_kg_mean", "rsi_dc"]


def cv_eval(X: pd.DataFrame, y: np.ndarray, seed: int):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    qwk, f1, acc = [], [], []
    for tr, te in skf.split(X, y):
        m = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                          subsample=0.8, colsample_bytree=0.8, random_state=seed,
                          eval_metric="mlogloss", verbosity=0)
        m.fit(X.iloc[tr], y[tr])
        p = m.predict(X.iloc[te])
        qwk.append(cohen_kappa_score(y[te], p, weights="quadratic"))
        f1.append(f1_score(y[te], p, average="macro"))
        acc.append(accuracy_score(y[te], p))
    return float(np.mean(qwk)), float(np.mean(f1)), float(np.mean(acc))


def run(subject: str, seed: int) -> dict:
    cfg = cv.SUBJECTS[subject]
    surf = cv.SURFACE_COLS[cfg["surface"]]
    eng = OntologyEngine.for_subject(cv.ontology_of(subject))
    fz = cv.Featurizer(eng, cfg["surface"])
    items = cv.load_items(subject)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    X = pd.DataFrame([fz(q["stem"], q["correct"], q["distractors"]) for q in items])

    print(f"\n===== {subject} | n={len(items)} | "
          f"nhãn: {cfg.get('label_by', '?')} | ontology {len(eng)} thực thể =====")
    print(f"{'bộ đặc trưng':26s} {'#cột':>5s} {'QWK':>7s} {'macro-F1':>9s} {'acc':>7s}")
    sets = [("bề mặt", surf), ("KG (khối cũ, thiếu)", KG_OLD),
            ("KG lõi giả thuyết", KG_CORE), ("KG đầy đủ", cv.KG_COLS),
            ("bề mặt + KG đầy đủ", surf + cv.KG_COLS)]
    res = {}
    for name, c in sets:
        q, f, a = cv_eval(X[c], y, seed)
        res[name] = {"n_cols": len(c), "qwk": q, "macro_f1": f, "acc": a}
        print(f"{name:26s} {len(c):5d} {q:7.3f} {f:9.3f} {a:7.3f}")
    maj = float((y == pd.Series(y).value_counts().idxmax()).mean())
    print(f"{'baseline (lớp đông nhất)':26s} {'—':>5s} {'—':>7s} {'—':>9s} {maj:7.3f}")

    gain_q = res["bề mặt + KG đầy đủ"]["qwk"] - res["bề mặt"]["qwk"]
    gain_f = res["bề mặt + KG đầy đủ"]["macro_f1"] - res["bề mặt"]["macro_f1"]
    print(f"\n⇒ giá trị BIÊN của ontology: QWK {gain_q:+.3f} · macro-F1 {gain_f:+.3f}")
    res["baseline_acc"] = maj
    res["marginal_gain"] = {"qwk": gain_q, "macro_f1": gain_f}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="both",
                    choices=sorted(cv.SUBJECTS) + ["both"])
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    subjects = sorted(cv.SUBJECTS) if args.subject == "both" else [args.subject]
    out = {}
    for s in subjects:
        out[s] = run(s, args.seed)
        op = cv.out_path(s, "ablation_full")
        Path(op).write_text(
            json.dumps({"subject": s, "label_by": cv.SUBJECTS[s].get("label_by"),
                        "seed": args.seed, "results": out[s]},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"→ {op}")


if __name__ == "__main__":
    main()
