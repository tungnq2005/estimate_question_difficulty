# -*- coding: utf-8 -*-
"""E3 — thí nghiệm Cold->Warm: tri thức có cấu trúc đáng giá bao nhiêu lượt
trả lời của học sinh? (T9, thí nghiệm CHÍNH của kế hoạch).

Ý TƯỞNG: với mỗi câu hỏi, so 3 cách ước lượng p-value khi chỉ có k lượt trả
lời đầu tiên (k nhỏ = "cold", k lớn = "warm"):
  (a) prior = mô hình CHỈ-KG (huấn luyện trên 2.137 câu nhãn LLM, KHÔNG thấy
      câu khảo sát) — "cold-start" thuần tri thức.
  (b) prior = mô hình CHỈ-VĂN-BẢN (TF-IDF), cùng cách huấn luyện.
  (c) prior = TRUNG BÌNH TOÀN CỤC (leave-one-out) — prior vô thông tin.
Trộn prior với dữ liệu quan sát bằng co rút Bayes:
    p̃ᵢ = (α·priorᵢ + k·p̂ᵢ⁽ᵏ⁾) / (α + k)
Đường (c) cần bao nhiêu lượt trả lời k* để đạt sai số ngang với đường (a) tại
k=0? → "tri thức có cấu trúc đáng giá ≈ k* lượt trả lời của học sinh."

DỮ LIỆU CẦN: subjects/history/samples/student_responses.csv (dạng long, xem
tools/item_analysis.py) — CHƯA CÓ cho tới khi T4 (tổ chức làm bài) hoàn tất.
Dùng --demo để tự kiểm thử phần THỐNG KÊ (co rút Bayes, MAE, k*) độc lập với
việc huấn luyện mô hình thật — --demo phát sinh phản hồi VÀ prior mô phỏng
với độ tương quan với "sự thật" điều khiển được qua --prior-noise-*, không
chạm tới pipeline KG/TF-IDF thật.

KIỂM CHỨNG BẮT BUỘC (#4 trong kế hoạch): chạy --verify-shuffle — hoán vị
prior (a)/(b) giữa các câu (phá tương quan thật nhưng giữ nguyên phân bố) rồi
so với đường (c). Nếu co rút Bayes cài đúng, đường "prior xáo trộn" phải TRÙNG
đường (c) trong khoảng tin cậy (một prior không tương quan với sự thật chỉ
đóng góp giá trị trung tâm của nó, giống hệt prior vô thông tin).

Usage:
    python tools/coldwarm.py --demo                      # tự kiểm thử thống kê
    python tools/coldwarm.py --demo --verify-shuffle      # kiểm chứng #4
    python tools/coldwarm.py --responses subjects/history/samples/student_responses.csv \\
        --csv .cache/history_canonical.features.csv       # chạy thật (sau T4)
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
LABEL2ID = {"Easy": 0, "Medium": 1, "Hard": 2}
SEED = 42
K_GRID = [0, 1, 2, 3, 5, 10, 20, 25]
ALPHA_GRID = [1, 2, 4, 8, 16, 32, 64, 128]

# Giả định ánh xạ lớp Dễ/TB/Khó -> p-value điển hình, dùng để biến xác suất
# lớp (predict_proba) của mô hình phân loại thành một "prior xác suất đúng"
# liên tục. ĐÂY LÀ GIẢ ĐỊNH, không phải số đo — cần nêu rõ trong luận văn và
# có thể hiệu chỉnh lại bằng chính p-value thật một khi có đủ dữ liệu (nhưng
# phải cẩn thận tránh rò rỉ: hiệu chỉnh trên tập KHÁC với tập đánh giá).
CLASS_TO_P = {"Easy": 0.85, "Medium": 0.55, "Hard": 0.25}


# ---------------------------------------------------------------------------
# 1. Nguồn PRIOR
# ---------------------------------------------------------------------------

def train_priors_from_features(csv_path: Path, survey_ids: list) -> pd.DataFrame:
    """Huấn luyện prior (a) KG-only và (b) text-only trên phần 2.137 câu
    KHÔNG bao gồm survey_ids (và dup_group của chúng, tránh rò rỉ gần-đúng —
    cùng nguyên tắc với E2), rồi dự đoán prior cho đúng survey_ids.
    Trả DataFrame index=item_id, cột prior_kg, prior_text."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from xgboost import XGBClassifier

    feat = pd.read_csv(csv_path).set_index("mcq_id")
    rows = []
    for fname in ("mcq_samples.json", "mcq_crawled.json"):
        p = REPO / "subjects" / "history" / "samples" / fname
        if p.exists():
            rows.extend(json.loads(p.read_text(encoding="utf-8")))
    pool = pd.DataFrame([r for r in rows if r.get("difficulty")
                        and r.get("is_canonical", True)]).set_index("id", drop=False)

    survey_dup_groups = set(pool.loc[survey_ids, "dup_group"].dropna())
    is_survey_related = (pool["id"].isin(survey_ids)
                         | pool["dup_group"].isin(survey_dup_groups))
    train_ids = pool.index[~is_survey_related]
    train_ids = train_ids.intersection(feat.index)
    test_ids = pd.Index(survey_ids).intersection(feat.index)
    print(f"  Prior huấn luyện trên {len(train_ids)} câu "
         f"(đã loại {len(pool)-len(train_ids)} câu khảo sát + bản gần-đúng); "
         f"dự đoán cho {len(test_ids)}/{len(survey_ids)} câu khảo sát")

    y_train = pool.loc[train_ids, "difficulty"].map(LABEL2ID).values
    kg_cols = [c for c in feat.columns
              if c.startswith(("kg_", "jaccard_", "rsi_", "kad_", "entity_match_coverage"))]
    kg_params = dict(n_estimators=600, max_depth=6, learning_rate=0.05,
                     subsample=0.8, colsample_bytree=0.8, min_child_weight=2,
                     eval_metric="mlogloss", random_state=SEED, n_jobs=-1)
    w = (len(y_train) / (3 * np.bincount(y_train)))[y_train]
    kg_model = XGBClassifier(**kg_params).fit(
        feat.loc[train_ids, kg_cols].values, y_train, sample_weight=w)
    proba_kg = kg_model.predict_proba(feat.loc[test_ids, kg_cols].values)

    texts_train = (pool.loc[train_ids, "stem"] + " " + pool.loc[train_ids, "correct"] + " "
                  + pool.loc[train_ids, "distractors"].apply(lambda d: " ".join(d))).values
    texts_test = (pool.loc[test_ids, "stem"] + " " + pool.loc[test_ids, "correct"] + " "
                 + pool.loc[test_ids, "distractors"].apply(lambda d: " ".join(d))).values
    text_model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000),
        LogisticRegression(max_iter=2000, class_weight="balanced"))
    text_model.fit(texts_train, y_train)
    proba_text = text_model.predict_proba(texts_test)

    class_p = np.array([CLASS_TO_P["Easy"], CLASS_TO_P["Medium"], CLASS_TO_P["Hard"]])
    return pd.DataFrame({
        "prior_kg": proba_kg @ class_p,
        "prior_text": proba_text @ class_p,
    }, index=test_ids)


