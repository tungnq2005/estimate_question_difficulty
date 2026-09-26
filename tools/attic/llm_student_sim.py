# -*- coding: utf-8 -*-
"""C3 — Mô phỏng học sinh bằng LLM đóng vai (Acquaye et al. 2026), CÓ GỌI API THẬT.

VÌ SAO CẦN: T1 (xin phép trường tổ chức làm bài) KHÔNG được duyệt, nên không
có p-value từ học sinh thật. Đây là phương án dự phòng đã ghi sẵn trong kế
hoạch — thay ground truth tâm trắc học thật bằng phản hồi mô phỏng, để E1
(nhãn LLM đo cái gì) và E3 (Cold->Warm, tools/coldwarm.py) vẫn chạy được.

KHÁC CƠ BẢN với tools/llm_persona_pilot.py: file kia là phán đoán THỦ CÔNG
độ đặc thù nội dung (δ) rồi suy ra đúng/sai bằng hàm bậc thang — không có LLM
nào thật sự trả lời câu hỏi. File này cho LLM **THỰC SỰ LÀM BÀI**: đóng vai
học sinh lớp 9 ở 5 mức năng lực, đọc câu hỏi, chọn phương án. Đây mới đúng
phương pháp của Acquaye 2026, và là điểm mấu chốt bảo vệ trước hội đồng:

  Acquaye 2026 phát hiện LLM **chấm trực tiếp** độ khó cho kết quả KÉM (đây
  chính là nhãn llm_vote3 hiện có của nhóm), nhưng LLM **đóng vai học sinh
  làm bài** rồi khớp IRT đạt tương quan 0,75-0,82 với tỉ lệ đúng thật (NAEP).
  Hai tác vụ khác nhau về bản chất -> dùng cái sau kiểm toán cái trước KHÔNG
  phải lập luận vòng tròn.

  Bài đó còn phát hiện: model YẾU hơn lại dự đoán độ khó thật TỐT hơn model
  mạnh (vì "sai giống học sinh" hơn). Nên dùng model nhanh/rẻ (deepseek flash)
  là lựa chọn CÓ CƠ SỞ, không phải thoả hiệp vì ngân sách.

CHỐNG THIÊN LỆCH (bắt buộc, nếu thiếu thì số đo vô nghĩa):
  1. MÙ HOÀN TOÀN: prompt KHÔNG chứa nhãn độ khó, KHÔNG chứa `notes`/lời giải,
     KHÔNG đánh dấu đâu là đáp án đúng.
  2. XÁO PHƯƠNG ÁN theo từng lần gọi (seed tất định theo item+persona+rep) —
     khử thiên lệch vị trí (LLM hay chọn A hoặc chọn đáp án dài nhất).
  3. NHIỀU LẦN LẶP ở temperature > 0 -> p-value có phương sai thật, không phải
     hàm bậc thang tất định.
  4. TÊN HỌC SINH ĐA DẠNG cho từng persona (Acquaye 2026: dùng tên thật cho
     kết quả tốt hơn dùng ID vô danh).

ĐẦU RA (schema TRÙNG KHỚP student_responses.csv thật -> nạp thẳng vào
tools/item_analysis.py và tools/coldwarm.py, không phải sửa gì):
    student_id, form, item_id, correct
Kèm nhật ký thô .jsonl để truy vết/tái lập từng lượt trả lời một.

Usage:
    export DEEPSEEK_API_KEY=sk-...        # hoặc --api-key
    python tools/llm_student_sim.py --dry-run          # xem prompt, không gọi API
    python tools/llm_student_sim.py --limit 5          # thử 5 câu trước
    python tools/llm_student_sim.py                    # chạy đủ 100 câu
"""
import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import requests

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
SAMPLES = REPO / "subjects" / "history" / "samples"

DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
# deepseek-v4-flash (nhẹ) vs deepseek-v4-pro (mạnh). Mặc định dùng FLASH — theo
# Acquaye 2026 model yếu hơn lại dự đoán độ khó thật tốt hơn vì "sai giống học
# sinh" hơn. Chạy cả hai (--model, --out-tag khác nhau) để kiểm chứng lại phát
# hiện đó trên tiếng Việt.
DEFAULT_MODEL = "deepseek-v4-flash"
LETTERS = ["A", "B", "C", "D"]

