"""
Demo: run the Su9 pipeline on 10 sample questions of varying difficulty
and show (a) entity linking, (b) key features, (c) correlation with teacher-hinted
difficulty labels — a quick sanity check that the features track difficulty.
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "src"))
from pipeline import Su9DifficultyPipeline

ROOT = Path(__file__).parent


def main() -> None:
    # Load sample questions
    with open(ROOT / "data" / "sample_questions.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    qs = data["questions"]
    questions = [q["text"] for q in qs]
    ids = [q["id"] for q in qs]
    hints = [q["difficulty_hint"] for q in qs]

    # Build pipeline
    pipe = Su9DifficultyPipeline(ROOT / "ontology" / "su9.ttl")
    print(f"Ontology loaded: {len(pipe.store)} entities\n")

    # --- 1. Entity linking per question ---
    print("=" * 78)
    print("1. ENTITY LINKING")
    print("=" * 78)
    for q in qs:
        explanation = pipe.explain(q["text"])
        print(f"\n[{q['id']}] (hint={q['difficulty_hint']}) {q['text']}")
        if not explanation["mentions"]:
            print("   (no entities linked)")
        for m in explanation["mentions"]:
            short = m["uri"].split("#")[-1] if m["uri"] else "UNLINKED"
            print(f"   - [{m['class'] or 'UNK'}] {m['surface']!r} -> {short}")

    # --- 2. Feature matrix ---
    print("\n" + "=" * 78)
    print("2. FEATURE MATRIX (selected columns)")
    print("=" * 78)
    df = pipe.featurize(questions, ids=ids, include_meta=True)
    df["difficulty_hint"] = hints

    key_cols = [
        "question_id", "difficulty_hint",
        "num_unique_entities", "type_diversity",
        "abstractness_max", "prereq_depth_max",
        "sem_dist_max", "bloom_combined_max",
        "inv_freq_sum",
    ]
    print(df[key_cols].to_string(index=False))

    # --- 3. Correlation with teacher-hinted difficulty ---
    print("\n" + "=" * 78)
    print("3. FEATURE - DIFFICULTY CORRELATION (Spearman)")
    print("=" * 78)
    numeric = df.select_dtypes(include="number")
    corrs = (
        numeric.corr(method="spearman")["difficulty_hint"]
        .drop("difficulty_hint")
        .dropna()
        .sort_values(key=lambda x: x.abs(), ascending=False)
    )
    print("Top 12 features correlated with difficulty:")
    for name, rho in corrs.head(12).items():
        bar = "+" * int(abs(rho) * 20) if rho > 0 else "-" * int(abs(rho) * 20)
        print(f"  {name:30s} rho={rho:+.3f}  {bar}")

    # --- 4. Save ---
    out = ROOT / "data" / "features_demo.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"\nSaved feature matrix to: {out}")


if __name__ == "__main__":
    main()
