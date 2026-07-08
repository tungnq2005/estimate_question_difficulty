"""
Relation Strength Indicativeness (RSI) Module
===============================================
RSI đo lường mức độ "chỉ dẫn" của câu dẫn (stem) tới từng đáp án.
Ý tưởng: Một câu hỏi KHÓ khi stem cung cấp thông tin mơ hồ,
dẫn đến cả đáp án đúng và đáp án sai. Một câu hỏi DỄ khi stem
chỉ dẫn rõ ràng tới đáp án đúng.

RSI được phân rã thành 4 thành phần:
1. Term Overlap (TO):   Tỷ lệ từ khóa stem xuất hiện trong đáp án
2. Entity Overlap (EO): Tỷ lệ entity stem xuất hiện trong đáp án
3. Semantic Closeness (SC): Khoảng cách ngữ nghĩa stem-đáp án
4. Distractor Confusion (DC): Mức độ confusion do distractors gây ra

Công thức tổng:
  RSI(correct) = w1*TO_c + w2*EO_c + w3*SC_c + w4*(1 - DC)
  RSI(distractor_i) = w1*TO_d + w2*EO_d + w3*SC_d
  RSI_final = RSI(correct) - max(RSI(distractor_i))

Giá trị RSI_final càng CAO → stem càng rõ ràng → câu hỏi DỄ hơn.
Giá trị RSI_final càng THẤP (gần 0 hoặc âm) → stem càng mơ hồ → câu hỏi KHÓ hơn.
"""

from __future__ import annotations

import math
import re
from typing import Dict, List, Optional, Tuple

from .ontology_bridge import Entity, OntologyEngine


# Trọng số mặc định cho 4 thành phần
DEFAULT_WEIGHTS = {
    "term_overlap_w": 0.25,
    "entity_overlap_w": 0.35,
    "semantic_closeness_w": 0.25,
    "distractor_confusion_w": 0.15,
}


def _tokenize(text: str) -> set:
    """Tách từ tiếng Việt (đơn giản: tách theo khoảng trắng và loại bỏ stop-word cơ bản)."""
    stop_words = {
        "của", "và", "là", "có", "được", "các", "với", "cho", "trong",
        "một", "những", "đã", "đang", "sẽ", "không", "này", "ở", "từ",
        "vào", "ra", "lên", "xuống", "qua", "lại", "đi", "về", "đến",
        "do", "bị", "hoặc", "nếu", "thì", "khi", "như", "cũng", "rất",
        "nên", "phải", "để", "vì", "bởi", "sau", "trước",
    }
    tokens = re.findall(r"[a-zA-Zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩị"
                        r"òóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+",
                        text.lower())
    return {t for t in tokens if t not in stop_words and len(t) > 1}


def _term_overlap(stem_text: str, option_text: str) -> float:
    """
    Thành phần 1: Term Overlap (TO)
    Tỷ lệ từ khóa stem xuất hiện trong option.
    
    TO = |tokens(stem) ∩ tokens(option)| / |tokens(stem)|
    """
    stem_tokens = _tokenize(stem_text)
    option_tokens = _tokenize(option_text)
    
    if not stem_tokens:
        return 0.0
    
    intersection = stem_tokens & option_tokens
    return len(intersection) / len(stem_tokens)


def _entity_overlap(
    stem_entities: List[Entity],
    option_entities: List[Entity]
) -> float:
    """
    Thành phần 2: Entity Overlap (EO)
    Tỷ lệ entity stem xuất hiện trong option.
    
    EO = |entities(stem) ∩ entities(option)| / |entities(stem)|
    """
    if not stem_entities:
        return 0.0
    
    stem_uris = {e.uri for e in stem_entities}
    option_uris = {e.uri for e in option_entities}
    
    intersection = stem_uris & option_uris
    return len(intersection) / len(stem_uris)


