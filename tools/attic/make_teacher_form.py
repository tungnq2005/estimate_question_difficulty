# -*- coding: utf-8 -*-
"""Sinh form giáo viên chấm Dễ/Trung bình/Khó cho ~120 câu khảo sát (T7).

Nguồn nhãn thứ 3, độc lập với nhãn LLM (llm_vote3) và p-value thực nghiệm
(T3/T4) — dùng để so 3 nguồn trên CÙNG một tập câu hỏi (E1 trong kế hoạch
Cold->Warm). QUAN TRỌNG: form KHÔNG hiển thị nhãn LLM cho giáo viên, để giữ
tính độc lập của nguồn nhãn này.

Đọc pool câu hỏi từ subjects/history/samples/test_forms.json (sinh bởi
tools/make_test_forms.py — T2), tra lại nội dung đầy đủ (stem + 4 phương án)
từ mcq_samples.json/mcq_crawled.json, XÁO thứ tự phương án theo seed cố định
(chống thiên lệch vị trí đáp án đúng), rồi sinh:
  - subjects/history/samples/teacher_difficulty_form.html  (mở trực tiếp)
  - subjects/history/samples/teacher_difficulty_form.gs     (Google Apps Script)
  - subjects/history/samples/teacher_difficulty_manifest.json (nội bộ — thứ
    tự xáo trộn từng câu, để đối chiếu khi cần, KHÔNG gửi giáo viên)

Usage:
    python tools/make_teacher_form.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(REPO))
from shared.form_template import generate_difficulty_form, generate_difficulty_apps_script

SEED = 42
CHUNK_SIZE = 30  # chia màn hình cho dễ chấm, không liên quan gán đề HS


def load_questions() -> dict:
    q = {}
    for fname in ("mcq_samples.json", "mcq_crawled.json"):
        p = REPO / "subjects" / "history" / "samples" / fname
        if p.exists():
            for r in json.loads(p.read_text(encoding="utf-8")):
                q[r["id"]] = r
    return q


def load_pool_ids() -> list:
    """Toàn bộ 120 câu trong pool T2: union các đề (đã có 10 câu neo lặp lại)
    + spare, khử trùng, giữ thứ tự ổn định (sort theo id) để manifest tái lập
    được."""
    tf_path = REPO / "subjects" / "history" / "samples" / "test_forms.json"
    if not tf_path.exists():
        sys.exit(f"Chưa có {tf_path}. Chạy tools/make_test_forms.py trước (T2).")
    data = json.loads(tf_path.read_text(encoding="utf-8"))
    ids = set()
    for items in data["forms"].values():
        ids.update(it["id"] for it in items)
    ids.update(it["id"] for it in data["spares"])
    return sorted(ids)


def shuffle_options(qid: str, q: dict, rng: np.random.Generator) -> list:
    """Trả list [(letter, text, is_correct)] đã xáo trộn, seed theo từng câu
    (ổn định qua nhiều lần chạy nếu SEED không đổi)."""
    opts = [(q["correct"], True)] + [(d, False) for d in q["distractors"]]
    order = rng.permutation(len(opts))
    letters = "ABCD"
    return [(letters[i], opts[order[i]][0], opts[order[i]][1])
           for i in range(len(opts))]


def main() -> None:
    questions = load_questions()
    pool_ids = load_pool_ids()
    print(f"Pool: {len(pool_ids)} câu (từ test_forms.json)")

    missing = [i for i in pool_ids if i not in questions]
    if missing:
        sys.exit(f"Thiếu nội dung cho {len(missing)} câu: {missing[:5]}...")

    manifest = {}
    sections = []
    items_by_section_gs = {}
    for ci in range(0, len(pool_ids), CHUNK_SIZE):
        chunk = pool_ids[ci:ci + CHUNK_SIZE]
        sec_id = f"nhom_{ci // CHUNK_SIZE + 1}"
        sec_title = f"Nhóm {ci // CHUNK_SIZE + 1} (câu {ci + 1}–{ci + len(chunk)})"
        items_html, items_gs = [], []
        for qid in chunk:
            q = questions[qid]
            rng = np.random.default_rng(SEED + hash(qid) % 1_000_000)
            opts = shuffle_options(qid, q, rng)
            manifest[qid] = {"order": [o[0] for o in opts],
                             "correct_letter": next(l for l, t, c in opts if c)}
            items_html.append({
                "id": qid,
                "stem": q["stem"],
                "context": q.get("source", ""),
                "options": [{"letter": l, "text": t, "is_correct": c}
                           for l, t, c in opts],
            })
            items_gs.append({"stem": q["stem"], "options": opts})
        sections.append({"id": sec_id, "title": sec_title,
                         "desc": f"{len(chunk)} câu — chấm độc lập, không cần theo thứ tự.",
                         "items": items_html})
        items_by_section_gs[sec_title] = items_gs

    html = generate_difficulty_form(
        subject_code="su9",
        subject_label="LỊCH SỬ 9",
        subject_vn="Lịch sử lớp 9",
        title="Phiếu chấm độ khó — Lịch sử 9 (khảo sát đối chiếu p-value)",
        sections=sections,
        intro_note=(
            "Bộ câu hỏi này được chọn để đối chiếu với dữ liệu học sinh làm bài thật "
            "và nhãn do AI gán tự động — nhãn của thầy/cô là một nguồn tham chiếu "
            "ĐỘC LẬP, xin đánh giá theo cảm nhận chuyên môn, không cần khớp với "
            "bất kỳ nguồn nào khác."
        ),
    )
    gs = generate_difficulty_apps_script(
        subject_label="Lich su 9", subject_code="su9",
        items_by_section=items_by_section_gs, total_items=len(pool_ids))

    out_html = REPO / "subjects" / "history" / "samples" / "teacher_difficulty_form.html"
    out_gs = REPO / "subjects" / "history" / "samples" / "teacher_difficulty_form.gs"
    out_manifest = REPO / "subjects" / "history" / "samples" / "teacher_difficulty_manifest.json"
    out_html.write_text(html, encoding="utf-8")
    out_gs.write_text(gs, encoding="utf-8")
    out_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  {len(sections)} nhóm x ~{CHUNK_SIZE} câu")
    print(f"  đã lưu -> {out_html}")
    print(f"  đã lưu -> {out_gs}")
    print(f"  đã lưu -> {out_manifest} (nội bộ, không gửi giáo viên)")


if __name__ == "__main__":
    main()
