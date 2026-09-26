# -*- coding: utf-8 -*-
"""Crawler trắc nghiệm kenhgiaovien.com (CÓ nhãn NB/TH/VD/VDC) — Lý 9 và Sử 9.

Nguồn (server-render, SGK cũ): kenhgiaovien.com/tai-lieu/trac-nghiem-vat-li-9
  - ~53 bài (bài 1..62), mỗi bài chia 4 phần: NHẬN BIẾT / THÔNG HIỂU /
    VẬN DỤNG / VẬN DỤNG CAO -> đây là NHÃN ĐỘ KHÓ theo ma trận (phương án c).
  - KHÔNG có đáp án đúng trong trang -> "correct" để null; bước sau xác định
    đáp án bằng LLM (đáp án vật lí là khách quan, LLM làm đáng tin cậy).

Output: subjects/physics/samples/mcq_kenhgiaovien.json

Usage:
    python tools/crawl/crawl_kenhgiaovien.py --limit 2   # thử 2 bài
    python tools/crawl/crawl_kenhgiaovien.py             # full
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[2]

# Cùng một cấu trúc trang cho nhiều môn: mỗi bài chia 4 phần NB/TH/VD/VDC.
SUBJECTS = {
    "physics": {"index": "https://kenhgiaovien.com/tai-lieu/trac-nghiem-vat-li-9",
                "slug": "trac-nghiem-vat-li-9-bai-", "id": "kgv"},
    "history": {"index": "https://kenhgiaovien.com/tai-lieu/trac-nghiem-lich-su-9",
                "slug": "trac-nghiem-lich-su-9-bai-", "id": "kgv_su"},
}

LEVEL_MAP = {
    "NHẬN BIẾT": ("NB", "Nhận biết"),
    "THÔNG HIỂU": ("TH", "Thông hiểu"),
    "VẬN DỤNG CAO": ("VDC", "Vận dụng cao"),
    "VẬN DỤNG": ("VD", "Vận dụng"),
}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"}


def clean(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get(url: str) -> str | None:
    try:
        r = requests.get(url, headers=UA, timeout=40)
    except requests.RequestException:
        return None
    return r.text if r.status_code == 200 else None


def parse_lesson(html: str) -> list:
    """Trả danh sách {stem, options:[str x4], level, level_vn, has_image}.

    Xử lý 2 định dạng khác nhau giữa các bài trên kenhgiaovien:
      - Options gắn nhãn:  <p>Câu N: ...</p><p>A. ...</p><p>B. ...</p>...
      - Options danh sách: <p>Câu N: ...</p><ol><li>...</li>...</ol>
    Tiêu đề phần (mức độ) có thể là <h3> hoặc <h4>, dạng "PHẦN 1. NHẬN BIẾT"
    hoặc "1. NHẬN BIẾT".
    """
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="than_bai") or soup
    out, cur, level = [], None, ("NB", "Nhận biết")
    for el in content.find_all(["h2", "h3", "h4", "h5", "p", "ol"]):
        if el.name in ("h2", "h3", "h4", "h5"):
            # Tiêu đề mức độ rất không nhất quán giữa các bài ("PHẦN 1.",
            # "PHẦN 1:", "1.", "PHẦN I.", "THÔNG DỤNG" = "THÔNG HIỂU"...) ->
            # chỉ cần bắt TỪ KHOÁ mức độ trong tiêu đề, không cần match số phần.
            t = clean(el.get_text(" ")).upper()
            if "VẬN DỤNG CAO" in t or "VAN DUNG CAO" in t:
                level = LEVEL_MAP["VẬN DỤNG CAO"]
            elif "NHẬN BIẾT" in t or "NHAN BIET" in t:
                level = LEVEL_MAP["NHẬN BIẾT"]
            elif "THÔNG HIỂU" in t or "THONG HIEU" in t or "THÔNG DỤNG" in t or "THONG DUNG" in t:
                level = LEVEL_MAP["THÔNG HIỂU"]
            elif "VẬN DỤNG" in t or "VAN DUNG" in t:
                level = LEVEL_MAP["VẬN DỤNG"]
            continue
        if el.name == "ol":
            if cur is not None:
                opts = [clean(li.get_text(" ")) for li in el.find_all("li")]
                if len(opts) == 4:
                    cur["options"] = opts
                    cur["has_image"] = cur["has_image"] or bool(el.find("img"))
            continue
        # <p>
        has_img = bool(el.find("img") or el.find("v:shape") or el.find("v:shapetype"))
        text = clean(el.get_text(" "))
        if not text:
            continue
        qm = re.match(r"^Câu\s+(\d+):?\s*(.*)$", text, re.S)
        om = re.match(r"^([ABCD])[\.:\)]\s*(.*)$", text, re.S)
        if qm:
            if cur is not None and len(cur["options"]) == 4 and not cur["has_image"]:
                out.append(cur)
            cur = {"stem": qm.group(2), "options": [], "level": level[0],
                   "level_vn": level[1], "has_image": has_img}
        elif om and cur is not None:
            cur["options"].append(om.group(2))
            cur["has_image"] = cur["has_image"] or has_img
        elif cur is not None:
            if not cur["options"]:
                cur["stem"] += " " + text
                cur["has_image"] = cur["has_image"] or has_img
            else:
                cur["options"][-1] += " " + text
                cur["has_image"] = cur["has_image"] or has_img
    if cur is not None and len(cur["options"]) == 4 and not cur["has_image"]:
        out.append(cur)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Crawler trắc nghiệm kenhgiaovien")
    ap.add_argument("--limit", type=int, default=0, help="chỉ crawl N bài đầu")
    ap.add_argument("--subject", default="physics", choices=sorted(SUBJECTS))
    ap.add_argument("--delay", type=float, default=1.0, help="giây nghỉ giữa 2 bài")
    args = ap.parse_args()
    cfg = SUBJECTS[args.subject]
    INDEX_URL = cfg["index"]
    OUT_PATH = (REPO_ROOT / "subjects" / args.subject / "samples"
                / "mcq_kenhgiaovien.json")

    idx_html = get(INDEX_URL)
    if idx_html is None:
        sys.exit("✗ Không tải được trang index")
    idx_soup = BeautifulSoup(idx_html, "html.parser")
    urls, seen = [], set()
    for a in idx_soup.find_all("a", href=True):
        href = urljoin(INDEX_URL, a["href"])
        href = href.split("#")[0]
        if re.search(cfg["slug"] + r"\d+", href) and href not in seen:
            seen.add(href)
            urls.append(href)
    if args.limit:
        urls = urls[: args.limit]
    print(f"== {len(urls)} bài tìm thấy, bắt đầu crawl ...")

    questions, fails = [], 0
    for i, u in enumerate(urls, 1):
        if i > 1 and args.delay:
            time.sleep(args.delay)
        html = get(u)
        if html is None:
            fails += 1
            print(f"[{i}/{len(urls)}] FAILED {u}")
            continue
        items = parse_lesson(html)
        for q in items:
            questions.append({
                "id": f'{cfg["id"]}_{len(questions) + 1:04d}',
                "stem": q["stem"],
                "correct": None,
                "distractors": [],
                "options": list(q["options"]),
                "option_letters": ["A", "B", "C", "D"],
                "difficulty": q["level"],
                "difficulty_vn": q["level_vn"],
                "label_source": "kenhgiaovien",
                "source": f"kenhgiaovien.com — {Path(u).name}",
                "source_url": u,
                "notes": None,
                "label_rationale": None,
            })
        print(f"[{i}/{len(urls)}] +{len(items):3d} câu (tổng {len(questions):5d}) | "
              f"{Path(u).name[:50]}")

    OUT_PATH.write_text(json.dumps(questions, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"\n===== XONG =====\nTổng câu: {len(questions)} | Bài lỗi: {fails}")
    from collections import Counter
    print("Theo mức độ:", dict(Counter(q["difficulty"] for q in questions)))
    print(f"Đã ghi -> {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