def _semantic_closeness(
    stem_entities: List[Entity],
    option_entities: List[Entity],
    engine: OntologyEngine
) -> float:
    """
    Thành phần 3: Semantic Closeness (SC)
    Khoảng cách ngữ nghĩa giữa stem và option trên KG.
    
    SC = avg_{e_s in stem} max_{e_o in option} [1 / (1 + dist(e_s, e_o))]
    """
    if not stem_entities or not option_entities:
        return 0.0
    
    total = 0.0
    for e_s in stem_entities:
        max_sim = 0.0
        for e_o in option_entities:
            dist = engine.semantic_distance(e_s.uri, e_o.uri)
            if dist is not None:
                sim = 1.0 / (1.0 + dist)
                max_sim = max(max_sim, sim)
        total += max_sim
    
    return total / len(stem_entities)


def _distractor_confusion(
    distractors_entities: List[List[Entity]],
    engine: OntologyEngine
) -> float:
    """
    Thành phần 4: Distractor Confusion (DC)
    Đo mức độ gây confusion bởi distractors.
    
    DC = avg_{d_i, d_j in distractors, i≠j} 
           [max semantic_sim(d_i, d_j)]
    
    DC càng cao → distractors càng giống nhau → gây nhầm lẫn cho học sinh.
    """
    if len(distractors_entities) < 2:
        return 0.0
    
    # Tính similarity giữa các cặp distractor
    scores = []
    for i in range(len(distractors_entities)):
        for j in range(i + 1, len(distractors_entities)):
            sim = _entity_overlap(distractors_entities[i], distractors_entities[j])
            # Nếu overlap = 0, thử semantic closeness
            if sim == 0:
                sim = _semantic_closeness(
                    distractors_entities[i],
                    distractors_entities[j],
                    engine
                )
            scores.append(sim)
    
    return sum(scores) / len(scores) if scores else 0.0


