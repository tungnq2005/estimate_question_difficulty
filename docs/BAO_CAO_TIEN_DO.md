# BÁO CÁO TIẾN ĐỘ NGHIÊN CỨU KHOA HỌC

**Tên đề tài:** Ước lượng độ khó câu hỏi trắc nghiệm Lịch sử 9 bằng Đồ thị Tri
thức (Knowledge Graph) và Học máy (XGBoost)

---

## 1. Tổng quan và Mục tiêu hệ thống

Hệ thống dự đoán độ khó câu hỏi trắc nghiệm khách quan (MCQ) môn Lịch sử lớp 9
theo hướng *a priori* (dự đoán trước khi triển khai kiểm tra), trong điều kiện
**cold-start** — không sử dụng dữ liệu phản hồi (response data) của học sinh, do
đó không áp dụng được các mô hình IRT (Item Response Theory) cổ điển vốn cần
tham số ước lượng từ log trả lời.

Bài toán được phát biểu dưới dạng **phân loại có giám sát 3 lớp** (Dễ / Trung
bình / Khó). Đầu vào là bộ ba `(stem, đáp án đúng, tập 3 đáp án nhiễu)`; đầu ra
là nhãn độ khó kèm **phân rã giải thích (XAI)** dựa trên đóng góp của từng thành
phần đặc trưng.

Kiến trúc gồm 3 pha: (1) mã hóa tri thức thành Đồ thị tri thức RDF/OWL; (2)
trích xuất vector đặc trưng từ đồ thị, entropy thông tin và embedding ngữ nghĩa;
(3) huấn luyện XGBoost và sinh giải thích.

---

## 2. Kết quả đạt được

### 2.1. Pha 1 — Xây dựng Ontology Lịch sử 9

Tri thức chương trình GDPT 2018 (Chương 1: Thế giới 1918–1945; Chương 2: Việt
Nam 1918–1945) được mã hóa thủ công thành đồ thị RDF, tuần tự hóa dưới định dạng
**Turtle (`.ttl`) + OWL**, nạp bằng `rdflib` và chuyển sang `networkx.DiGraph`
để tính toán các độ đo cấu trúc.

**Chỉ số đồ thị (đo bằng `tools/stats.py`):**

| Chỉ số | Giá trị |
|---|---|
| Số đỉnh (thực thể) | 434 |
| Số cạnh (quan hệ) | 761 |
| Đường kính (diameter, đồ thị vô hướng hóa) | 12 |
| Số cặp đường đi ngắn nhất đã tiền tính (all-pairs BFS) | 168.946 |

**Lược đồ (schema) — 8 lớp thực thể:** Event (84), Location (79), Concept (76),
Organization (76), Period (45), Document (35), Person (24), Movement (15).

**12 kiểu quan hệ có thể hiện (instance):** `hasOrganization` (136), `occursAt`
(134), `occursDuring` (127), `involvedConcept` (88), `locatedIn` (76),
`prerequisiteOf` (70), `contrastsWith` (62), `hasPerson` (45), `similarTo` (8),
`leads` (7), `directCause` (4), `deepCause` (4).

**Chú giải (annotation) cấp thực thể phục vụ tính đặc trưng:** `abstractness`
(298 thực thể, thang liên tục), `bloomLevel` (74), `frequencyInTextbook` (174),
`aliases` (623 bí danh — phục vụ liên kết thực thể), `weightsJson` (113 trọng số
cạnh có hướng), thông tin năm (45).

### 2.2. Pha 2 — Trích xuất đặc trưng

Mỗi MCQ được ánh xạ thành **vector 34 chiều** (cấu hình cụm `history`), chia 3
khối. Bước tiền xử lý chung là **liên kết thực thể (entity linking)**:
`extract_entities_from_text` quét văn bản, so khớp theo nhãn/bí danh với ưu tiên
**cụm khớp dài nhất** (longest-match, khóa sắp xếp `(-len, text)`), trả về tập
thực thể cho stem, đáp án đúng và từng đáp án nhiễu.

**Khối A — Đặc trưng đồ thị tri thức (24 chiều):**

