"""
Feature extraction for cold-start question difficulty estimation.

Given a question and a list of linked mentions (from EntityExtractor), produce
a fixed-dimensional feature vector suitable for XGBoost / other ML models.

Feature groups (all motivated for the paper):
  - Entity counts & type diversity
  - Abstractness statistics
  - Textbook-frequency statistics (rarity = harder, like IDF)
  - Prerequisite-depth statistics (core "depth of knowledge" signal)
  - Semantic-graph structural features (centrality, pairwise distances)
  - Curriculum-position features (where in the year's syllabus)
  - Bloom's Taxonomy features (annotated + inferred from interrogative verb)
  - Linguistic surface features (length, interrogative verbs)
"""

from __future__ import annotations

import math
import re
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from entity_extraction import Mention
from ontology_loader import OntologyStore, normalize_preserve_offsets

# ----------------------------------------------------------------------
# Bloom-level lexicon (inferred from interrogative verbs in Vietnamese)
# ----------------------------------------------------------------------
BLOOM_VERB_LEVEL: Dict[str, int] = {
    # Level 1 - Biết (Remember)
    "khi nao": 1, "ai": 1, "o dau": 1, "nam nao": 1, "la gi": 1,
    "ke ten": 1, "liet ke": 1, "trinh bay": 1, "neu": 1,
    # Level 2 - Hiểu (Understand)
    "vi sao": 2, "tai sao": 2, "y nghia": 2, "giai thich": 2,
    "mo ta": 2, "tom tat": 2,
    # Level 3 - Vận dụng (Apply)
    "phan tich": 3, "chung minh": 3, "lam ro": 3, "so sanh": 3,
    # Level 4 - Vận dụng cao (Analyze / Evaluate / Create)
    "danh gia": 4, "nhan xet": 4, "rut ra bai hoc": 4, "lien he": 4,
    "bai hoc": 4, "van dung": 4,
}

QUESTION_CATEGORY_VERBS: Dict[str, List[str]] = {
    "factual": ["khi nao", "ai", "o dau", "nam nao", "la gi", "ke ten", "liet ke", "trinh bay", "neu"],
    "causal": ["vi sao", "tai sao", "nguyen nhan"],
    "comparative": ["so sanh", "khac nhau", "giong nhau"],
    "analytical": ["phan tich", "chung minh", "lam ro"],
    "evaluative": ["danh gia", "nhan xet", "rut ra bai hoc", "lien he", "bai hoc", "van dung"],
}


@dataclass
class QuestionFeatures:
    """Flat feature dict + metadata. Use .to_dict() for XGBoost."""
    values: Dict[str, float] = field(default_factory=dict)
    meta: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, float]:
        return dict(self.values)


