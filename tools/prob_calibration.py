# -*- coding: utf-8 -*-
"""Chất lượng XÁC SUẤT của mô hình nền — và độ nhạy của kết luận với nó.

VÌ SAO CẦN. Đại lượng trung tâm của toàn đề tài là MỨC KỲ VỌNG

    E[y] = p @ [0, 1, 2, 3]          (counterfactual_validity.expected_level)

Mọi Δ can thiệp, mọi phán quyết cổng, mọi chứng chỉ trục đều là HIỆU của hai
số này. Nên chúng phụ thuộc trực tiếp vào chất lượng của `p` — chứ không chỉ
vào chỗ `p` đạt cực đại. Nhưng toàn bộ đề tài mới chỉ đo phần "chỗ cực đại"
(QWK, accuracy, AUC), chưa từng đo phần "xác suất có đúng cỡ không".

Lưu ý về từ "hiệu chỉnh" trong repo này — ba nghĩa KHÁC NHAU:
  * `label_calibration.py`      — hiệu chỉnh ĐỘ NGHIÊM KHẮC của người chấm
  * cờ `calibrated` ở `xai_difficulty` — cổng đã đối chiếu mô hình NHÃN XÁO
  * file này                    — hiệu chỉnh XÁC SUẤT (nghĩa của Guo 2017)

BỐN PHÉP ĐO, tất định, offline, không cần người và không gọi LLM:

  [1] NLL        — log-loss out-of-fold.
  [2] ECE        — sai số hiệu chỉnh kỳ vọng, 15 thùng theo độ tự tin.
                   Đo mô hình "nói 80% thì có đúng 80% lần không".
  [3] RPS        — ranked probability score, quy tắc chấm CHÍNH ĐÁNG cho thang
                   CÓ THỨ TỰ: phạt theo khoảng cách NB→VDC chứ không chỉ theo
                   đúng/sai. Đây là bạn song hành đúng của QWK (QWK đo mức đồng
                   thuận, RPS đo chất lượng xác suất). Brier bỏ qua thứ tự nên
                   KHÔNG dùng ở đây.
  [4] Nhiệt độ T — một số vô hướng, khớp bằng cực tiểu NLL trên chính dự đoán
                   out-of-fold, theo p_T ∝ p^(1/T). Với mô hình softmax đây
                   đúng bằng chia logit cho T.

VÌ SAO AN TOÀN VỚI BẢNG MỐC. Nhiệt độ là phép biến đổi ĐƠN ĐIỆU theo từng câu:
nó KHÔNG đổi argmax, nên QWK và accuracy đứng yên — 72 con số đã khoá không bị
đụng. Chỉ các đại lượng dựa trên E[y] mới dịch. File này báo cáo đúng mức dịch
đó, dưới dạng PHÂN TÍCH ĐỘ NHẠY, không thay thế gì cả.

T khớp trên chính tập out-of-fold nên đây là mức hiệu chỉnh LỚN NHẤT mà dữ liệu
cho phép — tức một CẬN TRÊN của độ dịch. Kết luận sống sót ở đây thì sống sót ở
mọi cách khớp T dè dặt hơn.

Chạy:  python tools/prob_calibration.py                (một backend)
       python tools/prob_calibration.py --all          (cả bốn, mỗi cái một tiến trình)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

SEED = 42
N_BINS = 15
OUT = f"docs/prob_calibration{cv.BACKEND_SUFFIX}.json"


# ----------------------------------------------------------------------
# Phép đo
# ----------------------------------------------------------------------
def temper(p: np.ndarray, t: float) -> np.ndarray:
    """p_T ∝ p^(1/T). Với mô hình softmax, đúng bằng chia logit cho T."""
    q = np.clip(p, 1e-12, 1.0) ** (1.0 / t)
    return q / q.sum(axis=1, keepdims=True)


def nll(p: np.ndarray, y: np.ndarray) -> float:
    return float(-np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1.0)).mean())


def ece(p: np.ndarray, y: np.ndarray, n_bins: int = N_BINS) -> float:
    """Sai số hiệu chỉnh kỳ vọng: |độ chính xác − độ tự tin| bình quân theo thùng."""
    conf, pred = p.max(axis=1), p.argmax(axis=1)
    hit = (pred == y).astype(float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    out = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.sum():
            out += m.mean() * abs(hit[m].mean() - conf[m].mean())
    return float(out)


def rps(p: np.ndarray, y: np.ndarray) -> float:
    """Ranked probability score — quy tắc chấm chính đáng cho thang CÓ THỨ TỰ."""
    k = p.shape[1]
    onehot = np.zeros_like(p)
    onehot[np.arange(len(y)), y] = 1.0
    d = np.cumsum(p, axis=1)[:, :-1] - np.cumsum(onehot, axis=1)[:, :-1]
    return float((d ** 2).sum(axis=1).mean() / (k - 1))


def fit_temperature(p: np.ndarray, y: np.ndarray) -> float:
    """Khớp T bằng cực tiểu NLL — lưới thô rồi mịn dần, tất định."""
    lo, hi = 0.25, 6.0
    for _ in range(6):
        grid = np.linspace(lo, hi, 40)
        losses = [nll(temper(p, t), y) for t in grid]
        j = int(np.argmin(losses))
        step = grid[1] - grid[0]
        lo, hi = max(0.05, grid[j] - step), grid[j] + step
    return float((lo + hi) / 2)


def expected(p: np.ndarray) -> np.ndarray:
    return p @ np.arange(p.shape[1])


def norm_entropy(p: np.ndarray) -> np.ndarray:
    """Entropy chuẩn hoá về [0,1] — đúng công thức `xai_difficulty.entropy`."""
    q = np.clip(p, 1e-12, 1.0)
    return -(q * np.log(q)).sum(axis=1) / np.log(p.shape[1])


def sel_acc(p: np.ndarray, y: np.ndarray, cov: float) -> float:
    """Độ chính xác trên cov% câu TỰ TIN NHẤT theo entropy (ít entropy nhất)."""
    h = norm_entropy(p)
    k = max(3, int(round(cov * len(y))))
    keep = np.argsort(h)[:k]
    return float((p.argmax(axis=1)[keep] == y[keep]).mean())


def block(p: np.ndarray, y: np.ndarray) -> dict:
    return {"nll": nll(p, y), "ece": ece(p, y), "rps": rps(p, y),
            "acc": float((p.argmax(axis=1) == y).mean()),
            "qwk": float(cohen_kappa_score(p.argmax(axis=1), y,
                                           weights="quadratic")),
            "sd_expected_level": float(expected(p).std()),
            "mean_confidence": float(p.max(axis=1).mean())}


# ----------------------------------------------------------------------
# Dự đoán out-of-fold, ĐÚNG lát mà chuỗi phản thực dùng
# ----------------------------------------------------------------------
def oof_proba(subject: str):
    cfg = cv.SUBJECTS[subject]
    eng = OntologyEngine.for_subject(cv.ontology_of(subject))
    fz = cv.Featurizer(eng, cfg["surface"])
    items = cv.load_items(subject)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    cols = cv.model_cols(cfg["surface"])
    X = pd.DataFrame([fz(q["stem"], q["correct"], q["distractors"])
                      for q in items])[cols]
    model_of = cv.fit_out_of_fold(X, y, SEED, cols)

    groups: dict[int, list[int]] = {}
    for i in range(len(y)):
        groups.setdefault(id(model_of[i]), []).append(i)
    p = None
    for _, rs in groups.items():
        pr = model_of[rs[0]].predict_proba(X.iloc[rs])
        if p is None:
            p = np.zeros((len(y), pr.shape[1]))
        p[rs] = pr
    return p, y


def analyse(subject: str) -> dict:
    p, y = oof_proba(subject)
    t = fit_temperature(p, y)
    q = temper(p, t)
    before, after = block(p, y), block(q, y)
    ey_b, ey_a = expected(p), expected(q)
    return {
        "n": int(len(y)), "temperature": t,
        "truoc": before, "sau": after,
        # Thứ hạng có giữ nguyên không → mọi kết quả dựa trên Spearman
        # (kiểm tra chéo nửa A/B, SHAP so can thiệp, đường cong bốn nền)
        # miễn nhiễm khi và chỉ khi số này ≈ 1.
        "spearman_E_truoc_sau": float(spearmanr(ey_b, ey_a).statistic),
        # Mọi Δ can thiệp co/giãn xấp xỉ theo tỉ số này.
        "ti_so_do_trai_E": float(ey_a.std() / ey_b.std()),
        "qwk_doi_khong": bool(abs(before["qwk"] - after["qwk"]) < 1e-9),
        # ---- CƠ CHẾ TỪ CHỐI: ngưỡng cứng H ≥ 0,80 ở xai_difficulty.verdict_of
        # quyết định câu nào bị tuyên "KHÔNG KẾT LUẬN". Ngưỡng đó đặt trên
        # entropy THÔ. Nếu mô hình quá tự tin thì entropy thấp giả tạo, ngưỡng
        # KHÔNG kích hoạt đủ, và hệ tự cho mình quyền giải thích ở những câu
        # lẽ ra phải im lặng.
        "tu_choi": {
            "nguong": 0.80,
            "H_trung_binh_truoc": float(norm_entropy(p).mean()),
            "H_trung_binh_sau": float(norm_entropy(q).mean()),
            "ti_le_im_lang_truoc": float((norm_entropy(p) >= 0.80).mean()),
            "ti_le_im_lang_sau": float((norm_entropy(q) >= 0.80).mean()),
            # Thứ hạng entropy có đổi không → sel20 có đổi không
            "spearman_H_truoc_sau": float(
                spearmanr(norm_entropy(p), norm_entropy(q)).statistic),
            "sel20_truoc": sel_acc(p, y, 0.20),
            "sel20_sau": sel_acc(q, y, 0.20),
            "sel40_truoc": sel_acc(p, y, 0.40),
            "sel40_sau": sel_acc(q, y, 0.40),
        },
    }


def main() -> None:
    res = {"backend": cv.BACKEND, "seed": SEED, "n_bins_ece": N_BINS,
           "ghi_chu": "T khớp trên chính OOF ⇒ cận trên của độ dịch"}
    for s in ("physics", "history_gv"):
        print(f"── {s} · backend {cv.BACKEND}")
        res[s] = analyse(s)
        r = res[s]
        print(f"   T = {r['temperature']:.3f}   "
              f"(T>1: quá tự tin · T<1: quá dè dặt)")
        print(f"   ECE {r['truoc']['ece']:.4f} → {r['sau']['ece']:.4f}    "
              f"RPS {r['truoc']['rps']:.4f} → {r['sau']['rps']:.4f}")
        print(f"   QWK {r['truoc']['qwk']:.4f} → {r['sau']['qwk']:.4f}    "
              f"(đứng yên: {r['qwk_doi_khong']})")
        print(f"   sd E[y] ×{r['ti_so_do_trai_E']:.3f}   "
              f"ρ(E trước, E sau) = {r['spearman_E_truoc_sau']:.5f}")
        tc = r["tu_choi"]
        print(f"   TỪ CHỐI (H ≥ 0,80): tỉ lệ im lặng "
              f"{tc['ti_le_im_lang_truoc']:.1%} → {tc['ti_le_im_lang_sau']:.1%}"
              f"   (H trung bình {tc['H_trung_binh_truoc']:.3f} → "
              f"{tc['H_trung_binh_sau']:.3f})")
        print(f"   sel@20% {tc['sel20_truoc']:.3f} → {tc['sel20_sau']:.3f}   "
              f"sel@40% {tc['sel40_truoc']:.3f} → {tc['sel40_sau']:.3f}   "
              f"ρ(H) = {tc['spearman_H_truoc_sau']:.4f}")
    Path(OUT).write_text(json.dumps(res, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    print(f"\n→ {OUT}")


if __name__ == "__main__":
    if "--all" in sys.argv:
        for b in ("xgb15", "tfidf", "text", "emb"):
            print(f"\n{'=' * 66}\nBACKEND {b}\n{'=' * 66}")
            env = dict(os.environ, QDE_BACKEND=b, PYTHONIOENCODING="utf-8")
            subprocess.run([sys.executable, __file__], env=env, check=True)
    else:
        main()
