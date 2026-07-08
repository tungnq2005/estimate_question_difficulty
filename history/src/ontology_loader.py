"""
Ontology loader for Su9 (Lich su 9) domain ontology.
Loads Turtle/OWL file into rdflib Graph + builds a NetworkX graph for
shortest-path / centrality computations used by the feature extractor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal

SU9 = Namespace("http://su9.edu.vn/ontology#")

# Classes we treat as "entities" (LessonUnit excluded from entity lookup by default)
ENTITY_CLASSES = {
    SU9.Event, SU9.Person, SU9.Location, SU9.Period,
    SU9.Organization, SU9.Movement, SU9.Document, SU9.Concept,
}

# Properties that form the semantic graph used for distance / centrality
SEMANTIC_EDGE_PROPS = {
    SU9.prerequisiteOf, SU9.causes, SU9.directCause, SU9.deepCause,
    SU9.resultsFrom, SU9.similarTo, SU9.contrastsWith, SU9.derivesFrom,
    SU9.occursAt, SU9.occursDuring, SU9.participatesIn, SU9.leads,
    SU9.involvedConcept, SU9.signed, SU9.memberOf, SU9.locatedIn,
    SU9.belongsToLesson,
}


@dataclass
class Entity:
    """Lightweight view over an ontology individual."""
    uri: str
    label: str
    cls: str
    aliases: List[str] = field(default_factory=list)
    bloom_level: Optional[int] = None
    abstractness: Optional[int] = None
    frequency_in_textbook: Optional[int] = None
    curriculum_position: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None

    @property
    def short_name(self) -> str:
        return self.uri.split("#")[-1]


class OntologyStore:
    """
    Loads the Su9 ontology and exposes:
      - entity lookup by URI / label / alias
      - a NetworkX DiGraph of semantic relationships
      - derived metrics (prerequisite depth, centrality) cached per entity
    """

    def __init__(self, ttl_path: str | Path):
        self.graph = Graph()
        self.graph.parse(str(ttl_path), format="turtle")

        self.entities: Dict[str, Entity] = {}
        self.label_index: Dict[str, str] = {}  # normalized label -> URI
        self._nx: Optional[nx.DiGraph] = None
        self._prereq_depth_cache: Dict[str, int] = {}
        self._centrality_cache: Dict[str, float] = {}

        self._load_entities()
        self._build_nx_graph()
        self._precompute_metrics()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def _load_entities(self) -> None:
        # First, collect curriculum_position on all LessonUnits (used for propagation)
        lesson_pos: Dict[str, int] = {}
        for s in self.graph.subjects(RDF.type, SU9.LessonUnit):
            for o in self.graph.objects(s, SU9.curriculumPosition):
                try:
                    lesson_pos[str(s)] = int(o)
                except (TypeError, ValueError):
                    pass

        for cls in ENTITY_CLASSES:
            for s in self.graph.subjects(RDF.type, cls):
                uri = str(s)
                ent = Entity(
                    uri=uri,
                    label=self._get_label(s),
                    cls=str(cls).split("#")[-1],
                )
                ent.aliases = self._get_aliases(s)
                ent.bloom_level = self._get_int(s, SU9.bloomLevel)
                ent.abstractness = self._get_int(s, SU9.abstractness)
                ent.frequency_in_textbook = self._get_int(s, SU9.frequencyInTextbook)
                ent.curriculum_position = self._get_int(s, SU9.curriculumPosition)
                ent.start_year = self._get_int(s, SU9.startYear)
                ent.end_year = self._get_int(s, SU9.endYear)

                # Propagate curriculum_position via belongsToLesson when missing
                if ent.curriculum_position is None:
                    for o in self.graph.objects(s, SU9.belongsToLesson):
                        pos = lesson_pos.get(str(o))
                        if pos is not None:
                            ent.curriculum_position = pos
                            break

                self.entities[uri] = ent

        # Build label index (normalized)
        for uri, ent in self.entities.items():
            for name in [ent.label] + ent.aliases:
                key = _normalize(name)
                if key:
                    self.label_index[key] = uri

    def _get_label(self, s) -> str:
        for o in self.graph.objects(s, RDFS.label):
            return str(o)
        return str(s).split("#")[-1]

    def _get_aliases(self, s) -> List[str]:
        out: List[str] = []
        for o in self.graph.objects(s, SU9.aliases):
            for part in str(o).split("|"):
                part = part.strip()
                if part:
                    out.append(part)
        return out

    def _get_int(self, s, prop) -> Optional[int]:
        for o in self.graph.objects(s, prop):
            try:
                return int(o)
            except (TypeError, ValueError):
                continue
        return None

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------
    def _build_nx_graph(self) -> None:
        g = nx.DiGraph()
        for uri, ent in self.entities.items():
            g.add_node(uri, label=ent.label, cls=ent.cls)

        for s, p, o in self.graph:
            if p in SEMANTIC_EDGE_PROPS and isinstance(o, URIRef):
                s_str, o_str = str(s), str(o)
                if s_str in self.entities and o_str in self.entities:
                    g.add_edge(s_str, o_str, prop=str(p).split("#")[-1])
                    # Undirected-style edges for similarity/contrast
                    if p in {SU9.similarTo, SU9.contrastsWith}:
                        g.add_edge(o_str, s_str, prop=str(p).split("#")[-1])
        self._nx = g

    def _precompute_metrics(self) -> None:
        assert self._nx is not None
        # Prerequisite depth: longest path along prerequisiteOf edges ending at node
        prereq_edges = [
            (u, v) for u, v, d in self._nx.edges(data=True)
            if d.get("prop") == "prerequisiteOf"
        ]
        prereq_g = nx.DiGraph()
        prereq_g.add_nodes_from(self._nx.nodes())
        prereq_g.add_edges_from(prereq_edges)

        if nx.is_directed_acyclic_graph(prereq_g):
            topo = list(nx.topological_sort(prereq_g))
            depth = {n: 0 for n in prereq_g.nodes()}
            for n in topo:
                for pred in prereq_g.predecessors(n):
                    depth[n] = max(depth[n], depth[pred] + 1)
            self._prereq_depth_cache = depth
        else:
            # Fallback: 0 for everyone
            self._prereq_depth_cache = {n: 0 for n in prereq_g.nodes()}

        # Degree centrality over the full semantic graph
        try:
            self._centrality_cache = nx.degree_centrality(self._nx)
        except Exception:
            self._centrality_cache = {n: 0.0 for n in self._nx.nodes()}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get(self, uri: str) -> Optional[Entity]:
        return self.entities.get(uri)

    def lookup_by_name(self, name: str) -> Optional[Entity]:
        key = _normalize(name)
        uri = self.label_index.get(key)
        return self.entities.get(uri) if uri else None

    def prerequisite_depth(self, uri: str) -> int:
        return self._prereq_depth_cache.get(uri, 0)

    def centrality(self, uri: str) -> float:
        return self._centrality_cache.get(uri, 0.0)

    def semantic_distance(self, u1: str, u2: str) -> Optional[int]:
        """Shortest undirected path length between two entities in semantic graph."""
        if self._nx is None or u1 not in self._nx or u2 not in self._nx:
            return None
        und = self._nx.to_undirected(as_view=True)
        try:
            return nx.shortest_path_length(und, u1, u2)
        except nx.NetworkXNoPath:
            return None

    @property
    def nx_graph(self) -> nx.DiGraph:
        assert self._nx is not None
        return self._nx

    def __len__(self) -> int:
        return len(self.entities)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
import re
import unicodedata


def _normalize(text: str) -> str:
    """Normalize Vietnamese text for lookup: lowercase, strip diacritics, collapse spaces.
    Used for building the label index (position-agnostic)."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "d")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_preserve_offsets(text: str) -> str:
    """Normalize but keep the same length so indices match the original string.
    Used for in-question matching so we can report correct character spans."""
    if not text:
        return ""
    # NFD decomposition keeps base chars, then strip combining marks.
    # We need equal-length: replace combining marks with nothing WOULD shrink,
    # so instead we fold directly on NFC form using char-level mapping.
    text = unicodedata.normalize("NFC", text)
    # Build mapping for common Vietnamese diacritics and đ/Đ.
    table = str.maketrans({
        "à": "a", "á": "a", "ả": "a", "ã": "a", "ạ": "a",
        "ă": "a", "ằ": "a", "ắ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
        "â": "a", "ầ": "a", "ấ": "a", "ẩ": "a", "ẫ": "a", "ậ": "a",
        "è": "e", "é": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
        "ê": "e", "ề": "e", "ế": "e", "ể": "e", "ễ": "e", "ệ": "e",
        "ì": "i", "í": "i", "ỉ": "i", "ĩ": "i", "ị": "i",
        "ò": "o", "ó": "o", "ỏ": "o", "õ": "o", "ọ": "o",
        "ô": "o", "ồ": "o", "ố": "o", "ổ": "o", "ỗ": "o", "ộ": "o",
        "ơ": "o", "ờ": "o", "ớ": "o", "ở": "o", "ỡ": "o", "ợ": "o",
        "ù": "u", "ú": "u", "ủ": "u", "ũ": "u", "ụ": "u",
        "ư": "u", "ừ": "u", "ứ": "u", "ử": "u", "ữ": "u", "ự": "u",
        "ỳ": "y", "ý": "y", "ỷ": "y", "ỹ": "y", "ỵ": "y",
        "đ": "d",
        "À": "a", "Á": "a", "Ả": "a", "Ã": "a", "Ạ": "a",
        "Ă": "a", "Ằ": "a", "Ắ": "a", "Ẳ": "a", "Ẵ": "a", "Ặ": "a",
        "Â": "a", "Ầ": "a", "Ấ": "a", "Ẩ": "a", "Ẫ": "a", "Ậ": "a",
        "È": "e", "É": "e", "Ẻ": "e", "Ẽ": "e", "Ẹ": "e",
        "Ê": "e", "Ề": "e", "Ế": "e", "Ể": "e", "Ễ": "e", "Ệ": "e",
        "Ì": "i", "Í": "i", "Ỉ": "i", "Ĩ": "i", "Ị": "i",
        "Ò": "o", "Ó": "o", "Ỏ": "o", "Õ": "o", "Ọ": "o",
        "Ô": "o", "Ồ": "o", "Ố": "o", "Ổ": "o", "Ỗ": "o", "Ộ": "o",
        "Ơ": "o", "Ờ": "o", "Ớ": "o", "Ở": "o", "Ỡ": "o", "Ợ": "o",
        "Ù": "u", "Ú": "u", "Ủ": "u", "Ũ": "u", "Ụ": "u",
        "Ư": "u", "Ừ": "u", "Ứ": "u", "Ử": "u", "Ữ": "u", "Ự": "u",
        "Ỳ": "y", "Ý": "y", "Ỷ": "y", "Ỹ": "y", "Ỵ": "y",
        "Đ": "d",
    })
    return text.translate(table).lower()


if __name__ == "__main__":
    here = Path(__file__).resolve().parent.parent
    store = OntologyStore(here / "ontology" / "su9.ttl")
    print(f"Loaded {len(store)} entities")
    sample = store.lookup_by_name("Dien Bien Phu")
    if sample:
        print(f"Sample lookup: {sample.label} "
              f"(depth={store.prerequisite_depth(sample.uri)}, "
              f"centrality={store.centrality(sample.uri):.3f})")