# 5 mức năng lực. Mỗi persona có TÊN thật (Acquaye 2026) + mô tả thói quen học
# tập cụ thể, thay vì chỉ nói "học sinh giỏi/yếu" — mô tả hành vi giúp model
# nhập vai nhất quán hơn là gán nhãn trừu tượng.
PERSONAS = [
    {
        "tau": 1, "name": "Trân",
        "desc": "học lực YẾU môn Lịch sử, điểm trung bình môn khoảng 3,5/10. Em "
                "gần như không học bài ở nhà và ngủ gật trong nhiều tiết Sử. "
                "Trong cả chương trình em chỉ nhớ được đúng vài cái tên nổi "
                "tiếng nhất: Cách mạng tháng Tám, Điện Biên Phủ, Bác Hồ đọc "
                "Tuyên ngôn Độc lập — và cũng không nhớ rõ năm nào. Em không "
                "phân biệt được các hội nghị, các cương lĩnh, các tổ chức với "
                "nhau. Với đại đa số câu hỏi trong đề, em KHÔNG BIẾT và khoanh "
                "bừa cho xong. Em thường làm đúng khoảng 3-4 câu trên 10.",
    },
    {
        "tau": 2, "name": "Huy",
        "desc": "học lực TRUNG BÌNH - YẾU môn Lịch sử, điểm trung bình môn khoảng "
                "5/10. Em chỉ học thuộc lòng vội phần in đậm trong sách vào tối "
                "trước hôm kiểm tra và quên khá nhanh. Em nhận ra được các sự "
                "kiện lớn hay được nhắc đi nhắc lại trên lớp, nhưng lẫn lộn các "
                "mốc thời gian gần nhau và không phân biệt được các văn kiện. "
                "Gặp câu phủ định ('không phải là...') em hay đọc sót chữ "
                "'không'. Câu nào đòi so sánh hay giải thích nguyên nhân thì em "
                "chọn theo cảm tính. Em thường làm đúng khoảng 5 câu trên 10.",
    },
    {
        "tau": 3, "name": "Ngọc",
        "desc": "học lực TRUNG BÌNH môn Lịch sử, điểm trung bình môn khoảng "
                "6,5/10. Em có học bài và nắm được mạch sự kiện chính của chương "
                "trình, làm tốt các câu nhận biết và thông hiểu quen thuộc. "
                "Nhưng với chi tiết hẹp ít được nhấn mạnh trên lớp, hoặc câu đòi "
                "so sánh hai giai đoạn, em phân vân giữa hai phương án và chọn "
                "sai chừng một nửa số lần. Em thường làm đúng khoảng 6-7 câu "
                "trên 10.",
    },
    {
        "tau": 4, "name": "Bảo",
        "desc": "học lực KHÁ môn Lịch sử, điểm trung bình môn khoảng 8/10. Em học "
                "bài đều đặn, hiểu quan hệ nhân quả giữa các sự kiện và làm được "
                "phần lớn câu vận dụng. Em vẫn sai ở những câu đòi phân biệt rất "
                "tinh vi giữa các hội nghị hoặc cương lĩnh liền kề nhau, và ở "
                "các chi tiết rất hẹp nằm ngoài trọng tâm ôn tập. Em thường làm "
                "đúng khoảng 8 câu trên 10.",
    },
    {
        "tau": 5, "name": "Linh",
        "desc": "học lực GIỎI môn Lịch sử, điểm trung bình môn 9,5/10, đang trong "
                "đội tuyển học sinh giỏi Sử của trường. Em nắm chắc cả chi tiết "
                "ngoài lề lẫn các luận điểm phân tích, làm được hầu hết câu vận "
                "dụng cao. Em chỉ sai ở vài câu có bẫy diễn đạt cực kỳ tinh vi. "
                "Em thường làm đúng khoảng 9 câu trên 10.",
    },
]

