# NCKH — Lớp giải thích tự kiểm chứng cho độ khó câu hỏi trắc nghiệm

> ### 👉 Mới vào? Đọc [docs/TONG_QUAN.md](docs/TONG_QUAN.md)
> Một file: bối cảnh · kỹ thuật dùng và vì sao · tác động · kết quả.
> Bản đồ tài liệu: [docs/README.md](docs/README.md) · bản đồ công cụ:
> [tools/README.md](tools/README.md)

Đề tài **không** ước lượng độ khó — nó **giải thích** dự đoán độ khó, và tự
chứng minh lời giải thích đó đáng tin tới đâu.

Lý do: ước lượng độ khó cần ground truth là **tỉ lệ học sinh trả lời đúng**, mà
xin phép tổ chức làm bài tại trường không được duyệt, và đề tài **không dùng mẫu
người thật**. Bài toán *giải thích* thì không cần: đối tượng được giải thích là
**dự đoán của mô hình**, và lời giải thích được chứng minh bằng **can thiệp** —
sửa đúng một phương án nhiễu rồi xem dự đoán có dịch không — chứ không bằng việc
khớp với phán đoán của ai.

Nhãn là **mức nhận thức NB/TH/VD/VDC do giáo viên gán theo ma trận đề**, không
phải độ khó thực nghiệm. Ranh giới này phải giữ trong mọi phát biểu.

Hai mảng dữ liệu, cùng một bộ máy: **Vật lí 9** (1 539 câu) và **Lịch sử 9**
(1 276 câu). Lớp giải thích chạy được trên **bốn mô hình nền** khác nhau, mỗi mô
hình có bảng mốc riêng — cả bốn đều tái lập `khớp 72 · lệch 0`.

---

## Cấu trúc thư mục

Ba "khối" (bucket) — nhìn là hiểu ngay đâu là *engine*, đâu là *dữ liệu*, đâu là *công cụ*:

```
.
├── shared/                  # 1) ENGINE — code dùng chung, subject-agnostic (import shared)
│   ├── ttl_builder.py       #    data (build_data.py) -> Turtle/OWL
│   ├── form_template.py     #    sinh form giáo viên: thẩm định ontology + chấm độ khó MCQ
│   ├── subjects.py          #    REGISTRY: cấu hình từng môn (namespace, lớp, cạnh, CỤM)
│   └── mcq/                 #    Pipeline độ khó MCQ (cluster-aware, xem docs/PIPELINE_REDESIGN_PLAN.md)
│       ├── ontology_bridge.py     #  OntologyEngine: TTL -> NetworkX graph + KAD (tất định)
│       ├── jaccard.py             #  độ dễ nhầm giữa đáp án đúng và nhiễu
│       ├── rsi.py                 #  mức câu dẫn "để lộ" đáp án
│       ├── features.py            #  gộp features (41 field, gate theo cụm) + train XGBoost
│       ├── numeric_features.py    #  cụm Toán/Lý: đáp án số (hệ số trượt tay, đảo tử-mẫu)
│       ├── literature_features.py #  cụm Văn: cùng tác giả/giai đoạn/chủ đề
│       ├── english_features.py    #  cụm Anh: 26 feature ngôn ngữ học riêng
│       └── embedding_cache.py     #  PhoBERT (tuỳ chọn)
│
├── subjects/                # 2) DỮ LIỆU — mỗi môn 1 thư mục
│   ├── history/             #    môn chủ lực (trước đây là su9_ontology/)
│   │   ├── build.py         #      data/ -> ontology/su9.ttl (+.owl)
│   │   ├── data/            #      Chuong1..7 + global_entities (dict giàu thông tin)
│   │   ├── ontology/        #      su9.ttl (sinh ra)
│   │   ├── samples/         #      mcq_samples.json (10 câu demo)
│   │   │                    #      + mcq_crawled.json (3.152 câu vietjack, nhãn LLM 4 mức)
│   │   └── legacy/          #      bản history cũ (319 thực thể) — LƯU TRỮ, xem docs/HISTORY_MERGE.md
│   ├── physics/ math/ chemistry/ english/ geography/ literature/
│   │                        #    mỗi môn: build.py + build_data.py + display_labels.py
│   │                        #    + ontology/ + samples/mcq_samples.json (10 câu/môn)
│
├── tools/                   # 3) CÔNG CỤ chạy trực tiếp
│   ├── build_all.py         #    build ontology cho cả 7 môn
│   ├── demo_mcq.py          #    demo pipeline độ khó (--subject; Anh đi nhánh riêng)
│   ├── train.py             #    train XGBoost độ khó (--subject, gộp mọi nguồn samples có nhãn)
│   ├── counterfactual_validity.py  # kiểm lời giải thích bằng can thiệp tối thiểu (--subject physics|history)
│   ├── ontology_resolution.py      # thang độ phân giải ontology: làm thô / PhoBERT / phân tầng
│   ├── ablate_full.py              # ablation với khối KG đầy đủ (thay ablate_physics.py)
│   ├── teacher_vs_llm_labels.py    # ghép cặp nhãn người vs nhãn máy (--subject both)
│   ├── perf_headroom.py            # headroom + kiểm rò rỉ bản sao (--leak)
│   ├── reproduce_all.py            # ĐÓNG GÓI TÁI LẬP: --list/--run/--check/--freeze, 72 số × 2 mô hình nền
│   ├── text_backend.py             # MÔ HÌNH NỀN THỨ HAI: PhoBERT đóng băng + 15 cột (QDE_BACKEND=text)
│   ├── text_vs_rules.py            # luật tay hay biểu diễn học được là chỗ nghẽn: 4 mô hình × 2 lát cắt
│   ├── backend_diff.py             # 72 số, hai bảng mốc: cái nào giữ, cái nào đổi, cái nào đổi dấu
│   ├── backend_curve.py            # BỐN mô hình nền × 14 chỉ số: lời giải thích chịu được bao nhiêu độ mờ
│   ├── pick_c_tfidf.py             # chọn C cho mô hình nền TF-IDF MỘT LẦN trên nhãn thật, rồi đóng đinh
│   ├── xai_difficulty.py           # XAI 5 bước DẪN BẰNG CAN THIỆP (chứng chỉ trục → can thiệp từng câu → đối chứng ghép cặp → phát ngôn)
│   ├── xai_sanity.py               # kiểm tra tỉnh táo cổng chứng chỉ: 39 mô hình NHÃN XÁO + đổi seed
│   ├── explain_difficulty.py       # XAI chẩn đoán (bản cũ, dẫn bằng SHAP): rã trục + hiệu chỉnh + điểm mù
│   ├── label_reliability.py        # độ tin của nhãn LLM khi không có người chấm thứ hai (test-retest)
│   ├── natural_raters.py           # độ tin của nhãn GIÁO VIÊN: câu trùng = người chấm tự nhiên, máy vs người
│   ├── crawl/               #    crawl_kenhgiaovien.py --subject physics|history (nhãn GV)
│   │                        #    + parse_legacy_su.py, crawler VietJack
│   ├── link_history_labels.py      # ghép nhãn GV (kenhgiaovien) + đáp án (vietjack)
│   ├── llm_answer_key.py           # sinh đáp án + KIỂM CHỨNG MÙ (--subject, --validate)
│   ├── label_source_axes.py        # trục nào là của độ khó, trục nào của người gán nhãn
│   ├── two_axis_feasibility.py     # hai trục có khả thi với asset đang có không
│   ├── operation_axis.py           # trục thao tác: đồ thị tiên quyết + vết giải
│   ├── llm_solution_trace.py       # LLM sinh VẾT GIẢI → đặc trưng (không phải nhãn)
│   ├── llm_judge_labels.py         # LLM chấm NB/TH/VD/VDC làm đường cơ sở (--subject)
│   ├── incremental_value.py        # "sao không hỏi thẳng LLM?" — mô hình lồng nhau
│   ├── axis_evidence.py            # DỰ BÁO → GIẢI THÍCH: 3 cửa bác bỏ cho TỪNG trục
│   ├── stats.py             #    thống kê ontology 1 môn
│   └── view.py              #    tra cứu tương tác đồ thị Lịch sử (CLI)
│
├── docs/                    # báo cáo + ghi chú thiết kế
├── pyproject.toml           # cài đặt gói `shared` (pip install -e .)
├── requirements.txt         # thư viện lõi
└── requirements-ml.txt      # torch + transformers (tuỳ chọn, cho Block B/C)
```

