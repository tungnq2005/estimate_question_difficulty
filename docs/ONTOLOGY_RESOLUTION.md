# Giả thuyết độ phân giải — kiểm trên hai môn, KHÔNG được ủng hộ

Ngày: 2026-09-01 (bản 2 — bộ đặc trưng đã sửa, xem `COUNTERFACTUAL_VALIDITY.md` §2).
Tool: `tools/ontology_resolution.py`.
Kết quả: `subjects/{physics,history}/samples/ontology_resolution.json`.

## 1. Giả thuyết đem kiểm

Thí nghiệm hiệu lực phản thực đo được: ở Vật Lí, nhiễu **thật** do giáo viên
viết nằm ở **0,33 hop** so với đáp án đúng — bốn phương án phần lớn **sụp về
cùng một nút**. Giả thuyết bào chữa dễ chịu nhất cho ontology:

> Khoảng cách trên đồ thị không lay chuyển được dự đoán **không phải vì ý tưởng
> sai**, mà vì ontology **không đủ mịn để phân biệt các phương án**. Mịn hơn thì
> tác dụng sẽ hiện ra.

## 2. Ba phép kiểm, hai môn

| # | phép | ý tưởng |
|---|---|---|
| A | **làm thô có kiểm soát** | gộp nút trong bán kính k thành siêu nút (k = 0…3), đo đường liều–đáp ứng |
| B | **đầu mút phân giải tối đa** | thay khối KG bằng cosine PhoBERT giữa các phương án — phân biệt **mọi** phương án (100%) |
| C | **phân tầng trên dữ liệu thật** | so nhóm câu ontology **đã tách được** phương án với nhóm **sụp về một nút** |

Can thiệp được **định nghĩa cố định** trên đồ thị mịn nhất ở mọi mức — "liều"
không đổi, chỉ **độ phân giải của đặc trưng mô hình** thay đổi. Khối KG ở đây
**có** `kad_path_distance_mean` tính trên đồ thị đã co, tức mô hình *nhìn thấy
được* khoảng cách ở mọi mức.

**Vì sao hai môn là phép kiểm mạnh hơn một môn:** Lịch Sử có ontology dày hơn và
tách phương án tốt hơn gần **3 lần** (42,7% so với 15,7%), nhiễu gốc nằm ở
**2,30 hop** thay vì 0,33. Nếu độ phân giải là nút thắt, Sử phải cho tác dụng rõ
hơn hẳn Lý.

## 3. Kết quả

### 3.1. Thang phân giải (phép A + B)

**Vật Lí** — nhiễu gốc 0,33 hop

| mức | #nút | tách được | hệ số hop | p | \|Δ\| nhánh KG | \|Δ\| bề mặt |
|---|---:|---:|---:|---:|---:|---:|
| k=0 | 319 | 15,7% | −0,00299 | 0,167 | 0,281 | 0,272 |
| k=1 | 153 | 11,3% | −0,00978 | 6,9e−06 | 0,278 | 0,278 |
| k=2 | 116 | 10,2% | −0,00615 | 0,0086 | 0,286 | 0,285 |
| k=3 | 101 | 9,7% | −0,00729 | 0,00065 | 0,272 | 0,271 |
| **emb** | — | **100,0%** | **+0,00545** | 0,016 | 0,288 | 0,350 |

**Lịch Sử** — nhiễu gốc 2,30 hop

| mức | #nút | tách được | hệ số hop | p | \|Δ\| nhánh KG | \|Δ\| bề mặt |
|---|---:|---:|---:|---:|---:|---:|
| k=0 | 480 | **42,7%** | +0,00166 | 0,140 | 0,137 | 0,187 |
| k=1 | 218 | 39,3% | +0,00175 | 0,107 | 0,132 | 0,188 |
| k=2 | 64 | 27,1% | +0,00251 | 0,015 | 0,125 | 0,190 |
| k=3 | 43 | 17,6% | +0,00115 | 0,263 | 0,124 | 0,195 |
| **emb** | — | **100,0%** | +0,00106 | 0,292 | 0,123 | 0,174 |

**Đọc bảng:**

- **Không có đường liều–đáp ứng.** 10 điều kiện (2 môn × 5 mức) trải độ tách từ
  **9,7% đến 100%**; hệ số hop luôn ≤ 0,0098 về trị tuyệt đối, **đổi dấu giữa
  hai môn** (Lý âm ở các mức đồ thị, Sử dương suốt), và **đổi dấu ngay trong
  Lý** khi lên đầu mút phân giải tối đa. Không hề đơn điệu theo độ phân giải.
