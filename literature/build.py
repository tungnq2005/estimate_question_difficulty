"""Build Ngu Van 9 ontology."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "shared"))

ns: dict = {"__file__": str(ROOT / "build_data.py")}
with open(ROOT / "build_data.py", "r", encoding="utf-8") as f:
    exec(f.read(), ns)

from ttl_builder import build_ttl, quote


def emit_period(row):
    pid, label, aliases, abstract, conf = row
    out = [f"lit:{pid} a lit:HistoricalPeriod ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    lit:aliases "{quote(aliases)}" ;')
    out += [f"    lit:abstractness {abstract} ;",
            f"    lit:confidence {conf} ."]
    return "\n".join(out)


def emit_genre(row):
    gid, label, aliases, abstract, conf = row
    out = [f"lit:{gid} a lit:Genre ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    lit:aliases "{quote(aliases)}" ;')
    out += [f"    lit:abstractness {abstract} ;",
            f"    lit:confidence {conf} ."]
    return "\n".join(out)


def emit_author(row):
    aid, label, aliases, period, abstract, freq, conf = row
    out = [f"lit:{aid} a lit:Author ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    lit:aliases "{quote(aliases)}" ;')
    out += [f"    lit:abstractness {abstract} ;",
            f"    lit:frequencyInTextbook {freq} ;",
            f"    lit:confidence {conf} ."]
    return "\n".join(out)


def emit_work(row):
    wid, label, aliases, author, period, genre, year, abstract, interp, hist, freq, conf = row
    out = [f"lit:{wid} a lit:LiteraryWork ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    lit:aliases "{quote(aliases)}" ;')
    if year:
        out.append(f'    lit:yearWritten "{quote(year)}" ;')
    out += [f"    lit:abstractness {abstract} ;",
            f"    lit:interpretiveDepth {interp} ;",
            f"    lit:historicalDistance {hist} ;",
            f"    lit:frequencyInTextbook {freq} ;",
            f"    lit:confidence {conf} ."]
    return "\n".join(out)


def emit_char(row):
    cid, label, work, abstract, conf = row
    return (f"lit:{cid} a lit:Character ;\n"
            f'    rdfs:label "{quote(label)}"@vi ;\n'
            f"    lit:abstractness {abstract} ;\n"
            f"    lit:confidence {conf} .")


def emit_device(row):
    did, label, aliases, abstract, conf = row
    out = [f"lit:{did} a lit:LiteraryDevice ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    lit:aliases "{quote(aliases)}" ;')
    out += [f"    lit:abstractness {abstract} ;",
            f"    lit:confidence {conf} ."]
    return "\n".join(out)


def emit_theme(row):
    tid, label, aliases, abstract, conf = row
    out = [f"lit:{tid} a lit:Theme ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    lit:aliases "{quote(aliases)}" ;')
    out += [f"    lit:abstractness {abstract} ;",
            f"    lit:confidence {conf} ."]
    return "\n".join(out)


def emit_lesson(tb_row):
    tb, num, label = tb_row
    return (f"lit:{tb}_B{num:02d} a lit:LessonUnit ;\n"
            f'    rdfs:label "{quote(f"[{tb}] Bai {num}: {label}")}"@vi ;\n'
            f"    lit:partOfTextbook lit:{tb} ;\n"
            f"    lit:curriculumPosition {num} .")


lessons_all = []
for tb, data_name in [("TB_Old", "LESSONS_OLD"), ("TB_KNTT", "LESSONS_KNTT"),
                     ("TB_CTST", "LESSONS_CTST"), ("TB_CD", "LESSONS_CD")]:
    for num, label in ns[data_name]:
        lessons_all.append((tb, num, label))


rel_lines = []
for a, b in ns["AUTHOR_ACTIVE_IN"]:
    rel_lines.append(f"lit:{a} lit:activeIn lit:{b} .")
for a, b in ns["AUTHORED_BY"]:
    rel_lines.append(f"lit:{a} lit:authoredBy lit:{b} .")
for a, b in ns["WRITTEN_IN"]:
    rel_lines.append(f"lit:{a} lit:writtenIn lit:{b} .")
for a, b in ns["HAS_GENRE"]:
    rel_lines.append(f"lit:{a} lit:hasGenre lit:{b} .")
for a, b in ns["CONTAINS_CHAR"]:
    rel_lines.append(f"lit:{a} lit:contains lit:{b} .")
for a, b in ns["WORK_USES_DEVICE"]:
    rel_lines.append(f"lit:{a} lit:uses lit:{b} .")
for a, b in ns["WORK_EXPRESSES"]:
    rel_lines.append(f"lit:{a} lit:expresses lit:{b} .")
for a, b in ns["RELATED"]:
    rel_lines.append(f"lit:{a} lit:relatedWork lit:{b} .")
for a, b in ns["SIMILARITIES"]:
    rel_lines.append(f"lit:{a} lit:similarTo lit:{b} .")
for a, b in ns["CONTRASTS"]:
    rel_lines.append(f"lit:{a} lit:contrastsWith lit:{b} .")


groups = [
    ("HISTORICAL PERIODS", emit_period, ns["PERIODS"]),
    ("GENRES", emit_genre, ns["GENRES"]),
    ("AUTHORS", emit_author, ns["AUTHORS"]),
    ("LITERARY WORKS", emit_work, ns["WORKS"]),
    ("CHARACTERS", emit_char, ns["CHARACTERS"]),
    ("LITERARY DEVICES", emit_device, ns["DEVICES"]),
    ("THEMES", emit_theme, ns["THEMES"]),
    ("LESSON UNITS", emit_lesson, lessons_all),
    ("RELATIONSHIPS", lambda r: r, rel_lines),
]

(ROOT / "ontology").mkdir(exist_ok=True)
build_ttl("lit", ROOT / "ontology", ns["HEADER"], ns["SCHEMA"], groups)