def make_demo_data(n_items: int = 100, seed: int = SEED,
                   prior_noise_kg: float = 0.08, prior_noise_text: float = 0.15,
                   n_responses: int = 55):
    """Sinh dữ liệu MÔ PHỎNG: true_p ngẫu nhiên cho n_items câu, phản hồi HS
    dạng Bernoulli(true_p), và 2 prior = true_p + nhiễu Gauss có độ lệch
    chuẩn khác nhau (prior_kg 'tốt hơn' prior_text theo mặc định — điều
    chỉnh qua CLI để kiểm thử các kịch bản khác). CHỈ để tự kiểm thử code
    thống kê, KHÔNG phản ánh câu hỏi Lịch sử thật."""
    rng = np.random.default_rng(seed)
    item_ids = [f"demo_{i:03d}" for i in range(n_items)]
    true_p = rng.beta(2, 2, size=n_items)  # trải đều quanh 0.5, có phương sai
    responses = {iid: (rng.random(n_responses) < p).astype(int)
                for iid, p in zip(item_ids, true_p)}
    priors = pd.DataFrame({
        "prior_kg": np.clip(true_p + rng.normal(0, prior_noise_kg, n_items), 0.02, 0.98),
        "prior_text": np.clip(true_p + rng.normal(0, prior_noise_text, n_items), 0.02, 0.98),
    }, index=item_ids)
    return responses, priors, dict(zip(item_ids, true_p))


# ---------------------------------------------------------------------------
# 2. Co rút Bayes + đường cong MAE(k)
# ---------------------------------------------------------------------------

