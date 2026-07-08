"""Build Math 9 ontology Turtle + OWL."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Load data
ns: dict = {"__file__": str(ROOT / "build_data.py")}
with open(ROOT / "build_data.py", "r", encoding="utf-8") as f:
    exec(f.read(), ns)

from shared.ttl_builder import build_ttl, quote


def emit_def(row):
    did, label, aliases, abstract, conf = row
    out = [f"math:{did} a math:Definition ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    math:aliases "{quote(aliases)}" ;')
    out.extend([f"    math:abstractness {abstract} ;",
                f"    math:confidence {conf} ."])
    return "\n".join(out)


def emit_theorem(row):
    tid, label, aliases, abstract, bloom, conf = row
    out = [f"math:{tid} a math:Theorem ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    math:aliases "{quote(aliases)}" ;')
    out.extend([f"    math:abstractness {abstract} ;",
                f"    math:bloomLevel {bloom} ;",
                f"    math:reasoningType \"prove\" ;",
                f"    math:confidence {conf} ."])
    return "\n".join(out)


def emit_formula(row):
    fid, label, aliases, symdens, steps, abstract, conf = row
    out = [f"math:{fid} a math:Formula ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    math:aliases "{quote(aliases)}" ;')
    out.extend([f"    math:symbolicDensity {symdens} ;",
                f"    math:applicationSteps {steps} ;",
                f"    math:abstractness {abstract} ;",
                f"    math:reasoningType \"compute\" ;",
                f"    math:confidence {conf} ."])
    return "\n".join(out)


def emit_concept(row):
    cid, label, aliases, abstract, bloom, conf = row
    out = [f"math:{cid} a math:Concept ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    math:aliases "{quote(aliases)}" ;')
    out.extend([f"    math:abstractness {abstract} ;",
                f"    math:bloomLevel {bloom} ;",
                f"    math:confidence {conf} ."])
    return "\n".join(out)


def emit_method(row):
    mid, label, aliases, steps, abstract, bloom, conf = row
    out = [f"math:{mid} a math:Method ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    math:aliases "{quote(aliases)}" ;')
    out.extend([f"    math:applicationSteps {steps} ;",
                f"    math:abstractness {abstract} ;",
                f"    math:bloomLevel {bloom} ;",
                f"    math:confidence {conf} ."])
    return "\n".join(out)


def emit_problem_type(row):
    pid, label, aliases, abstract, bloom, conf = row
    out = [f"math:{pid} a math:ProblemType ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    math:aliases "{quote(aliases)}" ;')
    out.extend([f"    math:abstractness {abstract} ;",
                f"    math:bloomLevel {bloom} ;",
                f"    math:confidence {conf} ."])
    return "\n".join(out)


def emit_object(row):
    oid, label, aliases, abstract, conf = row
    out = [f"math:{oid} a math:Object ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    math:aliases "{quote(aliases)}" ;')
    out.extend([f"    math:abstractness {abstract} ;",
                f"    math:confidence {conf} ."])
    return "\n".join(out)


def emit_lesson(tb_row):
    tb, num, label = tb_row
    return (f"math:{tb}_B{num:02d} a math:LessonUnit ;\n"
            f'    rdfs:label "{quote(f"[{tb}] Bai {num}: {label}")}"@vi ;\n'
            f"    math:partOfTextbook math:{tb} ;\n"
            f"    math:curriculumPosition {num} .")


# Collect lessons across textbooks
lessons_all = []
for tb, data_name in [("TB_Old", "LESSONS_OLD"), ("TB_KNTT", "LESSONS_KNTT"),
                     ("TB_CTST", "LESSONS_CTST"), ("TB_CD", "LESSONS_CD")]:
    for num, label in ns[data_name]:
        lessons_all.append((tb, num, label))


# Emit relationships
rel_lines = []
for a, b in ns["PREREQUISITES"]:
    rel_lines.append(f"math:{a} math:prerequisiteOf math:{b} .")
for a, b in ns["USES"]:
    rel_lines.append(f"math:{a} math:uses math:{b} .")
for a, b in ns["SOLVES"]:
    rel_lines.append(f"math:{a} math:solves math:{b} .")
for a, b in ns["APPLIES_TO"]:
    rel_lines.append(f"math:{a} math:appliesTo math:{b} .")
for a, b in ns["SIMILARITIES"]:
    rel_lines.append(f"math:{a} math:similarTo math:{b} .")
for a, b in ns["CONTRASTS"]:
    rel_lines.append(f"math:{a} math:contrastsWith math:{b} .")


groups = [
    ("DEFINITIONS", emit_def, ns["DEFINITIONS"]),
    ("THEOREMS", emit_theorem, ns["THEOREMS"]),
    ("FORMULAS", emit_formula, ns["FORMULAS"]),
    ("CONCEPTS", emit_concept, ns["CONCEPTS"]),
    ("METHODS", emit_method, ns["METHODS"]),
    ("PROBLEM TYPES", emit_problem_type, ns["PROBLEM_TYPES"]),
    ("OBJECTS", emit_object, ns["OBJECTS"]),
    ("LESSON UNITS", emit_lesson, lessons_all),
    ("RELATIONSHIPS", lambda r: r, rel_lines),
]

(ROOT / "ontology").mkdir(exist_ok=True)
build_ttl("math", ROOT / "ontology", ns["HEADER"], ns["SCHEMA"], groups)
