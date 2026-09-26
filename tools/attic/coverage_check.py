# -*- coding: utf-8 -*-
"""Đo mức độ 'phủ' của ontology KG hiện tại (su9.ttl trên đĩa) trên tập câu hỏi
thuộc các chương MỚI hoàn thiện (Bài 21-24: Nga&Mỹ/Châu Á/Đổi mới VN/CMKHKT-
toàn cầu hoá) so với phần còn lại — dùng để đo trước/sau khi bổ sung dữ liệu
ontology cho các chương này (xem docs/DEFERRED.md, phiên làm việc T-ontology).

Không chạy full ablation CV (n=106 câu ở nhóm mới, quá nhỏ để CV 5-fold ổn
định) — thay vào đó đo trực tiếp mức độ "có dữ liệu" của đặc trưng KG:
  - entity_match_coverage trung bình (đã có sẵn trong features.py)
  - tỉ lệ NaN từng cột kg_/jaccard_/rsi_/kad_ (Block A+B)
Đây là phép đo TRỰC TIẾP giả thuyết "hiệu năng KG yếu vì ontology thiếu",
tách biệt với nhiễu do cỡ mẫu nhỏ của một phép đo accuracy đầy đủ.

Usage:
    python tools/coverage_check.py --tag before   # sau khi checkout ttl cũ
    python tools/coverage_check.py --tag after    # với ttl hiện tại
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from shared.mcq.ontology_bridge import OntologyEngine
from shared.mcq.features import MCQ, batch_extract_features, features_to_dataframe

# Khớp đúng với logic phân nhóm dùng ở phiên làm việc bổ sung Bài 21-24.
GROUP_PATTERNS = {
    "nga_my_1991": r"Li.n bang Nga|n.{0,3}c M[ýỹ].{0,15}1991|n.{0,3}c M[ýỹ] và Tây [ÂA]u t. n.m 1991",
    "chau_a_1991": r"Ch.u . t. n.m 1991",
    "doi_moi_vn":  r"Vi.t Nam t. n.m 1991|C.ng cu.c .*i m.i t. n.m 1991|Vi.t Nam tr.n .ư.ng .ổi m.i",
    "cmkhkt_tch":  r"C.ch m.ng khoa h.c.{0,4}k. thu.t và xu th. to.n c.u|khoa h.c – k. thu.t v. xu th. to.n c.u",
}


def load_canonical_labeled() -> list:
    p = REPO / "subjects" / "history" / "samples" / "mcq_crawled.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    return [d for d in data if d.get("is_canonical", True) and d.get("difficulty")]


def classify(rows: list) -> dict:
    groups = {k: [] for k in GROUP_PATTERNS}
    groups["khac"] = []
    for d in rows:
        src = d.get("source", "")
        hit = next((k for k, pat in GROUP_PATTERNS.items()
                   if re.search(pat, src, re.IGNORECASE)), None)
        (groups[hit] if hit else groups["khac"]).append(d)
    return groups


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True, help="nhãn cho lần đo này (before/after)")
    ap.add_argument("--out-dir", default="tools/_coverage_runs")
    args = ap.parse_args()

    rows = load_canonical_labeled()
    groups = classify(rows)
    moi_ids = set()
    for k in GROUP_PATTERNS:
        moi_ids.update(d["id"] for d in groups[k])
    print(f"Nhóm 'chương mới' (Bài 21-24, {len(moi_ids)} câu): " +
          ", ".join(f"{k}={len(groups[k])}" for k in GROUP_PATTERNS))
    print(f"Nhóm 'chương cũ' (còn lại): {len(groups['khac'])} câu")

    engine = OntologyEngine(REPO / "subjects" / "history" / "ontology" / "su9.ttl")
    mcqs = [MCQ(id=d["id"], stem=d["stem"], correct=d["correct"],
               distractors=d["distractors"], difficulty=d["difficulty"],
               source=d.get("source"), notes=d.get("notes")) for d in rows]
    feats = batch_extract_features(mcqs, engine, verbose=False)
    df = features_to_dataframe(feats)

    kg_cols = [c for c in df.columns if c.startswith(("kg_", "jaccard_", "rsi_", "kad_"))]
    df["group"] = df["mcq_id"].map(lambda i: "chuong_moi" if i in moi_ids else "chuong_cu")

    summary = []
    for g, sub in df.groupby("group"):
        row = {"group": g, "n": len(sub),
              "entity_match_coverage_mean": sub["entity_match_coverage"].mean()}
        nan_rates = sub[kg_cols].isna().mean()
        row["kg_nan_rate_mean"] = nan_rates.mean()
        summary.append(row)
    summary_df = pd.DataFrame(summary)
    print("\n=== TÓM TẮT ĐỘ PHỦ KG (tag=%s) ===" % args.tag)
    print(summary_df.to_string(index=False))

    out_dir = REPO / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"coverage_{args.tag}.csv"
    df[["mcq_id", "group", "entity_match_coverage"] + kg_cols].to_csv(out_path, index=False)
    summary_df.to_csv(out_dir / f"summary_{args.tag}.csv", index=False)
    print(f"\n  đã lưu -> {out_path}")


if __name__ == "__main__":
    main()
