# Pipeline XAI giải thích độ khó — dẫn bằng CAN THIỆP

Công cụ: `tools/xai_difficulty.py`
Kết quả kiểm tra chéo: `subjects/physics/samples/xai_validate.json`,
`subjects/history/samples/xai_validate_gv.json`

> **Tài liệu này mô tả pipeline dưới MÔ HÌNH NỀN CŨ** — XGBoost trên 15 cột đặc
> trưng viết tay (`QDE_BACKEND=xgb15`, mặc định). Mọi con số trong các mục dưới
> đây là của mô hình đó.
>
> Từ 24/09/2026 pipeline chạy được trên **bốn** mô hình nền (`xgb15` · `tfidf` ·
> `text` · `emb`), trải từ 0 % tới 100 % khối lượng quyết định nằm ngoài cột đặt
> tên được. **Pipeline giữ nguyên, nhiều con số đổi, và một kết luận về cơ chế
> ĐỔI DẤU — nhưng đổi dấu theo một quy luật đo được.** Xem §10,
> `docs/BACKEND_CURVE.md` và `docs/MODEL_UPGRADE.md`. Chỗ nào số phụ thuộc mô
> hình nền, mục đó có ghi chú dẫn sang §10.

---

## 0. Vấn đề

### 0a. Vì sao đề tài là GIẢI THÍCH, không phải DỰ ĐOÁN

Bài toán *ước lượng* độ khó cần ground truth là tỉ lệ trả lời đúng của học sinh
thật. Ở đề tài này nguồn đó bị chặn — khảo sát T1 không được duyệt — và không
có cách nào lách: mọi thay thế (nhãn giáo viên, nhãn LLM) đều là một construct
khác, không phải độ khó thực nghiệm.

Bài toán *giải thích* không vướng chỗ đó. Đối tượng được giải thích là **dự
đoán của mô hình**, và tính đúng đắn của lời giải thích được chứng minh bằng
**can thiệp** — sửa đúng một thứ rồi xem dự đoán có dịch không — chứ không bằng
việc khớp với phán đoán của người. Nghĩa là thí nghiệm phản thực thay được cho
user study với giáo viên, nguồn lực cũng đang bị chặn.

Đây là lý do đề tài chuyển trục sang XAI: **không phải vì dự đoán thất bại, mà
vì giải thích là câu hỏi kiểm chứng được bằng tài nguyên đang có.**

Cái giá phải khai báo, và phải khai báo sớm chứ không để xuống phần giới hạn:
vấn đề ground truth không biến mất, nó **đổi chỗ**. Mô hình học nhãn *mức nhận
thức do giáo viên gán theo ma trận đề*, nên lời giải thích trả lời câu **"cái
gì khiến câu này được xếp mức cao trên thang NB/TH/VD/VDC"**, không phải "cái
gì khiến học sinh làm sai". Đó là một construct có thật và đáng nghiên cứu —
nó quyết định đề thi trông thế nào trong thực tế — nhưng nó không phải độ khó
thực nghiệm. Xem §9 cho danh sách đầy đủ những gì pipeline này KHÔNG làm được.

### 0b. Vì sao không dùng thẳng quy kết đặc trưng

Cách làm mặc định của ngành là **quy kết đặc trưng** (feature attribution — SHAP, LIME): với mỗi câu, gán cho mỗi đặc trưng
một con số nói nó đóng góp bao nhiêu vào dự đoán.

Nhưng quy kết trả lời câu hỏi *"mô hình dựa vào gì"*, và nó trả lời bằng cách
**tính từ cấu trúc cây**, không phải bằng cách thử. Trong chính bộ dữ liệu này,
tương quan giữa "SHAP gán bao nhiêu cho một trục" và "can thiệp lên trục đó
thực sự làm dự đoán đổi bao nhiêu" là:

| nhánh can thiệp | rho | p |
|---|---:|---:|
| Lý · `num_down` | −0,051 | 0,21 |
| Lý · `kg_near` | +0,005 | 0,91 |
| Lý · `kg_far` | −0,008 | 0,83 |
| Sử · `len_down` | −0,043 | 0,12 |
| Sử · `kg_near` | −0,090 | 0,06 |
| Sử · `kg_far` | −0,044 | 0,29 |

Quy kết và phản ứng thật gần như độc lập. Nên pipeline này đổi câu hỏi: không
hỏi *"mô hình dựa vào gì"* mà hỏi **"nếu sửa đúng một thứ ở câu này, độ khó dự
đoán có đổi không, và đổi bao nhiêu so với mức nhiễu"**.

---

## 1. Sơ đồ

```
B0  dữ liệu → đặc trưng → mô hình out-of-fold
      ↓
B1  CHỨNG CHỈ TRỤC          quần thể: trục nào ĐƯỢC PHÉP nêu tên
      ↓
B2  CAN THIỆP TỪNG CÂU      sửa 1 phương án THẬT, lặp R lần, đo |Δ E[y]|
      ↓
B3  ĐỐI CHỨNG GHÉP CẶP      cùng ô, cùng ràng buộc → sàn nhiễu của chính câu đó
      ↓
B4  QUY KẾT CÓ KIỂM CHỨNG   net = |Δ| − sàn, chuẩn hoá; SHAP tụt xuống đối chiếu
      ↓
B5  PHÁT NGÔN               3 cửa mới được nêu tên; có quyền nói KHÔNG QUY ĐƯỢC
      ↓
KIỂM TRA CHÉO               chia R lần lặp làm 2 nửa: lời giải thích có lặp lại?
```

Chạy:

```bash
python tools/xai_difficulty.py --step 1 --subject physics
python tools/xai_difficulty.py --step 2 --subject physics --id kgv_0138 --reps 24
python tools/xai_difficulty.py --step all --subject history_gv --n 3
python tools/xai_difficulty.py --validate --subject physics --n 150 --reps 16
python tools/xai_difficulty.py --coverage --subject physics --out subjects/physics/samples/xai_coverage.json
```

---

## 2. B1 — Chứng chỉ trục

**Làm gì.** Trước khi cho phép hệ thống nói *"câu này khó vì trục X"*, bắt trục
X chứng minh ở mức quần thể rằng nó có tác dụng thật. Trục trượt cửa này thì
vĩnh viễn không được nêu tên trong bất kỳ lời giải thích từng câu nào.

**Hai điều kiện, phải đủ cả hai.**

1. `p < 0,05` khi so với nhánh đối chứng khớp
2. dịch **đúng hướng đã hứa trước khi đo** — hướng phải viết ra trước, không
   được chọn sau khi nhìn số

Điều kiện 2 là cái ngăn "trục có ý nghĩa thống kê nhưng chạy ngược" lọt qua.

