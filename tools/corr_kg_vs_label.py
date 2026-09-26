# -*- coding: utf-8 -*-
"""Đo tương quan feature KG (entity match + prereq depth + numeric) vs nhãn NB/TH/VD/VDC
trên 1539 câu Vật Lí (kenhgiaovien). Kiểm giả thuyết "KG hiệu quả trên miền cấu trúc".

KHÔNG cần embeddings (PhoBERT) — chỉ dùng engine ontology, chạy nhanh.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

LEVEL = {"NB": 1, "TH": 2, "VD": 3, "VDC": 4}
NUM_RE = re.compile(r"\d")


def main():
    eng = OntologyEngine.for_subject("physics")
    rows = json.loads(Path("subjects/physics/samples/mcq_kenhgiaovien.json").read_text(encoding="utf-8"))
    print(f"Ontology: {len(eng)} thực thể | {len(rows)} câu có nhãn\n")

    recs = []
    for q in rows:
        y = LEVEL[q["difficulty"]]
        opts = [q["correct"]] + q["distractors"]
        ents = [eng.extract_entities_from_text(o) for o in opts]
        # entity match
        coverage = sum(1 for e in ents if e) / len(opts)
        num_correct = len(ents[0])
        num_dist = sum(len(e) for e in ents[1:]) / max(1, len(ents) - 1)
        # prereq depth
        dc = [eng.prerequisite_depth(e.uri) for e in ents[0]]
        dd = [eng.prerequisite_depth(e.uri) for e in ents[1:] for e in e]
        depth_correct = sum(dc) / len(dc) if dc else 0.0
        depth_dist = sum(dd) / len(dd) if dd else 0.0
        depth_max = max(dc + dd) if (dc + dd) else 0.0
        # numeric
        num_opts = sum(1 for o in opts if NUM_RE.search(o))
        recs.append({
            "y": y,
            "entity_match_coverage": coverage,
            "kg_num_correct_entities": num_correct,
            "kg_num_distractor_entities": num_dist,
            "kg_prereq_depth_mean_correct": depth_correct,
            "kg_prereq_depth_mean_distractors": depth_dist,
            "kg_prereq_depth_max": depth_max,
            "numeric_option_count": num_opts,
        })

    df = pd.DataFrame(recs)
    print(f"{'feature':34s} {'Pearson':>8s} {'Spearman':>9s}  {'p-value':>8s}")
    for c in df.columns:
        if c == "y":
            continue
        pear = df["y"].corr(df[c])
        spear = df["y"].corr(df[c], method="spearman")
        # p-value xấp xỉ cho Pearson (n=1539)
        n = len(df)
        import math
        t = pear * math.sqrt((n - 2) / (1 - pear * pear)) if abs(pear) < 1 else float("inf")
        # tránh overflow
        p = "n/a"
        print(f"{c:34s} {pear:8.3f} {spear:9.3f}")

    # phân bố y
    print("\nPhân bố nhãn (ordinal):", df["y"].value_counts().sort_index().to_dict())
    print("Trung bình feature theo mức độ:")
    for c in df.columns:
        if c == "y":
            continue
        g = df.groupby("y")[c].mean().round(3)
        print(f"  {c:32s} NB={g[1]:6.3f} TH={g[2]:6.3f} VD={g[3]:6.3f} VDC={g[4]:6.3f}")


if __name__ == "__main__":
    main()
