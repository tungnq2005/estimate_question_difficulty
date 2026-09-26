# -*- coding: utf-8 -*-
"""Phát hiện & đánh dấu câu hỏi trùng lặp trong bộ MCQ.

VÌ SAO CẦN: bộ câu hỏi crawl từ nhiều trang của cùng một họ nguồn (SGK cũ +
3 bộ SGK mới) chứa nhiều bản sao của cùng một câu. Khi chia train/test ngẫu
nhiên, bản sao rơi vào cả hai phía -> mô hình chỉ cần thuộc lòng -> mọi chỉ số
bị thổi phồng (đo được: accuracy 75,6% -> 61,6% sau khi chặn rò rỉ).

CÁCH LÀM: không xoá dữ liệu (giữ nguyên vết crawl để truy nguồn), chỉ ĐÁNH DẤU:
  - dup_group   : id của nhóm nội dung (các bản sao cùng nhóm)
  - is_canonical: True cho đúng 1 bản đại diện mỗi nhóm -> dùng để train/đánh giá

Ngoài trùng HỆT, script còn báo cáo trùng GẦN ĐÚNG (cosine TF-IDF ký tự) để
biết còn nguy cơ rò rỉ nào không.

Usage:
    python tools/dedup.py --subject history            # xem báo cáo (không ghi)
    python tools/dedup.py --subject history --write    # ghi cờ vào JSON
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
SAMPLE_FILES = ("mcq_samples.json", "mcq_crawled.json")


def content_key(q: dict) -> str:
    """Khoá nội dung: stem + đáp án đúng + 3 nhiễu (đã sắp xếp), bỏ mọi ký tự
    không phải chữ/số và không phân biệt hoa thường."""
    parts = [q["stem"], q["correct"]] + sorted(q["distractors"])
    return re.sub(r"\W+", "", "".join(parts).lower())


def stem_key(q: dict) -> str:
    return re.sub(r"\W+", "", q["stem"].lower())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="history")
    ap.add_argument("--write", action="store_true",
                    help="ghi cờ dup_group/is_canonical vào file JSON")
    ap.add_argument("--near-threshold", type=float, default=0.92,
                    help="ngưỡng cosine coi là trùng gần đúng (mặc định 0.92)")
    args = ap.parse_args()

    base = REPO / "subjects" / args.subject / "samples"
    files = {f: json.loads((base / f).read_text(encoding="utf-8"))
             for f in SAMPLE_FILES if (base / f).exists()}
    allq = [q for rows in files.values() for q in rows]
    print(f"Tổng số câu: {len(allq)}")

    # ---------- 1. Trùng HỆT ----------
    groups: dict = {}
    for q in allq:
        groups.setdefault(content_key(q), []).append(q)
    dup_groups = {k: v for k, v in groups.items() if len(v) > 1}
    n_dup_rows = sum(len(v) for v in dup_groups.values())
    print(f"\n[1] TRÙNG HỆT (stem + 4 phương án)")
    print(f"  {len(groups)} nội dung khác nhau  |  {len(dup_groups)} nhóm có bản sao")
    print(f"  {n_dup_rows} câu nằm trong nhóm trùng ({n_dup_rows/len(allq):.1%} dữ liệu)")
    print(f"  -> còn lại sau khử trùng: {len(groups)} câu")
    if dup_groups:
        biggest = max(dup_groups.values(), key=len)
        print(f"  nhóm lớn nhất: {len(biggest)} bản sao — "
              f"\"{biggest[0]['stem'][:70]}...\"")

    # ---------- 2. Trùng stem nhưng khác phương án ----------
    stem_groups: dict = {}
    for k, v in groups.items():
        stem_groups.setdefault(stem_key(v[0]), set()).add(k)
    same_stem_diff_opts = {k: v for k, v in stem_groups.items() if len(v) > 1}
    print(f"\n[2] CÙNG STEM nhưng KHÁC phương án: {len(same_stem_diff_opts)} stem "
          f"(hợp lệ — cùng câu hỏi, bộ đáp án khác nhau)")

    # ---------- 3. Trùng GẦN ĐÚNG (trên các bản canonical) ----------
    canon = [v[0] for v in groups.values()]
    print(f"\n[3] TRÙNG GẦN ĐÚNG giữa {len(canon)} bản canonical "
          f"(cosine ký tự >= {args.near_threshold})")
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.neighbors import NearestNeighbors

        texts = [" ".join([q["stem"], q["correct"]] + list(q["distractors"]))
                 for q in canon]
        X = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                            min_df=2, max_features=200000).fit_transform(texts)
        nn = NearestNeighbors(n_neighbors=2, metric="cosine").fit(X)
        dist, idx = nn.kneighbors(X)
        sim = 1.0 - dist[:, 1]
        near = int((sim >= args.near_threshold).sum())
        print(f"  {near} câu có 'hàng xóm' vượt ngưỡng ({near/len(canon):.1%})")
        for lvl in (0.99, 0.97, 0.95, 0.92):
            print(f"    >= {lvl}: {(sim >= lvl).sum()} câu")
        if near:
            worst = int(np.argmax(sim))
            print(f"  ví dụ cặp giống nhất (cosine {sim[worst]:.3f}):")
            print(f"    A: {canon[worst]['stem'][:78]}")
            print(f"    B: {canon[idx[worst,1]]['stem'][:78]}")
        print("  -> trùng HỆT đã được chặn bằng StratifiedGroupKFold theo "
              "dup_group (tools/train.py, tools/ablation.py); nếu con số trùng "
              "GẦN ĐÚNG này lớn thì nên gom thêm cụm gần-đúng vào cùng nhóm")
    except ImportError:
        print("  (bỏ qua: cần scikit-learn)")

    # ---------- 4. Ghi cờ ----------
    if args.write:
        gid_of = {k: i for i, k in enumerate(groups)}
        canon_ids = {v[0]["id"] for v in groups.values()}
        for fname, rows in files.items():
            # mcq_samples.json (10 câu gốc) là mốc chuẩn bất biến của môn Sử —
            # không bao giờ ghi vào; 10 câu này vốn không có bản trùng nào.
            if fname == "mcq_samples.json":
                print(f"\n  bỏ qua {fname} (file mốc chuẩn, giữ nguyên)")
                continue
            for q in rows:
                q["dup_group"] = gid_of[content_key(q)]
                q["is_canonical"] = q["id"] in canon_ids
            p = base / fname
            p.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
            n_can = sum(1 for q in rows if q["is_canonical"])
            print(f"\n  đã ghi {fname}: {n_can}/{len(rows)} câu là canonical")
    else:
        print("\n  (chạy lại với --write để ghi cờ dup_group/is_canonical)")


if __name__ == "__main__":
    main()