- *A1 — Cấu trúc (8):* số thực thể ở đáp án đúng/nhiễu; `entity_diversity` (số
  thực thể phân biệt / tổng); `abstractness_mean`, `bloom_level_mean` (trung
  bình annotation của thực thể chạm tới); độ sâu tiên quyết trung bình trên DAG
  `prerequisiteOf` cho đáp án đúng và nhiễu; `centrality_mean` (degree
  centrality trung bình).
- *A2 — Jaccard 3 cấp (8):* đo mức trùng lặp đáp án đúng ↔ từng đáp án nhiễu.
  - **Hard:** `|E_c ∩ E_d| / |E_c ∪ E_d|` trên tập URI thực thể.
  - **Soft:** `avg_{e_c} max_{e_d} 1/(1 + d(e_c, e_d))`, với `d` là độ dài đường
    đi ngắn nhất trên đồ thị, ngưỡng cắt `d ≤ 3`.
  - **KG-weighted:** `0.5·[URI trùng] + 0.3·(w/10) + 0.2·1/(1+|Δabstractness|)`,
    trong đó `w = max` trọng số `weightsJson` hai chiều.
  - Cùng hai đặc trưng stem↔đáp-án-đúng và stem↔đáp-án-nhiễu (max).
- *A3 — RSI, Relation Strength Indicativeness (8):* lượng hóa mức "chỉ dẫn" của
  stem tới đáp án qua 4 thành phần — Term Overlap (TO), Entity Overlap (EO),
  Semantic Closeness (SC = `avg max 1/(1+d)`), Distractor Confusion (DC = tương
  đồng trung bình giữa các cặp đáp án nhiễu). Điểm tổng hợp:

  ```
  RSI_correct    = 0.25·TO + 0.35·EO + 0.25·SC + 0.15·(1 − DC)
  RSI_distractor = 0.25·TO + 0.35·EO + 0.25·SC
  RSI_final      = RSI_correct − max_i RSI_distractor_i
  ```

  `RSI_final` cao ⇒ stem chỉ dẫn rõ tới đáp án đúng (dễ); gần 0 hoặc âm ⇒ stem
  mơ hồ, dẫn nhầm sang đáp án nhiễu (khó).

**Khối B — KAD, Knowledge-Augmented Difficulty (3 chiều):** entropy Shannon của
văn bản trên không gian thực thể,

```
H(text) = −Σ_i P(e_i | text)·log P(e_i | text),
P(e_i | text) = softmax( cos(v_text, v_{e_i}) / τ ),  τ = 0.1
```

với `v` là embedding PhoBERT. `H → 0` khi văn bản hội tụ về một thực thể (câu
hẹp, dễ); `H → log(434) ≈ 6.07` khi trải đều (câu rộng, khó). Bổ sung đặc trưng
khoảng cách đường đi trung bình đáp-án-đúng ↔ đáp-án-nhiễu trên đồ thị.

**Khối C — Semantic Embedding (6 chiều):** dùng **PhoBERT (`vinai/phobert-base`,
~135M tham số)** sinh embedding câu, tính cosine similarity stem↔đáp án (mean /
max / min / std trên tập đáp án nhiễu, và stem↔đáp-án-đúng). Đặc trưng phái
sinh `discriminative_power = sim(stem, đúng) − mean sim(stem, nhiễu)`.

**Đặc trưng meta (1 chiều):** `entity_match_coverage` = tỉ lệ phương án khớp
được ≥1 thực thể, để phân biệt giá trị 0 do "không có nhầm lẫn thực sự" với 0 do
"liên kết thực thể thất bại" — dùng đánh giá độ tin cậy của Khối A theo từng câu.

**Hai xử lý kỹ thuật của pipeline:**

1. **Kích hoạt hoàn toàn Khối B/C.** PhoBERT chạy trên CPU, embedding thực thể
   được cache ra `su9.embeddings.pkl` (431 vector) và tái sử dụng giữa các lần
   chạy. Trong mô hình cuối, 3 đặc trưng cosine của Khối C nằm nhóm đầu về độ
   quan trọng (xem 2.4).
