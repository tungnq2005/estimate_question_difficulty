"""
Ontology Bridge
================
Tải file .ttl (Turtle) vào rdflib Graph + xây dựng NetworkX graph
để tính toán semantic distance, prerequisite depth, centrality, v.v.

Hỗ trợ đầy đủ các property mới từ V4:
  - abstractness, bloomLevel, frequencyInTextbook
  - startYear, endYear (Period)
  - weightsJson (Event/Document/Movement)
  - Các Object Properties: hasPerson, hasOrganization, involvedConcept,
    prerequisiteOf, directCause, deepCause, similarTo, contrastsWith, locatedIn

V4.1 - Knowledge-Augmented Difficulty (KAD):
  - EntityEmbeddingCache: Pre-compute PhoBERT embeddings cho ALL entities
  - All-pairs shortest paths: Pre-compute graph distances cho O(1) lookup
  - knowledge_entropy(): Shannon Entropy of text in KG entity space
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal

SU9 = Namespace("http://su9.edu.vn/ontology#")

# Các lớp thực thể
ENTITY_CLASSES = {
    SU9.Event, SU9.Person, SU9.Location, SU9.Period,
    SU9.Organization, SU9.Movement, SU9.Document, SU9.Concept,
}

# Các cạnh đồ thị ngữ nghĩa
SEMANTIC_EDGE_PROPS = {
    SU9.prerequisiteOf, SU9.directCause, SU9.deepCause,
    SU9.similarTo, SU9.contrastsWith,
    SU9.occursAt, SU9.occursDuring,
    SU9.involvedConcept, SU9.hasPerson, SU9.hasOrganization,
    SU9.locatedIn, SU9.leads,
}

# Temperature cho soft assignment trong knowledge entropy
ENTROPY_TAU = 0.1


@dataclass
class Entity:
    """Thực thể trong Ontology."""
    uri: str
    label: str
    cls: str                      # Class name: Event, Person, ...
    aliases: List[str] = field(default_factory=list)
    abstractness: Optional[int] = None
    bloom_level: Optional[int] = None
    frequency_in_textbook: Optional[int] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    weights: Dict[str, int] = field(default_factory=dict)  # từ weightsJson

    @property
    def short_name(self) -> str:
        return self.uri.split("#")[-1]

    def __repr__(self) -> str:
        return f"Entity({self.short_name}, {self.cls})"


class OntologyEngine:
    """
    Load ontology từ file .ttl và cung cấp API để:
      - Tra cứu thực thể theo tên/alias
      - Tính semantic distance (shortest path)
      - Lấy prerequisite depth, centrality
      - Lấy weights từ weightsJson
    """

    def __init__(self, ttl_path: str | Path, embed_cache_path: Optional[str | Path] = None):
        """
        Args:
            ttl_path: Đường dẫn file .ttl ontology
            embed_cache_path: Đường dẫn lưu embedding cache (.pkl).
                              Nếu None, mặc định là ttl_path + '.embeddings.pkl'
        """
        self.graph = Graph()
        # Windows path fix: rdflib không handle D:\ prefix, convert sang file URI
        ttl_path_p = Path(ttl_path).resolve()
        ttl_uri = ttl_path_p.as_uri()
        self.graph.parse(ttl_uri, format="turtle")

        # Embedding cache path
        if embed_cache_path is None:
            self._embed_cache_path = ttl_path_p.with_suffix(".embeddings.pkl")
        else:
            self._embed_cache_path = Path(embed_cache_path)

        self.entities: Dict[str, Entity] = {}
        self.label_index: Dict[str, str] = {}  # normalized label -> URI
        self._nx: Optional[nx.DiGraph] = None
        self._prereq_depth_cache: Dict[str, int] = {}
        self._centrality_cache: Dict[str, float] = {}

        # KAD caches (lazy init)
        self._entity_label_list: List[str] = []
        self._embedding_cache: Optional["EntityEmbeddingCache"] = None
        self._all_pairs_dist: Optional[Dict[str, Dict[str, int]]] = None
        self._graph_diameter: int = 1

        self._load_entities()
        self._build_nx_graph()
        self._precompute_metrics()
        self._init_kad()


    # ------------------------------------------------------------------
    # LOADING
    # ------------------------------------------------------------------
    def _load_entities(self) -> None:
        for cls in ENTITY_CLASSES:
            for s in self.graph.subjects(RDF.type, cls):
                uri = str(s)
                ent = Entity(
                    uri=uri,
                    label=self._get_label(s),
                    cls=str(cls).split("#")[-1],
                )
                ent.aliases = self._get_aliases(s)
                ent.abstractness = self._get_int(s, SU9.abstractness)
                ent.bloom_level = self._get_int(s, SU9.bloomLevel)
                ent.frequency_in_textbook = self._get_int(s, SU9.frequencyInTextbook)
                ent.start_year = self._get_int(s, SU9.startYear)
                ent.end_year = self._get_int(s, SU9.endYear)
                ent.weights = self._get_weights(s)

                self.entities[uri] = ent

        # Build label index (normalized)
        for uri, ent in self.entities.items():
            for name in [ent.label] + ent.aliases:
                key = _normalize(name)
                if key and len(key) >= 2:
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

    def _get_weights(self, s) -> Dict[str, int]:
        """Parse weightsJson từ ontology."""
        for o in self.graph.objects(s, SU9.weightsJson):
            try:
                return json.loads(str(o))
            except (json.JSONDecodeError, TypeError):
                continue
        return {}

    # ------------------------------------------------------------------
    # GRAPH CONSTRUCTION
    # ------------------------------------------------------------------
    def _build_nx_graph(self) -> None:
        g = nx.DiGraph()
        for uri, ent in self.entities.items():
            g.add_node(uri, label=ent.label, cls=ent.cls)

        # Thêm cạnh từ Object Properties
        for s, p, o in self.graph:
            if p in SEMANTIC_EDGE_PROPS and isinstance(o, URIRef):
                s_str, o_str = str(s), str(o)
                if s_str in self.entities and o_str in self.entities:
                    g.add_edge(s_str, o_str, prop=str(p).split("#")[-1])
                    # Undirected-style cho similar/contrast
                    if p in {SU9.similarTo, SU9.contrastsWith}:
                        g.add_edge(o_str, s_str, prop=str(p).split("#")[-1])

        self._nx = g

    def _precompute_metrics(self) -> None:
        assert self._nx is not None

        # Prerequisite depth: longest path dọc theo prerequisiteOf
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
            self._prereq_depth_cache = {n: 0 for n in prereq_g.nodes()}

        # Degree centrality
        try:
            self._centrality_cache = nx.degree_centrality(self._nx)
        except Exception:
            self._centrality_cache = {n: 0.0 for n in self._nx.nodes()}

    def _init_kad(self) -> None:
        """Khởi tạo KAD: entity label list + all-pairs shortest paths."""
        self._entity_label_list = [ent.label for ent in self.entities.values()]
        self._entity_uri_list = list(self.entities.keys())

        # Pre-compute all-pairs shortest paths
        assert self._nx is not None
        undirected = self._nx.to_undirected()
        try:
            self._all_pairs_dist = dict(nx.all_pairs_shortest_path_length(undirected))
        except Exception:
            self._all_pairs_dist = {}
        
        # Tính diameter (max shortest path)
        max_dist = 0
        for src, targets in self._all_pairs_dist.items():
            for tgt, d in targets.items():
                max_dist = max(max_dist, d)
        self._graph_diameter = max(1, max_dist)

    # ------------------------------------------------------------------
    # KAD PUBLIC API
    # ------------------------------------------------------------------
    @property
    def entity_label_list(self) -> List[str]:
        return self._entity_label_list

    @property
    def entity_uri_list(self) -> List[str]:
        return self._entity_uri_list

    def embedding_cache(self) -> Optional["EntityEmbeddingCache"]:
        """Lazy init embedding cache (chỉ load khi cần).
        
        Strategy:
          1. Thử load từ disk (.pkl) → nếu có, dùng lại, không cần compute
          2. Nếu không có, compute PhoBERT cho 434 entities (~5-10s)
          3. Auto-save ra disk để lần sau load nhanh hơn
        
        Returns:
            EntityEmbeddingCache hoặc None nếu không có torch/PyTorch.
            Features.py sẽ tự động fallback về 0.0 khi cache=None.
        """
        if self._embedding_cache is None:
            try:
                from embedding_cache import EntityEmbeddingCache
                self._embedding_cache = EntityEmbeddingCache()
                
                # Thử load từ disk trước
                if self._embed_cache_path.exists():
                    self._embedding_cache.load(self._embed_cache_path)
                else:
                    # Không có cache → compute từ đầu
                    self._embedding_cache.precompute_all(self._entity_label_list)
                    # Auto-save để lần sau dùng lại
                    self._embedding_cache.save(self._embed_cache_path)
                    
            except ImportError as e:
                if "torch" in str(e).lower() or "transformers" in str(e).lower():
                    print(f"  ⚠️ Không có PyTorch/Transformers. "
                          f"KAD & Embedding features = 0.0 (mặc định).")
                else:
                    print(f"  ⚠️ Lỗi khi load embedding cache: {e}")
                return None
        return self._embedding_cache




    def knowledge_entropy(self, text: str) -> float:
        """
        Shannon Entropy của text trong không gian KG entities.
        
        Công thức:
          H(text) = -Σ P(e_i | text) × log(P(e_i | text))
        
        Với P(e_i | text) = softmax(cosine(v_text, v_entity_i) / τ)
          - τ = ENTROPY_TAU (temperature, mặc định 0.1)
        
        Returns:
          entropy (float): 0.0 → text chạm 1 entity (DỄ)
                           ~log(434) ≈ 6.07 → text chạm đều các entities (KHÓ)
                           0.0 nếu không có torch (fallback)
        """
        if not text.strip():
            return 0.0
        
        cache = self.embedding_cache()
        if cache is None:
            return 0.0  # fallback: không có torch
        
        if not cache.entity_embeddings:
            return 0.0  # fallback: chưa precompute
        
        v_text = cache.embed_text(text)
        entity_embs = np.array(list(cache.entity_embeddings.values()))
        
        # Vectorized cosine similarity: [768] × [N × 768] → [N]
        v_text_norm = v_text / (np.linalg.norm(v_text) + 1e-10)
        entity_norms = np.linalg.norm(entity_embs, axis=1, keepdims=True) + 1e-10
        cosines = (entity_embs @ v_text_norm) / entity_norms.flatten()
        
        # Soft assignment with temperature
        cosines = cosines.flatten()
        probs = np.exp(cosines / ENTROPY_TAU)
        probs = probs / (np.sum(probs) + 1e-10)
        
        # Shannon Entropy
        probs = np.clip(probs, 1e-10, 1.0)
        entropy = -np.sum(probs * np.log(probs))
        
        # Normalize bởi max entropy (log(N)) để về [0, 1]
        max_entropy = np.log(len(probs))
        return float(entropy / max_entropy)


    def path_distance(self, uri_a: str, uri_b: str) -> float:
        """
        Shortest path distance giữa 2 entities, normalised.
        
        Returns:
          float: 0.0 → rất gần (khó phân biệt)
                 1.0 → rất xa (dễ phân biệt)
        """
        if self._all_pairs_dist is None:
            return 0.5
        src = self._all_pairs_dist.get(uri_a, {})
        d = src.get(uri_b, self._graph_diameter)
        return float(d / self._graph_diameter)

    # ------------------------------------------------------------------
    # PUBLIC API (existing)
    # ------------------------------------------------------------------
    def get(self, uri: str) -> Optional[Entity]:
        return self.entities.get(uri)

    def lookup_by_name(self, name: str) -> Optional[Entity]:
        """Tra cứu entity theo tên (không dấu)."""
        key = _normalize(name)
        uri = self.label_index.get(key)
        return self.entities.get(uri) if uri else None

    def lookup_multiple(self, names: List[str]) -> List[Entity]:
        """Tra cứu nhiều entity cùng lúc."""
        result = []
        for name in names:
            ent = self.lookup_by_name(name)
            if ent:
                result.append(ent)
        return result

    def extract_entities_from_text(self, text: str) -> List[Entity]:
        """
        Trích xuất entity từ văn bản (stem/option) bằng longest-match.
        Trả về danh sách entity không trùng lặp.
        """
        normalized = _normalize_preserve_offsets(text)
        found: List[Tuple[int, int, Entity]] = []
        taken = [False] * len(normalized)

        # Sắp xếp label index giảm dần theo độ dài (longest match)
        sorted_labels = sorted(self.label_index.items(), key=lambda t: -len(t[0]))

        for name_key, uri in sorted_labels:
            ent = self.entities.get(uri)
            if not ent:
                continue
            start = 0
            while True:
                idx = normalized.find(name_key, start)
                if idx == -1:
                    break
                end = idx + len(name_key)
                # Check word boundary
                left_ok = (idx == 0) or (not normalized[idx - 1].isalnum())
                right_ok = (end >= len(normalized)) or (not normalized[end].isalnum())
                if left_ok and right_ok and not any(taken[idx:end]):
                    found.append((idx, end, ent))
                    for i in range(idx, end):
                        taken[i] = True
                start = idx + 1

        # Deduplicate và trả về
        seen = set()
        result = []
        for _, _, ent in sorted(found, key=lambda x: x[0]):
            if ent.uri not in seen:
                seen.add(ent.uri)
                result.append(ent)
        return result

    def semantic_distance(self, u1: str, u2: str) -> Optional[int]:
        """Shortest undirected path length giữa 2 entity."""
        if self._nx is None or u1 not in self._nx or u2 not in self._nx:
            return None
        und = self._nx.to_undirected(as_view=True)
        try:
            return nx.shortest_path_length(und, u1, u2)
        except nx.NetworkXNoPath:
            return None

    def prerequisite_depth(self, uri: str) -> int:
        return self._prereq_depth_cache.get(uri, 0)

    def centrality(self, uri: str) -> float:
        return self._centrality_cache.get(uri, 0.0)

    def get_weight(self, entity_uri: str, related_uri: str) -> int:
        """Lấy trọng số giữa 2 entity (từ weightsJson)."""
        ent = self.entities.get(entity_uri)
        if ent:
            return ent.weights.get(related_uri, 0)
        return 0

    @property
    def nx_graph(self) -> nx.DiGraph:
        assert self._nx is not None
        return self._nx

    def __len__(self) -> int:
        return len(self.entities)


# ------------------------------------------------------------------
# HELPERS (Vietnamese normalization)
# ------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Normalize Vietnamese text: lowercase, strip diacritics, collapse spaces."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "d")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _normalize_preserve_offsets(text: str) -> str:
    """Normalize nhưng giữ nguyên độ dài để index mapping."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
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
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    here = Path(__file__).resolve().parent.parent
    engine = OntologyEngine(here / "output" / "su9.ttl")
    print(f"Loaded {len(engine)} entities")
    print(f"Graph diameter: {engine._graph_diameter}")

    # Test lookup
    for name in ["Hồ Chí Minh", "Điện Biên Phủ", "Chiến tranh thế giới thứ hai"]:
        ent = engine.lookup_by_name(name)
        if ent:
            print(f"  [{ent.cls}] {name} -> {ent.short_name} "
                  f"(abs={ent.abstractness}, bloom={ent.bloom_level}, freq={ent.frequency_in_textbook})")

    # Test text extraction
    text = "Chủ tịch Hồ Chí Minh đọc Tuyên ngôn Độc lập vào ngày 2/9/1945"
    ents = engine.extract_entities_from_text(text)
    print(f"\nEntities in '{text}':")
    for e in ents:
        print(f"  - {e.label} ({e.cls})")

    # Test knowledge entropy (sẽ chạy embedding lần đầu ~5s)
    print("\n[KAD] Testing knowledge_entropy...")
    stem_easy = "Hiệp định Paris được ký năm 1973"
    stem_hard = "So sánh phong trào Đồng Khởi và Cần Vương"
    ent_easy = engine.knowledge_entropy(stem_easy)
    ent_hard = engine.knowledge_entropy(stem_hard)
    print(f"  Entropy('{stem_easy}') = {ent_easy:.4f}")
    print(f"  Entropy('{stem_hard}') = {ent_hard:.4f}")
    if ent_easy < ent_hard:
        print("  ✅ Entropy(easy) < Entropy(hard) — đúng kỳ vọng!")
    else:
        print("  ⚠️ Entropy chưa phân biệt rõ — cần tinh chỉnh temperature")
