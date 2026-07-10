# -*- coding: utf-8 -*-
"""Huấn luyện XGBoost phân loại độ khó MCQ cho một môn.

Nạp mọi nguồn câu hỏi có nhãn của môn (mcq_samples.json + mcq_crawled.json
nếu có), trích 34 features, train + đánh giá, in báo cáo.

Usage:
    python tools/train.py                      # history (mặc định)
    python tools/train.py --subject history --test-size 0.2
    python tools/train.py --csv out.csv        # lưu thêm ma trận feature
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from shared.mcq.ontology_bridge import OntologyEngine
from shared.mcq.features import (MCQ, batch_extract_features,
                                 features_to_dataframe, train_xgboost)
from shared.subjects import get_config

SAMPLE_FILES = ["mcq_samples.json", "mcq_crawled.json"]


def load_labeled_mcqs(cfg) -> list:
    mcqs, by_file = [], {}
    for fname in SAMPLE_FILES:
        path = cfg.dir / "samples" / fname
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        labeled = [r for r in rows if r.get("difficulty")]
        by_file[fname] = (len(labeled), len(rows))
        mcqs += [MCQ(id=r["id"], stem=r["stem"], correct=r["correct"],
                     distractors=r["distractors"], difficulty=r["difficulty"],
                     source=r.get("source"), notes=r.get("notes"))
                 for r in labeled]
    for fname, (labeled, total) in by_file.items():
        print(f"  {fname}: {labeled}/{total} câu có nhãn")
    return mcqs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="history")
    ap.add_argument("--test-size", type=float, default=0.2)
    ap.add_argument("--cv", type=int, default=0,
                    help="k>0: đánh giá bằng stratified k-fold CV thay vì 1 split")
    ap.add_argument("--csv", help="đường dẫn lưu ma trận feature (tuỳ chọn)")
    args = ap.parse_args()

    cfg = get_config(args.subject)
    print(f"=== TRAIN ĐỘ KHÓ MCQ: {args.subject.upper()} ===")
    mcqs = load_labeled_mcqs(cfg)
    if not mcqs:
        sys.exit("Không có câu hỏi nào có nhãn difficulty.")

    engine = OntologyEngine.for_subject(args.subject)
    print(f"\nTrích 34 features cho {len(mcqs)} câu...")
    feats = batch_extract_features(mcqs, engine, verbose=False)
    print(f"  xong: {len(feats)}/{len(mcqs)} câu")

    if args.csv:
        features_to_dataframe(feats).to_csv(args.csv, index=False, encoding="utf-8")
        print(f"  đã lưu feature matrix -> {args.csv}")

    result = train_xgboost(feats, test_size=args.test_size, cv_folds=args.cv)
    if "error" in result:
        sys.exit(f"Train lỗi: {result['error']}")

    eval_note = (f"{args.cv}-fold CV" if args.cv > 0
                 else f"test_size={args.test_size}")
    print(f"\n=== KẾT QUẢ ({eval_note}, n={result['n_samples']}) ===")
    print(f"Accuracy: {result['accuracy']:.4f}")
    print(result["classification_report"])
    print("Top 15 feature importance:")
    print(result["feature_importance"].head(15).to_string(index=False))


if __name__ == "__main__":
    main()
