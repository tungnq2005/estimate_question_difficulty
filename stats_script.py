# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'd:/CS/CS_Major/NCKH/package/su9_ontology/mcq_pipeline')
sys.stdout.reconfigure(encoding='utf-8')

from ontology_bridge import OntologyEngine
from pathlib import Path
from collections import Counter

engine = OntologyEngine(Path('d:/CS/CS_Major/NCKH/package/su9_ontology/output/su9.ttl'))

# Class distribution
cls_count = Counter()
for ent in engine.entities.values():
    cls_count[ent.cls] += 1

g = engine.nx_graph
edge_props = Counter()
for u, v, d in g.edges(data=True):
    edge_props[d.get('prop', 'unknown')] += 1

print("#" * 60)
print("# THONG KE ONTOLOGY LICH SU 9")
print("#" * 60)
print(f"Total entities: {len(engine.entities)}")
print(f"Total nodes: {g.number_of_nodes()}")
print(f"Total edges: {g.number_of_edges()}")
print(f"Graph diameter: {engine._graph_diameter}")
print()
print("=== Class phan bo ===")
for cls, cnt in sorted(cls_count.items(), key=lambda x: -x[1]):
    print(f"  {cnt:>3} x {cls}")
print()
print("=== Edge phan bo ===")
for p, c in sorted(edge_props.items(), key=lambda x: -x[1]):
    print(f"  {c:>3} x {p}")
print()
abs_c = bloom_c = freq_c = alias_c = weight_c = yr_c = 0
for ent in engine.entities.values():
    if ent.abstractness is not None: abs_c += 1
    if ent.bloom_level is not None: bloom_c += 1
    if ent.frequency_in_textbook is not None: freq_c += 1
    if ent.aliases: alias_c += len(ent.aliases)
    if ent.weights: weight_c += 1
    if ent.start_year is not None or ent.end_year is not None: yr_c += 1
print("=== Annotation ===")
print(f"  abstractness: {abs_c}")
print(f"  bloomLevel: {bloom_c}")
print(f"  frequencyInTextbook: {freq_c}")
print(f"  aliases entries: {alias_c}")
print(f"  weightsJson: {weight_c}")
print(f"  year info: {yr_c}")
print()
print(f"Entity labels: {len(engine.entity_label_list)}")
print(f"Entity URIs: {len(engine.entity_uri_list)}")
print(f"All-pairs distances computed: {len(engine._all_pairs_dist)} nodes")
if engine._all_pairs_dist:
    total_paths = sum(len(tgts) for tgts in engine._all_pairs_dist.values())
    print(f"Total shortest paths cached: {total_paths}")
