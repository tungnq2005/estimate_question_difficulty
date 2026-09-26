# -*- coding: utf-8 -*-
"""Chuyển CSV xuất từ Google Sheet (kết quả 3 Form học sinh) thành
subjects/history/samples/student_responses.csv — input cho tools/item_analysis.py
và tools/coldwarm.py.

CÁCH LẤY CSV: mở từng Sheet kết quả (link in ra khi chạy student_exam_forms.gs)
-> File > Download > Comma-separated values (.csv) -> lưu 3 file, mỗi file
ứng với 1 đề (A/B/C).

Cột trong Sheet Google Form theo thứ tự: Timestamp, Mã học sinh, <40 câu hỏi
theo ĐÚNG thứ tự đã tạo form (không bật shuffle câu hỏi — xem
tools/make_student_forms.py) — script này chấm đúng/sai bằng cách so khớp
văn bản đã chọn với correct_text trong student_exam_manifest.json theo VỊ TRÍ
CỘT, không theo tên cột (tên cột = nguyên văn stem, có thể bị Google Sheets
cắt bớt/đổi nếu quá dài — vị trí cột ổn định hơn).

Usage:
    python tools/convert_google_responses.py \\
        --A "De A - Ket qua.csv" --B "De B - Ket qua.csv" --C "De C - Ket qua.csv"
    python tools/convert_google_responses.py --demo   # tự kiểm thử bằng CSV giả lập
"""
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]


def load_manifest() -> dict:
    p = REPO / "subjects" / "history" / "samples" / "student_exam_manifest.json"
    if not p.exists():
        sys.exit(f"Chưa có {p}. Chạy tools/make_student_forms.py trước.")
    return json.loads(p.read_text(encoding="utf-8"))


def convert_one_form(csv_path: Path, form: str, manifest_items: list) -> pd.DataFrame:
    """Cột 0 = Timestamp, cột 1 = Mã học sinh, cột 2..41 = 40 câu (đúng thứ
    tự manifest_items). Trả DataFrame dài: student_id, form, item_id, correct."""
    raw = pd.read_csv(csv_path)
    n_q = len(manifest_items)
    q_cols = raw.columns[2:2 + n_q]
    if len(q_cols) != n_q:
        sys.exit(f"{csv_path.name}: có {len(q_cols)} cột câu hỏi, cần đúng {n_q} "
                 f"— kiểm tra lại có đúng file Sheet của đề {form} không, hoặc "
                 f"form đã bị sửa thêm/bớt câu sau khi tạo.")
    student_col = raw.columns[1]

    rows = []
    for _, r in raw.iterrows():
        sid = r[student_col]
        for item, col in zip(manifest_items, q_cols):
            chosen = r[col]
            correct = int(str(chosen).strip() == str(item["correct_text"]).strip())
            rows.append({"student_id": sid, "form": form,
                        "item_id": item["item_id"], "correct": correct})
    return pd.DataFrame(rows)


def make_demo_csv(manifest_items: list, form: str, n_students: int, seed: int) -> Path:
    """Sinh 1 file CSV giả lập ĐÚNG hình dạng Google Sheet xuất ra, để tự
    kiểm thử logic ghép cột/chấm điểm mà không cần Form thật."""
    rng = np.random.default_rng(seed)
    cols = ["Timestamp", "Ma hoc sinh"] + [it["stem"] for it in manifest_items]
    rows = []
    for s in range(n_students):
        sid = f"demo_{form}_{s:03d}"
        row = [f"2026/08/07 8:0{s}:00", sid]
        for it in manifest_items:
            # 70% chọn đúng, còn lại chọn ngẫu nhiên 1 trong các phương án khác
            if rng.random() < 0.7:
                row.append(it["correct_text"])
            else:
                wrong = [o for o in it["options"] if o != it["correct_text"]]
                row.append(rng.choice(wrong))
        rows.append(row)
    df = pd.DataFrame(rows, columns=cols)
    out = REPO / "subjects" / "history" / "samples" / f"_demo_google_export_{form}.csv"
    df.to_csv(out, index=False)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--A", help="CSV xuất từ Sheet kết quả đề A")
    ap.add_argument("--B", help="CSV xuất từ Sheet kết quả đề B")
    ap.add_argument("--C", help="CSV xuất từ Sheet kết quả đề C")
    ap.add_argument("--demo", action="store_true",
                    help="tự sinh + tự chấm 3 CSV giả lập để kiểm thử pipeline ghép nối")
    ap.add_argument("--out", default="subjects/history/samples/student_responses.csv")
    args = ap.parse_args()

    manifest = load_manifest()
    paths = {}
    if args.demo:
        print("⚠ CHẾ ĐỘ DEMO: CSV đầu vào là MÔ PHỎNG (tự sinh) — chỉ kiểm thử "
             "logic ghép cột/chấm điểm, không phải dữ liệu học sinh thật.\n")
        for form in ("A", "B", "C"):
            paths[form] = make_demo_csv(manifest[form], form, n_students=20, seed=hash(form) % 1000)
        args.out = "subjects/history/samples/student_responses.DEMO.csv"
    else:
        for form in ("A", "B", "C"):
            v = getattr(args, form)
            if v:
                paths[form] = Path(v)
        if not paths:
            sys.exit("Cần ít nhất 1 trong --A/--B/--C (đường dẫn CSV), hoặc dùng --demo.")

    all_dfs = []
    for form, path in paths.items():
        df = convert_one_form(path, form, manifest[form])
        print(f"  Đề {form}: {df['student_id'].nunique()} học sinh x "
             f"{df['item_id'].nunique()} câu = {len(df)} lượt trả lời "
             f"(p trung bình = {df['correct'].mean():.3f})")
        all_dfs.append(df)

    out_df = pd.concat(all_dfs, ignore_index=True)
    out_path = REPO / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"\n  tổng {len(out_df)} lượt trả lời, {out_df['student_id'].nunique()} học sinh")
    print(f"  đã lưu -> {out_path}")
    if args.demo:
        for form in paths:
            paths[form].unlink(missing_ok=True)
        print("  (đã xoá CSV giả lập tạm thời)")


if __name__ == "__main__":
    main()
