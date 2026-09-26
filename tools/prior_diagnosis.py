# -*- coding: utf-8 -*-
"""Chẩn đoán vì sao k* = 0 trong tools/coldwarm.py: prior-KG THỰC SỰ không có
tín hiệu, hay chỉ bị SAI HIỆU CHUẨN?

VÌ SAO CẦN: coldwarm.py so các prior bằng MAE, mà MAE trộn lẫn hai loại sai
khác hẳn nhau về hệ quả:

  (1) SAI THỨ HẠNG — prior không biết câu nào khó hơn câu nào. Đây mới là
      "tri thức có cấu trúc vô dụng", kết luận nặng.
  (2) SAI MỨC (hiệu chuẩn) — prior xếp hạng đúng nhưng đặt toàn bộ thang lệch
      đi. Đây chỉ là lỗi ánh xạ lớp->p, SỬA ĐƯỢC, không nói gì về giá trị của
      tri thức.

coldwarm.py ánh xạ lớp bằng hằng số cứng CLASS_TO_P = {Easy:0.85, Medium:0.55,
Hard:0.25} (trung bình ~0.55), trong khi p-value MÔ PHỎNG có trung bình ~0.72
(mô phỏng bị hiệu ứng sàn: persona yếu nhất vẫn đúng ~0.52 thay vì ~0.35 như
học sinh yếu thật). Lệch mức ~0.17 này một mình đã đủ làm prior thua "trung
bình toàn cục" — vốn đúng mức theo định nghĩa. Nếu không tách ra thì sẽ báo
cáo nhầm một lỗi hiệu chuẩn thành kết luận "ontology không đáng giá".

CÁCH TÁCH: báo cáo song song
  - Spearman/Pearson(prior, p_thật)  -> MIỄN NHIỄM với hiệu chuẩn, đo tín hiệu
    thứ hạng thuần tuý.
  - MAE nguyên trạng vs MAE sau khi hiệu chuẩn lại tuyến tính (đưa prior về
    đúng trung bình/độ lệch chuẩn của p thật).
  ⚠ Bản hiệu chuẩn lại dùng thông tin KHÔNG có lúc cold-start thật (phân phối
    p của chính tập test) -> chỉ là CẬN TRÊN lạc quan, phải ghi rõ khi báo cáo,
    KHÔNG được trình bày như kết quả cold-start.

Usage:
    python tools/prior_diagnosis.py \
        --responses subjects/history/samples/student_responses.LLMSIM_API.csv \
        --csv .cache/history_canonical.features.csv
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.coldwarm import train_priors_from_features, CLASS_TO_P  # noqa: E402


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.corrcoef(pd.Series(a).rank(), pd.Series(b).rank())[0, 1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--responses", required=True)
    ap.add_argument("--csv", required=True)
    args = ap.parse_args()

    resp = pd.read_csv(REPO / args.responses)
    p_true = resp.groupby("item_id")["correct"].mean()
    n_resp = resp.groupby("item_id")["correct"].size()

    priors = train_priors_from_features(REPO / args.csv, list(p_true.index))
    ids = priors.index.intersection(p_true.index)
    y = p_true.loc[ids].to_numpy()
    n = n_resp.loc[ids].to_numpy()

    print(f"\nn = {len(ids)} câu | lượt trả lời/câu: trung vị {np.median(n):.0f}")
    print(f"p thật (mô phỏng): trung bình {y.mean():.3f}  độ lệch chuẩn {y.std():.3f}")
    print(f"CLASS_TO_P đang dùng: {CLASS_TO_P}  -> mức trung bình ngụ ý "
          f"{np.mean(list(CLASS_TO_P.values())):.3f}")

    # Sàn nhiễu: p_true tự nó chỉ ước lượng từ n lượt -> có sai số nhị thức.
    # Mọi MAE nhỏ hơn mức này là vô nghĩa (đang đo nhiễu, không đo mô hình).
    noise_floor = float(np.mean(np.sqrt(y * (1 - y) / n)) * np.sqrt(2 / np.pi))
    print(f"\n⚠ SÀN NHIỄU của chính p thật: MAE ≈ {noise_floor:.4f} "
          f"(sai số nhị thức với n={np.median(n):.0f} lượt/câu).")
    print("  Mọi chênh lệch MAE nhỏ hơn mức này KHÔNG diễn giải được.")

    print(f"\n{'prior':<22}{'Pearson':>9}{'Spearman':>10}{'MAE gốc':>10}"
          f"{'MAE hiệu chuẩn lại':>20}")
    print("-" * 71)

    results = {}
    for name in ("prior_kg", "prior_text"):
        x = priors.loc[ids, name].to_numpy()
        pear = float(np.corrcoef(x, y)[0, 1])
        spea = spearman(x, y)
        mae_raw = float(np.mean(np.abs(x - y)))
        # hiệu chuẩn lại tuyến tính: đưa về đúng trung bình & độ lệch chuẩn của y
        x_cal = (x - x.mean()) / (x.std() + 1e-12) * y.std() + y.mean()
        mae_cal = float(np.mean(np.abs(x_cal - y)))
        results[name] = dict(pearson=pear, spearman=spea,
                             mae_raw=mae_raw, mae_cal=mae_cal)
        print(f"{name:<22}{pear:>+9.3f}{spea:>+10.3f}{mae_raw:>10.4f}{mae_cal:>20.4f}")

    # đối chứng: prior vô thông tin = trung bình toàn cục (leave-one-out)
    loo = (y.sum() - y) / (len(y) - 1)
    mae_loo = float(np.mean(np.abs(loo - y)))
    print(f"{'(trung bình toàn cục)':<22}{'—':>9}{'—':>10}{mae_loo:>10.4f}{mae_loo:>20.4f}")
    results["uninformative"] = dict(mae_raw=mae_loo, mae_cal=mae_loo)

    print("\n" + "=" * 71)
    print("KẾT LUẬN")
    print("=" * 71)
    kg = results["prior_kg"]
    if abs(kg["spearman"]) < 0.10:
        print(f"  prior-KG: Spearman = {kg['spearman']:+.3f} ≈ 0 -> KHÔNG có tín hiệu")
        print("  thứ hạng. Đây là kết luận THẬT, không phải lỗi hiệu chuẩn:")
        print("  đặc trưng tri thức không phân biệt được câu khó/dễ trên tập này.")
    else:
        gain = kg["mae_raw"] - kg["mae_cal"]
        print(f"  prior-KG CÓ tín hiệu thứ hạng (Spearman = {kg['spearman']:+.3f}),")
        print(f"  và hiệu chuẩn lại giảm MAE {gain:.4f} ({kg['mae_raw']:.4f} -> "
              f"{kg['mae_cal']:.4f}).")
        if kg["mae_cal"] < mae_loo:
            print(f"  Sau hiệu chuẩn, prior-KG THẮNG trung bình toàn cục "
                  f"({kg['mae_cal']:.4f} < {mae_loo:.4f})")
            print("  => k* = 0 ở coldwarm.py phần lớn là HIỆN VẬT HIỆU CHUẨN,")
            print("     KHÔNG phải bằng chứng tri thức vô dụng. Phải sửa CLASS_TO_P")
            print("     (hoặc học ánh xạ lớp->p) rồi chạy lại trước khi kết luận.")
        else:
            print(f"  Nhưng ngay cả sau hiệu chuẩn, prior-KG vẫn thua trung bình "
                  f"toàn cục ({kg['mae_cal']:.4f} ≥ {mae_loo:.4f})")
            print("  => tín hiệu thứ hạng có nhưng quá yếu để có giá trị thực dụng.")

    out = REPO / "subjects" / "history" / "samples" / "prior_diagnosis.json"
    out.write_text(json.dumps({
        "n_items": int(len(ids)),
        "p_true_mean": float(y.mean()), "p_true_std": float(y.std()),
        "class_to_p": CLASS_TO_P,
        "noise_floor_mae": noise_floor,
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  đã lưu -> {out}")


if __name__ == "__main__":
    main()
