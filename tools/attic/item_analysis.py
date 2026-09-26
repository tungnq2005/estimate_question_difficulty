# -*- coding: utf-8 -*-
"""Phân tích cổ điển (CTT) từ phản hồi học sinh: p-value, độ phân biệt,
point-biserial, KR-20 (T3).

VÌ SAO CẦN: đây là bước biến dữ liệu làm bài thô (T4) thành ground truth tâm
trắc học dùng cho E1/E2/E3 trong kế hoạch Cold->Warm. Không có bước này thì
p-value không được kiểm định chất lượng trước khi dùng để kết luận.

INPUT MONG ĐỢI — `student_responses.csv` dạng LONG, 1 dòng = 1 học sinh trả
lời 1 câu:
    student_id, form, item_id, correct
    hs001,      A,    su9_vj_1958, 1
    hs001,      A,    su9_vj_1780, 0
    ...
`correct` là 0/1 (đã chấm đúng/sai theo đáp án — việc so khớp phương án chọn
với đáp án đúng làm ở bước xuất dữ liệu từ Google Form, KHÔNG phải ở đây).
`form` dùng để nhóm KR-20 theo từng đề (không trộn 3 đề vì học sinh không
cùng làm chung một bài).

CHỈ SỐ TÍNH:
  - p-value       : tỉ lệ trả lời đúng trên tổng số học sinh đã làm câu đó.
  - discrimination: chỉ số phân biệt cổ điển D = p(nhóm giỏi 27%) - p(nhóm
                     kém 27%) theo tổng điểm CÙNG ĐỀ (không tính điểm câu
                     đang xét vào tổng, tránh tương quan giả tạo phần-toàn).
  - point_biserial: tương quan điểm-nhị phân giữa đúng/sai câu đó và tổng
                     điểm hiệu chỉnh (cùng đề, đã loại câu đang xét).
  - KR-20 (theo từng đề): độ tin cậy nội tại của đề trắc nghiệm.
  - corr(nhãn LLM, p-value): tương quan Pearson + Spearman — trung tâm cho E1.

NGƯỠNG CẢNH BÁO (theo kiểm chứng #3 trong kế hoạch):
  - KR-20 < 0.7           -> đề chưa đủ tin cậy để rút kết luận chắc chắn.
  - discrimination < 0.2  -> câu không phân biệt được HS giỏi/kém, cân nhắc loại.
  - p-value ~0 hoặc ~1    -> câu quá khó/quá dễ, gần như không có phương sai.

Usage:
    python tools/item_analysis.py --responses subjects/history/samples/student_responses.csv
    python tools/item_analysis.py --demo    # dữ liệu MÔ PHỎNG để tự kiểm thử script
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


def make_demo_responses(forms_json: Path, n_students_per_form: int = 50,
                        seed: int = 42) -> pd.DataFrame:
    """Sinh phản hồi MÔ PHỎNG (IRT 1PL thô) chỉ để tự kiểm thử pipeline —
    KHÔNG dùng số liệu này để kết luận bất cứ điều gì về đề thật."""
    rng = np.random.default_rng(seed)
    forms = json.loads(forms_json.read_text(encoding="utf-8"))["forms"]
    true_b = {"Easy": -1.0, "Medium": 0.0, "Hard": 1.0}  # độ khó IRT giả định
    rows = []
    for form, items in forms.items():
        for s in range(n_students_per_form):
            sid = f"demo_{form}_{s:03d}"
            theta = rng.normal(0, 1)  # năng lực HS giả định
            for it in items:
                b = true_b[it["difficulty"]] + rng.normal(0, 0.3)
                p = 1 / (1 + np.exp(-(theta - b)))
                correct = int(rng.random() < p)
                rows.append({"student_id": sid, "form": form,
                            "item_id": it["id"], "correct": correct})
    return pd.DataFrame(rows)


def discrimination_and_pb(df_form: pd.DataFrame) -> pd.DataFrame:
    """df_form: cột student_id, item_id, correct — CHỈ của một đề.
    Trả DataFrame index=item_id, cột p_value, n, discrimination, point_biserial."""
    wide = df_form.pivot_table(index="student_id", columns="item_id",
                               values="correct", aggfunc="first")
    total_all = wide.sum(axis=1, skipna=True)
    out = []
    for item in wide.columns:
        col = wide[item].dropna()
        n = len(col)
        p = col.mean() if n else np.nan
        # tổng điểm hiệu chỉnh: loại câu đang xét khỏi tổng, tránh tương quan
        # giả tạo phần-toàn (part-whole inflation)
        rest_total = (total_all - wide[item].fillna(0)).loc[col.index]

        # --- Point-biserial thủ công (không phụ thuộc scipy) ---
        if n >= 2 and col.nunique() > 1 and rest_total.std(ddof=0) > 0:
            m1 = rest_total[col == 1].mean()
            m0 = rest_total[col == 0].mean()
            sn = rest_total.std(ddof=0)
            q = 1 - p
            pb = (m1 - m0) / sn * np.sqrt(p * q) if sn > 0 else np.nan
        else:
            pb = np.nan

        # --- Discrimination cổ điển D = p(top 27%) - p(bottom 27%) ---
        k = max(1, round(0.27 * n))
        order = rest_total.sort_values(ascending=False)
        top_ids = order.index[:k]
        bot_ids = order.index[-k:]
        if n >= 2 * k and k >= 1:
            d = col.loc[top_ids].mean() - col.loc[bot_ids].mean()
        else:
            d = np.nan

        out.append({"item_id": item, "n": n, "p_value": p,
                    "discrimination": d, "point_biserial": pb})
    return pd.DataFrame(out).set_index("item_id")


def kr20(df_form: pd.DataFrame) -> tuple:
    """KR-20 cho một đề (items nhị phân 0/1). Trả (kr20, n_students, n_items)."""
    wide = df_form.pivot_table(index="student_id", columns="item_id",
                               values="correct", aggfunc="first")
    wide = wide.dropna()  # KR-20 cổ điển cần ma trận đầy đủ (mọi HS làm mọi câu)
    if wide.shape[0] < 2 or wide.shape[1] < 2:
        return np.nan, wide.shape[0], wide.shape[1]
    k = wide.shape[1]
    p = wide.mean(axis=0)
    q = 1 - p
    var_total = wide.sum(axis=1).var(ddof=1)
    if var_total == 0:
        return np.nan, wide.shape[0], k
    return float((k / (k - 1)) * (1 - (p * q).sum() / var_total)), wide.shape[0], k


def corr_llm_pvalue(item_stats: pd.DataFrame, df_pool: pd.DataFrame) -> dict:
    """Tương quan giữa nhãn LLM (Easy<Medium<Hard) và p-value thật — trung
    tâm cho E1: nếu |corr| thấp, nhãn LLM không đo độ khó thật.

    Câu neo (anchor) xuất hiện ở CẢ 3 đề nên có 3 dòng trong item_stats; gộp
    trung bình có trọng số theo n trước khi tương quan để không đếm câu neo
    nặng gấp 3 lần câu thường."""
    def _wavg(g):
        w = g["n"].fillna(0)
        return (g["p_value"] * w).sum() / w.sum() if w.sum() > 0 else np.nan
    per_item_p = item_stats.reset_index().groupby("item_id").apply(
        _wavg, include_groups=False)
    merged = per_item_p.to_frame("p_value").join(
        df_pool.set_index("id")[["difficulty"]], how="inner")
    merged["llm_ord"] = merged["difficulty"].map(LABEL2ID)
    merged = merged.dropna(subset=["llm_ord", "p_value"])
    if len(merged) < 3:
        return {"n": len(merged), "pearson": np.nan, "spearman": np.nan}
    pearson = float(np.corrcoef(merged["llm_ord"], merged["p_value"])[0, 1])
    # Spearman thủ công qua rank (tránh phụ thuộc scipy)
    r1 = merged["llm_ord"].rank().values
    r2 = merged["p_value"].rank().values
    spearman = float(np.corrcoef(r1, r2)[0, 1])
    return {"n": len(merged), "pearson": pearson, "spearman": spearman}


def load_item_pool() -> pd.DataFrame:
    rows = []
    for fname in ("mcq_samples.json", "mcq_crawled.json"):
        p = REPO / "subjects" / "history" / "samples" / fname
        if p.exists():
            rows.extend(json.loads(p.read_text(encoding="utf-8")))
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses",
                    default="subjects/history/samples/student_responses.csv")
    ap.add_argument("--demo", action="store_true",
                    help="sinh phản hồi MÔ PHỎNG để tự kiểm thử script khi "
                         "chưa có dữ liệu HS thật (KHÔNG dùng để kết luận)")
    ap.add_argument("--forms", default="subjects/history/samples/test_forms.json")
    ap.add_argument("--out", default="subjects/history/samples/item_stats.json")
    args = ap.parse_args()

    forms_path = REPO / args.forms
    if args.demo:
        print("⚠ CHẾ ĐỘ DEMO: dữ liệu phản hồi là MÔ PHỎNG (IRT 1PL giả định), "
              "chỉ để kiểm thử pipeline — không phản ánh học sinh thật.\n")
        df = make_demo_responses(forms_path)
        args.out = "subjects/history/samples/item_stats.DEMO.json"
    else:
        resp_path = REPO / args.responses
        if not resp_path.exists():
            sys.exit(f"Chưa có {resp_path}. Chạy với --demo để kiểm thử pipeline "
                     f"trước khi có dữ liệu HS thật (T4).")
        df = pd.read_csv(resp_path)

    required = {"student_id", "form", "item_id", "correct"}
    missing = required - set(df.columns)
    if missing:
        sys.exit(f"Thiếu cột bắt buộc trong responses: {missing}")

    print(f"Nạp {len(df)} lượt trả lời | {df['student_id'].nunique()} học sinh | "
          f"{df['item_id'].nunique()} câu | {df['form'].nunique()} đề\n")

    all_stats, kr20_report = [], {}
    for form, g in df.groupby("form"):
        stats = discrimination_and_pb(g)
        stats["form"] = form
        all_stats.append(stats)
        k, n_s, n_i = kr20(g)
        kr20_report[form] = {"KR20": k, "n_students": int(n_s), "n_items": int(n_i)}
        flag = "⚠ THẤP (<0.7)" if (k == k and k < 0.7) else "OK"
        print(f"  Đề {form}: KR-20={k:.3f} ({n_s} HS đầy đủ x {n_i} câu) — {flag}"
             if k == k else f"  Đề {form}: KR-20 không tính được (thiếu dữ liệu)")

    item_stats = pd.concat(all_stats)
    item_stats.index.name = "item_id"

    n_low_disc = int((item_stats["discrimination"] < 0.2).sum())
    n_extreme_p = int(((item_stats["p_value"] <= 0.05)
                       | (item_stats["p_value"] >= 0.95)).sum())
    print(f"\n  Câu có discrimination < 0.2: {n_low_disc}/{len(item_stats)} "
          f"← cân nhắc loại khỏi phân tích chính")
    print(f"  Câu p-value cực trị (<=0.05 hoặc >=0.95): {n_extreme_p}/{len(item_stats)} "
          f"← gần như không có phương sai, ít thông tin cho IRT")

    pool = load_item_pool()
    corr = corr_llm_pvalue(item_stats, pool)
    print(f"\n  corr(nhãn LLM, p-value) trên {corr['n']} câu: "
          f"Pearson={corr['pearson']:.3f}  Spearman={corr['spearman']:.3f}")
    if corr["n"] >= 3 and abs(corr["pearson"]) < 0.3:
        print("  ⚠ Tương quan yếu -> bằng chứng nhãn LLM KHÔNG đo tốt độ khó thật (E1)")

    out = {
        "kr20_by_form": kr20_report,
        "n_low_discrimination": n_low_disc,
        "n_extreme_p_value": n_extreme_p,
        "corr_llm_vs_pvalue": corr,
        # LIST chứ không phải dict-keyed-by-item_id: câu neo (anchor) xuất
        # hiện ở CẢ 3 đề nên item_id không duy nhất trong item_stats — khoá
        # theo dict sẽ âm thầm ghi đè, mất 2/3 phép đo của mỗi câu neo.
        "items": [
            {k: (None if v != v else v) for k, v in row.items()}
            for _, row in item_stats.reset_index().iterrows()
        ],
    }
    out_path = REPO / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  đã lưu -> {out_path}")


if __name__ == "__main__":
    main()
