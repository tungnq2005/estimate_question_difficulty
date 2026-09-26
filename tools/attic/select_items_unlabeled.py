# -*- coding: utf-8 -*-
"""Chọn ~45 câu cho khảo sát học sinh — KHÔNG DÙNG NHÃN ĐỘ KHÓ Ở BẤT KỲ ĐÂU.

VÌ SAO PHẢI VIẾT LẠI (thay cho tools/make_test_forms.py): script cũ phân tầng
theo nhãn `llm_vote3` và chọn "cặp câu đối chứng" dựa trên nhãn đó. Nhưng nhãn
LLM đã được đo là bám đặc trưng bề mặt (mạnh nhất: ĐỘ DÀI PHƯƠNG ÁN, ρ=+0,356)
chứ không bám độ khó nội dung — xem docs/PIVOT_T1_KHONG_DUYET.md mục 5b.2.
Dùng nhãn đó để chọn câu sẽ cài sẵn thiên kiến vào chính tập đánh giá, khiến
kết quả không diễn giải được. Ở đây nhãn KHÔNG được đọc, dù chỉ để phân tầng.

NGUYÊN TẮC THAY THẾ — TRẢI ĐỀU TRÊN BIẾN DỰ BÁO, KHÔNG PHẢI TRÊN NHÃN:
giả thuyết cần kiểm là "cấu trúc phương án nhiễu suy từ ontology có liên hệ
với độ khó thật". Trong thiết kế thí nghiệm, công suất thống kê của một nghiên
cứu tương quan đạt tối đa khi biến DỰ BÁO trải đều toàn dải (spread on the
predictor) — và điều đó KHÔNG cần biết trước độ khó. Vì vậy:

  - Biến chính:  rsi_dc  (độ giống nhau giữa các phương án nhiễu) — đặc trưng
    tương quan mạnh nhất với hiệu suất làm bài trong đo thử (ρ=+0,371), và
    đúng cơ chế Vinu 2015 nêu: độ khó MCQ nằm ở quan hệ đúng ↔ nhiễu.
  - Chia rsi_dc thành 5 nhóm ngũ phân vị, lấy ĐỀU số câu mỗi nhóm.
  - Trong mỗi nhóm, chọn theo maximin để trải thêm trên các biến phụ
    (jaccard_soft_mean, kad_path_distance_mean) và ĐA DẠNG BÀI HỌC.

ĐIỀU KIỆN LỌC (không liên quan độ khó):
  - entity_match_coverage >= 0.5  — nếu ontology không khớp được thực thể ở
    các phương án thì mọi đặc trưng KG là vô nghĩa cho câu đó; giữ lại chỉ
    làm loãng phép kiểm.
  - rsi_dc không khuyết.
  - is_canonical (đã khử trùng lặp) — chặn rò rỉ/lặp nội dung trong đề.
  - Độ dài câu dẫn hợp lý để làm quiz online.

Output tương thích tools/make_student_forms.py.

Usage:
    python tools/select_items_unlabeled.py --n 45
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
SAMPLES = REPO / "subjects" / "history" / "samples"
SEED = 42

PRIMARY = "rsi_dc"
SECONDARY = ["jaccard_soft_mean", "kad_path_distance_mean"]
# Trường nhãn TUYỆT ĐỐI KHÔNG được đọc trong script này.
FORBIDDEN = ("difficulty", "difficulty_4", "label_source", "needs_review")


def load_bank() -> dict:
    q = {}
    for fname in ("mcq_samples.json", "mcq_crawled.json"):
        p = SAMPLES / fname
        if p.exists():
            for r in json.loads(p.read_text(encoding="utf-8")):
                q[r["id"]] = r
    return q


def topic_of(rec: dict) -> str:
    """Khoá chủ đề thô từ trường `source` (tên bài) — chỉ để ĐA DẠNG HOÁ nội
    dung, không mang thông tin độ khó."""
    s = (rec.get("source") or "").strip()
    return s[:60] if s else "khac"


def maximin_pick(cand: pd.DataFrame, k: int, cols: list,
                 rng: np.random.Generator) -> list:
    """Chọn k dòng trải xa nhau nhất trên `cols` (chuẩn hoá z), ưu tiên thêm
    câu thuộc chủ đề chưa xuất hiện. Greedy maximin — tất định theo seed."""
    if len(cand) <= k:
        return list(cand.index)
    X = cand[cols].fillna(cand[cols].median())
    X = ((X - X.mean()) / (X.std() + 1e-9)).to_numpy()
    chosen = [int(rng.integers(len(cand)))]
    seen_topics = {cand.iloc[chosen[0]]["_topic"]}
    while len(chosen) < k:
        d = np.min(np.linalg.norm(X[:, None, :] - X[None, chosen, :], axis=2), axis=1)
        # thưởng cho chủ đề mới để đề không dồn vào một bài
        bonus = np.array([0.6 if t not in seen_topics else 0.0
                          for t in cand["_topic"]])
        d = d + bonus
        d[chosen] = -np.inf
        pick = int(np.argmax(d))
        chosen.append(pick)
        seen_topics.add(cand.iloc[pick]["_topic"])
    return [cand.index[i] for i in chosen]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=45, help="số câu cần chọn")
    ap.add_argument("--csv", default=".cache/history_canonical.features.csv")
    ap.add_argument("--min-coverage", type=float, default=0.5)
    ap.add_argument("--out", default="subjects/history/samples/selected_items_unlabeled.json")
    args = ap.parse_args()

    bank = load_bank()
    feat = pd.read_csv(REPO / args.csv).set_index("mcq_id")
    assert not any(c in feat.columns for c in FORBIDDEN), \
        "Ma trận đặc trưng chứa cột nhãn — script này không được phép đọc nhãn."

    df = feat.copy()
    df["_topic"] = [topic_of(bank.get(i, {})) for i in df.index]
    df["_stem_len"] = [len(bank[i]["stem"]) if i in bank else 999 for i in df.index]
    df["_n_opts"] = [len(bank[i]["distractors"]) + 1 if i in bank else 0 for i in df.index]

    n0 = len(df)
    ok = (df[PRIMARY].notna()
          & (df["entity_match_coverage"] >= args.min_coverage)
          & (df["_stem_len"].between(20, 220))
          & (df["_n_opts"] == 4)
          & df.index.isin(bank))
    pool = df[ok]
    print(f"Pool: {n0} câu -> {len(pool)} câu đủ điều kiện")
    print(f"  (có {PRIMARY}, độ phủ thực thể >= {args.min_coverage}, "
          f"câu dẫn 20-220 ký tự, đúng 4 phương án)")

    rng = np.random.default_rng(SEED)
    qs = pool[PRIMARY].quantile([0, .2, .4, .6, .8, 1.0]).to_numpy().copy()
    qs[-1] += 1e-9
    per = args.n // 5
    picked = []
    print(f"\nChia {PRIMARY} thành 5 nhóm ngũ phân vị, lấy ~{per} câu/nhóm:")
    for b in range(5):
        lo, hi = qs[b], qs[b + 1]
        sub = pool[(pool[PRIMARY] >= lo) & (pool[PRIMARY] < hi)]
        k = per + (1 if b < args.n - per * 5 else 0)
        sel = maximin_pick(sub, k, [PRIMARY] + SECONDARY, rng)
        picked += sel
        print(f"  nhóm {b+1} [{lo:.3f}, {hi:.3f}): {len(sub):>4} câu -> chọn {len(sel)}")

    sel_df = pool.loc[picked]
    print(f"\nĐã chọn {len(picked)} câu.")
    print(f"  {PRIMARY}: min {sel_df[PRIMARY].min():.3f} | "
          f"trung vị {sel_df[PRIMARY].median():.3f} | max {sel_df[PRIMARY].max():.3f}")
    print(f"  độ lệch chuẩn {PRIMARY} trong tập chọn: {sel_df[PRIMARY].std():.3f} "
          f"(toàn pool: {pool[PRIMARY].std():.3f})  ← cao hơn là tốt")
    print(f"  số bài học khác nhau: {sel_df['_topic'].nunique()}")
    print(f"  độ dài câu dẫn: trung vị {sel_df['_stem_len'].median():.0f} ký tự")

    # --- kiểm tra hậu nghiệm: tập chọn có vô tình lệch nhãn không? ---
    # CHỈ để BÁO CÁO tính cân bằng, KHÔNG dùng trong lựa chọn.
    labs = [bank[i].get("difficulty") for i in picked]
    from collections import Counter
    print("\n  [kiểm tra hậu nghiệm — nhãn KHÔNG dùng để chọn] phân bố nhãn LLM "
          "trong tập đã chọn:")
    for k, v in sorted(Counter(labs).items(), key=lambda x: str(x[0])):
        print(f"    {k}: {v} ({100*v/len(picked):.0f}%)")

    out = {
        "n_items": len(picked),
        "selection_rule": {
            "primary_spread_feature": PRIMARY,
            "secondary_features": SECONDARY,
            "min_entity_coverage": args.min_coverage,
            "labels_used": False,
            "note": "Nhãn độ khó KHÔNG được dùng ở bất kỳ bước nào của lựa chọn.",
        },
        "item_ids": list(picked),
        "items": [{"id": i, "stem": bank[i]["stem"], "correct": bank[i]["correct"],
                   "distractors": bank[i]["distractors"],
                   "source": bank[i].get("source"),
                   PRIMARY: float(sel_df.loc[i, PRIMARY])} for i in picked],
    }
    p = REPO / args.out
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  đã lưu -> {p}")


if __name__ == "__main__":
    main()
