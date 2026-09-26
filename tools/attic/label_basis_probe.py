# -*- coding: utf-8 -*-
"""Nhãn LLM và nhãn GIÁO VIÊN dựa vào cái gì để phán độ khó?

GIẢ THUYẾT (do người hướng dẫn đề tài nêu, 17/08/2026): LLM chấm độ khó chủ
yếu theo CÂU CHỮ (cách hành văn, dạng câu hỏi), còn giáo viên — người dạy thật
— coi trọng ĐỘ NHIỄU CỦA PHƯƠNG ÁN (distractor), vốn là thứ quyết định độ khó
thực tế của một câu trắc nghiệm.

Nếu đúng, đây là lời giải thích cơ học cho ba quan sát khó hiểu ở E1:
  - Cohen's κ(LLM, GV) ≈ -0,02  (hai bên gần như không đồng thuận)
  - nhãn LLM đơn điệu đúng chiều với p_sim, nhãn GV thì không
  - baseline TF-IDF thắng đậm trên nhãn LLM nhưng mất sạch tín hiệu trên p_sim
… tất cả đều là hệ quả của việc HAI NGUỒN NHÃN ĐANG ĐO HAI THỨ KHÁC NHAU,
chứ không phải "một bên đúng, một bên sai".

CÁCH KIỂM: chia đặc trưng thành hai nhóm tách biệt về ý nghĩa —

  [A] NHÓM PHƯƠNG ÁN/NHIỄU — đo quan hệ giữa đáp án đúng và các đáp án nhiễu:
      jaccard_* (trùng lặp thực thể đúng↔nhiễu), rsi_dc (distractor confusion),
      rsi_max_distractor, rsi_distractor_range, kad_path_distance_mean,
      kg_same_period/author_correct_distractor, emb_stem_distractor_*.
  [B] NHÓM CÂU CHỮ/STEM — chỉ phụ thuộc cách viết câu dẫn, KHÔNG phụ thuộc
      phương án nhiễu: độ dài stem, số từ, dạng phủ định, dạng câu hỏi,
      kad_entropy_stem, rsi_to_correct.

rồi so tương quan |Spearman| trung bình của mỗi nhóm với từng nguồn nhãn.
Giả thuyết đúng <=> nhóm [A] tương quan mạnh hơn với NHÃN GV, nhóm [B] tương
quan mạnh hơn với NHÃN LLM.

⚠ CỠ MẪU NHỎ (n≈76 câu có đủ cả 2 nhãn): mọi |ρ| < ~0,23 không khác 0 ở mức
5%. Script in kèm ngưỡng đó; KHÔNG diễn giải hiệu ứng dưới ngưỡng.

Usage:
    python tools/label_basis_probe.py \
        --teacher subjects/history/samples/su9_difficulty_teacher1_2026-08-17.json \
        --csv .cache/history_canonical.features.csv \
        --responses subjects/history/samples/student_responses.LLMSIM_API.csv
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
SAMPLES = REPO / "subjects" / "history" / "samples"
LABEL2ID = {"Easy": 0, "Medium": 1, "Hard": 2}
VERDICT2ID = {"easy": 0, "medium": 1, "hard": 2}

# --- [A] đặc trưng PHỤ THUỘC PHƯƠNG ÁN NHIỄU -------------------------------
DISTRACTOR_FEATS = [
    "jaccard_hard_max", "jaccard_hard_mean", "jaccard_soft_max",
    "jaccard_soft_mean", "jaccard_kg_max", "jaccard_kg_mean",
    "jaccard_stem_distractor_max",
    "rsi_dc", "rsi_max_distractor", "rsi_distractor_range", "rsi_final",
    "kad_path_distance_mean",
    "kg_num_distractor_entities", "kg_prereq_depth_mean_distractors",
    "kg_same_author_correct_distractor", "kg_same_period_correct_distractor",
    "kg_shared_theme_device_jaccard", "kg_entity_diversity",
    "emb_stem_distractor_mean_sim", "emb_stem_distractor_max_sim",
    "emb_stem_distractor_min_sim", "emb_stem_distractor_std_sim",
    "emb_discriminative_power",
]
# --- [B] đặc trưng CHỈ PHỤ THUỘC CÂU DẪN ------------------------------------
STEM_FEATS = ["kad_entropy_stem", "rsi_to_correct", "jaccard_stem_correct",
              "emb_stem_correct_sim"]

NEGATIVE_RE = re.compile(r"không phải|không đúng|ngoại trừ|không thuộc", re.I)


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 8 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return float("nan")
    return float(np.corrcoef(pd.Series(a[ok]).rank(), pd.Series(b[ok]).rank())[0, 1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--responses", required=True)
    args = ap.parse_args()

    tea_raw = json.loads((REPO / args.teacher).read_text(encoding="utf-8"))["responses"]
    teacher = {k: VERDICT2ID[v["verdict"]] for k, v in tea_raw.items()
               if v.get("verdict") in VERDICT2ID}

    bank = {}
    for f in ("mcq_samples.json", "mcq_crawled.json"):
        p = SAMPLES / f
        if p.exists():
            for r in json.loads(p.read_text(encoding="utf-8")):
                bank[r["id"]] = r

    resp = pd.read_csv(REPO / args.responses)
    p_sim = resp.groupby("item_id")["correct"].mean()

    feat = pd.read_csv(REPO / args.csv).set_index("mcq_id")

    ids = [i for i in teacher if i in feat.index and i in bank
           and bank[i].get("difficulty")]
    df = feat.loc[ids].copy()
    df["_gv"] = [teacher[i] for i in ids]
    df["_llm"] = [LABEL2ID[bank[i]["difficulty"]] for i in ids]
    df["_p"] = [p_sim.get(i, np.nan) for i in ids]

    # đặc trưng câu chữ tính trực tiếp từ văn bản (không có sẵn trong ma trận)
    df["_stem_len"] = [len(bank[i]["stem"]) for i in ids]
    df["_stem_words"] = [len(bank[i]["stem"].split()) for i in ids]
    df["_is_negative"] = [int(bool(NEGATIVE_RE.search(bank[i]["stem"]))) for i in ids]
    df["_opt_len_mean"] = [np.mean([len(bank[i]["correct"])] +
                                   [len(x) for x in bank[i]["distractors"]]) for i in ids]
    stem_feats = [c for c in STEM_FEATS if c in df.columns] + \
                 ["_stem_len", "_stem_words", "_is_negative", "_opt_len_mean"]
    dist_feats = [c for c in DISTRACTOR_FEATS if c in df.columns]

    # Loại đặc trưng vô nghĩa trên môn Sử: cột toàn NaN (đặc trưng bị cổng theo
    # cụm môn — vd. kg_same_author_* chỉ bật cho cụm Văn) hoặc hằng số (không
    # có phương sai thì tương quan không xác định).
    def usable(c: str) -> bool:
        s = pd.to_numeric(df[c], errors="coerce")
        return s.notna().sum() >= 8 and s.nunique(dropna=True) > 1
    dropped = [c for c in dist_feats + stem_feats if not usable(c)]
    dist_feats = [c for c in dist_feats if usable(c)]
    stem_feats = [c for c in stem_feats if usable(c)]
    if dropped:
        print(f"⚠ Bỏ {len(dropped)} đặc trưng toàn NaN/hằng số trên tập này: "
              f"{', '.join(dropped)}\n")

    n = len(df)
    crit = 1.96 / np.sqrt(n - 3)  # xấp xỉ ngưỡng |ρ| khác 0 ở mức 5%
    print(f"n = {n} câu có đủ nhãn GV + nhãn LLM + đặc trưng")
    print(f"Ngưỡng |ρ| khác 0 (α=5%, xấp xỉ Fisher): {crit:.3f} "
          "— dưới mức này KHÔNG diễn giải\n")

    targets = {"nhãn GV": "_gv", "nhãn LLM": "_llm", "p_sim (làm đúng)": "_p"}
    groups = {"[A] PHƯƠNG ÁN NHIỄU": dist_feats, "[B] CÂU CHỮ / STEM": stem_feats}

    print("=" * 74)
    print("TƯƠNG QUAN |Spearman| TRUNG BÌNH THEO NHÓM ĐẶC TRƯNG")
    print("=" * 74)
    print(f"{'nhóm':<24}{'#đt':>5}" + "".join(f"{t:>16}" for t in targets))
    summary = {}
    for gname, feats in groups.items():
        row = {}
        for tname, tcol in targets.items():
            rs = [abs(spearman(df[f], df[tcol])) for f in feats]
            rs = [r for r in rs if not np.isnan(r)]
            row[tname] = float(np.mean(rs)) if rs else float("nan")
        summary[gname] = row
        print(f"{gname:<24}{len(feats):>5}" + "".join(f"{row[t]:>16.3f}" for t in targets))

    print("\n" + "=" * 74)
    print("CHÊNH LỆCH  [A] nhiễu  −  [B] câu chữ   (dương = bám phương án nhiễu)")
    print("=" * 74)
    for tname in targets:
        d = summary["[A] PHƯƠNG ÁN NHIỄU"][tname] - summary["[B] CÂU CHỮ / STEM"][tname]
        print(f"  {tname:<22}{d:>+8.3f}")

    print("\n" + "=" * 74)
    print("TOP ĐẶC TRƯNG TỪNG NGUỒN NHÃN (|ρ| lớn nhất)")
    print("=" * 74)
    allf = dist_feats + stem_feats
    tag = {f: ("nhiễu" if f in dist_feats else "câu chữ") for f in allf}
    for tname, tcol in targets.items():
        rr = sorted(((abs(spearman(df[f], df[tcol])), spearman(df[f], df[tcol]), f)
                     for f in allf), reverse=True)
        print(f"\n  {tname}:")
        for a, r, f in rr[:6]:
            mark = " *" if a >= crit else "  "
            print(f"    {r:+.3f}{mark} {f:<38}[{tag[f]}]")
    print("\n  (* = khác 0 ở mức 5%)")

    out = SAMPLES / "label_basis_probe.json"
    out.write_text(json.dumps({"n": n, "crit": crit, "group_means": summary},
                              ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  đã lưu -> {out}")


if __name__ == "__main__":
    main()