---

## Cài đặt

Yêu cầu Python 3.9+ (khuyến nghị 3.12).

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate     |  Linux/macOS:  source .venv/bin/activate

pip install -e .                 # cài thư viện lõi + gói `shared` (bỏ mọi sys.path hack)

# (tuỳ chọn) Block B (KAD entropy) + Block C (PhoBERT embedding):
pip install -r requirements-ml.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

> Không có `torch`, pipeline vẫn chạy — 9 features của Block B/C tự về `0.0`.

---

## Sử dụng nhanh

```bash
# 1) Build ontology cho tất cả các môn (sinh subjects/<môn>/ontology/*.ttl + *.owl)
python tools/build_all.py

# 2) Thống kê một ontology
python tools/stats.py history          # hoặc: physics, math, chemistry, ...

# 3) Demo pipeline độ khó MCQ (in báo cáo XAI cho từng câu)
python tools/demo_mcq.py --subject history

# 4) Train XGBoost phân loại Dễ/Trung bình/Khó (dùng mọi câu có nhãn của môn)
python tools/train.py --subject history

# 5) Tra cứu tương tác đồ thị Lịch sử
python tools/view.py
```

Dùng engine trong code:

```python
from shared.mcq.ontology_bridge import OntologyEngine

engine = OntologyEngine.for_subject("history")   # hoặc "physics", ...
print(len(engine), "thực thể,", engine.nx_graph.number_of_edges(), "cạnh")
```

---

## Thêm nội dung mới

- **Thêm chương/bài cho Lịch sử:** tạo file `subjects/history/data/ChuongX/....py`
  (list `EVENTS`/`DOCUMENTS`/`MOVEMENTS` dạng dict), rồi `python subjects/history/build.py`.
  `build.py` tự quét (`glob`) toàn bộ `data/`.
- **Thêm dữ liệu cho môn khác:** sửa `subjects/<môn>/build_data.py`, rồi `python subjects/<môn>/build.py`.
- **Thêm một môn hoàn toàn mới:** tạo `subjects/<môn>/{build.py, build_data.py}`, và đăng ký
  trong `shared/subjects.py` (`REGISTRY`). Engine MCQ sẽ dùng lại được ngay khi có `samples/mcq_samples.json`.

---

## Trạng thái & bước tiếp theo

- ✅ Ontology + pipeline độ khó của **Lịch sử** chạy đầy đủ (nay 480 thực thể, 937 cạnh).
- ✅ 6 môn còn lại đã build ontology, có 10 câu MCQ mẫu/môn, **nạp được vào engine**.
- ✅ Pipeline **tất định** (2 lần chạy cho kết quả giống hệt) và **phân biệt theo cụm môn**:
  Sử (baseline) / Hóa+Địa (dense_relational) / Toán+Lý (prereq_dag, +4 feature số) /
  Văn (attributive_tree, +3 feature thuộc tính) / Anh (linguistic, 26 feature riêng)
  — thiết kế: [docs/PIPELINE_REDESIGN_PLAN.md](docs/PIPELINE_REDESIGN_PLAN.md).
- ✅ **3.152 câu MCQ Sử thật** (669 phục hồi từ nhánh git cũ + 2.483 crawl mới
  từ họ VietJack) + nhãn độ khó 4 mức bằng **voting 3 phiếu LLM độc lập**
  (2 giám khảo chấm mù + nhãn gốc), `label_source="llm_vote3"`, 124 câu gắn
  `needs_review` — **chờ giáo viên kiểm định**.
- ⚠️ **Đã phát hiện & xử lý rò rỉ dữ liệu:** bộ crawl chứa **54,7% bản sao**
  (3.162 câu → chỉ **2.147 nội dung khác nhau**). Bản sao rơi vào cả train lẫn
  test khiến mô hình thuộc lòng và chỉ số bị thổi phồng ~14 điểm. Đã đánh dấu
  `dup_group`/`is_canonical` (`tools/dedup.py`); `train.py` mặc định chỉ dùng
  bản canonical. **Mọi số liệu cũ (75,6%) không còn hiệu lực.**
- 📊 Kết quả trung thực (2.147 câu, 5-fold CV) — xem `tools/attic/ablation.py`:

  | Mô hình | Accuracy | macro-F1 | QWK |
  |---|---|---|---|
  | TF-IDF + Logistic (chỉ văn bản) | **69,9%** | 0,67 | 0,62 |
  | XGBoost 41 đặc trưng (đầy đủ) | 61,6% | 0,53 | 0,43 |
  | Chỉ đặc trưng tri thức (KG+KAD) | 55,9% | 0,48 | 0,33 |

- ⚠️ **Vấn đề nghiên cứu đang mở:** baseline văn bản đơn giản đang **vượt**
  pipeline tri thức, và các cụm từ quyết định nhãn là **khuôn mẫu câu hỏi**
  ("quốc gia nào" → Dễ, "điểm tương đồng/so với" → Khó) ⇒ nhãn LLM nhiều khả
  năng mã hoá *kiểu câu hỏi* hơn là *độ khó thật* (khớp phát hiện của Acquaye
  et al. 2026). Đang tiến hành **khảo sát trên lớp thật + giáo viên kiểm định**
  để có nhãn tham chiếu. Chi tiết: [docs/RELATED_WORK.md](docs/RELATED_WORK.md).
