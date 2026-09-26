# Trục thao tác — đo được không, và vì sao môn tự nhiên khác môn xã hội

> Công cụ: `tools/two_axis_feasibility.py` · `tools/operation_axis.py` ·
> `tools/llm_solution_trace.py` · `tools/llm_judge_labels.py` ·
> `tools/incremental_value.py`
> Kết quả: `subjects/*/samples/{two_axis_feasibility,operation_axis,incremental_value}.json`
> Toàn bộ số dưới đây lấy **nhãn GIÁO VIÊN** làm chân lý.

## 0. Câu hỏi

Lí thuyết hai trục của đề tài:

```
độ khó = TRỤC TRI THỨC (câu hỏi nằm ở đâu trong đồ thị tri thức)
       × TRỤC THAO TÁC (câu hỏi đòi thao tác nhận thức gì)
```

Chẩn đoán trước khi đo: **chỉ trục thứ nhất có dụng cụ.** Mọi cột KG cũ
(`kad_path_distance_mean`, `jaccard_*`, `rsi_dc`, `kg_prereq_*`) đều đo quan hệ
**đáp án ↔ nhiễu** — tức giả thuyết Vinu, đã bị bác bỏ ở
[COUNTERFACTUAL_VALIDITY.md](COUNTERFACTUAL_VALIDITY.md). Không cột nào đo
**câu dẫn → đáp án**. Còn thứ đang đóng vai "trục thao tác" thì thực chất là
**độ dài văn bản**, mà độ dài đã bị chứng minh là đặc tính của người gán nhãn
LLM chứ không của độ khó ([XAI_DIAGNOSIS.md](XAI_DIAGNOSIS.md) §1.8, và
`tools/label_source_axes.py`).

## 1. Dựng dụng cụ mới, và nó chết ở môn Sử

Thêm hai khối đề tài chưa từng có: **chiều sâu suy luận** (số bước trên đồ thị
từ thực thể câu dẫn → thực thể đáp án) và **dấu hiệu ngôn ngữ** (khuôn hỏi
tiếng Việt phân tầng Bloom).

Môn Sử, nhãn giáo viên, n = 1.276:

| bộ đặc trưng | QWK | AUC tầng cao | rec VD | rec VDC |
|---|---:|---:|---:|---:|
| bề mặt (hành văn) | 0,152 | 0,617 | 2,5% | 10,3% |
| thao tác · ngôn ngữ thuần (bỏ đếm từ) | 0,133 | 0,587 | 0,0% | 1,1% |
| **thao tác · chiều sâu KG** | 0,107 | **0,495** | 0,0% | 0,0% |
| trục tri thức (vị trí) | 0,135 | 0,535 | 1,2% | 0,0% |
| hai trục + bề mặt | 0,192 | 0,679 | 0,0% | 6,9% |

**AUC 0,495 là đúng bằng tung đồng xu.** Và không đổ được cho độ phủ: chỉ 39%
câu tính được chiều sâu (đáp án chứa thực thể nhận ra được ở 46,5% câu), nhưng
**xét riêng 496 câu nối được** thì `depth_min` ρ −0,088 / AUC 0,497,
`depth_mean` ρ −0,008 / AUC 0,496 — chuẩn hoá cả hai nguồn nhãn. Dấu còn **ngược**
trực giác: nhiều bước hơn thì *dễ* hơn.

## 2. Vì sao — đếm cạnh là đủ

| ontology | cạnh chủ đạo | cạnh **tiên quyết** | phủ câu dẫn→đáp án |
|---|---|---:|---:|
| Sử (`su9.ttl`) | `occursAt`, `occursDuring`, `hasContent`, `hasOrganization` | **0** | **0,0%** |
| Lý (`phys9.ttl`) | `prerequisiteOf`, `relatesQuantities` | **216** | 18,6% |

Không phải ý tưởng sai — là **đo trên đồ thị không mang thông tin đó**. Cạnh Sử
mã hoá *"cái gì liên quan cái gì"*; khoảng cách trên nó là độ gần chủ đề trong
bách khoa, một tính chất của **cách tác giả ontology nối**, không phải của việc
học sinh phải làm mấy bước. Cạnh `prerequisiteOf` mã hoá *"phải biết Y trước mới
tới được X"* — đúng ngữ nghĩa mà trục thao tác cần.

