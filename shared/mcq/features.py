"""
Feature Engineering Module v4.1
================================
Tổng hợp thành vector đặc trưng **41 chiều** (dataclass MCQFeatures):

  Block A (KG):       27 - KG Structure (8) + Jaccard (8) + RSI (8) + Văn (3)
  Block B (KAD):       3 - Knowledge Entropy (2) + Path Distance (1)
  Block C (Embedding): 6 - PhoBERT cosine similarities
  meta:                1 - entity_match_coverage
  Toán–Lý:             4 - numeric_* (chỉ cụm prereq_dag)

7 đặc trưng cuối bật/tắt theo `config.cluster` (xem shared/subjects.py), nên
mỗi môn thực dùng 34–38 chiều; môn Sử dùng 34. Riêng tiếng Anh đi nhánh riêng
với 26 đặc trưng ngôn ngữ học (shared/mcq/english_features.py).

Đặc trưng KHÔNG tính được trả **NaN**, không phải 0.0 — xem MISSING bên dưới.

Lý thuyết nền tảng:
  - Shannon Entropy (1948): Đo khối lượng thông tin trong câu hỏi
  - Graph Theory (Euler, 1736): Khoảng cách khái niệm giữa các đáp án
  - Semantic Similarity: Mức độ nhầm lẫn ngữ nghĩa giữa stem và options

Output: DataFrame gồm mcq_id + 41 cột features + label (Easy/Medium/Hard)
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from .ontology_bridge import Entity, OntologyEngine
from .jaccard import compute_jaccard_features
from .rsi import compute_rsi_features

# Giá trị cho đặc trưng KHÔNG TÍNH ĐƯỢC (thiếu PhoBERT, không khớp được thực
# thể nào, ...). Trước đây các trường hợp này trả 0.0 — nguy hiểm vì 0.0 là một
# giá trị HỢP LỆ mang nghĩa riêng ("không có nhầm lẫn", "các đáp án tách biệt
# tối đa"), nên thất bại trích xuất bị mô hình đọc thành tín hiệu thật, đúng
# lúc dữ liệu tệ nhất. XGBoost xử lý NaN gốc (tự học nhánh cho giá trị khuyết)
# nên không cần impute.
MISSING = float("nan")

# Đếm số lần từng đặc trưng bị khuyết trong một lần chạy batch, để
# batch_extract_features() báo cáo lại thay vì im lặng.
_missing_counts: Dict[str, int] = {}
_missing_reasons: Dict[str, str] = {}


def _mark_missing(features: Dict[str, float], names, reason: str) -> None:
    """Đánh dấu các đặc trưng là khuyết (NaN) và ghi nhận lý do."""
    for n in names:
        features[n] = MISSING
        _missing_counts[n] = _missing_counts.get(n, 0) + 1
        _missing_reasons.setdefault(n, reason)


@dataclass
class MCQ:
    """Một câu hỏi trắc nghiệm."""
    id: str
    stem: str
    correct: str
    distractors: List[str]
    difficulty: Optional[str] = None   # "Easy", "Medium", "Hard"
    source: Optional[str] = None       # Nguồn (chương, bài, ...)
    notes: Optional[str] = None        # Ghi chú bổ sung


@dataclass
class MCQFeatures:
    """Feature vector 41 chiều cho 1 MCQ (xem docstring đầu module)."""
    # Metadata
    mcq_id: str
    
    # ====== BLOCK A: KG-based (27 features) ======
    # A1: KG Structure (8)
    kg_num_correct_entities: int = 0
    kg_num_distractor_entities: float = 0.0
    kg_entity_diversity: float = 0.0
    kg_abstractness_mean: float = 0.0
    kg_bloom_level_mean: float = 0.0
    kg_prereq_depth_mean_correct: float = 0.0
    kg_prereq_depth_mean_distractors: float = 0.0
    kg_centrality_mean: float = 0.0
    
    # A2: Jaccard (8)
    jaccard_hard_max: float = 0.0
    jaccard_hard_mean: float = 0.0
    jaccard_soft_max: float = 0.0
    jaccard_soft_mean: float = 0.0
    jaccard_kg_max: float = 0.0
    jaccard_kg_mean: float = 0.0
    jaccard_stem_correct: float = 0.0
    jaccard_stem_distractor_max: float = 0.0
    
    # A3: RSI (8)
    rsi_correct: float = 0.0
    rsi_max_distractor: float = 0.0
    rsi_final: float = 0.0
    rsi_to_correct: float = 0.0
    rsi_eo_correct: float = 0.0
    rsi_sc_correct: float = 0.0
    rsi_dc: float = 0.0
    rsi_distractor_range: float = 0.0
    
    # ====== BLOCK B: KAD - Knowledge-Augmented Difficulty (3 features) 🆕 ======
    kad_entropy_stem: float = 0.0
    """Shannon Entropy of stem w.r.t. KG entity space. 
       Cao → stem chạm nhiều entities → KHÓ"""

    kad_entropy_correct: float = 0.0
    """Shannon Entropy of correct answer w.r.t. KG entity space.
       Cao → đáp án đúng có nhiều khía cạnh kiến thức"""

    kad_path_distance_mean: float = 0.5
    """Mean shortest path distance (normalized) between 
       correct entities and distractor entities in KG.
       Thấp → các đáp án gần nhau về khái niệm → KHÓ"""

    # ====== BLOCK C: Embedding Semantic Features (6 features) 🆕 ======
    emb_stem_distractor_mean_sim: float = 0.0
    """Mean cosine similarity between stem and all distractors.
       Cao → stem giống các đáp án sai → KHÓ"""

    emb_stem_distractor_max_sim: float = 0.0
    """Max cosine similarity between stem and any distractor.
       Cao → stem rất giống 1 distractor → KHÓ"""

    emb_stem_distractor_min_sim: float = 0.0
    """Min cosine similarity between stem and any distractor.
       Thấp → có ít nhất 1 distractor rất khác stem → DỄ"""

    emb_stem_distractor_std_sim: float = 0.0
    """Std dev of cosine similarities.
       Thấp → các distractors đồng đều → KHÓ"""

    emb_stem_correct_sim: float = 0.0
    """Cosine similarity between stem and correct answer.
       Cao → stem dẫn rõ đến đáp án đúng → DỄ"""

    emb_discriminative_power: float = 0.0
    """emb_stem_correct_sim - emb_stem_distractor_mean_sim.
       Cao → stem phân biệt rõ đúng/sai → DỄ
       Thấp/Âm → stem gây nhầm lẫn → KHÓ"""

    # ====== META: chất lượng khớp KG (1 feature) ======
    entity_match_coverage: float = 0.0
    """Tỉ lệ phương án (đáp án đúng + distractors) khớp được >=1 entity KG.
       Cho phép phân biệt "feature KG = 0 vì thật sự không nhầm lẫn" với
       "= 0 vì không khớp được entity" — thấp nghĩa là Block A ít tin cậy."""

    # ====== CỤM C (prereq_dag: Toán, Lý) — đáp án dạng số (4 features) ======
    # Chỉ được tính khi config.cluster == "prereq_dag"; môn khác giữ 0.0.
    numeric_answer_present: float = 0.0
    numeric_magnitude_ratio_to_correct: float = 0.0
    """Tỉ lệ distractor số lệch đáp án đúng một hệ số kinh điển (x0.5/x2/x4/x10...)."""
    numeric_reciprocal_swap_match: float = 0.0
    """Có distractor mang dấu vết đảo tử-mẫu tỉ số trong stem (lệch r^2 lần)."""
    numeric_same_formula_family: float = 0.0
    """Các Quantity khớp trong stem cùng thuộc một Formula tới mức nào (Lý)."""

    # ====== CỤM D (attributive_tree: Văn) — quan hệ thuộc tính (3 features) ======
    # Chỉ được tính khi config.cluster == "attributive_tree"; môn khác giữ 0.0.
    kg_same_author_correct_distractor: float = 0.0
    """Tỉ lệ distractor cùng tác giả với đáp án đúng (nhầm lẫn trong cụm tác giả)."""
    kg_same_period_correct_distractor: float = 0.0
    """Tỉ lệ distractor cùng giai đoạn văn học với đáp án đúng."""
    kg_shared_theme_device_jaccard: float = 0.0
    """Jaccard lớn nhất giữa tập chủ đề/biện pháp của đáp án đúng và distractor."""

    # Label (optional)
    label: Optional[str] = None
    
    @property
    def feature_vector(self) -> List[float]:
        """Trả về vector số (không bao gồm metadata & label)."""
        exclude = {"mcq_id", "label"}
        return [
            v for k, v in asdict(self).items()
            if k not in exclude and isinstance(v, (int, float))
        ]
    
    @property
    def feature_names(self) -> List[str]:
        """Trả về tên các features."""
        exclude = {"mcq_id", "label"}
        return [
            k for k, v in asdict(self).items()
            if k not in exclude and isinstance(v, (int, float))
        ]


def extract_single_mcq_features(
    mcq: MCQ,
    engine: OntologyEngine
) -> MCQFeatures:
    """
    Tính features cho một MCQ duy nhất (41 trường; 7 trường cuối gate theo cụm môn).
    
    Pipeline unified:
      1. Entity extraction (match KG entities)
      2. Jaccard + RSI + KG Structure (cần entities)
      3. KAD: Knowledge Entropy + Path Distance (cần embeddings)
      4. Embedding: PhoBERT cosine similarities (mọi text)
      5. Gom tất cả vào MCQFeatures
    """
    # === Bước 1: Entity Extraction ===
    stem_entities = engine.extract_entities_from_text(mcq.stem)
    correct_entities = engine.extract_entities_from_text(mcq.correct)
    distractors_entities = [
        engine.extract_entities_from_text(d) for d in mcq.distractors
    ]
    all_options = [mcq.correct] + mcq.distractors
    
    # === Bước 2: KG Features (Jaccard + RSI + Structure) ===
    jaccard_feats = compute_jaccard_features(
        stem_entities, correct_entities, distractors_entities, engine
    )
    rsi_feats = compute_rsi_features(
        mcq.stem, stem_entities, mcq.correct, correct_entities,
        mcq.distractors, distractors_entities, engine
    )
    kg_feats = _compute_kg_features(
        stem_entities, correct_entities, distractors_entities, engine
    )
    
    # === Bước 3: KAD Features (Entropy + Path Distance) ===
    kad_feats = _compute_kad_features(
        mcq, correct_entities, distractors_entities, engine
    )
    
    # === Bước 4: Embedding Features (PhoBERT cosine) ===
    emb_feats = _compute_embedding_features(
        mcq.stem, mcq.correct, mcq.distractors, engine
    )
    
    # === Bước 5: Gom tất cả ===
    features = MCQFeatures(mcq_id=mcq.id)
    
    # Block A
    features.kg_num_correct_entities = kg_feats["num_correct_entities"]
    features.kg_num_distractor_entities = kg_feats["num_distractor_entities"]
    features.kg_entity_diversity = kg_feats["entity_diversity"]
    features.kg_abstractness_mean = kg_feats["abstractness_mean"]
    features.kg_bloom_level_mean = kg_feats["bloom_level_mean"]
    features.kg_prereq_depth_mean_correct = kg_feats["prereq_depth_correct"]
    features.kg_prereq_depth_mean_distractors = kg_feats["prereq_depth_distractors"]
    features.kg_centrality_mean = kg_feats["centrality_mean"]
    
    for k, v in jaccard_feats.items():
        if hasattr(features, k):
            setattr(features, k, v)
    
    for k, v in rsi_feats.items():
        if hasattr(features, k):
            setattr(features, k, v)
    
    # Block B
    for k, v in kad_feats.items():
        if hasattr(features, k):
            setattr(features, k, v)
    
    # Block C
    for k, v in emb_feats.items():
        if hasattr(features, k):
            setattr(features, k, v)

    # Meta: độ phủ khớp entity trên các phương án
    option_entities = [correct_entities] + distractors_entities
    features.entity_match_coverage = (
        sum(1 for ents in option_entities if ents) / len(option_entities)
    )

    # === Bước 6: Feature riêng theo cụm môn (xem shared/subjects.py) ===
    cluster = engine.config.cluster if engine.config is not None else "history"
    if cluster == "prereq_dag":
        from .numeric_features import compute_numeric_features
        for k, v in compute_numeric_features(
            mcq.stem, mcq.correct, mcq.distractors, stem_entities, engine
        ).items():
            setattr(features, k, v)
    elif cluster == "attributive_tree":
        from .literature_features import compute_literature_features
        for k, v in compute_literature_features(
            correct_entities, distractors_entities, engine
        ).items():
            setattr(features, k, v)

    # Label
    features.label = mcq.difficulty

    return features


def _compute_kg_features(
    stem_entities: List[Entity],
    correct_entities: List[Entity],
    distractors_entities: List[List[Entity]],
    engine: OntologyEngine
) -> Dict[str, float]:
    """Tính KG-based features (Block A1)."""
    features = {}
    
    # Số entity
    features["num_correct_entities"] = float(len(correct_entities))
    distractor_counts = [len(d) for d in distractors_entities]
    features["num_distractor_entities"] = float(
        sum(distractor_counts) / len(distractor_counts) if distractor_counts else 0.0
    )
    
    # Entity diversity: tỷ lệ entity unique / total
    all_uris = set()
    total = 0
    for e in correct_entities:
        all_uris.add(e.uri)
        total += 1
    for d_ents in distractors_entities:
        for e in d_ents:
            all_uris.add(e.uri)
            total += 1
    features["entity_diversity"] = float(len(all_uris) / total) if total > 0 else 0.0
    
    # Abstractness — su9:abstractness chỉ được emit cho Period/Location/Person/
    # Organization/Concept (subjects/history/build.py:emit_static_entity); lớp
    # Event (emit_dynamic_entity) KHÔNG BAO GIỜ có trường này trong dữ liệu
    # nguồn (không phải build.py quên emit — data/*/events_*.py không có
    # field "abstractness"/"bloom" nào). Câu hỏi Lịch sử phần lớn khớp vào
    # Event -> abs_vals rỗng -> trước đây trả 0.0 giả (giống lỗi T5.2), nay NaN.
    abs_vals = [
        e.abstractness for e in correct_entities
        if e.abstractness is not None
    ]
    for d_ents in distractors_entities:
        for e in d_ents:
            if e.abstractness is not None:
                abs_vals.append(e.abstractness)
    if abs_vals:
        features["abstractness_mean"] = float(sum(abs_vals) / len(abs_vals))
    else:
        _mark_missing(features, ["abstractness_mean"],
                      "không có entity nào (thường là lớp Event) mang thuộc tính abstractness")

    # Bloom Level — chỉ Concept có su9:bloomLevel; cùng lý do như trên.
    bloom_vals = [
        e.bloom_level for e in correct_entities
        if e.bloom_level is not None
    ]
    for d_ents in distractors_entities:
        for e in d_ents:
            if e.bloom_level is not None:
                bloom_vals.append(e.bloom_level)
    if bloom_vals:
        features["bloom_level_mean"] = float(sum(bloom_vals) / len(bloom_vals))
    else:
        _mark_missing(features, ["bloom_level_mean"],
                      "không có entity nào (thường là lớp Event) mang thuộc tính bloomLevel")
    
    # Prerequisite depth
    prereq_correct = [
        engine.prerequisite_depth(e.uri)
        for e in correct_entities
    ]
    features["prereq_depth_correct"] = float(
        sum(prereq_correct) / len(prereq_correct) if prereq_correct else 0.0
    )
    prereq_dist = []
    for d_ents in distractors_entities:
        for e in d_ents:
            prereq_dist.append(engine.prerequisite_depth(e.uri))
    features["prereq_depth_distractors"] = float(
        sum(prereq_dist) / len(prereq_dist) if prereq_dist else 0.0
    )
    
    # Centrality
    cent_vals = []
    for e in correct_entities:
        cent_vals.append(engine.centrality(e.uri))
    for d_ents in distractors_entities:
        for e in d_ents:
            cent_vals.append(engine.centrality(e.uri))
    features["centrality_mean"] = float(
        sum(cent_vals) / len(cent_vals) if cent_vals else 0.0
    )
    
    return features


def _compute_kad_features(
    mcq: MCQ,
    correct_entities: List[Entity],
    distractors_entities: List[List[Entity]],
    engine: OntologyEngine
) -> Dict[str, float]:
    """
    Tính KAD features (Block B).
    
    Knowledge-Augmented Difficulty dựa trên:
      1. Shannon Entropy: Đo khối lượng thông tin trong KG space
      2. Graph Path Distance: Đo khoảng cách khái niệm giữa đáp án

    Chỉ 2 feature entropy hoạt động mọi lúc (knowledge_entropy() dùng embedding
    chứ không dùng text matching). Ngược lại kad_path_distance_mean CẦN khớp
    được thực thể ở đáp án đúng và ít nhất một đáp án nhiễu — không khớp được
    thì trả NaN (khuyết), xem MISSING ở đầu module.
    """
    features = {}

    # === 1. Knowledge Entropy ===
    try:
        features["kad_entropy_stem"] = engine.knowledge_entropy(mcq.stem)
    except Exception as e:
        _mark_missing(features, ["kad_entropy_stem"],
                      f"knowledge_entropy(stem) lỗi: {type(e).__name__}")

    try:
        features["kad_entropy_correct"] = engine.knowledge_entropy(mcq.correct)
    except Exception as e:
        _mark_missing(features, ["kad_entropy_correct"],
                      f"knowledge_entropy(correct) lỗi: {type(e).__name__}")

    # === 2. Path Distance ===
    # Distance giữa correct và từng distractor (nếu có entities).
    # LƯU Ý: đặc trưng này CẦN khớp được thực thể ở cả đáp án đúng lẫn ít nhất
    # một đáp án nhiễu — docstring cũ ghi "hoạt động mọi lúc" là sai (chỉ 2
    # feature entropy mới không cần khớp thực thể). Khi không khớp được, trước
    # đây trả hằng 0.5 ("neutral") — một con số bịa trông như dữ liệu thật;
    # nay đánh dấu khuyết.
    path_dists = []
    if correct_entities:
        for d_ents in distractors_entities:
            if d_ents:
                # Lấy khoảng cách ngắn nhất giữa bất kỳ cặp entity nào
                d = min(
                    engine.path_distance(e_c.uri, e_d.uri)
                    for e_c in correct_entities
                    for e_d in d_ents
                )
                path_dists.append(d)

    if path_dists:
        features["kad_path_distance_mean"] = float(np.mean(path_dists))
    else:
        _mark_missing(features, ["kad_path_distance_mean"],
                      "không khớp được thực thể ở đáp án đúng và/hoặc nhiễu")

    return features


def _compute_embedding_features(
    stem: str,
    correct: str,
    distractors: List[str],
    engine: OntologyEngine
) -> Dict[str, float]:
    """
    Tính Embedding features (Block C).
    
    Dùng PhoBERT cosine similarity để đo:
      - Mức độ giống nhau giữa stem và các options
      - Discriminative power của stem
    
    Không cần entity matching → hoạt động với MỌI câu hỏi.
    """
    features = {}
    
    try:
        cache = engine.embedding_cache()
        v_stem = cache.embed_text(stem)
        v_correct = cache.embed_text(correct)
        v_distractors = [cache.embed_text(d) for d in distractors]
        
        # Cosine similarity: stem vs distractors
        stem_dist_sims = [
            float(np.dot(v_stem, v_d) / (np.linalg.norm(v_stem) * np.linalg.norm(v_d) + 1e-10))
            for v_d in v_distractors
        ]
        
        features["emb_stem_distractor_mean_sim"] = float(np.mean(stem_dist_sims))
        features["emb_stem_distractor_max_sim"] = float(np.max(stem_dist_sims))
        features["emb_stem_distractor_min_sim"] = float(np.min(stem_dist_sims))
        features["emb_stem_distractor_std_sim"] = float(np.std(stem_dist_sims)) if len(stem_dist_sims) > 1 else 0.0
        
        # Cosine similarity: stem vs correct
        stem_correct_sim = float(
            np.dot(v_stem, v_correct) / (np.linalg.norm(v_stem) * np.linalg.norm(v_correct) + 1e-10)
        )
        features["emb_stem_correct_sim"] = stem_correct_sim
        
        # Discriminative power
        features["emb_discriminative_power"] = stem_correct_sim - features["emb_stem_distractor_mean_sim"]
        
    except Exception as e:
        # Không load được PhoBERT (hoặc lỗi khi embed): đánh dấu KHUYẾT, không
        # trả 0.0 — cosine 0.0 nghĩa là "stem và đáp án trực giao về ngữ nghĩa",
        # một tín hiệu mạnh và sai hoàn toàn so với "không đo được".
        _mark_missing(features, [
            "emb_stem_distractor_mean_sim", "emb_stem_distractor_max_sim",
            "emb_stem_distractor_min_sim", "emb_stem_distractor_std_sim",
            "emb_stem_correct_sim", "emb_discriminative_power",
        ], f"PhoBERT lỗi: {type(e).__name__}: {e}")

    return features


def batch_extract_features(
    mcqs: List[MCQ],
    engine: OntologyEngine,
    verbose: bool = True
) -> List[MCQFeatures]:
    """
    Tính features cho một batch MCQs.
    
    Args:
        mcqs: Danh sách MCQ
        engine: OntologyEngine đã load
        verbose: In log quá trình
    
    Returns:
        List[MCQFeatures]
    """
    _missing_counts.clear()
    _missing_reasons.clear()

    results = []
    n_failed = 0
    for i, mcq in enumerate(mcqs):
        if verbose:
            print(f"[{i+1}/{len(mcqs)}] Đang xử lý: {mcq.id}...", end=" ", flush=True)

        try:
            feats = extract_single_mcq_features(mcq, engine)
            results.append(feats)
            if verbose:
                print(f"OK (entropy_stem={feats.kad_entropy_stem:.3f}, disc_pow={feats.emb_discriminative_power:.3f})")
        except Exception as e:
            n_failed += 1
            if verbose:
                print(f"LỖI: {e}")

    report_missing(results, n_total=len(mcqs), n_failed=n_failed)
    return results


def report_missing(features_list, n_total: int = 0, n_failed: int = 0) -> Dict[str, int]:
    """In tỉ lệ khuyết của từng đặc trưng sau một lần chạy batch.

    Đếm trực tiếp NaN trên vector kết quả — bắt được cả NaN sinh ra ngoài
    module này (ví dụ rsi_dc trong rsi.py), không chỉ những chỗ có gọi
    _mark_missing().

    Bắt buộc nhìn vào con số này trước khi tin kết quả: đặc trưng khuyết tỉ lệ
    cao nghĩa là mô hình gần như không có tín hiệu ở đó, và phải nêu trong báo
    cáo thay vì để 0.0 giả làm nó trông như đang hoạt động.
    """
    n_total = n_total or len(features_list)
    if n_failed:
        print(f"\n  ⚠ {n_failed}/{n_total} câu lỗi hoàn toàn (không có feature).")
    if not features_list:
        return {}

    skip = {"mcq_id", "label"}
    counts: Dict[str, int] = {}
    for f in features_list:
        for k, v in asdict(f).items():
            if k in skip or not isinstance(v, float):
                continue
            if v != v:  # NaN
                counts[k] = counts.get(k, 0) + 1

    if not counts:
        print(f"\n  Không có đặc trưng nào khuyết trên {n_total} câu.")
        return counts

    print(f"\n  Đặc trưng KHUYẾT (NaN) trên {n_total} câu:")
    for name, cnt in sorted(counts.items(), key=lambda kv: -kv[1]):
        pct = cnt / n_total if n_total else 0.0
        flag = "  ← khuyết >50%, phải nêu trong báo cáo" if pct > 0.5 else ""
        print(f"    {name:<34} {cnt:>5}/{n_total} ({pct:>5.1%}){flag}")
    reasons = {k: v for k, v in _missing_reasons.items() if k in counts}
    if reasons:
        print("  Lý do (lần đầu gặp):")
        for name, reason in sorted(reasons.items()):
            print(f"    {name:<34} {reason}")
    return counts


def features_to_dataframe(features_list: List[MCQFeatures]) -> "pd.DataFrame":
    """
    Chuyển đổi features thành pandas DataFrame.
    
    Returns:
        pd.DataFrame: mcq_id + 41 cột features + label
    """
    import pandas as pd
    
    rows = []
    for feats in features_list:
        row = asdict(feats)
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Sắp xếp cột: metadata -> features -> label
    meta_cols = ["mcq_id"]
    label_col = "label"
    feat_cols = [c for c in df.columns if c not in meta_cols + [label_col]]
    df = df[meta_cols + feat_cols + [label_col]]
    
    return df


def train_xgboost(
    features_list: List[MCQFeatures],
    test_size: float = 0.2,
    random_state: int = 42,
    cv_folds: int = 0,
    groups: Optional[Dict[str, int]] = None,
) -> dict:
    """
    Huấn luyện XGBoost classifier.

    Args:
        features_list: Danh sách features đã gán nhãn
        test_size: Tỷ lệ test (bỏ qua khi cv_folds > 0)
        random_state: Seed
        cv_folds: >0 thì đánh giá bằng k-fold CV (ổn định hơn 1 lần split,
            khuyến nghị 5); model trả về vẫn fit trên toàn bộ data
        groups: map mcq_id -> dup_group. Có thì dùng StratifiedGroupKFold để
            mọi bản sao của cùng một nội dung nằm CÙNG một fold — chặn rò rỉ
            mà vẫn giữ được toàn bộ dữ liệu để train. Không có thì rơi về
            StratifiedKFold (chỉ an toàn nếu đã lọc trùng từ trước).

    Returns:
        Dict chứa model, accuracy, classification report
    """
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import (StratifiedGroupKFold, StratifiedKFold,
                                         cross_val_predict, train_test_split)
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import accuracy_score, classification_report
    import xgboost as xgb

    # Tạo DataFrame
    df = features_to_dataframe(features_list)

    # Lọc các dòng có label
    df_labeled = df[df["label"].notna()].copy()

    if len(df_labeled) < 10:
        return {"error": f"Not enough labeled data ({len(df_labeled)} samples)"}

    # Encode labels
    le = LabelEncoder()
    y = le.fit_transform(df_labeled["label"].values)

    # Feature matrix
    feat_cols = [c for c in df_labeled.columns
                 if c not in ["mcq_id", "label"]]
    X = df_labeled[feat_cols].values

    # Class weight cân bằng (n / (k * n_c)) — kéo recall lớp thiểu số (Hard)
    counts = np.bincount(y)
    class_w = len(y) / (len(counts) * counts.astype(float))
    weight_of = lambda yy: class_w[yy]

    def make_model():
        return xgb.XGBClassifier(
            n_estimators=600,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=2,
            objective="multi:softmax",
            num_class=len(le.classes_),
            random_state=random_state,
            eval_metric="mlogloss",
            n_jobs=-1,
        )

    cv_scheme = None
    if cv_folds > 0:
        g = None
        if groups:
            g = np.array([groups.get(i, -1) for i in df_labeled["mcq_id"]])
            if (g == -1).any():
                n_miss = int((g == -1).sum())
                print(f"  ⚠ {n_miss} câu không có dup_group — mỗi câu tự thành "
                      f"một nhóm riêng.")
                # id âm duy nhất cho từng câu thiếu nhóm, tránh gộp nhầm chúng
                # thành CÙNG một nhóm khổng lồ
                g[g == -1] = -np.arange(1, n_miss + 1)

        if g is not None:
            cv = StratifiedGroupKFold(n_splits=cv_folds, shuffle=True,
                                      random_state=random_state)
            cv_scheme = f"StratifiedGroupKFold({cv_folds}, groups=dup_group)"
            splits = list(cv.split(X, y, groups=g))
            # Bảo hiểm: không nhóm nào được nằm ở cả train lẫn test
            for tr, te in splits:
                assert not (set(g[tr]) & set(g[te])), "rò rỉ nhóm giữa các fold!"
            y_pred = cross_val_predict(make_model(), X, y, cv=splits,
                                       params={"sample_weight": weight_of(y)})
        else:
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True,
                                 random_state=random_state)
            cv_scheme = f"StratifiedKFold({cv_folds}) — KHÔNG chặn nhóm trùng"
            y_pred = cross_val_predict(make_model(), X, y, cv=cv,
                                       params={"sample_weight": weight_of(y)})
        y_eval = y
        model = make_model()
        model.fit(X, y, sample_weight=weight_of(y))
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        model = make_model()
        model.fit(X_train, y_train, sample_weight=weight_of(y_train))
        y_pred = model.predict(X_test)
        y_eval = y_test

    accuracy = accuracy_score(y_eval, y_pred)
    report = classification_report(y_eval, y_pred, target_names=le.classes_)
    
    # Feature importance
    importance = pd.DataFrame({
        "feature": feat_cols,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)
    
    return {
        "model": model,
        "label_encoder": le,
        "accuracy": accuracy,
        "classification_report": report,
        "feature_importance": importance,
        "n_samples": len(df_labeled),
        "cv_scheme": cv_scheme,
    }


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    repo_root = Path(__file__).resolve().parents[2]
    engine = OntologyEngine(repo_root / "subjects" / "history" / "ontology" / "su9.ttl")

    # Test với 1 MCQ
    mcq = MCQ(
        id="test_001",
        stem="Nguyên nhân sâu xa dẫn đến bùng nổ Chiến tranh thế giới thứ hai là gì?",
        correct="Sự phát triển không đều của chủ nghĩa tư bản",
        distractors=[
            "Chính sách thỏa hiệp, nhượng bộ của Anh, Pháp",
            "Sự xuất hiện của chủ nghĩa phát xít",
            "Khủng hoảng kinh tế 1929-1933"
        ],
        difficulty="Medium"
    )
    
    feats = extract_single_mcq_features(mcq, engine)
    print(f"=== Feature Vector 41 chiều cho MCQ: {mcq.id} ===")
    print(f"Label: {feats.label}")
    
    print(f"\nBlock A1 - KG Structure ({len([n for n in feats.feature_names if n.startswith('kg_')])} features):")
    for name in feats.feature_names:
        if name.startswith("kg_"):
            print(f"  {name}: {getattr(feats, name):.4f}")
    
    print(f"\nBlock A2 - Jaccard ({len([n for n in feats.feature_names if n.startswith('jaccard_')])} features):")
    for name in feats.feature_names:
        if name.startswith("jaccard_"):
            print(f"  {name}: {getattr(feats, name):.4f}")
    
    print(f"\nBlock A3 - RSI ({len([n for n in feats.feature_names if n.startswith('rsi_')])} features):")
    for name in feats.feature_names:
        if name.startswith("rsi_"):
            print(f"  {name}: {getattr(feats, name):.4f}")
    
    print(f"\n🆕 Block B - KAD ({len([n for n in feats.feature_names if n.startswith('kad_')])} features):")
    for name in feats.feature_names:
        if name.startswith("kad_"):
            print(f"  {name}: {getattr(feats, name):.4f}")
    
    print(f"\n🆕 Block C - Embedding ({len([n for n in feats.feature_names if n.startswith('emb_')])} features):")
    for name in feats.feature_names:
        if name.startswith("emb_"):
            print(f"  {name}: {getattr(feats, name):.4f}")
    
    print(f"\nTotal features: {len(feats.feature_vector)}")
    print(f"Feature names: {feats.feature_names}")
