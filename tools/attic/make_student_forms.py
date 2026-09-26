# -*- coding: utf-8 -*-
"""Sinh 3 Google Form cho học sinh làm bài (T4) — biến pool 120 câu (T2)
thành đề thi thật, mỗi đề 40 câu (10 câu neo + 30 câu riêng).

KHÁC với tools/make_teacher_form.py (giáo viên chấm độ khó): ở đây học sinh
CHỌN đáp án, không đánh giá độ khó — cần chấm đúng/sai sau khi thu bài.

Google Apps Script không có API xáo trộn PHƯƠNG ÁN của từng câu (chỉ có
form.setShuffleQuestions() xáo THỨ TỰ CÂU HỎI, không dùng ở đây để cột trong
Sheet kết quả khớp cố định với thứ tự câu trong `student_exam_manifest.json`)
— nên xáo phương án được làm THỦ CÔNG ở Python bằng đúng công thức seed như
tools/make_teacher_form.py (cùng SEED + hash(qid)) để 2 form (giáo viên chấm
độ khó và học sinh làm bài) hiển thị CÙNG một thứ tự phương án cho mỗi câu.

Output:
  - subjects/history/samples/student_exam_forms.gs        (Google Apps Script,
    3 hàm createForm_A/B/C — chạy TỪNG hàm một trong script.google.com)
  - subjects/history/samples/student_exam_manifest.json    (nội bộ — thứ tự
    câu + đáp án đúng từng đề, dùng để chấm bài sau khi thu, KHÔNG gửi HS)

Usage:
    python tools/make_student_forms.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]

SEED = 42  # PHẢI khớp SEED trong tools/make_teacher_form.py để 2 form đồng bộ xáo trộn


def load_questions() -> dict:
    q = {}
    for fname in ("mcq_samples.json", "mcq_crawled.json"):
        p = REPO / "subjects" / "history" / "samples" / fname
        if p.exists():
            for r in json.loads(p.read_text(encoding="utf-8")):
                q[r["id"]] = r
    return q


def shuffle_options(q: dict, rng: np.random.Generator) -> list:
    """Trả list [(letter, text, is_correct)] — CÙNG công thức với
    tools/make_teacher_form.py để 2 form khớp thứ tự phương án."""
    opts = [(q["correct"], True)] + [(d, False) for d in q["distractors"]]
    order = rng.permutation(len(opts))
    letters = "ABCD"
    return [(letters[i], opts[order[i]][0], opts[order[i]][1])
           for i in range(len(opts))]


def gs_form_function(form_name: str, subject_label: str, items: list) -> str:
    """Sinh 1 hàm Apps Script tạo Form cho 1 đề. `items`: list of dict
    {id, stem, options:[(letter,text,is_correct)]}, GIỮ NGUYÊN THỨ TỰ — thứ
    tự này phải khớp với thứ tự cột trong student_exam_manifest.json khi chấm."""
    lines = [f'''
function createForm_{form_name}() {{
  var form = FormApp.create("De {form_name} - Khao sat Lich su 9 (Cold-Warm)");
  form.setTitle("De {form_name} - Khao sat doc lap p-value - {subject_label}");
  form.setDescription(
    "Bai lam gom {len(items)} cau trac nghiem, khong tinh diem, chi phuc vu " +
    "nghien cuu ve uoc luong do kho cau hoi. Vui long lam MOT MINH, khong trao doi.\\n\\n" +
    "Nhap dung MA HOC SINH duoc phat de doi chieu ket qua an danh.\\n" +
    "Thoi gian de nghi: 45 phut."
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setShowLinkToRespondAgain(false);
  // KHONG bat setShuffleQuestions() — thu tu cau PHAI co dinh de khop cot
  // trong Sheet ket qua voi student_exam_manifest.json khi cham bai.

  form.addTextItem()
    .setTitle("Ma hoc sinh")
    .setHelpText("Nhap dung ma so duoc phat, dung de doi chieu an danh.")
    .setRequired(true);
''']
    for it in items:
        opts_texts = [t for _, t, _ in it["options"]]
        lines.append(f'  form.addMultipleChoiceItem()\n'
                    f'    .setTitle({json.dumps(it["stem"], ensure_ascii=False)})\n'
                    f'    .setChoiceValues({json.dumps(opts_texts, ensure_ascii=False)})\n'
                    f'    .setRequired(true);')
    lines.append(f'''
  var ss = SpreadsheetApp.create("De {form_name} - Ket qua");
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  Logger.log("De {form_name} da tao xong!");
  Logger.log("PUBLISHED URL: " + form.getPublishedUrl());
  Logger.log("EDIT URL: " + form.getEditUrl());
  Logger.log("RESPONSE SHEET: " + ss.getUrl());
}}
''')
    return "\n".join(lines)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-selection", metavar="JSON",
                    help="dùng tập câu chọn KHÔNG-NHÃN từ "
                         "tools/select_items_unlabeled.py (sinh 1 đề duy nhất) "
                         "thay cho thiết kế 3 đề cũ dựa trên nhãn LLM")
    args = ap.parse_args()

    questions = load_questions()

    if args.from_selection:
        p = Path(args.from_selection)
        if not p.is_absolute():
            p = REPO / p
        sel = json.loads(p.read_text(encoding="utf-8"))
        if sel.get("selection_rule", {}).get("labels_used") is not False:
            sys.exit("✗ File lựa chọn không xác nhận 'labels_used: false' — "
                     "từ chối dùng để tránh đưa thiên kiến nhãn vào đề.")
        forms = {"A": [{"id": i} for i in sel["item_ids"]]}
        print(f"Nguồn: {p.name} — 1 đề duy nhất, {len(sel['item_ids'])} câu, "
              "KHÔNG dùng nhãn độ khó.")
    else:
        tf_path = REPO / "subjects" / "history" / "samples" / "test_forms.json"
        if not tf_path.exists():
            sys.exit(f"Chưa có {tf_path}. Chạy tools/make_test_forms.py trước (T2).")
        forms = json.loads(tf_path.read_text(encoding="utf-8"))["forms"]
        print("⚠ Đang dùng thiết kế 3 đề CŨ (phân tầng theo nhãn llm_vote3). "
              "Nhãn này đã được đo là bám đặc trưng bề mặt — cân nhắc dùng "
              "--from-selection thay thế. Xem docs/PIVOT_T1_KHONG_DUYET.md.")

    manifest = {}
    n_forms = len(forms)
    gs_parts = ['''/**
 * Google Apps Script: Tao Google Form khao sat do kho cau hoi - Su 9
 *
 * CACH DUNG:
 *   1. Mo https://script.google.com/ -> New project -> dan TOAN BO file nay
 *   2. Save (Ctrl+S)
 *   3. Chon function createForm_A (va _B/_C neu co) tu dropdown
 *   4. Bam RUN (▶) -> lan dau se yeu cau grant permission, cu dong y
 *   5. Xem Execution log de lay PUBLISHED URL gui cho hoc sinh
 *   6. QUAN TRONG: KHONG doi thu tu cau hoi sau khi tao — thu tu phai khop
 *      voi student_exam_manifest.json (sinh cung luc, dung de cham bai)
 */
''']
    for form_name, items_brief in forms.items():
        built_items, manifest_items = [], []
        for it in items_brief:
            qid = it["id"]
            q = questions[qid]
            rng = np.random.default_rng(SEED + hash(qid) % 1_000_000)
            opts = shuffle_options(q, rng)
            correct_text = next(t for _, t, c in opts if c)
            built_items.append({"id": qid, "stem": q["stem"], "options": opts})
            manifest_items.append({"item_id": qid, "stem": q["stem"],
                                   "correct_text": correct_text,
                                   "options": [t for _, t, _ in opts]})
        manifest[form_name] = manifest_items
        gs_parts.append(gs_form_function(form_name, "Lich su 9", built_items))
        print(f"  Đề {form_name}: {len(built_items)} câu")

    out_gs = REPO / "subjects" / "history" / "samples" / "student_exam_forms.gs"
    out_manifest = REPO / "subjects" / "history" / "samples" / "student_exam_manifest.json"
    out_gs.write_text("\n".join(gs_parts), encoding="utf-8")
    out_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  đã lưu -> {out_gs}")
    print(f"  đã lưu -> {out_manifest} (nội bộ, dùng để chấm bài — không gửi học sinh)")
    print("\n  Sau khi thu bài: dùng tools/convert_google_responses.py để chấm và "
         "sinh student_responses.csv (input cho item_analysis.py / coldwarm.py).")


if __name__ == "__main__":
    main()