def split_half(responses: dict, seed: int = SEED) -> dict:
    """Chia đôi lượt trả lời mỗi câu: nửa A định nghĩa p thật, nửa B để
    subsample. BẮT BUỘC tách biệt — dùng chung 1 tập cho cả 2 việc sẽ làm
    MAE(k) lạc quan giả tạo dần về 0 khi k tăng (data leakage)."""
    rng = np.random.default_rng(seed)
    out = {}
    for iid, arr in responses.items():
        idx = rng.permutation(len(arr))
        half = len(arr) // 2
        out[iid] = {"A": arr[idx[:half]], "B": arr[idx[half:]]}
    return out


def mae_curve(halves: dict, prior: pd.Series, alpha: float, k_grid: list,
             n_repeats: int, seed: int = SEED):
    """Trả (mae_per_k: dict k->float, se_per_k: dict k->float qua bootstrap
    theo câu hỏi, per_item_err: dict k-> array lỗi trung bình mỗi câu)."""
    rng = np.random.default_rng(seed)
    items = [i for i in halves if i in prior.index]
    p_true = np.array([halves[i]["A"].mean() for i in items])
    mae_per_k, se_per_k, per_item_err = {}, {}, {}

    for k in k_grid:
        errs = np.full((len(items), n_repeats if k > 0 else 1), np.nan)
        for ii, iid in enumerate(items):
            b = halves[iid]["B"]
            pr = prior.loc[iid]
            if k == 0:
                errs[ii, 0] = abs(pr - p_true[ii])
                continue
            if k > len(b):
                continue  # không đủ dữ liệu nửa B cho k này ở câu này
            for r in range(n_repeats):
                draw = rng.choice(len(b), size=k, replace=False)
                phat = b[draw].mean()
                p_tilde = (alpha * pr + k * phat) / (alpha + k)
                errs[ii, r] = abs(p_tilde - p_true[ii])
        item_mean_err = np.nanmean(errs, axis=1)
        per_item_err[k] = item_mean_err
        valid = ~np.isnan(item_mean_err)
        mae_per_k[k] = float(np.mean(item_mean_err[valid])) if valid.any() else np.nan
        # bootstrap CI theo câu hỏi (không phải theo repeat — items là đơn vị độc lập)
        if valid.sum() >= 5:
            boots = [np.mean(rng.choice(item_mean_err[valid], size=valid.sum(), replace=True))
                     for _ in range(300)]
            se_per_k[k] = float(np.std(boots))
        else:
            se_per_k[k] = np.nan
    return mae_per_k, se_per_k, per_item_err


def pick_alpha_cv(halves: dict, prior: pd.Series, alpha_grid: list, k_grid: list,
                  n_repeats: int, n_folds: int = 5, seed: int = SEED) -> float:
    """Chọn alpha bằng K-fold trên chính tập câu hỏi: với mỗi alpha, tính MAE
    trung bình trên các k>0 gộp qua các fold (mỗi fold dùng CHÍNH mae_curve
    trên các câu của fold đó — không có "tham số" nào thực sự được fit từ
    dữ liệu train ngoài việc chọn alpha, nên fold ở đây chỉ nhằm tránh chọn
    alpha khớp với nhiễu ngẫu nhiên của 1 lần chạy)."""
    rng = np.random.default_rng(seed)
    items = np.array([i for i in halves if i in prior.index])
    folds = np.array_split(rng.permutation(items), n_folds)
    scores = {}
    for a in alpha_grid:
        fold_scores = []
        for fold_items in folds:
            sub_halves = {i: halves[i] for i in fold_items}
            mae_k, _, _ = mae_curve(sub_halves, prior, a, [k for k in k_grid if k > 0],
                                    n_repeats, seed=seed)
            vals = [v for v in mae_k.values() if v == v]
            if vals:
                fold_scores.append(np.mean(vals))
        scores[a] = np.mean(fold_scores) if fold_scores else np.inf
    best = min(scores, key=scores.get)
    print(f"    alpha grid-search: {', '.join(f'{a}={s:.4f}' for a, s in scores.items())}"
         f" -> chọn α={best}")
    return best


