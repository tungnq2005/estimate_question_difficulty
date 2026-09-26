# -*- coding: utf-8 -*-
"""Huấn luyện XGBoost phân loại độ khó MCQ cho một môn.

Nạp mọi nguồn câu hỏi có nhãn của môn (mcq_samples.json + mcq_crawled.json
nếu có), trích đặc trưng, train + đánh giá, in báo cáo.

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


def load_labeled_mcqs(cfg, keep_duplicates: bool = False):
    """Nạp câu hỏi có nhãn. Trả (mcqs, groups) với groups: mcq_id -> dup_group.

    Hai cách chặn rò rỉ do bản sao (bộ crawl chứa ~55% bản sao — để nguyên thì
    bản sao rơi vào cả train lẫn test, mô hình thuộc lòng, chỉ số bị thổi phồng
    ~14 điểm; xem tools/dedup.py):

      - mặc định: chỉ lấy bản canonical (mỗi nội dung 1 bản) — đơn giản nhưng
        vứt đi ~1.000 câu;
      - --keep-duplicates: giữ hết, và dùng `groups` để StratifiedGroupKFold
        nhốt mọi bản sao vào cùng một fold — giữ được toàn bộ dữ liệu train
        mà vẫn không rò rỉ. Đây là cách dùng ĐÚNG của cờ này.
    """
    mcqs, groups, by_file = [], {}, {}
    for fname in SAMPLE_FILES:
        path = cfg.dir / "samples" / fname
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        labeled = [r for r in rows if r.get("difficulty")]
        if not keep_duplicates:
            labeled = [r for r in labeled if r.get("is_canonical", True)]
        by_file[fname] = (len(labeled), len(rows))
        for r in labeled:
            mcqs.append(MCQ(id=r["id"], stem=r["stem"], correct=r["correct"],
                            distractors=r["distractors"],
                            difficulty=r["difficulty"],
                            source=r.get("source"), notes=r.get("notes")))
            if r.get("dup_group") is not None:
                groups[r["id"]] = r["dup_group"]
    for fname, (labeled, total) in by_file.items():
        note = "" if keep_duplicates else " (đã khử trùng lặp)"
        print(f"  {fname}: {labeled}/{total} câu dùng để train{note}")
    return mcqs, groups


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="history")
    ap.add_argument("--test-size", type=float, default=0.2)
    ap.add_argument("--cv", type=int, default=0,
                    help="k>0: đánh giá bằng stratified k-fold CV thay vì 1 split")
    ap.add_argument("--csv", help="đường dẫn lưu ma trận feature (tuỳ chọn)")
    ap.add_argument("--keep-duplicates", action="store_true",
                    help="giữ cả bản sao (CHỈ để tái hiện kết quả cũ — số liệu "
                         "sẽ bị thổi phồng do rò rỉ giữa các fold)")
    args = ap.parse_args()

    cfg = get_config(args.subject)
    print(f"=== TRAIN ĐỘ KHÓ MCQ: {args.subject.upper()} ===")
    mcqs, groups = load_labeled_mcqs(cfg, keep_duplicates=args.keep_duplicates)
    if not mcqs:
        sys.exit("Không có câu hỏi nào có nhãn difficulty.")

    engine = OntologyEngine.for_subject(args.subject)
    print(f"\nTrích đặc trưng cho {len(mcqs)} câu...")
    feats = batch_extract_features(mcqs, engine, verbose=False)
    print(f"  xong: {len(feats)}/{len(mcqs)} câu")

    if args.csv:
        features_to_dataframe(feats).to_csv(args.csv, index=False, encoding="utf-8")
        print(f"  đã lưu feature matrix -> {args.csv}")

    result = train_xgboost(feats, test_size=args.test_size, cv_folds=args.cv,
                           groups=groups)
    if "error" in result:
        sys.exit(f"Train lỗi: {result['error']}")

    eval_note = (result.get("cv_scheme") if args.cv > 0
                 else f"test_size={args.test_size}")
    print(f"\n=== KẾT QUẢ ({eval_note}, n={result['n_samples']}) ===")
    print(f"Accuracy: {result['accuracy']:.4f}")
    print(result["classification_report"])
    print("Top 15 feature importance:")
    print(result["feature_importance"].head(15).to_string(index=False))


if __name__ == "__main__":
    main()
