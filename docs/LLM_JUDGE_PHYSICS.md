# LLM-judge vs giáo viên — thang nhận thức NB/TH/VD/VDC (Vật Lí 9)

Ngày: 2026-08-21. Tool: `tools/llm_judge_physics.py`. Model: DeepSeek `deepseek-v4-pro`,
temperature 0, tắt thinking, MÙ đáp án (4 phương án xáo trộn deterministic theo `id`),
rubric Bộ GD&ĐT (NB/TH/VD/VDC). Input: 1.539 câu kenhgiaovien (nhãn GV sạch).

## Câu hỏi nghiên cứu
LLM (zero-shot, direct judging) có tái tạo được nhãn mức nhận thức do giáo viên
thiết kế (ma trận NB/TH/VD/VDC) không?

## Kết quả (n = 1.539)

| chỉ số | giá trị | ý nghĩa |
|---|---|---|
| Cohen κ (thô) | **+0.284** | fair, không mạnh |
| QWK (quadratic) | +0.540 | khớp metric ablation Lý |
| QWK (linear) | +0.415 | |
| Spearman ρ | +0.527 | |
| Kendall τ-b | +0.504 | |
| ⭐ Polychoric (biến ẩn) | **+0.644** | bất biến ngưỡng — đáng tin nhất |
| Đồng thuận tuyệt đối | 48.7% | |
| Đồng thuận sau chuẩn thang | 53.0% (κ=+0.310) | |

Phân bố biên:
- GV  : NB 443 | TH 510 | VD 367 | VDC 219
- LLM : NB 508 | TH 528 | VD 467 | VDC **36**  ← LLM gần như không chấm VDC

Recall của LLM theo từng mức GV: NB 67.3% | TH 44.9% | VD 54.2% | **VDC 11.0%**

Ma trận nhầm (hàng GV, cột LLM):

| GV \ LLM | NB | TH | VD | VDC |
|---|---|---|---|---|
| NB  (443) | 298 | 130 | 15 | 0 |
| TH  (510) | 148 | 229 | 130 | 3 |
| VD  (367) | 43 | 116 | 199 | 9 |
| VDC (219) | 19 | 53 | **123** | 24 |

## Ba kết luận (trung thực, không tô hồng)

1. **Không đoán bừa.** polychoric 0.64 + Kendall 0.50 ⇒ LLM theo dõi gradient
   NB→TH→VD→VDC khá tốt. Đây KHÔNG phải κ≈0 như bên Sử.
2. **Nhưng không tái tạo được nhãn GV.** κ=0.28 (fair), agreement 49% — một nửa
   số câu lệch ≥1 mức. "LLM chấm đúng nhãn nhận thức" là SAI; "LLM chấm gần đúng"
   mới đúng.
3. **⭐ Mù VDC.** LLM chỉ đúng 11% câu VDC, đổ 56% (123/219) vào VD. Cơ chế: mức
   "vận dụng cao" (nhiều bước, kết hợp nhiều công thức) chỉ xác định được qua LỜI
   GIẢI, còn bề mặt câu chữ chỉ để lộ "đây là bài tính" (→VD). Độ phức tạp lời giải
   KHÔNG nằm trên bề mặt câu hỏi — đúng blind-spot cold-start mà KG được dựng để
   lấp, và đã đo được là KG cũng không lấp được (xem PHYSICS_EXPERIMENT.md).

## Caveat bắt buộc (để không tự lừa mình)
So κ=0.28 (Lý) với κ≈0 (Sử) KHÔNG phải thí nghiệm có kiểm soát: Lý dùng thang
NHẬN THỨC NB/TH/VD/VDC (khách quan), Sử dùng thang ĐỘ KHÓ Dễ/TB/Khó (chủ quan).
Chênh lệch κ một phần do đổi ĐỊNH NGHĨA NHÃN, không phải chỉ do đổi môn.
⇒ Chốt được: (i) trên thang nhận thức khách quan LLM chỉ đồng thuận fair với GV;
(ii) LLM mù VDC. Chưa chốt: "môn cấu trúc → nhãn LLM hợp lệ hơn" (cần đối chứng
cùng thang đo).

## Việc mở (chờ duyệt)
- Kiểm giả thuyết "mù VDC do không thấy lời giải": cho LLM giải từng bước rồi chấm
  lại 1 mẫu VDC, xem recall VDC có nhảy không.
- Đo độ ổn định nội tại của LLM (test-retest: đổi thứ tự xáo phương án / model khác)
  để củng cố con số κ.

## Artifacts
- `subjects/physics/samples/mcq_kenhgiaovien_llmjudge.json` — nhãn LLM + thứ tự xáo.
- `subjects/physics/samples/llm_judge_agreement.json` — bảng đồng thuận đầy đủ.
