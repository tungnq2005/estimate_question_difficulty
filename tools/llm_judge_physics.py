# -*- coding: utf-8 -*-
"""LLM chấm mức độ nhận thức NB/TH/VD/VDC cho 1539 câu Lý kenhgiaovien, đo đồng thuận với nhãn giáo viên.

Mục đích (nhánh A): kiểm "LLM có tái tạo được nhãn nhận thức của giáo viên không".
- Nhãn GV = ma trận NB/TH/VD/VDC do kenhgiaovien.com phân sẵn (giáo viên thiết kế).
- LLM chấm lại CÙNG thang NB/TH/VD/VDC (rubric Bộ GD&ĐT), MÙ đáp án (4 phương án
  xáo trộn deterministic, không đánh dấu đáp án đúng).
- Đo đồng thuận: Cohen κ, QWK, Kendall τ-b, Spearman, polychoric (tách severity
  khỏi thứ tự), confusion matrix 4×4, đồng thuận sau khi chuẩn hoá thang.

Input : subjects/physics/samples/mcq_kenhgiaovien.json (đã có correct + distractors + difficulty)
Output: subjects/physics/samples/mcq_kenhgiaovien_llmjudge.json   (thêm llm_level + shuffle_order)
        subjects/physics/samples/llm_judge_agreement.json         (bảng đồng thuận)

Usage:
    python tools/llm_judge_physics.py --api-key sk-... --limit 20    # thử
    python tools/llm_judge_physics.py --api-key sk-...               # full 1539
    python tools/llm_judge_physics.py --api-key sk-... --model deepseek-v4-flash
"""
import argparse
import json
import os
import random
import re
import sys
import zlib
from pathlib import Path

import numpy as np
import requests
from scipy.stats import kendalltau
from sklearn.metrics import cohen_kappa_score as qwk

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
import label_calibration as lc  # tái dùng polychoric / cohen_kappa / match_marginals

IN_PATH = REPO / "subjects" / "physics" / "samples" / "mcq_kenhgiaovien.json"
OUT_JUDGE = REPO / "subjects" / "physics" / "samples" / "mcq_kenhgiaovien_llmjudge.json"
OUT_AGREE = REPO / "subjects" / "physics" / "samples" / "llm_judge_agreement.json"

BASE_URL = "https://api.deepseek.com/v1"
MODEL = "deepseek-v4-pro"
BATCH = 20
LEVELS = ["NB", "TH", "VD", "VDC"]
L2ID = {v: i for i, v in enumerate(LEVELS)}

RUBRIC = (
    "Bạn là giáo viên Vật Lí 9, chuyên gia về ma trận đề kiểm tra theo thang nhận "
    "thức của Bộ GD&ĐT. Với mỗi câu trắc nghiệm, hãy phân loại MỨC ĐỘ NHẬN THỨC mà "
    "câu hỏi yêu cầu vào ĐÚNG 1 trong 4 mức:\n"
    "- NB (Nhận biết): nhớ lại, nhận ra, nêu tên, phát biểu định nghĩa/khái niệm/"
    "định luật/công thức; dạng câu \"là gì\", \"hiện tượng nào\", \"định nghĩa\".\n"
    "- TH (Thông hiểu): hiểu ý nghĩa, giải thích, so sánh, phân biệt, phân loại, "
    "suy luận đơn giản từ khái niệm; không cần tính toán phức tạp.\n"
    "- VD (Vận dụng): áp dụng công thức/kiến thức vào tình huống cụ thể, tính toán "
    "một hoặc vài bước.\n"
    "- VDC (Vận dụng cao): kết hợp nhiều kiến thức/công thức, tính toán nhiều bước, "
    "tình huống mới phức tạp.\n"
    "Chỉ trả về JSON, không thêm bất kỳ văn bản nào ngoài JSON."
)


def call(model, system, user, api_key, max_tokens=4000):
    url = f"{BASE_URL}/chat/completions"
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
            r = requests.post(url, json=payload, headers=headers, timeout=180)
        except requests.RequestException as e:
            print(f"  ! lỗi mạng ({type(e).__name__}) lần {attempt + 1}/3")
            continue
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        print(f"  ! HTTP {r.status_code}: {r.text[:160]}")
        if r.status_code in (401, 403):
            break
    return None


def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
    i = text.find("{")
    j = text.rfind("}")
    if i >= 0 and j > i:
        text = text[i:j + 1]
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return json.loads(text)


def shuffled_options(q):
    """4 phương án (đúng + 3 nhiễu) xáo trộn deterministic theo id — không đánh dấu đúng."""
    opts = [q["correct"]] + list(q["distractors"])
    rng = random.Random(zlib.crc32(q["id"].encode("utf-8")) & 0x7FFFFFFF)
    order = list(range(4))
    rng.shuffle(order)
    return [opts[i] for i in order], order


def build_batch_prompt(qs, shuffles):
    lines = []
    for k, (q, order) in enumerate(zip(qs, shuffles), 1):
        opts = [q["correct"]] + list(q["distractors"])
        lines.append(f"Câu {k}: {q['stem']}")
        for c, idx in zip("ABCD", order):
            lines.append(f"{c}. {opts[idx]}")
        lines.append("")
    body = "\n".join(lines)
    return (body + "\nTrả về JSON schema: "
            f'{{"levels": ["NB", "TH", "VD", "VDC", ...]}} (đúng {len(qs)} phần tử '
            "theo thứ tự câu, mỗi phần tử là 1 trong NB/TH/VD/VDC).")


