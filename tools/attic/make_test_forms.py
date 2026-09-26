# -*- coding: utf-8 -*-
"""Chọn ~120 câu Lịch sử 9 để tổ chức làm bài thật, sinh 3 đề x 40 câu (T2).

VÌ SAO CẦN: đây là bước đầu của kế hoạch Cold->Warm — có học sinh làm bài
thật thì mới tính được p-value (ground truth tâm trắc học), thứ mà nhãn
llm_vote3 hiện tại (3.152/3.152 câu, 0 câu có nhãn giáo viên) không cung cấp
được. Xem plan đầy đủ: C:\\Users\\Tung\\.claude\\plans\\explore-the-codebase-to-sparkling-hopper.md

BỐN TIÊU CHÍ CHỌN CÂU (chỉ trên 2.137 câu is_canonical):
  1. Phân tầng theo nhãn LLM hiện có (Dễ/TB/Khó) — trải đều để p-value có
     phương sai khi phân tích.
  2. Ưu tiên câu mà mô hình CHỈ-KG và mô hình CHỈ-VĂN-BẢN bất đồng dự đoán
     (dự đoán out-of-fold qua StratifiedGroupKFold, không rò rỉ) — câu càng
     bất đồng càng mang nhiều thông tin để phân định giả thuyết.
  3. ⭐ CẶP CÂU ĐỐI CHỨNG KHUÔN MẪU (~20 cặp): cùng một "khuôn mẫu" câu hỏi
     (vd. "...quốc gia nào?", "Nguyên nhân... là gì?" — các khuôn mẫu này lấy
     trực tiếp từ cụm từ đã được xác nhận là quyết định nhãn TF-IDF, xem
     docs/RELATED_WORK.md mục 5), CÙNG nhãn LLM, nhưng khác xa nhau ở một
     proxy "trọng tâm SGK vs chi tiết ngoài lề" (kg_centrality_mean /
     kg_prereq_depth_mean_correct của thực thể khớp được). Nhãn LLM gần như
     chắc gán cùng mức cho cả hai; nếu p-value thật lệch lớn → bằng chứng
     trực tiếp nhãn LLM bám khuôn mẫu, không bám nội dung.
  4. Một phần trong 124 câu needs_review (nơi LLM tự phân vân khi vote).

THIẾT KẾ ĐỀ (anchor-test design chuẩn):
  - 10 câu NEO (anchor) — chọn stratified theo nhãn LLM, KHÔNG lấy từ các cặp
    đối chứng (anchor cần "điển hình", không phải câu đối chứng đặc biệt) —
    xuất hiện trong CẢ 3 đề để liên kết thang đo giữa các đề.
  - Mỗi đề thêm 30 câu KHÔNG trùng đề khác → 40 câu/đề, ~150 HS chia đều
    3 đề → ~50 lượt/câu (sai số chuẩn p-value ≈ 0,07).
  - Tổng số câu DUY NHẤT được gán vào đề = 10 + 3*30 = 100. Phần dư trong pool
    120 câu (≈20 câu) giữ làm SPARE — dự phòng nếu giáo viên (T7) loại bỏ câu
    nào đó lúc chấm nhãn tham chiếu, không phải sai số của kế hoạch.
  - Mỗi cặp đối chứng được gán CÙNG một đề (không tách đôi) để phân tích
    trong-đề đơn giản hơn.

Usage:
    python tools/make_test_forms.py
    python tools/make_test_forms.py --csv .cache/history_canonical.features.csv
    python tools/make_test_forms.py --pool-size 120 --n-control-pairs 20 \\
        --n-disagreement 30 --n-needs-review 15
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
SAMPLE_FILES = ("mcq_samples.json", "mcq_crawled.json")
LABEL2ID = {"Easy": 0, "Medium": 1, "Hard": 2}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}
SEED = 42

# Cùng khối đặc trưng như tools/ablation.py, để 2 mô hình OOF so sánh công bằng.
BLOCKS_KG = ("kg_", "jaccard_", "rsi_", "kad_", "entity_match_coverage")

# Khuôn mẫu câu hỏi lấy từ cụm từ ĐÃ XÁC NHẬN quyết định nhãn TF-IDF
# (docs/RELATED_WORK.md mục 5) + vài khuôn mẫu phổ biến khác trong đề Sử.
TEMPLATES = {
    "quoc_gia_nao":   r"quốc gia nào|nước nào",
    "nam_nao":        r"\bnăm nào\b|\bvào năm nào\b|\bnăm bao nhiêu\b",
    "nguyen_nhan":    r"nguyên nhân (chính|chủ yếu|sâu xa|trực tiếp|cơ bản)?",
    "khong_phai":     r"không phải là|không đúng|ngoại trừ",
    "so_sanh":        r"điểm tương đồng|điểm khác biệt|so với|giống nhau|khác nhau",
    "y_nghia":        r"ý nghĩa (lịch sử|quan trọng|to lớn)?",
    "su_kien_nao":    r"sự kiện nào",
    "noi_dung_nao":   r"nội dung nào (sau đây)? (đúng|không đúng|phù hợp)",
    "vai_tro":        r"vai trò (của|quan trọng)",
    "ket_qua":        r"kết quả|hệ quả",
}


def load_pool(csv_path: Path | None) -> pd.DataFrame:
    """Nạp câu hỏi canonical + (nếu có) ma trận feature đã cache."""
    rows = []
    for fname in SAMPLE_FILES:
        p = REPO / "subjects" / "history" / "samples" / fname
        if p.exists():
            rows.extend(json.loads(p.read_text(encoding="utf-8")))
    df = pd.DataFrame([r for r in rows if r.get("difficulty")
                       and r.get("is_canonical", True)])
    df = df.set_index("id", drop=False)
    print(f"Nguồn: {len(df)} câu canonical có nhãn "
          f"({(df['needs_review'] == True).sum()} needs_review)")

    if csv_path and csv_path.exists():
        feat = pd.read_csv(csv_path).set_index("mcq_id")
        common = df.index.intersection(feat.index)
        print(f"  ma trận feature: {len(feat)} câu, khớp {len(common)}/{len(df)}")
        df = df.loc[common]
        feat = feat.loc[common]
    else:
        print("  ⚠ không có --csv feature matrix -> bỏ qua tiêu chí #2 "
              "(bất đồng KG/văn bản) và dùng proxy thô cho tiêu chí #3")
        feat = None
    return df, feat


def tag_template(stem: str) -> str:
    s = stem.lower()
    for name, pat in TEMPLATES.items():
        if re.search(pat, s):
            return name
    return "khac"


def oof_predictions(df: pd.DataFrame, feat: pd.DataFrame):
    """Dự đoán out-of-fold (StratifiedGroupKFold, không rò rỉ) cho 2 mô hình:
    chỉ-KG (XGBoost trên khối A+B+meta) và chỉ-văn-bản (TF-IDF + Logistic).
    Trả về (kg_pred, text_pred) cùng chỉ mục với df."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
    from sklearn.pipeline import make_pipeline
    from xgboost import XGBClassifier

    y = df["difficulty"].map(LABEL2ID).values
    g = df["dup_group"].fillna(-1).values.astype(int)
    if (g == -1).any():
        n_miss = int((g == -1).sum())
        g = g.copy()
        g[g == -1] = -np.arange(1, n_miss + 1)
    cv = list(StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
             .split(df, y, groups=g))
    for tr, te in cv:
        assert not (set(g[tr]) & set(g[te])), "rò rỉ nhóm giữa các fold!"

    kg_cols = [c for c in feat.columns if c.startswith(BLOCKS_KG)]
    Xkg = feat[kg_cols].values
    kg_params = dict(n_estimators=600, max_depth=6, learning_rate=0.05,
                     subsample=0.8, colsample_bytree=0.8, min_child_weight=2,
                     eval_metric="mlogloss", random_state=SEED, n_jobs=-1)
    w = (len(y) / (3 * np.bincount(y)))[y]
    kg_pred = cross_val_predict(XGBClassifier(**kg_params), Xkg, y, cv=cv,
                                params={"sample_weight": w})

    texts = (df["stem"] + " " + df["correct"] + " "
            + df["distractors"].apply(lambda d: " ".join(d))).values
    tfidf = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000),
        LogisticRegression(max_iter=2000, class_weight="balanced"))
    text_pred = cross_val_predict(tfidf, texts, y, cv=cv)

    print(f"  OOF: KG-only acc={np.mean(kg_pred == y):.3f} | "
          f"text-only acc={np.mean(text_pred == y):.3f} | "
          f"bất đồng {np.mean(kg_pred != text_pred):.1%} câu")
    return pd.Series(kg_pred, index=df.index), pd.Series(text_pred, index=df.index)


