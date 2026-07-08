"""
Jaccard Similarity Module
==========================
Đo độ giống nhau giữa đáp án đúng và các distractors (đáp án nhiễu)
dựa trên Knowledge Graph với 3 cấp độ:

1. Jaccard Hard: Set overlap cứng giữa các entity URI
2. Jaccard Soft: Dùng semantic distance (shortest path) trên đồ thị
3. Jaccard KG Weighted: Kết hợp weightsJson + abstractness từ ontology

Công thức tổng quát:
  Jaccard(correct, distractor_i) = |entities(correct) ∩ entities(distractor_i)|
                                   / |entities(correct) ∪ entities(distractor_i)|

Giá trị càng cao → càng dễ gây nhầm lẫn → câu hỏi KHÓ hơn.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple

from .ontology_bridge import Entity, OntologyEngine


def jaccard_hard(
    correct_entities: List[Entity],
    distractor_entities: List[Entity]
) -> float:
    """
    Jaccard Hard: Set overlap cứng giữa các URI entity.
    
    Args:
        correct_entities: Entity trong đáp án đúng
        distractor_entities: Entity trong distractor
    
    Returns:
        Jaccard similarity (0.0 - 1.0)
    """
    if not correct_entities or not distractor_entities:
        return 0.0
    
    set_correct = {e.uri for e in correct_entities}
    set_dist = {e.uri for e in distractor_entities}
    
    intersection = set_correct & set_dist
    union = set_correct | set_dist
    
    return len(intersection) / len(union) if union else 0.0


def jaccard_soft(
    correct_entities: List[Entity],
    distractor_entities: List[Entity],
    engine: OntologyEngine,
    threshold: float = 3.0
) -> float:
    """
    Jaccard Soft: Dùng semantic distance trên đồ thị.
    
    Công thức:
      sim(e1, e2) = 1 / (1 + shortest_path_length(e1, e2))
      overlap_score = avg_{e_c in correct} max_{e_d in distractor} sim(e_c, e_d)
    
    Args:
        correct_entities: Entity trong đáp án đúng
        distractor_entities: Entity trong distractor
        engine: OntologyEngine đã load
        threshold: Ngưỡng distance để coi là "không liên quan"
    
    Returns:
        Soft Jaccard similarity (0.0 - 1.0)
    """
    if not correct_entities or not distractor_entities:
        return 0.0
    
    total_sim = 0.0
    for e_c in correct_entities:
        max_sim = 0.0
        for e_d in distractor_entities:
            dist = engine.semantic_distance(e_c.uri, e_d.uri)
            if dist is not None and dist <= threshold:
                sim = 1.0 / (1.0 + dist)
                max_sim = max(max_sim, sim)
        total_sim += max_sim
    
    return total_sim / len(correct_entities)


def jaccard_kg_weighted(
    correct_entities: List[Entity],
    distractor_entities: List[Entity],
    engine: OntologyEngine
) -> float:
    """
    Jaccard KG Weighted: Kết hợp weightsJson + abstractness.
    
    Nếu 2 entity có kết nối weightsJson, điểm similarity sẽ cao hơn.
    Ngoài ra còn tính abstractness: nếu entity trừu tượng, overlap sẽ có
    trọng số cao hơn (vì cùng trừu tượng = dễ nhầm hơn).
    
    Returns:
        Weighted Jaccard similarity (0.0 - 1.0)
    """
    if not correct_entities or not distractor_entities:
        return 0.0
    
    total_score = 0.0
    for e_c in correct_entities:
        max_score = 0.0
        for e_d in distractor_entities:
            score = 0.0
            
            # 1. Direct URI match
            if e_c.uri == e_d.uri:
                score += 0.5
            
            # 2. Weight từ weightsJson
            w1 = engine.get_weight(e_c.uri, e_d.uri)
            w2 = engine.get_weight(e_d.uri, e_c.uri)
            max_weight = max(w1, w2)
            if max_weight > 0:
                score += 0.3 * (max_weight / 10.0)
            
            # 3. Abstractness bonus: nếu cùng abstractness, dễ nhầm hơn
            if e_c.abstractness is not None and e_d.abstractness is not None:
                abs_diff = abs(e_c.abstractness - e_d.abstractness)
                score += 0.2 * (1.0 / (1.0 + abs_diff))
            
            max_score = max(max_score, score)
        total_score += max_score
    
    return total_score / len(correct_entities)


def compute_jaccard_features(
    stem_entities: List[Entity],
    correct_entities: List[Entity],
    distractors_entities: List[List[Entity]],
    engine: OntologyEngine
) -> Dict[str, float]:
    """
    Tính toàn bộ Jaccard features cho 1 MCQ.
    
    Args:
        stem_entities: Entity trong câu dẫn (stem)
        correct_entities: Entity trong đáp án đúng
        distractors_entities: List các entity trong từng distractor
        engine: OntologyEngine
    
    Returns:
        Dict chứa các Jaccard features
    """
    features = {}
    
    # Jaccard Hard: lấy giá trị lớn nhất, trung bình
    hard_scores = [
        jaccard_hard(correct_entities, d_ents)
        for d_ents in distractors_entities
    ]
    features["jaccard_hard_max"] = float(max(hard_scores)) if hard_scores else 0.0
    features["jaccard_hard_mean"] = float(
        sum(hard_scores) / len(hard_scores) if hard_scores else 0.0
    )
    
    # Jaccard Soft
    soft_scores = [
        jaccard_soft(correct_entities, d_ents, engine)
        for d_ents in distractors_entities
    ]
    features["jaccard_soft_max"] = float(max(soft_scores)) if soft_scores else 0.0
    features["jaccard_soft_mean"] = float(
        sum(soft_scores) / len(soft_scores) if soft_scores else 0.0
    )
    
    # Jaccard KG Weighted
    kg_scores = [
        jaccard_kg_weighted(correct_entities, d_ents, engine)
        for d_ents in distractors_entities
    ]
    features["jaccard_kg_max"] = float(max(kg_scores)) if kg_scores else 0.0
    features["jaccard_kg_mean"] = float(
        sum(kg_scores) / len(kg_scores) if kg_scores else 0.0
    )
    
    # Jaccard Stem-Correct: đo stem có dẫn đến đáp án đúng không
    stem_correct_hard = jaccard_hard(stem_entities, correct_entities) if stem_entities else 0.0
    stem_correct_soft = jaccard_soft(stem_entities, correct_entities, engine) if stem_entities else 0.0
    features["jaccard_stem_correct"] = max(stem_correct_hard, stem_correct_soft)
    
    # Jaccard Stem-Distractors: đo stem có dẫn đến đáp án sai không
    stem_dist_scores = [
        max(
            jaccard_hard(stem_entities, d_ents),
            jaccard_soft(stem_entities, d_ents, engine)
        )
        for d_ents in distractors_entities
    ] if stem_entities else [0.0]
    features["jaccard_stem_distractor_max"] = float(max(stem_dist_scores)) if stem_dist_scores else 0.0
    
    return features


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    engine = OntologyEngine(repo_root / "subjects" / "history" / "ontology" / "su9.ttl")

    # Test Jaccard với 1 câu hỏi mẫu
    stem_text = "Nguyên nhân sâu xa dẫn đến bùng nổ Chiến tranh thế giới thứ hai"
    correct_text = "Sự phát triển không đều của chủ nghĩa tư bản"
    distractors = [
        "Chính sách thỏa hiệp, nhượng bộ của Anh, Pháp",
        "Sự xuất hiện của chủ nghĩa phát xít",
        "Khủng hoảng kinh tế 1929-1933"
    ]
    
    stem_entities = engine.extract_entities_from_text(stem_text)
    correct_entities = engine.extract_entities_from_text(correct_text)
    distractors_entities = [
        engine.extract_entities_from_text(d) for d in distractors
    ]
    
    print(f"Stem entities: {[e.label for e in stem_entities]}")
    print(f"Correct entities: {[e.label for e in correct_entities]}")
    for i, d_ents in enumerate(distractors_entities):
        print(f"Distractor {i+1} entities: {[e.label for e in d_ents]}")
    
    feats = compute_jaccard_features(
        stem_entities, correct_entities, distractors_entities, engine
    )
    print("\nJaccard Features:")
    for k, v in feats.items():
        print(f"  {k}: {v:.4f}")