def compute_kstar(mae_c: dict, target: float, k_grid: list) -> float:
    """Nội suy tuyến tính: k nhỏ nhất trên đường (c) mà MAE(k) <= target."""
    ks = sorted(k_grid)
    for i in range(len(ks) - 1):
        k0, k1 = ks[i], ks[i + 1]
        m0, m1 = mae_c.get(k0), mae_c.get(k1)
        if m0 != m0 or m1 != m1:
            continue
        if m0 <= target:
            return float(k0)
        if m1 <= target:
            if m0 == m1:
                return float(k1)
            frac = (m0 - target) / (m0 - m1)
            return float(k0 + frac * (k1 - k0))
    return float("inf")  # không đường cong nào đạt target trong lưới k đã thử


# ---------------------------------------------------------------------------
# 3. Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses", default="subjects/history/samples/student_responses.csv")
    ap.add_argument("--csv", default=".cache/history_canonical.features.csv",
                    help="ma trận feature (tools/train.py --csv ...) để huấn luyện prior thật")
    ap.add_argument("--demo", action="store_true",
                    help="dữ liệu + prior MÔ PHỎNG, chỉ để tự kiểm thử thống kê")
    ap.add_argument("--demo-n-items", type=int, default=100)
    ap.add_argument("--prior-noise-kg", type=float, default=0.08)
    ap.add_argument("--prior-noise-text", type=float, default=0.15)
    ap.add_argument("--n-repeats", type=int, default=200)
    ap.add_argument("--n-repeats-alpha-search", type=int, default=40)
    ap.add_argument("--verify-shuffle", action="store_true",
                    help="kiểm chứng #4: hoán vị prior giữa các câu, phải "
                         "trùng đường (c) trong khoảng tin cậy")
    ap.add_argument("--out", default="subjects/history/samples/coldwarm_results.json")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)

    if args.demo:
        print("⚠ CHẾ ĐỘ DEMO: phản hồi + prior đều MÔ PHỎNG — chỉ kiểm thử "
             "đúng đắn của co rút Bayes/MAE/k*, không phản ánh dữ liệu thật.\n")
        responses, priors, _ = make_demo_data(
            args.demo_n_items, prior_noise_kg=args.prior_noise_kg,
            prior_noise_text=args.prior_noise_text)
        args.out = "subjects/history/samples/coldwarm_results.DEMO.json"
    else:
        resp_path = REPO / args.responses
        if not resp_path.exists():
            sys.exit(f"Chưa có {resp_path}. Chạy --demo để kiểm thử thống kê "
                     f"trước khi có dữ liệu HS thật (T4).")
        df = pd.read_csv(resp_path)
        responses = {iid: g.sort_values("student_id")["correct"].values
                    for iid, g in df.groupby("item_id")}
        csv_path = REPO / args.csv
        if not csv_path.exists():
            sys.exit(f"Chưa có {csv_path}. Chạy tools/train.py --csv ... trước.")
        priors = train_priors_from_features(csv_path, list(responses.keys()))

    priors["prior_uninformative"] = np.nan  # tính leave-one-out bên dưới
    halves = split_half(responses)
    p_true_all = pd.Series({i: halves[i]["A"].mean() for i in halves})
    n = len(p_true_all)
    priors["prior_uninformative"] = [
        (p_true_all.sum() - p_true_all[i]) / (n - 1) if n > 1 else p_true_all.mean()
        for i in priors.index
    ]

    n_ok = sum(1 for i in halves if len(halves[i]["B"]) < max(K_GRID))
    if n_ok:
        print(f"  ⚠ {n_ok}/{len(halves)} câu có nửa B < {max(K_GRID)} lượt "
             f"-> k lớn nhất bị bỏ qua cho các câu đó (báo cáo trong kết quả)")

    print(f"\nn = {len(halves)} câu | trung vị lượt trả lời/câu = "
         f"{int(np.median([len(a) for a in responses.values()]))}\n")

    prior_names = {"a_kg": "prior_kg", "b_text": "prior_text", "c_uninformative": "prior_uninformative"}
    curves = {}
    print("[1] Chọn alpha bằng CV cho từng loại prior...")
    alphas = {}
    for label, col in prior_names.items():
        print(f"  {label} ({col}):")
        alphas[label] = pick_alpha_cv(halves, priors[col], ALPHA_GRID, K_GRID,
                                      args.n_repeats_alpha_search)

    print("\n[2] Tính đường cong MAE(k) với alpha đã chọn...")
    for label, col in prior_names.items():
        mae_k, se_k, _ = mae_curve(halves, priors[col], alphas[label], K_GRID, args.n_repeats)
        curves[label] = {"mae": mae_k, "se": se_k, "alpha": alphas[label]}
        print(f"  {label:<16} α={alphas[label]:<4} "
             f"{' '.join(f'k{k}={mae_k[k]:.4f}' for k in K_GRID if mae_k[k] == mae_k[k])}")

    target = curves["a_kg"]["mae"][0]
    kstar = compute_kstar(curves["c_uninformative"]["mae"], target, K_GRID)
    print(f"\n[3] k* (đường vô thông tin đạt sai số của prior-KG tại k=0): "
         f"{kstar if kstar != float('inf') else 'KHÔNG đạt trong lưới k đã thử'}")
    if kstar != float("inf"):
        print(f"    -> \"Tri thức có cấu trúc (prior-KG) đáng giá ≈ {kstar:.1f} "
             f"lượt trả lời của học sinh.\"")

    result = {
        "n_items": len(halves), "k_grid": K_GRID, "alpha_grid": ALPHA_GRID,
        "alphas_chosen": alphas, "curves": curves, "k_star": kstar,
        "class_to_p_assumption": CLASS_TO_P,
    }

    if args.verify_shuffle:
        # LƯU Ý QUAN TRỌNG (rút ra từ lần chạy đầu của chính kiểm chứng này):
        # hoán vị prior_kg giữa các câu KHÔNG phải phép thử công bằng — nó phá
        # tương quan với sự thật nhưng vẫn giữ nguyên PHƯƠNG SAI cao của
        # prior_kg (trải theo phân phối thật), trong khi prior vô thông tin
        # (trung bình leave-one-out) gần như HẰNG SỐ (phương sai ~0). Một
        # prior nhiễu-nhưng-phương-sai-cao thật sự cho MAE cao hơn một prior
        # hằng số, dù cả hai đều "không có thông tin" — đó là hiệu ứng thống
        # kê THẬT (sai số kép khi so 2 biến ngẫu nhiên độc lập), không phải
        # lỗi code. Test đúng phải khớp CẢ kỳ vọng LẪN phương sai với đường
        # (c): sinh prior ngẫu nhiên đã khớp (mean, std) của prior_uninformative,
        # qua một nhánh code ĐỘC LẬP (rng.normal trực tiếp, không tái dùng
        # phép tính leave-one-out) để phép thử không tự lặp lại chính nó.
        print("\n[4] KIỂM CHỨNG #4: prior ngẫu nhiên (khớp mean/std với đường "
             "(c), sinh độc lập) — dùng chung alpha của đường (c)...")
        shared_alpha = alphas["c_uninformative"]
        loo_vals = priors["prior_uninformative"].values.astype(float)
        match_mean, match_sd = loo_vals.mean(), max(loo_vals.std(), 1e-6)
        random_prior = pd.Series(
            np.clip(rng.normal(match_mean, match_sd, size=len(priors)), 0.02, 0.98),
            index=priors.index)
        mae_rand, se_rand, _ = mae_curve(halves, random_prior, shared_alpha, K_GRID, args.n_repeats)
        max_gap, max_gap_se = 0.0, 0.0
        for k in K_GRID:
            m_r, m_c = mae_rand.get(k), curves["c_uninformative"]["mae"].get(k)
            if m_r == m_r and m_c == m_c:
                gap = abs(m_r - m_c)
                if gap > max_gap:
                    max_gap, max_gap_se = gap, curves["c_uninformative"]["se"].get(k, 0)
        ok = max_gap <= 3 * (max_gap_se or 0.01) + 1e-6
        verdict = "✓ TRÙNG trong khoảng tin cậy — co rút Bayes cài đúng" if ok else \
                 "✗ LỆCH RÕ RỆT -> có lỗi trong code co rút Bayes, KIỂM TRA LẠI trước khi dùng"
        print(f"    (dùng chung α={shared_alpha}, prior~N({match_mean:.3f},{match_sd:.3f}²)) "
             f"chênh lệch lớn nhất giữa 2 đường: {max_gap:.4f} (± {max_gap_se:.4f}) -> {verdict}")
        result["verify_shuffle"] = {"mae": mae_rand, "max_gap": max_gap,
                                    "max_gap_se": max_gap_se, "passed": ok,
                                    "shared_alpha": shared_alpha,
                                    "matched_mean": float(match_mean), "matched_sd": float(match_sd)}

    out_path = REPO / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str),
                        encoding="utf-8")
    print(f"\n  đã lưu -> {out_path}")


if __name__ == "__main__":
    main()