- **Môn có ontology tách tốt gần gấp 3 lại cho hệ số NHỎ HƠN** (Sử +0,0017 ở
  k=0 so với Lý −0,0030), tức ngược hẳn dự đoán của giả thuyết.
- **Để so:** can thiệp trục bề mặt làm |Δ| = 0,12–0,35 ở cùng bảng. Hiệu ứng
  khoảng cách nhỏ hơn **một tới hai bậc độ lớn**.

### 3.2. Phân tầng (phép C) — lặp lại được trên cả hai môn

| môn | nhóm | n | hệ số hop | p |
|---|---|---:|---:|---:|
| Vật Lí | ontology **tách được** | 640 | +0,00366 | 0,334 |
| Vật Lí | bốn phương án **sụp một nút** | 1817 | −0,00422 | 0,105 |
| Lịch Sử | ontology **tách được** | 2507 | +0,00157 | 0,403 |
| Lịch Sử | bốn phương án **sụp một nút** | 1723 | −0,00311 | 0,074 |

chênh hai nhóm: Lý **+0,0079** (z = +1,72) · Sử **+0,0047** (z = +1,83)

Giả thuyết độ phân giải dự đoán chênh này **âm rõ** (nhóm tách được phải nhạy
hơn). Đo được **dương ở cả hai môn**, cùng cỡ, cùng dấu — tức **lặp lại được**.
Gộp hai môn theo Stouffer: z ≈ **+2,51** (p ≈ 0,012).

⚠️ **Trung thực về độ mạnh:** từng môn một, **cả bốn hệ số đều không có ý nghĩa
thống kê** (p = 0,07 … 0,40). Luận điểm đứng được là ở chỗ **dấu lặp lại trên
hai miền độc lập**, không phải ở chỗ từng phép mạnh. Bản 1 của tài liệu này báo
z = +2,69 và dùng chữ "BÁC BỎ" — con số đó tính trên bộ đặc trưng **thiếu**
`kad_path_distance_mean`, nay đã sửa và **kết luận phải nói nhẹ đi**.

## 4. Kết luận

1. **Giả thuyết độ phân giải KHÔNG được ủng hộ** — nhưng cách nói đúng không
   phải "đã bác bỏ" mà là: **không còn gì để độ phân giải điều biến**, vì hiệu
   ứng khoảng cách vốn đã ≈ 0 ở mọi mức, mọi môn.
2. **Đây là phát biểu mạnh hơn "ontology còn thô".** Môn có ontology tách phương
   án tốt gấp 3 (Sử) cũng không cho tác dụng nào. Nút thắt **không nằm ở độ
   phân giải**.
3. **Không nên đầu tư dựng ontology mịn hơn để cứu ước lượng độ khó.** Đây là
   câu trả lời có bằng chứng cho "có nên làm tiếp không", tiết kiệm nhiều tuần công.
4. Kết hợp với `docs/COUNTERFACTUAL_VALIDITY.md`: ontology **có** giá trị dự báo
   biên nhỏ nhưng thật (QWK +0,036 Lý / +0,017 Sử, xem `tools/ablate_full.py`),
   và giá trị đó đến từ **độ phủ / vị trí khái niệm**, không phải từ **khoảng
   cách đáp-án↔nhiễu** — lát "KG lõi giả thuyết" là lát **yếu nhất** của khối KG
   ở cả hai môn.

## 5. Hạn chế

1. **Chỉ làm thô được, không làm mịn được.** Phép A quét 15,7% → 9,7% (Lý) và
   42,7% → 17,6% (Sử). Vùng giữa 42,7% và 100% **chỉ có đầu mút PhoBERT**, mà
   PhoBERT là *họ biểu diễn khác*, không phải "cùng đồ thị nhưng mịn hơn".
2. **Từng phép phân tầng đều không có ý nghĩa** (§3.2). Chỉ dấu lặp lại mới là
   bằng chứng.
3. **Khối KG của thang phân giải chỉ có 7 cột** — `jaccard_kg_*` và `rsi_dc`
   dựa trên tập láng giềng thực thể, muốn làm thô đúng phải viết lại chúng. Hai
   cột đó có mặt trong thí nghiệm phản thực (10 cột) nhưng vắng ở đây.
4. **Nhãn Sử là `llm_vote3`** — xem `COUNTERFACTUAL_VALIDITY.md` §5.2.
5. Vẫn là đo **trên mô hình**, không phải trên học sinh.

## 6. Việc mở

- Cân bằng nhóm "tách được"/"sụp" theo nhãn NB/TH/VD/VDC để loại nhiễu loại-câu.
- Viết bản làm-thô cho `jaccard_kg_*`/`rsi_dc` để thang phân giải dùng đủ 10 cột.
