# Hiệu lực phản thực — hai môn, kiểm lời giải thích bằng can thiệp, không cần người

Ngày: 2026-09-01 (bản 2 — xem §2 về việc sửa bộ đặc trưng).
Tool: `tools/counterfactual_validity.py`.
Kết quả: `subjects/{physics,history}/samples/counterfactual_validity.json`.

| | Vật Lí (tự nhiên) | Lịch Sử (xã hội) |
|---|---|---|
| dữ liệu | 1.539 câu, **nhãn giáo viên** | 2.137 câu canonical, **nhãn `llm_vote3`** |
| ontology | 319 thực thể / 310 cạnh | 480 thực thể / 937 cạnh |
| thang nhãn | NB / TH / VD / VDC | NB / TH / VD / VDC (`difficulty_vn`) |
| kho donor | 3.888 nhiễu thật | 5.951 nhiễu thật |

Hai môn dùng **cùng một thang 4 mức**, nên so trực tiếp được.

## 1. Vì sao làm thí nghiệm này

Đánh giá chất lượng một lời giải thích thường phải nhờ **người dùng thật** —
nguồn lực đang bị chặn (`docs/PIVOT_T1_KHONG_DUYET.md`). Thí nghiệm này thay
user study bằng một phép kiểm tự chủ:

> Nếu lời giải thích nói *"câu này khó vì trục BỀ MẶT"* hay *"vì trục TRI THỨC"*,
> thì **can thiệp tối thiểu đúng trục đó** phải làm dự đoán dịch chuyển đúng
> hướng. Không dịch chuyển ⇒ lời giải thích không phản ánh thứ mô hình thật sự dùng.

Đồng thời đây là phép kiểm **giả thuyết gốc của đề tài** (Vinu 2015: *độ khó =
độ tương tự giữa đáp án đúng và các phương án nhiễu*) ở mức **nhân quả**.

## 2. ⚠️ Sửa lỗi so với bản 1 — bộ đặc trưng KG đã thiếu chính đại lượng cần kiểm

Bản 1 dùng lại khối KG của `tools/attic/ablate_physics.py`: entity coverage, số thực
thể, độ sâu tiên quyết. Khối đó **không có** `kad_path_distance_mean`,
`jaccard_kg_*`, `rsi_dc` — tức **ba đại lượng vận hành hoá chính giả thuyết
Vinu**, dù dự án đã viết sẵn cả ba trong `shared/mcq/`.

Kết luận cũ "khoảng cách không lay chuyển mô hình" vì thế **chưa kiểm đúng thứ
định bác**: mô hình không có cách nào *nhìn thấy* khoảng cách. Bản 2 đưa đủ 10
cột KG (kể cả ba cột trên) và **sinh lại toàn bộ số liệu**. Mọi con số Vật Lí ở
bản 1 **không còn hiệu lực**.

Lưu ý cùng hướng: kết luận "KG thêm ~0 giá trị biên" trong
`docs/PHYSICS_EXPERIMENT.md` §5 cũng dựa trên khối KG thiếu đó — cần chạy lại
`tools/attic/ablate_physics.py` với khối đầy đủ trước khi đưa vào luận văn.

## 3. Thiết kế

Mỗi can thiệp thay **đúng một** phương án nhiễu bằng một nhiễu **thật** lấy từ
câu khác, nên văn bản không rơi ra ngoài phân phối.

| nhánh | can thiệp | hứa |
|---|---|---|
| `num_down` / `len_down` | Lý: bỏ 1 nhiễu **có số** · Sử: rút ngắn 1 nhiễu | dễ đi (−) |
| `num_up` / `len_up` | Lý: thêm 1 nhiễu **có số** · Sử: kéo dài 1 nhiễu | khó lên (+) |
| `kg_near` | nhiễu mới cách đáp án đúng **1 hop** | khó lên (+) |
| `kg_far` | nhiễu mới cách **≥3 hop / rời mạch** | dễ đi (−) |
| `placebo` | nhiễu bất kỳ, khớp bề mặt | không đổi |
| `placebo_ent` | như trên, **buộc donor có thực thể** — đối chứng khớp cho hai nhánh KG | không đổi |

**Trục bề mặt khác nhau theo môn, và đó là một phát hiện, không phải tiện tay
chọn:** tín hiệu bề mặt mạnh nhất của Lý là *có tính toán không*
(`num_option_count` ρ = +0,470), của Sử là *hành văn dài bao nhiêu*
(`len_dist_mean` ρ = **+0,536**; `n_year_options` ρ = +0,021, tức **số/năm vô
nghĩa với Sử**).

Đầu ra: Δ E[y] với E[y] = Σ pₖ·k (0 = NB … 3 = VDC), mô hình **out-of-fold**.

