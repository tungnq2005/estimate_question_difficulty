# -*- coding: utf-8 -*-
"""Crawler trắc nghiệm Lịch Sử 9 từ họ site VietJack -> staging JSON.

Nguồn crawl (đều server-render, không cần JS):

1. SGK CŨ (34 bài) — vietjack.me:
   a. Trang article "TOP 40 câu Trắc nghiệm ... Bài N" (``...-NNNNN.html``),
      URL lấy động từ mục lục
      ``/trac-nghiem-lop-9/trac-nghiem-lich-su-lop-9-co-dap-an``.
      Cấu trúc phẳng: ``<p>Câu N. stem</p>`` + 4 ``<p>A./B./C./D.</p>`` +
      ``<section class="vj-template-answer">`` ("Đáp án: X" + Giải thích).
   b. Trang quiz ``/kiem-tra-thi-thu/...`` (34 URL nhúng sẵn bên dưới, từ
      ``origin/training-model:output/lich_su.csv``): ``div.quiz-answer-item``
      > ``div.title-question`` + ``div.answers label`` + ``div.reason``
      ("Đáp án đúng là: X" + giải thích từng phương án).

2. 3 BỘ SGK MỚI (KNTT/CTST/CD):
   a. vietjack.com — trang bài/chương ``.jsp`` (URL lấy động từ 3 mục lục
      ``lich-su-9-{kn,ct,cd}/trac-nghiem-lich-su-lop-9-*.jsp``): cấu trúc
      phẳng như 1a nhưng đáp án nằm trong ``<section class="toggle">``
      ("Đáp án đúng là: X"). ~15-16 câu/bài, đáp án hiện đủ.
   b. khoahoc.vietjack.com — mục lục
      ``/trac-nghiem/Lop-9/mon-Lich-su?type=test&book={1,2,3}`` liệt kê
      ~120 đề/bộ "15 câu trắc nghiệm ... Bài N (Phần M)". Trang đề
      ``/thi-online/`` render đủ câu hỏi nhưng CHỈ ~6 câu đầu có đáp án
      (``div.option-choices`` với ``data-answer="Y"``); các câu sau
      data-answer rỗng (khóa sau tường VIP/API làm bài) -> đếm riêng
      ``hidden_ans``, không cố lách.

Chỉ giữ câu đủ 4 lựa chọn text + đúng 1 đáp án đúng; bỏ câu Đúng-Sai
nhiều ý, câu kèm hình ảnh. Khử trùng lặp nội bộ theo khóa bỏ dấu +
lowercase (stem + 4 đáp án đã sort) — cùng cách với ``parse_legacy_su.py``.

Đầu ra (STAGING — không đụng ``mcq_crawled.json``/``mcq_samples.json``):
    ``subjects/history/samples/mcq_crawled_vietjack_new.json``

Usage:
    python tools/crawl/crawl_vietjack.py                 # crawl đầy đủ
    python tools/crawl/crawl_vietjack.py --limit-de 2    # thử mỗi nguồn 2 trang
"""
import argparse
import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

try:  # certs hệ thống Windows (uv-python thiếu CA bundle mặc định)
    import truststore

    truststore.inject_into_ssl()
except ImportError:
    pass

import requests
from bs4 import BeautifulSoup, Tag

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "subjects" / "history" / "samples" / "mcq_crawled_vietjack_new.json"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 "
    "(nckh-mcq-research; polite sequential crawler)"
)
HEADERS = {"User-Agent": UA, "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8"}
DELAY_S = 1.8          # nghỉ giữa các request
RETRIES = 3            # số lần thử lại khi lỗi mạng/5xx
BACKOFF_S = 5.0        # chờ thêm mỗi lần retry
BLOCK_LIMIT = 3        # 403/429 liên tiếp -> dừng crawl, xuất phần đã có

OLD_INDEX_URL = "https://vietjack.me/trac-nghiem-lop-9/trac-nghiem-lich-su-lop-9-co-dap-an"

