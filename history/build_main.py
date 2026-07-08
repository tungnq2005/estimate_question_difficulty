"""
Main driver: combines build_ontology.py (schema, periods, locations, persons,
orgs, movements, documents, concepts) + build_ontology_part2.py (events,
lessons) + build_ontology_part3.py (relationships) and emits Turtle.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Load data from the three parts via exec so we keep logical separation
ns: dict = {"__file__": str(ROOT / "build_ontology.py")}
for part in ("build_ontology.py", "build_ontology_part2.py", "build_ontology_part3.py"):
    with open(ROOT / part, "r", encoding="utf-8") as f:
        exec(f.read(), ns)

HEADER, SCHEMA = ns["HEADER"], ns["SCHEMA"]
PERIODS = ns["PERIODS"]
LOCATIONS = ns["LOCATIONS"]
PERSONS = ns["PERSONS"]
ORGANIZATIONS = ns["ORGANIZATIONS"]
MOVEMENTS = ns["MOVEMENTS"]
DOCUMENTS = ns["DOCUMENTS"]
CONCEPTS = ns["CONCEPTS"]
LESSONS_OLD = ns["LESSONS_OLD"]
LESSONS_KNTT = ns["LESSONS_KNTT"]
LESSONS_CTST = ns["LESSONS_CTST"]
LESSONS_CD = ns["LESSONS_CD"]
EVENTS = ns["EVENTS"]
PREREQUISITES = ns["PREREQUISITES"]
CAUSES_DIRECT = ns["CAUSES_DIRECT"]
CAUSES_DEEP = ns["CAUSES_DEEP"]
SIMILARITIES = ns["SIMILARITIES"]
CONTRASTS = ns["CONTRASTS"]
PARTICIPATES = ns["PARTICIPATES"]
INVOLVED_CONCEPTS = ns["INVOLVED_CONCEPTS"]


# ======================================================================
# TURTLE EMITTERS
# ======================================================================

def quote(s: str) -> str:
    """Escape string for Turtle literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def emit_period(pid, label, aliases, start, end, abstractness, conf):
    out = [f"su9:{pid} a su9:Period ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    su9:aliases "{quote(aliases)}" ;')
    out.append(f"    su9:startYear {start} ; su9:endYear {end} ;")
    out.append(f"    su9:abstractness {abstractness} ;")
    out.append(f"    su9:confidence {conf} .")
    return "\n".join(out)


def emit_location(lid, label, aliases, located_in, abstractness, conf):
    out = [f"su9:{lid} a su9:Location ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    su9:aliases "{quote(aliases)}" ;')
    if located_in:
        out.append(f"    su9:locatedIn su9:{located_in} ;")
    out.append(f"    su9:abstractness {abstractness} ;")
    out.append(f"    su9:confidence {conf} .")
    return "\n".join(out)


def emit_person(pid, label, aliases, freq, abstractness, conf):
    out = [f"su9:{pid} a su9:Person ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    su9:aliases "{quote(aliases)}" ;')
    out.append(f"    su9:frequencyInTextbook {freq} ;")
    out.append(f"    su9:abstractness {abstractness} ;")
    out.append(f"    su9:confidence {conf} .")
    return "\n".join(out)


def emit_org(oid, label, aliases, freq, abstractness, conf):
    out = [f"su9:{oid} a su9:Organization ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    su9:aliases "{quote(aliases)}" ;')
    out.append(f"    su9:frequencyInTextbook {freq} ;")
    out.append(f"    su9:abstractness {abstractness} ;")
    out.append(f"    su9:confidence {conf} .")
    return "\n".join(out)


def emit_movement(mid, label, aliases, freq, abstractness, conf):
    out = [f"su9:{mid} a su9:Movement ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    su9:aliases "{quote(aliases)}" ;')
    out.append(f"    su9:frequencyInTextbook {freq} ;")
    out.append(f"    su9:abstractness {abstractness} ;")
    out.append(f"    su9:confidence {conf} .")
    return "\n".join(out)


def emit_doc(did, label, aliases, freq, abstractness, conf):
    out = [f"su9:{did} a su9:Document ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    su9:aliases "{quote(aliases)}" ;')
    out.append(f"    su9:frequencyInTextbook {freq} ;")
    out.append(f"    su9:abstractness {abstractness} ;")
    out.append(f"    su9:confidence {conf} .")
    return "\n".join(out)


def emit_concept(cid, label, aliases, freq, abstractness, bloom, conf):
    out = [f"su9:{cid} a su9:Concept ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    su9:aliases "{quote(aliases)}" ;')
    out.append(f"    su9:frequencyInTextbook {freq} ;")
    out.append(f"    su9:abstractness {abstractness} ;")
    out.append(f"    su9:bloomLevel {bloom} ;")
    out.append(f"    su9:confidence {conf} .")
    return "\n".join(out)


def emit_event(row):
    (eid, label, aliases, loc, period, bloom, abstract, freq,
     bai_old, bai_kntt, bai_ctst, bai_cd, conf) = row
    out = [f"su9:{eid} a su9:Event ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    su9:aliases "{quote(aliases)}" ;')
    if loc:
        out.append(f"    su9:occursAt su9:{loc} ;")
    if period:
        out.append(f"    su9:occursDuring su9:{period} ;")
    out.append(f"    su9:bloomLevel {bloom} ;")
    out.append(f"    su9:abstractness {abstract} ;")
    out.append(f"    su9:frequencyInTextbook {freq} ;")
    # Lesson mappings: use appearsInLesson, suffix tells textbook
    lesson_maps = [(bai_old, "TB_Old"), (bai_kntt, "TB_KNTT"),
                   (bai_ctst, "TB_CTST"), (bai_cd, "TB_CD")]
    for num, tb in lesson_maps:
        if num is not None:
            out.append(f"    su9:appearsInLesson su9:{tb}_B{num:02d} ;")
    out.append(f"    su9:confidence {conf} .")
    return "\n".join(out)


def emit_lesson(tb: str, num: int, label: str):
    return (f"su9:{tb}_B{num:02d} a su9:LessonUnit ;\n"
            f'    rdfs:label "{quote(f"[{tb}] Bai {num}: {label}")}"@vi ;\n'
            f"    su9:partOfTextbook su9:{tb} ;\n"
            f"    su9:curriculumPosition {num} .")


# ======================================================================
# BUILD
# ======================================================================

def main() -> None:
    out = [HEADER, SCHEMA]

    out.append("\n#################################################################")
    out.append("#   PERIODS")
    out.append("#################################################################\n")
    for row in PERIODS:
        out.append(emit_period(*row) + "\n")

    out.append("\n#################################################################")
    out.append("#   LOCATIONS")
    out.append("#################################################################\n")
    for row in LOCATIONS:
        out.append(emit_location(*row) + "\n")

    out.append("\n#################################################################")
    out.append("#   PERSONS")
    out.append("#################################################################\n")
    for row in PERSONS:
        out.append(emit_person(*row) + "\n")

    out.append("\n#################################################################")
    out.append("#   ORGANIZATIONS")
    out.append("#################################################################\n")
    for row in ORGANIZATIONS:
        out.append(emit_org(*row) + "\n")

    out.append("\n#################################################################")
    out.append("#   MOVEMENTS")
    out.append("#################################################################\n")
    for row in MOVEMENTS:
        out.append(emit_movement(*row) + "\n")

    out.append("\n#################################################################")
    out.append("#   DOCUMENTS")
    out.append("#################################################################\n")
    for row in DOCUMENTS:
        out.append(emit_doc(*row) + "\n")

    out.append("\n#################################################################")
    out.append("#   CONCEPTS")
    out.append("#################################################################\n")
    for row in CONCEPTS:
        out.append(emit_concept(*row) + "\n")

    # Lessons for all 4 textbooks
    out.append("\n#################################################################")
    out.append("#   LESSON UNITS (per textbook)")
    out.append("#################################################################\n")
    for (num, label) in LESSONS_OLD:
        out.append(emit_lesson("TB_Old", num, label))
    for (num, label) in LESSONS_KNTT:
        out.append(emit_lesson("TB_KNTT", num, label))
    for (num, label) in LESSONS_CTST:
        out.append(emit_lesson("TB_CTST", num, label))
    for (num, label) in LESSONS_CD:
        out.append(emit_lesson("TB_CD", num, label))
    out.append("")

    out.append("\n#################################################################")
    out.append("#   EVENTS")
    out.append("#################################################################\n")
    for row in EVENTS:
        out.append(emit_event(row) + "\n")

    # Relationships
    out.append("\n#################################################################")
    out.append("#   PREREQUISITES (la tien de cua)")
    out.append("#################################################################\n")
    for a, b in PREREQUISITES:
        out.append(f"su9:{a} su9:prerequisiteOf su9:{b} .")

    out.append("\n\n#################################################################")
    out.append("#   CAUSAL - DIRECT")
    out.append("#################################################################\n")
    for a, b in CAUSES_DIRECT:
        out.append(f"su9:{a} su9:directCause su9:{b} .")

    out.append("\n\n#################################################################")
    out.append("#   CAUSAL - DEEP")
    out.append("#################################################################\n")
    for a, b in CAUSES_DEEP:
        out.append(f"su9:{a} su9:deepCause su9:{b} .")

    out.append("\n\n#################################################################")
    out.append("#   SIMILARITIES")
    out.append("#################################################################\n")
    for a, b in SIMILARITIES:
        out.append(f"su9:{a} su9:similarTo su9:{b} .")

    out.append("\n\n#################################################################")
    out.append("#   CONTRASTS")
    out.append("#################################################################\n")
    for a, b in CONTRASTS:
        out.append(f"su9:{a} su9:contrastsWith su9:{b} .")

    out.append("\n\n#################################################################")
    out.append("#   PARTICIPATION")
    out.append("#################################################################\n")
    for p, e, rel in PARTICIPATES:
        out.append(f"su9:{p} su9:{rel} su9:{e} .")

    out.append("\n\n#################################################################")
    out.append("#   INVOLVED CONCEPTS")
    out.append("#################################################################\n")
    for s, c in INVOLVED_CONCEPTS:
        out.append(f"su9:{s} su9:involvedConcept su9:{c} .")

    # Write
    ttl_path = ROOT / "ontology" / "su9.ttl"
    ttl_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\n[OK] Wrote {ttl_path}")

    # Validate + export OWL
    from rdflib import Graph
    g = Graph()
    g.parse(str(ttl_path), format="turtle")
    owl_path = ROOT / "ontology" / "su9.owl"
    g.serialize(destination=str(owl_path), format="xml")
    print(f"[OK] Wrote {owl_path}  ({len(g)} triples)")

    # Stats
    from rdflib import RDF
    from collections import Counter
    counts = Counter()
    for s, p, o in g.triples((None, RDF.type, None)):
        if "su9" in str(o):
            counts[str(o).split("#")[-1]] += 1
    print("\nEntity counts by class:")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k:15s} {v}")


if __name__ == "__main__":
    main()