- 🧪 **Hiệu lực phản thực — HAI MÔN (09/2026)** — `tools/counterfactual_validity.py`.
  Cách kiểm lời giải thích **không cần người thật** (thay user study đang bị chặn):
  thay đúng 1 phương án nhiễu bằng nhiễu thật của câu khác, xem dự đoán có dịch
  chuyển đúng hướng lời giải thích đã hứa không. Chạy trên **Lý** (1.539 câu,
  nhãn giáo viên) và **Sử** (2.137 câu canonical, nhãn `llm_vote3`) — cùng thang
  NB/TH/VD/VDC nên so trực tiếp được.

  | can thiệp | Vật Lí | Lịch Sử |
  |---|---|---|
  | trục **bề mặt** (đối chứng dương) | −0,180 · p = 3e−28 | −0,115 · p = 2e−129 |
  | `kg_near` "nhiễu gần hơn → khó hơn" | **43,9% đúng hướng** | **45,0% đúng hướng** |
  | `kg_far` so đối chứng khớp | p = 0,65 | p = 0,76 |
  | hop có kiểm soát 14 biến | +0,013 (**ngược dấu**) | −0,001 (**p = 0,35**) |

  Đối chứng dương ăn rất mạnh ở cả hai môn ⇒ phép đo dùng được. Dưới phép đo đó,
  **giả thuyết gốc (Vinu 2015) bị bác ở cả hai miền**: `kg_near` đúng hướng
  **dưới mức ngẫu nhiên** ở cả hai; `jaccard_kg_max` ở Lý còn mang **dấu âm**
  (−0,205 — nhiễu càng dễ nhầm thì câu càng DỄ).

  ⚠️ **Sửa lỗi quan trọng:** bản đầu dùng khối KG của `ablate_physics.py`, vốn
  **thiếu** `kad_path_distance_mean`, `jaccard_kg_*`, `rsi_dc` — đúng ba đại
  lượng vận hành hoá giả thuyết. Đã bổ sung và sinh lại toàn bộ số liệu.
  Chi tiết: [docs/COUNTERFACTUAL_VALIDITY.md](docs/COUNTERFACTUAL_VALIDITY.md).

- 🔁 **Không có đặc trưng bề mặt phổ quát** — phát hiện chỉ thấy được nhờ thiết
  kế 1 môn tự nhiên + 1 môn xã hội. Mọi đại lượng có tín hiệu đều **đảo dấu**
  giữa hai môn (Spearman với nhãn 4 mức):

  | đại lượng | Vật Lí | Lịch Sử |
  |---|---:|---:|
  | độ dài đáp án đúng | **−0,292** | **+0,520** |
  | độ dài nhiễu (TB) | **−0,278** | **+0,536** |
  | số lựa chọn chứa số | **+0,470** | −0,007 |
  | `kg_centrality_mean` | **−0,306** | **+0,237** |
  | `kad_path_distance_mean` | +0,056 | −0,043 |

  Ở Sử phương án dài = mệnh đề phức = khó; ở Lý phương án dài = câu chữ khái
  niệm (câu tái hiện), còn câu khó là đáp án số ngắn. ⇒ mô hình độ khó huấn
  luyện trên một môn áp sang môn kia sẽ sai **có hệ thống**.

- 📊 **Ablation với khối KG ĐẦY ĐỦ** — `tools/ablate_full.py` (thay
  `ablate_physics.py`). Luận điểm cũ *"KG thêm ~0 giá trị biên"* **không đúng**:

  | bộ đặc trưng (QWK) | Vật Lí | Lịch Sử |
  |---|---:|---:|
  | bề mặt | 0,371 | 0,409 |
  | KG lõi giả thuyết (path dist + jaccard + rsi_dc) | **0,272** | **0,141** |
  | KG đầy đủ (10 cột) | 0,337 | 0,193 |
  | bề mặt + KG đầy đủ | **0,407** | **0,426** |
  | ⇒ giá trị biên của ontology | **+0,036** | **+0,017** |

  Ontology **có** đóng góp thật, nhưng **lát "lõi giả thuyết" là lát YẾU NHẤT**
  của khối KG ở cả hai môn. Giá trị đến từ **độ phủ / vị trí khái niệm**, không
  phải từ **độ dễ nhầm giữa các phương án**.

- 🔬 **Giả thuyết "ontology còn thô" KHÔNG được ủng hộ (09/2026)** —
  `tools/ontology_resolution.py`. Thang độ phân giải 2 môn × 5 mức, trải độ tách
  phương án **9,7% → 100%**: hệ số hop luôn |≤ 0,0098|, **đổi dấu giữa hai môn**,
  không đơn điệu. Môn có ontology tách tốt gấp 3 (Sử 42,7% so với Lý 15,7%) lại
  cho hệ số **nhỏ hơn**. Phân tầng lặp lại được trên cả hai môn (z = +1,72 và
  +1,83, gộp Stouffer ≈ +2,51) nhưng **từng phép đều không có ý nghĩa** — luận
  điểm đứng ở chỗ *dấu lặp lại trên hai miền*, không phải ở độ mạnh từng phép.
  ⇒ Nút thắt **không nằm ở độ phân giải**; không nên đầu tư dựng ontology mịn
  hơn để cứu ước lượng độ khó.
  Chi tiết: [docs/ONTOLOGY_RESOLUTION.md](docs/ONTOLOGY_RESOLUTION.md).
- 🧾 **Nhãn NGƯỜI vs nhãn MÁY, ghép cặp trên hai môn (09/2026)** —
  `tools/teacher_vs_llm_labels.py`. Cùng một câu, cùng một đặc trưng, hai nguồn nhãn.

  | | Lịch Sử | Vật Lí (n=1.539) |
  |---|---:|---:|
  | κ người ↔ máy | +0,013 (n=90) · **+0,256** (n=225, §1.8) | **+0,284** |
  | trục bề mặt chủ đạo: ρ NGƯỜI / MÁY | **+0,23 / +0,57** (chênh p<0,001) | +0,46 / +0,62 (p<0,001) |
  | mô hình học nhãn máy → đo trên nhãn NGƯỜI | **κ −0,006** | **κ +0,155** |

  ⭐ **LLM là bộ KHUẾCH ĐẠI trục bề mặt ở cả hai môn** — Lý: |ρ| lớn hơn ở
  **15/15** đặc trưng; Sử: dựa vào trục hành văn **gấp ~2,4 lần** người. Bất đồng
  dồn vào **tầng CAO**: trong 28 câu giáo viên Sử gán VD/VDC, LLM chỉ gán VD/VDC
  cho **2 câu (7,1%)**, **18 câu bị hạ thẳng xuống NB** — bản Sử của điểm mù VDC
  ở Lý (recall 11%), nhưng là **đảo ngược** chứ không chỉ bỏ sót.
  Mọi con số Sử vẫn phải đọc là *"tái tạo nhãn LLM"*.