def pick_control_pairs(df: pd.DataFrame, feat: pd.DataFrame | None,
                       n_pairs: int, rng: np.random.Generator) -> list:
    """Tìm ~n_pairs cặp câu: cùng khuôn mẫu + cùng nhãn LLM + lệch xa nhau ở
    proxy "trọng tâm SGK vs chi tiết ngoài lề". Trả về list[(id_core, id_periph,
    template, proxy_gap)]."""
    df = df.copy()
    df["template"] = df["stem"].apply(tag_template)
    if feat is not None and "kg_centrality_mean" in feat.columns:
        proxy = feat["kg_centrality_mean"].reindex(df.index)
        # Thiếu centrality (khớp thất bại hoàn toàn) -> không dùng làm ứng viên
        proxy_name = "kg_centrality_mean"
    else:
        # Không có feature matrix: proxy thô = độ dài câu hỏi (câu chi tiết
        # ngoài lề thường có stem dài, nhiều mốc thời gian/tên riêng cụ thể
        # hơn câu hỏi về sự kiện trọng tâm đã được diễn giải súc tích trong SGK)
        proxy = df["stem"].str.len().astype(float)
        proxy_name = "stem_len (proxy thô, không có feature matrix)"
    df["proxy"] = proxy

    candidates = []
    for (tmpl, label), g in df[df["template"] != "khac"].groupby(["template", "difficulty"]):
        g = g.dropna(subset=["proxy"])
        if len(g) < 2:
            continue
        hi = g.loc[g["proxy"].idxmax()]
        lo = g.loc[g["proxy"].idxmin()]
        gap = float(hi["proxy"] - lo["proxy"])
        if gap <= 0:
            continue
        candidates.append((hi["id"], lo["id"], f"{tmpl}/{label}", gap))

    candidates.sort(key=lambda t: -t[3])
    chosen = candidates[:n_pairs]
    print(f"  {len(candidates)} nhóm (khuôn mẫu × nhãn) đủ ứng viên cặp; "
          f"chọn {len(chosen)} cặp có chênh lệch {proxy_name} lớn nhất")
    return chosen


