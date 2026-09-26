# -*- coding: utf-8 -*-
"""Dùng LLM sinh VẾT GIẢI, rồi lấy số bước làm ĐẶC TRƯNG — không phải làm nhãn.

Ý chính, và đây là chỗ khác mọi cách dùng LLM trước đó trong đề tài:

    LLM ĐÁNG TIN ở việc GIẢI     — đo được: 87,7% trên 211 câu Sử có đáp án
                                   người (`tools/llm_answer_key.py`), mà Lý còn
                                   khách quan hơn Sử.
    LLM KHÔNG đáng tin ở việc PHÁN ĐỘ KHÓ — đo được: κ 0,256 với giáo viên, và
                                   ở tầng VD/VDC chỉ đồng thuận 7,1%.

Vậy hãy hỏi nó thứ nó làm được (giải), rồi lấy *tiến trình giải* làm cột đặc
trưng: mấy bước tính, dùng công thức nào, mấy đại lượng đã cho, mấy ẩn trung
gian. Nhãn độ khó vẫn hoàn toàn của giáo viên. Đặc trưng dẫn xuất từ năng lực
mô hình CÓ, không nhiễm thiên lệch mà nó KHÔNG có.

Thêm một tác dụng phụ đáng giá: khớp chuỗi chỉ nhận ra thực thể `Formula` ở
**1/1539 câu** (nhãn công thức là "U = I.R", không bao giờ trùng lời văn đề).
LLM thì liên kết được. Nên bước này cũng là **liên kết thực thể cho lớp công
thức** — mở khoá `applicationSteps` trong ontology vốn đang nằm không.

Chống rò rỉ: 4 phương án được XÁO tất định và KHÔNG đánh dấu đáp án, nên mô hình
phải thật sự giải chứ không đọc ngược từ đáp án.

Idempotent: câu đã có vết thì bỏ qua; chạy lại không tốn thêm lượt.

Chạy:
    python tools/llm_solution_trace.py --limit 100 --api-key sk-...   # thử
    python tools/llm_solution_trace.py --api-key sk-...               # full
    python tools/llm_solution_trace.py --dry-run
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import random
import re
import sys
import zlib
from pathlib import Path

import rdflib
import requests

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))
import counterfactual_validity as cv  # noqa: E402

BASE_URL = "https://api.deepseek.com/v1"
FLASH = "deepseek-v4-flash"
BATCH = 20
LETTERS = "ABCD"
OUT = REPO / "subjects" / "physics" / "samples" / "solution_traces.json"

OPS = {"nho": 0, "hieu": 1, "tinh": 2, "phantich": 3}


def formula_catalog(subject="physics"):
    """17 công thức gốc do người soạn — chỉ nhóm này mang `applicationSteps`."""
    f = glob.glob(f"subjects/{subject}/ontology/*.ttl")[0]
    g = rdflib.Graph()
    g.parse(f, format="turtle")
    P = rdflib.Namespace("http://edu.vn/phys9/ontology#")
    out = []
    for s in g.subjects(rdflib.RDF.type, P.Formula):
        uri = str(s)
        code = uri.split("#")[-1]
        st = next(g.objects(s, P.applicationSteps), None)
        if st is None:                      # bỏ nhóm LLM_* (trùng lặp, không có steps)
            continue
        out.append({"code": code, "uri": uri,
                    "label": str(next(g.objects(s, rdflib.RDFS.label), "")),
                    "steps": int(st)})
    return sorted(out, key=lambda d: d["code"])


SYSTEM = (
    "Bạn là giáo viên Vật Lí 9. Với mỗi câu trắc nghiệm, hãy THỰC SỰ GIẢI nó, "
    "rồi báo cáo TIẾN TRÌNH GIẢI (không cần viết lời giải ra). "
    "Bạn KHÔNG được đoán mức độ khó — chỉ mô tả tiến trình. "
    "Chỉ trả về JSON, không thêm văn bản ngoài JSON."
)


def build_prompt(chunk, cat):
    cat_txt = "\n".join(f"  {f['code']}: {f['label']}" for f in cat)
    qs = []
    for k, (q, order) in enumerate(chunk, 1):
        qs.append(f"Câu {k}: {q['stem']}")
        for c, oi in zip(LETTERS, order):
            qs.append(f"{c}. {q['_opts'][oi]}")
        qs.append("")
    return (
        "DANH MỤC CÔNG THỨC (dùng đúng mã này):\n" + cat_txt + "\n\n"
        + "\n".join(qs) +
        f"\nVới mỗi câu, trả về một đối tượng:\n"
        '  "i": số thứ tự câu\n'
        '  "s": số BƯỚC TÍNH TOÁN thực sự phải làm (0 nếu chỉ cần nhớ lại/nhận ra)\n'
        '  "f": danh sách mã công thức phải dùng (rỗng [] nếu không dùng công thức nào)\n'
        '  "g": số đại lượng ĐÃ CHO trong đề (có kèm số liệu)\n'
        '  "u": số ẩn TRUNG GIAN phải tìm trước khi ra được đáp án\n'
        '  "t": loại thao tác — "nho" | "hieu" | "tinh" | "phantich"\n'
        '  "a": chữ cái đáp án đúng\n'
        f'Trả về JSON: {{"r": [ ... đúng {len(chunk)} đối tượng ... ]}}'
    )


def call(system, user, api_key, model, max_tokens=8000):
    payload = {"model": model,
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}],
               "temperature": 0.0, "response_format": {"type": "json_object"},
               "thinking": {"type": "disabled"}, "max_tokens": max_tokens}
    h = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for attempt in range(3):
        try:
            r = requests.post(f"{BASE_URL}/chat/completions", json=payload,
                              headers=h, timeout=180)
        except requests.RequestException as e:
            print(f"  ! mạng ({type(e).__name__}) lần {attempt + 1}/3")
            continue
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        print(f"  ! HTTP {r.status_code}: {r.text[:160]}")
        if r.status_code in (401, 403):
            break
    return None


def parse_json(t):
    t = t.strip()
    if t.startswith("```"):
        t = t.split("```", 2)[1]
    i, j = t.find("{"), t.rfind("}")
    if i >= 0 and j > i:
        t = t[i:j + 1]
    return json.loads(re.sub(r",\s*([}\]])", r"\1", t))


def shuffled(q, p=0):
    o = list(range(len(q["_opts"])))
    random.Random(zlib.crc32(f"{q['id']}|trace|{p}".encode())).shuffle(o)
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.environ.get("DEEPSEEK_API_KEY"))
    ap.add_argument("--model", default=FLASH)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cat = formula_catalog()
    codes = {f["code"] for f in cat}
    items = cv.load_items("physics")
    for q in items:
        q["_opts"] = [q["correct"]] + list(q["distractors"])
    traces = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    todo = [q for q in items if q["id"] not in traces]
    if args.limit:
        todo = todo[: args.limit]
    ncall = -(-len(todo) // BATCH)
    print(f"== vết giải Lý · {len(items)} câu · đã có {len(traces)} · "
          f"cần {len(todo)} · {ncall} lượt gọi · danh mục {len(cat)} công thức")
    if args.dry_run:
        return
    if not args.api_key:
        sys.exit("✗ Thiếu API key (--api-key hoặc DEEPSEEK_API_KEY)")
    if not todo:
        print("không còn gì để làm")
        return

    ok = bad = 0
    for start in range(0, len(todo), BATCH):
        chunk = [(q, shuffled(q)) for q in todo[start:start + BATCH]]
        raw = call(SYSTEM, build_prompt(chunk, cat), args.api_key, args.model)
        if raw is None:
            bad += len(chunk)
            continue
        try:
            rs = parse_json(raw)["r"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            bad += len(chunk)
            print(f"  ! batch {start} parse lỗi ({type(e).__name__})")
            continue
        by_i = {int(r.get("i", k + 1)): r for k, r in enumerate(rs)
                if isinstance(r, dict)}
        for k, (q, order) in enumerate(chunk, 1):
            r = by_i.get(k)
            if not r:
                bad += 1
                continue
            letter = str(r.get("a", "")).strip().upper()[:1]
            picked = order[LETTERS.index(letter)] if letter in LETTERS else None
            fl = [c for c in (r.get("f") or []) if c in codes]
            traces[q["id"]] = {
                "steps": int(r.get("s", 0) or 0),
                "formulas": fl,
                "n_formula_unknown": len(r.get("f") or []) - len(fl),
                "given": int(r.get("g", 0) or 0),
                "unknowns": int(r.get("u", 0) or 0),
                "op_type": str(r.get("t", "")).lower().replace("í", "i"),
                "answer_ok": (picked == 0) if picked is not None else None,
            }
            ok += 1
        if (start // BATCH) % 10 == 0:
            print(f"  ... {ok}/{len(todo)}")

    OUT.write_text(json.dumps(traces, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"\nlấy được {ok} · hỏng {bad} · tổng lưu {len(traces)}")
    got = [t for t in traces.values()]
    agree = [t["answer_ok"] for t in got if t["answer_ok"] is not None]
    print(f"khớp đáp án đang lưu: {sum(agree)}/{len(agree)} "
          f"({sum(agree) / max(1, len(agree)):.1%})  "
          f"— nhất quán nội bộ, KHÔNG phải chuẩn vàng")
    print("phân bố số bước:",
          dict(sorted(collections.Counter(t["steps"] for t in got).items())[:8]))
    print("phân bố loại thao tác:",
          dict(collections.Counter(t["op_type"] for t in got).most_common()))
    print("công thức hay dùng:",
          dict(collections.Counter(f for t in got
                                   for f in t["formulas"]).most_common(6)))
    print(f"→ {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
