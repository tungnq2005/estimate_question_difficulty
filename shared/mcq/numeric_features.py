# -*- coding: utf-8 -*-
"""Numeric-answer features cho cụm môn prereq_dag (Toán, Lý).

Đáp án dạng giá trị số ("660W", "40°", "11V") không bao giờ khớp entity KG
(không node nào có nhãn là con số), nên Block A mù với loại câu này. Khối
feature này bù lại bằng tín hiệu thuần số học + tra cứu công thức từ stem:

- Khảo sát 9 distractor số trong bộ mẫu Toán/Lý cho thấy đa số distractor
  "hiệu quả" sinh ra từ hai lỗi tính quen thuộc của học sinh:
  (1) lệch một HỆ SỐ kinh điển (x0.5 / x2 / x4 / x10 — thiếu/thừa một bước
      nhân chia, quên bình phương, nhầm tiền tố đơn vị);
  (2) ĐẢO TỬ-MẪU một tỉ số trong công thức (VD máy biến thế lấy N1/N2
      thành N2/N1 -> đáp án lệch đúng (tỉ số)^2 lần).
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List, Optional

from .ontology_bridge import Entity, OntologyEngine

# "660W", "40°", "11,5 V", "-3.2", "1/20"... — số + đơn vị ngắn tuỳ chọn
_NUMERIC_ANSWER_RE = re.compile(
    r"^\s*-?\d+(?:[.,]\d+)?\s*[a-zA-ZΩωµ°%²³/·.\s]{0,12}$")
_NUMBER_RE = re.compile(r"-?\d+(?:[.,]\d+)?")

# Hệ số "trượt tay" kinh điển: thiếu/thừa 1 bước nhân đôi, bình phương,
# nhầm tiền tố đơn vị (deci/hecto/kilo).
_CLASSIC_SLIP_RATIOS = (0.5, 2.0, 0.25, 4.0, 0.1, 10.0, 0.01, 100.0)
_REL_TOL = 0.02


def parse_numeric(text: str) -> Optional[float]:
    """Giá trị số nếu text là đáp án dạng số (kèm đơn vị ngắn), else None."""
    if not text or not _NUMERIC_ANSWER_RE.match(text.strip()):
        return None
    m = _NUMBER_RE.search(text)
    return float(m.group(0).replace(",", ".")) if m else None


def extract_numbers(text: str) -> List[float]:
    """Mọi giá trị số xuất hiện trong text (dùng cho stem)."""
    return [float(m.replace(",", ".")) for m in _NUMBER_RE.findall(text or "")]


def _close(a: float, b: float, tol: float = _REL_TOL) -> bool:
    return b != 0 and abs(a - b) <= tol * abs(b)


def compute_numeric_features(
    stem: str,
    correct: str,
    distractors: List[str],
    stem_entities: List[Entity],
    engine: OntologyEngine,
) -> Dict[str, float]:
    feats = {
        "numeric_answer_present": 0.0,
        "numeric_magnitude_ratio_to_correct": 0.0,
        "numeric_reciprocal_swap_match": 0.0,
        "numeric_same_formula_family": 0.0,
    }

    c_val = parse_numeric(correct)
    d_vals = [parse_numeric(d) for d in distractors]
    numeric_d = [v for v in d_vals if v is not None]

    if c_val is not None:
        feats["numeric_answer_present"] = 1.0

    # (1) Tỉ lệ distractor lệch đáp án đúng một hệ số kinh điển
    if c_val not in (None, 0) and numeric_d:
        slips = sum(
            1 for v in numeric_d
            if any(_close(v, c_val * r) for r in _CLASSIC_SLIP_RATIOS)
        )
        feats["numeric_magnitude_ratio_to_correct"] = slips / len(numeric_d)

    # (2) Dấu vết đảo tử-mẫu: distractor ~ correct * r^2 hoặc correct / r^2
    #     với r là tỉ số của một cặp số bất kỳ trong stem
    if c_val not in (None, 0) and numeric_d:
        stem_nums = [n for n in extract_numbers(stem) if n != 0]
        ratios = {
            abs(a / b) for a in stem_nums for b in stem_nums
            if b != 0 and abs(a / b) not in (0.0, 1.0)
        }
        for v in numeric_d:
            if any(_close(v, c_val * r * r) or _close(v, c_val / (r * r))
                   for r in ratios):
                feats["numeric_reciprocal_swap_match"] = 1.0
                break

    # (3) Stem khớp được các Quantity cùng thuộc một Formula?
    #     (Lý có lớp Quantity + cạnh relatesQuantities; Toán không có -> 0)
    qty_uris = {e.uri for e in stem_entities if e.cls == "Quantity"}
    if qty_uris:
        coverage = Counter()
        for q_uri in qty_uris:
            for formula_uri, _, d in engine.nx_graph.in_edges(q_uri, data=True):
                if d.get("prop") == "relatesQuantities":
                    coverage[formula_uri] += 1
        if coverage:
            feats["numeric_same_formula_family"] = (
                max(coverage.values()) / len(qty_uris)
            )

    return feats