def agreement(gv, llm):
    gv = np.array(gv); llm = np.array(llm)
    n = len(gv)
    out = {"n": int(n)}
    out["teacher_dist"] = {v: int(np.sum(gv == i)) for v, i in L2ID.items()}
    out["llm_dist"] = {v: int(np.sum(llm == i)) for v, i in L2ID.items()}
    out["kappa_raw"] = float(lc.cohen_kappa(gv, llm))
    out["qwk_quadratic"] = float(qwk(gv, llm, weights="quadratic"))
    out["qwk_linear"] = float(qwk(gv, llm, weights="linear"))
    out["spearman"] = float(np.corrcoef(
        np.argsort(np.argsort(gv)), np.argsort(np.argsort(llm)))[0, 1])
    out["kendall_tau_b"] = float(kendalltau(gv, llm, variant="b").statistic)
    out["polychoric"] = float(lc.polychoric(gv, llm, k=4))
    out["agreement_raw"] = float(np.mean(gv == llm))
    gv_c = lc.match_marginals(gv, llm, k=4)
    out["agreement_calibrated"] = float(np.mean(gv_c == llm))
    out["kappa_calibrated"] = float(lc.cohen_kappa(gv_c, llm))
    # confusion matrix (hàng = GV, cột = LLM) + recall từng mức GV
    cm = np.zeros((4, 4), dtype=int)
    for a, b in zip(gv, llm):
        cm[a, b] += 1
    out["confusion_gv_row_llm_col"] = cm.tolist()
    recall = {}
    for i, v in enumerate(LEVELS):
        recall[v] = float(cm[i, i] / max(cm[i].sum(), 1))
    out["recall_per_teacher_level"] = recall
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.environ.get("DEEPSEEK_API_KEY"))
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--limit", type=int, default=0, help="chỉ xử lý N câu đầu")
    args = ap.parse_args()

    if not args.api_key:
        sys.exit("✗ Thiếu API key (--api-key hoặc DEEPSEEK_API_KEY)")

    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    qs = data[: args.limit] if args.limit else data
    print(f"== LLM chấm NB/TH/VD/VDC cho {len(qs)} câu (model={args.model}, batch {BATCH}) ...")

    done, failed = 0, 0
    for start in range(0, len(qs), BATCH):
        chunk = qs[start:start + BATCH]
        shuffles = [shuffled_options(q)[1] for q in chunk]
        prompt = build_batch_prompt(chunk, shuffles)
        raw = call(args.model, RUBRIC, prompt, args.api_key)
        if raw is None:
            failed += len(chunk)
            print(f"  ! batch {start}-{start + len(chunk)} thất bại (HTTP/network)")
            continue
        try:
            levels = parse_json(raw)["levels"]
        except (json.JSONDecodeError, KeyError) as e:
            failed += len(chunk)
            print(f"  ! batch {start} parse lỗi ({type(e).__name__}), bỏ")
            continue
        for q, order, lv in zip(chunk, shuffles, levels):
            lv = str(lv).strip().upper()
            if lv in L2ID:
                q["llm_level"] = lv
                q["shuffle_order"] = order
                done += 1
            else:
                failed += 1
        if (start // BATCH) % 5 == 0:
            print(f"  ... {done}/{len(qs)} câu đã chấm")

    judged = [q for q in qs if "llm_level" in q]
    print(f"\n===== CHẤM XONG =====\nChấm được: {done} | Lỗi/bỏ: {failed}")

    if judged:
        gv = [L2ID[q["difficulty"]] for q in judged]
        llm = [L2ID[q["llm_level"]] for q in judged]
        res = agreement(gv, llm)

        OUT_JUDGE.write_text(
            json.dumps(judged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        OUT_AGREE.write_text(
            json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Đã ghi -> {OUT_JUDGE.relative_to(REPO)}")
        print(f"Đã ghi -> {OUT_AGREE.relative_to(REPO)}\n")

        print("=" * 66)
        print("ĐỒNG THUẬN GV vs LLM (thang NB/TH/VD/VDC)")
        print("=" * 66)
        print(f"  n                            {res['n']}")
        print(f"  phân bố GV     " + "  ".join(
            f"{v}={res['teacher_dist'][v]}" for v in LEVELS))
        print(f"  phân bố LLM    " + "  ".join(
            f"{v}={res['llm_dist'][v]}" for v in LEVELS))
        print(f"  Cohen κ (thô)                {res['kappa_raw']:+.3f}")
        print(f"  QWK (quadratic)              {res['qwk_quadratic']:+.3f}")
        print(f"  QWK (linear)                 {res['qwk_linear']:+.3f}")
        print(f"  Spearman ρ                   {res['spearman']:+.3f}")
        print(f"  Kendall τ-b                  {res['kendall_tau_b']:+.3f}")
        print(f"  ⭐ Polychoric (biến ẩn)      {res['polychoric']:+.3f}")
        print(f"  đồng thuận tuyệt đối         {res['agreement_raw']*100:5.1f}%")
        print(f"  đồng thuận sau chuẩn thang   {res['agreement_calibrated']*100:5.1f}%  "
              f"(κ={res['kappa_calibrated']:+.3f})")
        print(f"\n  recall từng mức GV (hàng GV → LLM chấm đúng mức đó):")
        for v in LEVELS:
            print(f"    {v:<5} {res['recall_per_teacher_level'][v]*100:5.1f}%")


if __name__ == "__main__":
    main()