# 34 URL quiz SGK cũ — nguyên trạng từ origin/training-model:output/lich_su.csv
OLD_QUIZ_URLS = [
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-1-co-dap-an-lien-xo-va-cac-nuoc-dong-au-tu-1945-den-giua-nhung-nam-70-cua",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-2-co-dap-an-lien-xo-va-cac-nuoc-dong-au-tu-giua-nhung-nam-70-den-dau-nhung",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-3-co-dap-an-qua-trinh-phat-trien-cua-phong-trao-giai-phong-dan-toc-va-su-t",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-4-co-dap-an-cac-nuoc-chau-a",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-5-co-dap-an-cac-nuoc-dong-nam-a",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-6-co-dap-an-cac-nuoc-chau-phi",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-7-co-dap-an-cac-nuoc-my-latinh",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-8-co-dap-an-nuoc-mi",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-9-co-dap-an-nhat-ban",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-10-co-dap-an-cac-nuoc-tay-au",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-11-co-dap-an-trat-tu-the-gioi-moi-sau-chien-tranh-the-gioi-thu-2",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-12-co-dap-an-nhung-thanh-tuu-chu-yeu-va-y-nghia-lich-su-cua-cuoc-cach-mang",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-13-co-dap-an-tong-ket-lich-su-the-gioi-tu-sau-nam-1945-den-nay",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-14-co-dap-an-viet-nam-sau-chien-tranh-the-gioi-thu-nhat",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-15-co-dap-an-phong-trao-cach-mang-viet-nam-sau-chien-tranh-the-gioi-thu-nh",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-16-co-dap-an-hoat-dong-cua-nguyen-ai-quoc-o-nuoc-ngoai-nhung-nam-1919-1925",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-17-co-dap-an-cach-mang-viet-nam-truoc-khi-dang-cong-san-ra-doi",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-18-co-dap-an-dang-cong-san-viet-nam-ra-doi",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-19-co-dap-an-phong-trao-cach-mang-nhung-nam-1930-1935",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-20-co-dap-an-cuoc-van-dong-dan-chu-trong-nhung-nam-1936-1939",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-21-co-dap-an-viet-nam-trong-nhung-nam-1939-1945",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-22-co-dap-an-cao-trao-cach-mang-tien-toi-tong-khoi-nghia-thang-8-nam-1945",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-23-co-dap-an-tong-khoi-nghia-thang-8-nam-1945-va-su-thanh-lap-nuoc",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-24-co-dap-an-cuoc-dau-tranh-bao-ve-va-xay-dung-chinh-quyen-dan-chu-nhan-da",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-25-co-dap-an-nhung-nam-dau-cua-cuoc-khang-chien-toan-quoc-chong-thuc-dan-p",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-26-co-dap-an-buoc-phat-trien-moi-cua-cuoc-khang-chien-toan-quoc-chong-thuc",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-27-co-dap-an-cuoc-khang-chien-toan-quoc-chong-thuc-dan-phap-ket-thuc-1953",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-28-co-dap-an-xay-dung-xa-hoi-chu-nghia-o-mien-bac-dau-tranh-chong-de-quoc",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-29-co-dap-an-ca-nuoc-truc-tiep-chien-dau-chong-mi-cuu-nuoc-1965-1973",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-30co-dap-an-hoan-thanh-giai-phong-mien-nam-thong-nhat-dat-nuoc-1973-1975",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-31-co-dap-an-viet-nam-trong-nhung-nam-dau-sau-dai-thang-mua-xuan-1975",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-32-co-dap-an-xay-dung-dat-nuoc-dau-tranh-bao-ve-to-quoc-1976-1985",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-33-co-dap-an-viet-nam-tren-duong-doi-moi-di-len-xa-hoi-chu-nghia",
    "https://vietjack.me/kiem-tra-thi-thu/trac-nghiem-lich-su-9-bai-34-co-dap-an-tong-ket-lich-su-viet-nam-tu-sau-chien-tranh-the-gioi-thu-nha",
]

# (mã bộ sách, tham số book trên khoahoc, mục lục trắc nghiệm trên vietjack.com)
NEW_BOOKS = [
    ("KNTT", 1, "https://www.vietjack.com/lich-su-9-kn/trac-nghiem-lich-su-lop-9-ket-noi.jsp"),
    ("CD", 2, "https://www.vietjack.com/lich-su-9-cd/trac-nghiem-lich-su-lop-9-canh-dieu.jsp"),
    ("CTST", 3, "https://www.vietjack.com/lich-su-9-ct/trac-nghiem-lich-su-lop-9-chan-troi.jsp"),
]
KHOAHOC_LIST_URL = "https://khoahoc.vietjack.com/trac-nghiem/Lop-9/mon-Lich-su?type=test&book={book}"

