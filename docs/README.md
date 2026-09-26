# Bản đồ tài liệu

22 file. Mục này nói **đọc cái nào để trả lời câu hỏi gì**, và cái nào là lịch
sử chứ không phải hiện trạng.

---

## Đọc theo thứ tự này nếu mới vào

1. **`TONG_QUAN.md`** — bối cảnh, kỹ thuật dùng và vì sao, tác động, kết quả.
   Một file, đọc hết là nắm được đề tài. **Bắt đầu ở đây.**
2. **`XAI_PIPELINE.md`** — phương pháp đầy đủ: 5 bước, cổng chứng chỉ, kiểm tra
   tỉnh táo, kiểm tra chéo, lớp khai thác. Đây là chương lõi của bài báo.
3. **`BACKEND_CURVE.md`** — kết quả mới nhất và mạnh nhất: bốn mô hình nền,
   lời giải thích chịu được bao nhiêu độ mờ.
4. **`RESULTS_FROZEN.md`** — cách hội đồng kiểm chứng: 72 con số, bốn bảng mốc.

---

## Theo câu hỏi

| bạn muốn biết | đọc |
|---|---|
| đề tài này rốt cuộc làm gì, và kết quả là gì | `TONG_QUAN.md` |
| báo cáo cho GVHD: kỳ vừa rồi đã làm gì | `BAO_CAO_TIEN_DO_09_2026.md` |
| phương pháp giải thích hoạt động ra sao | `XAI_PIPELINE.md` |
| vì sao đổi mô hình nền, và đổi rồi thì sao | `MODEL_UPGRADE.md` → `BACKEND_CURVE.md` |
| thí nghiệm phản thực thiết kế thế nào | `COUNTERFACTUAL_VALIDITY.md` |
| số có tái lập được không | `RESULTS_FROZEN.md`, `VERIFY.md` |
| trục thao tác / trục tri thức, bằng chứng đâu | `OPERATION_AXIS.md`, `XAI_DIAGNOSIS.md` |
| vì sao đề tài không ước lượng độ khó nữa | `PIVOT_T1_KHONG_DUYET.md` |
| văn liệu và ranh giới phát biểu | `RELATED_WORK.md` |
| viết bài báo thì xếp chương thế nào | `PAPER_SKELETON.md` |
| dữ liệu ở đâu ra, ontology dựng thế nào | `HISTORY_MERGE.md`, `ONTOLOGY_RESOLUTION.md`, `PHYSICS_EXPERIMENT.md` |
| nhãn LLM đáng tin tới đâu | `LLM_JUDGE_PHYSICS.md` |
| còn dư địa bao nhiêu trước khi chạm trần nhãn | `PERF_HEADROOM.md` |
| việc gì đang treo | `DEFERRED.md` |

---

## Lịch sử, KHÔNG phải hiện trạng

Giữ lại để đối chiếu, nhưng **đừng trích số từ đây** — chúng có thể đã bị kết
quả mới thay thế:

| file | là gì |
|---|---|
| `BAO_CAO_TIEN_DO.md`, `BAO_CAO_TIEN_DO_TUAN_2.md` | báo cáo tiến độ các kỳ trước (bản mới nhất: `BAO_CAO_TIEN_DO_09_2026.md`) |
| `PIPELINE_REDESIGN_PLAN.md` | kế hoạch thiết kế lại pipeline (07/2026) |
| `TOM_TAT_BAI_BAO.md` | ghi chú đọc tài liệu |
| `archive/*.html` | sáu bản báo cáo tiến độ dạng HTML |

---

## File kết quả (JSON) — sinh ra bởi công cụ, không sửa tay

| file | sinh bởi |
|---|---|
| `results_frozen{,_tf,_pb,_eo}.json` | `reproduce_all.py --freeze` — bốn bảng mốc |
| `backend_curve.json` | `backend_curve.py` — bảng bốn mô hình nền |
| `text_vs_rules.json` + `text_vs_rules_run.log` | `text_vs_rules.py` |
| `xai_sanity{,_tf,_pb,_eo}.json` | `xai_sanity.py` — phân bố rỗng của cổng |
| `natural_raters{,_tf,_pb,_eo}.json` | `natural_raters.py` |
| `perf_headroom.json`, `leak_check.json` | `perf_headroom.py`, kiểm rò rỉ |
