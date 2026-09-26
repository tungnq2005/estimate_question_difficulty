# -*- coding: utf-8 -*-
"""Độ mạnh phạt C quyết định độ TỰ TIN — chứ không phải cách biểu diễn.

GIẢ THUYẾT cần kiểm. Ở chế độ `text` và `emb`, xác suất KHÔNG do PhoBERT sinh
ra: PhoBERT bị đóng băng và chỉ trả một vector 768 chiều, không có đầu phân
loại, không có softmax nào trên thang NB/TH/VD/VDC. Toàn bộ xác suất do lớp hồi
quy logistic phía trên tạo ra (`TextModel.predict_proba` → `self.lr`).

Nếu vậy thì độ tự tin phải là hàm của LỚP TRÊN và mức phạt của nó, chứ không
phải của cách biểu diễn. Bằng chứng gián tiếp đã có: `text` (PhoBERT + 15 cột)
và `emb` (PhoBERT trần) dùng chung C = 0,01 và cho nhiệt độ gần như y hệt —
1,458 so với 1,455 ở Lý. Hai cách biểu diễn khác nhau, cùng một độ tự tin.

Phép kiểm trực tiếp: quét C trên chế độ `tfidf`, giữ nguyên mọi thứ khác, xem
nhiệt độ có đi theo C không.

VÌ SAO ĐÁNG KIỂM. C = 16 của `tfidf` được chọn bằng cách CỰC ĐẠI QWK
(`pick_c_tfidf.py`). QWK chỉ nhìn chỗ xác suất đạt cực đại, hoàn toàn mù với
việc xác suất có đúng cỡ hay không. Nếu C lớn làm mô hình tự tin hơn, thì quy
trình chọn siêu tham số của chính đề tài đã âm thầm đánh đổi độ hiệu chỉnh lấy
độ đồng thuận — mà không ai biết, vì không ai đo.

Chạy:  QDE_BACKEND=tfidf python tools/c_vs_calibration.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
import prob_calibration as pc  # noqa: E402
import text_backend as tb  # noqa: E402

GRID = [1.0, 4.0, 16.0, 64.0, 256.0]   # đúng lưới của pick_c_tfidf.py
OUT = "docs/c_vs_calibration.json"


def main() -> None:
    if cv.BACKEND != "tfidf":
        sys.exit("chạy với QDE_BACKEND=tfidf")
    res = {"grid": GRID, "backend": cv.BACKEND,
           "ghi_chu": "C=16 là giá trị pick_c_tfidf.py chọn theo cực đại QWK"}
    for subj in ("physics", "history_gv"):
        print(f"\n===== {subj} =====")
        print(f"{'C':>8}{'QWK':>10}{'ECE thô':>11}{'nhiệt độ T':>13}"
              f"{'ECE sau':>10}{'tự tin TB':>12}")
        res[subj] = {}
        for c in GRID:
            tb.C_TFIDF = c
            p, y = pc.oof_proba(subj)
            t = pc.fit_temperature(p, y)
            b, a = pc.block(p, y), pc.block(pc.temper(p, t), y)
            res[subj][str(c)] = {"qwk": b["qwk"], "ece_tho": b["ece"],
                                 "T": t, "ece_sau": a["ece"],
                                 "tu_tin_tb": b["mean_confidence"]}
            mark = "  ← đang dùng" if c == 16.0 else ""
            print(f"{c:>8.0f}{b['qwk']:>10.4f}{b['ece']:>11.4f}{t:>13.3f}"
                  f"{a['ece']:>10.4f}{b['mean_confidence']:>12.3f}{mark}")
    Path(OUT).write_text(json.dumps(res, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    print(f"\n→ {OUT}")


if __name__ == "__main__":
    main()
