# Gác lửng — những nhánh đã dừng, và vì sao

Các file ở đây **không còn chạy trong đường ống nào** và không tool nào đang
dùng import chúng. Chúng được giữ lại chứ không xoá, vì trong một đề tài nghiên
cứu thì **nhánh đã thử và đã bỏ cũng là dữ liệu**: nó trả lời câu "sao các bạn
không làm cách X" bằng một file có thật, có ngày tháng, thay vì bằng trí nhớ.

Không file nào ở đây được trích dẫn trong bảng 72 số đóng băng.

---

## A. Nhánh KHẢO SÁT NGƯỜI THẬT — dừng vĩnh viễn

**Vì sao dừng.** Kế hoạch gốc cần học sinh làm bài thật để có `p-value` (tỉ lệ
trả lời đúng) làm ground truth, cộng thêm giáo viên chấm độ khó làm nguồn nhãn
thứ ba. Xin phép tổ chức làm bài tại trường (mốc T1) **không được duyệt**, và
ràng buộc của đề tài từ đó là **không dùng mẫu người thật** — không học sinh,
không giáo viên chấm, kể cả một người.

Đây là lý do đề tài chuyển trục từ *ước lượng* độ khó sang *giải thích* độ khó:
lời giải thích kiểm chứng được bằng **can thiệp** trên văn bản, không cần người.
Xem `docs/PIVOT_T1_KHONG_DUYET.md`.

| file | nó làm gì |
|---|---|
| `make_test_forms.py` | chọn ~120 câu Sử, sinh 3 đề × 40 câu để tổ chức làm bài |
| `select_items_unlabeled.py` | bản viết lại của trên, chọn ~45 câu **không nhìn nhãn** |
| `make_student_forms.py` | sinh 3 Google Form cho học sinh làm bài |
| `make_teacher_form.py` | sinh form giáo viên chấm Dễ / Trung bình / Khó |
| `make_self_assessment_form.py` | form tự đánh giá, thay cho pilot mô phỏng |
| `convert_google_responses.py` | CSV từ Google Sheet → `student_responses.csv` |
| `convert_self_assessment.py` | JSON từ form tự đánh giá → cùng schema trên |
| `item_analysis.py` | phân tích cổ điển (CTT): p-value, độ phân biệt, KR-20 |
| `coldwarm.py` | thí nghiệm Cold→Warm: tri thức có cấu trúc đáng bao nhiêu lượt trả lời |

`item_analysis.py` và `coldwarm.py` đọc `student_responses.csv` — **file đó chưa
bao giờ tồn tại**, vì không có lượt trả lời nào được thu.

### A2. Thay học sinh thật bằng học sinh mô phỏng — cũng dừng

| file | nó làm gì | vì sao dừng |
|---|---|---|
| `llm_student_sim.py` | LLM đóng vai học sinh làm bài, có gọi API thật | đổi một construct không kiểm được lấy một construct khác cũng không kiểm được; LLM trả lời theo văn phong câu hỏi, không theo năng lực |
| `llm_persona_pilot.py` | pilot 20 cặp câu, δ do người gán tay, không gọi API | chỉ là bước dò trước cho cái trên |

---

## B. Bị thay bởi bản mới

| file | bị thay bởi | vì sao |
|---|---|---|
| `ablation.py` | `ablate_full.py` | bản cũ thiếu ba đại lượng của chính giả thuyết Vinu 2015 (`kad_path_distance`, `jaccard_kg_*`, `rsi_dc`), nên nó chưa kiểm đúng thứ nó định bác |
| `ablate_physics.py` | `ablate_full.py` | như trên, bản riêng cho môn Lý |
| `explain_difficulty.py` | `xai_difficulty.py` | bản cũ **dẫn bằng SHAP**; toàn bộ kết quả của đề tài nói quy kết SHAP không dự báo được phản ứng can thiệp, nên để nó lại là tự mâu thuẫn |

---

## C. Thăm dò một lần, đã trả lời xong

| file | câu hỏi nó trả lời |
|---|---|
| `binary_easy_hard.py` | gộp 4 mức thành dễ/khó thì con số có "đẹp" lên không — có, nhưng đó là đổi bài toán để lấy số đẹp, không phải kết quả |
| `coverage_check.py` + `_coverage_runs/` | ontology phủ được bao nhiêu phần câu hỏi ở các chương mới bổ sung |
| `label_basis_probe.py` | nhãn LLM và nhãn giáo viên dựa vào cái gì (giả thuyết do GVHD nêu 17/08/2026) |
| `_test_block_swap.py` | cơ chế hoán khối vết giải — bản nháp trước khi có cổng B1 chuẩn; đã thành `axis_evidence.py` |

---

## D. Nhánh không đi

| file | vì sao không đi |
|---|---|
| `colab_finetune_phobert.py` | **tinh chỉnh** PhoBERT trên GPU Colab. Đề tài dùng PhoBERT **đóng băng** (chỉ lấy vector, không huấn luyện lại): rẻ hơn, tất định, cache được ra đĩa, và quan trọng hơn — mô hình nền phải **đơn giản và tái lập được** vì nó là *đối tượng được giải thích*, không phải sản phẩm. Xem `docs/MODEL_UPGRADE.md` §6. |
