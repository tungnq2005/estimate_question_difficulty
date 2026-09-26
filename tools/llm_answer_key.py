# -*- coding: utf-8 -*-
"""Sinh ĐÁP ÁN ĐÚNG cho câu trắc nghiệm kenhgiaovien (trang nguồn không có đáp án).

Trang kenhgiaovien.com chỉ đăng câu hỏi + nhãn mức độ do giáo viên soạn, KHÔNG
đăng đáp án. Nhãn độ khó (thứ ta cần) là của người; chỉ mỗi đáp án phải sinh
bằng LLM. Công cụ này tách bạch hai thứ đó và ĐO ĐỘ TIN CẬY của phần sinh ra.

Khác biệt giữa hai môn — và lí do phải đo:
  physics  đáp án khách quan (tính toán / định luật) → LLM đáng tin
  history  đáp án ÍT khách quan hơn (diễn giải, "nguyên nhân chủ yếu", "ý nghĩa
           quan trọng nhất") → KHÔNG được mặc định là đúng

May mắn: môn Sử có 236 câu đã ghép được đáp án NGƯỜI từ vietjack. Đó là tập
KIỂM CHỨNG MÙ — chạy `--validate` để đo đúng bao nhiêu phần trăm TRƯỚC khi tiêu
lượt gọi cho hơn 1.000 câu còn lại. Môn Lý trước đây không có thứ này.

Ba bước:
  0. bước chuẩn hoá (offline, không tốn lượt) — đưa `correct`/`distractors` về
     đúng bộ 4 phương án của kenhgiaovien. Bản ghép cũ chép nguyên phương án của
     vietjack, nhưng câu dẫn trùng KHÔNG bảo đảm bộ phương án trùng.
  1. `--validate` — chấm mù các câu đã biết đáp án người → độ chính xác thật.
  2. mặc định     — điền đáp án cho các câu canonical còn thiếu, rồi lan sang
     bản trùng. Nhiều lượt (`--passes 2`) cho hai lần xáo phương án khác nhau;
     hai lượt khớp nhau = tín hiệu tin cậy, lệch nhau = gắn cờ để lọc.

Chống thiên lệch vị trí: mỗi lượt xáo thứ tự phương án theo hash của id (tất
định), nên mô hình không thể bám vào "đáp án hay nằm ở vị trí B".

Idempotent: câu đã có `correct` thì bỏ qua; chạy lại không tốn thêm lượt.

Chạy:
    python tools/llm_answer_key.py --subject history --repair
    python tools/llm_answer_key.py --subject history --validate --api-key sk-...
    python tools/llm_answer_key.py --subject history --passes 2 --api-key sk-...
    python tools/llm_answer_key.py --subject history --dry-run     # đếm lượt gọi
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import random
import re
import sys
import unicodedata
import zlib
from collections import Counter
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]

BASE_URL = "https://api.deepseek.com/v1"
FLASH = "deepseek-v4-flash"
BATCH = 20
LETTERS = "ABCD"

SUBJECTS = {
    "physics": {
        "path": REPO / "subjects" / "physics" / "samples" / "mcq_kenhgiaovien.json",
        "system": (
            "Bạn là giáo viên Vật Lí 9. Với mỗi câu trắc nghiệm, chọn đáp án ĐÚNG "
            "duy nhất trong 4 lựa chọn A/B/C/D. Chỉ trả về JSON, không thêm văn bản "
            "ngoài JSON."
        ),
    },
    "history": {
        "path": REPO / "subjects" / "history" / "samples" / "mcq_kenhgiaovien.json",
        "system": (
            "Bạn là giáo viên Lịch sử 9, dạy theo sách giáo khoa Lịch sử 9 của Bộ "
            "GD&ĐT Việt Nam. Với mỗi câu trắc nghiệm, chọn đáp án ĐÚNG duy nhất "
            "trong 4 lựa chọn A/B/C/D, căn cứ vào nội dung SGK. Với câu hỏi dạng "
            "“chủ yếu nhất”, “quan trọng nhất”, “cơ bản nhất”, hãy chọn phương án "
            "mà SGK nhấn mạnh, không chọn phương án chỉ đúng một phần. "
            "Chỉ trả về JSON, không thêm văn bản ngoài JSON."
        ),
    },
}


# ----------------------------------------------------------------- tiện ích
def norm(t: str) -> str:
    t = unicodedata.normalize("NFC", (t or "").lower())
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()


def match_option(correct: str, options: list) -> int | None:
    """Chỉ số phương án khớp với chuỗi đáp án đến từ nguồn khác.

    Khớp đúng trước; không có thì dùng difflib nhưng ĐÒI HỎI khoảng cách rõ với
    phương án nhì (>= 0.15) để tránh gán bừa khi hai nguồn thực ra là hai đề
    khác nhau tình cờ trùng câu dẫn.
    """
    c, opts = norm(correct), [norm(o) for o in options]
    if c in opts:
        return opts.index(c)
    sc = sorted(((difflib.SequenceMatcher(None, c, o).ratio(), i)
                 for i, o in enumerate(opts)), reverse=True)
    if sc[0][0] >= 0.70 and sc[0][0] - sc[1][0] >= 0.15:
        return sc[0][1]
    return None


def shuffled(q: dict, p: int) -> list:
    """Hoán vị tất định của 4 phương án cho lượt p — cùng id, cùng p ⇒ cùng thứ tự."""
    order = list(range(len(q["options"])))
    random.Random(zlib.crc32(f"{q['id']}|{p}".encode())).shuffle(order)
    return order


def call(system: str, user: str, api_key: str, model: str, max_tokens=4000):
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"},
        "thinking": {"type": "disabled"},
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for attempt in range(3):
        try:
            r = requests.post(f"{BASE_URL}/chat/completions", json=payload,
                              headers=headers, timeout=120)
        except requests.RequestException as e:
            print(f"  ! lỗi mạng ({type(e).__name__}) lần {attempt + 1}/3")
            continue
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        print(f"  ! HTTP {r.status_code}: {r.text[:160]}")
        if r.status_code in (401, 403):
            break
    return None


def parse_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
    i, j = text.find("{"), text.rfind("}")
    if i >= 0 and j > i:
        text = text[i:j + 1]
    return json.loads(re.sub(r",\s*([}\]])", r"\1", text))


def build_prompt(chunk: list) -> str:
    lines = []
    for k, (q, order) in enumerate(chunk, 1):
        lines.append(f"Câu {k}: {q['stem']}")
        for c, oi in zip(LETTERS, order):
            lines.append(f"{c}. {q['options'][oi]}")
        lines.append("")
    return ("\n".join(lines) + "\nTrả về JSON schema: "
            f'{{"answers": ["A", "B", ...]}} (đúng {len(chunk)} chữ cái theo thứ tự câu).')


def solve(items: list, p: int, api_key: str, model: str, system: str) -> dict:
    """Một lượt chấm mù. Trả về {id: chỉ số phương án theo THỨ TỰ GỐC}."""
    picked, bad = {}, 0
    for start in range(0, len(items), BATCH):
        chunk = [(q, shuffled(q, p)) for q in items[start:start + BATCH]]
        raw = call(system, build_prompt(chunk), api_key, model)
        if raw is None:
            bad += len(chunk)
            print(f"  ! lượt {p} batch {start}-{start + len(chunk)} thất bại")
            continue
        try:
            ans = parse_json(raw)["answers"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            bad += len(chunk)
            print(f"  ! lượt {p} batch {start} parse lỗi ({type(e).__name__})")
            continue
        for (q, order), letter in zip(chunk, ans):
            letter = str(letter).strip().upper()[:1]
            if letter in LETTERS:
                picked[q["id"]] = order[LETTERS.index(letter)]
            else:
                bad += 1
        if (start // BATCH) % 5 == 0:
            print(f"  ... lượt {p}: {len(picked)}/{len(items)}")
    if bad:
        print(f"  lượt {p}: {bad} câu không lấy được đáp án")
    return picked


# ------------------------------------------------------------------ bước 0
def repair(data: list) -> dict:
    """Đưa `correct`/`distractors` về đúng bộ phương án của kenhgiaovien.

    `link_history_labels.py` chép nguyên `correct` + `distractors` của vietjack.
    Nhưng câu dẫn trùng KHÔNG bảo đảm bộ phương án trùng — có câu bộ phương án
    lệch hẳn, khiến các đặc trưng nhiễu loạn (`len_dist_mean`, jaccard...) được
    tính trên phương án của MỘT ĐỀ KHÁC với đề mà giáo viên đã gán nhãn.
    """
    st = Counter()
    for q in data:
        if not q.get("correct"):
            continue
        if not q.get("options"):      # bộ Lý đã bỏ `options` sau khi chốt đáp án
            st["giữ (không còn options)"] += 1
            continue
        if str(q.get("answer_source", "")).startswith("llm_answer_key"):
            st["giữ (LLM)"] += 1
            continue
        idx = match_option(q["correct"], q["options"])
        if idx is None:                       # hai nguồn thực ra là hai đề khác
            q["correct"], q["distractors"] = None, []
            q["answer_from"] = None
            q.pop("answer_letter", None)
            q.pop("answer_source", None)
            st["gỡ (phương án lệch)"] += 1
            continue
        exact = norm(q["correct"]) == norm(q["options"][idx])
        q["correct"] = q["options"][idx]
        q["distractors"] = [o for i, o in enumerate(q["options"]) if i != idx]
        q["answer_letter"] = LETTERS[idx]
        q["answer_source"] = "vietjack"
        st["khớp đúng" if exact else "khớp mờ"] += 1
    return dict(st)


def flag_defects(data: list) -> int:
    """Đánh dấu câu có phương án TRÙNG NHAU — lỗi của trang nguồn, không phải của LLM.

    Một câu 4 phương án mà có hai phương án cùng nội dung thì không tồn tại đáp
    án duy nhất: chọn bản nào cũng vừa đúng vừa sai. Không sửa được, chỉ gắn cờ
    để phía dùng loại ra thay vì âm thầm giữ lại.
    """
    n = 0
    for q in data:
        if not q.get("options"):
            continue
        q["option_defect"] = len(set(q["options"])) < len(q["options"])
        n += q["option_defect"]
    return n


def propagate(data: list) -> int:
    """Lan đáp án từ bản canonical sang các bản trùng cùng dup_group."""
    src = {q["dup_group"]: q for q in data
           if q.get("is_canonical") and q.get("correct") and q.get("dup_group") is not None}
    n = 0
    for q in data:
        if q.get("correct") or q.get("is_canonical") or not q.get("options"):
            continue
        s = src.get(q.get("dup_group"))
        if not s:
            continue
        idx = match_option(s["correct"], q["options"])
        if idx is None:
            continue
        q["correct"] = q["options"][idx]
        q["distractors"] = [o for i, o in enumerate(q["options"]) if i != idx]
        q["answer_letter"] = LETTERS[idx]
        q["answer_source"] = (s.get("answer_source") or "unknown") + ":propagated"
        n += 1
    return n


# ------------------------------------------------------------------ bước 1
def validate(data: list, args, cfg) -> dict:
    """Chấm MÙ những câu đã biết đáp án người → độ chính xác thật của LLM."""
    gold = {q["id"]: q["options"].index(q["correct"]) for q in data
            if q.get("answer_source") == "vietjack" and q.get("correct")
            and q.get("options")}
    items = [q for q in data if q["id"] in gold]
    if args.limit:
        items = items[: args.limit]
        gold = {q["id"]: gold[q["id"]] for q in items}
    ncall = args.passes * -(-len(items) // BATCH)
    print(f"[1] KIỂM CHỨNG MÙ — {len(items)} câu có đáp án NGƯỜI (vietjack), "
          f"{args.passes} lượt · {ncall} lượt gọi")
    if args.dry_run:
        return {"n": len(items), "n_calls": ncall, "dry_run": True}

    runs = [solve(items, p, args.api_key, args.model, cfg["system"])
            for p in range(args.passes)]
    per = []
    for p, picked in enumerate(runs):
        ok = sum(1 for i, g in gold.items() if picked.get(i) == g)
        cov = len(picked)
        per.append({"pass": p, "n_answered": cov, "acc": ok / max(1, cov)})
        print(f"    lượt {p}: trả lời {cov}/{len(items)} · ĐÚNG {ok} "
              f"({ok / max(1, cov):.1%})")

    out = {"n": len(items), "passes": per, "n_calls": ncall}
    if args.passes >= 2:
        both = [i for i in gold if all(i in r for r in runs)]
        agree = [i for i in both if len({r[i] for r in runs}) == 1]
        dis = [i for i in both if i not in set(agree)]
        acc_a = sum(1 for i in agree if runs[0][i] == gold[i]) / max(1, len(agree))
        acc_d = sum(1 for i in dis if runs[0][i] == gold[i]) / max(1, len(dis))
        print(f"    hai lượt KHỚP: {len(agree)}/{len(both)} "
              f"({len(agree) / max(1, len(both)):.1%}) · trong đó đúng {acc_a:.1%}")
        print(f"    hai lượt LỆCH: {len(dis)} · lượt 0 đúng {acc_d:.1%}")
        print("    ⇒ chênh giữa hai dòng trên = sức lọc của cờ answer_agree.")
        out["consistency"] = {"n_both": len(both), "n_agree": len(agree),
                              "acc_agree": acc_a, "n_disagree": len(dis),
                              "acc_disagree_pass0": acc_d}
    return out


# ------------------------------------------------------------------ bước 2
def fill(data: list, args, cfg) -> dict:
    todo = [q for q in data if q.get("is_canonical") and not q.get("correct")]
    if args.limit:
        todo = todo[: args.limit]
    ncall = args.passes * -(-len(todo) // BATCH)
    print(f"[2] SINH ĐÁP ÁN — {len(todo)} câu canonical còn thiếu, "
          f"{args.passes} lượt · {ncall} lượt gọi")
    if args.dry_run or not todo:
        return {"n_todo": len(todo), "n_calls": ncall, "dry_run": args.dry_run}

    runs = [solve(todo, p, args.api_key, args.model, cfg["system"])
            for p in range(args.passes)]
    n_ok = n_dis = 0
    for q in todo:
        votes = [r[q["id"]] for r in runs if q["id"] in r]
        if not votes:
            continue
        idx, cnt = Counter(votes).most_common(1)[0]
        q["correct"] = q["options"][idx]
        q["distractors"] = [o for i, o in enumerate(q["options"]) if i != idx]
        q["answer_letter"] = LETTERS[idx]
        q["answer_source"] = "llm_answer_key"
        q["answer_votes"] = [LETTERS[v] for v in votes]
        q["answer_agree"] = bool(cnt == len(votes) and len(votes) == args.passes)
        n_ok += 1
        n_dis += (not q["answer_agree"])
    print(f"    điền được {n_ok}/{len(todo)} câu · {n_dis} câu các lượt LỆCH nhau "
          f"({n_dis / max(1, n_ok):.1%}, gắn cờ answer_agree=false)")
    return {"n_todo": len(todo), "n_filled": n_ok, "n_disagree": n_dis,
            "n_calls": ncall}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="history", choices=sorted(SUBJECTS))
    ap.add_argument("--api-key", default=os.environ.get("DEEPSEEK_API_KEY"))
    ap.add_argument("--model", default=FLASH)
    ap.add_argument("--passes", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--repair", action="store_true",
                    help="chỉ chuẩn lại phương án (offline), không gọi API")
    ap.add_argument("--validate", action="store_true",
                    help="chấm mù tập đã biết đáp án để đo độ chính xác")
    ap.add_argument("--dry-run", action="store_true", help="chỉ đếm lượt gọi")
    args = ap.parse_args()

    cfg = SUBJECTS[args.subject]
    path = cfg["path"]
    data = json.loads(path.read_text(encoding="utf-8"))
    print(f"== {args.subject} · {len(data)} câu · {path.relative_to(REPO)}")

    st = repair(data)
    print("[0] chuẩn lại phương án: " + " · ".join(f"{k} {v}" for k, v in st.items()))

    report = {"subject": args.subject, "n_total": len(data), "repair": st,
              "model": args.model, "passes": args.passes}
    if not args.repair:
        if not args.dry_run and not args.api_key:
            sys.exit("✗ Thiếu API key (--api-key hoặc DEEPSEEK_API_KEY). "
                     "Dùng --dry-run để xem trước số lượt gọi.")
        report["validate" if args.validate else "fill"] = (
            validate(data, args, cfg) if args.validate else fill(data, args, cfg))

    n_def = flag_defects(data)
    n_prop = propagate(data)
    n_ans = sum(1 for q in data if q.get("correct"))
    src = Counter(q.get("answer_source") for q in data if q.get("correct"))
    canon = [q for q in data if q.get("is_canonical")]
    print(f"[3] lan sang bản trùng: +{n_prop} câu · "
          f"{n_def} câu có phương án TRÙNG NHAU (lỗi nguồn, cờ option_defect)")
    print(f"\n== TỔNG: {n_ans}/{len(data)} câu có đáp án ({n_ans / len(data):.1%}) · "
          + " · ".join(f"{k} {v}" for k, v in src.items()))
    print(f"   canonical có đáp án: "
          f"{sum(1 for q in canon if q.get('correct'))}/{len(canon)}")

    if not args.dry_run:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        rp = path.with_name("answer_key_report.json")
        report.update(n_propagated=n_prop, n_with_answer=n_ans,
                      n_option_defect=n_def, answer_source=dict(src))
        rp.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                      encoding="utf-8")
        print(f"→ {path.relative_to(REPO)}\n→ {rp.relative_to(REPO)}")


if __name__ == "__main__":
    main()
