"""
Shared engine for the NCKH grade-9 question-difficulty project.

Two independent capabilities live here, both subject-agnostic:

- ``shared.ttl_builder`` — turns a subject's declarative data (``build_data.py``)
  into a W3C Turtle + OWL ontology. Used by every ``subjects/<name>/build.py``.
- ``shared.form_template`` — generates two independent teacher-facing forms:
  an ontology-claim verification form (Đúng/Sai/Không chắc) and an MCQ
  difficulty-rating form (Dễ/Trung bình/Khó), each with an HTML + Google
  Apps Script variant.
- ``shared.mcq``          — the MCQ difficulty pipeline: loads a subject ontology
  into a NetworkX graph and produces the 41-feature vector (KG + Jaccard + RSI +
  KAD entropy + PhoBERT embeddings) used to estimate question difficulty.

The engine is configured per subject through :mod:`shared.subjects`.
"""

__version__ = "0.4.1"