def compute_rsi_features(
    stem_text: str,
    stem_entities: List[Entity],
    correct_text: str,
    correct_entities: List[Entity],
    distractors_texts: List[str],
    distractors_entities: List[List[Entity]],
    engine: OntologyEngine,
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Tính toàn bộ RSI features cho 1 MCQ.
    
    Args:
        stem_text: Văn bản câu dẫn
        stem_entities: Entity trong câu dẫn
        correct_text: Văn bản đáp án đúng
        correct_entities: Entity trong đáp án đúng
        distractors_texts: Văn bản các distractors
        distractors_entities: Entity trong từng distractor
        engine: OntologyEngine
        weights: Trọng số cho 4 thành phần
    
    Returns:
        Dict chứa các RSI features
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    features = {}
    
    # === RSI cho đáp án đúng ===
    to_correct = _term_overlap(stem_text, correct_text)
    eo_correct = _entity_overlap(stem_entities, correct_entities)
    sc_correct = _semantic_closeness(stem_entities, correct_entities, engine)
    dc = _distractor_confusion(distractors_entities, engine)
    
    rsi_correct = (
        w["term_overlap_w"] * to_correct +
        w["entity_overlap_w"] * eo_correct +
        w["semantic_closeness_w"] * sc_correct +
        w["distractor_confusion_w"] * (1.0 - dc)
    )
    
    # === RSI cho từng distractor ===
    rsi_distractors = []
    for i, (d_text, d_ents) in enumerate(zip(distractors_texts, distractors_entities)):
        to_dist = _term_overlap(stem_text, d_text)
        eo_dist = _entity_overlap(stem_entities, d_ents)
        sc_dist = _semantic_closeness(stem_entities, d_ents, engine)
        
        rsi_d = (
            w["term_overlap_w"] * to_dist +
            w["entity_overlap_w"] * eo_dist +
            w["semantic_closeness_w"] * sc_dist
        )
        rsi_distractors.append(rsi_d)
    
    # === RSI Final ===
    max_rsi_distractor = max(rsi_distractors) if rsi_distractors else 0.0
    rsi_final = rsi_correct - max_rsi_distractor
    
    # === Lưu features ===
    features["rsi_correct"] = float(rsi_correct)
    features["rsi_max_distractor"] = float(max_rsi_distractor)
    features["rsi_final"] = float(rsi_final)
    
    # RSI components
    features["rsi_to_correct"] = float(to_correct)
    features["rsi_eo_correct"] = float(eo_correct)
    features["rsi_sc_correct"] = float(sc_correct)
    features["rsi_dc"] = float(dc)
    
    # Phân phối RSI cho các distractor
    for i, rsi_d in enumerate(rsi_distractors):
        features[f"rsi_distractor_{i+1}"] = float(rsi_d)
    
    # Chênh lệch RSI: hiệu giữa distractor tốt nhất và distractor tệ nhất
    if len(rsi_distractors) >= 2:
        features["rsi_distractor_range"] = float(max(rsi_distractors) - min(rsi_distractors))
    else:
        features["rsi_distractor_range"] = 0.0
    
    return features


# ======================================================================
# PHÂN TÍCH NÂNG CAO (cho Explainable AI)
# ======================================================================

def analyze_rsi_decomposition(
    stem_text: str,
    stem_entities: List[Entity],
    correct_text: str,
    correct_entities: List[Entity],
    distractors_texts: List[str],
    distractors_entities: List[List[Entity]],
    engine: OntologyEngine
) -> dict:
    """
    Phân tích chi tiết từng thành phần RSI, dùng cho Explainability.
    Trả về báo cáo giải thích bằng tiếng Việt.
    """
    w = DEFAULT_WEIGHTS
    report = {
        "summary": "",
        "components": {},
        "verdict": "",
        "suggestion": "",
    }
    
    # TO
    to_correct = _term_overlap(stem_text, correct_text)
    to_distractors = [_term_overlap(stem_text, d) for d in distractors_texts]
    
    # EO
    eo_correct = _entity_overlap(stem_entities, correct_entities)
    eo_distractors = [_entity_overlap(stem_entities, d) for d in distractors_entities]
    
    # SC
    sc_correct = _semantic_closeness(stem_entities, correct_entities, engine)
    sc_distractors = [_semantic_closeness(stem_entities, d, engine) for d in distractors_entities]
    
    # DC
    dc = _distractor_confusion(distractors_entities, engine)
    
    # RSI scores
    rsi_correct = (
        w["term_overlap_w"] * to_correct +
        w["entity_overlap_w"] * eo_correct +
        w["semantic_closeness_w"] * sc_correct +
        w["distractor_confusion_w"] * (1.0 - dc)
    )
    rsi_dist_scores = [
        w["term_overlap_w"] * to_d +
        w["entity_overlap_w"] * eo_d +
        w["semantic_closeness_w"] * sc_d
        for to_d, eo_d, sc_d in zip(to_distractors, eo_distractors, sc_distractors)
    ]
    rsi_final = rsi_correct - (max(rsi_dist_scores) if rsi_dist_scores else 0.0)
    
    # Lưu components
    report["components"]["term_overlap"] = {
        "correct": to_correct,
        "distractors": to_distractors,
        "explanation": (
            f"Từ khóa trong stem xuất hiện ở đáp án đúng ({to_correct:.1%}) "
            f"và ở các đáp án sai ({[f'{s:.1%}' for s in to_distractors]}). "
            f"{'Stem có từ khóa rõ ràng dẫn đến đáp án đúng.' if to_correct > 0.3 else 'Stem có ít từ khóa đặc trưng.'}"
        )
    }
    report["components"]["entity_overlap"] = {
        "correct": eo_correct,
        "distractors": eo_distractors,
        "explanation": (
            f"Thực thể lịch sử trong stem xuất hiện ở đáp án đúng ({eo_correct:.1%}) "
            f"và ở các đáp án sai ({[f'{s:.1%}' for s in eo_distractors]}). "
            f"{'Stem chỉ dẫn rõ ràng tới thực thể đúng.' if eo_correct > 0.5 else 'Stem có thể gây nhầm lẫn về thực thể.'}"
        )
    }
    report["components"]["semantic_closeness"] = {
        "correct": sc_correct,
        "distractors": sc_distractors,
        "explanation": (
            f"Khoảng cách ngữ nghĩa trên Knowledge Graph: "
            f"stem-đúng={sc_correct:.3f}, stem-sai={[f'{s:.3f}' for s in sc_distractors]}. "
            f"{'Stem gần với đáp án đúng hơn trên KG.' if sc_correct > max(sc_distractors + [0]) else 'Stem có thể gần với đáp án sai hơn.'}"
        )
    }
    report["components"]["distractor_confusion"] = {
        "value": dc,
        "explanation": (
            f"Các distractors giống nhau ở mức {dc:.1%}. "
            f"{'Các distractors quá giống nhau, gây nhầm lẫn.' if dc > 0.3 else 'Các distractors khác biệt rõ ràng.'}"
        )
    }
    
    # Verdict
    if rsi_final > 0.3:
        report["verdict"] = "DỄ"
        report["summary"] = (
            f"Câu hỏi DỄ (RSI={rsi_final:.3f}): Stem chỉ dẫn rõ ràng đến đáp án đúng, "
            f"vượt trội so với các đáp án nhiễu."
        )
        report["suggestion"] = "Câu hỏi đã tốt, có thể cân nhắc tăng độ khó bằng cách làm mơ hồ stem."
    elif rsi_final > 0.0:
        report["verdict"] = "TRUNG BÌNH"
        report["summary"] = (
            f"Câu hỏi TRUNG BÌNH (RSI={rsi_final:.3f}): Stem tương đối rõ ràng "
            f"nhưng distractors vẫn có thể gây nhầm lẫn."
        )
        report["suggestion"] = "Có thể điều chỉnh nhẹ distractors để tăng/giảm độ khó."
    else:
        report["verdict"] = "KHÓ"
        report["summary"] = (
            f"Câu hỏi KHÓ (RSI={rsi_final:.3f}): Stem mơ hồ, "
            f"chỉ dẫn đến đáp án sai nhiều hơn đáp án đúng."
        )
        # Gợi ý cải thiện
        if dc > 0.3 and sc_correct < 0.3:
            report["suggestion"] = (
                "Gợi ý: (1) Thêm từ khóa đặc trưng vào stem, "
                "(2) Tách biệt các distractors về mặt ngữ nghĩa, "
                "(3) Đảm bảo stem có entity riêng biệt với đáp án đúng."
            )
        else:
            report["suggestion"] = (
                "Gợi ý: Bổ sung thông tin cụ thể vào stem để dẫn đến đáp án đúng rõ ràng hơn."
            )
    
    return report


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    engine = OntologyEngine(repo_root / "subjects" / "history" / "ontology" / "su9.ttl")

    # Test RSI
    stem_text = "Nguyên nhân sâu xa dẫn đến bùng nổ Chiến tranh thế giới thứ hai"
    correct_text = "Sự phát triển không đều của chủ nghĩa tư bản"
    distractors_texts = [
        "Chính sách thỏa hiệp, nhượng bộ của Anh, Pháp",
        "Sự xuất hiện của chủ nghĩa phát xít",
        "Khủng hoảng kinh tế 1929-1933"
    ]
    
    stem_entities = engine.extract_entities_from_text(stem_text)
    correct_entities = engine.extract_entities_from_text(correct_text)
    distractors_entities = [
        engine.extract_entities_from_text(d) for d in distractors_texts
    ]
    
    features = compute_rsi_features(
        stem_text, stem_entities, correct_text, correct_entities,
        distractors_texts, distractors_entities, engine
    )
    print("RSI Features:")
    for k, v in features.items():
        print(f"  {k}: {v:.4f}")
    
    print("\n" + "="*60)
    print("PHÂN TÍCH RSI CHI TIẾT (XAI)")
    print("="*60)
    report = analyze_rsi_decomposition(
        stem_text, stem_entities,
        correct_text, correct_entities,
        distractors_texts, distractors_entities, engine
    )
    print(f"Đánh giá: {report['verdict']}")
    print(f"Kết luận: {report['summary']}")
    print(f"Gợi ý: {report['suggestion']}")
