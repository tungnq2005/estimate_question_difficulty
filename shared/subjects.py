"""
Per-subject configuration for the difficulty engine.

This is the seam that makes ``shared.mcq`` reusable across every subject instead
of being hard-wired to History. Each :class:`SubjectConfig` says where a subject's
ontology lives and how to read it (namespace + which classes are content entities
+ which object properties are semantic graph edges).

History is configured explicitly so its behavior is identical to the pre-refactor
pipeline. The six tuple-based subjects leave ``entity_classes``/``edge_props``
empty, which tells the engine to auto-discover them from the ontology.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]      # shared/ -> repo root
SUBJECTS_DIR = REPO_ROOT / "subjects"

# Classes / object-properties that are curriculum scaffolding, not content.
# Excluded from auto-discovery so they don't distort the semantic graph.
NON_ENTITY_CLASSES = {"LessonUnit", "Textbook"}
NON_SEMANTIC_EDGES = {"partOfTextbook", "appearsInLesson", "belongsToLesson",
                      "curriculumPosition"}


@dataclass(frozen=True)
class SubjectConfig:
    name: str                      # folder name under subjects/, e.g. "history"
    namespace: str                 # ontology IRI namespace, ends with '#'
    prefix: str                    # ttl filename prefix, e.g. "su9", "phys9"
    entity_classes: Tuple[str, ...] = ()   # local names; () => auto-discover
    edge_props: Tuple[str, ...] = ()       # local names; () => auto-discover

    @property
    def dir(self) -> Path:
        return SUBJECTS_DIR / self.name

    @property
    def ttl_path(self) -> Path:
        return self.dir / "ontology" / f"{self.prefix}.ttl"

    @property
    def owl_path(self) -> Path:
        return self.dir / "ontology" / f"{self.prefix}.owl"


# History (su9) — the flagship. Explicit class/edge sets reproduce the exact
# legacy behavior of the pre-refactor OntologyEngine (byte-identical features).
HISTORY = SubjectConfig(
    name="history",
    namespace="http://su9.edu.vn/ontology#",
    prefix="su9",
    entity_classes=("Event", "Person", "Location", "Period",
                    "Organization", "Movement", "Document", "Concept"),
    edge_props=("prerequisiteOf", "directCause", "deepCause",
                "similarTo", "contrastsWith", "occursAt", "occursDuring",
                "involvedConcept", "hasPerson", "hasOrganization",
                "locatedIn", "leads"),
)


def _simple(name: str, prefix: str) -> SubjectConfig:
    """A tuple-based subject: shared IRI scheme, classes/edges auto-discovered."""
    return SubjectConfig(name=name,
                         namespace=f"http://edu.vn/{prefix}/ontology#",
                         prefix=prefix)


REGISTRY = {
    "history": HISTORY,
    "physics": _simple("physics", "phys9"),
    "math": _simple("math", "math9"),
    "chemistry": _simple("chemistry", "chem9"),
    "english": _simple("english", "eng9"),
    "geography": _simple("geography", "geo9"),
    "literature": _simple("literature", "lit9"),
}


def get_config(subject: str) -> SubjectConfig:
    try:
        return REGISTRY[subject]
    except KeyError:
        known = ", ".join(REGISTRY)
        raise KeyError(f"Unknown subject '{subject}'. Known subjects: {known}")
