# Verification Guide for Su9 Ontology v0.2

This ontology was built from general knowledge of the Vietnamese 9th-grade History
curriculum, not by direct reading of any specific SGK edition. Before using in a
paper, the following items **should be verified** by a Sử teacher or against
physical textbooks.

## Priority 1 — MUST verify

### Lesson mappings for new textbook series (post-2021)

The `appearsInLesson` links to `TB_KNTT`, `TB_CTST`, and `TB_CD` lesson numbers
were approximated from published tables of contents. The exact bài number, chapter
grouping, and whether a specific event/concept is actually covered may differ.

**Action:** open each of the 3 SGK tích hợp Lịch sử 9 (Kết nối tri thức, Chân trời
sáng tạo, Cánh Diều, 2024 edition) and verify the mapping for at least:

- Cách mạng tháng Tám 1945 (E_CachMangThangTam)
- Chiến dịch Điện Biên Phủ 1954 (E_DienBienPhu1954)
- Đại hội Đảng VI / Đổi mới (E_DaiHoi6_1986)
- Liên Xô tan rã (E_LienXoTanRa)
- Thành lập ASEAN (E_ThanhLapASEAN)

If the lesson numbers are wrong, edit in `build_ontology_part2.py` (the `EVENTS`
list, columns 10–12 for KNTT/CTST/CD) and re-run `python3 build_main.py`.

### Frequency counts (`frequencyInTextbook`)

All values are **estimates** scaled by perceived importance, NOT actual counts.
For a paper, these should be replaced with real frequency counts from the textbook
text. Priority entities to recount first are the high-frequency ones:

- `Pe_HoChiMinh` (estimated 80)
- `O_DangCongSanVN` (50)
- `O_VNDCCH` (30)
- `C_ChuNghiaXaHoi` (30)
- `E_CachMangThangTam` (25)

### Bloom level annotations

All `bloomLevel` values were set based on the concept's presumed cognitive demand
when first taught. Should be reviewed by 2+ teachers with Cohen's kappa measured
for paper submission.

## Priority 2 — SHOULD verify

### Prerequisite edges

The 96 prerequisite edges encode pedagogical sequencing — "to understand X,
students need to have learned Y first." Review especially:

- Chains ending at summary events (CMT8, DBP, GP miền Nam 1975) — these are deep
  (depth 15–27) and may be over-connected
- Causal vs prerequisite distinction: some edges might be better labeled as `deepCause`
  rather than `prerequisiteOf`

### Person-event participation

Some `participatesIn`/`leads` links for foreign leaders (Nixon, Johnson, Kennedy)
are coarse — verify if the textbook mentions them in that specific event.

## Priority 3 — Nice to verify

### Location hierarchies (`locatedIn`)

Mostly self-evident geography, but double-check administrative boundaries if
you plan to compute region-based features.

### Period boundaries

The overlapping periods (e.g., `P_1945_1954` vs `P_1945_1946` + `P_1946_1954`)
are intentional — the extractor picks the tightest-fitting period. But if you
want cleaner ontology, consolidate.

---

## How to verify efficiently

The ontology has a `confidence` property on every individual (values 1–3).

```python
from rdflib import Graph, Namespace
SU9 = Namespace("http://su9.edu.vn/ontology#")
g = Graph().parse("ontology/su9.ttl", format="turtle")

# Find everything marked low-confidence
for s in g.subjects(SU9.confidence, None):
    conf = int(next(g.objects(s, SU9.confidence)))
    if conf <= 1:
        label = next(g.objects(s, SU9.label), s)
        print(f"[conf={conf}] {label}")
```

After verification, update the value in the Python source (`build_ontology*.py`)
and re-run `build_main.py`.

---

## What does NOT need verification

- Historical dates and events — these are well-established facts.
- Entity class assignments (Event vs Person vs Concept).
- The ontology schema itself (classes and object properties).
- The feature extraction code.