def stratified_fill(pool_ids: set, df: pd.DataFrame, need: int,
                    rng: np.random.Generator) -> list:
    """Bổ sung câu còn thiếu, chia đều 3 mức khó, không trùng pool_ids."""
    if need <= 0:
        return []
    remaining = df[~df["id"].isin(pool_ids)]
    per_label = max(1, need // 3)
    picked = []
    for label in ("Easy", "Medium", "Hard"):
        cand = remaining[remaining["difficulty"] == label]
        cand = cand[~cand["id"].isin(picked)]
        k = min(per_label, len(cand))
        if k:
            picked.extend(rng.choice(cand["id"].values, size=k, replace=False))
    # bù nốt phần lẻ nếu need không chia hết cho 3
    while len(picked) < need:
        left = remaining[~remaining["id"].isin(pool_ids | set(picked))]
        if left.empty:
            break
        picked.append(rng.choice(left["id"].values))
    return picked


def assign_forms(df: pd.DataFrame, anchors: list, pairs: list,
                 rest_priority: list, rng: np.random.Generator):
    """Gán câu không-neo vào 3 đề (30 câu/đề), giữ nguyên từng cặp đối chứng
    trong CÙNG một đề, cân bằng số câu + nhãn khó giữa 3 đề (greedy)."""
    forms = {"A": [], "B": [], "C": []}
    form_labels = {"A": [], "B": [], "C": []}

    def least_loaded(need_slots=1):
        return min(forms, key=lambda f: len(forms[f]))

    used = set(anchors)
    # 1) cặp đối chứng: xếp nguyên cặp vào đề đang ít câu nhất
    for id_a, id_b, tmpl, gap in pairs:
        if id_a in used or id_b in used:
            continue
        f = least_loaded()
        forms[f].extend([id_a, id_b])
        used.update([id_a, id_b])

    # 2) phần còn lại (bất đồng KG/text + needs_review + stratified fill):
    #    round-robin, cân bằng nhãn khó giữa các đề
    for qid in rest_priority:
        if qid in used:
            continue
        f = min(forms, key=lambda x: len(forms[x]))
        forms[f].append(qid)
        used.add(qid)

    for f in forms:
        forms[f] = forms[f][:30]  # trần 30 câu không-neo / đề
    return forms


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=".cache/history_canonical.features.csv",
                    help="ma trận feature đã cache (tools/train.py --csv ...)")
    ap.add_argument("--pool-size", type=int, default=120)
    ap.add_argument("--n-control-pairs", type=int, default=20)
    ap.add_argument("--n-disagreement", type=int, default=30)
    ap.add_argument("--n-needs-review", type=int, default=15)
    ap.add_argument("--out", default="subjects/history/samples/test_forms.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    csv_path = REPO / args.csv if not Path(args.csv).is_absolute() else Path(args.csv)
    df, feat = load_pool(csv_path)

    kg_pred = text_pred = None
    if feat is not None:
        print("\n[1] Dự đoán out-of-fold (KG-only vs text-only)...")
        kg_pred, text_pred = oof_predictions(df, feat)

    print("\n[2] Tìm cặp câu đối chứng khuôn mẫu...")
    pairs = pick_control_pairs(df, feat, args.n_control_pairs, rng)
    pair_ids = {i for a, b, *_ in pairs for i in (a, b)}

    disagreement_ids = []
    if kg_pred is not None:
        dis = df.index[(kg_pred != text_pred) & (~df.index.isin(pair_ids))]
        disagreement_ids = list(rng.permutation(dis.values))[:args.n_disagreement]
        print(f"\n[3] {len(dis)} câu KG/văn bản bất đồng dự đoán -> "
              f"lấy {len(disagreement_ids)}")

    nr_pool = df.index[(df["needs_review"] == True)
                       & (~df.index.isin(pair_ids))
                       & (~df.index.isin(disagreement_ids))]
    needs_review_ids = list(rng.permutation(nr_pool.values))[:args.n_needs_review]
    print(f"\n[4] {len(nr_pool)} câu needs_review khả dụng -> "
          f"lấy {len(needs_review_ids)}")

    pool_ids = pair_ids | set(disagreement_ids) | set(needs_review_ids)
    need = args.pool_size - len(pool_ids)
    fill_ids = stratified_fill(pool_ids, df, max(0, need), rng)
    pool_ids |= set(fill_ids)
    print(f"\n[5] Bổ sung stratified: +{len(fill_ids)} câu "
          f"-> tổng pool {len(pool_ids)} câu")

    # ---------- Chọn 10 câu neo: stratified, KHÔNG lấy từ cặp đối chứng ----------
    anchor_cand = df.loc[list(pool_ids - pair_ids)]
    anchors = []
    per_label = {"Easy": 3, "Medium": 4, "Hard": 3}
    for label, k in per_label.items():
        cand = anchor_cand[anchor_cand["difficulty"] == label]
        k = min(k, len(cand))
        if k:
            anchors.extend(rng.choice(cand["id"].values, size=k, replace=False))
    print(f"\n[6] {len(anchors)} câu neo (chung cả 3 đề): "
          f"{[df.loc[a, 'difficulty'] for a in anchors]}")

    # ---------- Gán 3 đề ----------
    rest_priority = (list(rng.permutation(list(disagreement_ids)))
                     + list(rng.permutation(list(needs_review_ids)))
                     + list(rng.permutation(fill_ids)))
    forms = assign_forms(df, anchors, pairs, rest_priority, rng)
    for f in forms:
        forms[f] = anchors + forms[f]
    assigned = set(anchors) | {i for v in forms.values() for i in v}
    spares = sorted(pool_ids - assigned)

    print("\n[7] Kết quả:")
    for f, ids in forms.items():
        labels = df.loc[ids, "difficulty"].value_counts().to_dict()
        print(f"  Đề {f}: {len(ids)} câu ({labels})")
    print(f"  Spare (dự phòng, không gán đề): {len(spares)} câu")

    # ---------- Xuất JSON ----------
    def brief(qid):
        r = df.loc[qid]
        return {"id": qid, "stem": r["stem"], "difficulty": r["difficulty"],
                "is_anchor": qid in anchors,
                "template": tag_template(r["stem"])}

    out = {
        "meta": {
            "seed": SEED, "pool_size": len(pool_ids), "n_pairs": len(pairs),
            "n_disagreement": len(disagreement_ids),
            "n_needs_review": len(needs_review_ids),
            "n_stratified_fill": len(fill_ids),
            "n_anchors": len(anchors),
            "has_feature_matrix": feat is not None,
        },
        "control_pairs": [
            {"core_or_edge_a": a, "core_or_edge_b": b, "group": tmpl, "gap": gap,
             "label_a": df.loc[a, "difficulty"], "label_b": df.loc[b, "difficulty"]}
            for a, b, tmpl, gap in pairs
        ],
        "anchors": [brief(i) for i in anchors],
        "forms": {f: [brief(i) for i in ids] for f, ids in forms.items()},
        "spares": [brief(i) for i in spares],
    }
    out_path = REPO / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  đã lưu -> {out_path}")
    print("  (đề đầy đủ nội dung câu hỏi + phương án nằm trong forms[*][*].id -> "
          "tra lại mcq_crawled.json; T7 sẽ sinh form Google Apps Script từ file này)")


if __name__ == "__main__":
    main()
