"""Build Tieng Anh 9 ontology."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "shared"))

ns: dict = {"__file__": str(ROOT / "build_data.py")}
with open(ROOT / "build_data.py", "r", encoding="utf-8") as f:
    exec(f.read(), ns)

from ttl_builder import build_ttl, quote


def emit_grammar(row):
    gid, label, aliases, cefr, complex_, abstract, bloom, conf = row
    out = [f"eng:{gid} a eng:GrammarStructure ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    eng:aliases "{quote(aliases)}" ;')
    out += [f'    eng:cefrLevel "{cefr}" ;',
            f"    eng:structuralComplexity {complex_} ;",
            f"    eng:abstractness {abstract} ;",
            f"    eng:bloomLevel {bloom} ;",
            f"    eng:confidence {conf} ."]
    return "\n".join(out)


def emit_vocab(row):
    vid, label, aliases, band, freq, abstract, conf = row
    out = [f"eng:{vid} a eng:VocabularyTopic ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    eng:aliases "{quote(aliases)}" ;')
    out += [f"    eng:frequencyBand {band} ;",
            f"    eng:frequencyInTextbook {freq} ;",
            f"    eng:abstractness {abstract} ;",
            f"    eng:confidence {conf} ."]
    return "\n".join(out)


def emit_function(row):
    fid, label, aliases, abstract, bloom, conf = row
    out = [f"eng:{fid} a eng:LanguageFunction ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    eng:aliases "{quote(aliases)}" ;')
    out += [f"    eng:abstractness {abstract} ;",
            f"    eng:bloomLevel {bloom} ;",
            f"    eng:confidence {conf} ."]
    return "\n".join(out)


def emit_skill(row):
    sid, label, aliases, abstract, bloom, conf = row
    out = [f"eng:{sid} a eng:SkillType ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    eng:aliases "{quote(aliases)}" ;')
    out += [f"    eng:abstractness {abstract} ;",
            f"    eng:bloomLevel {bloom} ;",
            f"    eng:confidence {conf} ."]
    return "\n".join(out)


def emit_text_type(row):
    tid, label, aliases, abstract, bloom, conf = row
    out = [f"eng:{tid} a eng:TextType ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    eng:aliases "{quote(aliases)}" ;')
    out += [f"    eng:abstractness {abstract} ;",
            f"    eng:bloomLevel {bloom} ;",
            f"    eng:confidence {conf} ."]
    return "\n".join(out)


def emit_lesson(tb_row):
    tb, num, label = tb_row
    return (f"eng:{tb}_B{num:02d} a eng:LessonUnit ;\n"
            f'    rdfs:label "{quote(f"[{tb}] Unit {num}: {label}")}"@vi ;\n'
            f"    eng:partOfTextbook eng:{tb} ;\n"
            f"    eng:curriculumPosition {num} .")


lessons_all = []
for tb, data_name in [("TB_Old", "LESSONS_OLD"), ("TB_ThiDiem", "LESSONS_ThiDiem"),
                      ("TB_GlobalSuccess", "LESSONS_GS"), ("TB_Friends", "LESSONS_Friends")]:
    for num, label in ns[data_name]:
        lessons_all.append((tb, num, label))


rel_lines = []
for a, b in ns["PREREQUISITES"]:
    rel_lines.append(f"eng:{a} eng:prerequisiteOf eng:{b} .")
for a, b in ns["SPEC_GRAMMAR"]:
    rel_lines.append(f"eng:{a} eng:specializesGrammar eng:{b} .")
for a, b in ns["EXPRESSES"]:
    rel_lines.append(f"eng:{a} eng:expresses eng:{b} .")
for a, b in ns["USES_GRAMMAR"]:
    rel_lines.append(f"eng:{a} eng:usesGrammar eng:{b} .")
for a, b in ns["USES_VOCAB"]:
    rel_lines.append(f"eng:{a} eng:usesVocabulary eng:{b} .")
for a, b in ns["RELATED_VOCAB"]:
    rel_lines.append(f"eng:{a} eng:relatedVocab eng:{b} .")
for a, b in ns["SIMILARITIES"]:
    rel_lines.append(f"eng:{a} eng:similarTo eng:{b} .")
for a, b in ns["CONTRASTS"]:
    rel_lines.append(f"eng:{a} eng:contrastsWith eng:{b} .")


groups = [
    ("GRAMMAR STRUCTURES", emit_grammar, ns["GRAMMAR"]),
    ("VOCABULARY TOPICS", emit_vocab, ns["VOCAB"]),
    ("LANGUAGE FUNCTIONS", emit_function, ns["FUNCTIONS"]),
    ("SKILL TYPES", emit_skill, ns["SKILLS"]),
    ("TEXT TYPES", emit_text_type, ns["TEXT_TYPES"]),
    ("LESSON UNITS", emit_lesson, lessons_all),
    ("RELATIONSHIPS", lambda r: r, rel_lines),
]

(ROOT / "ontology").mkdir(exist_ok=True)
build_ttl("eng", ROOT / "ontology", ns["HEADER"], ns["SCHEMA"], groups)