SYSTEM_PROMPT = (
    "Đây là một bài mô phỏng giáo dục. Bạn KHÔNG phải là trợ lý AI đang trả lời "
    "câu hỏi. Bạn đang mô phỏng chính xác hành vi làm bài của MỘT học sinh lớp 9 "
    "cụ thể người Việt Nam trong phòng thi môn Lịch sử.\n\n"
    "NHIỆM VỤ CỦA BẠN KHÔNG PHẢI LÀ TRẢ LỜI ĐÚNG. Nhiệm vụ của bạn là dự đoán "
    "đúng em học sinh đó sẽ khoanh vào ô nào — kể cả khi đó là ô sai. Một mô "
    "phỏng mà học sinh yếu vẫn làm đúng hết là mô phỏng THẤT BẠI.\n\n"
    "Cách làm:\n"
    "1. Đọc mô tả học lực của em học sinh. Tự hỏi: với trình độ này, em ấy CÓ "
    "THỰC SỰ NHỚ kiến thức cần để làm câu này không?\n"
    "2. Nếu CÓ nhớ chắc -> chọn phương án đúng.\n"
    "3. Nếu chỉ mang máng -> chọn phương án nghe QUEN TAI nhất, hoặc phương án "
    "chứa từ khoá vừa xuất hiện trong câu hỏi. Đây thường là bẫy và thường sai.\n"
    "4. Nếu KHÔNG nhớ gì -> em ấy đoán bừa. Hãy chọn thật sự ngẫu nhiên trong 4 "
    "phương án, ĐỪNG dùng kiến thức của bạn để chọn đúng.\n\n"
    "Học sinh lớp 9 học lực yếu ở Việt Nam làm đề trắc nghiệm Lịch sử thường chỉ "
    "đúng khoảng 30-40% số câu — gần mức đoán bừa. Nếu bạn thấy mình đang chọn "
    "đúng gần hết cho một em học lực yếu, nghĩa là bạn đang trả lời bằng kiến "
    "thức của BẠN chứ không phải của em ấy, và bạn đã làm sai nhiệm vụ.\n\n"
    "Chỉ trả lời bằng đúng MỘT chữ cái in hoa: A, B, C hoặc D. Không giải thích."
)


def build_user_prompt(persona: dict, stem: str, options: list) -> str:
    opts = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(options))
    return (
        f"Em tên là {persona['name']}, {persona['desc']}\n\n"
        f"Câu hỏi:\n{stem}\n\n{opts}\n\n"
        f"{persona['name']} chọn đáp án nào? Chỉ trả lời một chữ cái."
    )


def load_items(limit: int | None) -> list:
    """100 câu duy nhất trong 3 đề khảo sát (10 câu neo dùng chung cả 3 đề)."""
    tf = json.loads((SAMPLES / "test_forms.json").read_text(encoding="utf-8"))
    crawled = {r["id"]: r for r in json.loads(
        (SAMPLES / "mcq_crawled.json").read_text(encoding="utf-8"))}
    samples = {r["id"]: r for r in json.loads(
        (SAMPLES / "mcq_samples.json").read_text(encoding="utf-8"))}
    bank = {**samples, **crawled}

    seen, items = set(), []
    for form_id, rows in tf["forms"].items():
        for r in rows:
            iid = r["id"] if isinstance(r, dict) else r
            if iid in seen:
                continue
            seen.add(iid)
            q = bank.get(iid)
            if q is None:
                print(f"  ⚠ bỏ qua {iid}: không tìm thấy trong ngân hàng câu hỏi")
                continue
            items.append({
                "id": iid,
                "stem": q["stem"],
                "correct": q["correct"],
                "distractors": list(q["distractors"]),
                "label_llm": q.get("difficulty"),
                "form": form_id,
            })
    items.sort(key=lambda x: x["id"])          # tất định, không phụ thuộc thứ tự đề
    return items[:limit] if limit else items