OPTION_RE = re.compile(r"^\s*([A-D])\s*[.:)]\s*(.+)$", re.DOTALL)
CAU_RE = re.compile(r"^\s*Câu\s*([\d\s]{1,6})\s*[.:]\s*(.*)$", re.DOTALL)
ANSWER_RE = re.compile(
    r"Đáp án(?:\s*đúng)?(?:\s*(?:là|cần chọn là))?\s*[:：]?\s*([A-D])\b",
    re.IGNORECASE,
)
# Câu dạng Đúng-Sai nhiều ý (chương trình 2025) — không phải MCQ 4 lựa chọn
TRUE_FALSE_HINT = re.compile(r"mỗi ý\s*a\)|đúng hay sai|trong mỗi ý sau", re.IGNORECASE)


# ---------------------------------------------------------------- helpers --
def clean_text(s: str) -> str:
    s = s.replace("\xa0", " ").replace("​", "")
    return re.sub(r"\s+", " ", s).strip()


def norm_key(text: str) -> str:
    """Khóa so trùng: bỏ dấu, thường hóa, gộp khoảng trắng (khớp parse_legacy_su)."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "d").lower()
    return re.sub(r"\s+", " ", text).strip()


def dedupe_key(stem: str, correct: str, distractors: list) -> str:
    opts = sorted(norm_key(o) for o in [correct, *distractors])
    return norm_key(stem) + "||" + "|".join(opts)


def is_heading_para(text: str) -> bool:
    """Heading mục lạc vào stem ("I. CÂU HỎI TRẮC NGHIỆM NHIỀU LỰA CHỌN"...)."""
    t = clean_text(text)
    if not t:
        return True
    if len(t) <= 90 and t == t.upper() and re.search(r"[A-ZĐÂẤẦÊỆỌỎƯỨ]", t):
        return True
    return bool(re.match(r"^(phần|dạng)\s*[ivx\d]+\b", t, re.IGNORECASE)
                and re.search(r"trắc nghiệm|lựa chọn|đúng\s*.?\s*sai", t, re.IGNORECASE))


def strip_option_prefix(text: str) -> tuple:
    """"A. Nội dung" -> ("A", "Nội dung"); trả (None, text) nếu không có."""
    m = OPTION_RE.match(text)
    if m:
        return m.group(1), clean_text(m.group(2))
    return None, clean_text(text)


class Fetcher:
    """requests.Session + delay lịch sự + retry nhẹ + phát hiện bị chặn."""

    def __init__(self):
        self.sess = requests.Session()
        self.sess.headers.update(HEADERS)
        self.consecutive_blocks = 0
        self.blocked = False
        self.n_requests = 0

    def get(self, url: str):
        """Trả về text HTML hoặc None (lỗi). Đặt self.blocked nếu site chặn."""
        if self.blocked:
            return None
        for attempt in range(1, RETRIES + 1):
            if self.n_requests:
                time.sleep(DELAY_S)
            self.n_requests += 1
            try:
                r = self.sess.get(url, timeout=45)
            except requests.RequestException as e:
                print(f"    ! lỗi mạng ({type(e).__name__}) lần {attempt}/{RETRIES}")
                time.sleep(BACKOFF_S * attempt)
                continue
            if r.status_code in (403, 429):
                self.consecutive_blocks += 1
                print(f"    ! HTTP {r.status_code} (chặn?) — {self.consecutive_blocks}/{BLOCK_LIMIT}")
                if self.consecutive_blocks >= BLOCK_LIMIT:
                    self.blocked = True
                    return None
                time.sleep(BACKOFF_S * attempt * 2)
                continue
            if r.status_code >= 500:
                print(f"    ! HTTP {r.status_code} lần {attempt}/{RETRIES}")
                time.sleep(BACKOFF_S * attempt)
                continue
            if r.status_code != 200:
                print(f"    ! HTTP {r.status_code} — bỏ trang")
                return None
            self.consecutive_blocks = 0
            return r.text
        return None


# ------------------------------------------------- parser 1: khoahoc đề --
def parse_khoahoc_de(html: str, url: str, de_title: str, stats: dict) -> list:
    """Trang /thi-online/ trên khoahoc.vietjack.com (data-answer=Y/N)."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for item in soup.select("div.quiz-answer-item"):
        tq = item.select_one(".title-question")
        opts_el = item.select("div.option-choices")
        if tq is None or not opts_el:
            continue
        flags = [(oc.get("data-answer") or "").strip().upper() for oc in opts_el]
        if all(f == "" for f in flags):      # đáp án bị khóa (ngoài 6 câu đầu)
            stats["hidden_ans"] += 1
            continue
        if len(opts_el) != 4:
            stats["skip_not4"] += 1
            continue
        if flags.count("Y") != 1:
            stats["skip_noans"] += 1
            continue
        if tq.find("img") or any(oc.find("img") for oc in opts_el):
            stats["skip_other"] += 1
            continue
        # stem: bỏ các đoạn heading mục ("I. CÂU HỎI TRẮC NGHIỆM ...")
        paras = [clean_text(p.get_text(" ", strip=True)) for p in tq.find_all("p")]
        paras = [p for p in paras if p]
        if not paras:
            paras = [clean_text(tq.get_text(" ", strip=True))]
        stem = clean_text(" ".join(p for p in paras if not is_heading_para(p)))
        stem = re.sub(r"^Câu\s*[\d\s]{1,6}\s*[.:]\s*", "", stem)
        if not stem or TRUE_FALSE_HINT.search(stem):
            stats["skip_other"] += 1
            continue
        options = [strip_option_prefix(clean_text(oc.get_text(" ", strip=True)))[1]
                   for oc in opts_el]
        if any(not o for o in options):
            stats["skip_other"] += 1
            continue
        correct = options[flags.index("Y")]
        distractors = [o for i, o in enumerate(options) if flags[i] != "Y"]
        out.append({
            "stem": stem, "correct": correct, "distractors": distractors,
            "source": f"khoahoc.vietjack.com — {de_title}",
            "source_url": url, "notes": None,
        })
    return out


