"""
Entity extraction pipeline for Vietnamese history questions.

Strategy (in order):
  1. Alias/label dictionary matching against the ontology (longest-match, diacritic-insensitive).
  2. Year/period pattern matching to link temporal mentions to Period individuals.
  3. (Optional) External Vietnamese NER (underthesea / PhoBERT) for entities that
     aren't in the ontology yet — returned as "unlinked" mentions, useful for
     flagging coverage gaps in the ontology.

The ontology-based matching is intentionally the primary signal: our downstream
feature functions need the entity to be resolved to an ontology URI.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ontology_loader import OntologyStore, _normalize, normalize_preserve_offsets

# Optional underthesea import — guarded so the pipeline still runs without it.
try:
    from underthesea import ner as _uts_ner  # type: ignore
    _HAS_UTS = True
except Exception:
    _HAS_UTS = False


@dataclass
class Mention:
    surface: str              # raw text as it appears in the question
    start: int                # char offset in normalized text
    end: int
    uri: Optional[str] = None # ontology URI if linked, else None
    cls: Optional[str] = None # class name if linked
    source: str = "dict"      # "dict" | "period" | "ner"


# ----------------------------------------------------------------------
# Year / period patterns
# ----------------------------------------------------------------------
YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")
YEAR_RANGE_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\s*[-\u2013]\s*(1[89]\d{2}|20\d{2})\b")


class EntityExtractor:
    """
    Resolve entity mentions in a Vietnamese history question to ontology URIs.
    """

    def __init__(self, store: OntologyStore, use_ner: bool = False):
        self.store = store
        self.use_ner = use_ner and _HAS_UTS

        # Build reverse index: sorted normalized names -> URIs (longest first)
        # Filter out aliases that would collide with common Vietnamese words.
        vn_stopwords = {
            "nam", "ngay", "thang", "nhung", "va", "la", "cua", "den", "trong",
            "voi", "tu", "hay", "cac", "mot", "hai", "ba", "bon", "nay", "do",
            "vi", "sao", "the", "nao", "gi", "cho", "o", "ra", "vao", "khi",
            "truoc", "sau", "tren", "duoi", "giua", "can", "neu", "thi",
            # single-letter confusion
            "a", "b", "c", "d", "e", "g", "h", "i", "k", "l", "m", "n",
            "o", "p", "q", "r", "s", "t", "u", "v", "x", "y",
        }
        self._name_to_uri: List[Tuple[str, str]] = []
        for name_key, uri in store.label_index.items():
            if len(name_key) < 3:
                continue
            # Skip if the entire normalized name is a stopword
            if name_key in vn_stopwords:
                continue
            self._name_to_uri.append((name_key, uri))
        # Sort by length descending so longest matches win
        self._name_to_uri.sort(key=lambda t: -len(t[0]))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def extract(self, question: str) -> List[Mention]:
        """Extract entity mentions from a question, linked to ontology URIs where possible."""
        # Position-preserving normalization: same length as original -> indices line up.
        normalized = normalize_preserve_offsets(question)
        mentions: List[Mention] = []

        # 1. Dictionary matching (longest-match, non-overlapping)
        taken = [False] * len(normalized)
        for name_key, uri in self._name_to_uri:
            # name_key is space-collapsed; scan with a simple windowed search that
            # tolerates extra whitespace/punctuation in the question.
            for idx, end in self._find_all(normalized, name_key):
                if self._is_word_boundary(normalized, idx, end) and not any(taken[idx:end]):
                    ent = self.store.get(uri)
                    mentions.append(Mention(
                        surface=question[idx:end],
                        start=idx, end=end,
                        uri=uri,
                        cls=ent.cls if ent else None,
                        source="dict",
                    ))
                    for i in range(idx, end):
                        taken[i] = True

        # 2. Year / period matching (on original text so hyphens survive)
        for m in YEAR_RANGE_RE.finditer(question):
            y1, y2 = int(m.group(1)), int(m.group(2))
            period_uri = self._find_period(y1, y2)
            if period_uri:
                mentions.append(Mention(
                    surface=m.group(0), start=m.start(), end=m.end(),
                    uri=period_uri, cls="Period", source="period",
                ))
                for i in range(m.start(), m.end()):
                    if i < len(taken):
                        taken[i] = True
        for m in YEAR_RE.finditer(question):
            if any(taken[i] for i in range(m.start(), min(m.end(), len(taken)))):
                continue
            y = int(m.group(1))
            period_uri = self._find_period(y, y)
            if period_uri:
                mentions.append(Mention(
                    surface=m.group(0), start=m.start(), end=m.end(),
                    uri=period_uri, cls="Period", source="period",
                ))

        # 3. Optional external NER for unlinked mentions
        if self.use_ner:
            for surface, start, end in self._ner_spans(question):
                overlap = any(s < end and start < e
                              for s, e in [(mn.start, mn.end) for mn in mentions])
                if not overlap:
                    mentions.append(Mention(
                        surface=surface, start=start, end=end,
                        uri=None, cls=None, source="ner",
                    ))

        # Deduplicate by (uri, span) and sort
        seen = set()
        unique: List[Mention] = []
        for mn in sorted(mentions, key=lambda x: (x.start, -x.end)):
            key = (mn.uri, mn.start, mn.end)
            if key not in seen:
                seen.add(key)
                unique.append(mn)
        return unique

    @staticmethod
    def _find_all(haystack: str, needle: str):
        """Yield (start, end) where needle matches haystack, allowing collapsed whitespace."""
        # Simple exact find first
        start = 0
        while True:
            idx = haystack.find(needle, start)
            if idx == -1:
                break
            yield idx, idx + len(needle)
            start = idx + 1

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _is_word_boundary(text: str, start: int, end: int) -> bool:
        left_ok = (start == 0) or (not text[start - 1].isalnum())
        right_ok = (end == len(text)) or (not text[end].isalnum())
        return left_ok and right_ok

    def _find_period(self, y1: int, y2: int) -> Optional[str]:
        """Find the ontology Period that best covers [y1, y2]."""
        best_uri: Optional[str] = None
        best_span = 10**9
        for uri, ent in self.store.entities.items():
            if ent.cls != "Period" or ent.start_year is None or ent.end_year is None:
                continue
            if ent.start_year <= y1 and y2 <= ent.end_year:
                span = ent.end_year - ent.start_year
                if span < best_span:
                    best_span = span
                    best_uri = uri
        return best_uri

    def _ner_spans(self, question: str):
        if not _HAS_UTS:
            return []
        try:
            tagged = _uts_ner(question)
        except Exception:
            return []
        spans = []
        buf, buf_start = [], None
        cursor = 0
        for token_info in tagged:
            if not isinstance(token_info, (list, tuple)) or len(token_info) < 4:
                continue
            word, _, _, entity = token_info[0], token_info[1], token_info[2], token_info[3]
            idx = question.find(word, cursor)
            if idx == -1:
                continue
            cursor = idx + len(word)
            if entity.startswith("B-"):
                if buf and buf_start is not None:
                    surface = " ".join(buf)
                    spans.append((surface, buf_start, buf_start + len(surface)))
                buf, buf_start = [word], idx
            elif entity.startswith("I-") and buf:
                buf.append(word)
            else:
                if buf and buf_start is not None:
                    surface = " ".join(buf)
                    spans.append((surface, buf_start, buf_start + len(surface)))
                buf, buf_start = [], None
        if buf and buf_start is not None:
            surface = " ".join(buf)
            spans.append((surface, buf_start, buf_start + len(surface)))
        return spans


if __name__ == "__main__":
    from pathlib import Path
    here = Path(__file__).resolve().parent.parent
    store = OntologyStore(here / "ontology" / "su9.ttl")
    ex = EntityExtractor(store)

    examples = [
        "Chiến dịch Điện Biên Phủ năm 1954 có ý nghĩa gì?",
        "So sánh Hiệp định Genève 1954 và Hiệp định Paris 1973.",
        "Phân tích nguyên nhân thắng lợi của Cách mạng tháng Tám.",
        "Đường lối Đổi mới được đề ra tại Đại hội Đảng lần thứ mấy?",
        "Trình bày vai trò của Nguyễn Ái Quốc trong giai đoạn 1919-1930.",
    ]
    for q in examples:
        mentions = ex.extract(q)
        print(f"\nQ: {q}")
        for m in mentions:
            print(f"  - [{m.cls or 'UNK'}] {m.surface!r} -> {m.uri}")
