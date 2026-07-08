"""
MCQ Difficulty Estimation Pipeline v4.1
=========================================
Sử dụng Knowledge Graph (Ontology) + Knowledge Entropy + Embedding
cho Lịch sử 9 để dự đoán độ khó của câu hỏi trắc nghiệm
và cung cấp Explainable AI (XAI).

33 Features | 3 Blocks | Unified Pipeline
  Block A (KG):       24 features - Jaccard + RSI + KG Structure
  Block B (KAD):       3 features - Knowledge Entropy + Path Distance
  Block C (Embedding): 6 features - PhoBERT cosine similarities

Modules:
  - ontology_bridge: Load TTL ontology → NetworkX graph + KAD API
  - embedding_cache: Pre-compute PhoBERT embeddings cho entities
  - jaccard: 3-level Jaccard similarity (hard/soft/kg-weighted)
  - rsi: Relation Strength Indicativeness + 4-component decomposition
  - features: 33 features across 3 blocks for XGBoost
  - demo: End-to-end pipeline demo
"""

from .ontology_bridge import OntologyEngine, Entity
from .embedding_cache import EntityEmbeddingCache
from .jaccard import (
    jaccard_hard, jaccard_soft, jaccard_kg_weighted,
    compute_jaccard_features
)
from .rsi import compute_rsi_features, analyze_rsi_decomposition
from .features import (
    MCQ, MCQFeatures,
    extract_single_mcq_features, batch_extract_features,
    features_to_dataframe, train_xgboost
)
