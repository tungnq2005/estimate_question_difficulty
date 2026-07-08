"""Build Physics 9 ontology."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "shared"))

ns: dict = {"__file__": str(ROOT / "build_data.py")}
with open(ROOT / "build_data.py", "r", encoding="utf-8") as f:
    exec(f.read(), ns)

from ttl_builder import build_ttl, quote


def _base(cls, prefix='phys'):
    """Emit factory helper for entities with uniform shape (id, label, aliases, abstract, bloom, conf)."""
    pass


def emit_law(row):
    lid, label, aliases, abstract, bloom, conf = row
    out = [f"phys:{lid} a phys:Law ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    phys:aliases "{quote(aliases)}" ;')
    out += [f"    phys:abstractness {abstract} ;",
            f"    phys:bloomLevel {bloom} ;",
            f"    phys:confidence {conf} ."]
    return "\n".join(out)


def emit_formula(row):
    fid, label, aliases, sym, steps, abstract, conf = row
    out = [f"phys:{fid} a phys:Formula ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    phys:aliases "{quote(aliases)}" ;')
    out += [f"    phys:symbolicDensity {sym} ;",
            f"    phys:applicationSteps {steps} ;",
            f"    phys:abstractness {abstract} ;",
            f"    phys:confidence {conf} ."]
    return "\n".join(out)


def emit_quantity(row):
    qid, label, symbol, unit_id, abstract, conf = row
    out = [f"phys:{qid} a phys:Quantity ;",
           f'    rdfs:label "{quote(label)}"@vi ;',
           f'    phys:symbol "{quote(symbol)}" ;']
    out += [f"    phys:abstractness {abstract} ;",
            f"    phys:confidence {conf} ."]
    return "\n".join(out)


def emit_unit(row):
    uid, label, symbol, conf = row
    return (f"phys:{uid} a phys:Unit ;\n"
            f'    rdfs:label "{quote(label)}"@vi ;\n'
            f'    phys:symbol "{quote(symbol)}" ;\n'
            f"    phys:confidence {conf} .")


def emit_phenomenon(row):
    pid, label, aliases, abstract, bloom, conf = row
    out = [f"phys:{pid} a phys:Phenomenon ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    phys:aliases "{quote(aliases)}" ;')
    out += [f"    phys:abstractness {abstract} ;",
            f"    phys:bloomLevel {bloom} ;",
            f"    phys:confidence {conf} ."]
    return "\n".join(out)


def emit_device(row):
    did, label, aliases, abstract, conf = row
    out = [f"phys:{did} a phys:Device ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    phys:aliases "{quote(aliases)}" ;')
    out += [f"    phys:abstractness {abstract} ;",
            f"    phys:confidence {conf} ."]
    return "\n".join(out)


def emit_concept(row):
    cid, label, aliases, abstract, bloom, conf = row
    out = [f"phys:{cid} a phys:Concept ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    phys:aliases "{quote(aliases)}" ;')
    out += [f"    phys:abstractness {abstract} ;",
            f"    phys:bloomLevel {bloom} ;",
            f"    phys:confidence {conf} ."]
    return "\n".join(out)


def emit_method(row):
    mid, label, aliases, steps, abstract, bloom, conf = row
    out = [f"phys:{mid} a phys:Method ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    phys:aliases "{quote(aliases)}" ;')
    out += [f"    phys:applicationSteps {steps} ;",
            f"    phys:abstractness {abstract} ;",
            f"    phys:bloomLevel {bloom} ;",
            f"    phys:confidence {conf} ."]
    return "\n".join(out)


def emit_problem(row):
    pid, label, aliases, abstract, bloom, conf = row
    out = [f"phys:{pid} a phys:ProblemType ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    phys:aliases "{quote(aliases)}" ;')
    out += [f"    phys:abstractness {abstract} ;",
            f"    phys:bloomLevel {bloom} ;",
            f"    phys:confidence {conf} ."]
    return "\n".join(out)


def emit_experiment(row):
    eid, label, aliases, bloom, conf = row
    out = [f"phys:{eid} a phys:ExperimentSetup ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    phys:aliases "{quote(aliases)}" ;')
    out += [f"    phys:bloomLevel {bloom} ;",
            f"    phys:confidence {conf} ."]
    return "\n".join(out)


def emit_lesson(tb_row):
    tb, num, label = tb_row
    return (f"phys:{tb}_B{num:02d} a phys:LessonUnit ;\n"
            f'    rdfs:label "{quote(f"[{tb}] Bai {num}: {label}")}"@vi ;\n'
            f"    phys:partOfTextbook phys:{tb} ;\n"
            f"    phys:curriculumPosition {num} .")


lessons_all = []
for tb, data_name in [("TB_Old", "LESSONS_OLD"), ("TB_KNTT", "LESSONS_KNTT"),
                     ("TB_CTST", "LESSONS_CTST"), ("TB_CD", "LESSONS_CD")]:
    for num, label in ns[data_name]:
        lessons_all.append((tb, num, label))


rel_lines = []
for a, b in ns["HAS_UNIT"]:
    rel_lines.append(f"phys:{a} phys:hasUnit phys:{b} .")
for a, b in ns["MEASURES"]:
    rel_lines.append(f"phys:{a} phys:measures phys:{b} .")
for a, b in ns["RELATES"]:
    rel_lines.append(f"phys:{a} phys:relatesQuantities phys:{b} .")
for a, b in ns["DERIVED_FROM"]:
    rel_lines.append(f"phys:{a} phys:derivedFrom phys:{b} .")
for a, b in ns["EXPLAINED_BY"]:
    rel_lines.append(f"phys:{a} phys:explainedBy phys:{b} .")
for a, b in ns["USED_IN"]:
    rel_lines.append(f"phys:{a} phys:usedIn phys:{b} .")
for a, b in ns["SOLVES"]:
    rel_lines.append(f"phys:{a} phys:solves phys:{b} .")
for a, b in ns["USES"]:
    rel_lines.append(f"phys:{a} phys:uses phys:{b} .")
for a, b in ns["PREREQUISITES"]:
    rel_lines.append(f"phys:{a} phys:prerequisiteOf phys:{b} .")
for a, b in ns["SIMILARITIES"]:
    rel_lines.append(f"phys:{a} phys:similarTo phys:{b} .")
for a, b in ns["CONTRASTS"]:
    rel_lines.append(f"phys:{a} phys:contrastsWith phys:{b} .")


groups = [
    ("LAWS", emit_law, ns["LAWS"]),
    ("FORMULAS", emit_formula, ns["FORMULAS"]),
    ("QUANTITIES", emit_quantity, ns["QUANTITIES"]),
    ("UNITS", emit_unit, ns["UNITS"]),
    ("PHENOMENA", emit_phenomenon, ns["PHENOMENA"]),
    ("DEVICES", emit_device, ns["DEVICES"]),
    ("CONCEPTS", emit_concept, ns["CONCEPTS"]),
    ("METHODS", emit_method, ns["METHODS"]),
    ("PROBLEM TYPES", emit_problem, ns["PROBLEM_TYPES"]),
    ("EXPERIMENTS", emit_experiment, ns["EXPERIMENTS"]),
    ("LESSON UNITS", emit_lesson, lessons_all),
    ("RELATIONSHIPS", lambda r: r, rel_lines),
]

(ROOT / "ontology").mkdir(exist_ok=True)
build_ttl("phys", ROOT / "ontology", ns["HEADER"], ns["SCHEMA"], groups)
