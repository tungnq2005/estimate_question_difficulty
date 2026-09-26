# -*- coding: utf-8 -*-
"""Gộp ontology LLM (supplement) vào phys9.ttl: khử trùng + lọc + emit (chống chu trình).

Bước chạy SAU tools/ontology_llm_builder.py. Làm:
  1. Khử trùng lặp thực thể LLM (theo label chuẩn hoá), gộp aliases.
  2. Lọc bỏ thực thể ĐÃ CÓ trong ontology hiện tại.
  3. Emit TTL cho thực thể mới + cạnh tiên quyết. CHỈ thêm cạnh không tạo
     chu trình (chu trình làm DAG sụp -> prereq depth toàn 0).
  4. Nối vào phys9.ttl (idempotent: xoá block cũ trước), xoá cache embedding.

Usage:
    python tools/merge_llm_ontology.py
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import networkx as nx

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

TTL = REPO / "subjects" / "physics" / "ontology" / "phys9.ttl"
SUPP = REPO / "subjects" / "physics" / "samples" / "llm_ontology_supplement.json"
BLOCK_MARK = "# ==== LLM supplement (ontology_llm_builder) ===="

CLASS_MAP = {
    "Quantity": "phys:Quantity", "Law": "phys:Law", "Formula": "phys:Formula",
    "Concept": "phys:Concept", "Device": "phys:Device", "Phenomenon": "phys:Phenomenon",
    "Unit": "phys:Unit", "Method": "phys:Method", "ProblemType": "phys:ProblemType",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "d").lower()  # đ là chữ riêng, không phải dấu
    return re.sub(r"[^a-z0-9]", "", s)


def quote(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    # 0) Idempotent: xoá block LLM cũ TRƯỚC (để engine load ontology gốc sạch)
    ttl_text = TTL.read_text(encoding="utf-8")
    if BLOCK_MARK in ttl_text:
        ttl_text = ttl_text[: ttl_text.index(BLOCK_MARK)].rstrip()
        TTL.write_text(ttl_text + "\n", encoding="utf-8")

    supp = json.loads(SUPP.read_text(encoding="utf-8"))
    llm_ents = supp["entities"]
    llm_pres = supp["prerequisites"]

    from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402
    eng = OntologyEngine.for_subject("physics")
    existing = {norm(e.label) for e in eng.entities.values()}
    for e in eng.entities.values():
        for a in e.aliases:
            existing.add(norm(a))

    # 1 pass: khử trùng LLM + lọc trùng ontology, map orig_idx -> final_id
    kept, final_id, seen_llm = [], {}, {}
    for e in llm_ents:
        k = norm(e["label"])
        if k in existing:
            final_id[e["i"]] = None
            continue
        if k in seen_llm:
            prev = kept[seen_llm[k]]
            prev["aliases"] = sorted(set(prev["aliases"]) | set(e.get("aliases", [])))
            final_id[e["i"]] = kept[seen_llm[k]]["id"]
            continue
        eid = f"LLM_{len(kept):03d}"
        kept.append({"id": eid, "label": e["label"], "class": e.get("class", "Concept"),
                     "aliases": list(e.get("aliases", [])),
                     "symbol": e.get("symbol", "")})
        seen_llm[k] = len(kept) - 1
        final_id[e["i"]] = eid
    print(f"1+2) LLM {len(llm_ents)} -> giữ {len(kept)} thực thể MỚI")

    # 3) Emit thực thể
    lines = []
    for e in kept:
        cls = CLASS_MAP.get(e["class"], "phys:Concept")
        aliases = "|".join(a for a in e["aliases"] if a and norm(a) != norm(e["label"]))
        out = [f"phys:{e['id']} a {cls} ;",
               f'    rdfs:label "{quote(e["label"])}"@vi ;']
        if aliases:
            out.append(f'    phys:aliases "{quote(aliases)}" ;')
        if e.get("symbol"):
            out.append(f'    phys:symbol "{quote(e["symbol"])}" ;')
        out[-1] = out[-1].rstrip(" ;") + " ."
        lines.append("\n".join(out))

    # 3b) Cạnh tiên quyết với chống chu trình
    llm_dag = nx.DiGraph()
    llm_dag.add_nodes_from(e["id"] for e in kept)
    pres_lines, skipped_cycle = [], 0
    for p in llm_pres:
        a = final_id.get(p.get("a"))
        b = final_id.get(p.get("b"))
        if not (a and b and a != b):
            continue
        if nx.has_path(llm_dag, b, a):  # thêm a->b sẽ tạo chu trình
            skipped_cycle += 1
            continue
        llm_dag.add_edge(a, b)
        pres_lines.append(f"phys:{a} phys:prerequisiteOf phys:{b} .")
    print(f"3) Emit: {len(lines)} thực thể, {len(pres_lines)} cạnh tiên quyết "
          f"(bỏ {skipped_cycle} cạnh tạo chu trình)")

    # 4) Nối vào TTL + xoá cache embedding cũ
    ttl_text = TTL.read_text(encoding="utf-8").rstrip()
    block = f"\n\n{BLOCK_MARK}\n" + "\n".join(lines) + "\n"
    if pres_lines:
        block += "\n".join(pres_lines) + "\n"
    TTL.write_text(ttl_text + "\n" + block + "\n", encoding="utf-8")
    emb = TTL.with_suffix(".embeddings.pkl")
    if emb.exists():
        emb.unlink()
    print(f"4) Đã nối vào {TTL.name} + xoá cache embedding cũ")


if __name__ == "__main__":
    main()
