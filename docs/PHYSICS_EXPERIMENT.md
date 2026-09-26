# Thí nghiệm Vật Lí 9 — KG ontology có dự đoán độ khó không?

Ngày: 2026-08-17. Phạm vi: package `/mnt/d/CS/CS_Major/NCKH/package`.

## 1. Mục tiêu & giả thuyết

Sau khi kết luận KG KHÔNG hiệu quả trên môn Sử (miền tự sự), câu hỏi pivot:
**"KG có hiệu quả trên miền CÓ CẤU TRÚC (Vật Lí) không?"** — vì Lý có chuỗi
tiên quyết (điện trở → định luật Ôm → đoạn mạch) + câu đáp án số + công thức,
khớp thiết kế `prereq_dag` + `numeric_*` của engine.

Giả thuyết cần kiểm: feature KG (đặc biệt `kg_prereq_depth`, `numeric_*`) có
TƯƠNG QUAN / dự đoán được độ khó trên Lý — điều nó không làm được trên Sử.

## 2. Bồi ontology Lý bằng LLM (kết quả C6)

Ontology Lý gốc 132 thực thể (điện/quang) QUÁ MỎNG: độ phủ entity chỉ ~0,19,
THIẾU NGUYÊN khối cơ học (công, công suất, cơ năng, động năng, thế năng).

Pipeline (2 tool mới):
- `tools/ontology_llm_builder.py` — LLM-A (deepseek-v4-flash) trích thực thể +
  cạnh tiên quyết từ 5 chương SGK; LLM-B (deepseek-v4-pro) kiểm chéo.
- `tools/merge_llm_ontology.py` — khử trùng + lọc + gộp vào `phys9.ttl`, CÓ
  chống chu trình (chu trình làm DAG sụp → prereq depth toàn 0 — đã bắt & sửa).

Kết quả:
- 294 thực thể thô → 207 mới (khử trùng + lọc trùng) → **132 → 319 thực thể**.
- `entity_match_coverage`: 0,187 → **0,427** (57% câu khớp ≥1 thực thể).
- Cạnh prereq: 67 → 255 (bỏ 2 cạnh tạo chu trình).
- Câu có `prereq depth > 0`: ~11% → **29%**.

## 3. Dữ liệu (phương án c — ma trận NB/TH/VD/VDC)

Nguồn (c) đúng ý: **kenhgiaovien.com** — trang tài nguyên giáo viên, mỗi bài
chia sẵn 4 mức NHẬN BIẾT / THÔNG HIỂU / VẬN DỤNG / VẬN DỤNG CAO.

- `tools/crawl/crawl_kenhgiaovien.py` — crawl 53 bài SGK Vật Lí 9 cũ → 1545 câu,
  parse 4 định dạng tiêu đề mức độ khác nhau (bug: "PHẦN 1.", "1.", "PHẦN 1:",
  "PHẦN I.", + lỗi chính tả "THÔNG DỤNG").
- `tools/llm_answer_key.py` — nguồn KHÔNG có đáp án → LLM flash xác định đáp án
  (đáp án vật lí khách quan, khác nhãn độ khó chủ quan). 1545/1545 thành công.

Dữ liệu cuối `subjects/physics/samples/mcq_kenhgiaovien.json`:
- **1539 câu** (đủ đáp án + 3 nhiễu + nhãn), phân bố NB 443 / TH 510 / VD 367 / VDC 219.
- Cộng 416 câu VietJack (KHTN, có đáp án, chưa nhãn) → tổng ~1955 câu.

## 4. Tương quan feature ↔ nhãn (đơn biến)

`tools/corr_kg_vs_label.py` — Spearman từng feature vs nhãn ordinal (NB=1..VDC=4):

| feature | Pearson | Spearman |
|---|---|---|
| numeric_option_count (lựa chọn có số) | **+0.470** | **+0.463** |
| entity_match_coverage | -0.319 | -0.339 |
| kg_num_distractor_entities | -0.270 | -0.321 |
| kg_prereq_depth_max | -0.248 | -0.292 |
| kg_prereq_depth_mean_correct | -0.184 | -0.244 |

Số lựa chọn có số tăng đơn điệu: NB=0.41 → TH=1.09 → VD=2.32 → VDC=2.74.

**Diễn giải:** nhãn NB/TH/VD trên Lý ≈ "có tính toán không". Feature số bắt trực
tiếp điều đó (+0.47). Feature KG tương quan ÂM vì câu DỄ nhắc tên khái niệm
(KG thấy → depth>0), câu KHÓ là tính toán (toàn số, KG không thấy tên khái niệm).

## 5. Ablation công bằng (KG có giá trị biên nào không)

`tools/attic/ablate_physics.py` — XGBoost 4 lớp, 5-fold CV (QWK/macro-F1/acc):

| feature set | QWK | macro-F1 | acc |
|---|---|---|---|
| numeric | 0.371 | 0.299 | 0.377 |
| kg | 0.316 | 0.293 | 0.368 |
| numeric+kg | 0.375 | 0.336 | 0.369 |
| baseline (đoán lớp đông) | — | — | 0.331 |

**KG thêm GẦN NHƯ KHÔNG CÓ giá trị biên:** numeric+kg (0.375) ≈ numeric (0.371).