- 🎯 **NGUỒN NHÃN GIÁO VIÊN CHO MÔN SỬ — 1.279 câu (09/2026)** —
  `tools/crawl/crawl_kenhgiaovien.py --subject history` + `tools/link_history_labels.py`.
  Tìm được `kenhgiaovien.com/tai-lieu/trac-nghiem-lich-su-9`: **34 bài**, mỗi bài
  chia sẵn 4 phần NB/TH/VD/VDC do **giáo viên soạn theo ma trận đề** — đúng loại
  nguồn đã cứu môn Lý, độc lập hoàn toàn với đề tài.

  | | |
  |---|---|
  | crawl | **1.339 câu**, 0 bài lỗi |
  | khử trùng | **1.279** nội dung khác nhau (chỉ **4,5%** trùng — so với 54,7% ở bộ vietjack) |
  | phân bố | NB 521 · TH 590 · VD 81 · VDC 87 |
  | đáp án | **1.279/1.279 câu canonical** (211 người + 1.068 LLM sinh) |
  | dùng được | **1.276** (3 câu bị loại: trang nguồn in trùng phương án) |

  ⇒ Vị thế môn Sử đổi hẳn: từ **90 câu** nhãn người lên **1.276 câu** nhãn người,
  không phải xin phép ai. Nhãn độ khó là **của giáo viên**; chỉ mỗi đáp án là do
  LLM sinh — và phần sinh đó đã được **đo**, không phải tin.

- ✅ **Đáp án do LLM sinh, có đo độ chính xác (09/2026)** —
  `tools/llm_answer_key.py --subject history`. Trang kenhgiaovien không đăng đáp
  án. Khác bản làm cho môn Lý (sinh rồi tin), lần này có **tập kiểm chứng mù**:
  211 câu đã ghép được đáp án NGƯỜI từ vietjack, chấm mù trước khi tiêu lượt gọi
  cho hơn 1.000 câu kia.

  Chống thiên lệch vị trí: mỗi lượt **xáo phương án tất định** theo hash id, chạy
  **2 lượt xáo khác nhau**; hai lượt lệch nhau ⇒ cờ `answer_agree=false`.

  | trên 211 câu đáp án NGƯỜI | n | chính xác |
  |---|---:|---:|
  | lượt 0 · lượt 1 | 211 | **87,7% · 89,6%** |
  | hai lượt **KHỚP** | 192 (91,0%) | **92,7%** |
  | hai lượt **LỆCH** | 19 | 36,8% (≈ mức đoán mò 25%) |

  Cờ `answer_agree` **tự khai báo** câu đáng ngờ: khi hai lượt lệch, độ chính xác
  rơi về gần mức ngẫu nhiên. Trên bộ sinh thật, 85/1.079 câu (7,9%) bị gắn cờ —
  và **không lệch theo mức độ** (χ² = 6,72, p = 0,082), nên loại chúng không làm
  thiên lệch phân bố nhãn.

  ⚠️ Khi báo cáo phải nói rõ: "gold" ở đây là đáp án vietjack — cũng là đáp án
  người đăng trên mạng, không phải chuẩn tuyệt đối. **87,7% là cận dưới.**

- 🧹 **Một lỗi ghép dữ liệu đã sửa** — bản ghép đầu chép nguyên `correct` **và**
  `distractors` của vietjack sang câu kenhgiaovien. Nhưng câu dẫn trùng **không**
  bảo đảm bộ phương án trùng: 184 câu khớp đúng, 27 khớp mờ, **25 câu lệch hẳn**
  (hai đề khác nhau tình cờ trùng câu dẫn). 25 câu đó đang mang phương án của
  *một đề khác* với đề mà giáo viên đã gán nhãn — mọi đặc trưng nhiễu loạn
  (`len_dist_mean`, `jaccard_kg_*`, `kad_path_distance_mean`) tính trên chúng đều
  vô nghĩa. Đã gỡ và soi lại toàn bộ về đúng bộ phương án gốc.

- 🧭 **TRỤC THAO TÁC — giải được ở môn tự nhiên, không giải được ở môn xã hội (09/2026)** —
  [docs/OPERATION_AXIS.md](docs/OPERATION_AXIS.md). Lí thuyết hai trục (tri thức ×
  thao tác) chỉ có dụng cụ cho trục thứ nhất; thứ đóng vai trục thao tác thực chất
  là **độ dài văn bản**. Dựng dụng cụ thật rồi đo:

  | | cạnh **tiên quyết** | thao tác·chiều sâu KG |
  |---|---:|---:|
  | Sử (`su9.ttl`) | **0** | QWK 0,000 · **AUC 0,495** |
  | Lý (`phys9.ttl`) | **216** | QWK 0,262 · AUC 0,696 |

  Không phải ý tưởng sai — **đồ thị Sử không chứa loại cạnh đó**. Cạnh Sử mã hoá
  "cái gì liên quan cái gì"; cạnh `prerequisiteOf` của Lý mã hoá "phải biết Y trước
  mới tới X" — đúng ngữ nghĩa trục thao tác cần. Kiểm cả trên riêng 496 câu Sử nối
  được: vẫn AUC ≈ 0,50, và dấu **ngược** trực giác.

- 🔬 **Vết giải do LLM sinh — làm ĐẶC TRƯNG, không làm nhãn** — `tools/llm_solution_trace.py`.
  LLM **đáng tin ở việc giải** (đo được 87,7%) nhưng **không đáng tin ở việc phán độ
  khó** (κ 0,256; tầng cao 7,1%). Nên hỏi nó *tiến trình giải* — mấy bước, công thức
  nào, mấy ẩn — rồi lấy đó làm cột. Nó cũng liên kết được thực thể `Formula` mà khớp
  chuỗi chỉ nhận ra ở **1/1539 câu**. 77 lượt gọi, 0 lỗi.

  ⚠️ **Đã sửa một phát biểu quá lời**: chú giải `applicationSteps` của ontology
  **không** trả công như từng viết — ρ với số bước LLM tự đếm là **+0,928**, tức gần
  như bản sao; thêm vào chỉ được AUC +0,004. Chỗ ontology trả công thật là **đồ thị
  tiên quyết** (xem mục kế).

  ⚠️ Đã loại `tr_op_type` khỏi mọi cấu hình sạch: một mình nó đạt QWK 0,492 so với
  0,540 của bộ chấm độ khó trực tiếp — tức **nhãn LLM trá hình**.

