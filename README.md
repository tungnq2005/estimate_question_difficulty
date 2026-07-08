# NCKH — Ước lượng độ khó câu hỏi bằng Đồ thị Tri thức (Grade-9 QDE)

Xây dựng **đồ thị tri thức (ontology)** cho các môn lớp 9 và dùng chúng để **ước
lượng độ khó câu hỏi trắc nghiệm** trong điều kiện *cold-start* (chưa có dữ liệu
trả lời của học sinh). Mỗi câu hỏi được mã hoá thành **vector 33 đặc trưng**
(KG structure + Jaccard + RSI + KAD entropy + PhoBERT) làm đầu vào cho XGBoost
phân loại **Dễ / Trung bình / Khó** kèm giải thích (XAI).

Môn **Lịch sử (`history`)** là mảng hoàn chỉnh nhất; 6 môn còn lại dùng chung
đúng một bộ máy (engine).

---

## Cấu trúc thư mục

Ba "khối" (bucket) — nhìn là hiểu ngay đâu là *engine*, đâu là *dữ liệu*, đâu là *công cụ*:

```
.
├── shared/                  # 1) ENGINE — code dùng chung, subject-agnostic (import shared)
│   ├── ttl_builder.py       #    data (build_data.py) -> Turtle/OWL
│   ├── form_template.py     #    sinh form giáo viên kiểm định độ khó
│   ├── subjects.py          #    REGISTRY: cấu hình từng môn (namespace, lớp, cạnh)
│   └── mcq/                 #    Pipeline độ khó MCQ (33 features)
│       ├── ontology_bridge.py  #  OntologyEngine: TTL -> NetworkX graph + KAD
│       ├── jaccard.py          #  độ dễ nhầm giữa đáp án đúng và nhiễu
│       ├── rsi.py              #  mức câu dẫn "để lộ" đáp án
│       ├── features.py         #  gộp 33 features + train XGBoost
│       └── embedding_cache.py  #  PhoBERT (tuỳ chọn)
│
├── subjects/                # 2) DỮ LIỆU — mỗi môn 1 thư mục
│   ├── history/             #    môn chủ lực (trước đây là su9_ontology/)
│   │   ├── build.py         #      data/ -> ontology/su9.ttl (+.owl)
│   │   ├── data/            #      Chuong1..7 + global_entities (dict giàu thông tin)
│   │   ├── ontology/        #      su9.ttl (sinh ra)
│   │   ├── samples/         #      mcq_samples.json
│   │   └── legacy/          #      bản history cũ (319 thực thể) — LƯU TRỮ, xem docs/HISTORY_MERGE.md
│   ├── physics/ math/ chemistry/ english/ geography/ literature/
│   │                        #    mỗi môn: build.py + build_data.py + display_labels.py + ontology/
│
├── tools/                   # 3) CÔNG CỤ chạy trực tiếp
│   ├── build_all.py         #    build ontology cho cả 7 môn
│   ├── demo_mcq.py          #    demo pipeline độ khó (--subject)
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

# 4) Tra cứu tương tác đồ thị Lịch sử
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

- ✅ Ontology + pipeline độ khó của **Lịch sử** chạy đầy đủ (434 thực thể, 761 cạnh).
- ✅ 6 môn còn lại đã build được ontology và **nạp được vào engine** (qua auto-discovery).
- ⏳ Các mục nghiên cứu còn treo (thay đổi số liệu → cần duyệt): xem [docs/DEFERRED.md](docs/DEFERRED.md).
- 🔀 Vì sao gộp `history` từ hai bản cũ: xem [docs/HISTORY_MERGE.md](docs/HISTORY_MERGE.md).
- 📄 Báo cáo tiến độ: [docs/BAO_CAO_TIEN_DO_TUAN_2.md](docs/BAO_CAO_TIEN_DO_TUAN_2.md).