> ⚠️ Hai điều kiện này **không đủ** — xem §2b: chúng cấp chứng chỉ cho 30/39 (Lý),
> 27/39 (Sử) mô hình học trên nhãn xáo. Cổng hiện hành thêm điều kiện thứ ba (vượt
> mô hình nhãn xáo, p hoán vị < 0,05, ở mọi seed) và xét **theo nhánh**, không
> theo trục. Bảng dưới là kết quả theo hai điều kiện gốc.

**Kết quả.**

| môn | trục | nhánh | vượt đối chứng | p | kết |
|---|---|---|---:|---:|---|
| Lý | BỀ MẶT | `num_down` | −0,1566 | 2,9e−28 | **ĐẠT** |
| Lý | BỀ MẶT | `num_up` | +0,0941 | 7,3e−21 | **ĐẠT** |
| Lý | TRI THỨC | `kg_near` | −0,0423 | 0,044 | trượt — *ngược hướng* |
| Lý | TRI THỨC | `kg_far` | +0,0022 | 0,65 | trượt — không có |
| Sử | BỀ MẶT | `len_down` | −0,0679 | 1,8e−17 | **ĐẠT** |
| Sử | BỀ MẶT | `len_up` | +0,0726 | 2,0e−25 | **ĐẠT** |
| Sử | TRI THỨC | `kg_near` | +0,0191 | 0,10 | trượt |
| Sử | TRI THỨC | `kg_far` | +0,0054 | 0,95 | trượt |

Trục bề mặt đạt **cả hai chiều** ở cả hai môn — đây là **đối chứng dương** của
chính phép đo: nếu ngay cả trục đã biết là mạnh cũng không bắt được thì phép
đo hỏng, chứ không phải KG hỏng.

Trục tri thức trượt ở cả hai môn, hai nguồn nhãn. Ở môn Lý nó trượt theo kiểu
đáng chú ý: `kg_near` **có** ý nghĩa thống kê (p=0,044) nhưng **dấu ngược** —
nhiễu gần đáp án hơn làm câu *dễ đi*, trái với giả thuyết Vinu 2015.

Hệ quả trực tiếp: **trục tri thức bị cấm nêu tên trong lời giải thích từng câu**
ở cả hai môn. Không phải do quyết định của người viết, mà do nó trượt bài kiểm
tra của chính nó.

---

## 2b. Kiểm tra tỉnh táo cho cổng B1 — luật ở §2 KHÔNG qua

`python tools/xai_sanity.py` → `docs/xai_sanity.json` (84 lần chạy phản thực,
~17 phút song song).

**Câu hỏi.** Cổng chứng chỉ đáng tin phải **trượt** khi mô hình không học được
gì. Phép thử chuẩn (Adebayo et al. 2018, *data randomization test*): xáo ngẫu
nhiên nhãn, huấn luyện lại, chạy lại toàn bộ phản thực, rồi chấm bằng đúng hàm
`certificate()`. Làm 39 lần mỗi môn. Kèm theo: chạy dữ liệu thật với 3 seed khác
(đổi cách chia lát, khởi tạo mô hình, cách rút donor).

> Ở ba mô hình nền văn bản, loạt này chạy lại với `QDE_DONOR_SEED=42` (một bộ
> phản thực dùng chung cho cả 84 lần chạy — phân bố rỗng hẹp lại, phép kiểm
> **chặt hơn**). Kết cục đổi và đổi theo hướng ngược nhau giữa hai môn: **Lý
> trượt luật CHẶT ở `xgb15` rồi qua ở cả ba mô hình văn bản; Sử thì ngược lại.**
> Và một ca suýt lọt đáng nhớ: dưới `tfidf`, nhánh `kg_near` của Lý QUA luật §2
> gốc (Wilcoxon p = 0,022, đúng hướng) nhưng p hoán vị = 0,150 — **cổng hoán vị
> là thứ giữ kết luận trung tâm của đề tài đứng yên khi đổi mô hình nền.**
> Xem §10.1 và `docs/BACKEND_CURVE.md` §2.

**Kết quả: luật §2 trượt nặng.**

| cấp chứng chỉ cho mô hình học trên NHÃN XÁO (mỗi mô hình so với 38 còn lại) | Lý | Sử |
|---|---:|---:|
| luật §2 — một nhánh bất kỳ, Wilcoxon p < 0,05 + đúng hướng | **30/39** | **27/39** |
| luật CHẶT — MỌI nhánh, thêm điều kiện vượt mô hình nhãn xáo (p hoán vị < 0,05) | 0/39 | 0/39 |
| theo NHÁNH — nhánh nào vượt đối chứng, đúng hướng, vượt nhãn xáo | 3/39 (mỗi nhánh 0–1/39) | 4/39 (mỗi nhánh 1/39) |

Vì sao luật §2 hỏng: Wilcoxon trên 600–1.300 cặp thì mọi phản ứng có hệ thống
của mô hình đều "có ý nghĩa" — kể cả của một mô hình học thuộc nhãn ngẫu nhiên,
vì nó vẫn phải dựa vào đặc trưng nào đó. Còn "đúng hướng" với mô hình ngẫu nhiên
là tung đồng xu, lại có hai nhánh để thử. So với **đối chứng giả dược** là cần
nhưng chưa đủ; phải so với **mô hình không học được gì**.

**Dữ liệu thật dưới luật hiệu chỉnh.** p hoán vị = (1 + số mô hình xáo có hiệu
ứng theo hướng hứa ≥ thật) / 40 — 0,025 nghĩa là vượt cả 39 mô hình xáo.

| nhánh | hứa | seed 42 | 43 | 44 | 45 |
|---|---|---:|---:|---:|---:|
| Lý `num_down` (bớt số) | dễ đi | **0,025** | **0,025** | **0,025** | **0,025** |
| Lý `num_up` (thêm số) | khó lên | 0,100 | 0,100 | 0,100 | 0,100 |
| Sử `len_down` (rút ngắn) | dễ đi | **0,025** | **0,025** | **0,025** | **0,025** |
| Sử `len_up` (kéo dài) | khó lên | **0,025** | 0,050 | 0,050 | 0,100 |
| TRI THỨC (4 nhánh, hai môn) | | 0,33–0,78 | 0,33–0,83 | 0,33–0,60 | 0,40–0,85 |

Đọc: chiều **BỚT** — bớt con số / rút ngắn phương án làm hệ xếp câu thấp đi —
vượt **mọi** mô hình nhãn xáo, ở cả hai môn, cả bốn seed. Chiều **THÊM** thì
không phân biệt được với một mô hình học nhãn ngẫu nhiên (Lý), hoặc bấp bênh
theo seed (Sử). Trục TRI THỨC trượt ở mọi luật — kết luận đó không đổi.

**Hệ quả cho cổng — ĐÃ CHỐT (11/09/2026): cổng THEO NHÁNH.**