- 🔭 **TỪ DỰ BÁO SANG GIẢI THÍCH — ba cửa mà một LLM không qua được (09/2026)** —
  `tools/axis_evidence.py`. Đây mới là chỗ đề tài là **XAI**, không phải một
  bộ dự báo khác. Dự báo thì LLM cũng làm được; điều LLM **không** làm được là
  chịu ba phép bác bỏ sau. Môn Lý, 53 bài, nhãn giáo viên:

  **Cửa 1 — khử trục tri thức bằng THIẾT KẾ** (chỉ so câu trong cùng một bài):
  `tr_steps` β **+0,641**, t **+21,5**; và hệ số *trong bài* **lớn hơn** *giữa bài*
  (0,641 vs 0,330) ⇒ không phải bí danh của "chủ đề khó".

  **Cửa 2 — thiết kế phải giết được yếu tố ta biết là sai.** Cặp cùng bài:

  | | tỉ lệ thắng | p |
  |---|---:|---:|
  | `tr_steps` | **90,5%** | ≈ 0 |
  | `kad_path_distance_mean` ⟨Vinu⟩ | **41,6%** | 9,3e−9 (**ngược dấu**) |
  | XÁO ngẫu nhiên ⟨placebo⟩ | 50,7% | 0,27 (đúng: **không** qua) |

  **Cửa 3 — can thiệp TRÊN MANIFOLD** (3.198 cặp cùng bài, ghép khối của câu ít
  bước vào câu nhiều bước, so với chênh nhãn thật):

  | khối hoán đổi | phần khoảng cách nhãn giải thích được |
  |---|---:|
  | toàn bộ đặc trưng (mốc trên) | **89%** |
  | **trục thao tác** | **22%** |
  | `kad_path_distance_mean` ⟨đối chứng⟩ | **1%** |

  Ba số, ba ý: mô hình **hiệu chỉnh tốt ở mức từng câu** (89%); trục thao tác có
  **tỉ trọng đo được bằng đơn vị độ khó** (22%); và mô hình **không bịa** hiệu ứng
  cho yếu tố đã bị bác bỏ (1%) — điều SHAP không bảo đảm, vì SHAP luôn chia hết
  100% kể cả cho cột vô nghĩa.

  ⇒ Đề tài **không** hơn LLM ở con số dự báo (QWK 0,531 vs 0,540). Nó hơn ở chỗ
  **mọi phát biểu đều đứng trước một phép bác bỏ** — và một phát biểu đã thật sự
  bị bác bỏ ba lần bằng ba thiết kế độc lập (giả thuyết Vinu).

- ⚖️ **TRỤC TRI THỨC ĐỔI DẤU THEO MÔN — `tools/axis_evidence.py`** (09/2026).
  Áp đúng ba cửa trên cho trục tri thức, nhóm đối sánh chặt hơn (Lý: ô **bài ×
  số bước**, 128 ô — khống chế CẢ chủ đề LẪN tải thao tác):

  | `kg_centrality_mean` | ρ trong nhóm | cặp ghép | giải thích được |
  |---|---:|---:|---:|
  | **Sử** | **+0,201** (t +2,87) | **66,1%** (p 2e−96) | **62,5%** |
  | **Lý** | −0,067 (t **−3,22**) | **44,7%** (p 6e−10) | — |

  Sử: khái niệm càng ở vùng liên kết dày ⇒ càng **khó**. Lý: càng trung tâm ⇒
  càng **DỄ** (ρ giữa bài **−0,75**) — định luật Ôm, công suất là nền móng hỏi ở
  tầng NB; câu VD/VDC là tình huống riêng lẻ chạm ít thực thể ngoại vi.

  ⇒ *"Vị trí trong đồ thị góp phần vào độ khó"* **đúng nhưng chưa đủ**: **chiều**
  của nó phụ thuộc môn. Một hệ dùng chung một dấu cho mọi môn sẽ sai ở một nửa
  số môn — và gộp hai môn lại tính tương quan sẽ che mất điều này.

  Đối chứng xáo ngẫu nhiên trượt đúng ở cả hai môn (50,7% / 48,5%). ⚠️ Nhưng đối
  chứng Vinu **không** trượt ở Sử (60,1%) — gần như chắc do chọn mẫu (chỉ tính
  được cho 517/1.276 câu), nên **không dùng cửa này ở Sử để tuyên bố bác bỏ**;
  ba bằng chứng bác bỏ khác vẫn đứng độc lập.

- 🧩 **ĐỒ THỊ TRI THỨC ĐÓNG GÓP CHÍNH XÁC BAO NHIÊU, Ở ĐÂU (Lý)** — tách 4 kênh mà
  "trục thao tác" từng gộp chung:

  | thêm vào nền *vết giải LLM* (AUC 0,713) | ΔAUC | ΔQWK |
  |---|---:|---:|
  | chú giải ontology ⟨`applicationSteps`⟩ | +0,004 | +0,012 |
  | **đồ thị tiên quyết** (216 cạnh) | **+0,049** (p 0,0000) | +0,001 (p **0,92**) |
  | — trong đó rút gọn được về *đếm thực thể* | +0,047 | |
  | — **phần topo không rút gọn được** | **+0,021** [+0,009, +0,035] | |

  Hai kết luận sắc hơn hẳn "ontology có đóng góp": **(1)** đồ thị giúp phân biệt
  *tầng cao hay không*, **không** giúp xếp đúng bốn mức (ΔQWK p = 0,92); **(2)** 43%
  cái tưởng là topo thật ra chỉ là đếm xem câu chạm bao nhiêu thực thể — phần thật sự
  cần đồ thị là **+0,021 AUC**, và đó mới là phần tỉ lệ thuận với chất lượng đồ thị.

  Và nó chạy **ngược** trực giác: `op_pre_need_new` (số tiên quyết đáp án đòi mà câu
  dẫn không cấp) trung bình NB **0,44** → VDC **0,06**, β trong bài **−0,181**
  (t −6,69). Câu VD/VDC môn Lý là *tình huống số liệu*, nhắc rất ít thực thể có tên.
  Nên đồ thị tiên quyết ở Lý **không đo chiều sâu suy luận** — nó là **bộ nhận dạng
  loại câu** (khái niệm vs tính toán). Đóng góp thật, tên gọi phải sửa.

- 🎯 **PHÉP QUYẾT ĐỊNH: "sao không hỏi thẳng LLM cho xong?"** — `tools/incremental_value.py`.
  Mô hình lồng nhau, chân lý = nhãn giáo viên, cả hai môn có nhãn LLM trên **đúng
  những câu đó**.

  | | Lý ΔQWK | Lý ΔAUC | Sử ΔQWK | Sử ΔAUC |
  |---|---|---|---|---|
  | ta thêm cho LLM | +0,021 (p 0,204) | **+0,075 (p 0,000)** | **+0,064 (p 0,029)** | **+0,088 (p 0,003)** |
  | LLM thêm cho ta | +0,030 (p 0,008) | +0,008 (p 0,033) | +0,020 (p 0,360) | +0,015 (p 0,127) |

  Đề tài **không cạnh tranh với LLM ở việc gán nhãn** — nó thắng ở **đúng chỗ LLM
  hỏng**: recall VDC ở Lý **11,0% → 31,1%**. Ở Sử bất đối xứng sạch: ta thêm được cho
  LLM, LLM không thêm được cho ta.

  Hai sản phẩm dùng được ngay, không cần dữ liệu học sinh:
  **(1)** cờ *"câu này LLM dễ chấm hụt"* — AUC **0,764** ở Lý;
  **(2)** danh sách ngắn nghi tầng cao — đưa 100 câu Lý thì **94 câu đúng** (nền 38,1%);
  Sử 31% trên nền 13,2%.