class FeatureExtractor:
    def __init__(self, store: OntologyStore):
        self.store = store

    # ------------------------------------------------------------------
    def extract(self, question: str, mentions: List[Mention]) -> QuestionFeatures:
        linked = [m for m in mentions if m.uri is not None]
        unique_uris = sorted({m.uri for m in linked if m.uri})
        entities = [self.store.get(u) for u in unique_uris]
        entities = [e for e in entities if e is not None]

        feats: Dict[str, float] = {}

        # -------- Entity counts --------
        feats["num_mentions"] = float(len(linked))
        feats["num_unique_entities"] = float(len(unique_uris))
        feats["num_unlinked_mentions"] = float(len(mentions) - len(linked))

        # Type counts
        type_counts = {"Event": 0, "Person": 0, "Location": 0, "Period": 0,
                       "Organization": 0, "Movement": 0, "Document": 0, "Concept": 0}
        for e in entities:
            if e.cls in type_counts:
                type_counts[e.cls] += 1
        for k, v in type_counts.items():
            feats[f"count_{k.lower()}"] = float(v)
        feats["type_diversity"] = float(sum(1 for v in type_counts.values() if v > 0))

        # -------- Abstractness --------
        abs_vals = [e.abstractness for e in entities if e.abstractness is not None]
        feats["abstractness_mean"] = float(_mean(abs_vals))
        feats["abstractness_max"] = float(max(abs_vals) if abs_vals else 0)
        feats["abstractness_min"] = float(min(abs_vals) if abs_vals else 0)
        feats["abstractness_range"] = feats["abstractness_max"] - feats["abstractness_min"]

        # -------- Textbook frequency (rarity) --------
        freqs = [e.frequency_in_textbook for e in entities if e.frequency_in_textbook is not None]
        feats["freq_mean"] = float(_mean(freqs))
        feats["freq_min"] = float(min(freqs) if freqs else 0)
        # Inverse-frequency (IDF-like) — rarer entities make harder questions
        feats["inv_freq_sum"] = float(sum(1.0 / (1 + f) for f in freqs))
        feats["log_inv_freq_mean"] = float(
            _mean([math.log(1.0 + 1.0 / (1 + f)) for f in freqs])
        )

        # -------- Prerequisite depth --------
        depths = [self.store.prerequisite_depth(u) for u in unique_uris]
        feats["prereq_depth_max"] = float(max(depths) if depths else 0)
        feats["prereq_depth_sum"] = float(sum(depths))
        feats["prereq_depth_mean"] = float(_mean(depths))

        # -------- Graph centrality --------
        cents = [self.store.centrality(u) for u in unique_uris]
        feats["centrality_mean"] = float(_mean(cents))
        feats["centrality_max"] = float(max(cents) if cents else 0)
        # Low centrality = peripheral entity = harder
        feats["peripheral_score"] = float(1.0 - _mean(cents)) if cents else 0.0

        # -------- Pairwise semantic distance --------
        if len(unique_uris) >= 2:
            distances = []
            for i in range(len(unique_uris)):
                for j in range(i + 1, len(unique_uris)):
                    d = self.store.semantic_distance(unique_uris[i], unique_uris[j])
                    if d is not None:
                        distances.append(d)
            feats["sem_dist_max"] = float(max(distances) if distances else 0)
            feats["sem_dist_mean"] = float(_mean(distances))
            feats["sem_dist_disconnected"] = float(
                sum(1 for i in range(len(unique_uris))
                    for j in range(i + 1, len(unique_uris))
                    if self.store.semantic_distance(unique_uris[i], unique_uris[j]) is None)
            )
        else:
            feats["sem_dist_max"] = 0.0
            feats["sem_dist_mean"] = 0.0
            feats["sem_dist_disconnected"] = 0.0

        # -------- Curriculum position --------
        positions = [e.curriculum_position for e in entities if e.curriculum_position is not None]
        feats["curr_pos_min"] = float(min(positions) if positions else 0)
        feats["curr_pos_max"] = float(max(positions) if positions else 0)
        feats["curr_pos_span"] = feats["curr_pos_max"] - feats["curr_pos_min"]
        # Period crossing
        period_uris = [e.uri for e in entities if e.cls == "Period"]
        feats["crosses_periods"] = float(1 if len(set(period_uris)) >= 2 else 0)
        # World-vs-VN mix (very rough: Location-based)
        world_locs = {"su9:L_LienXo", "su9:L_My", "su9:L_NhatBan", "su9:L_TrungQuoc",
                      "su9:L_TayAu", "su9:L_DongAu", "su9:L_DongNamA", "su9:L_ChauPhi",
                      "su9:L_MyLatinh", "su9:L_Cuba", "su9:L_Phap", "su9:L_AnDo",
                      "su9:L_Geneva", "su9:L_Paris"}
        world_count = sum(1 for e in entities
                          if e.cls == "Location" and e.uri.split("#")[-1] in
                          {u.split(":")[-1] for u in world_locs})
        vn_locs = sum(1 for e in entities
                      if e.cls == "Location" and e.uri.split("#")[-1] not in
                      {u.split(":")[-1] for u in world_locs})
        feats["world_history_signal"] = float(world_count)
        feats["vn_history_signal"] = float(vn_locs)

        # -------- Bloom levels --------
        bloom_annotated = [e.bloom_level for e in entities if e.bloom_level is not None]
        feats["bloom_annotated_max"] = float(max(bloom_annotated) if bloom_annotated else 0)
        feats["bloom_annotated_mean"] = float(_mean(bloom_annotated))
        inferred_bloom, category_flags = self._infer_bloom_and_category(question)
        feats["bloom_inferred"] = float(inferred_bloom)
        feats["bloom_combined_max"] = float(max([inferred_bloom] + bloom_annotated)
                                            if bloom_annotated else inferred_bloom)
        for cat, flag in category_flags.items():
            feats[f"qtype_{cat}"] = float(flag)

        # -------- Linguistic surface --------
        feats["q_length_chars"] = float(len(question))
        feats["q_length_words"] = float(len(question.split()))
        # Number of distinct interrogative/cue verbs
        q_norm = normalize_preserve_offsets(question)
        feats["num_cue_phrases"] = float(
            sum(1 for v in BLOOM_VERB_LEVEL if v in q_norm)
        )

        meta = {
            "question": question,
            "linked_uris": unique_uris,
            "linked_labels": [e.label for e in entities],
            "inferred_bloom": inferred_bloom,
            "category_flags": category_flags,
        }
        return QuestionFeatures(values=feats, meta=meta)

    # ------------------------------------------------------------------
    @staticmethod
    def _infer_bloom_and_category(question: str):
        q_norm = normalize_preserve_offsets(question)
        level = 1
        for phrase, lv in BLOOM_VERB_LEVEL.items():
            if re.search(r"\b" + re.escape(phrase) + r"\b", q_norm):
                level = max(level, lv)
        categories = {cat: 0 for cat in QUESTION_CATEGORY_VERBS}
        for cat, verbs in QUESTION_CATEGORY_VERBS.items():
            for v in verbs:
                if re.search(r"\b" + re.escape(v) + r"\b", q_norm):
                    categories[cat] = 1
                    break
        return level, categories


def _mean(xs):
    return statistics.mean(xs) if xs else 0.0


if __name__ == "__main__":
    from pathlib import Path
    from entity_extraction import EntityExtractor

    here = Path(__file__).resolve().parent.parent
    store = OntologyStore(here / "ontology" / "su9.ttl")
    extractor = EntityExtractor(store)
    fe = FeatureExtractor(store)

    q = "Phân tích ý nghĩa lịch sử của chiến dịch Điện Biên Phủ 1954 đối với Hiệp định Genève."
    mentions = extractor.extract(q)
    feats = fe.extract(q, mentions)
    print("Question:", q)
    print("Linked entities:", feats.meta["linked_labels"])
    print("Inferred Bloom:", feats.meta["inferred_bloom"])
    print("\nFeature vector:")
    for k, v in feats.values.items():
        print(f"  {k}: {v}")