# --------------------------------------- parser 2: vietjack.me quiz page --
def _reason_to_note(reason_el: Tag) -> tuple:
    """Trả (đáp án 'A'-'D' | None, giải thích | None) từ div.reason."""
    # tách bản sao riêng: decompose/find_all_next bên dưới phải bị chặn
    # trong phạm vi reason, không được lan ra cả trang (soup dùng chung)
    reason_el = BeautifulSoup(str(reason_el), "html.parser")
    # cắt phần "Xem thêm ..." trở đi (liên kết dẫn bài khác)
    for s in reason_el.find_all(string=re.compile(r"Xem thêm", re.IGNORECASE)):
        parent = s.find_parent()
        if parent is None:
            continue
        for el in list(parent.find_all_next()):
            if isinstance(el, Tag):
                el.decompose()
        parent.decompose()
    text = clean_text(reason_el.get_text(" ", strip=True))
    text = re.sub(r"^Xem đáp án\s*", "", text, flags=re.IGNORECASE)
    m = ANSWER_RE.search(text)
    if not m:
        return None, None
    correct = m.group(1).upper()
    note = ANSWER_RE.sub("", text, count=1)
    note = re.sub(r"^\s*(Giải thích\s*[:：]?)\s*", "", note, flags=re.IGNORECASE)
    note = clean_text(note) or None
    return correct, note


