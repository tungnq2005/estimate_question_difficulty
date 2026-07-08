# Su9 Ontology — Cold-start Question Difficulty Estimation (History Grade 9)

**Version 0.2** — Expanded domain ontology + feature pipeline for estimating the
difficulty of Vietnamese 9th-grade History exam questions **before** any student
response data is available (cold-start setting). Designed to plug into an existing
XGBoost regression/classification pipeline as an additional feature block alongside
linguistic and IRT-style features.

### What's in v0.2 (vs v0.1)
- **323 entities** across 9 classes (was 101) — ~3× expansion
- **84 lesson units** across 4 textbook series (was 34 in bộ cũ only):
  - SGK cũ (trước 2021), Kết nối tri thức, Chân trời sáng tạo, Cánh Diều
- **96 prerequisite edges** forming deep reasoning chains (was 25)
- **27 causal edges** (direct + deep)
- **Multi-textbook `appearsInLesson`** property — one entity can be mapped to different
  lessons across textbook series
- **`confidence` data property** (1–3) flags entities that need teacher verification
- 3024 triples total (was 778)

---

## 1. Project structure

```
su9_ontology/
├── ontology/
│   ├── su9.ttl            # Turtle format (readable, edit this)
│   └── su9.owl            # RDF/XML (generated, for Protege)
├── src/
│   ├── ontology_loader.py     # Load OWL + build NetworkX graph + precompute metrics
│   ├── entity_extraction.py   # Dictionary NER + year/period linking + optional underthesea
│   ├── feature_extraction.py  # 46 difficulty features across 8 groups
│   └── pipeline.py            # End-to-end: question -> DataFrame
├── data/
│   ├── sample_questions.json  # 10 demo questions with difficulty hints
│   └── features_demo.csv      # (generated) feature matrix from demo.py
├── demo.py                    # Run end-to-end and show feature-difficulty correlations
└── README.md
```

---

## 2. Setup

```bash
pip install rdflib networkx pandas
# Optional (for extending with Vietnamese NER beyond dictionary matching):
pip install underthesea
```

Python 3.9+.

---

## 3. Quick start

```python
from src.pipeline import Su9DifficultyPipeline

pipe = Su9DifficultyPipeline("ontology/su9.ttl")

# Single question
feat = pipe.featurize_one("Phân tích ý nghĩa của chiến dịch Điện Biên Phủ 1954.")
print(feat.values)          # dict of 46 features
print(feat.meta["linked_labels"])  # entities found

# Batch -> DataFrame ready for XGBoost
import pandas as pd
df = pipe.featurize([q1, q2, q3, ...])
# X = df.drop(columns=["question_id", "question"])
# model.fit(X, y_difficulty)
```

Run `python demo.py` to see the full pipeline on 10 sample questions, including
Spearman correlation of each feature with teacher-hinted difficulty.

---

## 4. Ontology design

### Classes
- `Event` — specific historical events (CMT8, ĐBP, Đổi mới, ...)
- `Person` — historical figures (Hồ Chí Minh, Võ Nguyên Giáp, Gorbachev, ...)
- `Location` — places (Hà Nội, Điện Biên Phủ, Liên Xô, ...)
- `Period` — time frames (1919–1930, Chiến tranh Lạnh, ...)
- `Organization` — ĐCSVN, Việt Minh, ASEAN, NATO, ...
- `Movement` — phong trào (Đông Du, Cần Vương, Dân chủ 1936–1939, ...)
- `Document` — hiệp định, cương lĩnh, tuyên ngôn
- `Concept` — abstract concepts (CNXH, Chiến tranh Lạnh, Toàn cầu hóa, ...)
- `LessonUnit` — 34 bài trong SGK

### Key properties

| Property | Type | Used for |
|---|---|---|
| `prerequisiteOf` | transitive | **Depth-of-knowledge** — the core difficulty signal |
| `directCause` / `deepCause` | sub-prop of `causes` | Distinguishes immediate vs. underlying causes (questions about deep causes are harder) |
| `similarTo` / `contrastsWith` | symmetric | Links for comparison questions |
| `belongsToLesson` | — | Curriculum position lookup |
| `bloomLevel` | int 1–4 | Biết / Hiểu / Vận dụng / Vận dụng cao |
| `abstractness` | int 1–5 | Concrete dates (1) to abstract xu thế (5) |
| `frequencyInTextbook` | int | Rarity → harder (IDF-style signal) |
| `curriculumPosition` | int 1–34 | Later lessons presumed harder |

### Extending the ontology
Open `ontology/su9.ttl` — it is deliberately written as a readable Turtle file.
To add a new event:

```turtle
su9:E_YourEventName a su9:Event ;
    rdfs:label "Display Name"@vi ;
    su9:aliases "Alt name 1|Alt name 2" ;
    su9:occursAt su9:L_SomeLocation ;
    su9:belongsToLesson su9:B25 ;
    su9:bloomLevel 2 ;
    su9:abstractness 3 ;
    su9:frequencyInTextbook 8 .

# Optional: add prerequisite edges
su9:E_SomeEarlierEvent su9:prerequisiteOf su9:E_YourEventName .
```

