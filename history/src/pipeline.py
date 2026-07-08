"""
End-to-end pipeline: question(s) -> ontology features -> pandas DataFrame.

Usage:
    from pipeline import Su9DifficultyPipeline
    pipe = Su9DifficultyPipeline("ontology/su9.ttl")
    df = pipe.featurize(["Cau hoi 1", "Cau hoi 2", ...])
    # df is ready for XGBoost .fit / .predict
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

import pandas as pd

from ontology_loader import OntologyStore
from entity_extraction import EntityExtractor, Mention
from feature_extraction import FeatureExtractor, QuestionFeatures


class Su9DifficultyPipeline:
    """Wraps the ontology, entity extractor, and feature extractor."""

    def __init__(self, ttl_path: Union[str, Path], use_ner: bool = False):
        self.store = OntologyStore(ttl_path)
        self.extractor = EntityExtractor(self.store, use_ner=use_ner)
        self.fe = FeatureExtractor(self.store)

    # ------------------------------------------------------------------
    def featurize_one(self, question: str) -> QuestionFeatures:
        mentions = self.extractor.extract(question)
        return self.fe.extract(question, mentions)

    def featurize(
        self,
        questions: List[str],
        ids: Optional[List[str]] = None,
        include_meta: bool = False,
    ) -> pd.DataFrame:
        """Return a DataFrame where each row is a question's feature vector."""
        rows: List[Dict] = []
        for i, q in enumerate(questions):
            feat = self.featurize_one(q)
            row: Dict = {"question_id": ids[i] if ids else f"q{i+1}", "question": q}
            row.update(feat.values)
            if include_meta:
                row["linked_labels"] = "; ".join(feat.meta["linked_labels"])
                row["inferred_bloom"] = feat.meta["inferred_bloom"]
            rows.append(row)
        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    def explain(self, question: str) -> Dict:
        """Return a detailed explanation of how features were computed for one question.
        Useful for SHAP-style per-question inspection or manual error analysis.
        """
        mentions = self.extractor.extract(question)
        feat = self.fe.extract(question, mentions)
        return {
            "question": question,
            "mentions": [
                {"surface": m.surface, "uri": m.uri, "class": m.cls, "source": m.source}
                for m in mentions
            ],
            "features": feat.values,
            "meta": feat.meta,
        }


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent
    pipe = Su9DifficultyPipeline(here / "ontology" / "su9.ttl")
    questions = [
        "Chủ tịch Hồ Chí Minh đọc Tuyên ngôn Độc lập vào ngày nào?",
        "So sánh Hiệp định Genève 1954 và Hiệp định Paris 1973.",
    ]
    df = pipe.featurize(questions, include_meta=True)
    print(df[["question_id", "num_unique_entities", "prereq_depth_max",
              "sem_dist_max", "bloom_combined_max", "inferred_bloom"]])