def parse_me_quiz(html: str, url: str, stats: dict) -> list:
    """Trang /kiem-tra-thi-thu/ trên vietjack.me (div.quiz-answer-item)."""
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.find("title")
    page_title = clean_text(title_el.get_text()) if title_el else url
    page_title = re.sub(r"^\d+ câu hỏi trắc nghiệm thuộc\s*", "", page_title)
    out = []
    for item in soup.select("div.quiz-answer-item"):
        tq = item.select_one("div.title-question")
        labels = item.select("div.answers label")
        reason = item.select_one("div.reason")
        if tq is None or not labels:
            continue
        if tq.find("img") or any(lb.find("img") for lb in labels):
            stats["skip_other"] += 1
            continue
        stem = clean_text(tq.get_text(" ", strip=True))
        stem = re.sub(r"^Câu\s*[\d\s]{1,6}\s*[.:]\s*", "", stem)
        if not stem or TRUE_FALSE_HINT.search(stem):
            stats["skip_other"] += 1
            continue
        options = []
        for lb in labels:
            letter, text = strip_option_prefix(clean_text(lb.get_text(" ", strip=True)))
            if text:
                options.append((letter, text))
        if len(options) != 4:
            stats["skip_not4"] += 1
            continue
        correct_letter, note = _reason_to_note(reason) if reason else (None, None)
        if correct_letter is None:
            stats["skip_noans"] += 1
            continue
        letters = [l for l, _ in options]
        if letters == [None] * 4:  # không có tiền tố A-D -> theo thứ tự trang
            letters = ["A", "B", "C", "D"]
        if correct_letter not in letters:
            stats["skip_noans"] += 1
            continue
        texts = [t for _, t in options]
        idx = letters.index(correct_letter)
        out.append({
            "stem": stem,
            "correct": texts[idx],
            "distractors": [t for i, t in enumerate(texts) if i != idx],
            "source": f"vietjack.me — {page_title}",
            "source_url": url,
            "notes": note,
        })
    return out


# --------------------- parser 3: trang article phẳng (me .html / com .jsp) --
def parse_article(html: str, url: str, stats: dict, site: str) -> list:
    """Trang article: p "Câu N." + 4 p "A-D." + section đáp án.

    Dùng cho vietjack.me (``div#content-post``, ``section.vj-template-answer``)
    và vietjack.com (``div.middle-col``, ``section.toggle``).
    """
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.find("title")
    page_title = clean_text(title_el.get_text()) if title_el else url
    body = (soup.select_one("div#content-post") or soup.select_one("div.detail-body")
            or soup.select_one("div.middle-col"))
    if body is None:
        stats["pages_failed"] += 1
        return []
    out = []
    cur_stem, cur_opts, cur_img = None, [], False

    def flush(section_el):
        nonlocal cur_stem, cur_opts, cur_img
        if cur_stem is None:
            return
        stem, opts, has_img = cur_stem, cur_opts, cur_img
        cur_stem, cur_opts, cur_img = None, [], False
        if TRUE_FALSE_HINT.search(stem) or has_img or not stem:
            stats["skip_other"] += 1
            return
        if len(opts) != 4:
            stats["skip_not4"] += 1
            return
        if section_el is None:
            stats["skip_noans"] += 1
            return
        sec_text = clean_text(section_el.get_text(" ", strip=True))
        m = ANSWER_RE.search(sec_text)
        if not m:
            stats["skip_noans"] += 1
            return
        correct_letter = m.group(1).upper()
        letters = [l for l, _ in opts]
        if correct_letter not in letters:
            stats["skip_noans"] += 1
            return
        note = ANSWER_RE.sub("", sec_text, count=1)
        note = re.sub(r"^\s*Hiển thị đáp án\s*", "", note, flags=re.IGNORECASE)
        note = re.sub(r"^\s*(Giải thích\s*[:：]?)\s*", "", note, flags=re.IGNORECASE)
        note = re.sub(r"Xem thêm (câu hỏi trắc nghiệm|các bài).*$", "", note,
                      flags=re.IGNORECASE)
        note = clean_text(note) or None
        texts = [t for _, t in opts]
        idx = letters.index(correct_letter)
        out.append({
            "stem": stem,
            "correct": texts[idx],
            "distractors": [t for i, t in enumerate(texts) if i != idx],
            "source": f"{site} — {page_title}",
            "source_url": url,
            "notes": note,
        })

    for el in body.descendants:
        if not isinstance(el, Tag):
            continue
        if el.name == "section":
            cls = el.get("class") or []
            if "vj-template-answer" in cls or "toggle" in cls:
                flush(el)
            continue
        if el.name != "p" or el.find_parent("section") is not None:
            continue
        text = clean_text(el.get_text(" ", strip=True))
        if not text:
            continue
        m = CAU_RE.match(text)
        if m:
            if cur_stem is not None:  # câu trước không gặp section đáp án
                flush(None)
            cur_stem = clean_text(m.group(2))
            cur_opts, cur_img = [], bool(el.find("img"))
            continue
        letter, opt_text = strip_option_prefix(text)
        if letter and cur_stem is not None:
            if len(cur_opts) < 4:
                cur_opts.append((letter, opt_text))
                cur_img = cur_img or bool(el.find("img"))
            continue
        # đoạn nối tiếp stem (trước khi có lựa chọn); bỏ đoạn quảng cáo
        if (cur_stem is not None and not cur_opts
                and not re.match(r"^(Quảng cáo|Săn SALE|Xem thêm)", text, re.IGNORECASE)):
            cur_stem = clean_text(cur_stem + " " + text)
            cur_img = cur_img or bool(el.find("img"))
    flush(None)
    return out