2. **Tính tất định (determinism).** Phiên bản trước phụ thuộc thứ tự duyệt của
   `set`/`dict`/`rdflib` — vốn thay đổi theo `PYTHONHASHSEED` từng tiến trình —
   khiến hai lần chạy cùng mã lệch tới 57 giá trị đặc trưng của Khối A (do 38
   khóa nhãn chuẩn hóa bị ≥2 thực thể tranh chấp). Đã chuẩn hóa: duyệt theo thứ
   tự sắp xếp, tie-break tất định (nhãn chính ưu tiên hơn bí danh; cùng hạng lấy
   URI nhỏ nhất theo từ điển; cạnh trùng cặp `(s,o)` giữ property lớn nhất). Sau
   sửa, hai lần chạy độc lập cho kết quả **trùng khớp từng bit**, trong khi bảo
   toàn cấu trúc 434 đỉnh / 761 cạnh / đường kính 12.

### 2.3. Xây dựng tập dữ liệu huấn luyện

**Nguồn và tiền xử lý.** Tập gồm **3.152 MCQ** đúng cấu trúc (stem + 4 phương án
+ đáp án đúng + lời giải): 669 câu tái lập từ dữ liệu crawl cũ (parse bằng regex,
khử trùng lặp theo khóa `chuẩn-hóa(stem) + đáp-án đã-sắp-xếp`) và 2.483 câu thu
thập bổ sung từ họ nguồn VietJack (SGK cũ + 3 bộ KNTT/CTST/CD), có giới hạn tốc
độ (≥1.5s/request).

**Gán nhãn theo đồng thuận 3 phiếu (3-vote consensus).** Thang nhãn gốc là 4 mức
chuẩn ma trận đề Việt Nam (Nhận biết / Thông hiểu / Vận dụng / Vận dụng cao),
ánh xạ về 3 lớp (NB→Dễ, TH→Trung bình, VD+VDC→Khó). Quy trình:

- **2 giám khảo LLM độc lập** chấm **mù** trên bản dữ liệu đã loại bỏ toàn bộ
  nhãn (tránh hiệu ứng mồi — anchoring), mỗi giám khảo dùng một *persona* và
  rubric khác nhau; nhãn LLM sẵn có được dùng làm phiếu thứ ba.
- **Luật hợp nhất:** đa số ≥2/3 quyết định nhãn; trường hợp 3 phiếu phân kỳ hoàn
  toàn, lấy **hạng trung vị** trên thang có thứ tự và đặt cờ `needs_review`.
- **Đồng bộ hóa trùng lặp:** các câu trùng khớp `(stem + 4 phương án)` được ép
  về cùng một nhãn (đa số trong nhóm).

**Chỉ số kiểm định độ tin cậy nhãn (định lượng):**

| Chỉ số | Giá trị |
|---|---|
| Đồng thuận tuyệt đối 2 giám khảo mù, thang 4 mức | 0,898 |
| Đồng thuận trong khoảng ±1 mức (adjacent) | 1,000 |
| Đồng thuận 2 giám khảo, quy về 3 lớp | 0,910 |
| 3 phiếu nhất trí hoàn toàn | 79,2% (2.497 câu) |
| 3 phiếu đa số 2/3 | 20,3% (641 câu) |
| 3 phiếu phân kỳ hoàn toàn → `needs_review` | 0,4% (14 câu) |

Đồng thuận adjacent = 1,000 cho thấy không có cặp chấm nào lệch quá 1 mức — tín
hiệu nhất quán của rubric. Số câu hỏi có nội dung trùng nhưng nhãn mâu thuẫn
giảm từ **106 xuống 6** sau hợp nhất; tổng **124 câu** mang cờ `needs_review`
(gồm 14 câu phân kỳ và các câu bị đảo nhãn khi đồng bộ trùng lặp), được ưu tiên
cho giáo viên kiểm định. Toàn bộ nhãn gắn `label_source="llm_vote3"`.

**Phân bố nhãn cuối:** Nhận biết 1.234 · Thông hiểu 1.399 · Vận dụng 433 · Vận
dụng cao 86 → 3 lớp: Dễ 1.234 / Trung bình 1.399 / Khó 519.

### 2.4. Pha 3 — Huấn luyện và đánh giá mô hình

