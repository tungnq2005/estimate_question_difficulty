# -*- coding: utf-8 -*-
"""Chuẩn hoá & so sánh các thang nhãn độ khó, tách ĐỘ NGHIÊM KHẮC khỏi THỨ TỰ.

VẤN ĐỀ: giáo viên gán "Khó" cho 7,8% câu, LLM gán ~32%. Hai người dùng THANG
KHÁC NHAU cho cùng một khái niệm. Nếu so trực tiếp thì lẫn lộn hai loại bất
đồng hoàn toàn khác nhau về hệ quả:

  (1) LỆCH NGƯỠNG (severity/leniency) — cùng thứ tự, khác chỗ đặt vạch chia.
      Đây KHÔNG phải bất đồng thật: chỉ cần hiệu chỉnh thang là khớp. Trong
      tâm trắc học đây là "rater severity", xử lý bằng mô hình đa mặt.
  (2) LỆCH THỨ TỰ — hai bên xếp hạng các câu khác nhau. Đây MỚI là bất đồng
      thật về việc câu nào khó hơn câu nào.

Cohen's κ trộn lẫn cả hai (κ phạt cả lệch ngưỡng), nên κ = -0,02 KHÔNG chứng
minh được hai nguồn xếp hạng khác nhau. Ngược lại Spearman miễn nhiễm với lệch
ngưỡng, nhưng bị SUY GIẢM MẠNH do đồng hạng khi chỉ có 3 mức cho ~90 câu.

BỐN PHÉP ĐO, từ thô đến đúng nhất:
  [1] Phân bố biên từng nguồn -> định lượng độ nghiêm khắc.
  [2] Kendall tau-b — hiệu chỉnh đồng hạng (Spearman thì không).
  [3] ⭐ TƯƠNG QUAN POLYCHORIC — giả định tồn tại một biến độ khó LIÊN TỤC ẩn,
      mỗi người chấm cắt nó ở ngưỡng riêng; ước lượng tương quan của biến ẩn
      ĐỘC LẬP HOÀN TOÀN với chỗ đặt ngưỡng. Đây là câu trả lời đúng về mặt
      phương pháp cho câu hỏi "hai người có cùng cảm nhận thứ tự không?".
  [4] TƯƠNG QUAN POLYSERIAL giữa nhãn hạng và p_sim (liên tục) — cùng tinh
      thần, cho trường hợp một bên liên tục.
  [5] ĐỒNG THUẬN SAU KHI KHỚP PHÂN BỐ BIÊN — ép nhãn GV về đúng tỉ lệ
      Dễ/TB/Khó của nhãn LLM theo thứ hạng, rồi đo lại. Chênh lệch giữa đồng
      thuận trước và sau = phần bất đồng CHỈ do lệch ngưỡng.

Usage:
    python tools/label_calibration.py \
        --teacher subjects/history/samples/su9_difficulty_teacher1_2026-08-17.json \
        --responses subjects/history/samples/student_responses.LLMSIM_API.csv
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import norm, kendalltau, multivariate_normal

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
SAMPLES = REPO / "subjects" / "history" / "samples"
LABEL2ID = {"Easy": 0, "Medium": 1, "Hard": 2}
VERDICT2ID = {"easy": 0, "medium": 1, "hard": 2}
NAMES = ["Dễ", "TB", "Khó"]


def thresholds_from(x: np.ndarray, k: int = 3) -> np.ndarray:
    """Ngưỡng probit suy từ phân bố biên: τ_j = Φ⁻¹(tỉ lệ tích luỹ)."""
    cum = np.cumsum([np.mean(x == c) for c in range(k)])[:-1]
    cum = np.clip(cum, 1e-6, 1 - 1e-6)
    return norm.ppf(cum)


def bivnorm_cdf(a: float, b: float, rho: float) -> float:
    if not np.isfinite(a) or not np.isfinite(b):
        return float(norm.cdf(min(a, b))) if (np.isinf(a) or np.isinf(b)) else 0.0
    return float(multivariate_normal.cdf([a, b], mean=[0, 0],
                                         cov=[[1, rho], [rho, 1]]))


def polychoric(x: np.ndarray, y: np.ndarray, k: int = 3) -> float:
    """Ước lượng ML hai bước: ngưỡng lấy từ phân bố biên, tối ưu rho trên
    bảng chéo. Trả tương quan của BIẾN ẨN liên tục — bất biến với chỗ đặt
    ngưỡng, tức không bị ảnh hưởng bởi việc một người chấm dễ dãi hơn."""
    tx = np.concatenate([[-np.inf], thresholds_from(x, k), [np.inf]])
    ty = np.concatenate([[-np.inf], thresholds_from(y, k), [np.inf]])
    tab = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            tab[i, j] = np.sum((x == i) & (y == j))

    def negll(rho: float) -> float:
        rho = float(np.clip(rho, -0.995, 0.995))
        ll = 0.0
        for i in range(k):
            for j in range(k):
                if tab[i, j] == 0:
                    continue
                p = (bivnorm_cdf(tx[i + 1], ty[j + 1], rho)
                     - bivnorm_cdf(tx[i], ty[j + 1], rho)
                     - bivnorm_cdf(tx[i + 1], ty[j], rho)
                     + bivnorm_cdf(tx[i], ty[j], rho))
                ll += tab[i, j] * np.log(max(p, 1e-12))
        return -ll

    return float(minimize_scalar(negll, bounds=(-0.95, 0.95),
                                 method="bounded").x)


def polyserial(ordinal: np.ndarray, cont: np.ndarray, k: int = 3) -> float:
    """Ước lượng hai bước: r_ps = r_pearson · s_y / Σ φ(τ_j).
    Dùng khi một biến hạng (nhãn) và một biến liên tục (p_sim)."""
    r = float(np.corrcoef(ordinal, cont)[0, 1])
    tau = thresholds_from(ordinal, k)
    denom = float(np.sum(norm.pdf(tau)))
    if denom < 1e-9:
        return float("nan")
    return float(np.clip(r * np.std(cont, ddof=1) / (np.std(cont, ddof=1) * denom), -1, 1)) \
        if False else float(np.clip(r / denom, -1, 1))


def cohen_kappa(a: np.ndarray, b: np.ndarray) -> float:
    cats = sorted(set(a) | set(b))
    po = float(np.mean(a == b))
    pe = sum(np.mean(a == c) * np.mean(b == c) for c in cats)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def match_marginals(src: np.ndarray, target: np.ndarray, k: int = 3) -> np.ndarray:
    """Gán lại nhãn `src` theo THỨ HẠNG sao cho phân bố biên khớp `target`.
    Giữ nguyên thứ tự tương đối của src, chỉ dời ngưỡng."""
    props = np.cumsum([np.mean(target == c) for c in range(k)])
    order = np.argsort(np.argsort(src, kind="stable"), kind="stable")
    q = order / max(len(src) - 1, 1)
    out = np.zeros(len(src), dtype=int)
    for i, v in enumerate(q):
        out[i] = int(np.searchsorted(props[:-1], v, side="right"))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", required=True)
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

    ids = [i for i in teacher if i in bank and bank[i].get("difficulty")
           and i in p_sim.index]
    gv = np.array([teacher[i] for i in ids])
    llm = np.array([LABEL2ID[bank[i]["difficulty"]] for i in ids])
    ps = np.array([p_sim[i] for i in ids])
    # p_sim -> hạng độ khó (p cao = dễ), để so cùng chiều với nhãn
    n = len(ids)
    print(f"n = {n} câu có đủ ba nguồn\n")

    # ---------------- [1] độ nghiêm khắc ----------------
    print("=" * 70)
    print("[1] PHÂN BỐ BIÊN — ĐỘ NGHIÊM KHẮC CỦA TỪNG NGUỒN")
    print("=" * 70)
    print(f"{'nguồn':<14}" + "".join(f"{x:>10}" for x in NAMES) + f"{'mức TB':>10}")
    for nm, v in (("nhãn GV", gv), ("nhãn LLM", llm)):
        pr = [np.mean(v == c) for c in range(3)]
        print(f"{nm:<14}" + "".join(f"{x*100:>9.1f}%" for x in pr) + f"{v.mean():>10.2f}")
    # p_sim chia 3 nhóm đều để tham chiếu
    print(f"\n  Chênh lệch mức trung bình GV vs LLM: {gv.mean()-llm.mean():+.2f} "
          f"(âm = GV chấm DỄ DÃI hơn)")
    print("  => Đây là lệch NGƯỠNG. Nó làm hỏng κ nhưng KHÔNG ảnh hưởng")
    print("     tương quan hạng — nên không thể dùng nó để giải thích ρ thấp.")

    # ---------------- [2][3] thứ tự ----------------
    print("\n" + "=" * 70)
    print("[2-3] THỨ TỰ: GV vs LLM  (các phép đo miễn nhiễm ngưỡng)")
    print("=" * 70)
    sp = float(np.corrcoef(pd.Series(gv).rank(), pd.Series(llm).rank())[0, 1])
    tb = kendalltau(gv, llm, variant="b")
    pc = polychoric(gv, llm)
    kp = cohen_kappa(gv, llm)
    print(f"  Cohen's κ                          {kp:+.3f}   (bị phạt bởi lệch ngưỡng)")
    print(f"  Spearman ρ                         {sp:+.3f}   (suy giảm do đồng hạng)")
    print(f"  Kendall τ-b (hiệu chỉnh đồng hạng) {tb.statistic:+.3f}   p={tb.pvalue:.3f}")
    print(f"  ⭐ Polychoric (biến ẩn liên tục)    {pc:+.3f}   ← ước lượng đúng nhất")

    # ---------------- [4] với p_sim ----------------
    print("\n" + "=" * 70)
    print("[4] THỨ TỰ: TỪNG NGUỒN NHÃN vs p_sim")
    print("=" * 70)
    print("  (nhãn Dễ=0/Khó=2 nên tương quan với tỉ lệ ĐÚNG phải ÂM)")
    print(f"\n{'nguồn':<14}{'Spearman':>11}{'Kendall τ-b':>14}{'Polyserial':>13}")
    for nm, v in (("nhãn GV", gv), ("nhãn LLM", llm)):
        s = float(np.corrcoef(pd.Series(v).rank(), pd.Series(ps).rank())[0, 1])
        t = kendalltau(v, ps, variant="b")
        py = polyserial(v, ps)
        print(f"{nm:<14}{s:>+11.3f}{t.statistic:>+14.3f}{py:>+13.3f}")

    # ---------------- [5] khớp phân bố biên ----------------
    print("\n" + "=" * 70)
    print("[5] ĐỒNG THUẬN SAU KHI CHUẨN HOÁ THANG (ép GV về phân bố của LLM)")
    print("=" * 70)
    gv_c = match_marginals(gv, llm)
    a0, a1 = float(np.mean(gv == llm)), float(np.mean(gv_c == llm))
    k1 = cohen_kappa(gv_c, llm)
    print(f"  đồng thuận tuyệt đối TRƯỚC chuẩn hoá: {a0*100:>5.1f}%   κ={kp:+.3f}")
    print(f"  đồng thuận tuyệt đối SAU  chuẩn hoá: {a1*100:>5.1f}%   κ={k1:+.3f}")
    print(f"  phần bất đồng chỉ do LỆCH NGƯỠNG   : {(a1-a0)*100:+.1f} điểm")
    if a1 - a0 < 0.05:
        print("\n  => Chuẩn hoá thang KHÔNG cứu được đồng thuận.")
        print("     Bất đồng là THẬT (khác thứ tự), không phải do khác thang.")
    else:
        print("\n  => Một phần đáng kể bất đồng chỉ do khác thang, không phải")
        print("     do khác cảm nhận thứ tự. Nên báo cáo κ SAU chuẩn hoá.")

    out = SAMPLES / "label_calibration.json"
    out.write_text(json.dumps({
        "n": n, "kappa_raw": kp, "spearman_gv_llm": sp,
        "kendall_gv_llm": float(tb.statistic), "polychoric_gv_llm": pc,
        "agreement_raw": a0, "agreement_calibrated": a1, "kappa_calibrated": k1,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  đã lưu -> {out}")


if __name__ == "__main__":
    main()