## 4. Kết quả

### 4.1. Vật Lí

| nhánh | n | hứa | Δ TB | đúng hướng | so đối chứng khớp | p |
|---|---:|---:|---:|---:|---:|---:|
| `num_down` | 603 | − | **−0,1795** | 72,6% | −0,1566 | **3,0e−28** |
| `num_up` | 1058 | + | **+0,0713** | 61,0% | +0,0941 | **7,3e−21** |
| `kg_near` | 469 | + | −0,0862 | **43,9%** | −0,0423 | 0,044 |
| `kg_far` | 632 | − | −0,0323 | 51,7% | +0,0022 | 0,646 |

hop: nhiễu gốc **0,33** → `kg_near` 0,75 · `kg_far` 6,20 (76,3% rời mạch).
Hồi quy Δ theo hop, kiểm soát **14** biến Δ đặc trưng khác:
**+0,0127** (SE 0,0026, p = 9,3e−07) — **dương, tức NGƯỢC giả thuyết gốc**.

### 4.2. Lịch Sử

| nhánh | n | hứa | Δ TB | đúng hướng | so đối chứng khớp | p |
|---|---:|---:|---:|---:|---:|---:|
| `len_down` | 2131 | − | **−0,1150** | 72,3% | −0,1221 | **2,4e−129** |
| `len_up` | 2098 | + | **+0,0705** | 65,0% | +0,0648 | **3,3e−36** |
| `kg_near` | 921 | + | −0,0157 | **45,0%** | −0,0293 | 2,0e−06 |
| `kg_far` | 1180 | − | +0,0053 | 50,2% | −0,0020 | 0,764 |

hop: nhiễu gốc **2,14–2,39** → `kg_near` 0,96 · `kg_far` 3,98 (chỉ 2,8% rời mạch).
Hồi quy có kiểm soát: **−0,0010** (SE 0,0011, **p = 0,35**) — **bằng không**.

### 4.3. Ba điều hai môn nói giống nhau

1. **Đối chứng dương ăn rất mạnh ở cả hai môn** (p = 3e−28 và 2e−129) ⇒ phép đo
   hoạt động, kết quả âm tính của nhánh KG không phải do phép đo cùn.
2. **`kg_near` đi NGƯỢC lời hứa ở cả hai môn.** Giả thuyết gốc nói nhiễu càng
   gần đáp án trên đồ thị thì càng dễ nhầm ⇒ khó lên. Đo được: đúng hướng
   **43,9%** (Lý) và **45,0%** (Sử) — **dưới mức ngẫu nhiên ở cả hai**, và ở Sử
   sai hướng có ý nghĩa (p = 2,0e−06).
3. **`kg_far` bằng không ở cả hai môn** so với đối chứng khớp (p = 0,65 và 0,76).

### 4.4. Điều hai môn nói KHÁC nhau — và đây mới là phần đáng viết

Mọi đại lượng có tín hiệu đều **đổi dấu** giữa hai môn (Spearman với nhãn 4 mức):

| đại lượng | Vật Lí | Lịch Sử |
|---|---:|---:|
| `len_correct` | **−0,292** | **+0,520** |
| `len_dist_mean` | **−0,278** | **+0,536** |
| `num_option_count` | **+0,470** | −0,007 |
| `kg_centrality_mean` | **−0,306** | **+0,237** |
| `jaccard_kg_max` | **−0,205** | +0,046 |
| `kg_prereq_correct` | −0,244 | −0,017 |
| `kad_path_distance_mean` | +0,056 | −0,043 |

- **Độ dài đảo dấu hoàn toàn.** Ở Sử, phương án dài = mệnh đề phức = khó. Ở Lý,
  phương án dài = câu chữ khái niệm (câu tái hiện), còn câu khó là đáp án số
  ngắn ("2,5 A"). ⇒ **không có đặc trưng bề mặt phổ quát**; một mô hình độ khó
  huấn luyện trên môn này áp sang môn kia sẽ sai **có hệ thống**, không phải sai
  ngẫu nhiên.
- **`jaccard_kg_max` ở Lý mang dấu ÂM (−0,205)** — nhiễu càng *dễ nhầm* theo
  đúng định nghĩa của Vinu thì câu càng **DỄ**. Đây là bác bỏ giả thuyết gốc
  bằng chính vận hành hoá của nó.
- **`kad_path_distance_mean` ≈ 0 ở cả hai môn và trái dấu nhau** (+0,056 /
  −0,043) — đại lượng trung tâm của đề tài **không mang tín hiệu ở đâu cả**.

### 4.5. Quy kết (SHAP) so với can thiệp

