"""
Demo: End-to-End MCQ Difficulty Estimation Pipeline v4.1
===========================================================
Pipeline đầy đủ với 33 features (3 blocks):
  Block A (KG):       24 features - Jaccard + RSI + KG Structure
  Block B (KAD):       3 features - Knowledge Entropy + Path Distance 🆕
  Block C (Embedding): 6 features - PhoBERT cosine similarities 🆕

Usage:
  python mcq_pipeline/demo.py
"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ontology_bridge import OntologyEngine
from features import MCQ, extract_single_mcq_features, batch_extract_features
from rsi import analyze_rsi_decomposition


def load_mcqs(json_path: str) -> list:
    """Load MCQs from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    mcqs = []
    for item in data:
        mcq = MCQ(
            id=item["id"],
            stem=item["stem"],
            correct=item["correct"],
            distractors=item["distractors"],
            difficulty=item.get("difficulty"),
            source=item.get("source"),
        )
        mcqs.append(mcq)
    
    return mcqs


def display_report(mcq: MCQ, engine: OntologyEngine):
    """Display full report for one MCQ with XAI explanation."""
    # Compute features (33-d vector)
    feats = extract_single_mcq_features(mcq, engine)
    
    # Re-extract entities for XAI
    stem_entities = engine.extract_entities_from_text(mcq.stem)
    correct_entities = engine.extract_entities_from_text(mcq.correct)
    distractors_entities = [
        engine.extract_entities_from_text(d) for d in mcq.distractors
    ]
    
    # RSI decomposition for XAI
    report = analyze_rsi_decomposition(
        mcq.stem, stem_entities,
        mcq.correct, correct_entities,
        mcq.distractors, distractors_entities,
        engine
    )
    
    print("=" * 80)
    print(f"  Câu hỏi: {mcq.id}")
    print(f"  Stem:    {mcq.stem}")
    print(f"  Đúng:    {mcq.correct}")
    for i, d in enumerate(mcq.distractors):
        print(f"  Sai {i+1}:   {d}")
    print(f"  Nhãn gốc: {mcq.difficulty} | Dự đoán RSI: {report['verdict']}")
    print("=" * 80)
    
    # === Block A: KG Features ===
    print(f"\n  [Block A - KG Features (24)]")
    print(f"  ├─ A1 - KG Structure:")
    for name in feats.feature_names:
        val = getattr(feats, name)
        if name.startswith("kg_"):
            print(f"  │   {name}: {val:.4f}")
    print(f"  ├─ A2 - Jaccard:")
    for name in feats.feature_names:
        val = getattr(feats, name)
        if name.startswith("jaccard_"):
            print(f"  │   {name}: {val:.4f}")
    print(f"  └─ A3 - RSI:")
    for name in feats.feature_names:
        val = getattr(feats, name)
        if name.startswith("rsi_"):
            print(f"      {name}: {val:.4f}")
    
    # === Block B: KAD Features 🆕 ===
    print(f"\n  🆕 [Block B - Knowledge-Augmented Difficulty]")
    for name in feats.feature_names:
        val = getattr(feats, name)
        if name.startswith("kad_"):
            print(f"      {name}: {val:.4f}")
    
    # === Block C: Embedding Features 🆕 ===
    print(f"\n  🆕 [Block C - Embedding Semantic Features]")
    for name in feats.feature_names:
        val = getattr(feats, name)
        if name.startswith("emb_"):
            print(f"      {name}: {val:.4f}")
    
    # === XAI Explanation ===
    print(f"\n  [Explainable AI - Phân tích chi tiết]")
    print(f"  ├─ Term Overlap: {report['components']['term_overlap']['explanation']}")
    print(f"  ├─ Entity Overlap: {report['components']['entity_overlap']['explanation']}")
    print(f"  ├─ Semantic Closeness: {report['components']['semantic_closeness']['explanation']}")
    print(f"  └─ Distractor Confusion: {report['components']['distractor_confusion']['explanation']}")
    
    print(f"\n  → Kết luận: {report['summary']}")
    print(f"  → Gợi ý: {report['suggestion']}")
    
    # === KAD Analysis ===
    print(f"\n  [Knowledge-Augmented Difficulty Analysis]")
    if feats.kad_entropy_stem < 0.3:
        entropy_verdict = "Stem chỉ chạm 1-2 entities → DỄ (câu hỏi hẹp)"
    elif feats.kad_entropy_stem < 0.6:
        entropy_verdict = "Stem chạm vài entities → TRUNG BÌNH"
    else:
        entropy_verdict = "Stem chạm nhiều entities → KHÓ (câu hỏi rộng)"
    print(f"  ├─ Knowledge Entropy (stem): {feats.kad_entropy_stem:.3f} → {entropy_verdict}")
    
    if feats.kad_path_distance_mean < 0.3:
        path_verdict = "Các đáp án gần nhau trên KG → KHÓ (dễ nhầm)"
    elif feats.kad_path_distance_mean < 0.6:
        path_verdict = "TRUNG BÌNH"
    else:
        path_verdict = "Các đáp án xa nhau trên KG → DỄ (dễ phân biệt)"
    print(f"  ├─ Path Distance (correct-distractors): {feats.kad_path_distance_mean:.3f} → {path_verdict}")
    
    if feats.emb_discriminative_power > 0.15:
        disc_verdict = "Stem phân biệt rõ → DỄ"
    elif feats.emb_discriminative_power > 0.0:
        disc_verdict = "Stem khá rõ → TRUNG BÌNH"
    else:
        disc_verdict = "Stem gây nhầm lẫn → KHÓ"
    print(f"  └─ Discriminative Power: {feats.emb_discriminative_power:.3f} → {disc_verdict}")
    
    print()


