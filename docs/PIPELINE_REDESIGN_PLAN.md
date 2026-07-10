# Kế hoạch: Pipeline độ khó theo cụm môn (Cluster-aware MCQ pipeline)

> **TIẾN ĐỘ (07/2026)** — đã triển khai xong phần lớn:
> - ✅ GĐ1: `SubjectConfig.cluster` + `prereq_edge` + lọc property/class
>   chết khỏi auto-discovery (`shared/subjects.py`, `ontology_bridge.py`).
> - ✅ Determinism fix (phát sinh, có duyệt): pipeline trước đó lệch 57 giá
>   trị giữa 2 lần chạy cùng code — đã sửa tận gốc, xem `DEFERRED.md` Nhóm B.
> - ✅ GĐ2: `entity_match_coverage` (feature 34) — vào top-4 importance khi
>   train thật trên 679 câu Sử.
> - ✅ GĐ3: 4 feature numeric cụm C (`shared/mcq/numeric_features.py`, thiết
>   kế đã chỉnh theo khảo sát distractor thực tế — bắt "hệ số trượt tay
>   kinh điển" và "đảo tử-mẫu") + 3 feature attribution cụm D
>   (`shared/mcq/literature_features.py`). Tổng dataclass: 41 field,
>   gate theo cluster, môn ngoài cụm giữ 0.0.
> - ✅ GĐ4: `shared/mcq/english_features.py` — `EnglishMCQFeatures` 26
>   feature, nhánh riêng trong `tools/demo_mcq.py` cho cụm linguistic.
> - Dữ liệu: 669 câu Sử crawl cũ đã vào `subjects/history/samples/
>   mcq_crawled.json` kèm nhãn LLM 4 mức (chờ giáo viên kiểm định);
>   train đầu tiên: accuracy 61.8% (Easy F1 0.75, Hard F1 0.12 — thiếu mẫu
>   Hard). Crawler VietJack đang chạy bổ sung.

## Bối cảnh

Pipeline 33-feature (`shared/mcq/features.py` + `jaccard.py` + `rsi.py` +
`ontology_bridge.py`) được xây ban đầu **chỉ cho Lịch sử**, sau đó dùng lại
cho 6 môn còn lại qua `SubjectConfig`/registry (`shared/subjects.py`) — Lịch
sử khai báo `entity_classes`/`edge_props` tường minh, 6 môn kia tự động dò
(`owl:Class`/`owl:ObjectProperty` trong namespace).

Sau khi soạn `mcq_samples.json` cho cả 7 môn và chạy thử pipeline, phát hiện
**pipeline không "trung lập" giữa các môn như tưởng** — nó mang nhiều giả
định ngầm định hình theo dữ liệu Lịch sử (Event/weightsJson/prerequisiteOf...)
mà không phải môn nào cũng có. Hai khảo sát đọc-code sâu (không sửa gì) đã
xác nhận cụ thể mức độ lệch này — xem tóm tắt bên dưới.

**Quyết định của người dùng** (đã chốt, không xét lại trong kế hoạch này):
1. Thiết kế lại theo **từng cụm môn**, chấp nhận số lượng/ý nghĩa feature
   khác nhau giữa các môn, ưu tiên độ chính xác hơn khả năng so sánh chéo
   bằng đúng 33 con số.
2. Môn Anh: thêm **bộ feature ngôn ngữ học riêng** thay cho phần KG-entity đã
   chết về cấu trúc, thay vì viết lại câu hỏi cho khớp entity.
3. Môn Sử: **vẫn hoãn** như `docs/DEFERRED.md` đã chốt — kế hoạch này không
   đụng tới dữ liệu/feature của Sử, không được làm đổi số liệu đã có.

## Phát hiện nền tảng (từ 2 khảo sát đọc-code)

### Feature nào phụ thuộc gì (trên tổng 33 feature)

| Nhóm | Số feature | Ghi chú |
|---|---|---|
| Cần entity-match thành công | 22 | `extract_entities_from_text` khớp cụm từ chính xác (đã bỏ dấu), không có fallback mờ |
| + cần `weightsJson` | 2 (`jaccard_kg_max/mean`) | Chỉ Sử có (`emit_dynamic_entity`), 0 nơi khác |
| + cần `abstractness`/`bloomLevel` | 2 (`kg_abstractness_mean`, `kg_bloom_level_mean`) | Độ phủ chênh lệch rất lớn giữa các môn (0%–100%) |
| + cần đúng cạnh `prerequisiteOf` (hardcode string, `ontology_bridge.py:257`) | 2 | Văn **không có cạnh này** → luôn = 0 |
| Chỉ dùng text (bền với thiếu entity) | 10 | `rsi_to_correct`, `kad_entropy_stem/correct`, 6 `emb_*` |

Hai lỗi kỹ thuật đáng chú ý, độc lập với việc redesign theo cụm:
- `kad_path_distance_mean` (`features.py:341-360`) được ghi chú là "Block B,
  text-only" nhưng thực ra **cần entity-match** (`if correct_entities:`),
  fallback về hằng số trung tính `0.5` khi thiếu — tài liệu sai so với code.
- `rsi_dc` (`rsi.py:121-151`): khi không có entity distractor nào, trả về
  `0.0` một cách im lặng → công thức RSI đọc thành "(1-DC)=1.0" = "distractor
  phân biệt tối đa" — một giá trị mặc định trông giống tín hiệu thật, làm
  lệch `rsi_correct` theo hướng "dễ hơn" đúng lúc dữ liệu entity kém nhất.

### 5 cụm môn (theo hình dạng đồ thị + kiểu đáp án MCQ)

| Cụm | Môn | Đặc điểm |
|---|---|---|
| A | **Sử** | Baseline, **ngoài phạm vi** — cạnh causal/temporal thật, có `weightsJson`, đáp án hỗn hợp (cụm từ/số/mệnh đề) |
| B | **Hóa, Địa** | Đáp án là cụm từ entity, đồ thị giàu quan hệ domain-specific (`reactant/product`, `locatedIn/causes`), alias/annotation khá tốt — pipeline hiện tại đã ổn |
| C | **Toán, Lý** | Đáp án là cụm từ entity nhưng đôi khi là **giá trị số thuần** ("660W", "40°") không khớp entity nào; đồ thị gần như chỉ có `prerequisiteOf`; alias rất thưa (15%/9%) |
| D | **Văn** | Đáp án là cụm từ entity, nhưng **không có cạnh `prerequisiteOf` nào** (đồ thị dạng cây thuộc-tính: tác giả↔tác phẩm↔giai đoạn↔thể loại↔nhân vật↔biện pháp↔chủ đề) → 2 feature prereq-depth vô nghĩa về cấu trúc |
| E | **Anh** | Đáp án là **câu tiếng Anh hoàn chỉnh**, không phải cụm từ trùng nhãn entity → 22/33 feature về gần 0 một cách cấu trúc, không phải do câu hỏi soạn kém |

## Kiến trúc đề xuất

### 1. Mở rộng `SubjectConfig` (`shared/subjects.py`)

```python
@dataclass(frozen=True)
class SubjectConfig:
    name: str
    namespace: str
    prefix: str
    entity_classes: Tuple[str, ...] = ()
    edge_props: Tuple[str, ...] = ()
    cluster: str = "generic"                    # MỚI
    prereq_edge: Optional[str] = "prerequisiteOf"  # MỚI — None = môn không có khái niệm DAG tiên quyết
```

- `history`: `cluster="history"`, `prereq_edge="prerequisiteOf"` — **giữ mặc
  định y hệt hiện tại**, không đổi hành vi.
- `chemistry`, `geography`: `cluster="dense_relational"`.
- `math`, `physics`: `cluster="prereq_dag"`.
- `literature`: `cluster="attributive_tree"`, `prereq_edge=None`.
- `english`: `cluster="linguistic"` — nhánh pipeline riêng hoàn toàn (mục 4).

### 2. Gỡ hardcode `"prerequisiteOf"` (`ontology_bridge.py:254-271`)

`_precompute_metrics` đọc `self.config.prereq_edge` (mặc định
`"prerequisiteOf"` khi `config=None`, tức Sử không đổi gì) thay vì literal
string cứng. Với Văn (`prereq_edge=None`), `features.py` nhận biết điều này
và **thay** 2 feature prereq-depth bằng feature khác (mục 3) thay vì âm thầm
trả về 0 trông giống tín hiệu thật.

### 3. Feature theo từng cụm — cộng thêm, không phá vỡ 33 feature gốc

- **Cụm B (Hóa, Địa)**: giữ nguyên 33 feature. Không cần đổi kiến trúc.
- **Cụm C (Toán, Lý)**: giữ nguyên 33 feature + thêm khối phát hiện **đáp án
  số** (regex nhận diện giá trị số/đơn vị, VD `^-?\d+(\.\d+)?\s*(°|W|V|Ω|m)?$`):
  - `numeric_answer_present`
  - `numeric_magnitude_gap_min` (đáp án đúng gần distractor gần nhất bao nhiêu — càng gần càng khó)
  - `numeric_unit_match` (distractor có cùng đơn vị không — cùng đơn vị dễ gây nhầm hơn)
  - `numeric_distractor_plausibility` (distractor có phải "sai lệch theo mẫu thường gặp", VD lệch x2/x10, không)
  → 33 + 4 = 37 feature cho Toán/Lý.
- **Cụm D (Văn)**: bỏ 2 slot prereq-depth chết, thay bằng 3 feature dựa
  trên cạnh thật của môn này (`authoredBy`, `writtenIn`/`activeIn`,
  `expresses`/`uses`):
  - `kg_same_author_correct_distractor`
  - `kg_same_period_correct_distractor`
  - `kg_shared_theme_device_jaccard`
  → 31 + 3 = 34 feature cho Văn.
- **Cụm B mở rộng (tuỳ chọn, ưu tiên thấp, Phase 3 sau)**: thêm Jaccard theo
  cạnh có kiểu (VD `jaccard_reactant_product` cho Hóa, `jaccard_located_causes`
  cho Địa) để không gộp mọi loại cạnh vào 1 metric khoảng cách vô hướng như
  hiện tại — cải thiện chất lượng tín hiệu, không bắt buộc để chạy được.

### 4. Cụm E (Anh) — module riêng `shared/mcq/english_features.py`

Dataclass `EnglishMCQFeatures` mới, tái dùng tối đa hạ tầng có sẵn (không
thêm dependency nặng — chỉ dùng `re`/`difflib` có sẵn trong Python):

- **Khối stem-KG** (entity link ở *stem* vẫn hoạt động tốt — tái dùng
  `engine.extract_entities_from_text(stem)`):
  `stem_entity_matched`, `stem_entity_bloom_level`, `stem_entity_abstractness`,
  `stem_entity_cefr_level` (chỉ GrammarStructure, verify tên property đúng
  trong `subjects/english/build_data.py` trước khi code).
- **Khối độ phức tạp ngôn ngữ** (đo trên `correct`/`distractors`, thuần
  regex/đếm từ, không cần model): số từ, độ dài ký tự, số mệnh đề (đếm
  quan hệ từ/liên từ phụ thuộc: who/which/that/because/if/when/although...),
  bậc phức tạp thì động từ (0=hiện tại đơn → 4=quá khứ hoàn thành/điều kiện
  loại 3), theo đúng các `GrammarStructure` thực có trong ontology.
- **Khối độ "giống nhau gây nhiễu"**: edit-distance (`difflib.SequenceMatcher`,
  có sẵn trong Python, không thêm dependency) giữa đáp án đúng và từng
  distractor — distractor gần đúng-nhưng-sai theo kiểu "goes/go/is going/went"
  là tín hiệu khó rất mạnh và rẻ để tính; tái dùng `_tokenize`/term-overlap
  đã có trong `rsi.py` (đã hỗ trợ ký tự Latin nên chạy được trên tiếng Anh).
- **Khối text-only tái dùng nguyên bản** (gọi thẳng hàm đã có, không viết lại):
  `kad_entropy_stem/correct` (`engine.knowledge_entropy`), 6 `emb_*`
  (`_compute_embedding_features` trong `features.py`). Lưu ý PhoBERT là model
  tiếng Việt — embedding cho văn bản tiếng Anh vẫn chạy được nhưng chất lượng
  ngữ nghĩa không đảm bảo; chấp nhận dùng tạm (rẻ, đã có sẵn), không đề xuất
  thêm model tiếng Anh riêng trong kế hoạch này.

Tổng ước tính: ~24 feature (4 stem-KG + 8 phức tạp ngôn ngữ + 4 nhiễu +
2 KAD + 6 embedding), không cần khớp đúng 33.

Kiểm chứng: chạy trên 10 câu mẫu Anh đã có, xác nhận thủ công feature biến
thiên hợp lý theo nhãn khó/dễ (VD câu điều kiện loại 2/3, mệnh đề quan hệ nên
có `tense_complexity` cao + `edit_distance` thấp hơn câu thì hiện tại đơn).

### 5. Sửa lỗi chung — chỉ thêm, không đổi giá trị feature đã có

Thay vì sửa trực tiếp `kad_path_distance_mean`/`rsi_dc` (đổi giá trị, có thể
ảnh hưởng số liệu Sử), thêm 1 feature phụ **mới, cộng thêm**, cho mọi môn:

- `entity_match_coverage`: tỉ lệ đáp án (đúng + distractors) khớp được ≥1
  entity. Cho phép người đọc phân biệt "0.0 vì thật sự không gây nhầm" với
  "0.0 vì thiếu dữ liệu entity" — sửa vấn đề diễn giải mà **không đổi bất kỳ
  giá trị nào trong 33 feature gốc của bất kỳ môn nào, kể cả Sử**.

Việc đổi thẳng công thức fallback của `kad_path_distance_mean`/`rsi_dc` (theo
hướng NaN/đánh dấu-thiếu như `docs/DEFERRED.md` Nhóm B đã gợi ý) vẫn để hoãn
chung với các mục Sử, vì đổi fallback là đổi giá trị cho **mọi** môn dùng
pipeline chung, kể cả Sử.

### 6. Việc dọn "thuộc tính khai báo nhưng không emit"

`_discover_classes`/`_discover_edge_props` (`ontology_bridge.py:151-169`)
hiện lấy mọi `owl:Class`/`owl:ObjectProperty` khai báo trong schema, kể cả
loại chưa từng có instance thật (`frequencyInTextbook` Lý/Toán, `bloomLevel`
Văn, `requiresVectorReasoning` Lý, vài object-property rác ở Hóa/Toán/Địa/Anh).
Thêm điều kiện lọc: chỉ giữ property/class có **ít nhất 1 instance thật**
trong graph. An toàn cho Sử (Sử dùng danh sách tường minh, không qua
auto-discovery).

## Kế hoạch triển khai theo giai đoạn

**Giai đoạn 1 — Dựng khung, KHÔNG đổi hành vi**
- Thêm field `cluster`/`prereq_edge` vào `SubjectConfig`, điền REGISTRY.
- Đổi `_precompute_metrics` đọc `config.prereq_edge` thay vì hardcode.
- Thêm lọc property/class rỗng-instance vào auto-discovery.
- Kiểm chứng: dump 33 feature-value cho toàn bộ câu mẫu của **cả 7 môn**
  trước/sau, diff byte-for-byte — kỳ vọng **không đổi gì** (kể cả 6 môn kia,
  vì bước này chỉ gỡ property chết chứ chưa thêm/bớt feature nào).

**Giai đoạn 2 — Thêm feature phụ trợ, vẫn không đổi giá trị cũ**
- Thêm `entity_match_coverage` cho mọi môn.
- Sửa docstring `kad_path_distance_mean` (chỉ tài liệu, không đổi số).
- Kiểm chứng: diff lại — chỉ có 1 cột mới xuất hiện, 33 giá trị cũ của mọi
  môn (kể cả Sử) vẫn y hệt.

**Giai đoạn 3 — Feature riêng theo cụm (làm độc lập từng cụm, review riêng)**
- 3a. Văn: hoán 2 slot prereq-depth chết → 3 feature attribution-cluster mới.
- 3b. Toán/Lý: thêm 4 feature nhận diện đáp án số.
- 3c. (tuỳ chọn) Hóa/Địa: thêm Jaccard theo cạnh có kiểu.
- Mỗi mục kiểm chứng riêng bằng `tools/demo_mcq.py --subject <môn>` +
  đọc thủ công phần XAI in ra, xác nhận feature mới không toàn số 0.

**Giai đoạn 4 — Pipeline riêng cho Anh**
- Viết `shared/mcq/english_features.py` + `EnglishMCQFeatures` theo mục 4.
- Nối `tools/demo_mcq.py`/`features.py` để môn Anh (`cluster="linguistic"`)
  đi qua nhánh riêng này thay vì `extract_single_mcq_features`.
- Kiểm chứng trên 10 câu mẫu đã có; phần in báo cáo XAI hiện tại có câu chữ
  cứng kiểu "Thực thể lịch sử..." — cần viết lại câu chữ cho phù hợp Anh,
  không tái dùng nguyên văn.

**Giai đoạn 5 — Đề xuất làm giàu dữ liệu (không thuộc phạm vi code)**
- Bổ sung `aliases` cho Toán (15%→?) và Lý (9%→?) — ưu tiên thấp, vì Giai
  đoạn 3b đã bù một phần tín hiệu qua feature số.

## Ràng buộc bắt buộc xuyên suốt

Sau **mọi** giai đoạn: 33 giá trị feature của môn Sử (chạy trên
`subjects/history/samples/mcq_samples.json`) phải **byte-identical** với
trước khi bắt đầu — dùng đúng phương pháp byte-diff đã áp dụng ở lần refactor
trước (xem `docs/HISTORY_MERGE.md`). Bất kỳ giai đoạn nào làm lệch dù chỉ 1
giá trị của Sử đều phải dừng lại và xem xét lại, không tiếp tục.

## Việc cần làm trước khi code (đã biết, chưa xác nhận)

- Tên property `cefrLevel` trong `subjects/english/build_data.py` cần đọc
  lại để chắc đúng, trước khi dùng trong `EnglishMCQFeatures`.
- Danh sách quan hệ từ/liên từ dùng cho `clause_count`/`tense_complexity`
  của tiếng Anh nên đối chiếu lại với đúng các `GrammarStructure` đang có
  trong ontology (không chỉ 10 câu mẫu) để không bỏ sót nhóm ngữ pháp nào.
