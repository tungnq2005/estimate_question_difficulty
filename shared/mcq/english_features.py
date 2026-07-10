# -*- coding: utf-8 -*-
"""Feature block riêng cho cụm linguistic (Tiếng Anh).

Đáp án MCQ Tiếng Anh là CÂU/TỪ tiếng Anh tự nhiên ("This bridge was built in
1990.", "goes"), không phải cụm từ trùng nhãn entity — nên 22/33 feature KG
của pipeline chung về 0 một cách cấu trúc với môn này. Thay vào đó:

- Stem vẫn khớp entity tốt (khung tiếng Việt của stem nêu thẳng tên cấu trúc
  ngữ pháp/chủ đề từ vựng) -> khai thác annotation của entity stem
  (bloomLevel, abstractness, cefrLevel, structuralComplexity).
- Độ khó của phương án nằm ở ngôn ngữ học: độ phức tạp thì-động-từ, số mệnh
  đề, câu bị động — đo bằng heuristic regex, không cần dependency mới.
- Distractor tiếng Anh "hiệu quả" là biến thể ngữ pháp sát đáp án đúng
  (goes/go/is going/went) -> edit-distance (difflib, stdlib) là tín hiệu mạnh.
- Tái dùng nguyên khối text-only của pipeline chung: KAD entropy + 6 feature
  PhoBERT (chấp nhận PhoBERT là model tiếng Việt — tín hiệu suy giảm nhưng
  không bằng 0; xem docs/PIPELINE_REDESIGN_PLAN.md).
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from statistics import pstdev
from typing import Dict, List, Optional

from rdflib import URIRef

from .ontology_bridge import Entity, OntologyEngine

CEFR_ORDER = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5, "C2": 6}

_IRREGULAR_V3 = (
    "been|built|done|made|written|taken|given|seen|known|found|told|brought|"
    "bought|caught|taught|thought|sold|sent|kept|left|lost|paid|put|read|said|"
    "shown|spoken|spent|worn|won|broken|chosen|driven|eaten|fallen|grown|drawn|"
    "gone|come|become|begun|drunk|sung|swum|run|forgotten|gotten|got|held|met|"
    "sat|stood|understood|heard|felt|built"
)
_V3 = rf"(?:\w+ed|{_IRREGULAR_V3})"

# (bậc, pattern) — xét từ bậc cao xuống, lấy bậc đầu tiên khớp
_TENSE_LEVELS = [
    (4, re.compile(rf"\b(?:would|could|might)\s+(?:not\s+)?have\s+{_V3}\b", re.I)),
    (4, re.compile(rf"\bhad\s+(?:not\s+)?{_V3}\b", re.I)),
    (3, re.compile(rf"\b(?:is|are|was|were|be|been|being)\s+(?:not\s+)?{_V3}\b", re.I)),
    (3, re.compile(rf"\b(?:have|has)\s+(?:not\s+)?{_V3}\b", re.I)),
    (3, re.compile(r"\b(?:would|could|might)\s+(?:not\s+)?\w+\b", re.I)),
    (2, re.compile(r"\b(?:is|are|was|were|am|be|been)\s+(?:not\s+)?\w+ing\b", re.I)),
    (2, re.compile(r"\b(?:going\s+to)\s+\w+\b", re.I)),
    (1, re.compile(r"\b(?:did|was|were|went|saw|had|visited|came|took|gave|got|said)\b|\b\w+ed\b", re.I)),
    (1, re.compile(r"\b(?:should|must|can|may|will|shall)\b", re.I)),
]

_CLAUSE_MARKERS = re.compile(
    r"\b(?:who|whom|whose|which|that|because|if|when|while|although|though|"
    r"since|unless|before|after|where|so that|in order to)\b", re.I)

_PASSIVE = re.compile(rf"\b(?:is|are|was|were|be|been|being)\s+(?:not\s+)?{_V3}\b", re.I)

_EN_STOPWORDS = {"the", "a", "an", "to", "of", "in", "on", "at", "and", "or",
                 "is", "are", "was", "were", "be", "for", "with", "by"}


@dataclass
class EnglishMCQFeatures:
    """Feature vector 26 chiều cho MCQ Tiếng Anh (cụm linguistic)."""
    mcq_id: str

    # ====== E1: Stem-KG — entity khớp được ở stem (6) ======
    stem_entity_matched: float = 0.0
    stem_entity_count: float = 0.0
    stem_grammar_bloom_level: float = 0.0
    stem_grammar_abstractness: float = 0.0
    stem_grammar_cefr_level: float = 0.0        # A1=1 ... C2=6, 0 = không rõ
    stem_grammar_structural_complexity: float = 0.0

    # ====== E2: Độ phức tạp ngôn ngữ của phương án (7) ======
    ans_word_count: float = 0.0
    ans_mean_word_count_distractors: float = 0.0
    ans_clause_count: float = 0.0
    ans_tense_complexity: float = 0.0           # 0..4 (hiện tại đơn -> hoàn thành/điều kiện)
    ans_max_tense_complexity_distractors: float = 0.0
    ans_passive_present: float = 0.0
    ans_len_uniformity: float = 0.0             # 1/(1+std độ dài) — đều nhau = khó

    # ====== E3: Độ "giống gây nhiễu" của distractor (5) ======
    dist_edit_ratio_max: float = 0.0            # distractor sát đáp án nhất
    dist_edit_ratio_mean: float = 0.0
    dist_token_overlap_mean: float = 0.0
    dist_shared_prefix_ratio: float = 0.0       # chỉ khác phần đuôi (goes/going)
    dist_same_first_word: float = 0.0

    # ====== E4: Tái dùng text-only từ pipeline chung (8) ======
    kad_entropy_stem: float = 0.0
    kad_entropy_correct: float = 0.0
    emb_stem_distractor_mean_sim: float = 0.0
    emb_stem_distractor_max_sim: float = 0.0
    emb_stem_distractor_min_sim: float = 0.0
    emb_stem_distractor_std_sim: float = 0.0
    emb_stem_correct_sim: float = 0.0
    emb_discriminative_power: float = 0.0

    label: Optional[str] = None

    @property
    def feature_vector(self) -> List[float]:
        exclude = {"mcq_id", "label"}
        return [v for k, v in asdict(self).items()
                if k not in exclude and isinstance(v, (int, float))]

    @property
    def feature_names(self) -> List[str]:
        exclude = {"mcq_id", "label"}
        return [k for k, v in asdict(self).items()
                if k not in exclude and isinstance(v, (int, float))]


def _tense_level(text: str) -> float:
    for level, pat in _TENSE_LEVELS:
        if pat.search(text):
            return float(level)
    return 0.0


def _tokens(text: str) -> set:
    return {t for t in re.findall(r"[a-zA-Z']+", text.lower())
            if t not in _EN_STOPWORDS and len(t) > 1}


def _annotation_mean(engine: OntologyEngine, entities: List[Entity],
                     prop_name: str) -> float:
    vals = []
    for e in entities:
        for o in sorted(engine.graph.objects(URIRef(e.uri),
                                             engine.NS[prop_name]), key=str):
            try:
                vals.append(float(str(o)))
            except ValueError:
                continue
            break
    return sum(vals) / len(vals) if vals else 0.0


def extract_english_mcq_features(mcq, engine: OntologyEngine) -> EnglishMCQFeatures:
    """Trích 26 features cho 1 MCQ Tiếng Anh. `mcq` là shared.mcq.features.MCQ."""
    f = EnglishMCQFeatures(mcq_id=mcq.id)
    options = [mcq.correct] + mcq.distractors

    # === E1: stem-KG ===
    stem_entities = engine.extract_entities_from_text(mcq.stem)
    f.stem_entity_matched = 1.0 if stem_entities else 0.0
    f.stem_entity_count = float(len(stem_entities))
    if stem_entities:
        f.stem_grammar_bloom_level = _annotation_mean(engine, stem_entities, "bloomLevel")
        f.stem_grammar_abstractness = _annotation_mean(engine, stem_entities, "abstractness")
        f.stem_grammar_structural_complexity = _annotation_mean(
            engine, stem_entities, "structuralComplexity")
        cefr_vals = []
        for e in stem_entities:
            for o in sorted(engine.graph.objects(URIRef(e.uri),
                                                 engine.NS.cefrLevel), key=str):
                lv = CEFR_ORDER.get(str(o).strip().upper())
                if lv:
                    cefr_vals.append(lv)
        f.stem_grammar_cefr_level = float(max(cefr_vals)) if cefr_vals else 0.0

    # === E2: độ phức tạp ngôn ngữ ===
    word_counts = [len(o.split()) for o in options]
    f.ans_word_count = float(word_counts[0])
    if len(word_counts) > 1:
        f.ans_mean_word_count_distractors = sum(word_counts[1:]) / (len(word_counts) - 1)
    f.ans_clause_count = float(len(_CLAUSE_MARKERS.findall(mcq.correct)))
    f.ans_tense_complexity = _tense_level(mcq.correct)
    if mcq.distractors:
        f.ans_max_tense_complexity_distractors = max(
            _tense_level(d) for d in mcq.distractors)
    f.ans_passive_present = 1.0 if any(_PASSIVE.search(o) for o in options) else 0.0
    f.ans_len_uniformity = 1.0 / (1.0 + pstdev(word_counts)) if len(word_counts) > 1 else 0.0

    # === E3: distractor sát đáp án đúng tới đâu ===
    if mcq.distractors:
        ratios = [SequenceMatcher(None, mcq.correct.lower(), d.lower()).ratio()
                  for d in mcq.distractors]
        f.dist_edit_ratio_max = max(ratios)
        f.dist_edit_ratio_mean = sum(ratios) / len(ratios)
        c_tokens = _tokens(mcq.correct)
        if c_tokens:
            overlaps = [len(c_tokens & _tokens(d)) / len(c_tokens)
                        for d in mcq.distractors]
            f.dist_token_overlap_mean = sum(overlaps) / len(overlaps)
        prefix_ratios = []
        for d in mcq.distractors:
            m = SequenceMatcher(None, mcq.correct.lower(), d.lower())
            match = m.find_longest_match(0, len(mcq.correct), 0, len(d))
            common_prefix = match.size if match.a == 0 and match.b == 0 else 0
            prefix_ratios.append(common_prefix / max(len(mcq.correct), 1))
        f.dist_shared_prefix_ratio = sum(prefix_ratios) / len(prefix_ratios)
        first = mcq.correct.split()[0].lower() if mcq.correct.split() else ""
        f.dist_same_first_word = sum(
            1 for d in mcq.distractors
            if d.split() and d.split()[0].lower() == first
        ) / len(mcq.distractors)

    # === E4: tái dùng text-only của pipeline chung ===
    try:
        f.kad_entropy_stem = engine.knowledge_entropy(mcq.stem)
        f.kad_entropy_correct = engine.knowledge_entropy(mcq.correct)
    except Exception:
        pass
    from .features import _compute_embedding_features
    for k, v in _compute_embedding_features(
            mcq.stem, mcq.correct, mcq.distractors, engine).items():
        if hasattr(f, k):
            setattr(f, k, v)

    f.label = mcq.difficulty
    return f