Chạy y hệt khối "thao tác · ontology" hai môn: Sử **QWK 0,000 · AUC 0,498** (đồ
thị tiên quyết rỗng), Lý **QWK 0,262 · AUC 0,696 · rec VD 40,9%**.

## 3. Vết giải do LLM sinh — dùng làm ĐẶC TRƯNG, không làm nhãn

`tools/llm_solution_trace.py`. Nguyên tắc, và đây là chỗ khác mọi cách dùng LLM
trước đó trong đề tài:

| | đo được |
|---|---|
| LLM **đáng tin** ở việc **GIẢI** | 87,7% trên 211 câu Sử có đáp án người (`llm_answer_key.py`) |
| LLM **không** đáng tin ở việc **PHÁN ĐỘ KHÓ** | κ 0,256 với giáo viên; tầng VD/VDC đồng thuận 7,1% |

Vậy hỏi nó thứ nó làm được, rồi lấy **tiến trình giải** làm cột: mấy bước tính,
dùng công thức nào, mấy đại lượng đã cho, mấy ẩn trung gian. Nhãn độ khó vẫn
hoàn toàn của giáo viên.

Tác dụng phụ: khớp chuỗi nhận ra thực thể `Formula` ở đúng **1/1539 câu** (nhãn
công thức là "U = I.R", không bao giờ trùng lời văn đề). LLM thì liên kết được —
140 câu `F_Ohm`, 108 câu `F_R_DayDan`, 58 câu `F_CongSuat`… nhờ đó
`applicationSteps` trong `.ttl` mới truy cập được.

> ⚠️ **Sửa một phát biểu quá lời.** Bản đầu của mục này viết `tr_ont_steps_sum`
> ρ +0,474 là *"chỗ ontology thật sự trả công"*. **Sai.** Đo lại:
> ρ(`tr_steps`, `tr_ont_steps_sum`) = **+0,928** — chú giải của ontology gần như
> là **bản sao** của số bước mà chính LLM đã đếm. Thêm khối này vào vết giải chỉ
> được QWK +0,012 · AUC +0,004, và recall VDC còn **giảm** (21,5% → 20,1%).
> Chỗ ontology trả công thật nằm ở **đồ thị tiên quyết**, không ở chú giải — xem
> §3.3.

Chi phí: 77 lượt gọi, 0 lỗi, 1.539/1.539 câu. Đáp án nó suy ra khớp đáp án đang
lưu 91,9% (nhất quán nội bộ — **không** phải chuẩn vàng, vì đáp án Lý cũng do
LLM sinh trước đó).

### 3.1. ⚠️ Một cột phải loại: `tr_op_type`

Tôi hỏi LLM phân loại thao tác thành `nhớ / hiểu / tính / phân tích`. Bốn nhãn
đó ánh xạ gần 1:1 vào NB/TH/VD/VDC. Kiểm trực tiếp: **dùng riêng cột đó làm dự
đoán được QWK +0,492**, trong khi LLM chấm độ khó thẳng được +0,540 — nó thu lại
**91%** sức mạnh của một bộ chấm độ khó, tức vi phạm đúng tiền đề trên. Đã loại
khỏi mọi cấu hình "sạch" và báo cáo riêng.

Cùng lí do, mọi cột đếm chữ cũng bị loại: **một mình `opt_n_words`** cho QWK
0,506 · AUC 0,783 ở môn Lý, đánh bại cả khối bề mặt 5 cột hiện tại. Ở Lý độ dài
*có thể* là hệ quả thật của thao tác (câu VD/VDC buộc phải cấp dữ kiện; ρ +0,562
ở Lý so với +0,243 ở Sử trên cùng loại nhãn), nhưng vẫn phải tách bạch để lập
luận không dựa vào nó.

### 3.2. Môn Lý, nhãn giáo viên, n = 1.539

| bộ đặc trưng | #cột | QWK | AUC cao | rec VD | rec VDC |
|---|---:|---:|---:|---:|---:|
| bề mặt (hiện tại) | 5 | 0,371 | 0,721 | 28,9% | 12,3% |
| KG hiện tại (đáp án↔nhiễu, Vinu) | 10 | 0,336 | 0,702 | 71,9% | 0,9% |
| vết giải **thuần thủ tục** | 6 | 0,420 | 0,717 | 34,1% | 20,1% |
| **thủ tục + ontology + văn bản, bỏ độ dài** | 22 | **0,471** | **0,797** | 34,9% | **26,9%** |
| thủ tục + tất cả (có độ dài) | 38 | 0,546 | 0,832 | 40,9% | 30,1% |