**Cấu hình.** Bộ phân loại **XGBoost** (`objective="multi:softmax"`), siêu tham
số: `n_estimators=600, max_depth=6, learning_rate=0.05, subsample=0.8,
colsample_bytree=0.8, min_child_weight=2`. Do phân bố lớp lệch (lớp Khó chiếm
16,4%), áp **trọng số mẫu cân bằng** `w_c = N / (K·N_c)`. Đánh giá bằng **kiểm
định chéo phân tầng 5-fold (StratifiedKFold)** thay cho một lần tách hold-out để
giảm phương sai ước lượng.

**⚠️ Cập nhật quan trọng (rà soát 08/2026) — con số accuracy ban đầu KHÔNG còn
hiệu lực.** Kiểm tra lại bộ 3.152 câu bằng khoá nội dung (`tools/dedup.py`)
phát hiện chỉ có **2.147 nội dung câu hỏi khác nhau** — **54,7%** số câu là
bản sao do crawl trùng nhiều trang mirror cùng một ngân hàng gốc. Vòng CV
5-fold ban đầu chia ngẫu nhiên theo *câu*, nên bản sao của cùng một câu rơi
vào cả tập train lẫn test → mô hình học thuộc lòng thay vì học quy luật, mọi
chỉ số bị thổi phồng. Sau khi khử trùng lặp (mỗi nội dung giữ đúng 1 bản đại
diện) và đánh giá lại bằng đúng phương pháp cũ (5-fold CV, cùng seed):

| Mô hình | Accuracy (còn rò rỉ) | Accuracy (đã khử trùng lặp) |
|---|---|---|
| XGBoost 41 đặc trưng (đầy đủ) | 0,756 | **0,616** |
| Chỉ đặc trưng tri thức (KG+KAD) | 0,747 | **0,559** |
| TF-IDF + Logistic (chỉ văn bản, đối chứng) | 0,822 | **0,699** |

Hai điểm cần báo cáo trung thực:

1. **Baseline TF-IDF thuần văn bản đang vượt toàn bộ pipeline tri thức**
   (0,699 so với 0,616) sau khi loại rò rỉ — pipeline KG hiện tại **chưa
   chứng minh được giá trị gia tăng** so với một baseline rẻ hơn nhiều.
2. **Cụm từ mà TF-IDF dựa vào để phân biệt các lớp là khuôn mẫu câu hỏi,
   không phải nội dung tri thức**: "quốc gia nào"/"nước nào"/"năm" → Dễ;
   "nguyên nhân"/"không phải là" → Trung bình; "điểm tương đồng"/"so với"/
   "điểm khác biệt" → Khó. Đây là dấu hiệu cho thấy nhãn 3-phiếu LLM đang
   mã hoá phần nào **dạng câu hỏi** thay vì **độ khó nội dung thật** — cùng
   hướng với phát hiện độc lập của Acquaye et al. (arXiv:2601.09953, 2026):
   LLM chấm trực tiếp độ khó là phương pháp kém tin cậy.

**Hệ quả cho thiết kế nghiên cứu:** mọi đánh giá từ nay bắt buộc dùng tập đã
khử trùng lặp hoặc GroupKFold theo `dup_group` (đã cập nhật `tools/train.py`,
`tools/attic/ablation.py` mặc định theo hướng này); và cần một nguồn nhãn **độc lập
với LLM** để đối chứng — đây là lý do nhóm triển khai khảo sát học sinh + xác
nhận của giáo viên thứ hai (mục 3).

**Số liệu kèm theo (đo trên tập đã khử trùng lặp, vẫn còn nguyên giá trị
tham khảo):**
- Xếp hạng tầm quan trọng đặc trưng (theo gain, top-4 của khối tri thức):
  `emb_stem_distractor_mean_sim`, `entity_match_coverage`, `rsi_max_distractor`,
  `kg_bloom_level_mean` — tín hiệu ngữ nghĩa (Khối C) và đồ thị tri thức
  (Khối A) đều có đóng góp, nhưng chưa đủ để vượt baseline văn bản thuần.
- Chỉ số kiểm định độ tin cậy nhãn (bảng ở 2.3) — đồng thuận 3-phiếu vẫn có
  giá trị làm sạch dữ liệu (giảm mâu thuẫn nhãn 106 → 6 câu); vấn đề rò rỉ
  và nhãn bề mặt là hai vấn đề khác, không phủ định việc làm sạch này.