- Luật CHẶT được định ra **trước** khi chạy K = 39. Theo nó, môn Lý **không còn
  trục nào** được nêu tên; môn Sử chỉ đạt ở 1/4 seed. Không chọn.
- Luật **theo NHÁNH** — chọn. Chỉ những nhánh đạt hiệu chỉnh ở **mọi** seed mới
  được góp vào lời giải thích từng câu: **Lý `num_down`, Sử `len_down`**. Cấp
  nhầm từng nhánh 0–1/39. Luật này được chọn **sau** khi thấy số — khi viết phải
  khai báo đúng như vậy, kèm kết quả của luật CHẶT.
- Mã: `GATE = "arms"` trong `xai_difficulty.py`; `allowed_arms()` quyết định
  nhánh nào được gộp vào điểm từng câu (B4), vào lời phát ngôn (B5) và vào lời
  khuyên sửa đề (§8b.3). Kiểm tra chéo (§7) **không** đổi — nó đo độ ổn định
  của phép đo, không phụ thuộc cổng.
- **Cái giá phải khai: độ phủ.** Trục BỀ MẶT giờ chỉ nói được ở câu dựng được
  nhánh đạt chứng chỉ: Lý 39,2% số câu (câu có phương án chứa con số để bớt),
  Sử 99,7%. Với 60,8% số câu Lý còn lại, hệ trả *KHÔNG QUY ĐƯỢC* — đúng như
  nó phải trả.

---

## 3. B2 — Can thiệp từng câu

**Thay bằng văn bản thật, không cộng số vào cột.** Cộng +1 vào một cột đặc
trưng tạo ra một câu không tồn tại trên đời; mô hình chưa từng thấy vùng đó và
Δ đo được là ảo. Ở đây mỗi can thiệp thay đúng **một** phương án nhiễu bằng
một nhiễu **có thật** lấy từ câu khác trong bộ, nên câu phản thực vẫn nằm
trong phân phối.

**Lặp R lần.** Một lần thay là *một* mẫu ngẫu nhiên trong vô số cách thay.
Không lặp thì đo được sự may rủi của một donor cụ thể, không phải sức nặng của
trục.

> **R = 12 là THIẾU LỰC — đã đo.** Câu `kgv_0138` ở 12 lần/nhánh cho
> `KHÔNG QUY ĐƯỢC` (trục bề mặt p = 0,080); ở 24 lần/nhánh cùng câu đó, cùng
> đối chứng ghép cặp, cho `QUY ĐƯỢC — trục BỀ MẶT` (p = 0,016). Phán quyết
> **lật** chỉ vì số lần lặp. Mặc định đã đổi thành `--reps 24`. Khi báo cáo một
> câu cụ thể nên chạy 24 trở lên, và nên ghi rõ R đã dùng — một phán quyết
> `KHÔNG QUY ĐƯỢC` ở R thấp không phải bằng chứng rằng trục không có tác dụng,
> chỉ là chưa đủ lực để thấy.

**Mô hình out-of-fold.** Câu đang chẩn đoán chưa bao giờ nằm trong tập huấn
luyện của mô hình đang chấm nó. Nếu không thì phản ứng đo được chỉ là mô hình
nhớ lại chính nó.

---

## 4. B3 — Đối chứng ghép cặp

Thay bất cứ phương án nào cũng làm dự đoán nhúc nhích. Nhìn |Δ| thô rồi kết
luận "trục này mạnh" là tính cả phần nhúc nhích do *hành động thay*, không
phải do *trục*.

Mỗi lần can thiệp đều kèm ngay một đối chứng: thay **đúng ô vừa bị động vào**,
donor khớp độ dài (±45%) và khớp việc có số hay không — chỉ khác đúng thuộc
tính đang muốn đo. Với hai nhánh KG, donor đối chứng còn buộc phải có thực thể,
vì một donor không thực thể nào tự nó đã là một can thiệp KG.

> **Lỗi đã sửa.** Bản đầu dùng nhánh giả dược dựng sẵn trong
> `counterfactual_validity.py`, nhưng nhánh đó luôn thay ô số 0 trong khi
> `num_up` thay ô không-có-số đầu tiên. Hai ô khác nhau thì hiệu số vô nghĩa.
> Đối chứng phải khớp cả **vị trí**, không chỉ khớp thuộc tính.

Ghép cặp còn cho kiểm định mạnh hơn: `ttest_rel` trên |Δ can thiệp| − |Δ đối
chứng| của từng cặp, thay vì so hai nhóm rời.

---

## 4b. Độ phủ — trục nào đo được ở bao nhiêu câu

Không phải câu nào cũng dựng được phản thực cho mọi nhánh: `num_down` cần câu
có sẵn một nhiễu chứa số, `kg_near` cần trong kho donor có nhiễu chứa thực thể
cách đáp án đúng 1 hop, v.v.

| nhánh | Lý (1.539 câu) | Sử (1.276 câu) |
|---|---:|---:|
| `num_down` / `len_down` | 39,2% | 99,7% |
| `num_up` / `len_up` | 68,7% | 99,8% |
| `kg_near` | 30,5% | 33,9% |
| `kg_far` | 41,1% | 46,5% |
| **trục BỀ MẶT (ít nhất 1 nhánh)** | 100,0% | 100,0% |
| **trục TRI THỨC (ít nhất 1 nhánh)** | **41,1%** | **46,5%** |

Số trong bảng sinh bởi `--coverage`, lưu ở `xai_coverage*.json`, và bị buộc
trong bảng đóng băng (`tools/reproduce_all.py --check`).

**Trục tri thức chỉ đo được ở dưới một nửa số câu.** Với phần còn lại, phán
quyết đúng là *"chưa biết"*, không phải *"đã kiểm tra và không thấy tác dụng"*.
Công cụ phân biệt hai trường hợp này bằng dòng:

```
! trục TRI THỨC KHÔNG đo được ở câu này — không có donor hợp lệ để dựng
  phản thực. Đây là 'chưa biết', KHÔNG phải 'đã kiểm tra và thấy không có
  tác dụng'.
```

Hai hệ quả phải nêu khi báo cáo:

1. **Chọn mẫu.** Tập câu đo được trục KG là tập câu *có nhắc thực thể trong
   ontology*, tức đã lệch về phía câu bám sát chương trình. Kết luận về trục KG
   chỉ có giá trị trên tập đó, không suy rộng ra cả bộ.
2. **Độ phủ ≠ độ mạnh.** `kg_near` ⊂ `kg_far` ở cả hai môn (dựng được `near`
   thì luôn dựng được `far`), nên độ phủ của trục KG bị chặn bởi `kg_far`.

---

## 5. B4 — Quy kết có kiểm chứng

Ví dụ câu `kgv_0138` ("Vật kính của máy ảnh sử dụng:"), 24 lần/nhánh:

