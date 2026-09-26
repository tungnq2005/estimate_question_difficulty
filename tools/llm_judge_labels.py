# -*- coding: utf-8 -*-
"""LLM chấm mức NB/TH/VD/VDC — cho môn nào cũng chạy, để làm ĐƯỜNG CƠ SỞ.

Vì sao cần: phản biện đầu tiên với cả đề tài là *"vậy sao không hỏi thẳng LLM
cho xong?"*. Muốn trả lời thì phải có nhãn LLM **trên đúng những câu mà giáo
viên đã chấm**, ở cả hai môn. Lý đã có (`llm_judge_physics.py`, 1.539 câu);
Sử thì chỉ có 225 câu ghép được từ bộ vietjack — quá ít. Công cụ này chấm nốt.

Chấm MÙ: 4 phương án xáo tất định theo id, không đánh dấu đáp án đúng.
Idempotent: câu đã chấm thì bỏ qua.

Chạy:  python tools/llm_judge_labels.py --subject history_gv --api-key sk-...
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import random
import sys
import zlib
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))
import counterfactual_validity as cv  # noqa: E402
from llm_judge_physics import call, parse_json  # noqa: E402

BATCH = 20
LEVELS = ["NB", "TH", "VD", "VDC"]

RUBRIC = {
    "history": (
        "Bạn là giáo viên Lịch sử 9, chuyên gia về ma trận đề kiểm tra theo thang "
        "nhận thức của Bộ GD&ĐT. Với mỗi câu trắc nghiệm, hãy phân loại MỨC ĐỘ "
        "NHẬN THỨC mà câu hỏi yêu cầu vào ĐÚNG 1 trong 4 mức:\n"
        "- NB (Nhận biết): nhớ lại sự kiện, mốc thời gian, tên nhân vật, tổ chức, "
        "địa danh; dạng \"năm nào\", \"ai là\", \"ở đâu\", \"tên gọi\".\n"
        "- TH (Thông hiểu): giải thích nguyên nhân, ý nghĩa, mục đích; hiểu bản "
        "chất sự kiện; dạng \"vì sao\", \"nhằm\", \"phản ánh điều gì\".\n"
        "- VD (Vận dụng): so sánh, nhận xét, phân loại, liên hệ giữa các sự kiện; "
        "rút ra đặc điểm chung từ nhiều sự kiện.\n"
        "- VDC (Vận dụng cao): đánh giá, rút ra bài học, liên hệ thực tiễn hoặc "
        "với giai đoạn khác, nhận định về tác động lâu dài.\n"
        "Chỉ trả về JSON, không thêm bất kỳ văn bản nào ngoài JSON."
    ),
}


def shuffled(q):
    opts = [q["correct"]] + list(q["distractors"])
    order = list(range(len(opts)))
    random.Random(zlib.crc32(q["id"].encode()) & 0x7FFFFFFF).shuffle(order)
    return opts, order


def build_prompt(chunk):
    lines = []
    for k, q in enumerate(chunk, 1):
        opts, order = shuffled(q)
        lines.append(f"Câu {k}: {q['stem']}")
        for c, i in zip("ABCD", order):
            lines.append(f"{c}. {opts[i]}")
        lines.append("")
    return ("\n".join(lines) + '\nTrả về JSON: {"levels": ["NB", "TH", ...]} '
            f"(đúng {len(chunk)} mức theo thứ tự câu).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="history_gv")
    ap.add_argument("--api-key", default=os.environ.get("DEEPSEEK_API_KEY"))
    ap.add_argument("--model", default="deepseek-v4-flash")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    items = cv.load_items(args.subject)
    ont = cv.ontology_of(args.subject)
    out = REPO / "subjects" / ont / "samples" / f"llm_judge_{args.subject}.json"
    have = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    todo = [q for q in items if q["id"] not in have]
    if args.limit:
        todo = todo[: args.limit]
    print(f"== chấm mù {args.subject}: {len(items)} câu · đã có {len(have)} · "
          f"cần {len(todo)} · {-(-len(todo) // BATCH)} lượt gọi")
    if args.dry_run:
        return
    if not args.api_key:
        sys.exit("✗ Thiếu API key")
    rubric = RUBRIC[ont]

    ok = bad = 0
    for s in range(0, len(todo), BATCH):
        chunk = todo[s:s + BATCH]
        raw = call(args.model, rubric, build_prompt(chunk), args.api_key)
        if raw is None:
            bad += len(chunk)
            continue
        try:
            lv = parse_json(raw)["levels"]
        except (json.JSONDecodeError, KeyError, TypeError):
            bad += len(chunk)
            continue
        for q, v in zip(chunk, lv):
            v = str(v).strip().upper()
            if v in LEVELS:
                have[q["id"]] = v
                ok += 1
            else:
                bad += 1
        if (s // BATCH) % 5 == 0:
            print(f"  ... {ok}/{len(todo)}")

    out.write_text(json.dumps(have, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nchấm được {ok} · hỏng {bad} · tổng {len(have)}")
    print("phân bố:", dict(collections.Counter(have.values())))
    print(f"→ {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
