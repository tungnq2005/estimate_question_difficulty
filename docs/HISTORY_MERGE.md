# Hợp nhất môn Lịch sử (History merge)

Trước khi refactor, dự án có **hai bản Lịch sử song song** cùng dùng namespace
`http://su9.edu.vn/ontology#` nhưng là **hai ontology khác nhau**:

| | `su9_ontology/` (mới) | `history/` (cũ) |
|---|---|---|
| Thực thể | **434** | 319 |
| Lớp gốc | `Tri_thuc_Lich_su` | `HistoricalEntity` |
| Dữ liệu | 18 file theo chương/bài (dict giàu thông tin) | 3 file `build_ontology*.py` (tuple) |
| Điểm mạnh riêng | `weightsJson`, `hasPerson`, mô hình Event chi tiết; là bản pipeline MCQ đang chạy | lớp *curriculum* (`LessonUnit`, `appearsInLesson`), entity-linker tốt hơn (lọc stopword, năm→Period, NER) |

Sự chồng chéo này là nguồn khó hiểu lớn nhất của codebase (chỉ ~70/841 URI trùng,
**0 Event trùng** vì quy ước ID đã rẽ nhánh).

## Quyết định

**`su9_ontology/` là bản chuẩn (canonical) → trở thành `subjects/history/`.**

Lý do: (1) đây là bản pipeline MCQ thực sự đang đọc; (2) artifact mới nhất;
(3) bố cục dữ liệu theo chương/bài dễ mở rộng; (4) mang mô hình Event + `weightsJson`
mà các đặc trưng Jaccard-KG và KAD được tính từ đó.

Bản cũ **không bị xoá** — nó là *nguồn dữ liệu chỉ-đọc* cho phase 2, được giữ tại:

```
subjects/history/legacy/
├── ontology/su9.ttl        # ontology 319 thực thể (BẢN SAO DUY NHẤT của lớp curriculum)
├── src/                    # pipeline free-text: entity_extraction (linker tốt hơn), feature_extraction, ...
├── build_ontology*.py      # builder cũ
└── data/sample_questions.json
```

## Còn treo cho phase 2 (xem [DEFERRED.md](DEFERRED.md))

Việc *thực sự* hợp nhất dữ liệu là một **tác vụ nhập liệu có kiểm định của giáo viên**,
không phải đổi code, và nó **thay đổi số liệu đặc trưng** — nên để lại phase 2:

- Chuyển (crosswalk) 88 cá thể *curriculum* + annotation (`abstractness`/`bloomLevel`/
  `frequencyInTextbook`) từ `legacy/ontology/su9.ttl` sang 84 Event của bản mới.
- "Thăng cấp" entity-linker của `legacy/src/entity_extraction.py` (lọc stopword,
  năm→Period, NER) — sẽ thêm liên kết năm→Period nên **đổi feature của MCQ**.