| trục | \|Δ\| trục | sàn nhiễu | còn lại | p | tỉ trọng | SHAP nói |
|---|---:|---:|---:|---:|---:|---:|
| BỀ MẶT | 0,574 | 0,435 | **0,140** | 0,016 | 56% | **18%** |
| TRI THỨC | 0,210 | 0,100 | 0,109 | 0,000 | 44% | **82%** |

Con số thô 0,574 gần như hoàn toàn là sàn nhiễu; phần thật của trục chỉ 0,140.

Cột "SHAP nói" giữ lại **không phải để dùng** mà để người đọc thấy khoảng lệch:
SHAP dành 82% cho trục tri thức, can thiệp cho 44% — gần như đảo ngược, trên
cùng một câu, cùng một mô hình.

⚠️ *Bảng trên đo trục BỀ MẶT trên **cả hai nhánh**, trước khi chốt cổng theo
nhánh (§2b). Dưới cổng hiện hành câu này ra* **KHÔNG QUY ĐƯỢC**: *không phương
án nào chứa con số để bớt, nên nhánh duy nhất được phép (`num_down`) không dựng
được; phần 0,140 ở trên đến từ `num_up` — chiều chưa qua được mô hình nhãn xáo.
Ví dụ vẫn giữ để minh hoạ cơ chế B2–B4 (sàn nhiễu, SHAP lệch), không phải để
minh hoạ một lời giải thích được phép phát ngôn.*

---

## 6. B5 — Phát ngôn, và quyền im lặng

Một trục chỉ được nêu tên khi qua **đủ ba cửa**:

1. đạt chứng chỉ ở B1 — trục có thật ở mức quần thể
2. `p < 0,05` ở B2-vs-B3 — trục lay chuyển được **chính câu này**
3. `net ≥ 0,02` mức — dịch chuyển đủ lớn để đáng nói

Bốn phán quyết có thể xảy ra:

| phán quyết | khi nào |
|---|---|
| `QUY ĐƯỢC` | một trục qua ba cửa và trội gấp đôi trục còn lại |
| `QUY ĐƯỢC (chia)` | hai trục cùng qua, không trục nào trội hẳn |
| `KHÔNG QUY ĐƯỢC` | không trục nào qua — độ khó nằm ngoài các trục đang đo |
| `KHÔNG KẾT LUẬN` | entropy dự đoán ≥ 0,80, quá bất định để giải thích |

**Vì sao cần đường thoát.** Một hệ giải thích mà câu nào cũng giải thích được
là một hệ không kiểm chứng được. SHAP luôn trả về một con số, kể cả khi mô
hình chẳng phản ứng gì với bất cứ can thiệp nào.

**Không chặn im lặng.** Trục trượt chứng chỉ nhưng vẫn lay chuyển được câu thì
phải nói ra, dưới dạng một dòng riêng:

```
◦ trục TRI THỨC CÓ lay chuyển câu này (0.109 mức, p=0.000) nhưng KHÔNG
  được nêu làm nguyên nhân: ở B1 trục này trượt chứng chỉ.
  Mô hình vẫn dùng khối đặc trưng đó, nhưng như một dấu hiệu KHÁC với
  ý nghĩa được gán cho nó — hướng khớp lời hứa chỉ 29% số lần.
```

Khối KG **có** tác dụng lên dự đoán. Nó chỉ không có tác dụng theo nghĩa mà
giả thuyết gán cho nó. Đọc nó như *"câu này có nhắc khái niệm trong chương
trình không"*, không phải *"các phương án dễ nhầm tới mức nào"*.

---

## 7. Kiểm tra chéo — lời giải thích có lặp lại được không

Chia R lần lặp thành hai nửa dùng donor **khác nhau hoàn toàn**. Ước lượng độ
nghiêng của câu (`net` bề mặt − `net` tri thức) ở nửa A, xem nó dự báo nửa B
được không. Rồi hỏi cùng câu đó với SHAP.

| | Lý (150 câu) | Sử (150 câu) |
|---|---:|---:|
| (a) can thiệp nửa A → nửa B | **+0,722** [0,62; 0,81] | **+0,733** [0,62; 0,81] |
| độ tin cậy lời giải thích dùng đủ R lần lặp (Spearman–Brown) | **0,84** | **0,85** |
| trần cho mọi đại lượng dự báo nửa B = √(a) | 0,850 | 0,856 |
| (b) SHAP cây (lề log-odds từng lớp, path-dependent) → nửa B | +0,297 [0,15; 0,43] | −0,088 [−0,26; 0,08] |
| (c) Shapley theo khối trên E[y], nghĩa can thiệp → nửa B | +0,224 [0,07; 0,37] | +0,028 [−0,13; 0,20] |
| (b) đạt bao nhiêu % trần | **35%** [18%; 51%] | ≈ 0% (−10% [−30%; 9%]) |
| (c) đạt bao nhiêu % trần | 26% [8%; 43%] | 3% [−16%; 23%] |

Khoảng tin cậy 95%: bootstrap 2.000 lần theo câu. Công cụ:
`python tools/xai_difficulty.py --validate --subject physics --n 150 --reps 16`.

> Dòng (b) và (c) **không sống sót khi đổi mô hình nền**: dưới mô hình văn bản,
> (b) ở Lý rơi từ +0,297 về −0,050. Dòng (a) — độ lặp lại của lớp can thiệp —
> thì sống sót (0,722 → 0,705). Xem §10.2.

**(a) là độ lặp lại, KHÔNG phải trần.** Nửa B là một phép đo có nhiễu, độ tin
cậy ≈ 0,72–0,73. Theo lý thuyết đo lường cổ điển, một đại lượng *không nhiễu*
tương quan với nửa B tối đa ở √0,72 ≈ 0,85 — đó mới là trần. Lời giải thích dùng
đủ R lần lặp có độ tin cậy Spearman–Brown **0,84–0,85**, tức ước lượng từng câu
**ổn định thật**.

⚠️ *Đính chính (09/2026): bản trước lấy (a) làm trần và ghi "SHAP đạt 41%". Trần
đó quá thấp nên con số nghiêng có lợi cho SHAP; tính đúng là 35%.*

**(b)(c) là kết quả chính.** Ở môn Lý, quy kết bắt được một phần thật — **không
nên nói SHAP vô dụng** — nhưng chỉ khoảng một phần ba trần. Ở môn Sử, cả hai
biến thể về không. Biến thể (c) được thêm để chặn câu bắt bẻ "chọn nhầm loại
SHAP": (b) quy kết lề log-odds của từng lớp và đi theo đường trong cây, còn can
thiệp đo E[y]; (c) tính đúng giá trị Shapley cho hai khối đặc trưng trên chính
E[y], khối vắng mặt lấy giá trị của 200 câu nền — hai người chơi nên tính chính
xác, không xấp xỉ. Kết quả: (c) **không** tốt hơn (b), ở Lý còn thấp hơn.