def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    here = Path(__file__).resolve().parent.parent
    
    print("=" * 80)
    print("  MCQ DIFFICULTY ESTIMATION PIPELINE v4.1")
    print("  Sử dụng Knowledge Graph + Knowledge Entropy + Embedding")
    print("  33 features | 3 blocks | Unified Pipeline")
    print("=" * 80)
    
    # Bước 1: Load Ontology
    print("\n[1/4] Đang load Ontology...")
    ttl_path = here / "output" / "su9.ttl"
    if not ttl_path.exists():
        print(f"  ❌ Không tìm thấy file {ttl_path}")
        print("  Hãy chạy 'python build_main.py' trước.")
        return
    
    engine = OntologyEngine(ttl_path)
    print(f"  ✅ Đã load {len(engine)} entities từ Ontology")
    print(f"  ✅ Đã pre-compute {len(engine.entity_label_list)} entity labels")
    print(f"  ✅ Đã pre-compute all-pairs shortest paths (diameter={engine._graph_diameter})")
    
    # Bước 2: Load MCQs
    print("\n[2/4] Đang load MCQ samples...")
    json_path = here / "mcq_pipeline" / "mcq_samples.json"
    if not json_path.exists():
        json_path = here / "mcq_samples.json"
    
    mcqs = load_mcqs(json_path)
    print(f"  ✅ Đã load {len(mcqs)} câu hỏi trắc nghiệm")
    
    # Bước 3: Tính features
    print("\n[3/4] Đang tính features cho từng câu hỏi...")
    print("  (Lần đầu sẽ load PhoBERT ~5s, các lần sau nhanh hơn)")
    features_list = batch_extract_features(mcqs, engine, verbose=True)
    print(f"  ✅ Đã tính xong {len(features_list)} feature vectors (33 features/vector)")
    
    # Bước 4: Báo cáo
    print("\n[4/4] Xuất báo cáo Explainable AI...")
    for mcq in mcqs:
        display_report(mcq, engine)
    
    # Tổng kết
    print("=" * 80)
    print("  TỔNG KẾT")
    print("=" * 80)
    print(f"  Ontology: {len(engine)} entities, {engine.nx_graph.number_of_edges()} quan hệ")
    print(f"  Số MCQ:   {len(mcqs)}")
    print(f"  Features: {len(features_list[0].feature_vector) if features_list else 0} features/vector")
    print(f"  Blocks:   KG(24) + KAD(3) + Embedding(6)")
    
    # Phân bố khó dễ
    print(f"\n  Phân bố khó dễ theo RSI:")
    from collections import Counter
    verdicts = []
    for mcq in mcqs:
        stem_entities = engine.extract_entities_from_text(mcq.stem)
        correct_entities = engine.extract_entities_from_text(mcq.correct)
        distractors_entities = [
            engine.extract_entities_from_text(d) for d in mcq.distractors
        ]
        report = analyze_rsi_decomposition(
            mcq.stem, stem_entities,
            mcq.correct, correct_entities,
            mcq.distractors, distractors_entities,
            engine
        )
        verdicts.append(report["verdict"])
    
    counter = Counter(verdicts)
    for k, v in sorted(counter.items()):
        print(f"    {k}: {v} câu ({v/len(mcqs)*100:.0f}%)")
    
    print("\n  ✅ Pipeline v4.1 hoàn tất!")
    print(f"  🔬 KAD: Knowledge Entropy + Graph Path Distance")
    print(f"  🔬 Embedding: PhoBERT cosine similarities")


if __name__ == "__main__":
    main()
