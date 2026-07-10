"""
Feature Engineering Module v4.1
================================
Tổng hợp features từ 3 blocks thành vector đặc trưng 33 chiều:

  Block A (KG):       24 features - Jaccard + RSI + KG Structure
  Block B (KAD):       3 features - Knowledge Entropy + Path Distance 🆕
  Block C (Embedding): 6 features - PhoBERT cosine similarities 🆕

Pipeline unified: Mọi câu hỏi (dù có match entity hay không)
đều được tính đầy đủ 33 features → XGBoost tự học pattern.

Lý thuyết nền tảng:
  - Shannon Entropy (1948): Đo khối lượng thông tin trong câu hỏi
  - Graph Theory (Euler, 1736): Khoảng cách khái niệm giữa các đáp án
  - Semantic Similarity: Mức độ nhầm lẫn ngữ nghĩa giữa stem và options

Output: DataFrame với 33 cột features + label (Easy/Medium/Hard)
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
    """Feature vector 33 chiều cho 1 MCQ."""
    # Metadata
    mcq_id: str
    
    # ====== BLOCK A: KG-based (24 features) ======
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
    Tính features cho một MCQ duy nhất (33 features).
    
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
    
    # Abstractness
    abs_vals = [
        e.abstractness for e in correct_entities
        if e.abstractness is not None
    ]
    for d_ents in distractors_entities:
        for e in d_ents:
            if e.abstractness is not None:
                abs_vals.append(e.abstractness)
    features["abstractness_mean"] = float(
        sum(abs_vals) / len(abs_vals) if abs_vals else 0.0
    )
    
    # Bloom Level
    bloom_vals = [
        e.bloom_level for e in correct_entities
        if e.bloom_level is not None
    ]
    for d_ents in distractors_entities:
        for e in d_ents:
            if e.bloom_level is not None:
                bloom_vals.append(e.bloom_level)
    features["bloom_level_mean"] = float(
        sum(bloom_vals) / len(bloom_vals) if bloom_vals else 0.0
    )
    
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
    
    Các feature này hoạt động MỌI LÚC, kể cả khi không match entity,
    vì knowledge_entropy() dùng embedding chứ không dùng text matching.
    """
    features = {}
    
    # === 1. Knowledge Entropy ===
    try:
        features["kad_entropy_stem"] = engine.knowledge_entropy(mcq.stem)
    except Exception:
        features["kad_entropy_stem"] = 0.0
    
    try:
        features["kad_entropy_correct"] = engine.knowledge_entropy(mcq.correct)
    except Exception:
        features["kad_entropy_correct"] = 0.0
    
    # === 2. Path Distance ===
    # Distance giữa correct và từng distractor (nếu có entities)
    if correct_entities:
        path_dists = []
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
            features["kad_path_distance_mean"] = 0.5  # fallback
    else:
        features["kad_path_distance_mean"] = 0.5  # fallback: neutral
    
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
        # Fallback: nếu không load được PhoBERT, dùng giá trị mặc định
        features["emb_stem_distractor_mean_sim"] = 0.0
        features["emb_stem_distractor_max_sim"] = 0.0
        features["emb_stem_distractor_min_sim"] = 0.0
        features["emb_stem_distractor_std_sim"] = 0.0
        features["emb_stem_correct_sim"] = 0.0
        features["emb_discriminative_power"] = 0.0
    
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
    results = []
    for i, mcq in enumerate(mcqs):
        if verbose:
            print(f"[{i+1}/{len(mcqs)}] Đang xử lý: {mcq.id}...", end=" ", flush=True)
        
        try:
            feats = extract_single_mcq_features(mcq, engine)
            results.append(feats)
            if verbose:
                print(f"OK (entropy_stem={feats.kad_entropy_stem:.3f}, disc_pow={feats.emb_discriminative_power:.3f})")
        except Exception as e:
            if verbose:
                print(f"LỖI: {e}")
    
    return results


def features_to_dataframe(features_list: List[MCQFeatures]) -> "pd.DataFrame":
    """
    Chuyển đổi features thành pandas DataFrame.
    
    Returns:
        pd.DataFrame: 33 cột features + label
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
    random_state: int = 42
) -> dict:
    """
    Huấn luyện XGBoost classifier.
    
    Args:
        features_list: Danh sách features đã gán nhãn
        test_size: Tỷ lệ test
        random_state: Seed
    
    Returns:
        Dict chứa model, accuracy, classification report
    """
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split
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
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Huấn luyện XGBoost
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        objective="multi:softmax",
        num_class=len(le.classes_),
        random_state=random_state,
        use_label_encoder=False,
        eval_metric="mlogloss",
    )
    model.fit(X_train, y_train)
    
    # Đánh giá
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, target_names=le.classes_)
    
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
    print(f"=== Feature Vector 33 chiều cho MCQ: {mcq.id} ===")
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
