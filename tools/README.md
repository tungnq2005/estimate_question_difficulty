# Bản đồ công cụ

38 file. Mục này nói **file nào làm gì** và **file nào là đường ống chính**, để
không phải đọc 38 docstring mới biết bắt đầu từ đâu.

Nhánh đã dừng nằm ở `tools/attic/` kèm lý do từng file.

---

## 0. Bắt đầu từ đây

```bash
python tools/reproduce_all.py --list     # kế hoạch: 3 bước LLM + 15 bước offline
python tools/reproduce_all.py --check    # 72 con số có còn khớp mốc không
python tools/backend_curve.py            # bảng bốn mô hình nền — kết quả chính
```

---

## 1. Đường ống chính — lớp giải thích

Chạy theo đúng thứ tự này; bước sau đọc đầu ra bước trước.

| # | công cụ | làm gì |
|---|---|---|
| 1 | `counterfactual_validity.py` | **lõi.** Dựng đặc trưng, huấn luyện mô hình nền out-of-fold, sinh phản thực (sửa đúng 1 phương án), đo dự đoán dịch bao nhiêu so với nhánh đối chứng khớp. Mọi tool dưới đây import nó. |
| 2 | `xai_sanity.py` | **cổng tỉnh táo.** 39 mô hình học trên NHÃN XÁO + 4 seed thật → phân bố rỗng cho cổng chứng chỉ. **Phải chạy trước mọi bước XAI.** |
| 3 | `xai_difficulty.py` | 5 bước giải thích từng câu + `--validate` (kiểm tra chéo nửa A/nửa B), `--coverage`, `--selective`, `--recourse` |
| 4 | `_run_xai.py` | chạy một chế độ của (3) cho cả hai môn — gói cho `reproduce_all` |
| 5 | `natural_raters.py` | máy so với người trên **các cặp câu trùng** — thay cho người chấm thứ hai |

## 2. Mô hình nền — thứ ĐƯỢC giải thích

| công cụ | làm gì |
|---|---|
| `text_backend.py` | ba mô hình nền văn bản: `text` (PhoBERT đóng băng + 15 cột), `tfidf`, `emb`. Bật bằng `QDE_BACKEND`. |
| `pick_c_tfidf.py` | chọn `C` cho mô hình `tfidf` **một lần** trên nhãn thật, rồi đóng đinh — không dò lại mỗi lần chạy |
| `text_vs_rules.py` | hồ sơ đo đạc biện minh cho việc đổi mô hình: 4 mô hình × 2 lát cắt × đường cong học × cặp câu trùng |
| `backend_curve.py` | **kết quả chính.** Gộp 4 mô hình nền × 14 chỉ số thành một bảng |
| `backend_diff.py` | 72 số dưới hai bảng mốc bất kỳ: cái nào giữ, cái nào đổi, cái nào đổi dấu |

## 3. Bằng chứng về TRỤC — nội dung mà lời giải thích nói ra

| công cụ | làm gì |
|---|---|
| `axis_evidence.py` | ba cửa bác bỏ cho từng trục: hiệu ứng cố định trong cùng bài · so cặp · can thiệp khối |
| `operation_axis.py` | trục thao tác: ontology tiên quyết + vết giải LLM |
| `ablate_full.py` | ablation với khối KG **đầy đủ** (có đủ 3 đại lượng của giả thuyết Vinu 2015) |
| `incremental_value.py` | giá trị biên của từng khối đặc trưng |
| `two_axis_feasibility.py` | hai trục có tách được nhau không |
| `label_source_axes.py` | đổi nguồn nhãn thì trục nào còn giữ — trục bề mặt là tạo tác của người gán |
| `perf_headroom.py` | còn bao nhiêu dư địa trước khi chạm trần của nhãn |

## 4. Nhãn và độ tin của nhãn

| công cụ | làm gì |
|---|---|
| `llm_answer_key.py` | sinh đáp án + kiểm mù cho bộ Sử (**bước LLM, đã đóng băng**) |
| `llm_solution_trace.py` | vết giải cho môn Lý — dùng làm **đặc trưng**, không phải nhãn (**LLM, đóng băng**) |
| `llm_judge_labels.py` / `llm_judge_physics.py` | LLM chấm mức NB/TH/VD/VDC làm nguồn nhãn đối chứng (**LLM, đóng băng**) |
| `label_calibration.py` | hiệu chỉnh thang của giám khảo LLM |
| `label_reliability.py` | bốn phép thay cho người chấm thứ hai |
| `teacher_vs_llm_labels.py` | hai nguồn nhãn lệch nhau ở đâu |
| `e1_label_audit.py` | kiểm toàn vẹn nhãn |
| `dedup.py` | đánh dấu bản sao (`dup_group` / `is_canonical`) — bộ crawl Sử có 54,7 % bản sao |
| `link_history_labels.py` | nối nhãn vào bộ Sử đã gộp |

## 5. Ontology

| công cụ | làm gì |
|---|---|
| `build_all.py` | build ontology cho mọi môn (`*.ttl` → `*.owl`) |
| `ontology_llm_builder.py` · `merge_llm_ontology.py` | mở rộng ontology bằng LLM rồi gộp vào |
| `ontology_resolution.py` | độ phân giải ontology ảnh hưởng thế nào tới kết quả |
| `corr_kg_vs_label.py` | tương quan thô giữa đặc trưng KG và nhãn |
| `crawl/` | 4 script crawl nguồn (kenhgiaovien, vietjack, vietjack Lý, parse bản Sử cũ) |

## 6. Tiện ích

| công cụ | làm gì |
|---|---|
| `reproduce_all.py` | **đóng gói tái lập.** 72 con số buộc vào đường dẫn khoá cụ thể; `--check` thoát mã 1 nếu lệch |
| `stats.py` · `view.py` | thống kê / tra cứu ontology |
| `demo_mcq.py` | demo pipeline độ khó cho từng câu |
| `train.py` | huấn luyện XGBoost phân loại độ khó (bộ phân loại chuẩn, **không** phải mô hình nền của lớp giải thích) |
| `prior_diagnosis.py` | chẩn đoán trước khi chạy |

---

## Một quy ước phải nhớ

`QDE_BACKEND` đổi **mô hình nền của lớp giải thích**, và mỗi mô hình ghi ra một
hậu tố file riêng nên bốn bộ kết quả sống song song, không đè nhau:

| `QDE_BACKEND` | mô hình | đầu ra | bảng mốc |
|---|---|---|---|
| `xgb15` (mặc định) | XGBoost, 15 cột luật tay | `*.json` | `results_frozen.json` |
| `tfidf` | TF-IDF + 15 cột đó | `*_tf.json` | `results_frozen_tf.json` |
| `text` | PhoBERT đóng băng + 15 cột đó | `*_pb.json` | `results_frozen_pb.json` |
| `emb` | PhoBERT đóng băng, không cột luật tay | `*_eo.json` | `results_frozen_eo.json` |

Các nghiên cứu ở mục 3 và 4 **cố ý không đổi theo công tắc này**: chúng so các
khối đặc trưng với nhau bằng một bộ phân loại chuẩn, chứ không đo phản ứng của
hệ thống được giải thích.
