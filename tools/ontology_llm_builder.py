# -*- coding: utf-8 -*-
"""Bồi ontology Vật Lí 9 bằng LLM (dựa SGK) + 2-LLM chéo.

LLM-A (flash): trích thực thể (đại lượng/định luật/công thức/khái niệm/dụng cụ/
                hiện tượng/đơn vị) + cạnh tiên quyết, THEO TỪNG CHƯƠNG.
LLM-B (pro)  : kiểm chéo toàn bộ thực thể + cạnh, đánh dấu keep/remove.

Đầu ra (staging, chưa ghi vào build_data.py):
    subjects/physics/samples/llm_ontology_supplement.json

Usage:
    python tools/ontology_llm_builder.py --api-key sk-... --limit 1   # thử 1 chương
    python tools/ontology_llm_builder.py --api-key sk-...             # full + chéo
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]

BASE_URL = "https://api.deepseek.com/v1"
FLASH = "deepseek-v4-flash"
PRO = "deepseek-v4-pro"

# Chương trình SGK Vật Lí 9 (bộ cũ: điện/quang/năng lượng) + CƠ HỌC bổ sung
# (từ KHTN 9 chương trình mới — SGK cũ không có khối này).
CURRICULUM = [
    ("Điện học", [
        "Sự phụ thuộc của cường độ dòng điện vào hiệu điện thế",
        "Điện trở của dây dẫn - Định luật Ôm (U = I.R)",
        "Đoạn mạch nối tiếp, đoạn mạch song song, mạch hỗn hợp",
        "Sự phụ thuộc của điện trở vào chiều dài, tiết diện, vật liệu dây dẫn (R = ρ.L/S)",
        "Biến trở - điện trở dùng trong kỹ thuật",
        "Công suất điện (P = U.I = I².R = U²/R)",
        "Điện năng - công của dòng điện (A = P.t)",
        "Định luật Jun-Lenxơ (Q = I².R.t)",
        "Sử dụng an toàn và tiết kiệm điện",
    ]),
    ("Điện từ học", [
        "Nam châm vĩnh cửu, tác dụng từ của dòng điện, từ trường",
        "Từ phổ - đường sức từ, quy tắc bàn tay phải",
        "Lực điện từ, quy tắc bàn tay trái, động cơ điện một chiều",
        "Hiện tượng cảm ứng điện từ, điều kiện xuất hiện dòng điện cảm ứng",
        "Dòng điện xoay chiều, máy phát điện xoay chiều",
        "Truyền tải điện năng đi xa, máy biến thế (U1/U2 = N1/N2)",
    ]),
    ("Quang học", [
        "Khúc xạ ánh sáng, quan hệ góc tới - góc khúc xạ",
        "Thấu kính hội tụ, thấu kính phân kì, tiêu cự",
        "Ảnh của vật tạo bởi thấu kính (1/f = 1/d + 1/d')",
        "Máy ảnh, mắt, mắt cận, mắt lão, kính lúp",
        "Ánh sáng trắng và ánh sáng màu, tán sắc ánh sáng, màu sắc các vật",
    ]),
    ("Bảo toàn và chuyển hóa năng lượng", [
        "Năng lượng, các dạng năng lượng, sự chuyển hóa năng lượng",
        "Định luật bảo toàn năng lượng",
        "Sản xuất điện năng: nhiệt điện, thủy điện, điện gió, điện mặt trời, điện hạt nhân",
    ]),
    ("Cơ học (bổ sung từ KHTN 9)", [
        "Công cơ học (A = F.s), công suất (P = A/t)",
        "Cơ năng, thế năng trọng trường (Wt = m.g.h), thế năng đàn hồi",
        "Động năng (Wđ = ½.m.v²), sự chuyển hóa giữa động năng và thế năng",
    ]),
]

CLASSES = "Quantity (đại lượng) | Law (định luật) | Formula (công thức) | Concept (khái niệm) | Device (dụng cụ/thiết bị) | Phenomenon (hiện tượng) | Unit (đơn vị đo) | Method (phương pháp giải) | ProblemType (dạng bài)"

EXTRACT_SYSTEM = (
    "Bạn là chuyên gia xây dựng ontology Vật Lí lớp 9 (chương trình Việt Nam). "
    "Nhiệm vụ: từ danh sách chủ đề SGK, trích ra các THỰC THỂ và QUAN HỆ TIÊN QUYẾT "
    "để xây đồ thị tri thức phục vụ ước lượng độ khó câu hỏi.\n"
    "Chỉ trả về JSON, không thêm văn bản ngoài JSON."
)

EXTRACT_USER = (
    "Chương SGK Vật Lí 9 cần trích (kèm chủ đề):\n\n"
    "{curriculum}\n\n"
    "Hãy trích:\n"
    "1. THỰC THỂ — mỗi thực thể gồm:\n"
    "   - class: một trong các lớp sau: {classes}\n"
    "   - label: tên tiếng Việt chuẩn (viết đúng dấu).\n"
    "   - aliases: mảng các cách gọi khác (kí hiệu, tên ngắn, tên thường dùng "
    "trong đề thi). PHẢI có dạng KHÔNG DẤU (thường gặp khi crawl đề). "
    "VD: \"Dinh luat Om\" có alias [\"Ohm\", \"dinh luat Om\", \"U=I.R\"].\n"
    "   - symbol: kí hiệu đại lượng (chỉ cho Quantity/Unit; nếu không có thì bỏ trống).\n"
    "2. PREREQUISITES — danh sách cặp tiên quyết: thực thể A phải học TRƯỚC thực thể B "
    "(quan hệ \"A là tiền đề của B\"). Tham chiếu bằng chỉ số của thực thể trong mảng entities.\n\n"
    "Trả về ĐÚNG JSON theo schema:\n"
    '{{"entities": [{{"i": 0, "class": "Quantity", "label": "Cường độ dòng điện", '
    '"aliases": ["I", "cuong do dong dien"], "symbol": "I"}}], '
    '"prerequisites": [{{"a": 0, "b": 5}}]}}\n\n'
    "Phủ ĐỦ đại lượng, định luật, công thức, khái niệm, dụng cụ, đơn vị của chương."
)

CROSS_SYSTEM = (
    "Bạn là chuyên gia Vật Lí 9 kiểm định chất lượng một đồ thị tri thức vừa được "
    "sinh tự động. Nhiệm vụ: duyệt từng thực thể và từng cạnh tiên quyết, đánh dấu "
    "keep (đúng) hoặc remove (sai / trùng lặp / không phải kiến thức Vật Lí 9 / "
    "lớp sai / chiều tiên quyết sai). Chỉ trả về JSON, không thêm văn bản ngoài JSON."
)

CROSS_USER = (
    "Đồ thị tri thức sinh tự động cho Vật Lí 9:\n"
    "{entities_json}\n\n"
    "Các cạnh tiên quyết (tham chiếu theo chỉ số):\n"
    "{prereq_json}\n\n"
    "Hãy liệt kê CHỈ các thực thể và cạnh SAI (cần LOẠI BỎ) — sai lớp, trùng lặp, "
    "không phải kiến thức Vật Lí 9, hoặc chiều tiên quyết sai. "
    "Nếu tất cả đúng thì trả mảng rỗng. Trả về JSON schema:\n"
    '{{"remove_entities": [{{"i": 3, "reason": "trung lap"}}], '
    '"remove_prerequisites": [{{"idx": 5, "reason": "sai chieu"}}]}}'
)


def call(model, system, user, temperature=0.2, max_tokens=8000):
    url = f"{BASE_URL}/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        # deepseek-v4-* là model suy luận: tắt reasoning để trả JSON thẳng
        # (nhanh + không tốn token) — đúng bài học từ llm_student_sim.py.
        "thinking": {"type": "disabled"},
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=180)
        except requests.RequestException as e:
            print(f"  ! lỗi mạng ({type(e).__name__}) lần {attempt + 1}/3")
            continue
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        print(f"  ! HTTP {r.status_code}: {r.text[:200]}")
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
    # sửa lỗi JSON phổ biến của LLM: dấu phẩy thừa trước } hoặc ]
    text = re.sub(r",\s*([}\]])", r"\1", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # cắt tới kí tự "}" cuối cùng hợp lệ nếu bị cắt giữa chừng
        for cut in range(len(text), 0, -1):
            try:
                return json.loads(text[:cut] + "}")
            except json.JSONDecodeError:
                continue
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.environ.get("DEEPSEEK_API_KEY"))
    ap.add_argument("--limit", type=int, default=0, help="chỉ xử lý N chương")
    args = ap.parse_args()

    global API_KEY
    API_KEY = args.api_key
    if not API_KEY:
        sys.exit("✗ Thiếu API key (--api-key hoặc env DEEPSEEK_API_KEY)")

    chapters = CURRICULUM[: args.limit] if args.limit else CURRICULUM

    all_ents, all_pres = [], []
    for ci, (ch_name, topics) in enumerate(chapters, 1):
        ch_text = f"- {ch_name}:\n" + "\n".join(f"    + {t}" for t in topics)
        user = EXTRACT_USER.format(curriculum=ch_text, classes=CLASSES)
        print(f"== [{ci}/{len(chapters)}] LLM-A ({FLASH}): {ch_name} ...")
        raw = call(FLASH, EXTRACT_SYSTEM, user)
        if raw is None:
            print("  ! LLM-A thất bại, bỏ chương này.")
            continue
        data = parse_json(raw)
        ents = data.get("entities", [])
        pres = data.get("prerequisites", [])
        remap = {}
        for e in ents:
            new_i = len(all_ents)
            remap[e.get("i")] = new_i
            e["i"] = new_i
            all_ents.append(e)
        for p in pres:
            if p.get("a") in remap and p.get("b") in remap:
                all_pres.append({"a": remap[p["a"]], "b": remap[p["b"]]})
        print(f"   -> {len(ents)} thực thể, {len(pres)} cạnh (tổng {len(all_ents)} thực thể, "
              f"{len(all_pres)} cạnh)")

    print(f"== LLM-B ({PRO}): kiểm chéo toàn bộ {len(all_ents)} thực thể + {len(all_pres)} cạnh ...")
    raw2 = call(PRO, CROSS_SYSTEM, CROSS_USER.format(
        entities_json=json.dumps(all_ents, ensure_ascii=False),
        prereq_json=json.dumps(all_pres, ensure_ascii=False)),
        max_tokens=8000)
    if raw2 is None:
        print("  ! LLM-B thất bại — bỏ qua bước chéo, giữ toàn bộ flash.")
        rm_ent, rm_pre = set(), set()
    else:
        try:
            review = parse_json(raw2)
            rm_ent = {r["i"] for r in review.get("remove_entities", [])}
            rm_pre = {r["idx"] for r in review.get("remove_prerequisites", [])}
            # Guard: nếu pro bác > 40% là dấu hiệu nó hiểu nhầm nhiệm vụ
            # (từng xảy ra: bác toàn bộ 131 cạnh) -> bỏ qua bước chéo.
            if len(rm_ent) > 0.4 * len(all_ents) or len(rm_pre) > 0.4 * len(all_pres):
                print(f"  ! LLM-B bác quá nhiều ({len(rm_ent)}/{len(all_ents)} thực thể, "
                      f"{len(rm_pre)}/{len(all_pres)} cạnh) — coi như hiểu nhầm, giữ toàn bộ flash.")
                rm_ent, rm_pre = set(), set()
        except Exception as e:
            print(f"  ! LLM-B trả JSON lỗi ({type(e).__name__}) — bỏ qua bước chéo, giữ toàn bộ flash.")
            (REPO / "subjects" / "physics" / "samples" / "_cross_raw_debug.txt").write_text(
                raw2, encoding="utf-8")
            rm_ent, rm_pre = set(), set()
    kept_ents = [e for e in all_ents if e.get("i") not in rm_ent]
    valid_idx = {e["i"] for e in kept_ents}
    kept_pres = [p for p in all_pres if all_pres.index(p) not in rm_pre
                 and p.get("a") in valid_idx and p.get("b") in valid_idx]
    print(f"   LLM-B bác: {len(rm_ent)} thực thể, {len(rm_pre)} cạnh")
    print(f"   => GIỮ: {len(kept_ents)} thực thể, {len(kept_pres)} cạnh")

    out = {"entities": kept_ents, "prerequisites": kept_pres}
    out_path = REPO / "subjects" / "physics" / "samples" / "llm_ontology_supplement.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nĐã ghi -> {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