# ------------------------------------------------------------- pipelines --
def get_old_article_urls(fetcher: Fetcher) -> list:
    """Danh sách trang article bài 1-34 SGK cũ, từ trang mục lục."""
    html = fetcher.get(OLD_INDEX_URL)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    tc = soup.select_one("div.tablecontent")
    if tc is None:
        return []
    urls, seen = [], set()
    for a in tc.find_all("a", href=True):
        href = urljoin(OLD_INDEX_URL, a["href"])
        if re.search(r"/trac-nghiem-lich-su-9-bai-\d+.*\.html$", href) and href not in seen:
            seen.add(href)
            urls.append(href)
    return urls


def get_vjcom_urls(fetcher: Fetcher, index_url: str) -> list:
    """Danh sách trang trắc nghiệm bài/chương .jsp của 1 bộ sách mới."""
    html = fetcher.get(index_url)
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    urls, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = urljoin(index_url, a["href"])
        if (re.search(r"/trac-nghiem-(bai|chuong)-[a-z0-9-]*\.jsp$", href)
                and href.startswith("https://www.vietjack.com/lich-su-9-")
                and href not in seen):
            seen.add(href)
            urls.append(href)
    return urls


def get_khoahoc_de_urls(fetcher: Fetcher, book: int) -> list:
    """[(url, tiêu đề đề)] các đề bài-level của 1 bộ sách mới trên khoahoc."""
    html = fetcher.get(KHOAHOC_LIST_URL.format(book=book))
    if html is None:
        return []
    soup = BeautifulSoup(html, "html.parser")
    des, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/thi-online/" not in href or "trac-nghiem-lich-su-9" not in href:
            continue
        if href in seen:
            continue
        seen.add(href)
        title = clean_text(re.sub(r"^\s*\d+\.\s*", "", a.get_text(" ", strip=True)))
        des.append((href, title))
    return des