Vấn đề cốt lõi không phải "SHAP sai" mà là: **SHAP không tự nói cho ta biết nó
đang ở đâu trên thang đó**. Cùng một công cụ, cùng một loại mô hình, hai bộ dữ
liệu — một lần được khoảng một phần ba trần, một lần được 0, và nhìn từ bên
ngoài hai lần trông y hệt nhau. Can thiệp thì tự mang theo sai số của chính nó.

---

## 8. Áp dụng cho một trục mới / môn mới

Thêm một trục vào `AXES` trong `tools/xai_difficulty.py` cần bốn thứ:

1. **Nhánh can thiệp** — cách sửa đúng một chỗ của câu để đẩy trục lên và
   xuống. Thêm vào `arms_for()` và `make_counterfactual()` trong
   `tools/counterfactual_validity.py`.
2. **Lời hứa về hướng** — viết vào `PROMISE` **trước khi chạy**. Đây là ràng
   buộc quan trọng nhất; hướng chọn sau khi nhìn số thì chứng chỉ mất giá trị.
3. **Đối chứng khớp** — donor phải giống can thiệp ở mọi mặt trừ đúng thuộc
   tính của trục. Nếu trục dựa trên thực thể thì đối chứng cũng phải có thực thể.
4. **Một câu tiếng Việt** trong `means` — sẽ xuất hiện nguyên văn trong lời
   giải thích, nên phải là thứ giáo viên đọc hiểu ngay.

Thêm một môn thì chỉ cần khai báo trong `cv.SUBJECTS` (đường dẫn, trường nhãn,
ánh xạ nhãn, loại trục bề mặt, ontology) — phần còn lại chạy nguyên.

**Giới hạn.** Trục thao tác của môn Lý (`prerequisiteOf`, `applicationSteps`)
**chưa** vào được pipeline này, vì nó không can thiệp được bằng cách thay một
phương án — phải hoán cả khối đặc trưng với một câu thật cùng bài, là một loại
bằng chứng yếu hơn. Xem `docs/OPERATION_AXIS.md` §4.6.

---

## 8b. Khai thác — lời giải thích dùng được vào việc gì

Faithfulness và stability đã đo được (§7). Hai trục còn lại của một hệ XAI —
*plausibility* và *utility* — thường cần người. Mục này thử hỏi xem có đo được
**utility** mà không cần người không.

### 8b.1 Thử 1: lấy lời giải thích làm cơ chế TỪ CHỐI trả lời — KHÔNG ĐƯỢC

`python tools/xai_difficulty.py --selective --subject physics --n 400 --reps 24`

Giả thuyết: chỗ lời giải thích bó tay (*KHÔNG QUY ĐƯỢC*) là chỗ mô hình hay
sai. Nếu đúng thì lớp giải thích thành một tín hiệu dùng được để hệ tự từ chối
xếp mức. Đối chứng bắt buộc: **entropy** của dự đoán — thứ có sẵn, không tốn gì.

**Đường cong độ phủ ↔ độ chính xác** (giữ lại k% câu "tự tin nhất"; n=300, R=16
— đúng cấu hình `reproduce_all.py` chạy lại được):

| xếp hạng theo | 100% | 80% | 60% | 40% | 20% |
|---|---:|---:|---:|---:|---:|
| **Lý** · entropy (đối chứng) | 37,7% | 39,2% | 39,4% | 40,8% | **45,0%** |
| **Lý** · sức giải thích | 37,7% | 41,2% | 43,9% | 36,7% | **30,0%** |
| **Sử** · entropy (đối chứng) | 64,3% | 68,8% | 74,4% | 78,3% | **83,3%** |
| **Sử** · sức giải thích | 64,3% | 62,9% | 62,2% | 60,8% | **53,3%** |

*Số theo cổng theo nhánh (§2b). Entropy không phụ thuộc cổng nên giữ nguyên;
dưới cổng cũ, dòng sức giải thích @20% là 28,3% (Lý) / 53,3% (Sử).*

> Ở ba mô hình nền văn bản, **cả hai cột @20 % đều lên** nhưng entropy vẫn dẫn
> trước ở **cả tám ô** (bốn mô hình nền × hai môn), tức **kết luận âm của mục
> này — sức giải thích không thắng được entropy — giữ nguyên trên toàn dải
> 0 → 100 % độ mờ.** Xem §10.3.

Entropy hoạt động đúng như một tín hiệu tự tin phải hoạt động; sức giải thích đi
xuống ở cả hai môn. Mẫu hình này **lặp lại ở một cấu hình độc lập** (n=400,
R=24, chạy dưới cổng cũ): Lý 35,8%→52,5% với entropy so với →25,0% với sức giải
thích; Sử 61,8%→85,0% so với →48,8%.

Xét trong từng tầng entropy để loại khả năng nó chỉ đang lặp lại entropy: sáu
tầng (3 tầng × 2 môn), **không tầng nào** có tương quan dương có ý nghĩa.

Dưới cổng theo nhánh, số câu được *QUY ĐƯỢC* ở môn Lý còn 33/300 (11%) — vì chỉ
câu có phương án chứa con số mới dựng được nhánh `num_down`. Môn Sử: 98/300 (33%).

### 8b.2 Cơ chế — và hai môn khác nhau ở đâu

> ⚠ **Mục này phụ thuộc mô hình nền mạnh hơn mọi mục khác.** Dưới mô hình văn bản,
> ρ(sức giải thích, entropy) **đổi dấu ở cả hai môn**, nên cơ chế trình bày ở đây
> chỉ đúng cho `xgb15`. **Cơ chế tổng quát đã tìm được** sau khi chạy bốn mô hình
> nền: ρ giảm đơn điệu theo *tỉ trọng khối không đặt tên được* và đổi dấu ở cùng
> một ngưỡng ở cả hai môn — xem §10.3 và `docs/BACKEND_CURVE.md` §3.3. Đừng trích
> mục này mà không kèm tên mô hình nền.

Cơ chế đề xuất: *sức giải thích* đo mức độ một sửa đổi nhỏ lay chuyển được dự
đoán, tức đo **khoảng cách tới ranh giới quyết định**. Câu gần ranh giới thì vừa
dễ lay chuyển (nên "giải thích được") vừa có dự đoán kém chắc.

| | Lý | Sử |
|---|---:|---:|
| ρ(sức giải thích, entropy) | **+0,293** (p = 2,5e−7) | **+0,175** (p = 0,002) |
| ρ(sức giải thích, \|sai lệch\|) | −0,009 (p = 0,88) | **+0,138** (p = 0,017) |

*Cổng cũ: +0,198 / +0,013 (Lý), +0,230 / +0,249 (Sử). Kết luận không đổi chiều.*