| | \|SHAP\| bề mặt | \|SHAP\| KG | tỉ trọng KG |
|---|---:|---:|---:|
| Vật Lí | 0,4996 | 0,5570 | **46,5%** |
| Lịch Sử | 1,1187 | 0,4037 | **28,6%** |

Ở Lý, SHAP gán cho nhóm KG **nhiều hơn** nhóm bề mặt (46,5% tỉ trọng), trong
khi can thiệp cho thấy trục bề mặt đổi dự đoán 0,18 mức còn trục KG thì sai
hướng hoặc bằng 0. **Quy kết và can thiệp lệch nhau rõ.** Ở Sử khoảng lệch nhỏ
hơn (28,6%) nhưng cùng chiều.

⇒ Bằng chứng đo được cho phê phán của *Frontiers in Education 2026* rằng SHAP
chỉ mở "a small window of insight", và là lý do một hệ XAI cho ước lượng độ khó
**không được dừng ở feature attribution** — phải báo cáo **cả quy kết lẫn hiệu
lực can thiệp**.

Ở mức từng câu, tương quan |SHAP nhóm| với phản ứng ròng ≈ 0 ở Lý (−0,05…+0,01,
p > 0,2) và nhỏ ở Sử (−0,06…−0,08), lại có đối chứng bão hoà cùng cỡ ⇒ **chỉ số
mức-từng-câu không dùng được**, luận điểm chỉ nên đứng ở mức toàn cục.

## 5. Hạn chế

1. **Đo trên mô hình, không đo trên học sinh.** Kết luận là "can thiệp trục KG
   không lay chuyển *mô hình*". Muốn nói về *độ khó thật* vẫn cần học sinh làm bài.
2. **Nhãn Sử là `llm_vote3`** — chính đối tượng bị kiểm toán ở
   `docs/PIVOT_T1_KHONG_DUYET.md`. Kết quả Sử nên đọc là "mô hình tái tạo nhãn
   LLM phản ứng thế nào", không phải "độ khó thật phản ứng thế nào". Việc trục
   *hành văn* thống trị ở Sử (ρ = +0,54) khớp với phát hiện cũ rằng nhãn LLM bám
   khuôn mẫu câu chữ — nay có thêm bằng chứng **nhân quả**.
3. **Nhãn Lý là nhãn giáo viên nhưng là thang NHẬN THỨC** (NB/TH/VD/VDC), không
   phải thang độ khó. Xem Q3 trong `docs/TONG_KET_BRAINSTORM.html`.
4. **`kg_near` chỉ đạt 0,75–0,96 hop** chứ không đúng 1,0, vì donor thường chứa
   nhiều thực thể và một trong số đó trùng thực thể của đáp án đúng.
5. Hệ số hop dương ở Lý (+0,0127) đi kèm **14 biến kiểm soát**; nó là tác dụng
   *riêng phần* khi giữ nguyên confusability, không nên đọc như tác dụng tổng.

## 6. Kết luận

1. **Phép đo hiệu lực phản thực dùng được ở cả hai môn** — đối chứng dương
   p = 3e−28 / 2e−129, đối chứng âm hoạt động, tất định, bền theo seed. Đây là
   cách kiểm lời giải thích **không cần người thật**.
2. **Giả thuyết gốc bị bác ở cả hai miền, bằng chính vận hành hoá của nó.**
   `kg_near` đúng hướng dưới 50% ở cả hai; `kg_far` bằng 0; `jaccard_kg` ở Lý
   mang dấu ngược; `kad_path_distance_mean` ≈ 0 ở cả hai và trái dấu nhau.
3. **Không có trục bề mặt phổ quát.** Độ dài đảo dấu hoàn toàn giữa hai môn
   (−0,28 so với +0,54). Đây là luận điểm khái quát hoá mạnh nhất rút ra được từ
   thiết kế hai môn, và nó **chỉ thấy được khi có cả một môn tự nhiên và một môn
   xã hội**.
4. **Cho hướng XAI:** SHAP gán 46,5% (Lý) / 28,6% (Sử) quy kết cho nhóm KG trong
   khi can thiệp cho thấy trục đó sai hướng hoặc bằng 0 ⇒ feature attribution
   một mình **nói quá vai trò của ontology**.

## 7. Việc mở

- **Chạy lại `tools/attic/ablate_physics.py` với khối KG đầy đủ** — kết luận "KG thêm
  ~0 giá trị biên" hiện dựa trên khối thiếu (§2).
- Thang độ phân giải ontology: `docs/ONTOLOGY_RESOLUTION.md`.
- Kiểm nhãn Sử bằng 90 câu nhãn giáo viên hiện có, để tách "phản ứng của mô hình
  tái tạo nhãn LLM" khỏi "phản ứng với độ khó do người gán".
