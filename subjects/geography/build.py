"""Build Geography 9 ontology."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

ns: dict = {"__file__": str(ROOT / "build_data.py")}
with open(ROOT / "build_data.py", "r", encoding="utf-8") as f:
    exec(f.read(), ns)

from shared.ttl_builder import build_ttl, quote


def emit_region(row):
    rid, label, aliases, scope, freq, abstract, conf = row
    out = [f"geo:{rid} a geo:Region ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    geo:aliases "{quote(aliases)}" ;')
    out.extend([f"    geo:spatialScope {scope} ;",
                f"    geo:frequencyInTextbook {freq} ;",
                f"    geo:abstractness {abstract} ;",
                f"    geo:confidence {conf} ."])
    return "\n".join(out)


def emit_simple(cls):
    def f(row):
        eid, label, aliases, freq, abstract, conf = row
        out = [f"geo:{eid} a geo:{cls} ;",
               f'    rdfs:label "{quote(label)}"@vi ;']
        if aliases:
            out.append(f'    geo:aliases "{quote(aliases)}" ;')
        out.extend([f"    geo:frequencyInTextbook {freq} ;",
                    f"    geo:abstractness {abstract} ;",
                    f"    geo:confidence {conf} ."])
        return "\n".join(out)
    return f


def emit_with_scope(cls):
    """For entities with an extra spatialScope field before freq."""
    def f(row):
        eid, label, aliases, scope, freq, abstract, conf = row
        out = [f"geo:{eid} a geo:{cls} ;",
               f'    rdfs:label "{quote(label)}"@vi ;']
        if aliases:
            out.append(f'    geo:aliases "{quote(aliases)}" ;')
        out.extend([f"    geo:spatialScope {scope} ;",
                    f"    geo:frequencyInTextbook {freq} ;",
                    f"    geo:abstractness {abstract} ;",
                    f"    geo:confidence {conf} ."])
        return "\n".join(out)
    return f


def emit_phenomenon(row):
    pid, label, aliases, scope, factors, freq, abstract, bloom, conf = row
    out = [f"geo:{pid} a geo:Phenomenon ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    geo:aliases "{quote(aliases)}" ;')
    out.extend([f"    geo:spatialScope {scope} ;",
                f"    geo:explanatoryFactors {factors} ;",
                f"    geo:frequencyInTextbook {freq} ;",
                f"    geo:abstractness {abstract} ;",
                f"    geo:bloomLevel {bloom} ;",
                f"    geo:confidence {conf} ."])
    return "\n".join(out)


def emit_with_bloom(cls):
    def f(row):
        eid, label, aliases, freq, abstract, bloom, conf = row
        out = [f"geo:{eid} a geo:{cls} ;",
               f'    rdfs:label "{quote(label)}"@vi ;']
        if aliases:
            out.append(f'    geo:aliases "{quote(aliases)}" ;')
        out.extend([f"    geo:frequencyInTextbook {freq} ;",
                    f"    geo:abstractness {abstract} ;",
                    f"    geo:bloomLevel {bloom} ;",
                    f"    geo:confidence {conf} ."])
        return "\n".join(out)
    return f


def emit_process(row):
    pid, label, aliases, abstract, freq, bloom, conf = row
    out = [f"geo:{pid} a geo:Process ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    geo:aliases "{quote(aliases)}" ;')
    out.extend([f"    geo:frequencyInTextbook {freq} ;",
                f"    geo:abstractness {abstract} ;",
                f"    geo:bloomLevel {bloom} ;",
                f"    geo:confidence {conf} ."])
    return "\n".join(out)


def emit_lesson(tb_row):
    tb, num, label = tb_row
    return (f"geo:{tb}_B{num:02d} a geo:LessonUnit ;\n"
            f'    rdfs:label "{quote(f"[{tb}] Bai {num}: {label}")}"@vi ;\n'
            f"    geo:partOfTextbook geo:{tb} ;\n"
            f"    geo:curriculumPosition {num} .")


lessons_all = []
for tb, data_name in [("TB_Old", "LESSONS_OLD"), ("TB_KNTT", "LESSONS_KNTT"),
                     ("TB_CTST", "LESSONS_CTST"), ("TB_CD", "LESSONS_CD")]:
    for num, label in ns[data_name]:
        lessons_all.append((tb, num, label))


rel_lines = []
for a, b in ns["LOCATED_IN"]:
    rel_lines.append(f"geo:{a} geo:locatedIn geo:{b} .")
for a, b in ns["ADJACENT_TO"]:
    rel_lines.append(f"geo:{a} geo:adjacentTo geo:{b} .")
for a, b in ns["HAS_RESOURCE"]:
    rel_lines.append(f"geo:{a} geo:hasResource geo:{b} .")
for a, b in ns["SPECIALIZES_IN"]:
    rel_lines.append(f"geo:{a} geo:specializesIn geo:{b} .")
for a, b in ns["GROWN_IN"]:
    rel_lines.append(f"geo:{a} geo:grownIn geo:{b} .")
for a, b in ns["RAISED_IN"]:
    rel_lines.append(f"geo:{a} geo:raisedIn geo:{b} .")
for a, b in ns["OCCURS_IN"]:
    rel_lines.append(f"geo:{a} geo:occursIn geo:{b} .")
for a, b in ns["CAUSES"]:
    rel_lines.append(f"geo:{a} geo:causes geo:{b} .")
for a, b in ns["PREREQUISITES"]:
    rel_lines.append(f"geo:{a} geo:prerequisiteOf geo:{b} .")
for a, b in ns["SIMILARITIES"]:
    rel_lines.append(f"geo:{a} geo:similarTo geo:{b} .")
for a, b in ns["CONTRASTS"]:
    rel_lines.append(f"geo:{a} geo:contrastsWith geo:{b} .")


groups = [
    ("REGIONS", emit_region, ns["REGIONS"]),
    ("NATURAL FEATURES", emit_simple("NaturalFeature"), ns["NATURAL_FEATURES"]),
    ("PHENOMENA", emit_phenomenon, ns["PHENOMENA"]),
    ("RESOURCES", emit_with_scope("Resource"), ns["RESOURCES"]),
    ("INDUSTRIES", emit_with_scope("Industry"), ns["INDUSTRIES"]),
    ("CROPS", emit_simple("Crop"), ns["CROPS"]),
    ("LIVESTOCK", emit_simple("Livestock"), ns["LIVESTOCK"]),
    ("DEMOGRAPHIC", emit_with_bloom("Demographic"), ns["DEMOGRAPHIC"]),
    ("CONCEPTS", emit_with_bloom("Concept"), ns["CONCEPTS"]),
    ("PROCESSES", emit_process, ns["PROCESSES"]),
    ("LESSON UNITS", emit_lesson, lessons_all),
    ("RELATIONSHIPS", lambda r: r, rel_lines),
]

(ROOT / "ontology").mkdir(exist_ok=True)
build_ttl("geo", ROOT / "ontology", ns["HEADER"], ns["SCHEMA"], groups)