Vế đầu đúng như cơ chế dự đoán, ở **cả hai** môn. Vế sau thì hai môn **tách nhau**:

- **Môn Lý — kết quả rỗng.** Sức giải thích không tương quan với độ lớn sai lệch.
  Phát biểu đúng mức: nó là một **bản sao nhiễu của entropy**, bắt lại đúng phần
  entropy đã có và không thêm gì. Chênh lệch *QUY ĐƯỢC* − *KHÔNG QUY ĐƯỢC* là
  −4,8% với KTC95 [−16,9%, +7,8%] — chứa 0, nên **không** được nói là có hại.
- **Môn Sử — đi sai hướng.** Sức giải thích tương quan **dương** với độ lớn sai
  lệch (ρ = +0,138, p = 0,017). Giữ lại câu "giải thích được" tức là giữ lại câu
  mô hình sai nhiều hơn. Tín hiệu yếu đi dưới cổng theo nhánh (cổng cũ: +0,249)
  nhưng vẫn cùng chiều và vẫn có ý nghĩa.

Một lưu ý về độ chắc, phải nêu: chênh lệch độ chính xác ở môn Sử **không ổn định**
giữa các lần chạy (cổng cũ, n=400: −8,4% [−18,0%, +1,5%]; cổng cũ, n=300: −11,0%
[−21,2%, −0,4%]; cổng theo nhánh, n=300: −7,8% [−19,1%, +3,5%]). Nên kết luận cho
môn Sử phải dựa vào **tương quan ρ(sức giải thích, |sai lệch|)**, thứ giữ chiều và
giữ ý nghĩa qua cả hai cổng, chứ không dựa vào khoảng tin cậy của hiệu số.

**Điều này không hạ thấp phần faithfulness** (§7: ρ = +0,722 / +0,733 nửa A →
nửa B, vẫn đứng nguyên). Nó nói một điều hẹp hơn và cụ thể hơn:

> **Sức giải thích không phải là tín hiệu tự tin.** Một lời giải thích trung
> thực về câu này vẫn có thể đi kèm một dự đoán mong manh về chính câu đó.

Hệ quả phương pháp, đáng nêu vì văn liệu hay lẫn: **đừng dựng selective
prediction trên độ lớn quy kết.** Trực giác "mô hình giải thích được thì mô hình
chắc chắn" không đứng được — ở miền tự sự nó còn đi ngược — và cái rẻ hơn nhiều
(entropy) làm tốt hơn hẳn.

### 8b.3 Thử 2: biến lời giải thích thành LỜI KHUYÊN SỬA ĐỀ — được

`python tools/xai_difficulty.py --recourse --subject physics --n 250 --reps 16`

Đổi câu hỏi từ *"câu này khó vì đâu"* sang *"sửa tối thiểu gì thì hệ xếp lại
mức"* — dạng đầu ra người soạn đề dùng được. Mọi sửa đổi thay đúng một phương án
nhiễu bằng một nhiễu THẬT của câu khác, nên đề sau khi sửa vẫn đọc được.

| trên 250 câu | Lý | Sử |
|---|---:|---:|
| sửa được xuống mức thấp hơn — **qua nhánh đạt chứng chỉ** | **33,6%** | **30,8%** |
| sửa được lên mức cao hơn — qua nhánh đạt chứng chỉ | 15,6% | 15,2% |
| nhánh dùng làm lời khuyên | chỉ `num_down` (bớt số) | chỉ `len_down` (rút ngắn) |
| câu có sửa đổi đổi được mức nhưng BỊ LOẠI (nhánh chưa đạt) | 150 | 130 |
| *(mọi sửa đổi, kể cả chưa đạt)* sửa được theo hướng nào đó | 87,2% | 66,4% |
| *(mọi sửa đổi)* tỉ lệ sửa đổi thành công | 46,2% | 18,8% |

Trước khi chốt cổng theo nhánh (§2b), hai dòng đầu là 51,2% / 33,6% và 46,4% /
36,0% — phần chênh là lời khuyên đi qua chiều **thêm** (`num_up`, `len_up`), chiều
không vượt được mô hình nhãn xáo. Lời khuyên giờ nghiêng hẳn về **hạ mức** — khớp
với chiều duy nhất đã chứng minh được: *bớt con số / rút ngắn phương án thì hệ xếp
thấp đi*.

**Cổng B1 áp cả ở đây**, và đó là chỗ dễ sai nhất. Bản đầu tiên của công cụ đề
xuất sửa `kgv_0138` qua nhánh `kg_far` — tức khuyên sửa đề dựa trên chính trục
mà đề tài đã chứng minh là trượt chứng chỉ. Đã vá: chỉ **nhánh** qua cổng B1 mới
được dùng làm lời khuyên, và công cụ **khai báo số sửa đổi bị loại**.

Cảnh báo phải đi kèm mọi lần dùng: đây là sửa đổi làm **mô hình** xếp lại mức,
không phải bằng chứng học sinh sẽ thấy khác. Giá trị của nó thừa hưởng từ §7 —
nếu phần faithfulness không qua thì phần này cũng không.

> Và đúng vì thừa hưởng từ §7, mục này **yếu đi dưới mô hình văn bản**: lời khuyên
> hạ mức rơi từ 33,6% xuống 20,0% (Lý) và 30,8% xuống 12,8% (Sử) — sửa một cột
> viết tay không còn dịch được dự đoán nhiều như trước, vì cột đó không còn giữ
> phần lớn quyết định. Xem §10.3.

### 8b.4 Thử 3: rã tới từng CỘT thay vì cả khối

`explain()` giờ truy tiếp: trong trục đã nêu tên, cột nào chịu trách nhiệm. Hai
tình huống phải phân biệt, vì đọc khác nhau:

- **ăn khớp** — cột xê dịch khác nhau giữa các lần (ví dụ `len_dist_mean`, phụ
  thuộc donor bốc được), đo được mức ăn khớp bằng tương quan hạng Δcột ↔ Δdự đoán.
- **đều** — cột xê dịch y hệt mỗi lần (ví dụ `num_option_count` luôn đổi đúng ±1 khi bớt/thêm
  một nhiễu có số). Phương sai bằng 0 nên **không có tương quan để đo**; chỉ nói
  được "đây là cột đã xê dịch". Công cụ ghi rõ là ca này thay vì im lặng báo một
  con số trông giống ca trên.

---

## 9. Cái pipeline này KHÔNG làm được

- **Không giải thích độ khó với học sinh thật.** Nó giải thích *dự đoán của mô
  hình*, và mô hình học từ nhãn mức nhận thức NB/TH/VD/VDC do giáo viên gán,
  không phải từ tỉ lệ trả lời đúng. Chưa có dữ liệu học sinh (T1 chưa duyệt).
