# -*- coding: utf-8 -*-
"""Crawler trắc nghiệm Vật Lí 9 từ VietJack -> subjects/physics/samples/mcq_crawled.json.

Tái dùng các hàm parse HTML tổng quát từ crawl_vietjack.py (crawler Lịch Sử).
Vật Lí 9 chương trình mới nằm trong môn "Khoa học tự nhiên 9" (KHTN), nên các
trang mục lục trộn lẫn chủ đề Vật Lí + Hoá + Sinh; ta chỉ giữ Vật Lí bằng bộ lọc
từ khóa chủ đề trên slug bài viết.

Nguồn (đều vietjack.com, server-render, không cần JS):
  - vat-ly-lop-9/trac-nghiem-vat-ly-9.jsp                      (600+ câu tổng hợp)
  - khoa-hoc-tu-nhien-9-{kn,cd,ct}/trac-nghiem-vat-li-9-*.jsp  (3 bộ sách mới)

Usage:
    python tools/crawl/crawl_vietjack_ly.py              # crawl đầy đủ
    python tools/crawl/crawl_vietjack_ly.py --limit-de 2 # thử 2 trang/bộ
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.crawl.crawl_vietjack import Fetcher, parse_article, dedupe_key  # noqa: E402

OUT_PATH = REPO_ROOT / "subjects" / "physics" / "samples" / "mcq_crawled.json"

INDEX_URLS = [
    ("SGK cu", "https://vietjack.com/vat-ly-lop-9/trac-nghiem-vat-ly-9.jsp"),
    ("KNTT", "https://vietjack.com/khoa-hoc-tu-nhien-9-kn/trac-nghiem-vat-li-9-ket-noi.jsp"),
    ("CD", "https://vietjack.com/khoa-hoc-tu-nhien-9-cd/trac-nghiem-vat-li-9-canh-dieu.jsp"),
    ("CTST", "https://vietjack.com/khoa-hoc-tu-nhien-9-ct/trac-nghiem-vat-li-9-chan-troi.jsp"),
]

# Chỉ lấy trang BÀI (chứa câu hỏi); bỏ trang CHƯƠNG (mục lục, không có câu parse được).
ARTICLE_RE = re.compile(r"/trac-nghiem-bai-\d+-[a-z0-9-]+\.jsp$")

# Chủ đề VẬT LÍ lớp 9 (allowlist) — KHTN 9 là môn tích hợp nên mục lục trộn
# cả Hoá (kim loại, alcohol, glucose...) và Sinh (gene, nhiễm sắc thể...).
# Allowlist an toàn hơn blocklist vì chủ đề Vật Lí là tập hữu hạn.
PHYSICS_ALLOW = re.compile(
    r"cong-suat|co-nang|dong-nang|the-nang|khuc-xa|phan-xa|lang-kinh"
    r"|thau-kinh|kinh-lup|tan-sac|mau-sac|anh-sang|dien-tro|ohm"
    r"|doan-mach|noi-tiep|song-song|cam-ung|dong-dien|nang-luong"
    r"|tai-tao|tieu-cu|co-hoc", re.IGNORECASE,
)


def get_article_urls(fetcher: Fetcher, index_url: str) -> list:
    html = fetcher.get(index_url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    urls, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = urljoin(index_url, a["href"])
        if not ARTICLE_RE.search(href) or href in seen:
            continue
        seen.add(href)
        # Lọc theo SLUG (không phải full URL). Allowlist: chỉ giữ chủ đề Vật Lí.
        slug = href.rsplit("/", 1)[-1]
        if not PHYSICS_ALLOW.search(slug):
            continue
        urls.append(href)
    return urls


def main() -> None:
    ap = argparse.ArgumentParser(description="Crawler trắc nghiệm Vật Lí 9 (VietJack)")
    ap.add_argument("--limit-de", type=int, default=0,
                    help="chỉ crawl N trang đầu mỗi nguồn (thử nghiệm)")
    args = ap.parse_args()

    fetcher = Fetcher()
    stats = {"pages_ok": 0, "pages_failed": 0, "raw": 0, "dupes": 0,
             "skip_not4": 0, "skip_noans": 0, "skip_other": 0, "by_book": {}}
    questions, seen_keys = [], set()

    plan = []
    for book, index in INDEX_URLS:
        if fetcher.blocked:
            break
        urls = get_article_urls(fetcher, index)
        if args.limit_de:
            urls = urls[:args.limit_de]
        print(f"== {book}: {len(urls)} trang bài (vật lí, đã lọc bỏ hoá/sinh)")
        plan += [(book, u) for u in urls]

    print(f"== Tổng {len(plan)} trang cần crawl\n")
    for i, (book, url) in enumerate(plan, 1):
        if fetcher.blocked:
            print("!! Site chặn — dừng, xuất phần đã crawl được.")
            break
        html = fetcher.get(url)
        if html is None:
            stats["pages_failed"] += 1
            print(f"[{i}/{len(plan)}] FAILED {url[:80]}")
            continue
        items = parse_article(html, url, stats, "vietjack.com")
        stats["pages_ok"] += 1
        stats["raw"] += len(items)
        added = 0
        for q in items:
            key = dedupe_key(q["stem"], q["correct"], q["distractors"])
            if key in seen_keys:
                stats["dupes"] += 1
                continue
            seen_keys.add(key)
            questions.append({
                "id": f"ly9_vj_{len(questions) + 1:04d}",
                "stem": q["stem"], "correct": q["correct"],
                "distractors": q["distractors"], "difficulty": None,
                "difficulty_vn": None, "label_source": None,
                "source": q["source"], "source_url": q["source_url"],
                "notes": q["notes"], "label_rationale": None,
            })
            stats["by_book"][book] = stats["by_book"].get(book, 0) + 1
            added += 1
        print(f"[{i}/{len(plan)}] {book:6s} +{added:3d} (raw {len(items):3d}) "
              f"tổng {len(questions):5d} | {url.split('/')[-1][:55]}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n===== KẾT QUẢ =====")
    print(f"Trang OK / lỗi         : {stats['pages_ok']} / {stats['pages_failed']}")
    print(f"Câu parse thô          : {stats['raw']}")
    print(f"Giữ (sau khử trùng)    : {len(questions)}")
    print(f"Trùng lặp bỏ           : {stats['dupes']}")
    print(f"Loại - thiếu/thừa lựa chọn : {stats['skip_not4']}")
    print(f"Loại - không đáp án    : {stats['skip_noans']}")
    print(f"Loại - dạng khác (ảnh) : {stats['skip_other']}")
    print("Theo nguồn:", json.dumps(stats["by_book"], ensure_ascii=False))
    print(f"Đã ghi -> {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