After editing, regenerate the RDF/XML for Protégé:
```python
from rdflib import Graph
Graph().parse("ontology/su9.ttl").serialize("ontology/su9.owl", format="xml")
```

---

## 5. Feature groups (46 features total)

| Group | # feats | Examples | Why it signals difficulty |
|---|---|---|---|
| Entity counts | 11 | `num_unique_entities`, `count_event`, `type_diversity` | More entities / types = more ground to cover |
| Abstractness | 4 | `abstractness_max`, `abstractness_range` | Abstract concepts (CNXH, trật tự hai cực) are harder than dates |
| Rarity | 4 | `inv_freq_sum`, `log_inv_freq_mean` | Rarely-seen entities are less familiar |
| Prerequisite depth | 3 | `prereq_depth_max`, `prereq_depth_sum` | Deep chains require more prior knowledge |
| Graph structure | 6 | `centrality_mean`, `sem_dist_max`, `sem_dist_disconnected` | Peripheral or disconnected entities = harder bridging |
| Curriculum | 5 | `curr_pos_max`, `crosses_periods`, `world_vs_vn_mix` | Cross-era or cross-region questions are harder |
| Bloom / cognitive | 8 | `bloom_annotated_max`, `bloom_inferred`, `qtype_analytical`, `qtype_evaluative` | Higher Bloom = harder cognitive demand |
| Linguistic surface | 5 | `q_length_words`, `num_cue_phrases` | Basic but useful control features |

The **annotated Bloom vs. inferred Bloom distinction** is deliberate: `bloom_annotated`
comes from the ontology (what level the concept was introduced at in the textbook),
`bloom_inferred` comes from the interrogative verb in the question. `bloom_combined_max`
takes the max — this is the feature that correlated ρ = +0.94 with teacher-hinted
difficulty on our 10-question demo.

---

## 6. Integrating with your existing XGBoost pipeline

```python
# Your existing features (linguistic, IRT / RSI if you have response data)
X_existing = your_existing_featurizer(questions)

# New ontology features
from src.pipeline import Su9DifficultyPipeline
pipe = Su9DifficultyPipeline("ontology/su9.ttl")
df = pipe.featurize(questions)
X_ontology = df.drop(columns=["question_id", "question"]).values

# Concatenate and train
import numpy as np
X = np.hstack([X_existing, X_ontology])
model = XGBClassifier(...).fit(X, y)
```

For **ablation studies** (which is what reviewers will want):

1. `baseline` = RSI / response-stat features only
2. `+ontology` = baseline + ontology features (46 new dims)
3. `ontology-only` = ontology features only (demonstrates cold-start feasibility)
4. `full` = baseline + ontology + linguistic embeddings (PhoBERT)

---

## 7. Limitations & roadmap

**Current scope.** Seed ontology with ~100 individuals. Sufficient to demonstrate
the approach on selected questions; for full-syllabus coverage, aim for 300–500
individuals and systematically annotate all 34 bài.

**NER coverage.** The dictionary-based extractor resolves everything in the
ontology. Questions referencing entities **not** yet in the ontology will be
missed by dictionary matching — set `use_ner=True` when constructing the pipeline
to get underthesea suggestions for unlinked mentions (useful for identifying
ontology gaps during annotation).

**Prerequisite depth is hand-curated.** For scaling, consider learning prerequisite
edges from the SGK text (e.g., following Liang et al. on concept prerequisite
learning) rather than manual annotation.

**Inter-annotator agreement.** Bloom level and abstractness values should
ideally be set by ≥2 teachers with Cohen's kappa reported — important for paper
submissions to AIED / EDM / BEA.

**Language of identifiers.** Ontology identifiers and labels are stored in
unaccented Vietnamese for filesystem/tool portability; the extractor handles
diacritic folding so real-world questions with diacritics match correctly.

---

## 8. Paper-writing notes

Features where this approach is novel compared to most question-difficulty work:

1. **`prereq_depth_max` / `sem_dist_disconnected`** — graph-structural signals
   computed from a domain ontology. Rarely seen in prior work on QDE.
2. **`bloom_combined_max`** — combining ontology-annotated Bloom (what level was
   this concept taught at?) with interrogative-inferred Bloom (what level does
   this question require?) is distinct from either alone.
3. **`crosses_periods`, `world_vs_vn_mix`** — curriculum-aware features specific
   to history as a domain.

For the ablation table, we recommend reporting: (baseline RSI), (ontology-only
= cold-start), (ontology + linguistic), (full). The cold-start row is the one
that makes this paper distinct from prior IRT-based work.

Cite/compare with: Liang et al. 2018 (concept prerequisite learning), Pandarova
et al. 2019 (linguistic difficulty features), Benedetto et al. 2020 (transformer-
based QDE).
