# -*- coding: utf-8 -*-
"""Sinh form TỰ ĐÁNH GIÁ (trả lời + chấm độ khó) để bạn (và vài người quen)
tự gán nhãn thật — thay/đối chiếu với pilot mô phỏng LLM (tools/llm_persona_pilot.py).

Chạy HOÀN TOÀN LOCAL — mở file .html trực tiếp bằng trình duyệt, không cần
Google Form/Apps Script/API key nào. Nhiều người có thể dùng CÙNG file (mỗi
người tự nhập "mã người đánh giá" khác nhau), rồi gửi lại từng file JSON export.

ƯU TIÊN: 70 câu đã có trong pilot LLM (20 cặp đối chứng x2 + 30 mẫu ngẫu
nhiên) được xếp Ở NHÓM ĐẦU TIÊN — đây là nơi so sánh trực tiếp với
tools/llm_persona_pilot.py có giá trị nhất. Phần còn lại của pool 120 câu xếp
ở các nhóm sau, làm thêm nếu có thời gian.

Output:
  - subjects/history/samples/self_assessment_form.html
  - subjects/history/samples/self_assessment_manifest.json (nội bộ, để chấm
    đúng/sai câu trả lời sau khi thu — KHÔNG cần gửi cho người đánh giá)

Sau khi thu file export JSON (1 file / người), dùng:
  python tools/convert_self_assessment.py --files a.json b.json ...

Usage:
    python tools/make_self_assessment_form.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from shared.form_template import generate_self_assessment_form

SEED = 42  # khớp SEED ở make_teacher_form.py / make_student_forms.py
CHUNK_SIZE = 30


def load_questions() -> dict:
    q = {}
    for fname in ("mcq_samples.json", "mcq_crawled.json"):
        p = REPO / "subjects" / "history" / "samples" / fname
        if p.exists():
            for r in json.loads(p.read_text(encoding="utf-8")):
                q[r["id"]] = r
    return q


def shuffle_options(q: dict, rng: np.random.Generator) -> list:
    opts = [(q["correct"], True)] + [(d, False) for d in q["distractors"]]
    order = rng.permutation(len(opts))
    letters = "ABCD"
    return [(letters[i], opts[order[i]][0], opts[order[i]][1])
           for i in range(len(opts))]


def priority_ids(tf: dict) -> list:
    """70 câu trong pilot LLM (20 cặp x2 + 30 mẫu ngẫu nhiên), theo đúng danh
    sách hard-code trong tools/llm_persona_pilot.py — import trực tiếp để
    không lệch."""
    sys.path.insert(0, str(REPO / "tools"))
    import llm_persona_pilot as pilot
    ids = list(pilot.DELTA.keys()) + list(pilot.RANDOM_SAMPLE_DELTA.keys())
    return ids


def main() -> None:
    tf_path = REPO / "subjects" / "history" / "samples" / "test_forms.json"
    if not tf_path.exists():
        sys.exit(f"Chưa có {tf_path}. Chạy tools/make_test_forms.py trước (T2).")
    tf = json.loads(tf_path.read_text(encoding="utf-8"))
    questions = load_questions()

    pool_ids = set()
    for items in tf["forms"].values():
        pool_ids.update(it["id"] for it in items)
    pool_ids.update(it["id"] for it in tf["spares"])

    prio = [i for i in priority_ids(tf) if i in pool_ids]
    rest = sorted(pool_ids - set(prio))
    ordered = prio + rest
    print(f"Pool: {len(ordered)} câu ({len(prio)} câu ưu tiên trùng pilot LLM + "
         f"{len(rest)} câu còn lại)")

    manifest = {}
    sections = []
    # Nhóm 1 riêng: đúng 70 câu ưu tiên (để so sánh trực tiếp với pilot LLM)
    chunks = [("uu_tien", "Nhóm ưu tiên — trùng pilot mô phỏng LLM", prio)]
    for ci in range(0, len(rest), CHUNK_SIZE):
        chunk = rest[ci:ci + CHUNK_SIZE]
        chunks.append((f"nhom_{ci//CHUNK_SIZE+2}",
                       f"Nhóm {ci//CHUNK_SIZE+2} (còn lại trong pool)", chunk))

    for sec_id, sec_title, ids in chunks:
        if not ids:
            continue
        items_html = []
        for qid in ids:
            q = questions[qid]
            rng = np.random.default_rng(SEED + hash(qid) % 1_000_000)
            opts = shuffle_options(q, rng)
            manifest[qid] = {"order": [o[0] for o in opts],
                             "correct_letter": next(l for l, t, c in opts if c),
                             "correct_text": next(t for _, t, c in opts if c)}
            items_html.append({
                "id": qid, "stem": q["stem"], "context": q.get("source", ""),
                "options": [{"letter": l, "text": t} for l, t, _ in opts],
            })
        sections.append({"id": sec_id, "title": sec_title,
                         "desc": f"{len(ids)} câu.", "items": items_html})
        print(f"  {sec_title}: {len(ids)} câu")

    html = generate_self_assessment_form(
        subject_code="su9", subject_label="LỊCH SỬ 9", subject_vn="Lịch sử lớp 9",
        title="Tự làm bài + tự chấm độ khó — Lịch sử 9",
        sections=sections,
        intro_note=(
            "Nhóm ưu tiên trùng đúng 70 câu đã dùng trong pilot mô phỏng LLM — "
            "làm nhóm này trước để so sánh trực tiếp được. Không sao nếu chỉ làm "
            "được một phần, cứ Export JSON những gì đã làm."
        ),
    )
    out_html = REPO / "subjects" / "history" / "samples" / "self_assessment_form.html"
    out_manifest = REPO / "subjects" / "history" / "samples" / "self_assessment_manifest.json"
    out_html.write_text(html, encoding="utf-8")
    out_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  đã lưu -> {out_html}")
    print(f"  đã lưu -> {out_manifest} (nội bộ, dùng để chấm — không gửi người đánh giá)")
    print("\n  Mở file .html bằng trình duyệt để tự làm. Nhiều người có thể dùng "
         "chung 1 file (mỗi người nhập mã riêng), mỗi người Export 1 file JSON riêng.")


if __name__ == "__main__":
    main()
