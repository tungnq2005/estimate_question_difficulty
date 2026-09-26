"""Cơ chế test cho hướng A (nhánh hoán-khối) — NON-DESTRUCTIVE.
Không ghi/đè bất kỳ file kết quả nào. Chỉ đọc dữ liệu + huấn luyện trong RAM.

Ý tưởng: dựng ma trận đặc trưng 21 cột (bề mặt số 5 + KG 10 + vết giải 6),
fit out-of-fold trên nhãn GIÁO VIÊN môn Lý, rồi HOÁN KHỐI VẾT GIẢI giữa hai
câu cùng bài chênh >=2 bước. Đo ΔE[y] và so với hoán-khối đối chứng (cùng bài,
chênh 0 bước). Đây là kiểm chứng cơ chế, chưa phải chạy cổng B1.
"""
import sys, json, re
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import counterfactual_validity as cv
import operation_axis as oa
from shared.mcq.ontology_bridge import OntologyEngine

SEED = 42
SWAP_COLS = ["tr_steps", "tr_n_formula", "tr_given", "tr_unknowns",
             "tr_ont_steps_sum", "tr_ont_steps_max"]

eng = OntologyEngine.for_subject("physics")
fz = cv.Featurizer(eng, "numeric")
items = cv.load_items("physics")
traces = oa.load_traces("physics")
y = np.array([cv.SUBJECTS["physics"]["label_map"][q["difficulty"]] for q in items])

cols = cv.SURFACE_COLS["numeric"] + cv.KG_COLS + SWAP_COLS
feats = []
for q in items:
    f = fz(q["stem"], q["correct"], q["distractors"])
    f.update(oa.trace_features(q["id"], traces, {}))
    feats.append(f)
X = pd.DataFrame(feats)[cols]
print(f"n={len(items)} | cols={len(cols)} | NaN trong khối hoán: "
      f"{X[SWAP_COLS].isna().any(axis=1).sum()} câu")

model_of = cv.fit_out_of_fold(X, y, SEED, cols)
base = cv.predict_expected(model_of, feats, list(range(len(items))), cols)
print(f"E[y] gốc {base.mean():.3f} vs nhãn thật {y.mean():.3f}\n")

def lesson_of(q):
    u = q.get("source_url") or ""
    m = re.search(r"/tai-lieu/([^/?#]+)", u)
    return m.group(1) if m else u

steps = np.array([traces.get(q["id"], {}).get("steps", np.nan) for q in items], float)
by = defaultdict(list)
for i, q in enumerate(items):
    if not np.isnan(steps[i]):
        by[lesson_of(q)].append(i)

rng = np.random.default_rng(SEED)
rows = []
for ls, idxs in by.items():
    for a in idxs:
        for b in idxs:
            if a == b:
                continue
            d = steps[b] - steps[a]           # b nhiều bước hơn a
            if d < 2:
                continue
            # can thiệp: câu a (ít bước) NHẬN khối vết giải của b (nhiều bước) -> hứa +
            f_cf = dict(feats[a])
            for c in SWAP_COLS:
                f_cf[c] = feats[b][c]
            d_up = cv.expected_level(model_of[a], f_cf, cols) - base[a]
            # đối chứng: donor cùng bài chênh 0 bước
            same = [j for j in idxs if abs(steps[j] - steps[a]) < 1 and j != a]
            if not same:
                continue
            j = same[rng.integers(len(same))]
            f_pb = dict(feats[a])
            for c in SWAP_COLS:
                f_pb[c] = feats[j][c]
            d_pb = cv.expected_level(model_of[a], f_pb, cols) - base[a]
            rows.append((d_up, d_pb, d))

df = pd.DataFrame(rows, columns=["d_up", "d_pb", "dSteps"])
print(f"cặp dựng được: {len(df)} | câu liên quan: "
      f"{df.shape[0] and len(set(rows) and range(len(df)))}")
print(f"\nKHỐI VẾT GIẢI hoán vào (hứa +):")
print(f"  Δ trung bình   = {df.d_up.mean():+.4f}")
print(f"  đúng hướng (+) = {(df.d_up > 0).mean():.1%}")
print(f"ĐỐI CHỨNG (cùng bài, chênh 0 bước):")
print(f"  Δ trung bình   = {df.d_pb.mean():+.4f}")
print(f"  đúng hướng (+) = {(df.d_pb > 0).mean():.1%}")
diff = df.d_up - df.d_pb
try:
    _, p = wilcoxon(df.d_up, df.d_pb)
except Exception as e:
    p = float("nan")
print(f"\nΔ can thiệp − Δ đối chứng = {diff.mean():+.4f}  (p Wilcoxon = {p:.3g})")
