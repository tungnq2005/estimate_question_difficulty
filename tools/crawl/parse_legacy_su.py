# -*- coding: utf-8 -*-
"""Parse bộ 670 câu trắc nghiệm Lịch Sử 9 crawl cũ -> mcq_crawled.json.

Nguồn: ``data_processed/sử_processed.txt`` trên nhánh git cũ
``origin/training-model`` (crawl từ vietjack.me, format text thuần:
Câu N / Câu hỏi / Các đáp án A-D / Đáp án đúng / Giải thích).

Đầu ra: ``subjects/history/samples/mcq_crawled.json`` — nằm CẠNH
``mcq_samples.json`` (10 câu gốc, không đụng tới). Schema mỗi câu khớp
dataclass ``MCQ`` trong ``shared/mcq/features.py``, cộng thêm các field
phục vụ gán nhãn: ``difficulty_vn`` (Nhận biết/Thông hiểu/Vận dụng/
Vận dụng cao), ``label_source`` ("llm" | "teacher" | null), ``source_url``.

Usage:
    python tools/crawl/parse_legacy_su.py            # tự lấy qua `git show`
    python tools/crawl/parse_legacy_su.py <raw.txt>  # hoặc từ file có sẵn
"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "subjects" / "history" / "samples" / "mcq_crawled.json"
GIT_REF = "origin/training-model:data_processed/sử_processed.txt"
SOURCE = "vietjack.me — Trắc nghiệm Lịch Sử 9 (crawl legacy, nhánh training-model)"

SEPARATOR = re.compile(r"^-{20,}\s*$", re.MULTILINE)
BLOCK_RE = re.compile(
    r"Câu\s+(?P<num>\d+):\s*\n"
    r"Môn:.*\n"
    r"Câu hỏi:\s*(?P<stem>.*)\n"
    r"Các đáp án:\s*\n"
    r"\s+A\.\s*(?P<a>.*)\n"
    r"\s+B\.\s*(?P<b>.*)\n"
    r"\s+C\.\s*(?P<c>.*)\n"
    r"\s+D\.\s*(?P<d>.*)\n"
    r"Đáp án đúng:\s*(?P<ans>[ABCD])[^\n]*"
    r"(?:\nGiải thích:\s*(?P<note>.*))?",
    re.DOTALL,
)


def _norm_key(text: str) -> str:
    """Khóa so trùng: bỏ dấu, thường hóa, gộp khoảng trắng."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "d").lower()
    return re.sub(r"\s+", " ", text).strip()


def parse(raw: str) -> list:
    questions, dupes, failed = [], 0, []
    seen = set()
    for block in SEPARATOR.split(raw):
        if "Câu hỏi:" not in block:
            continue
        m = BLOCK_RE.search(block)
        if not m:
            failed.append(block.strip()[:80])
            continue
        opts = {k: m.group(k).strip() for k in ("a", "b", "c", "d")}
        correct = opts.pop(m.group("ans").lower())
        stem = m.group("stem").strip()
        note = (m.group("note") or "").strip() or None

        key = _norm_key(stem) + "||" + "|".join(sorted(_norm_key(o) for o in [correct, *opts.values()]))
        if key in seen:
            dupes += 1
            continue
        seen.add(key)

        questions.append({
            "id": f"su9_vj_{len(questions) + 1:04d}",
            "stem": stem,
            "correct": correct,
            "distractors": list(opts.values()),
            "difficulty": None,
            "difficulty_vn": None,
            "label_source": None,
            "source": SOURCE,
            "source_url": None,
            "notes": note,
        })

    print(f"Parsed: {len(questions)} | trùng lặp bỏ qua: {dupes} | lỗi parse: {len(failed)}")
    for f in failed:
        print(f"  FAILED: {f}")
    return questions


def main() -> None:
    if len(sys.argv) > 1:
        raw = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        raw = subprocess.run(
            ["git", "show", GIT_REF], cwd=REPO_ROOT,
            capture_output=True, check=True,
        ).stdout.decode("utf-8")

    questions = parse(raw)
    OUT_PATH.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Đã ghi {len(questions)} câu -> {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