Hàng in đậm là cấu hình **sạch**: không cột độ dài, không cột phán đoán LLM.

### 3.3. Tách bốn kênh — ontology đóng góp ở đâu, bao nhiêu

"Trục thao tác" ở §3.2 gộp bốn nguồn rất khác nhau. Tách ra rồi đo riêng (môn Lý,
nhãn giáo viên, n = 1.539):

| kênh | #cột | QWK | AUC cao | rec VDC | cột mạnh nhất (t trong bài) |
|---|---:|---:|---:|---:|---|
| **A** · đồ thị tiên quyết thuần | 5 | 0,080 | 0,601 | 0,0% | `op_pre_need_new` t −6,7 |
| **B** · chú giải ontology qua khớp chuỗi | 6 | 0,193 | 0,607 | 2,7% | `op_n_formula` t +4,4 |
| **C** · vết giải LLM (0 ontology) | 4 | **0,408** | **0,713** | **21,5%** | `tr_given` t +23,5 |
| **D** · lai: LLM liên kết → ontology cấp số | 2 | 0,379 | 0,697 | 10,5% | `tr_ont_steps_max` t +21,0 |

Cộng dồn lên nền vết giải LLM:

| | AUC cao | ΔAUC so với C | p |
|---|---:|---:|---:|
| C · vết giải LLM thuần | 0,713 | — | — |
| C + D ⟨chú giải ontology⟩ | 0,717 | +0,004 | — |
| C + A ⟨đồ thị tiên quyết⟩ | 0,762 | **+0,049 [+0,033, +0,066]** | **0,0000** |
| C + A + B + D ⟨toàn trục⟩ | 0,778 | +0,065 | — |

Nhưng ΔQWK của A chỉ **+0,001 [−0,019, +0,021], p = 0,92**. Nghĩa là:
**đồ thị tri thức giúp phân biệt "tầng cao hay không", KHÔNG giúp xếp đúng bốn
mức.** Đây là phát biểu chính xác hơn hẳn "ontology đóng góp".

**Bao nhiêu trong đó là topo thật, bao nhiêu chỉ là đếm thực thể?**

| thêm vào C | ΔAUC | KTC 95% | p |
|---|---:|---|---:|
| chỉ ĐẾM thực thể (`kg_num_*`, `depth_n_*`) | +0,047 | [+0,024, +0,069] | 0,0000 |
| chỉ TOPO tiên quyết | +0,049 | [+0,033, +0,067] | 0,0000 |
| **TOPO, SAU KHI đã có ĐẾM** | **+0,021** | **[+0,009, +0,035]** | **0,0000** |

Vậy khoảng **43%** cái tưởng là "topo" thật ra chỉ là *đếm xem câu chạm bao nhiêu
thực thể* — thứ không cần đồ thị nào cả. Phần **không rút gọn được về đếm** là
**+0,021 AUC**. Nhỏ, nhưng khác 0 chắc chắn, và đó mới là phần **tỉ lệ thuận với
chất lượng đồ thị**.

### 3.4. Và nó chạy NGƯỢC chiều trực giác

`op_pre_need_new` = số tiên quyết mà **đáp án** đòi nhưng **câu dẫn không cấp**.
Đây đáng lẽ là "chiều sâu suy luận" đúng nghĩa nhất. Đo được:

| | NB | TH | VD | VDC |
|---|---:|---:|---:|---:|
| trung bình `op_pre_need_new` | **0,44** | 0,41 | 0,13 | **0,06** |

β trong bài **−0,181**, t **−6,69**. Càng đòi nhiều tiên quyết thì càng **DỄ**.

Lí do giống hệt cơ chế đổi dấu của trục tri thức ở §4.7: câu VD/VDC môn Lý là
**tình huống số liệu**, nhắc rất ít thực thể có tên; câu NB/TH mới là câu hỏi về
khái niệm nằm sâu trong chuỗi tiên quyết. Nên đồ thị tiên quyết ở đây **không đo
chiều sâu suy luận** — nó hoạt động như một **bộ nhận dạng LOẠI CÂU** (khái niệm
hay tính toán). Đóng góp là thật, tên gọi thì phải sửa.