- **Không kết luận nhân quả về nhận thức.** "Sửa độ dài phương án làm dự đoán
  dịch 0,14 mức" là mệnh đề về mô hình, không phải về đầu học sinh. Nó chỉ trở
  thành mệnh đề về độ khó thật nếu nhãn là độ khó thật.
- **Không thay phán đoán giáo viên.** Mô hình học nhãn máy chuyển giao sang
  nhãn người ở κ = +0,155 — quá thấp để thay thế, đủ để làm gợi ý.
- **Nhãn tự nó chỉ khớp ~0,4.** Cùng một câu được gán nhãn hai lần trong ngân
  hàng đề: QWK 0,391 (Lý) / 0,355 (Sử) — trần của mọi mô hình ≈ 0,63 / 0,60.
  Nhãn vốn dao động, nên lớp giải thích luôn phải có quyền nói *KHÔNG KẾT LUẬN*.
  Trên CHÍNH các câu đó, mô hình nền **cũ** chỉ đạt 0,091 / 0,003
  (`tools/natural_raters.py`) — tức lớp giải thích khi ấy đang giải thích một mô
  hình chưa tốt. Mô hình nền **mới** đạt 0,409 / 0,347, tức **đã chạm mức người**
  (§10.1), nên giới hạn này nay chỉ còn nằm ở bản thân nhãn, không còn ở mô hình.
- **Chỉ hai trục can thiệp được bằng văn bản.** Độ phức tạp lời giải nằm ngoài
  bề mặt câu hỏi và chưa vào được khung này.

---

## 10. Dưới mô hình nền thứ hai — cái gì chuyển được, cái gì không

Từ 24/09/2026 pipeline chạy được trên **bốn** mô hình nền, **cùng một bộ tiêu
chí, cùng một bộ phản thực, cùng một hàm `certificate()`**. Bốn mô hình xếp theo
**tỉ trọng khối lượng quyết định nằm NGOÀI cột đặt tên được**:

| `QDE_BACKEND` | mô hình | đầu ra | khối không đặt tên được (Lý/Sử) |
|---|---|---|---:|
| `xgb15` (mặc định) | XGBoost, 15 cột viết tay | `*.json` | 0 % / 0 % |
| `tfidf` | TF-IDF từ + ký tự + 15 cột đó, C=16 | `*_tf.json` | 49,7 % / 56,4 % |
| `text` | PhoBERT đóng băng (768) + 15 cột đó, C=0,01 | `*_pb.json` | 77,6 % / 87,9 % |
| `emb` | PhoBERT đóng băng, KHÔNG cột luật tay | `*_eo.json` | 100 % / 100 % |

Mỗi mô hình nền có bảng mốc riêng (`docs/results_frozen{,_tf,_pb,_eo}.json`),
cả bốn đều `--check` khớp 72 · lệch 0.

Lý do đổi và bốn mảng bằng chứng: `docs/MODEL_UPGRADE.md`. **Bản bốn điểm đầy đủ
và phát biểu cuối: `docs/BACKEND_CURVE.md`** (`python tools/backend_curve.py`).
Bảng chênh lệch 72 số giữa hai bảng mốc bất kỳ: `python tools/backend_diff.py`.
Mục này chỉ nói **cái gì trong pipeline này chuyển được sang mô hình khác**.

### 10.1 Chuyển được — lớp CAN THIỆP

Hai nhánh bề mặt vẫn vượt đối chứng có ý nghĩa (Lý `num_up` +0,188, p ≈ 4·10⁻⁹⁶;
Sử `len_up` +0,075, p ≈ 4·10⁻³³), hai nhánh tri thức vẫn không. **Kết luận âm
về trục TRI THỨC (§3, §4) giữ nguyên qua cả BỐN mô hình nền** — tám ô, không ô
nào p hoán vị < 0,05:

| p hoán vị | xgb15 | tfidf | text | emb |
|---|---:|---:|---:|---:|
| Lý `kg_near` | 0,675 | 0,150 | 0,350 | 0,725 |
| Lý `kg_far` | 0,650 | 0,875 | 0,625 | 0,775 |
| Sử `kg_near` | 0,325 | 0,350 | 0,575 | 0,650 |
| Sử `kg_far` | 0,775 | 0,575 | 0,975 | 0,975 |

Nó không phải hệ quả của việc chọn XGBoost, và không còn đường nào để nói thế.

Độ lặp lại của lớp can thiệp (§7 dòng a) cũng giữ ở miền cấu trúc trên TOÀN
DẢI: Lý 0,722 / 0,673 / 0,705 / 0,725. Miền tự sự thì dao động: Sử 0,733 /
0,515 / 0,638 / 0,598 — phát biểu đúng mức là *ổn định ở miền cấu trúc*, không
phải *ổn định*.

Cổng B1 (§2b) đổi kết cục, theo hai chiều ngược nhau giữa hai môn — và **ba mô
hình nền văn bản cho cùng một kết cục**, tức đây không phải chuyện của PhoBERT:

| | xgb15 | tfidf | text | emb |
|---|---|---|---|---|
| Lý · qua luật CHẶT (`iut`) | không | **có** | **có** | **có** |
| Lý · nhánh vững mọi seed | `num_down` | +`num_up` | +`num_up` | +`num_up` |
| Lý · p hoán vị `num_up` | 0,100 | **0,025** | **0,025** | **0,025** |
| Lý · độ phủ của chứng chỉ | 39,2 % | **100 %** | **100 %** | **100 %** |
| Sử · qua luật CHẶT (`iut`) | **có** | không | không | không |
| Sử · nhánh vững mọi seed | `len_down` | `len_up` | `len_up` | `len_up` |
| Sử · p hoán vị `len_down` | 0,025 | 0,150 | 0,050 | 0,150 |

Lý được thêm `num_up` ở mọi mô hình văn bản, nên trục BỀ MẶT qua luật nghiêm
nhất và cổng không còn phải dựa vào một nhánh duy nhất. Sử mất `len_down` ở mọi
mô hình văn bản. Chiều nào cũng lặp lại ba lần, nên không đổ cho nhiễu được.

Và trên **cặp câu trùng** (`tools/natural_raters.py`), máy–người đi từ 0,091 lên
0,409 ở Lý (người–người 0,391) và 0,003 lên 0,347 ở Sử (người–người 0,355) —
xem §9.

### 10.2 KHÔNG chuyển được — lớp QUY KẾT

§7 dòng (b) và (c), so cùng cấu hình (n=150, R=16), bốn mô hình nền xếp theo tỉ
trọng khối **không đặt tên được**:

