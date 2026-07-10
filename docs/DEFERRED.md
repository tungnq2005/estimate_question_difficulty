# Các mục còn treo (Deferred to Phase 2)

Refactor vừa rồi là **tái cấu trúc giữ nguyên hành vi** (behavior-preserving):
mọi builder/pipeline cho ra kết quả **giống hệt trước** (Lịch sử: 434 thực thể,
761 cạnh, đường kính 12; features Block A không đổi).

Các mục dưới đây được **cố ý để lại** vì chúng **thay đổi số liệu đặc trưng /
kết quả nghiên cứu** (đang có trong `BAO_CAO_TIEN_DO_TUAN_2.md`), nên cần bạn
duyệt và nên làm trên nhánh riêng, đối chiếu byte-diff trước/sau.

## Nhóm A — Hợp nhất dữ liệu Lịch sử (cần giáo viên)
- **Crosswalk curriculum**: đưa 88 cá thể `LessonUnit`/`appearsInLesson` + các
  annotation `abstractness`/`bloomLevel`/`frequencyInTextbook` từ
  `subjects/history/legacy/ontology/su9.ttl` sang 84 Event của bản canonical.
  → làm sống lại 3 feature `curr_pos_*` (hiện luôn 0.0).
- **Thăng cấp entity-linker** từ `legacy/src/entity_extraction.py` (lọc stopword,
  năm→Period, NER). → thêm liên kết năm→Period ⇒ **đổi feature MCQ**.

## Nhóm B — Sửa lỗi đúng đắn (đổi số)
- **Xác định (determinism)**: ✅ **ĐÃ XỬ LÝ phía LOAD (07/2026, có duyệt)**.
  Kiểm chứng thực tế cho thấy nặng hơn đánh giá ban đầu: 2 lần chạy cùng code
  lệch **57 giá trị Block A** (kể cả Sử — 38 khóa nhãn bị ≥2 entity tranh
  chấp, thứ tự iterate đổi theo hash seed từng tiến trình) ⇒ số liệu cũ chưa
  bao giờ ổn định, không tồn tại "bộ số đã công bố" để bảo toàn. Đã sửa trong
  `ontology_bridge.py`: iterate theo thứ tự sort + tie-break tất định (nhãn
  chính thắng alias, cùng hạng URI nhỏ thắng; cạnh trùng cặp (s,o) lấy prop
  lớn nhất theo từ điển). Sau sửa: 2 lần chạy thường giống hệt; cấu trúc
  434 entity / 761 cạnh / diameter 12 giữ nguyên. *Còn treo phần DATA*:
  các khai báo trùng trong `data/` (nguồn của 38 tranh chấp) vẫn nên được
  giáo viên rà và hợp nhất — giờ chỉ là làm sạch dữ liệu, không còn gây
  bất định.
- **`emit_dynamic_entity` (Lịch sử)** không phát `abstractness`/`bloomLevel`/
  `frequencyInTextbook` cho bất kỳ Event nào dù schema có khai báo ⇒
  `kg_abstractness_mean`, `kg_bloom_level_mean` đang tính lệch. Bổ sung sau khi có Nhóm A.
- **`features.py`**: thay các `except -> 0.0` / bỏ dòng thầm lặng bằng
  cơ chế "thiếu thì đánh dấu NaN + báo", để feature suy giảm không bị hiểu nhầm là giá trị thật.

## Nhóm C — Refactor lớn (rủi ro cao, để riêng)
- **`emit_*` → CLASS_SPEC**: sinh `HEADER`/`SCHEMA` từ một spec khai báo, để lược đồ
  và bộ phát không lệch nhau. (~700 LOC, chạm code sinh cả 7 ontology.)
- **Dựng lại dấu tiếng Việt cho `rdfs:label`** từ `display_labels.py`. Đúng về nguyên tắc
  nhưng **đổi mọi vector PhoBERT** ⇒ đổi mọi số Block C.

## Ghi chú kỹ thuật nhỏ (an toàn, làm lúc nào cũng được)
- `subjects/history/data/Chuong5/events_chuong5_bai21.py` và `bai22.py` đang **rỗng
  (0 byte)**; `Chuong6/`, `Chuong7/` là thư mục rỗng — đây là **mốc TODO** (bài 21/22,
  chương 6/7 dự kiến bổ sung), cố ý giữ lại.
- `subjects/history/legacy/` và các README trong đó tham chiếu đường dẫn cũ
  (`build_main.py`, `output/`) — giữ nguyên vì là bản lưu trữ.