### 3.5. ⚠️ Giá trị p của phép cặp ghép KHÔNG đáng tin

Các cặp không độc lập — một câu xuất hiện trong hàng chục cặp — nên kiểm định nhị
thức là **quá dễ dãi**. Bằng chứng nội bộ: đối chứng xáo ngẫu nhiên ra **48,1%
với p = 0,006** ở phép này, trong khi ở §4.6 nó ra 50,7% với p = 0,27. Đối chứng
hành xử không nhất quán ⇒ **đọc phép cặp ghép bằng ĐỘ LỚN hiệu ứng, đừng đọc bằng
p**. Các kết luận định lượng trong doc này dựa vào bootstrap AUC và hệ số hiệu
ứng cố định, không dựa vào p của cặp ghép.

## 4. Phép quyết định — "vậy sao không hỏi thẳng LLM cho xong?"

`tools/incremental_value.py`. Cần nhãn LLM **trên đúng những câu giáo viên đã
chấm**, ở cả hai môn — Sử được chấm nốt bằng `tools/llm_judge_labels.py`
(64 lượt gọi, 1.276/1.276). Mô hình lồng nhau, chân lý là nhãn giáo viên.

### 4.1. Lý (n = 1.539) — LLM khá, ta vẫn thêm được

| mô hình | #cột | QWK | AUC cao | rec VD | rec VDC |
|---|---:|---:|---:|---:|---:|
| (a) chỉ nhãn LLM | 1 | 0,540 | 0,765 | 54,2% | 11,0% |
| (b) chỉ đặc trưng SẠCH | 52 | 0,531 | **0,832** | 40,6% | **31,1%** |
| (c) cả hai | 53 | **0,560** | **0,840** | 43,6% | 32,0% |

| | ΔQWK | ΔAUC |
|---|---|---|
| SẠCH thêm cho LLM | +0,021 [−0,011, +0,053] p = 0,204 | **+0,075 [+0,056, +0,094] p = 0,000** |
| LLM thêm cho SẠCH | +0,030 [+0,009, +0,053] p = 0,008 | +0,008 [+0,001, +0,016] p = 0,033 |

Cả hai chiều đều có ý nghĩa ⇒ **hai nguồn mang thông tin bổ sung nhau**, không
ai thay được ai. Chỗ đóng góp của ta nằm đúng ở **tầng cao**: AUC +0,075, và
recall VDC 11,0% → 31,1% (gần gấp ba). LLM xếp hạng thô tốt (QWK 0,540) nhưng
gộp VDC vào VD (rec VD 54,2% mà VDC 11,0%).

### 4.2. Sử (n = 1.276) — LLM kém, và không thêm được gì

| mô hình | #cột | QWK | AUC cao |
|---|---:|---:|---:|
| (a) chỉ nhãn LLM | 1 | 0,151 | 0,557 |
| (b) chỉ đặc trưng SẠCH | 30 | 0,197 | 0,629 |
| (c) cả hai | 31 | 0,216 | 0,644 |

| | ΔQWK | ΔAUC |
|---|---|---|
| SẠCH thêm cho LLM | **+0,064 [+0,008, +0,122] p = 0,029** | **+0,088 [+0,033, +0,140] p = 0,003** |
| LLM thêm cho SẠCH | +0,020 [−0,021, +0,064] p = 0,360 | +0,015 [−0,004, +0,035] p = 0,127 |

Bất đối xứng sạch: **ta thêm được cho LLM, LLM không thêm được cho ta.**

### 4.3. Báo trước lỗi của LLM

Mục tiêu là lỗi nguy hiểm: **LLM nói tầng thấp mà giáo viên nói tầng cao**.

| môn | n (tỉ lệ) | AUC |
|---|---:|---:|
| Lý | 231 (15,0%) | **0,764 [0,732, 0,792]** |
| Sử | 142 (11,1%) | 0,623 [0,575, 0,676] |

Ở Lý, AUC 0,764 đủ để gắn cờ *"câu này LLM dễ chấm hụt — xem lại"*. Đây là sản
phẩm dùng được ngay, không cần chờ dữ liệu học sinh.

### 4.4. Điểm vận hành — thứ giáo viên thật sự dùng

Danh sách ngắn các câu **nghi là tầng cao** để rà tay. Precision:

| k | Lý: LLM | Lý: SẠCH | Lý: cả hai | | Sử: LLM | Sử: SẠCH | Sử: cả hai |
|---:|---:|---:|---:|---|---:|---:|---:|
| 25 | 88,0% | 92,0% | **96,0%** | | 36,0% | 32,0% | 32,0% |
| 50 | 78,0% | 92,0% | 92,0% | | 26,0% | 26,0% | 34,0% |
| 100 | 77,0% | 93,0% | **94,0%** | | 17,0% | **31,0%** | 32,0% |
| tất cả tầng cao | 66,7% | 68,6% | 70,8% | | 15,5% | **25,0%** | 27,4% |
| *tỉ lệ nền* | *38,1%* | | | | *13,2%* | | |

Lý: đưa 100 câu thì **94 câu đúng là VD/VDC**, trên nền 38,1%. Sử: 31% trên nền
13,2% — gấp 2,3 lần, hữu ích nhưng không phải máy chấm.

### 4.5. Lặp lại với seed khác

Chạy lại toàn bộ §4 với `--seed 7` (chia fold khác, bootstrap khác):

| | seed 42 | seed 7 |
|---|---|---|
| Lý · SẠCH thêm cho LLM (ΔAUC) | +0,075 p 0,000 | +0,070 p 0,000 |
| Lý · LLM thêm cho SẠCH (ΔQWK) | +0,030 p 0,008 | +0,039 p 0,000 |
| Lý · báo trước lỗi chấm hụt | AUC 0,764 | AUC 0,775 |
| Lý · precision@100 | 94,0% | 94,0% |
| Sử · SẠCH thêm cho LLM (ΔQWK) | +0,064 p 0,029 | +0,089 p 0,004 |
| Sử · LLM thêm cho SẠCH (ΔQWK) | +0,020 p 0,360 | +0,036 p 0,144 |
| Sử · precision@100 | 31,0% | 27,0% |

Mọi kết luận giữ nguyên, kể cả bất đối xứng ở môn Sử (LLM không thêm được gì).

### 4.6. Từ DỰ BÁO sang GIẢI THÍCH — `tools/axis_evidence.py`

Mọi số ở §3–§4 mới là **dự báo**. Một LLM cũng dự báo được, và không ai kiểm
chứng nổi lời nó nói. Muốn phát biểu *"câu này khó VÌ nó đòi 3 bước tính"* theo
nghĩa khoa học thì phải qua ba cửa, và đây là kết quả qua từng cửa.

### Cửa 1 — hiệu ứng có sống sót khi giữ nguyên trục tri thức không?

Khử bằng **thiết kế**, không bằng thống kê: chỉ so các câu **trong cùng một
bài** (53 bài Lý, 29 câu/bài, bài nào cũng đủ 3–4 mức nhãn). Hồi quy hiệu ứng cố
định theo bài:

| cột | β **trong bài** | t | ρ trong | β giữa bài | ρ giữa |
|---|---:|---:|---:|---:|---:|
| `tr_given` | +0,477 | **+23,5** | +0,500 | +0,210 | +0,562 |
| `tr_steps` | +0,641 | **+21,5** | +0,477 | +0,330 | +0,552 |
| `tr_ont_steps_sum` | +0,510 | **+19,9** | +0,473 | +0,274 | +0,590 |
| `tr_n_formula` | +0,753 | **+19,1** | +0,451 | +0,382 | +0,587 |
| `tr_unknowns` | +0,778 | **+16,1** | +0,345 | +0,644 | +0,573 |
| `kad_path_distance_mean` ⟨đối chứng⟩ | −0,274 | −2,34 | **−0,074** | +0,139 | +0,033 |

Hệ số **trong bài lớn hơn giữa bài** (0,641 vs 0,330) ⇒ hiệu ứng **không** phải
bí danh của "chủ đề khó". Đây là điều tương quan thô không nói được.

### Cửa 2 — thiết kế có giết được một yếu tố ta biết là sai không?

Nếu thiết kế làm yếu tố nào cũng "đúng" thì nó vô dụng. Cặp cùng bài chênh ≥ 1
độ lệch chuẩn, hỏi: câu có giá trị cao hơn có được giáo viên gán mức cao hơn?