| | xgb15 · 0 % | tfidf · ~50 % | text · ~78–88 % | emb · 100 % |
|---|---:|---:|---:|---:|
| Lý (b) quy kết TỪNG CỘT → nửa B | **+0,297** | **+0,132** | **−0,050** | không định nghĩa được |
| Lý (b) đạt % trần | 34,9 % | 16,1 % | −6,0 % | — |
| Lý (c) Shapley **theo KHỐI** → nửa B | +0,224 | **+0,329** | +0,036 | — |
| Sử (b) quy kết TỪNG CỘT → nửa B | −0,088 | +0,095 | +0,047 | — |
| Sử (c) Shapley **theo KHỐI** → nửa B | +0,028 | **+0,173** | +0,123 | — |

Ở Lý, (b) từng là **kết quả dương duy nhất** của lớp quy kết, và nó **rơi đơn
điệu** theo tỉ trọng. Lý do đọc được ngay ở bảng quy kết theo khối — mô hình văn
bản có khối thứ ba, khối **VĂN BẢN**, và khối đó nuốt dần:

| tỉ trọng khối VĂN BẢN | xgb15 | tfidf | text | emb |
|---|---:|---:|---:|---:|
| Lý | 0 % | 49,7 % | 77,6 % | 100 % |
| Sử | 0 % | 56,4 % | 87,9 % | 100 % |

Khối nhúng / khối TF-IDF là khối **không đặt tên được**. Nhưng bốn điểm cho thấy
hệ quả **không đồng nhất giữa hai độ phân giải của quy kết**: dòng (c) — Shapley
theo khối — **không rơi**, và đạt đỉnh ở mô hình nền giữa, cao hơn cả `xgb15` ở
cả hai môn. Phát biểu rút ra (bản bốn điểm, đã sửa bản hai điểm):

> **Độ phân giải của lời giải thích quyết định nó chịu được bao nhiêu độ mờ.**
> Quy kết TỪNG CỘT rơi đơn điệu theo tỉ trọng khối không đặt tên được; quy kết
> THEO KHỐI thì không. Lớp can thiệp giữ nguyên trên toàn dải ở miền cấu trúc
> (ρ nửa A → nửa B = 0,722 / 0,673 / 0,705 / 0,725), dao động ở miền tự sự.

Hệ quả thực hành: **khi mô hình nền không phải mô hình trên đặc trưng viết tay,
giữ quy kết ở mức KHỐI, đừng rã tới từng cột** (§8b.4).

### 10.3 Lớp KHAI THÁC (§8b) — một kết luận giữ, một cơ chế ĐO ĐƯỢC

| | xgb15 · 0 % | tfidf · ~50 % | text · ~78–88 % | emb · 100 % |
|---|---:|---:|---:|---:|
| Lý · từ chối @20 %, entropy | 45,0 % | 71,7 % | 81,7 % | 78,3 % |
| Lý · từ chối @20 %, sức giải thích | 30,0 % | 38,3 % | 48,3 % | 55,0 % |
| **Lý · ρ(sức giải thích, entropy)** | **+0,293** | **+0,174** | **−0,124** | **−0,071** |
| Lý · lời khuyên hạ mức | 33,6 % | 24,8 % | 20,0 % | 17,2 % |
| Lý · lời khuyên nâng mức | 15,6 % | 26,8 % | 40,4 % | 45,2 % |
| Sử · từ chối @20 %, entropy | 83,3 % | 88,3 % | 88,3 % | 86,7 % |
| Sử · từ chối @20 %, sức giải thích | 53,3 % | 61,7 % | 70,0 % | 70,0 % |
| **Sử · ρ(sức giải thích, entropy)** | **+0,175** | **+0,133** | **−0,135** | **−0,099** |
| Sử · lời khuyên hạ mức | 30,8 % | 11,6 % | 12,8 % | 14,0 % |
| Sử · lời khuyên nâng mức | 15,2 % | 30,0 % | 26,0 % | 27,2 % |

**Giữ nguyên (§8b.1):** entropy thắng sức giải thích ở **cả tám ô** — bốn mô
hình nền × hai môn. Kết luận "đừng dựng selective prediction trên độ lớn quy
kết" đứng vững hơn hẳn bản một-mô-hình.

**Cơ chế (§8b.2) — đã tìm được, không còn bỏ ngỏ.** ρ(sức giải thích, entropy)
**giảm đơn điệu theo tỉ trọng khối không đặt tên được** và **đổi dấu ở cùng một
chỗ trong cả hai môn** (giữa `tfidf` và `text`). Nó là hàm của độ mờ, không phải
nhiễu, không phải đặc tính của môn hay của kiến trúc:

> *Sức giải thích* đo khoảng cách tới ranh giới quyết định **chỉ khi phần lớn
> quyết định còn nằm trong các cột đặt tên được**. Khi khối không đặt tên được
> chiếm quá nửa, câu mà các cột luật tay còn lay chuyển được lại chính là câu mà
> **khối văn bản chưa quyết chắc** — nên nó đi **ngược** với entropy.

Ngưỡng nằm đâu đó giữa 50 % và 78 %; bốn điểm không định vị chính xác hơn được,
và đừng giả vờ là định vị được.

**Đổi CHIỀU (§8b.3):** ở môn Lý, đơn điệu trên cả bốn — lời khuyên **hạ mức**
33,6 → 24,8 → 20,0 → 17,2 %, **nâng mức** 15,6 → 26,8 → 40,4 → 45,2 %. Mô hình
nền càng mờ thì sửa một cột luật tay càng khó kéo dự đoán xuống, càng dễ đẩy
lên. Hệ quả thực dụng khó chịu: **hạ mức mới là việc người soạn đề cần, mà nó
chạy tốt nhất ở đúng mô hình nền chấm kém nhất.**

### 10.4 Hai sai lệch phải công bố cùng mọi con số `_tf` / `_pb` / `_eo`

1. **`QDE_DONOR_SEED=42` cho toàn loạt kiểm tra tỉnh táo** — 84 lần chạy dùng
   chung một bộ phản thực thay vì rút lại mỗi lần (nếu không thì riêng bước này
   mất hơn 10 giờ nhúng). Phân bố rỗng hẹp lại ⇒ phép kiểm **chặt hơn**, không
   phải dễ hơn. Trường `donor_seed` được ghi vào mọi file phản thực.
2. **Cổng THEO NHÁNH được chọn sau khi nhìn số** (đã nêu ở §2b) — vẫn đúng cho
   cả bốn mô hình nền.
3. Riêng `tfidf`: **`C = 16` chọn một lần trên nhãn THẬT** bằng lưới
   1 / 4 / 16 / 64 / 256 (`tools/pick_c_tfidf.py`), rồi dùng y hệt cho cả 39 mô
   hình nhãn xáo. Dò lại `C` ở mỗi lần chạy thì mô hình nhãn xáo cũng được chỉnh
   riêng cho dữ liệu của nó và phép kiểm tỉnh táo mất nghĩa. Cực đại nằm TRONG
   lưới, không phải giá trị mép.
