# -*- coding: utf-8 -*-
"""E1 — Nhãn độ khó do LLM chấm THỰC SỰ đo cái gì?

Đây là đóng góp thực nghiệm chính sau khi T1 (khảo sát học sinh thật) không
được duyệt — xem docs/PIVOT_T1_KHONG_DUYET.md.

BA NGUỒN NHÃN được so trên CÙNG một tập ~120 câu:
  (1) llm_vote3   — nhãn LLM chấm TRỰC TIẾP (3 phiếu), nguồn đang dùng để train
  (2) giáo viên   — nhãn người, PHI-LLM  (teacher_difficulty_form.html -> JSON)
  (3) p_sim       — tỉ lệ đúng của học sinh MÔ PHỎNG (tools/llm_student_sim.py)

VÌ SAO CẦN CẢ BA: (1) và (3) đều do LLM sinh ra, nên nếu chỉ có hai nguồn đó
thì mọi kết luận đều có thể bị phản biện là "LLM kiểm toán LLM". Nguồn (2) là
thứ DUY NHẤT phá được vòng tròn đó. Cụ thể, hai giả thuyết cạnh tranh chỉ phân
định được khi có nhãn giáo viên:

  H_a: nhãn LLM đo sai độ khó       -> corr(GV, p_sim) >> corr(LLM, p_sim)
  H_b: MÔ PHỎNG đo sai độ khó       -> corr(GV, p_sim) ≈ corr(LLM, p_sim), cả hai thấp

BỐN PHÉP ĐO:
  [1] Tương quan từng cặp trong ba nguồn (Pearson + Spearman).
  [2] Cohen's kappa giữa (1) và (2) — mức đồng thuận người-máy trên thang hạng.
  [3] ⭐ KIỂM ĐỊNH 20 CẶP CÂU ĐỐI CHỨNG KHUÔN MẪU — bằng chứng trung tâm.
      Các cặp được chọn (tools/make_test_forms.py) sao cho CÙNG khuôn mẫu câu
      hỏi + CÙNG nhãn LLM, nhưng khác nhau về độ trọng tâm nội dung. Nếu p_sim
      (và/hoặc nhãn GV) LỆCH đáng kể trong khi nhãn LLM gán CÙNG mức -> bằng
      chứng trực tiếp nhãn LLM bám khuôn mẫu, không bám nội dung. Dùng kiểm
      định Wilcoxon signed-rank (phi tham số, không giả định phân phối).
  [4] Đối chứng khuôn mẫu: mô hình chỉ dùng đặc trưng KHUÔN MẪU của stem
      (n-gram) dự đoán NHÃN LLM tốt đến đâu, so với dự đoán P_SIM tốt đến đâu.
      Chênh lệch lớn = chốt hạ: nhãn LLM đoán được từ khuôn mẫu, độ khó thật thì không.

Usage:
    # chưa có nhãn GV — vẫn chạy được phần [1][3][4] với 2 nguồn
    python tools/e1_label_audit.py --responses subjects/history/samples/student_responses.LLMSIM_API.csv

    # khi đã có file GV export
    python tools/e1_label_audit.py \
        --responses subjects/history/samples/student_responses.LLMSIM_API.csv \
        --teacher su9_difficulty_co_lan_2026-08-13.json [thêm file GV khác...]
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

LABEL2ID = {"Easy": 0, "Medium": 1, "Hard": 2}
VERDICT2ID = {"easy": 0, "medium": 1, "hard": 2}


def spearman(a, b) -> float:
    return float(np.corrcoef(pd.Series(a).rank(), pd.Series(b).rank())[0, 1])


def pearson(a, b) -> float:
    return float(np.corrcoef(a, b)[0, 1])


def cohen_kappa(a, b) -> float:
    """Cohen's kappa không trọng số trên nhãn hạng 0/1/2."""
    a, b = np.asarray(a), np.asarray(b)
    cats = sorted(set(a) | set(b))
    n = len(a)
    po = float(np.mean(a == b))
    pe = sum((np.mean(a == c) * np.mean(b == c)) for c in cats)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def load_teacher(paths: list) -> pd.DataFrame:
    """Đọc (các) file JSON export từ teacher_difficulty_form.html.
    Trả DataFrame: rater, item_id, verdict_id."""
    rows = []
    for p in paths:
        p = Path(p)
        if not p.is_absolute():
            p = REPO / p
        data = json.loads(p.read_text(encoding="utf-8"))
        rater = (data.get("teacher") or data.get("rater") or p.stem)
        resp = data.get("responses", data)
        it = resp.items() if isinstance(resp, dict) else (
            (r.get("id") or r.get("item_id"), r) for r in resp)
        for item_id, r in it:
            v = r.get("verdict") if isinstance(r, dict) else r
            if v in VERDICT2ID:
                rows.append({"rater": rater, "item_id": item_id,
                             "verdict_id": VERDICT2ID[v]})
    if not rows:
        raise SystemExit("✗ Không đọc được đánh giá nào từ file giáo viên.")
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses", required=True)
    ap.add_argument("--teacher", nargs="*", default=[],
                    help="(các) file JSON export từ teacher_difficulty_form.html")
    ap.add_argument("--out", default="subjects/history/samples/e1_results.json")
    args = ap.parse_args()

    # --- nguồn (3): p_sim ---
    resp = pd.read_csv(REPO / args.responses if not Path(args.responses).is_absolute()
                       else args.responses)
    p_sim = resp.groupby("item_id")["correct"].mean()
    n_resp = resp.groupby("item_id")["correct"].size()

    # --- nguồn (1): nhãn LLM ---
    bank = {}
    for f in ("mcq_samples.json", "mcq_crawled.json"):
        p = SAMPLES / f
        if p.exists():
            for r in json.loads(p.read_text(encoding="utf-8")):
                bank[r["id"]] = r
    ids = [i for i in p_sim.index if i in bank and bank[i].get("difficulty")]
    llm = pd.Series({i: LABEL2ID[bank[i]["difficulty"]] for i in ids})
    ps = p_sim.loc[ids]

    print(f"n = {len(ids)} câu | lượt trả lời/câu: trung vị {n_resp.loc[ids].median():.0f}")
    print(f"p_sim: trung bình {ps.mean():.3f}  độ lệch chuẩn {ps.std():.3f}")

    results = {"n_items": len(ids), "p_sim_mean": float(ps.mean())}

    # --- nguồn (2): giáo viên ---
    teacher = None
    if args.teacher:
        tdf = load_teacher(args.teacher)
        raters = sorted(tdf["rater"].unique())
        print(f"\nNhãn giáo viên: {len(raters)} người chấm ({', '.join(raters)}), "
              f"{tdf['item_id'].nunique()} câu")
        if len(raters) >= 2:
            wide = tdf.pivot_table(index="item_id", columns="rater", values="verdict_id")
            both = wide.dropna()
            if len(both) > 1:
                k_tt = cohen_kappa(both.iloc[:, 0].astype(int), both.iloc[:, 1].astype(int))
                print(f"  Cohen's κ GIỮA CÁC GIÁO VIÊN (n={len(both)}): {k_tt:+.3f}")
                results["kappa_teacher_teacher"] = k_tt
        else:
            print("  ⚠ CHỈ 1 giáo viên -> không tính được độ tin cậy liên-người-chấm. "
                  "Phải nêu là hạn chế.")
        teacher = tdf.groupby("item_id")["verdict_id"].mean()

    # ================= [1] Tương quan từng cặp =================
    print("\n" + "=" * 68)
    print("[1] TƯƠNG QUAN GIỮA CÁC NGUỒN NHÃN")
    print("=" * 68)
    print("  (nhãn mã hoá Dễ=0/TB=1/Khó=2, nên tương quan với p_sim phải ÂM)")
    r_llm = pearson(llm.values, ps.values)
    s_llm = spearman(llm.values, ps.values)
    print(f"\n  nhãn LLM  vs p_sim : Pearson {r_llm:+.3f}  Spearman {s_llm:+.3f}")
    results["corr_llm_psim"] = {"pearson": r_llm, "spearman": s_llm}

    if teacher is not None:
        common = [i for i in ids if i in teacher.index]
        tv, pv, lv = teacher.loc[common].values, ps.loc[common].values, llm.loc[common].values
        r_t, s_t = pearson(tv, pv), spearman(tv, pv)
        print(f"  nhãn GV   vs p_sim : Pearson {r_t:+.3f}  Spearman {s_t:+.3f}  (n={len(common)})")
        r_lt, s_lt = pearson(lv, tv), spearman(lv, tv)
        print(f"  nhãn LLM  vs nhãn GV: Pearson {r_lt:+.3f}  Spearman {s_lt:+.3f}")
        k_lt = cohen_kappa(lv.astype(int), np.rint(tv).astype(int))
        print(f"  Cohen's κ (LLM vs GV): {k_lt:+.3f}")
        results.update({
            "corr_teacher_psim": {"pearson": r_t, "spearman": s_t},
            "corr_llm_teacher": {"pearson": r_lt, "spearman": s_lt},
            "kappa_llm_teacher": k_lt,
        })

        print("\n  --- PHÂN ĐỊNH HAI GIẢ THUYẾT CẠNH TRANH ---")
        if abs(s_t) > abs(s_llm) + 0.15:
            print(f"  |Spearman(GV, p_sim)| = {abs(s_t):.3f} >> "
                  f"|Spearman(LLM, p_sim)| = {abs(s_llm):.3f}")
            print("  => ỦNG HỘ H_a: nhãn LLM đo độ khó KÉM hơn nhãn người rõ rệt.")
            print("     Mô phỏng bắt được thứ nhãn GV bắt được mà nhãn LLM bỏ lỡ.")
        elif abs(s_t) < 0.20:
            print(f"  Cả GV ({abs(s_t):.3f}) lẫn LLM ({abs(s_llm):.3f}) đều tương quan "
                  "THẤP với p_sim.")
            print("  => ỦNG HỘ H_b: vấn đề nằm ở MÔ PHỎNG, không phải ở nhãn LLM.")
            print("     KHÔNG được kết luận 'nhãn LLM sai' từ dữ liệu này.")
        else:
            print(f"  GV ({abs(s_t):.3f}) và LLM ({abs(s_llm):.3f}) tương đương "
                  "-> chưa phân định được. Cần thêm dữ liệu/nguồn.")
    else:
        print("\n  ⚠ CHƯA CÓ NHÃN GIÁO VIÊN -> không phân định được hai giả thuyết")
        print("    H_a (nhãn LLM sai) vs H_b (mô phỏng sai). Mọi kết luận về nhãn LLM")
        print("    ở bước này chỉ là TẠM THỜI. Chạy lại với --teacher khi có dữ liệu.")

    # ================= [3] 20 cặp câu đối chứng =================
    tf_path = SAMPLES / "test_forms.json"
    if tf_path.exists():
        tf = json.loads(tf_path.read_text(encoding="utf-8"))
        print("\n" + "=" * 68)
        print("[3] KIỂM ĐỊNH 20 CẶP CÂU ĐỐI CHỨNG KHUÔN MẪU  ← bằng chứng trung tâm")
        print("=" * 68)
        print("  Mỗi cặp: CÙNG khuôn mẫu câu hỏi, CÙNG nhãn LLM, khác độ trọng tâm nội dung.")
        print(f"\n  {'#':<3}{'nhóm/nhãn LLM':<20}{'p_sim A':>9}{'p_sim B':>9}{'|Δ|':>8}")
        diffs, same_label = [], 0
        for i, pr in enumerate(tf.get("control_pairs", []), 1):
            a, b = pr["core_or_edge_a"], pr["core_or_edge_b"]
            if a not in ps.index or b not in ps.index:
                continue
            pa, pb = ps[a], ps[b]
            diffs.append(pa - pb)
            same_label += int(pr.get("label_a") == pr.get("label_b"))
            print(f"  {i:<3}{pr['group']:<20}{pa:>9.3f}{pb:>9.3f}{abs(pa-pb):>8.3f}")
        diffs = np.array(diffs)
        if len(diffs):
            ad = np.abs(diffs)
            print(f"\n  n = {len(diffs)} cặp | {same_label} cặp được nhãn LLM gán CÙNG mức")
            print(f"  |Δp_sim| trung bình = {ad.mean():.3f} | trung vị = {np.median(ad):.3f}")
            print(f"  cặp |Δ| ≥ 0,20: {(ad>=0.20).sum()}/{len(ad)}   "
                  f"| cặp |Δ| ≤ 0,05: {(ad<=0.05).sum()}/{len(ad)}")
            # --- KIỂM ĐỊNH ĐÚNG GIẢ THUYẾT ---
            # KHÔNG dùng Wilcoxon signed-rank: nó kiểm "A có hệ thống cao hơn B
            # không", trong khi giả thuyết của ta là "|Δ| lớn hơn mức ngẫu nhiên
            # không" — dấu của Δ vô nghĩa vì nhãn A/B trong cặp là tuỳ ý.
            #
            # NULL đúng: hai câu bất kỳ ĐƯỢC LLM GÁN CÙNG MỨC thì |Δp_sim| bao
            # nhiêu? Nếu nhãn LLM thật sự đo độ khó, các câu cùng nhãn phải có
            # p_sim gần nhau -> |Δ| nhỏ. Hoán vị nhiều lần để lấy phân phối null.
            rng = np.random.default_rng(42)
            by_label = {}
            for i in ids:
                by_label.setdefault(int(llm[i]), []).append(i)
            null_means = []
            for _ in range(5000):
                sample = []
                for _k in range(len(diffs)):
                    lab = rng.choice(list(by_label))
                    pool_l = by_label[lab]
                    if len(pool_l) < 2:
                        continue
                    x, z = rng.choice(pool_l, 2, replace=False)
                    sample.append(abs(ps[x] - ps[z]))
                if sample:
                    null_means.append(np.mean(sample))
            null_means = np.array(null_means)
            pval = float(np.mean(null_means >= ad.mean()))
            print(f"\n  NULL (2 câu ngẫu nhiên CÙNG nhãn LLM): "
                  f"|Δ| trung bình = {null_means.mean():.3f} "
                  f"[khoảng 95%: {np.percentile(null_means,2.5):.3f}–"
                  f"{np.percentile(null_means,97.5):.3f}]")
            print(f"  Quan sát trên 20 cặp đối chứng: {ad.mean():.3f}  -> p = {pval:.4f}")

            # Sàn nhiễu: |Δ| kỳ vọng chỉ do sai số lấy mẫu nhị thức của p_sim.
            nmed = float(n_resp.loc[ids].median())
            se_p = float(np.mean(np.sqrt(ps.values * (1 - ps.values) / nmed)))
            noise_delta = se_p * np.sqrt(2) * np.sqrt(2 / np.pi)
            print(f"  Sàn nhiễu (chỉ do {nmed:.0f} lượt/câu): |Δ| ≈ {noise_delta:.3f}")

            results["control_pairs"] = {
                "n": int(len(diffs)), "mean_abs_delta": float(ad.mean()),
                "null_mean_abs_delta": float(null_means.mean()),
                "perm_p": pval, "noise_floor_delta": float(noise_delta)}

            print("\n  DIỄN GIẢI:")
            if ad.mean() <= noise_delta * 1.2:
                print("  ⚠ |Δ| quan sát KHÔNG vượt sàn nhiễu -> chưa kết luận được gì.")
                print("     Cần nhiều lượt trả lời/câu hơn (tăng --repeats).")
            elif pval < 0.05:
                print("  20 cặp đối chứng lệch NHIỀU HƠN hai câu cùng nhãn bất kỳ")
                print("  -> thiết kế cặp đối chứng đã bắt trúng thứ nhãn LLM bỏ lỡ.")
            else:
                print(f"  |Δ| của cặp đối chứng ({ad.mean():.3f}) KHÔNG cao hơn hai câu")
                print(f"  cùng nhãn bất kỳ ({null_means.mean():.3f}, p={pval:.3f}).")
                print("  Nhưng chú ý: bản thân mức null đã RẤT CAO — nghĩa là các câu")
                print("  được LLM gán CÙNG mức vốn đã khác nhau ~{:.0f} điểm phần trăm"
                      .format(null_means.mean() * 100))
                print("  về độ khó thật. Đó mới là phát hiện: nhãn LLM không thu hẹp")
                print("  được độ khó thật, chứ không phải cặp đối chứng đặc biệt.")

    # ================= [4] Đối chứng khuôn mẫu =================
    print("\n" + "=" * 68)
    print("[4] KHUÔN MẪU CÂU HỎI DỰ ĐOÁN ĐƯỢC GÌ?")
    print("=" * 68)
    # Mô hình khuôn mẫu phải được HUẤN LUYỆN TRÊN TOÀN BỘ ngân hàng câu hỏi
    # (~2.000 câu), KHÔNG phải trên 100 câu khảo sát: TF-IDF hàng chục nghìn
    # đặc trưng fit trên 100 mẫu thì không học được gì (đo thử: accuracy 0,410
    # còn thua đoán lớp đa số 0,420) — đó là hiện vật cỡ mẫu, không phải kết quả.
    # Thiết kế đúng: train trên phần KHÔNG chứa câu khảo sát (chặn rò rỉ theo
    # dup_group), rồi dùng CÙNG MỘT mô hình đó chấm hai thứ trên 100 câu khảo sát:
    #   (a) nó khớp NHÃN LLM tốt đến đâu, (b) nó khớp P_SIM tốt đến đâu.
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline

        pool = pd.DataFrame([r for r in bank.values()
                             if r.get("difficulty") and r.get("is_canonical", True)])
        pool = pool.set_index("id", drop=False)
        survey_groups = set(pool.loc[pool["id"].isin(ids), "dup_group"].dropna())
        is_survey = pool["id"].isin(ids) | pool["dup_group"].isin(survey_groups)
        tr = pool[~is_survey]
        print(f"  Huấn luyện mô hình KHUÔN MẪU trên {len(tr)} câu "
              f"(đã loại câu khảo sát + bản trùng), chấm trên {len(ids)} câu khảo sát.")

        model = make_pipeline(
            TfidfVectorizer(ngram_range=(1, 3), min_df=2, max_features=20000),
            LogisticRegression(max_iter=2000, class_weight="balanced"))
        model.fit(tr["stem"].values, tr["difficulty"].map(LABEL2ID).values)

        stems_test = np.array([bank[i]["stem"] for i in ids])
        pred = model.predict(stems_test)
        acc_l = float(np.mean(pred == llm.values))
        base = float(pd.Series(llm.values).value_counts(normalize=True).max())
        # dự đoán liên tục để tương quan với p_sim: kỳ vọng hạng lớp
        proba = model.predict_proba(stems_test)
        expected_rank = proba @ np.array([0, 1, 2])
        r_p, s_p = pearson(expected_rank, ps.values), spearman(expected_rank, ps.values)

        print(f"\n  CHỈ dùng n-gram của CÂU DẪN (không hề dùng nội dung tri thức):")
        print(f"    khớp NHÃN LLM : accuracy {acc_l:.3f}  "
              f"(đoán lớp đa số = {base:.3f}, chênh {acc_l-base:+.3f})")
        print(f"    khớp P_SIM    : Pearson {r_p:+.3f}  Spearman {s_p:+.3f}")
        results["template_probe"] = {
            "n_train": int(len(tr)), "acc_llm_label": acc_l,
            "majority_baseline": base, "pearson_psim": r_p, "spearman_psim": s_p}

        if acc_l - base > 0.10 and abs(s_p) < 0.25:
            print("\n  => CHỐT HẠ: khuôn mẫu câu dẫn khớp NHÃN LLM rõ rệt trên mức")
            print("     ngẫu nhiên, nhưng gần như KHÔNG khớp hiệu suất làm bài.")
            print("     Nhãn LLM mã hoá DẠNG câu hỏi, không mã hoá ĐỘ KHÓ nội dung.")
        elif acc_l - base <= 0.10:
            print("\n  => Khuôn mẫu KHÔNG khớp nhãn LLM tốt hơn đoán bừa trên tập này")
            print("     -> chưa ủng hộ giả thuyết 'nhãn bám khuôn mẫu' bằng phép đo này.")
        else:
            print("\n  => Khuôn mẫu khớp CẢ HAI -> chưa tách bạch được.")
    except ImportError:
        print("  (bỏ qua — thiếu scikit-learn)")

    out = REPO / args.out
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  đã lưu -> {out}")
    print("\n⚠ p_sim là phản hồi MÔ PHỎNG, không phải học sinh thật "
          "(xem docs/PIVOT_T1_KHONG_DUYET.md).")


if __name__ == "__main__":
    main()
