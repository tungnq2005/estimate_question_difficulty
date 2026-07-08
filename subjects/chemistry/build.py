"""Build Chemistry 9 ontology."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

ns: dict = {"__file__": str(ROOT / "build_data.py")}
with open(ROOT / "build_data.py", "r", encoding="utf-8") as f:
    exec(f.read(), ns)

from shared.ttl_builder import build_ttl, quote


def emit_subclass(row):
    cid, label, aliases, abstract, conf = row
    out = [f"chem:{cid} a chem:SubstanceClass ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    chem:aliases "{quote(aliases)}" ;')
    out.extend([f"    chem:abstractness {abstract} ;",
                f"    chem:confidence {conf} ."])
    return "\n".join(out)


def emit_substance(row):
    sid, label, formula, aliases, cls, freq, abstract, conf = row
    out = [f"chem:{sid} a chem:Substance ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if formula:
        out.append(f'    chem:formula "{quote(formula)}" ;')
    all_aliases = aliases + (f"|{formula}" if formula and aliases else (formula if formula else ""))
    if all_aliases:
        out.append(f'    chem:aliases "{quote(all_aliases)}" ;')
    out.extend([f"    chem:frequencyInTextbook {freq} ;",
                f"    chem:abstractness {abstract} ;",
                f"    chem:confidence {conf} ."])
    return "\n".join(out)


def emit_reaction_type(row):
    rid, label, aliases, abstract, bloom, conf = row
    out = [f"chem:{rid} a chem:ReactionType ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    chem:aliases "{quote(aliases)}" ;')
    out.extend([f"    chem:abstractness {abstract} ;",
                f"    chem:bloomLevel {bloom} ;",
                f"    chem:confidence {conf} ."])
    return "\n".join(out)


def emit_property(row):
    pid, label, aliases, abstract, bloom, conf = row
    out = [f"chem:{pid} a chem:Property ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    chem:aliases "{quote(aliases)}" ;')
    out.extend([f"    chem:abstractness {abstract} ;",
                f"    chem:bloomLevel {bloom} ;",
                f"    chem:confidence {conf} ."])
    return "\n".join(out)


def emit_fg(row):
    fid, label, aliases, abstract, conf = row
    out = [f"chem:{fid} a chem:FunctionalGroup ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    chem:aliases "{quote(aliases)}" ;')
    out.extend([f"    chem:abstractness {abstract} ;",
                f"    chem:confidence {conf} ."])
    return "\n".join(out)


def emit_concept(row):
    cid, label, aliases, abstract, bloom, conf = row
    out = [f"chem:{cid} a chem:Concept ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    chem:aliases "{quote(aliases)}" ;')
    out.extend([f"    chem:abstractness {abstract} ;",
                f"    chem:bloomLevel {bloom} ;",
                f"    chem:confidence {conf} ."])
    return "\n".join(out)


def emit_process(row):
    pid, label, aliases, steps, abstract, bloom, conf = row
    out = [f"chem:{pid} a chem:Process ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    chem:aliases "{quote(aliases)}" ;')
    out.extend([f"    chem:stepsInSynthesis {steps} ;",
                f"    chem:abstractness {abstract} ;",
                f"    chem:bloomLevel {bloom} ;",
                f"    chem:confidence {conf} ."])
    return "\n".join(out)


def emit_reaction(row):
    rid, label, aliases, rtype, bal_complex, bloom, conf = row
    out = [f"chem:{rid} a chem:Reaction ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    chem:aliases "{quote(aliases)}" ;')
    out.extend([
        f"    chem:reactionType chem:{rtype} ;",
        f"    chem:balancingComplexity {bal_complex} ;",
        f"    chem:bloomLevel {bloom} ;",
        f"    chem:confidence {conf} .",
    ])
    return "\n".join(out)


def emit_lesson(tb_row):
    tb, num, label = tb_row
    return (f"chem:{tb}_B{num:02d} a chem:LessonUnit ;\n"
            f'    rdfs:label "{quote(f"[{tb}] Bai {num}: {label}")}"@vi ;\n'
            f"    chem:partOfTextbook chem:{tb} ;\n"
            f"    chem:curriculumPosition {num} .")


lessons_all = []
for tb, data_name in [("TB_Old", "LESSONS_OLD"), ("TB_KNTT", "LESSONS_KNTT"),
                     ("TB_CTST", "LESSONS_CTST"), ("TB_CD", "LESSONS_CD")]:
    for num, label in ns[data_name]:
        lessons_all.append((tb, num, label))


rel_lines = []
for a, b in ns["INSTANCE_OF"]:
    rel_lines.append(f"chem:{a} chem:instanceOf chem:{b} .")
for a, b in ns["HAS_PROPERTY"]:
    rel_lines.append(f"chem:{a} chem:hasProperty chem:{b} .")
for a, b in ns["CONTAINS"]:
    rel_lines.append(f"chem:{a} chem:contains chem:{b} .")
for a, b in ns["REACTION_REACTANTS"]:
    rel_lines.append(f"chem:{a} chem:reactant chem:{b} .")
for a, b in ns["REACTION_PRODUCTS"]:
    rel_lines.append(f"chem:{a} chem:product chem:{b} .")
for a, b in ns["PRODUCES"]:
    rel_lines.append(f"chem:{a} chem:produces chem:{b} .")
for a, b in ns["PREREQUISITES"]:
    rel_lines.append(f"chem:{a} chem:prerequisiteOf chem:{b} .")
for a, b in ns["SIMILARITIES"]:
    rel_lines.append(f"chem:{a} chem:similarTo chem:{b} .")
for a, b in ns["CONTRASTS"]:
    rel_lines.append(f"chem:{a} chem:contrastsWith chem:{b} .")


groups = [
    ("SUBSTANCE CLASSES", emit_subclass, ns["SUBSTANCE_CLASSES"]),
    ("SUBSTANCES", emit_substance, ns["SUBSTANCES"]),
    ("REACTION TYPES", emit_reaction_type, ns["REACTION_TYPES"]),
    ("PROPERTIES", emit_property, ns["PROPERTIES"]),
    ("FUNCTIONAL GROUPS", emit_fg, ns["FUNCTIONAL_GROUPS"]),
    ("CONCEPTS", emit_concept, ns["CONCEPTS"]),
    ("PROCESSES", emit_process, ns["PROCESSES"]),
    ("REACTIONS", emit_reaction, ns["REACTIONS"]),
    ("LESSON UNITS", emit_lesson, lessons_all),
    ("RELATIONSHIPS", lambda r: r, rel_lines),
]

(ROOT / "ontology").mkdir(exist_ok=True)
build_ttl("chem", ROOT / "ontology", ns["HEADER"], ns["SCHEMA"], groups)