| cột | thắng | thua | tỉ lệ | p |
|---|---:|---:|---:|---:|
| `tr_given` | 4.477 | 257 | **94,6%** | ≈ 0 |
| `tr_steps` | 5.349 | 561 | **90,5%** | ≈ 0 |
| `tr_n_formula` | 4.914 | 571 | 89,6% | ≈ 0 |
| `tr_unknowns` | 3.481 | 458 | 88,4% | ≈ 0 |
| `kad_path_distance_mean` ⟨đối chứng⟩ | 492 | 690 | **41,6%** | 9,3e−9 |
| **XÁO ngẫu nhiên** ⟨đối chứng⟩ | 3.570 | 3.477 | **50,7%** | 0,27 |

Hai dòng đối chứng làm đúng việc của chúng: cột xáo ngẫu nhiên **không** qua
được (50,7%, p = 0,27) ⇒ thiết kế không tự sinh ra kết quả. Còn đại lượng Vinu
thì **41,6% — dưới 50% có ý nghĩa**: quan hệ có thật nhưng **ngược dấu** giả
thuyết. Đáp án càng xa nhiễu thì càng *dễ*, không phải càng khó. Đây là lần thứ
ba giả thuyết Vinu bị bác bỏ bằng một thiết kế độc lập.

### Cửa 3 — lời giải thích của mô hình có đúng lượng không?

Can thiệp **trên manifold**, không bịa giá trị: lấy 3.198 cặp câu **cùng bài**
chênh ≥ 2 bước, ghép khối đặc trưng của câu **ít bước** vào câu **nhiều bước**,
rồi so ΔE[y] của mô hình với chênh **nhãn thật** của đúng hai câu đó.

| khối bị hoán đổi | ΔE[y] mô hình | Δ nhãn thật | phần giải thích |
|---|---:|---:|---:|
| TOÀN BỘ đặc trưng (mốc trên) | −1,312 | −1,470 | **89%** |
| **thao tác (vết giải)** | −0,323 | −1,470 | **22%** |
| `kad_path_distance_mean` ⟨đối chứng⟩ | −0,011 | −1,470 | **1%** |

Ba con số này nói ba điều khác nhau, và cả ba đều cần:

- **89%** — thay toàn bộ đặc trưng thì mô hình dịch chuyển gần đúng bằng nhãn
  thật dịch chuyển. Mô hình **hiệu chỉnh tốt ở mức từng câu**, không chỉ đúng
  trung bình.
- **22%** (tức **25%** phản ứng của mô hình) — đó là **tỉ trọng thật** của trục
  thao tác trong lời giải thích. Không phải "gần 1 nên trung thực", mà là một
  phép **phân rã có đơn vị**: trục thao tác giải thích được ngần này khoảng cách
  độ khó giữa hai câu cùng bài.
- **1%** — mô hình **không bịa** hiệu ứng cho yếu tố đã bị bác bỏ. Đây là điều
  quy kết SHAP không bảo đảm: SHAP luôn chia hết 100% cho các cột, kể cả cột vô
  nghĩa (xem [XAI_DIAGNOSIS.md](XAI_DIAGNOSIS.md) §3).

⚠️ Cách đọc sai mà tôi suýt mắc: coi tỉ lệ 0,22 là "mô hình không trung thực".
Sai — chênh nhãn −1,47 là chênh **toàn phần** giữa hai câu, còn mỗi dòng chỉ
hoán đổi **một khối**. Tỉ lệ ở đây là **phần đóng góp**, phải đọc cùng mốc trên.

### Vì sao ba cửa này mới là đóng góp XAI

Một LLM trả lời "VDC" thì **không phép nào ở trên áp dụng được cho nó**: không
khử được nhiễu chủ đề khỏi lời nó nói, không có đối chứng để giết lời nói sai,
không can thiệp được vào "lí do" của nó để đo. Đề tài không hơn LLM ở con số dự
báo (§4.1: QWK 0,531 so với 0,540) — nó hơn ở chỗ **mọi phát biểu của nó đều
đứng trước một phép bác bỏ**, và một phát biểu đã thật sự bị bác bỏ ba lần
(giả thuyết Vinu).

### 4.7. Áp ba cửa cho TRỤC TRI THỨC — và một dấu hiệu đổi chiều theo môn

