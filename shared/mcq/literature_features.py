# -*- coding: utf-8 -*-
"""Attribution features cho cụm môn attributive_tree (Văn).

Đồ thị Văn không có cạnh prerequisiteOf nào (2 feature prereq-depth luôn 0
một cách cấu trúc). Thay vào đó, độ nhầm lẫn giữa các phương án đến từ các
quan hệ THUỘC-TÍNH thật của môn này: cùng tác giả, cùng giai đoạn văn học,
chung chủ đề / biện pháp nghệ thuật — distractor "cùng cụm thuộc tính" với
đáp án đúng là distractor khó loại.
"""

from __future__ import annotations

from typing import Dict, List, Set

from .ontology_bridge import Entity, OntologyEngine


def _related_targets(engine: OntologyEngine, uri: str, props: Set[str],
                     self_classes: Set[str], cls: str) -> Set[str]:
    """Tập node đích của các cạnh `props` đi ra từ uri (+ chính nó nếu thuộc
    self_classes — VD hỏi thẳng về Author thì author-set là chính nó)."""
    out = set()
    if cls in self_classes:
        out.add(uri)
    for _, target, d in engine.nx_graph.out_edges(uri, data=True):
        if d.get("prop") in props:
            out.add(target)
    return out


def _entity_set(engine: OntologyEngine, entities: List[Entity],
                props: Set[str], self_classes: Set[str]) -> Set[str]:
    out: Set[str] = set()
    for e in entities:
        out |= _related_targets(engine, e.uri, props, self_classes, e.cls)
    return out


def compute_literature_features(
    correct_entities: List[Entity],
    distractors_entities: List[List[Entity]],
    engine: OntologyEngine,
) -> Dict[str, float]:
    feats = {
        "kg_same_author_correct_distractor": 0.0,
        "kg_same_period_correct_distractor": 0.0,
        "kg_shared_theme_device_jaccard": 0.0,
    }
    if not correct_entities or not distractors_entities:
        return feats

    author_c = _entity_set(engine, correct_entities,
                           {"authoredBy"}, {"Author"})
    period_c = _entity_set(engine, correct_entities,
                           {"writtenIn", "activeIn"}, {"HistoricalPeriod"})
    theme_c = _entity_set(engine, correct_entities,
                          {"expresses", "uses"},
                          {"Theme", "LiteraryDevice"})

    n = len(distractors_entities)
    same_author = same_period = 0
    best_jaccard = 0.0
    for d_ents in distractors_entities:
        if not d_ents:
            continue
        if author_c & _entity_set(engine, d_ents, {"authoredBy"}, {"Author"}):
            same_author += 1
        if period_c & _entity_set(engine, d_ents,
                                  {"writtenIn", "activeIn"},
                                  {"HistoricalPeriod"}):
            same_period += 1
        theme_d = _entity_set(engine, d_ents, {"expresses", "uses"},
                              {"Theme", "LiteraryDevice"})
        union = theme_c | theme_d
        if union:
            best_jaccard = max(best_jaccard,
                               len(theme_c & theme_d) / len(union))

    feats["kg_same_author_correct_distractor"] = same_author / n
    feats["kg_same_period_correct_distractor"] = same_period / n
    feats["kg_shared_theme_device_jaccard"] = best_jaccard
    return feats
