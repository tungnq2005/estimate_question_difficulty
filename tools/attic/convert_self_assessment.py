# -*- coding: utf-8 -*-
"""Chuyển (các) file JSON export từ self_assessment_form.html thành 2 output:
  - phần TRẢ LỜI  -> gộp vào student_responses.csv (schema: student_id, form,
    item_id, correct) — form="SELF_<rater>", dùng được thẳng cho
    tools/item_analysis.py / tools/coldwarm.py.
  - phần CHẤM ĐỘ KHÓ -> subjects/history/samples/self_difficulty_ratings.csv
    (rater, item_id, verdict) — so được với nhãn LLM và (khi có) nhãn giáo
    viên trên CÙNG các câu.

Usage:
    python tools/convert_self_assessment.py --files su9_self_minh_2026-08-07.json ...
    python tools/convert_self_assessment.py --demo   # tự kiểm thử, không cần file thật
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
LABEL2ID = {"Easy": 0, "Medium": 1, "Hard": 2}
VERDICT2LABEL = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}


def load_manifest() -> dict:
    p = REPO / "subjects" / "history" / "samples" / "self_assessment_manifest.json"
    if not p.exists():
        sys.exit(f"Chưa có {p}. Chạy tools/make_self_assessment_form.py trước.")
    return json.loads(p.read_text(encoding="utf-8"))


def make_demo_export(manifest: dict, rater: str, seed: int) -> dict:
    """Tự tạo 1 export JSON giả lập ĐÚNG hình dạng thật, để kiểm thử logic
    ghép nối mà không cần ai thực sự làm bài."""
    import numpy as np
    rng = np.random.default_rng(seed)
    responses = {}
    for item_id, m in manifest.items():
        # 75% chọn đúng, còn lại random trong 4 phương án
        if rng.random() < 0.75:
            letter = m["correct_letter"]
        else:
            letter = rng.choice([l for l in m["order"]])
        verdict = rng.choice(["easy", "medium", "hard"], p=[0.3, 0.4, 0.3])
        responses[item_id] = {"answer": letter, "verdict": verdict,
                              "ts": "2026-08-07T00:00:00Z"}
    return {"subject": "su9", "rater": rater, "exported_at": "2026-08-07T00:00:00Z",
           "responses": responses}


def process_export(payload: dict, manifest: dict) -> tuple:
    rater = payload.get("rater", "anonymous")
    ans_rows, diff_rows = [], []
    for item_id, r in payload.get("responses", {}).items():
        m = manifest.get(item_id)
        if not m:
            continue
        if r.get("answer"):
            correct = int(r["answer"] == m["correct_letter"])
            ans_rows.append({"student_id": f"self_{rater}", "form": f"SELF_{rater}",
                            "item_id": item_id, "correct": correct})
        if r.get("verdict"):
            diff_rows.append({"rater": rater, "item_id": item_id,
                             "verdict": VERDICT2LABEL.get(r["verdict"], r["verdict"])})
    return pd.DataFrame(ans_rows), pd.DataFrame(diff_rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", help="đường dẫn (các) file JSON đã export")
    ap.add_argument("--demo", action="store_true",
                    help="tự sinh 2 file export giả lập để kiểm thử pipeline")
    ap.add_argument("--responses-out", default="subjects/history/samples/student_responses.SELF.csv")
    ap.add_argument("--difficulty-out", default="subjects/history/samples/self_difficulty_ratings.csv")
    args = ap.parse_args()

    manifest = load_manifest()
    payloads = []
    if args.demo:
        print("⚠ CHẾ ĐỘ DEMO: file export là MÔ PHỎNG (tự sinh) — chỉ kiểm thử logic "
             "ghép nối, không phải dữ liệu người thật.\n")
        payloads = [make_demo_export(manifest, "demo_a", 1),
                   make_demo_export(manifest, "demo_b", 2)]
        args.responses_out = "subjects/history/samples/student_responses.SELF.DEMO.csv"
        args.difficulty_out = "subjects/history/samples/self_difficulty_ratings.DEMO.csv"
    else:
        if not args.files:
            sys.exit("Cần --files <file1.json> [file2.json ...], hoặc dùng --demo.")
        for f in args.files:
            payloads.append(json.loads(Path(f).read_text(encoding="utf-8")))

    all_ans, all_diff = [], []
    for payload in payloads:
        ans, diff = process_export(payload, manifest)
        print(f"  {payload.get('rater','?')}: {len(ans)} câu trả lời "
             f"(p={ans['correct'].mean():.3f})  |  {len(diff)} câu chấm độ khó"
             if len(ans) else f"  {payload.get('rater','?')}: 0 câu trả lời")
        all_ans.append(ans)
        all_diff.append(diff)

    df_ans = pd.concat(all_ans, ignore_index=True) if all_ans else pd.DataFrame()
    df_diff = pd.concat(all_diff, ignore_index=True) if all_diff else pd.DataFrame()

    out_ans = REPO / args.responses_out
    out_diff = REPO / args.difficulty_out
    df_ans.to_csv(out_ans, index=False, encoding="utf-8")
    df_diff.to_csv(out_diff, index=False, encoding="utf-8")
    print(f"\n  tổng {len(df_ans)} lượt trả lời từ {df_ans['student_id'].nunique() if len(df_ans) else 0} người")
    print(f"  đã lưu -> {out_ans}")
    print(f"  tổng {len(df_diff)} lượt chấm độ khó")
    print(f"  đã lưu -> {out_diff}")

    if len(df_diff):
        print("\n  Gộp với student_responses.csv thật (nếu có) rồi chạy "
             "tools/item_analysis.py để so p-value; so self_difficulty_ratings.csv "
             "với nhãn LLM (mcq_crawled.json) để tính Cohen's kappa.")
    if args.demo:
        print("\n  (dữ liệu DEMO — xoá 2 file .DEMO.csv trước khi dùng dữ liệu thật)")


if __name__ == "__main__":
    main()