`tools/axis_evidence.py` tổng quát hoá §4.6 cho mọi trục. Với trục tri thức,
biến gây nhiễu cần khử là **tải thao tác**, nên nhóm đối sánh chặt hơn: ô
**bài × số bước** (Lý: 128 ô). Môn Sử không có vết giải nên lùi về cùng bài
(34 nhóm).

Ghi chú: tôi từng nói centrality "gần như cố định trong một bài" nên không dùng
được thiết kế này. **Sai** — ICC theo bài chỉ **0,149** (Lý) và **0,052** (Sử),
tức 85–95% biến thiên nằm TRONG bài. Thiết kế dùng được.

| trục tri thức, cửa 1 | β trong nhóm | t | ρ trong | ρ giữa nhóm |
|---|---:|---:|---:|---:|
| **Lý** `kg_centrality_mean` | **−0,084** | **−3,22** | −0,067 | **−0,759** |
| **Lý** `kg_entity_match_coverage` | −0,096 | −3,57 | −0,078 | −0,745 |
| **Lý** `kg_num_correct` | −0,074 | −2,98 | −0,070 | −0,757 |
| **Sử** `kg_centrality_mean` | **+0,069** | **+2,87** | **+0,201** | +0,240 |
| **Sử** `kg_entity_match_coverage` | +0,058 | +2,29 | +0,113 | +0,116 |
| **Sử** `kg_num_correct` | +0,020 | +0,79 | +0,050 | +0,204 |

Cặp ghép cùng nhóm xác nhận, và **ngược chiều nhau**:

| | Lý | Sử |
|---|---:|---:|
| `kg_centrality_mean` | **44,7%** (p 6e−10) | **66,1%** (p 2e−96) |
| XÁO ngẫu nhiên ⟨đối chứng⟩ | 50,7% (p 0,27) ✔ trượt | 48,5% (p 0,053) ✔ trượt |

**Đây là kết quả đáng kể nhất của mục này: trục tri thức ĐỔI DẤU theo môn.**

- **Sử**: khái niệm càng ở vùng liên kết dày ⇒ càng **khó**. Nhân vật, sự kiện
  trung tâm là thứ được hỏi ở tầng phân tích, đánh giá.
- **Lý**: khái niệm càng trung tâm ⇒ càng **dễ**. Định luật Ôm, công suất là nền
  móng, được hỏi ở tầng nhận biết; câu VD/VDC là tình huống riêng lẻ, chạm vào
  ít thực thể và toàn thực thể ngoại vi. Tương quan **giữa các bài** còn mạnh
  hơn nhiều (ρ ≈ **−0,75**).

Hệ quả cho lí thuyết hai trục: *"vị trí trong đồ thị góp phần vào độ khó"* là
phát biểu **đúng nhưng chưa đủ** — **chiều** của nó phụ thuộc môn. Một hệ dùng
chung một dấu cho mọi môn sẽ sai ở một nửa số môn. Đây là điều tương quan gộp
hai môn lại sẽ che mất.

Cửa 3 (can thiệp trên manifold):

| | Δnhãn thật | mốc trên | khối tri thức | Vinu ⟨đối chứng⟩ |
|---|---:|---:|---:|---:|
| Sử | −0,226 | 100,0% | **62,5%** | **1,8%** |
| Lý | +0,119 | 37,7% | −47,3% | −9,4% |

Ở Sử, trục tri thức giải thích **62,5%** khoảng cách độ khó giữa hai câu cùng
bài — mạnh hơn nhiều so với trục thao tác ở Lý (17,5%). Ở Lý thì Δnhãn thật chỉ
+0,119: khống chế xong bài **và** số bước thì trục tri thức gần như không còn
liên hệ với nhãn, nên mọi tỉ lệ ở dòng đó **không đọc được** — và chính điều đó
là kết quả.

⚠️ **Một đối chứng KHÔNG trượt, phải nói rõ.** Ở Sử, `kad_path_distance_mean`
qua được cửa 2 (60,1%, p 6e−11). Lí do gần như chắc chắn là **chọn mẫu**: đại
lượng này chỉ tính được cho 517/1.276 câu (cần cả đáp án lẫn nhiễu có thực thể
trong đồ thị), nên nó chạy trên một mẫu con đã bị chọn lọc, khác mẫu của các cột
kia. Đối chứng chạy trên **toàn mẫu** — cột xáo ngẫu nhiên — thì trượt đúng như
phải thế (48,5%). Nhưng chừng nào chưa tách được hai khả năng này thì **không
được dùng cửa 2 ở môn Sử để tuyên bố bác bỏ Vinu**; ba bằng chứng bác bỏ khác
(`counterfactual_validity`, hồi quy hop có kiểm soát, cửa 2 ở môn Lý 41,6%) vẫn
đứng độc lập.

