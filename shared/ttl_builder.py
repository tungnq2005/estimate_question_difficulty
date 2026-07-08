"""
Generic Turtle emitter for subject ontologies.
Each subject provides a `build_data.py` with:
  - HEADER, SCHEMA (Turtle strings)
  - Data lists with known shapes (see function signatures)
  - Relationship lists

This module emits Turtle + RDF/XML, validates via rdflib, and prints stats.
"""

from pathlib import Path
from typing import List, Tuple


def quote(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build_ttl(
    prefix: str,            # e.g. "math"
    out_dir: Path,
    header: str,
    schema: str,
    groups: list,           # list of (section_name, emit_fn, data_rows)
):
    """
    groups: list of tuples (section_header, emit_function, list_of_rows)
    emit_function(row) -> string of Turtle for that row
    """
    parts = [header, schema]
    for section_header, emit_fn, rows in groups:
        parts.append(f"\n#################################################################")
        parts.append(f"#   {section_header}")
        parts.append(f"#################################################################\n")
        for row in rows:
            parts.append(emit_fn(row) + "\n")

    ttl_path = out_dir / f"{prefix}9.ttl"
    ttl_path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"[OK] Wrote {ttl_path}")

    from rdflib import Graph
    g = Graph()
    g.parse(str(ttl_path), format="turtle")
    owl_path = out_dir / f"{prefix}9.owl"
    g.serialize(destination=str(owl_path), format="xml")
    print(f"[OK] Wrote {owl_path}  ({len(g)} triples)")

    from rdflib import RDF
    from collections import Counter
    counts = Counter()
    for _, _, o in g.triples((None, RDF.type, None)):
        if prefix in str(o) or "owl" not in str(o):
            counts[str(o).split("#")[-1]] += 1
    print("Entity counts:")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        if v > 1 and k not in ("Class", "ObjectProperty", "DatatypeProperty",
                               "TransitiveProperty", "SymmetricProperty",
                               "Ontology", "Thing"):
            print(f"  {k:20s} {v}")
    return g


def triple(subj_uri, pred, obj_uri):
    return f"{subj_uri} {pred} {obj_uri} ."
