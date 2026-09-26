# -*- coding: utf-8 -*-
"""PHÂN TÍCH ĐỘ NHẠY: chạy lại trọn chuỗi phản thực trên XÁC SUẤT ĐÃ HIỆU CHỈNH.

Câu hỏi duy nhất file này trả lời:

    Nếu mức kỳ vọng E[y] được tính từ xác suất ĐÃ hiệu chỉnh nhiệt độ thay vì
    xác suất thô, thì CỔNG có đổi phán quyết không, và hiệu ứng dịch bao nhiêu?

CÁCH LÀM. Bọc đúng hai hàm tính E[y] trong `counterfactual_validity`
(`predict_expected` và `expected_level`) để chúng đưa xác suất qua

    p_T ∝ p^(1/T)

trước khi nhân với [0,1,2,3]. T lấy từ `docs/prob_calibration{suffix}.json`,
khớp riêng cho từng môn và từng mô hình nền. Mọi thứ khác — lát chia, bộ donor,
seed, hàm cổng — giữ y nguyên, nên chênh lệch quan sát được CHỈ do hiệu chỉnh.

KHÔNG ghi đè gì. Kết quả ra `*_calibT.json` bên cạnh file gốc; bảng mốc và 72
con số không bị đụng.

Chạy:  python tools/calib_sensitivity.py --subject physics
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402


def temper(p: np.ndarray, t: float) -> np.ndarray:
    q = np.clip(p, 1e-12, 1.0) ** (1.0 / t)
    return q / q.sum(axis=1, keepdims=True)


def install(t: float) -> None:
    """Thay hai hàm tính E[y] bằng bản có hiệu chỉnh nhiệt độ."""
    def predict_expected(model_of, rows, items_idx, cols):
        import pandas as pd
        df = pd.DataFrame(rows)[list(cols)]
        out = np.zeros(len(rows))
        groups: dict[int, list[int]] = {}
        for r, i in enumerate(items_idx):
            groups.setdefault(id(model_of[i]), []).append(r)
        for _, rs in groups.items():
            proba = model_of[items_idx[rs[0]]].predict_proba(df.iloc[rs])
            out[rs] = temper(proba, t) @ np.arange(proba.shape[1])
        return out

    def expected_level(model, feat_row, cols) -> float:
        import pandas as pd
        proba = model.predict_proba(pd.DataFrame([feat_row])[list(cols)])
        return float(temper(proba, t)[0] @ np.arange(proba.shape[1]))

    cv.predict_expected = predict_expected
    cv.expected_level = expected_level


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="physics", choices=sorted(cv.SUBJECTS))
    args, rest = ap.parse_known_args()

    src = Path(f"docs/prob_calibration{cv.BACKEND_SUFFIX}.json")
    if not src.exists():
        sys.exit(f"thiếu {src} — chạy tools/prob_calibration.py trước")
    t = json.loads(src.read_text(encoding="utf-8"))[args.subject]["temperature"]
    print(f"── {args.subject} · backend {cv.BACKEND} · T = {t:.3f}")
    install(t)

    out = cv.out_path(args.subject, "counterfactual_validity").replace(
        ".json", "_calibT.json")
    sys.argv = [sys.argv[0], "--subject", args.subject, "--out", out, *rest]
    cv.main()


if __name__ == "__main__":
    main()