> ⚠️ **ĐÃ SỬA 01/09/2026 — kết luận này KHÔNG còn đúng.** Khối `kg` ở trên
> **thiếu** `kad_path_distance_mean`, `jaccard_kg_*`, `rsi_dc` — đúng ba đại
> lượng vận hành hoá giả thuyết Vinu, dù `shared/mcq/` đã có sẵn cả ba. Chạy lại
> với khối KG đầy đủ (`tools/ablate_full.py`): **QWK 0,371 → 0,407 (+0,036)** ở
> Lý và **0,409 → 0,426 (+0,017)** ở Sử. Ontology **có** giá trị biên thật, chỉ
> là nhỏ — và lát "KG lõi giả thuyết" lại là lát **yếu nhất** của khối
> (QWK 0,272 ở Lý, 0,141 ở Sử). Xem `docs/COUNTERFACTUAL_VALIDITY.md` §2.

Trong-nhóm VD vs VDC (đều là câu tính toán — cho KG "đất diễn"):
- Mọi feature KG tương quan ≈ 0 với VD-vs-VDC (|r| < 0.07).
- XGBoost KG-only (VD vs VDC): QWK = **-0.024** (âm), acc 0.604 < baseline 0.626.

## 6. Kết luận (trung thực)

1. **KG ontology KHÔNG góp phần dự đoán độ khó trên Lý** — kể cả trong phép kiểm
   công bằng (ablation: thêm 0 giá trị biên; trong-nhóm: phẳng/âm).
2. **Tín hiệu thật trên Lý là "tính toán vs nhắc lại"** — feature số +0.47, đơn
   điệu sạch theo nhãn. Đây là phát hiện dương tính có giá trị.
3. **Nguyên nhân gốc:** nhãn NB/TH/VD (Bloom) mã hoá "mức nhận thức = có-tính-
   toán", KHÔNG mã hoá "độ sâu chuỗi tiên quyết". KG đo trục thứ hai, nên không
   khớp nhãn. Đây không phải "KG bị numeric lấn át" mà "KG đo đúng thứ nó được
   thiết kế, chỉ là thứ đó không phải thứ nhãn mã hoá".
4. **Hệ quả cho luận văn:** reframe từ "mô hình KG đoán độ khó" (đã bác bỏ) sang
   "độ khó trên miền cấu trúc được quyết định bởi LOẠI thao tác nhận thức (tính
   toán), bắt được bằng feature đặc thù miền, không phải đồ thị thực thể".

### 6b. Vì sao KG không giúp được ngay cả ở TIER CAO (VD/VDC)

Giả thuyết tự nhiên: "KG (độ sâu tiên quyết) sẽ ảnh hưởng tier cao hơn, không
phải câu phổ thông". Đã kiểm bằng phép trong-nhóm VD-vs-VDC (mục 5): phẳng/âm.

Lý do SÂU hơn "ontology còn nông":
- KG đo **VỊ TRÍ tri thức trong chuỗi học** (khái niệm nào phải học trước khái
  niệm nào). Đây là trục *kiến thức*.
- Nhãn Bloom (VD/VDC) đo **MỨC PHỨC TẠP CỦA THAO TÁC nhận thức** (nhớ → hiểu →
  áp dụng → áp dụng nhiều bước). Đây là trục *thao tác*.
- Hai trục TRỰC GIAO. VDC = "thao tác phức tạp trên khái niệm có-thể-NÔNG".
  VD: "Tính R tương đương của mạch 3 điện trở hỗn hợp" (VDC) dùng khái niệm
  *điện trở* (depth ~1, nông); còn "Định luật Ôm là gì?" (NB) nhắc thẳng *Ôm*
  (nằm sâu hơn trong chuỗi). Depth thậm chí đi NGƯỢC với độ khó.
- ⇒ KG không "đo sai nhãn" — nó đo đúng trục kiến thức, chỉ là độ khó (Bloom)
  không nằm trên trục đó. Giả thuyết "KG giúp tier cao" thất bại vì tier cao
  được định nghĩa bằng thao tác, không bằng vị trí kiến thức.

**Hệ quả tích cực:** KG vẫn có giá trị thật ở NHIỆM VỤ KHÁC — gợi ý kiến thức
tiên quyết cần ôn trước khi làm câu (prerequisite-aware tutoring), ánh xạ câu→
khái niệm, phân tích chương trình. Chỉ là ước lượng độ khó KHÔNG phải chỗ nó giúp.

## 7. Files tạo trong thí nghiệm này

- `tools/ontology_llm_builder.py` — LLM trích ontology từ SGK (2-LLM chéo).
- `tools/merge_llm_ontology.py` — khử trùng + gộp + chống chu trình.
- `tools/crawl/crawl_kenhgiaovien.py` — crawler kenhgiaovien (nhãn NB/TH/VD/VDC).
- `tools/llm_answer_key.py` — LLM xác định đáp án.
- `tools/corr_kg_vs_label.py` — tương quan feature ↔ nhãn.
- `tools/attic/ablate_physics.py` — ablation công bằng.
- `subjects/physics/samples/mcq_crawled.json` — 416 câu VietJack (KHTN).
- `subjects/physics/samples/mcq_kenhgiaovien.json` — 1539 câu (nhãn + đáp án).
- `subjects/physics/samples/llm_ontology_supplement.json` — staging ontology LLM.
- `subjects/physics/ontology/phys9.ttl` — đã bồi lên 319 thực thể.

## 8. Next steps (tuỳ chọn)

- (a) Chạy thêm feature text (TF-IDF/embedding) để so "text vs numeric vs KG" đủ bộ.
- (b) Kiểm chứng nhãn kenhgiaovien bằng 1 GV mẫu (độ tin của nhãn NB/TH/VD).
- (c) Viết dàn ý luận văn "sàn" từ các kết quả âm tính + phát hiện numeric này.