def shuffled_options(item: dict, seed_key: str) -> tuple:
    """Xáo phương án tất định theo seed_key -> (options, chỉ số đáp án đúng).

    Tất định để chạy lại cho ra ĐÚNG cùng thứ tự phương án (tái lập được),
    nhưng khác nhau giữa các lượt (khử thiên lệch vị trí)."""
    opts = [item["correct"]] + item["distractors"]
    rng = random.Random(seed_key)
    idx = list(range(len(opts)))
    rng.shuffle(idx)
    return [opts[i] for i in idx], idx.index(0)


def call_api(base_url: str, api_key: str, model: str, system: str, user: str,
             temperature: float, timeout: int, max_retries: int,
             thinking: bool = False) -> str | None:
    """Gọi API tương thích chuẩn OpenAI (DeepSeek, ...).

    thinking=False (mặc định) tắt chế độ suy luận. ĐÂY LÀ LỰA CHỌN CÓ CHỦ ĐÍCH,
    không phải để tiết kiệm: deepseek-v4-* là model suy luận, để mặc định nó
    sinh ~56 token cân nhắc trước khi trả lời -> lập luận cẩn thận tới mức
    persona "học lực Yếu" vẫn chọn đúng, tỉ lệ đúng kịch trần ở cả 5 mức và
    p-value mất hết phương sai. Học sinh thật trong phòng thi trả lời theo
    phản xạ. Tắt suy luận cho hành vi GẦN học sinh hơn, đúng tinh thần phát
    hiện của Acquaye 2026 (model càng ít "nghĩ kỹ" càng mô phỏng học sinh tốt).
    Bật lại bằng --thinking để làm nhánh ĐỐI CHỨNG.
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": temperature,
        # tắt suy luận: chỉ cần vài token cho 1 chữ cái. bật suy luận: phải
        # chừa đủ chỗ cho reasoning_content, nếu không content sẽ rỗng.
        "max_tokens": 512 if thinking else 8,
    }
    if not thinking:
        payload["thinking"] = {"type": "disabled"}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for attempt in range(max_retries):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=timeout)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            if r.status_code in (429, 500, 502, 503, 504):
                wait = 2 ** attempt
                print(f"    HTTP {r.status_code}, chờ {wait}s rồi thử lại...")
                time.sleep(wait)
                continue
            print(f"    ✗ HTTP {r.status_code}: {r.text[:200]}")
            return None
        except requests.RequestException as e:
            wait = 2 ** attempt
            print(f"    lỗi mạng ({e.__class__.__name__}), chờ {wait}s...")
            time.sleep(wait)
    return None


def parse_letter(raw: str | None) -> str | None:
    if not raw:
        return None
    for ch in raw.strip().upper():
        if ch in LETTERS:
            return ch
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.environ.get("DEEPSEEK_API_KEY"))
    ap.add_argument("--base-url", default=os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL))
    ap.add_argument("--model", default=os.environ.get("LLM_MODEL", DEFAULT_MODEL))
    ap.add_argument("--repeats", type=int, default=4,
                    help="số lần lặp mỗi (câu, persona) — càng nhiều p-value càng mịn")
    ap.add_argument("--temperature", type=float, default=1.0,
                    help="cần > 0 để p-value có phương sai thật")
    ap.add_argument("--limit", type=int, default=None, help="chỉ chạy N câu đầu (để thử)")
    ap.add_argument("--sleep", type=float, default=0.15, help="giãn cách giữa các lời gọi")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--max-retries", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true", help="in prompt mẫu, KHÔNG gọi API")
    ap.add_argument("--thinking", action="store_true",
                    help="BẬT chế độ suy luận (mặc định TẮT — xem docstring call_api). "
                         "Dùng cho nhánh đối chứng kiểm định lại Acquaye 2026.")
    ap.add_argument("--out-tag", default="LLMSIM_API")
    args = ap.parse_args()

    items = load_items(args.limit)
    total = len(items) * len(PERSONAS) * args.repeats
    print(f"Câu hỏi: {len(items)} | persona: {len(PERSONAS)} | lặp: {args.repeats}"
          f"  ->  {total} lượt trả lời")
    print(f"Model: {args.model} @ {args.base_url}\n")

    if args.dry_run:
        it = items[0]
        opts, ci = shuffled_options(it, f"{it['id']}|1|0")
        print("=" * 72)
        print("SYSTEM:\n" + SYSTEM_PROMPT)
        print("-" * 72)
        print("USER:\n" + build_user_prompt(PERSONAS[0], it["stem"], opts))
        print("-" * 72)
        print(f"(đáp án đúng nằm ở vị trí {LETTERS[ci]} sau khi xáo — "
              f"model KHÔNG được biết điều này)")
        print("=" * 72)
        print("\n--dry-run: chưa gọi API. Bỏ cờ này để chạy thật.")
        return

    if not args.api_key:
        sys.exit("✗ Thiếu API key. Đặt biến môi trường DEEPSEEK_API_KEY hoặc dùng --api-key")

    out_csv = SAMPLES / f"student_responses.{args.out_tag}.csv"
    log_path = SAMPLES / f"llm_student_sim.{args.out_tag}.jsonl"

    # Tiếp tục được sau khi ngắt: đọc lại nhật ký, bỏ qua lượt đã có.
    done = set()
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                done.add((r["item_id"], r["tau"], r["rep"]))
            except (json.JSONDecodeError, KeyError):
                continue
        if done:
            print(f"Đã có {len(done)} lượt trong nhật ký cũ -> bỏ qua, chạy tiếp.\n")

    n_done = n_fail = 0
    t0 = time.time()
    with log_path.open("a", encoding="utf-8") as log:
        for qi, it in enumerate(items, 1):
            for p in PERSONAS:
                for rep in range(args.repeats):
                    key = (it["id"], p["tau"], rep)
                    if key in done:
                        continue
                    opts, correct_idx = shuffled_options(
                        it, f"{it['id']}|{p['tau']}|{rep}")
                    raw = call_api(
                        args.base_url, args.api_key, args.model, SYSTEM_PROMPT,
                        build_user_prompt(p, it["stem"], opts),
                        args.temperature, args.timeout, args.max_retries,
                        thinking=args.thinking)
                    letter = parse_letter(raw)
                    if letter is None:
                        n_fail += 1
                    is_correct = int(letter == LETTERS[correct_idx]) if letter else None
                    log.write(json.dumps({
                        "item_id": it["id"], "tau": p["tau"], "persona": p["name"],
                        "rep": rep, "raw": raw, "letter": letter,
                        "correct_letter": LETTERS[correct_idx],
                        "is_correct": is_correct, "label_llm": it["label_llm"],
                        "form": it["form"],
                    }, ensure_ascii=False) + "\n")
                    log.flush()
                    n_done += 1
                    time.sleep(args.sleep)
            rate = n_done / max(time.time() - t0, 1e-6)
            eta = (total - len(done) - n_done) / rate if rate > 0 else 0
            print(f"  [{qi}/{len(items)}] {it['id']}  "
                  f"đã gọi {n_done} | lỗi {n_fail} | còn ~{eta/60:.1f} phút")

    # --- Kết xuất CSV đúng schema student_responses.csv ---
    import pandas as pd
    rows = [json.loads(l) for l in log_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [r for r in rows if r.get("is_correct") is not None]
    df = pd.DataFrame([{
        "student_id": f"llmsim_p{r['tau']}_r{r['rep']+1}",
        "form": r["form"],
        "item_id": r["item_id"],
        "correct": r["is_correct"],
    } for r in rows])
    df.to_csv(out_csv, index=False, encoding="utf-8")

    print(f"\n✓ {len(df)} lượt trả lời hợp lệ ({n_fail} lượt không đọc được đáp án)")
    print(f"  -> {out_csv}")
    print(f"  -> {log_path}  (nhật ký thô, truy vết từng lượt)")

    p = df.groupby("item_id")["correct"].mean()
    print(f"\np-value mô phỏng: trung bình {p.mean():.3f} | "
          f"nhỏ nhất {p.min():.3f} | lớn nhất {p.max():.3f} | độ lệch chuẩn {p.std():.3f}")
    if p.std() < 0.10:
        print("  ⚠ Phương sai p-value RẤT THẤP — model có thể đang trả lời đúng bất kể "
              "persona (không nhập vai được mức năng lực yếu). Kiểm tra tỉ lệ đúng theo "
              "từng persona bên dưới trước khi dùng số này.")
    # --- KIỂM ĐỊNH HIỆU LỰC MÔ PHỎNG ---
    # Không đòi đơn điệu TUYỆT ĐỐI: với ~n lượt/persona, chênh lệch nhỏ giữa hai
    # mức kề nhau (nhất là ở vùng sát trần) nằm trong nhiễu lấy mẫu và bắt lỗi nó
    # là sai về thống kê. Cái phải kiểm là: (a) có gradient năng lực rõ rệt không
    # (tương quan hạng τ vs tỉ lệ đúng), (b) mức yếu nhất có thực sự xuống thấp
    # không, (c) từng đảo chiều có vượt nhiễu không.
    raw_df = pd.DataFrame(rows)
    g = raw_df.groupby("tau")["is_correct"]
    by_tau, n_tau = g.mean(), g.size()
    print("\nTỉ lệ đúng theo mức năng lực (kèm sai số chuẩn):")
    for tau, acc in by_tau.items():
        nm = next(x["name"] for x in PERSONAS if x["tau"] == tau)
        se = (acc * (1 - acc) / n_tau[tau]) ** 0.5
        print(f"  τ={tau} ({nm}): {acc:.3f} ± {se:.3f}   (n={n_tau[tau]})")

    taus = by_tau.index.to_numpy(dtype=float)
    accs = by_tau.to_numpy(dtype=float)
    rho = float(np.corrcoef(pd.Series(taus).rank(), pd.Series(accs).rank())[0, 1])
    spread = float(accs.max() - accs.min())
    print(f"\n  Tương quan hạng τ vs tỉ lệ đúng: ρ = {rho:+.3f}   "
          f"| độ trải: {spread:.3f}")

    ok = True
    if rho < 0.80:
        print("  ⚠ Gradient năng lực YẾU — persona chưa phân tách được. "
              "Sửa mô tả persona trước khi dùng số này.")
        ok = False
    if spread < 0.25:
        print("  ⚠ Độ trải quá hẹp — mọi mức năng lực làm bài gần như nhau.")
        ok = False
    if accs[0] > 0.55:
        print(f"  ⚠ Mức YẾU NHẤT đạt {accs[0]:.3f} — quá cao so với học sinh yếu "
              "thật (~0,35). Model đang dùng kiến thức của CHÍNH NÓ thay vì nhập vai.")
        ok = False
    # báo cáo đảo chiều, nhưng chỉ coi là vấn đề khi vượt 2 sai số chuẩn
    for i in range(len(accs) - 1):
        d = accs[i + 1] - accs[i]
        if d < 0:
            se_d = ((accs[i] * (1 - accs[i]) / n_tau.iloc[i]) +
                    (accs[i + 1] * (1 - accs[i + 1]) / n_tau.iloc[i + 1])) ** 0.5
            sig = "VƯỢT nhiễu — cần xem lại" if abs(d) > 2 * se_d else "trong nhiễu, chấp nhận được"
            print(f"  · đảo chiều τ={int(taus[i])}→τ={int(taus[i+1])}: "
                  f"{d:+.3f} (2·SE={2*se_d:.3f}) — {sig}")
            if abs(d) > 2 * se_d:
                ok = False
    print("\n  => Mô phỏng " + ("ĐẠT hiệu lực để dùng cho E1/E3."
                                if ok else "CHƯA đạt — phải sửa hoặc nêu rõ hạn chế."))

    print("\n⚠ Đây là phản hồi MÔ PHỎNG, không phải học sinh thật. Mọi con số dẫn xuất "
          "(p-value, k*) phải ghi rõ 'trên dữ liệu mô phỏng' trong báo cáo.")


if __name__ == "__main__":
    main()