### 2.5. Giải thích được (XAI)

Điểm `RSI_final` được phân rã tường minh thành 4 thành phần (TO/EO/SC/DC), mỗi
thành phần kèm diễn giải định lượng và ngưỡng phán định (`RSI_final > 0.3`: Dễ;
`0–0.3`: Trung bình; `< 0`: Khó), cùng gợi ý chỉnh sửa câu hỏi (ví dụ: bổ sung
từ khóa đặc trưng vào stem, tách biệt ngữ nghĩa các đáp án nhiễu).

### 2.6. Kiến trúc đa môn (tổng quát hóa engine)

Pipeline được tham số hóa theo **5 cụm môn** dựa trên hình thái đồ thị và kiểu
đáp án, dùng chung một engine cho 7 môn: `history` (baseline) · `dense_relational`
(Hóa, Địa) · `prereq_dag` (Toán, Lý — thêm 4 đặc trưng cho đáp án dạng số: tỉ số
sai hệ số kinh điển, dấu vết đảo tử–mẫu, cùng họ công thức) · `attributive_tree`
(Văn — thêm 3 đặc trưng đồng tác giả/giai đoạn/chủ đề) · `linguistic` (Anh — 26
đặc trưng ngôn ngữ học riêng: độ phức tạp thì động từ, số mệnh đề, khoảng cách
biên tập đáp án). Bộ đặc trưng đầy đủ 41 trường, tự bật/tắt theo `config.cluster`,
không làm thay đổi 34 đặc trưng của cấu hình `history`.

---

## 3. Kế hoạch nghiên cứu tiếp theo

Ưu tiên đổi từ "nâng accuracy" sang "có nhãn tham chiếu đáng tin cậy để biết
accuracy hiện tại có ý nghĩa hay không" — hệ quả trực tiếp của phát hiện ở 2.4.

- **Nhãn tham chiếu độc lập (đang triển khai):** khảo sát trên lớp học thật +
  xác nhận của một giáo viên thứ hai, làm nguồn đối chứng cho nhãn 3-phiếu
  LLM. Đây là điều kiện tiên quyết trước khi công bố bất kỳ con số accuracy
  nào là kết luận chính của đề tài.
- **PhoBERT fine-tune làm baseline bắt buộc:** *fine-tune* toàn bộ tham số
  trên chuỗi `stem [SEP] đáp án` (không chỉ dùng embedding đông lạnh), đánh
  giá bằng **out-of-fold prediction** trên đúng 5-fold đã dùng cho ablation
  (`tools/attic/colab_finetune_phobert.py`, chạy trên Google Colab — xem giải thích
  bên dưới) để so sánh công bằng, không rò rỉ. Nếu PhoBERT fine-tune cũng vượt
  pipeline KG như TF-IDF đã vượt, đây là bằng chứng cần **thiết kế lại** cách
  đặc trưng tri thức được đưa vào mô hình, không chỉ là vấn đề thiếu dữ liệu.
- **Stacking:** đưa xác suất posterior của PhoBERT fine-tune làm đặc trưng bổ
  sung cho XGBoost–KG (`tools/attic/ablation.py --oof-phobert`), kiểm tra tri thức
  có cộng thêm được gì so với PhoBERT dùng riêng hay không — đây là câu hỏi
  nghiên cứu thật, thay vì mục tiêu chạm một ngưỡng accuracy định trước.
- **Kiểm định của giáo viên:** ưu tiên 124 câu `needs_review` và lớp Khó; cập
  nhật `label_source="teacher"` cho các câu đã xác nhận, đo lại độ đồng thuận
  người–LLM (Cohen's κ).
- **Mở rộng tri thức:** bổ sung đồ thị Chương 3 (Việt Nam 1945–1975) và các bài
  còn để trống (Bài 21–22, Chương 6–7).
- **Kích hoạt các annotation còn thiếu:** phát `abstractness`/`bloomLevel`/
  `frequencyInTextbook` cho đủ Event để làm sống 3 đặc trưng `curr_pos_*` hiện
  còn hằng 0 (chi tiết tại `docs/DEFERRED.md`).