- 📐 **Khung bài báo — [docs/PAPER_SKELETON.md](docs/PAPER_SKELETON.md) (09/2026)**.
  Mọi tài liệu rời trong `docs/` được xếp vào đúng một chương; 12 bảng/hình buộc
  vào file JSON sinh ra chúng; và mục §5 liệt kê **ranh giới phát biểu** — những
  câu nghe xuôi tai nhưng dữ liệu không đỡ nổi, kèm cách nói đúng thay thế
  (ví dụ: không được viết *"SHAP không trung thực"*, phải viết *"SHAP không tự
  nói cho ta biết nó đang ở đâu trên thang đó"*). Bốn chỗ còn chặn được nêu tên,
  xếp theo mức chặn.

- 📈 **Headroom hiệu năng — đo trước khi đổi, và quyết định KHÔNG đổi (09/2026)**
  — `tools/perf_headroom.py`, [docs/PERF_HEADROOM.md](docs/PERF_HEADROOM.md).

  Phát hiện một chỗ lệch còn sót: nhãn NB/TH/VD/VDC là thang **có thứ tự** nhưng
  mô hình học nó như 4 lớp rời rạc, trong khi QWK phạt theo bình phương khoảng
  cách. Chữa bằng hồi quy + ngưỡng khớp phân vị (học từ lát huấn luyện, không
  nhìn nhãn kiểm) được **QWK +0,064 (Lý) / +0,051 (Sử)**.

  Nhưng **AUC tầng cao đi xuống**, ở môn Sử gần đúng bằng phần QWK thu được
  (−0,064). Không cấu hình nào thắng cả hai: hồi quy có thứ tự xếp 4 mức khớp
  hơn, multiclass tách tầng cao tốt hơn. Câu "dẫn bằng QWK hay AUC tầng cao"
  vì thế không còn là chuyện trình bày — nó quyết định luôn cấu hình mô hình.

  **Quyết định lúc đó: không đổi.** Đổi mô hình thì toàn bộ lớp giải thích phải
  chạy lại (mọi phép đo đều là phản ứng của *mô hình cụ thể đó*) và toàn bộ bảng
  số đóng băng phải làm lại, để lấy về một chỉ số mà khung XAI đã xếp xuống phụ lục.

  *(24/09/2026: cái giá đó cuối cùng đã trả — nhưng cho một lý do khác và lớn
  hơn nhiều, là khả năng thích nghi, không phải để đổi lấy vài điểm QWK. Xem mục
  cuối README và [docs/MODEL_UPGRADE.md](docs/MODEL_UPGRADE.md).)* Chỗ đáng
  cân nhắc là **cân trọng số lớp cho riêng môn Lý**: giữ nguyên kiến trúc
  multiclass, AUC gần như nguyên (0,765→0,767), mà **recall VDC tăng gần gấp ba**
  (0,187→0,534).

  **Kiểm rò rỉ bản sao — nghi ngờ KHÔNG đúng.** Bộ Lý không có `is_canonical`
  nên nghi các bản sao lọt cả hai phía. Kiểm ra: 101 nhóm trùng câu dẫn (14,4%
  số câu) nhưng chỉ **50/101 nhóm cùng nhãn** — nửa còn lại là câu khác nhau
  tình cờ chung câu dẫn. Buộc mọi bản sao vào cùng một lát chỉ đổi QWK **−0,009**.
  Số hiện tại đứng được; bộ lọc của môn Sử cũng sạch (0 nhóm còn sót).

- 🔎 **Khai thác lớp giải thích — một kết quả RỖNG và một kết quả DÙNG ĐƯỢC (09/2026)**
  — `xai_difficulty.py --selective | --recourse`, [XAI_PIPELINE.md §8b](docs/XAI_PIPELINE.md).

  Faithfulness và stability đã đo được. Hai trục còn lại của một hệ XAI —
  *plausibility* và *utility* — thường cần người. Mục này thử đo **utility** mà
  không cần người.

  **Thử 1 — lấy lời giải thích làm cơ chế TỪ CHỐI trả lời: KHÔNG ĐƯỢC.** Giữ lại
  20% câu "tự tin nhất": xếp theo entropy cho **45,0% (Lý)** / **83,3% (Sử)** độ
  chính xác; xếp theo sức giải thích cho **30,0%** / **53,3%**. Mẫu hình lặp lại
  ở một cấu hình độc lập (n=400, R=24). Trong 6 tầng entropy, không tầng nào có
  tương quan dương có ý nghĩa.

  Cơ chế đo được: ρ(sức giải thích, entropy) = **+0,293** (Lý) / **+0,175** (Sử),
  đều có ý nghĩa — sức giải thích đo khoảng cách tới ranh giới quyết định. Nhưng
  ρ(sức giải thích, |sai lệch|) **tách hai môn**: −0,009 n.s. ở Lý (**kết quả
  rỗng** — bản sao nhiễu của entropy, không thêm gì) so với **+0,138** p=0,017 ở
  Sử (**đi sai hướng thật** — giữ câu "giải thích được" là giữ câu mô hình sai
  nhiều hơn). Kết luận môn Sử dựa vào tương quan này chứ không dựa vào khoảng tin
  cậy của hiệu số độ chính xác, vì cái sau lật ý nghĩa giữa hai lần chạy.

  Điều này KHÔNG hạ thấp phần faithfulness (ρ +0,722/+0,733 vẫn đứng). Nó nói một
  điều hẹp: **sức giải thích không phải tín hiệu tự tin** — nên **đừng dựng
  selective prediction trên độ lớn quy kết**, cái rẻ hơn nhiều (entropy) làm tốt hơn.

  **Thử 2 — biến lời giải thích thành LỜI KHUYÊN SỬA ĐỀ: được.** Thay đúng một
  phương án nhiễu bằng nhiễu THẬT của câu khác: **33,6% (Lý) / 30,8% (Sử)** số câu (chỉ qua nhánh đạt chứng chỉ; trước khi chốt cổng theo nhánh: 51,2% / 33,6%)
  sửa được xuống mức thấp hơn bằng một thay đổi đơn lẻ. Cổng B1 áp cả ở đây —
  bản đầu tiên đề xuất sửa qua nhánh `kg_far`, tức khuyên sửa đề bằng chính trục
  đề tài đã bác; đã vá, và công cụ **khai báo số sửa đổi bị loại**.

- 📦 **Đóng gói tái lập — bảng số của báo cáo là một BÀI KIỂM TRA (09/2026)** —
  `tools/reproduce_all.py`, [docs/RESULTS_FROZEN.md](docs/RESULTS_FROZEN.md).
  **25 con số** được trích dẫn trong báo cáo bị buộc vào đường dẫn khoá cụ thể
  trong file cụ thể, kèm dung sai đặt theo *mức mà kết luận vẫn giữ nguyên* chứ
  không theo độ chính xác của máy. `--check` thoát mã 1 nếu có số lệch, nên cắm
  được vào CI.

  Điểm quan trọng khi trình bày: **13 bước được tách làm hai loại** — 3 bước cần
  LLM (đóng băng, không chạy lại, sinh ra *dữ liệu đầu vào* chứ không sinh ra kết
  luận) và 10 bước offline tất định (~48 phút, seed 42). Nghĩa là **không kết luận
  nào của đề tài phụ thuộc vào việc gọi lại mô hình ngôn ngữ** — hội đồng chạy 10
  bước offline là dựng lại được toàn bộ bảng số.

  Chạy lại thử `operation_axis` (131s) và `xai_coverage` (62s): **khớp tuyệt đối,
  lệch +0,0000** trên mọi số. XGBoost tất định với seed cố định trên máy này.

  Nhóm đối chứng cũng bị buộc (`kad_path_distance ⟨đối chứng⟩`, 0,85% ở Lý và
  1,8% ở Sử): nếu một ngày đối chứng đột nhiên lên cao thì thiết kế đã hỏng, và
  `--check` phải báo.

- 🧪 **XAI DẪN BẰNG CAN THIỆP, không dẫn bằng quy kết (09/2026)** —
  `tools/xai_difficulty.py`, [docs/XAI_PIPELINE.md](docs/XAI_PIPELINE.md).

  **Đây là mạch chính của đề tài.** Bài toán *dự đoán* độ khó cần ground truth là
  tỉ lệ trả lời đúng của học sinh thật — bị chặn vì T1 không duyệt, không lách
  được. Bài toán *giải thích* thì không: đối tượng được giải thích là dự đoán của
  mô hình, và lời giải thích được chứng minh bằng **can thiệp** chứ không bằng
  việc khớp với người, nên thí nghiệm phản thực thay được cho user study. Cái giá
  phải khai báo: ground truth không biến mất mà **đổi chỗ** — mô hình học nhãn
  *mức nhận thức theo ma trận đề*, nên lời giải thích nói về **"vì sao câu này
  được xếp mức cao trên thang NB/TH/VD/VDC"**, không phải "vì sao học sinh làm
  sai" (`XAI_PIPELINE.md` §0a, §9).

  Pipeline 5 bước: **chứng chỉ trục** (trục nào được phép nêu tên) → **can thiệp
  từng câu** (thay 1 nhiễu THẬT, lặp R lần) → **đối chứng ghép cặp** (cùng ô,
  cùng ràng buộc → sàn nhiễu riêng của câu) → **quy kết có kiểm chứng** →
  **phát ngôn** với quyền nói *KHÔNG QUY ĐƯỢC*.

  **Kiểm tra chéo là kết quả chính.** Chia R lần lặp thành hai nửa donor độc lập:
  ước lượng nửa A dự báo nửa B ở **rho +0,722** (Lý) / **+0,733** (Sử) — độ tin
  cậy của lời giải thích dùng đủ R lần lặp là **0,84 / 0,85** (Spearman–Brown).
  Quy kết SHAP dự báo cùng nửa B chỉ **+0,297** (Lý, đạt **35%** trần √ρ) và
  **−0,088 n.s.** (Sử, ≈ 0%); biến thể công bằng nhất — Shapley theo khối trên
  chính E[y] — còn thấp hơn (26% / 3%). Vấn đề không phải "SHAP sai" mà là
  **SHAP không tự nói cho ta biết nó đang ở đâu trên thang đó** — cùng công cụ,
  cùng loại mô hình, hai bộ dữ liệu, một lần khoảng một phần ba trần, một lần 0,
  nhìn từ ngoài trông y hệt nhau. *(Bản trước ghi 41% — tính với trần sai ρ thay
  vì √ρ, nghiêng có lợi cho SHAP.)*

  Cổng B1 chặn được đúng thứ cần chặn: trục TRI THỨC **trượt chứng chỉ ở cả hai
  môn** (Lý: `kg_near` p=0,044 nhưng **dấu ngược**; `kg_far` p=0,65 — Sử: 0,10 và
  0,95), nên không được nêu làm nguyên nhân ở bất kỳ câu nào. Trục BỀ MẶT đạt cả
  hai chiều ở cả hai môn *theo luật gốc*, làm đối chứng dương cho chính phép đo.

  ⚠️ **Kiểm tra tỉnh táo (09/2026, `tools/xai_sanity.py`):** chính luật cổng này
  cấp chứng chỉ cho **30/39** (Lý) và **27/39** (Sử) mô hình học trên **nhãn
  xáo** — nó không đủ làm cổng. Hiệu chỉnh bằng 39 mô hình nhãn xáo: chỉ chiều
  **bớt** (bớt số / rút ngắn phương án → xếp thấp đi) vượt mọi mô hình xáo, ở cả
  hai môn, cả 4 seed; chiều **thêm** thì không chắc. **Đã chốt cổng theo nhánh**
  (11/09/2026): lời giải thích chỉ được dùng Lý `num_down`, Sử `len_down` — cái
  giá là độ phủ Lý còn 39,2% số câu — `docs/XAI_PIPELINE.md` §2b.

  Ba giới hạn đã đo và ghi rõ: (a) **R=12 thiếu lực** — câu `kgv_0138` lật từ
  *KHÔNG QUY ĐƯỢC* (p=0,080) sang *QUY ĐƯỢC* (p=0,016) khi lên R=24, nên mặc định
  đã đổi thành 24; (b) **trục KG chỉ đo được ở 41,1% câu Lý / 46,5% câu Sử**, phần
  còn lại là *"chưa biết"* chứ không phải *"không có tác dụng"*, và công cụ in
  tách bạch hai trường hợp; (c) đối chứng phải khớp cả **vị trí ô**, không chỉ
  khớp thuộc tính — lỗi này đã có trong bản đầu và đã sửa.

- 🩺 **Hệ XAI chẩn đoán, không phải hệ gán nhãn** — `tools/attic/explain_difficulty.py`.
  Mỗi câu xuất 4 phần: **dự đoán** (kèm entropy, có quyền *"không kết luận"*) ·
  **rã trục** bề mặt / tri thức · **hiệu chỉnh** bằng hiệu lực can thiệp đã đo ·
  **điểm mù**. Mọi con số hiệu chỉnh đọc từ file kết quả thí nghiệm, không
  hard-code, nên sửa thí nghiệm thì lời giải thích tự đổi.

  Ví dụ `su9_vj_0191`: quy kết SHAP dành **54%** cho trục tri thức, nhưng bỏ cả
  trục đó chỉ đổi E[y] **+0,005** (trục bề mặt: +0,067) — và mục hiệu chỉnh in
  thẳng rằng can thiệp cho thấy trục tri thức không lay chuyển dự đoán theo
  hướng giả thuyết. Mục điểm mù tự đổi kết luận theo môn: Sử *"KHÔNG dùng thay
  phán đoán giáo viên"*, Lý *"dùng được như GỢI Ý, không thay thế"*.

  Đây là chỗ đề tài khác ba công trình đã chiếm ô "XGBoost + SHAP giải thích độ
  khó" (Mathematics 12(10):1455 · MAKE 8(5):137 · AI 7(7):249): **lời giải thích
  tự mang bằng chứng về độ tin của chính nó**. Chi tiết + một cạm bẫy đo lường
  đã ghi lại: [docs/XAI_DIAGNOSIS.md](docs/XAI_DIAGNOSIS.md).

- 🔍 **Không có giáo viên thứ hai — làm được gì (09/2026)** —
  `tools/label_reliability.py`. Bốn phép thay cho người chấm thứ hai:

  | phép | kết quả |
  |---|---|
  | phân xử bằng **p-value mô phỏng** (76 câu đủ 3 nguồn) | GV ρ −0,081 · LLM ρ +0,214 — **không phép nào có ý nghĩa** |
  | ⭐ **test-retest của LLM** trên 715 nhóm nội dung trùng | 2.145 cặp phiếu · đồng thuận 86,5% · **κ +0,786** |
  | kiểm toàn vẹn nhãn | câu đơn: **0/1.422 lỗi** · nhóm trùng: 95,5% giải thích bằng gộp-mức-nhóm, **32 nhóm chưa** |
  | nhãn GV có học được không (n=90) | κ −0,123 — nhưng **đối chứng** nhãn LLM cũng chỉ +0,034 ⇒ **phép không đủ lực** |

  ⭐ Điều thay được cho giáo viên thứ hai: **LLM là công cụ đo ổn định**
  (κ ≈ 0,79 khi chấm lại nội dung trùng), nên κ(GV, LLM) = +0,013 **không giải
  thích được bằng "LLM chấm bừa"** — hai nguồn lệch nhau **có hệ thống**.
  ⇒ Đứng được: *hai nguồn đo hai thứ khác nhau*. **Không** đứng được:
  *"pipeline Sử đo sai độ khó"*. Chi tiết: [docs/XAI_DIAGNOSIS.md](docs/XAI_DIAGNOSIS.md) §1.6.

- 🔁 **Đổi mô hình nền — lời giải thích chịu được bao nhiêu độ mờ (24/09/2026)**
  — `tools/text_backend.py`, `tools/text_vs_rules.py`, `tools/backend_curve.py`,
  [docs/MODEL_UPGRADE.md](docs/MODEL_UPGRADE.md),
  [docs/BACKEND_CURVE.md](docs/BACKEND_CURVE.md),
  [XAI_PIPELINE.md §10](docs/XAI_PIPELINE.md).

  Vấn đề: mô hình nền cũ (XGBoost trên 15 cột viết tay) **không thích nghi**.
  Đo trước khi sửa (`text_vs_rules.py`, 4 mô hình × 2 lát cắt × 3 seed): ngay cả
  TF-IDF cũng bỏ xa 15 cột viết tay, và đường cong học của 15 cột **phẳng ở Lý,
  đi xuống ở Sử** — thêm dữ liệu không cứu được. Chỗ nghẽn là **biểu diễn**,
  không phải lượng nhãn.

  Mô hình nền mới: **PhoBERT đóng băng (mean-pool 768) + 15 cột đó**, hồi quy
  logistic C=0,01, OOF 5 lát. Phương án **sắp theo chữ cái** nên mô hình không
  biết đáp án nào đúng ⇒ dữ liệu crawl thêm không kèm đáp án vẫn dùng được.
  Bật bằng `QDE_BACKEND=text`, ghi ra `*_pb.json` — **bảng 56 số cũ không bị đụng**.

  | | cũ | mới |
  |---|---:|---:|
  | QWK trên **bài chưa gặp** (Lý / Sử) | 0,375 / 0,138 | **0,551 / 0,362** |
  | máy–người trên **câu trùng** (Lý / Sử) | 0,091 / 0,003 | **0,409 / 0,347** |
  | *(để so: người–người)* | 0,391 / 0,355 | 0,391 / 0,355 |
  | cổng B1 luật CHẶT, Lý | trượt | **qua** (độ phủ 39,2% → 100%) |
  | cổng B1 luật CHẶT, Sử | qua | **trượt** |
  | quy kết dự báo can thiệp, Lý (ρ) | +0,297 | **−0,050** |

  **Rồi chạy thêm HAI mô hình nền nữa**, vì hai điểm thì nối đường nào cũng
  được. Bốn mô hình xếp theo **tỉ trọng quyết định nằm ngoài cột đặt tên được**:
  `xgb15` 0 % → `tfidf` ~50 % → `text` ~78–88 % → `emb` 100 % (ca giới hạn: không
  còn cột đặt tên được nào, nên quy kết **không định nghĩa được**, không phải
  bằng 0).

  | môn Lý | xgb15 | tfidf | text | emb |
  |---|---:|---:|---:|---:|
  | máy–người trên câu trùng | 0,091 | 0,336 | 0,409 | **0,472** |
  | **can thiệp: nửa A → nửa B** | +0,722 | +0,673 | +0,705 | +0,725 |
  | **quy kết TỪNG CỘT → nửa B** | **+0,297** | **+0,132** | **−0,050** | — |
  | **quy kết THEO KHỐI → nửa B** | +0,224 | **+0,329** | +0,036 | — |
  | ρ(sức giải thích, entropy) | +0,293 | +0,174 | −0,124 | −0,071 |

  Kết luận, và nó mạnh hơn hẳn bản hai-điểm: **độ phân giải của lời giải thích
  quyết định nó chịu được bao nhiêu độ mờ.** Quy kết **từng cột** rơi đơn điệu
  theo tỉ trọng; quy kết **theo khối** thì không, và đạt đỉnh ở mô hình nền giữa
  — cao hơn cả mô hình cũ. Lớp **can thiệp** giữ nguyên trên toàn dải ở miền cấu
  trúc. Và cơ chế từng bỏ ngỏ ở `XAI_PIPELINE.md` §8b.2 nay **đo được**: ρ(sức
  giải thích, entropy) giảm đơn điệu theo độ mờ và đổi dấu ở **cùng một chỗ ở cả
  hai môn**.

  **Kết luận âm về trục TRI THỨC lặp lại ở cả 8 ô** (4 mô hình nền × 2 môn), nên
  không còn bị phản biện bằng *"tại các bạn chọn XGBoost"*. Và có một ca suýt
  lọt đáng đưa vào bài: dưới `tfidf`, `kg_near` của Lý **qua luật chứng chỉ gốc**
  (Wilcoxon p = 0,022, đúng hướng) nhưng p hoán vị = 0,150 — nếu đề tài vẫn dùng
  luật cũ thì chỉ cần đổi mô hình nền là kết luận trung tâm đảo chiều.

  Phải đọc kèm, đây **không** phải đợt thay mô hình "mọi thứ đều tốt lên": lời
  khuyên **hạ mức** — thứ người soạn đề thật sự cần — rơi đơn điệu 33,6 → 24,8 →
  20,0 → 17,2 % ở Lý, tức nó chạy tốt nhất ở đúng mô hình nền chấm kém nhất.

  ```bash
  python tools/reproduce_all.py --check --backend tfidf  # cả 4 bảng: khớp 72 · lệch 0
  python tools/backend_curve.py                          # bảng bốn mô hình nền
  python tools/backend_diff.py                           # 41 số giữ nguyên, 31 đổi
  ```

- ⏳ Các mục nghiên cứu còn treo: xem [docs/DEFERRED.md](docs/DEFERRED.md).
- 🔀 Vì sao gộp `history` từ hai bản cũ: xem [docs/HISTORY_MERGE.md](docs/HISTORY_MERGE.md).
- 📄 Báo cáo tiến độ: [docs/BAO_CAO_TIEN_DO_TUAN_2.md](docs/BAO_CAO_TIEN_DO_TUAN_2.md).
