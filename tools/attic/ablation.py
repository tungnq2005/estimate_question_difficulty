# -*- coding: utf-8 -*-
"""Ablation study: đo đóng góp của từng khối đặc trưng cho dự đoán độ khó.

Tất cả cấu hình dùng CHUNG một bộ 5-fold (cùng seed) để so sánh công bằng,
và báo cáo đủ metric: accuracy, macro-F1, QWK (có tính thứ tự Dễ<TB<Khó).

Fold chia bằng StratifiedGroupKFold theo `dup_group` — mọi bản sao của cùng
một nội dung câu hỏi luôn nằm cùng một fold. Bắt buộc: bộ crawl có ~55% bản
sao, chia ngẫu nhiên thì bản sao rơi vào cả train lẫn test và accuracy bị
thổi phồng ~14 điểm (75,6% → 61,6%).

M8 là biến thể ORDINAL LOGISTIC (proportional-odds, McCullagh 1980) — đối
chứng cho phản biện Thuy et al. EvalLAC'25 rằng coi Dễ/TB/Khó là nhãn danh
nghĩa (nominal) làm mất thông tin thứ tự.

Usage:
    python tools/ablation.py --csv <feature_matrix.csv>
    python tools/ablation.py --csv ... --oof-phobert oof_phobert.csv   # sau khi có Colab
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from sklearn.model_selection import (StratifiedGroupKFold, StratifiedKFold,
                                     cross_val_predict)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
LABEL2ID = {"Easy": 0, "Medium": 1, "Hard": 2}
SEED = 42

XGB_PARAMS = dict(n_estimators=600, max_depth=6, learning_rate=0.05,
                  subsample=0.8, colsample_bytree=0.8, min_child_weight=2,
                  eval_metric="mlogloss", random_state=SEED, n_jobs=-1)

# Định nghĩa các khối đặc trưng theo tiền tố tên cột
BLOCKS = {
    "A_kg":    ("kg_", "jaccard_", "rsi_"),   # Khối A: cấu trúc đồ thị tri thức
    "B_kad":   ("kad_",),                      # Khối B: entropy / khoảng cách đồ thị
    "C_emb":   ("emb_",),                      # Khối C: ngữ nghĩa PhoBERT (đông lạnh)
    "meta":    ("entity_match_coverage",),     # meta: độ tin cậy khớp thực thể
}


##############################################################################
# Ordinal logistic regression (proportional-odds, McCullagh 1980) — đối
# chiếu với XGBoost NOMINAL: hiện Dễ<TB<Khó bị coi là 3 lớp KHÔNG liên quan
# gì nhau (nhầm Dễ->Khó bị phạt như nhầm Dễ->TB), trong khi thứ tự thật sự
# có ý nghĩa. Đây là phản biện Thuy et al. EvalLAC'25 đã ghi trong
# docs/RELATED_WORK.md — hội đồng có thể hỏi. Không dùng mord/statsmodels
# (không có sẵn trong môi trường) — tự cài đặt bằng scipy.optimize để không
# thêm dependency mới.
#
# Mô hình: điểm ẩn s = X @ beta; P(y<=0) = sigmoid(theta0 - s),
# P(y<=1) = sigmoid(theta1 - s), theta1 = theta0 + softplus(delta) > theta0
# (đảm bảo thứ tự ngưỡng). Khác XGBoost, mô hình tuyến tính này KHÔNG xử lý
# được NaN -> phải impute (median, fit trên train fold, không rò rỉ) trước.
##############################################################################

def _ordinal_nll(params, X, y, sample_weight, l2=1.0):
    n_feat = X.shape[1]
    beta = params[:n_feat]
    theta0, delta = params[n_feat], params[n_feat + 1]
    theta1 = theta0 + np.log1p(np.exp(delta))  # softplus, đảm bảo theta1 > theta0
    s = X @ beta
    sig = lambda z: 1.0 / (1.0 + np.exp(-z))
    p_le0 = sig(theta0 - s)
    p_le1 = sig(theta1 - s)
    eps = 1e-9
    p = np.where(y == 0, p_le0,
                np.where(y == 1, p_le1 - p_le0, 1 - p_le1))
    # Trọng số cân bằng lớp (giống sample_weight của XGBoost ở M1-M5) — thiếu
    # bước này thì mô hình chỉ tối ưu log-likelihood không trọng số, thiên
    # lệch mạnh về lớp đa số (Medium/Easy) và gần như không đoán được Hard
    # (15,5% dữ liệu) — đo được: F1_Hard rơi từ 0,22 (M1) xuống 0,05.
    nll = -(sample_weight * np.log(np.clip(p, eps, 1.0))).sum()
    return nll + l2 * (beta @ beta)


def fit_ordinal_logit(X: np.ndarray, y: np.ndarray, sample_weight: np.ndarray,
                      l2: float = 1.0):
    n_feat = X.shape[1]
    x0 = np.zeros(n_feat + 2)
    x0[n_feat] = -0.5  # theta0 ban đầu
    x0[n_feat + 1] = np.log(np.exp(1.0) - 1)  # softplus(delta0) = 1.0
    res = minimize(_ordinal_nll, x0, args=(X, y, sample_weight, l2),
                   method="L-BFGS-B", options={"maxiter": 500})
    return res.x


def predict_ordinal_logit(params: np.ndarray, X: np.ndarray) -> np.ndarray:
    n_feat = X.shape[1]
    beta = params[:n_feat]
    theta0, delta = params[n_feat], params[n_feat + 1]
    theta1 = theta0 + np.log1p(np.exp(delta))
    s = X @ beta
    sig = lambda z: 1.0 / (1.0 + np.exp(-z))
    p0 = sig(theta0 - s)
    p1 = sig(theta1 - s) - p0
    p2 = 1 - p0 - p1
    return np.argmax(np.stack([p0, p1, p2], axis=1), axis=1)


def run_ordinal_logit_cv(df: pd.DataFrame, cols: list, y: np.ndarray,
                         cv: list, sample_weight: np.ndarray) -> np.ndarray:
    """OOF predict bằng ordinal logit trên `cols`, impute+scale RIÊNG cho
    từng fold (fit trên train, transform test — không rò rỉ)."""
    X_raw = df[cols].values
    y_pred = np.empty(len(y), dtype=int)
    for tr, te in cv:
        imputer = SimpleImputer(strategy="median")
        X_tr = imputer.fit_transform(X_raw[tr])
        X_te = imputer.transform(X_raw[te])
        scaler = StandardScaler()
        X_tr = scaler.fit_transform(X_tr)
        X_te = scaler.transform(X_te)
        params = fit_ordinal_logit(X_tr, y[tr], sample_weight[tr])
        y_pred[te] = predict_ordinal_logit(params, X_te)
    return y_pred


def load_labels(keep_duplicates: bool = False) -> dict:
    """Nhãn mới nhất (sau voting 3 phiếu) theo mcq_id.

    Mặc định chỉ lấy bản canonical — bộ crawl có ~55% bản sao, giữ lại thì
    bản sao rơi vào cả train lẫn test và mọi chỉ số bị thổi phồng.
    """
    lab = {}
    for fname in ("mcq_samples.json", "mcq_crawled.json"):
        p = REPO / "subjects" / "history" / "samples" / fname
        if p.exists():
            for q in json.loads(p.read_text(encoding="utf-8")):
                if q.get("difficulty") and (keep_duplicates
                                            or q.get("is_canonical", True)):
                    lab[q["id"]] = q["difficulty"]
    return lab


def load_groups() -> dict:
    """mcq_id -> dup_group, để nhốt mọi bản sao vào cùng một fold."""
    g = {}
    for fname in ("mcq_samples.json", "mcq_crawled.json"):
        p = REPO / "subjects" / "history" / "samples" / fname
        if p.exists():
            for q in json.loads(p.read_text(encoding="utf-8")):
                if q.get("dup_group") is not None:
                    g[q["id"]] = q["dup_group"]
    return g


def load_texts() -> dict:
    """Văn bản câu hỏi (stem + các phương án) cho baseline TF-IDF."""
    txt = {}
    for fname in ("mcq_samples.json", "mcq_crawled.json"):
        p = REPO / "subjects" / "history" / "samples" / fname
        if p.exists():
            for q in json.loads(p.read_text(encoding="utf-8")):
                if q.get("difficulty"):
                    txt[q["id"]] = " ".join(
                        [q["stem"], q["correct"]] + list(q["distractors"]))
    return txt


def top_ngrams(texts, y, n=12) -> None:
    """In các cụm từ mà baseline TF-IDF dựa vào nhiều nhất cho từng nhãn —
    dùng để kiểm tra nhãn có bị quyết định bởi KHUÔN MẪU CÂU HỎI hay không."""
    vec = TfidfVectorizer(ngram_range=(1, 3), min_df=3, max_features=60000)
    X = vec.fit_transform(texts)
    clf = LogisticRegression(max_iter=2000, class_weight="balanced").fit(X, y)
    names = np.array(vec.get_feature_names_out())
    print("\nCụm từ quyết định nhãn theo TF-IDF (kiểm tra nhãn bề mặt):")
    for ci, cname in enumerate(["Dễ", "Trung bình", "Khó"]):
        top = np.argsort(clf.coef_[ci])[-n:][::-1]
        print(f"  {cname:<11}: {', '.join(names[top])}")


def cols_of(df: pd.DataFrame, prefixes) -> list:
    return [c for c in df.columns
            if c not in ("mcq_id", "label") and c.startswith(tuple(prefixes))]


def evaluate(name: str, y, y_pred, n_feat) -> dict:
    return {
        "cấu hình": name,
        "n_feat": n_feat,
        "accuracy": accuracy_score(y, y_pred),
        "macro_F1": f1_score(y, y_pred, average="macro"),
        "QWK": cohen_kappa_score(y, y_pred, weights="quadratic"),
        "F1_Hard": f1_score(y, y_pred, average=None)[2],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="ma trận feature đã cache")
    ap.add_argument("--oof-phobert", help="CSV out-of-fold prob từ Colab "
                                          "(cột: mcq_id,p_easy,p_medium,p_hard)")
    ap.add_argument("--out", help="lưu bảng kết quả ra CSV")
    ap.add_argument("--keep-duplicates", action="store_true",
                    help="giữ cả bản sao để train; vẫn KHÔNG rò rỉ vì fold chia "
                         "theo dup_group. Cho nhiều dữ liệu train hơn.")
    ap.add_argument("--show-ngrams", action="store_true",
                    help="in các cụm từ TF-IDF dựa vào (chẩn đoán nhãn bề mặt)")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    lab = load_labels(keep_duplicates=args.keep_duplicates)
    df["label"] = df["mcq_id"].map(lab)
    df = df[df["label"].notna()].reset_index(drop=True)
    y = df["label"].map(LABEL2ID).values

    # Trọng số cân bằng lớp + 5-fold DÙNG CHUNG cho mọi cấu hình.
    # Dùng StratifiedGroupKFold theo dup_group: mọi bản sao của cùng một nội
    # dung nằm cùng fold ⇒ không rò rỉ, kể cả khi giữ nguyên bản sao để train.
    w = (len(y) / (3 * np.bincount(y)))[y]
    gmap = load_groups()
    g = np.array([gmap.get(i, -1) for i in df["mcq_id"]])
    if (g == -1).any():
        n_miss = int((g == -1).sum())
        print(f"  ⚠ {n_miss} câu thiếu dup_group — mỗi câu tự thành 1 nhóm.")
        g[g == -1] = -np.arange(1, n_miss + 1)
    cv = list(StratifiedGroupKFold(n_splits=5, shuffle=True,
                                   random_state=SEED).split(df, y, groups=g))
    for tr, te in cv:
        assert not (set(g[tr]) & set(g[te])), "rò rỉ nhóm giữa các fold!"
    print(f"n = {len(df)} câu | {len(set(g))} nhóm nội dung | phân bố: "
          f"{dict(zip(['Easy','Medium','Hard'], np.bincount(y)))}")
    print("  CV: StratifiedGroupKFold(5, groups=dup_group) — đã assert không rò rỉ\n")

    rows = []

    def run_xgb(name, cols):
        if not cols:
            return
        X = df[cols].values
        p = cross_val_predict(XGBClassifier(**XGB_PARAMS), X, y, cv=cv,
                              params={"sample_weight": w})
        rows.append(evaluate(name, y, p, len(cols)))
        print(f"  ✓ {name}")

    # ---------- Baseline ----------
    p = cross_val_predict(DummyClassifier(strategy="most_frequent"),
                          np.zeros((len(y), 1)), y, cv=cv)
    rows.append(evaluate("B0. Đoán lớp đa số", y, p, 0))
    print("  ✓ B0. Đoán lớp đa số")

    texts = load_texts()
    if texts:
        Xt = np.array([texts.get(i, "") for i in df["mcq_id"]])
        tfidf = make_pipeline(
            TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000),
            LogisticRegression(max_iter=2000, class_weight="balanced"))
        p = cross_val_predict(tfidf, Xt, y, cv=cv)
        rows.append(evaluate("B1. TF-IDF + Logistic (chỉ văn bản)", y, p, -1))
        print("  ✓ B1. TF-IDF + Logistic")
        if args.show_ngrams:
            top_ngrams(Xt, y)

    # ---------- Mô hình đầy đủ & tháo từng khối ----------
    all_cols = [c for c in df.columns if c not in ("mcq_id", "label")]
    run_xgb("M1. ĐẦY ĐỦ (mọi đặc trưng)", all_cols)

    for blk, pref in BLOCKS.items():
        keep = [c for c in all_cols if c not in cols_of(df, pref)]
        run_xgb(f"M2. BỎ khối {blk}", keep)

    # ---------- Chỉ dùng riêng từng khối ----------
    for blk, pref in BLOCKS.items():
        run_xgb(f"M3. CHỈ khối {blk}", cols_of(df, pref))

    # Câu hỏi cốt lõi: tri thức có cấu trúc (A+B) vs ngữ nghĩa văn bản (C)
    run_xgb("M4. CHỈ tri thức (A+B+meta, KHÔNG PhoBERT)",
            cols_of(df, BLOCKS["A_kg"] + BLOCKS["B_kad"] + BLOCKS["meta"]))
    run_xgb("M5. CHỈ ngữ nghĩa (C, PhoBERT đông lạnh)", cols_of(df, BLOCKS["C_emb"]))

    # ---------- Ordinal (proportional-odds) vs nominal (M1) ----------
    # M1 coi Dễ/TB/Khó là 3 lớp không liên quan; đây là mô hình có tính thứ tự
    # (Dễ<TB<Khó). QWK tăng rõ so với M1 -> việc bỏ qua thứ tự đang mất thông
    # tin thật; QWK không đổi -> XGBoost nominal đã "tự học" được thứ tự.
    print("  (M8 dùng scipy.optimize, chậm hơn XGBoost — có thể mất một lúc)")
    p = run_ordinal_logit_cv(df, all_cols, y, cv, w)
    rows.append(evaluate("M8. ORDINAL LOGIT (proportional-odds, mọi đặc trưng)",
                         y, p, len(all_cols)))
    print("  ✓ M8. ORDINAL LOGIT")

    # ---------- Stacking với PhoBERT fine-tuned (nếu có OOF từ Colab) ----------
    if args.oof_phobert and Path(args.oof_phobert).exists():
        oof = pd.read_csv(args.oof_phobert)
        m = df[["mcq_id"]].merge(oof, on="mcq_id", how="left")
        pcols = [c for c in oof.columns if c != "mcq_id"]
        if m[pcols].isna().any().any():
            print("  ⚠ thiếu OOF cho một số câu — bỏ qua stacking")
        else:
            # PhoBERT một mình (argmax xác suất out-of-fold)
            p = m[pcols].values.argmax(axis=1)
            rows.append(evaluate("M6. PhoBERT fine-tune (chỉ văn bản)", y, p, -1))
            print("  ✓ M6. PhoBERT fine-tune")
            # Stacking: đặc trưng tri thức + xác suất PhoBERT
            df2 = df.copy()
            for c in pcols:
                df2[c] = m[c].values
            X = df2[[c for c in df2.columns if c not in ("mcq_id", "label")]].values
            p = cross_val_predict(XGBClassifier(**XGB_PARAMS), X, y, cv=cv,
                                  params={"sample_weight": w})
            rows.append(evaluate("M7. STACKING (tri thức + PhoBERT)", y, p,
                                 X.shape[1]))
            print("  ✓ M7. STACKING")
    else:
        print("\n  (chưa có --oof-phobert: chạy notebook Colab trước để có M6, M7)")

    # ---------- Báo cáo ----------
    res = pd.DataFrame(rows)
    print("\n" + "=" * 92)
    print("KẾT QUẢ ABLATION (StratifiedGroupKFold 5-fold, cùng fold cho mọi cấu hình)")
    print("=" * 92)
    print(res.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    full = res[res["cấu hình"].str.startswith("M1.")]
    if not full.empty:
        base = full.iloc[0]
        print("\nMức RỚT khi bỏ từng khối (so với M1 đầy đủ) — càng rớt nhiều "
              "= khối đó càng quan trọng:")
        for _, r in res[res["cấu hình"].str.startswith("M2.")].iterrows():
            print(f"  {r['cấu hình']:<28} accuracy {r['accuracy']-base['accuracy']:+.4f} | "
                  f"QWK {r['QWK']-base['QWK']:+.4f}")

        ordinal = res[res["cấu hình"].str.startswith("M8.")]
        if not ordinal.empty:
            o = ordinal.iloc[0]
            d_qwk = o["QWK"] - base["QWK"]
            d_acc = o["accuracy"] - base["accuracy"]
            d_hard = o["F1_Hard"] - base["F1_Hard"]
            print(f"\nOrdinal (M8) so với Nominal (M1) — cùng bộ đặc trưng: "
                  f"QWK {d_qwk:+.4f} | accuracy {d_acc:+.4f} | F1_Hard {d_hard:+.4f}")
            if d_qwk > 0.01 and d_acc < -0.02:
                print("  QWK tăng + accuracy giảm -> ordinal đánh đổi accuracy tổng thể để xếp "
                      "hạng đúng thứ tự hơn (thường kèm F1_Hard tăng vì lớp Khó là thiểu số "
                      "15,5% dữ liệu) — nêu rõ đây là trade-off, không phải ordinal 'thắng tuyệt đối'.")
            elif d_qwk > 0.01:
                print("  QWK tăng rõ, accuracy không giảm -> ordinal tốt hơn nominal trên cả 2 mặt.")
            else:
                print("  QWK không đổi/giảm -> XGBoost nominal đã tự học được thứ tự, "
                      "ordinal không mang lại lợi ích rõ rệt.")

    if args.out:
        res.to_csv(args.out, index=False, encoding="utf-8")
        print(f"\nĐã lưu -> {args.out}")


if __name__ == "__main__":
    main()