def main() -> None:
    ap = argparse.ArgumentParser(description="Crawler trắc nghiệm Lịch Sử 9 (VietJack)")
    ap.add_argument("--limit-de", type=int, default=0,
                    help="chỉ crawl N trang đầu mỗi nguồn (thử nghiệm)")
    ap.add_argument("--skip-old", action="store_true", help="bỏ qua SGK cũ")
    ap.add_argument("--skip-new", action="store_true", help="bỏ qua 3 bộ SGK mới")
    args = ap.parse_args()

    fetcher = Fetcher()
    stats = {
        "pages_ok": 0, "pages_failed": 0,
        "raw": 0, "dupes": 0,
        "skip_not4": 0, "skip_noans": 0, "skip_other": 0, "hidden_ans": 0,
        "by_book": {"SGK cũ": 0, "KNTT": 0, "CD": 0, "CTST": 0},
        "by_kind": {},
    }
    questions, seen_keys = [], set()

    def add_all(items: list, book: str, kind: str) -> int:
        stats["raw"] += len(items)
        added = 0
        for q in items:
            key = dedupe_key(q["stem"], q["correct"], q["distractors"])
            if key in seen_keys:
                stats["dupes"] += 1
                continue
            seen_keys.add(key)
            questions.append({
                "id": f"su9_vjnew_{len(questions) + 1:04d}",
                "stem": q["stem"], "correct": q["correct"],
                "distractors": q["distractors"], "difficulty": None,
                "difficulty_vn": None, "label_source": None,
                "source": q["source"], "source_url": q["source_url"],
                "notes": q["notes"],
                "label_rationale": None,  # khớp schema mcq_crawled.json hiện tại
            })
            stats["by_book"][book] += 1
            stats["by_kind"][kind] = stats["by_kind"].get(kind, 0) + 1
            added += 1
        return added

    plan = []  # (kind, url, book_tag, extra)
    if not args.skip_old:
        print("== Mục lục SGK cũ (vietjack.me) ...")
        article_urls = get_old_article_urls(fetcher)
        print(f"   {len(article_urls)} trang article bài học")
        arts = article_urls[: args.limit_de] if args.limit_de else article_urls
        quizzes = OLD_QUIZ_URLS[: args.limit_de] if args.limit_de else OLD_QUIZ_URLS
        plan += [("me_article", u, "SGK cũ", None) for u in arts]
        plan += [("me_quiz", u, "SGK cũ", None) for u in quizzes]
    if not args.skip_new:
        for book_tag, book_no, vjcom_index in NEW_BOOKS:
            if fetcher.blocked:
                break
            print(f"== Mục lục {book_tag}: vietjack.com + khoahoc (book={book_no}) ...")
            vjcom_urls = get_vjcom_urls(fetcher, vjcom_index)
            des = get_khoahoc_de_urls(fetcher, book_no)
            print(f"   vietjack.com: {len(vjcom_urls)} trang | khoahoc: {len(des)} đề")
            if args.limit_de:
                vjcom_urls = vjcom_urls[: args.limit_de]
                des = des[: args.limit_de]
            plan += [("vjcom", u, book_tag, None) for u in vjcom_urls]
            plan += [("khoahoc", u, book_tag, t) for u, t in des]

    print(f"== Tổng cộng {len(plan)} trang cần crawl\n")
    t0 = time.time()
    for i, (kind, url, book_tag, extra) in enumerate(plan, 1):
        if fetcher.blocked:
            print("!! Site chặn liên tục — dừng, xuất phần đã crawl được.")
            break
        html = fetcher.get(url)
        if html is None:
            stats["pages_failed"] += 1
            print(f"[{i}/{len(plan)}] {kind} FAILED {url[:90]}")
            continue
        if kind == "me_article":
            items = parse_article(html, url, stats, "vietjack.me")
        elif kind == "me_quiz":
            items = parse_me_quiz(html, url, stats)
        elif kind == "vjcom":
            items = parse_article(html, url, stats, "vietjack.com")
        else:
            items = parse_khoahoc_de(html, url, extra, stats)
        stats["pages_ok"] += 1
        added = add_all(items, book_tag, kind)
        el = time.time() - t0
        print(f"[{i}/{len(plan)}] {kind:10s} {book_tag:6s} +{added:3d} (raw {len(items):3d}) "
              f"tổng {len(questions):5d} | {el:6.0f}s | {url.split('/')[-1][:65]}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("\n===== KẾT QUẢ =====")
    print(f"Trang OK / lỗi                 : {stats['pages_ok']} / {stats['pages_failed']}")
    print(f"Câu parse thô                  : {stats['raw']}")
    print(f"Giữ (sau khử trùng nội bộ)     : {len(questions)}")
    print(f"Trùng lặp bỏ                   : {stats['dupes']}")
    print(f"Loại - thiếu/thừa lựa chọn     : {stats['skip_not4']}")
    print(f"Loại - không xác định đáp án   : {stats['skip_noans']}")
    print(f"Loại - dạng khác (Đ/S, ảnh)    : {stats['skip_other']}")
    print(f"Đáp án bị khóa (khoahoc, VIP)  : {stats['hidden_ans']}")
    print("Theo bộ sách :", json.dumps(stats["by_book"], ensure_ascii=False))
    print("Theo nguồn   :", json.dumps(stats["by_kind"], ensure_ascii=False))
    print(f"Đã ghi -> {OUT_PATH.relative_to(REPO_ROOT)}")
    if fetcher.blocked:
        print("CẢNH BÁO: crawl dừng sớm do site chặn (403/429 liên tục).")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