## 5. Chốt

0. **Đóng góp không phải "dự báo tốt hơn LLM" mà là "phát biểu kiểm chứng được".**
   Ba cửa ở §4.6 — khử nhiễu bằng thiết kế, đối chứng giết được yếu tố sai, can
   thiệp trên manifold để phân rã có đơn vị — áp được cho hệ này và **không áp
   được cho một LLM**. Trục thao tác (Lý) qua cả ba: t = +21,5 trong bài; 90,5%
   cặp cùng bài; 17,5% khoảng cách nhãn (mốc trên 87,7%).
0b. **Trục tri thức ĐỔI DẤU theo môn** (§4.7): Sử ρ trong nhóm **+0,201**, cặp
   ghép 66,1%, giải thích **62,5%** khoảng cách nhãn — càng trung tâm càng KHÓ.
   Lý thì ngược: t **−3,22**, cặp ghép **44,7%**, ρ giữa bài **−0,75** — càng
   trung tâm càng DỄ. Vậy *"vị trí trong đồ thị góp phần vào độ khó"* là phát
   biểu đúng nhưng **chưa đủ**: dùng chung một dấu cho mọi môn sẽ sai ở một nửa
   số môn. Gộp hai môn lại rồi tính tương quan sẽ che mất điều này.
1. **Trục thao tác đo được, nhưng dụng cụ phụ thuộc môn.** Ở môn tự nhiên, thao
   tác là một phép tính có vết: nó để lại dấu trong đồ thị tiên quyết, trong
   `applicationSteps`, và trong tiến trình giải. Ở môn xã hội, đồ thị hiện tại
   không mang thông tin đó và không có gì thay thế — bằng chứng là AUC 0,495.
2. **Đóng góp thật của ontology đã định vị được**: không phải khoảng cách
   đáp án↔nhiễu (Vinu, đã bác bỏ), mà là (a) `kg_centrality_mean` — vị trí trong
   mạng liên kết, ρ ≈ +0,24 và **bền với cả hai nguồn nhãn**; (b) ở môn tự
   nhiên, `applicationSteps` trên đồ thị tiên quyết, mở khoá được nhờ LLM liên
   kết công thức.
3. **Chỗ đứng so với "hỏi thẳng LLM"**: không cạnh tranh ở việc gán nhãn, mà
   thắng ở **đúng chỗ LLM hỏng** — tầng cao. AUC +0,075 (p = 0,000) ở Lý,
   +0,088 (p = 0,003) ở Sử, recall VDC gần gấp ba.
4. **Vị thế thực tế theo môn.** Lý: hệ gợi ý 4 mức dùng được, kèm cờ cảnh báo
   lỗi LLM (AUC 0,764) và danh sách ngắn 94% chính xác. Sử: đèn sàng lọc nhị
   phân, gấp 2,3 lần tỉ lệ nền — **không** dùng thay phán đoán giáo viên.

## 6. Việc mở, xếp theo đòn bẩy

- **Làm dày `prerequisiteOf` cho Lý** — 216 cạnh / 319 thực thể, chỉ phủ 18,6%.
  Đây là khoản đầu tư duy nhất đã có số đo chứng minh sẽ trả lãi.
- **Sửa `relatesQuantities`** — hiện 32 triple cho 32 công thức, tức **1 đại
  lượng mỗi công thức**, trong khi `U = I·R` phải liên hệ cả U, I, R. Sửa xong
  mới dựng được đồ thị hai phía công thức↔đại lượng, và khi đó "số bước xử lý" =
  số công thức phải nối từ đại lượng đã cho tới đại lượng phải tìm.
- **Cân số cột giữa các nhóm** trước khi so quy kết chiếm chỗ (xem
  [XAI_DIAGNOSIS.md](XAI_DIAGNOSIS.md) §3).
- Môn Sử cần **loại cạnh khác hẳn** (cấu trúc lập luận), không phải thêm cạnh
  chủ đề. Chưa có phương án đã kiểm chứng.
