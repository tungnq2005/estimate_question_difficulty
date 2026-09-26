# Đổi mô hình nền của lớp giải thích — lý do, cách làm, cái được và cái mất

Công cụ mới: `tools/text_backend.py`, `tools/text_vs_rules.py`, `tools/backend_diff.py`
Bảng mốc mới: `docs/results_frozen_pb.json` (72 số, `--check` khớp 72 · lệch 0)
Bảng mốc cũ: `docs/results_frozen.json` — 56 giá trị cũ **giữ nguyên từng chữ số**,
nay thêm 16 số của hồ sơ đo đạc; `--check` khớp 72 · lệch 0

> **Đọc `docs/BACKEND_CURVE.md` sau tài liệu này.** Tài liệu này so **hai** mô
> hình nền. Sau đó đã chạy thêm hai mô hình nền nữa (`tfidf`, `emb`), và bản
> bốn điểm **sửa lại kết luận ở §9** — chính xác hơn và mạnh hơn.

---

## 0. Tóm tắt

Vấn đề đặt ra: mô hình nền của đề tài (XGBoost trên 15 cột đặc trưng viết tay)
**không thích nghi** — gặp bài học chưa từng thấy thì chấm kém, và trên những
câu trùng xuất hiện ở hai đề khác nhau nó không đồng ý với giáo viên ở mức mà
hai lần chấm của người đồng ý với nhau.

Đã thay mô hình nền bằng **PhoBERT đóng băng (mean-pool, 768 chiều) + 15 cột cũ,
hồi quy logistic C = 0,01, out-of-fold 5 lát**. Toàn bộ chuỗi giải thích chạy lại
từ đầu dưới mô hình mới.

Kết quả gọn trong một câu: **dự đoán tốt lên rất nhiều, can thiệp vững hơn, nhưng
quy kết mất tính trung thực.**

| | cũ (15 cột) | mới (PhoBERT + 15 cột) |
|---|---:|---:|
| Lý · QWK trên **bài chưa gặp** | 0,375 | **0,551** |
| Sử · QWK trên **bài chưa gặp** | 0,138 | **0,362** |
| Lý · máy–người trên **câu trùng** (QWK) | 0,091 | **0,409** (người–người 0,391) |
| Sử · máy–người trên **câu trùng** (QWK) | 0,003 | **0,347** (người–người 0,355) |
| Lý · cổng B1 luật CHẶT (tiền đăng ký) | trượt | **qua** |
| Lý · độ phủ của cổng B1 | 39,2 % số câu | **100 %** |
| Sử · cổng B1 luật CHẶT | qua | **trượt** |
| Lý · quy kết dự báo được can thiệp (ρ) | +0,297 | **−0,050** |
| Lý · Shapley khối dự báo can thiệp (ρ) | +0,224 | **+0,036** |

Hai dòng cuối là cái giá phải trả, và là phát hiện đáng viết chứ không phải thất
bại: **lớp CAN THIỆP di chuyển được sang mô hình khác, lớp QUY KẾT thì không.**

*(Sửa sau khi có bốn mô hình nền: vế sau đúng cho quy kết TỪNG CỘT, sai cho quy
kết THEO KHỐI — xem §9 và `BACKEND_CURVE.md`.)*

---

## 1. Vì sao phải đổi

Câu hỏi đặt ra lúc đầu: "tăng khả năng thích nghi của mô hình". Hai đường có thể
đi — thêm mẫu có nhãn chuẩn hơn, hoặc dùng đặc trưng đánh giá chuẩn hơn. Phải đo
xem đường nào mới là chỗ nghẽn, chứ không đoán.

`tools/text_vs_rules.py` đo ba việc trên cùng một lát cắt, bốn mô hình:

| ký hiệu | mô hình |
|---|---|
| **R15** | XGBoost trên 15 cột viết tay — mô hình nền cũ |
| **T** | TF-IDF từ + ký tự, hồi quy logistic — nền văn bản rẻ nhất |
| **E** | PhoBERT đóng băng, hồi quy logistic |
| **E+R15** | PhoBERT + 15 cột đó — mô hình nền mới |

Phương án của mỗi câu được **sắp xếp theo chữ cái** trước khi ghép vào văn bản,
nên T và E không biết phương án nào đúng. Đây không phải chi tiết kỹ thuật vụn:
nó có nghĩa là **dữ liệu crawl thêm không kèm đáp án vẫn dùng được**.

---

## 2. Bằng chứng 1 — 15 cột viết tay đúng là chỗ nghẽn

Lát cắt ngẫu nhiên (thứ mọi con số cũ của đề tài dùng), 3 seed, QWK out-of-fold:

| | Lý (1 539 câu) | Sử (1 276 câu) |
|---|---:|---:|
| R15 | 0,395 ± 0,008 | 0,161 ± 0,005 |
| T | 0,574 ± 0,004 | 0,281 ± 0,009 |
| E | 0,556 ± 0,007 | 0,395 ± 0,022 |
| E+R15 | 0,565 ± 0,004 | 0,392 ± 0,015 |

Đọc: **ngay cả TF-IDF** — mô hình văn bản rẻ nhất, không huấn luyện gì — cũng bỏ
xa 15 cột viết tay (+0,18 QWK ở Lý, +0,12 ở Sử). Chỗ nghẽn nằm ở biểu diễn, không
nằm ở lượng nhãn. Thêm 15 cột vào PhoBERT gần như không đổi gì (0,556 → 0,565 ở
Lý; 0,395 → 0,392 ở Sử): **15 cột đó gần như đã nằm trọn trong biểu diễn văn bản.**

Giữ 15 cột lại trong mô hình nền không phải vì chúng thêm độ chính xác, mà vì lớp
giải thích cần chúng: đó là những đại lượng nói được thành lời với giáo viên.

---

## 3. Bằng chứng 2 — "thích nghi" phải đo trên bài chưa gặp

Chia lát **theo trang bài học** (`source_url`), nên tập kiểm toàn câu thuộc bài mô
hình chưa từng thấy. Đây mới là phép đo khái quát hoá, và là phép đo mà đề tài
trước đây **chưa hề làm**.

**Lý — 53 bài**

| | ngẫu nhiên | bài mới | rơi |
|---|---:|---:|---:|
| R15 | 0,395 | 0,375 | −0,020 |
| T | 0,574 | 0,506 | −0,068 |
| E | 0,556 | 0,543 | −0,013 |
| E+R15 | 0,565 | **0,551** | −0,014 |

**Sử — 34 bài**

| | ngẫu nhiên | bài mới | rơi |
|---|---:|---:|---:|
| R15 | 0,161 | 0,138 | −0,023 |
| T | 0,281 | 0,266 | −0,015 |
| E | 0,395 | 0,361 | −0,034 |
| E+R15 | 0,392 | **0,362** | −0,030 |

Hai điều đọc được:

1. **E+R15 gấp rưỡi tới gấp hai R15 trên bài chưa gặp** (0,551 vs 0,375; 0,362 vs
   0,138). Đây là câu trả lời trực tiếp cho "tăng khả năng thích nghi".
2. **T rơi nhiều nhất khi đổi sang lát bài mới** (−0,068 ở Lý, gấp 5 lần E). TF-IDF
   học từ vựng của từng bài; PhoBERT thì không. Nên dù T ngang E trên lát ngẫu
   nhiên, **chỉ E mới thật sự thích nghi** — đó là lý do chọn E chứ không chọn T,
   dù T rẻ hơn nhiều.

Mức rơi này cũng đáng đặt cạnh tài liệu: Faraji và cộng sự (2026) báo cáo mức rơi
≈ 0,28 khi chuyển bộ dữ liệu cho bài toán phân mức Bloom. Ở đây rơi 0,014–0,034 —
nhưng phải nói rõ đây là **bài khác trong cùng một nguồn**, không phải bộ dữ liệu
khác, nên hai con số không so trực tiếp được.

---

## 4. Bằng chứng 3 — thêm dữ liệu có đáng không

Đường cong học: bớt **số BÀI** trong tập huấn luyện (không bớt câu lẻ), đo trên
lát bài mới.

**Lý**

| % số bài | R15 | T | E | E+R15 |
|---:|---:|---:|---:|---:|
| 25 % | 0,340 | 0,363 | 0,445 | 0,454 |
| 50 % | 0,346 | 0,454 | 0,496 | 0,504 |
| 100 % | 0,375 | 0,506 | 0,543 | **0,551** |

**Sử**

| % số bài | R15 | T | E | E+R15 |
|---:|---:|---:|---:|---:|
| 25 % | 0,159 | 0,218 | 0,319 | 0,317 |
| 50 % | 0,163 | 0,231 | 0,324 | 0,329 |
| 100 % | 0,138 | 0,266 | 0,361 | **0,362** |

Đọc: R15 **gần như phẳng ở Lý** — tăng gấp bốn số bài chỉ được +0,035 QWK — và ở
Sử thì **đi xuống** (0,159 → 0,138, trong khi sai số chuẩn là ±0,02): thêm bài học
không làm 15 cột viết tay chấm khá hơn chút nào, chỉ làm nhiễu. Mô hình văn bản thì
vẫn đang dốc lên ở cả hai môn (+0,097 Lý, +0,045 Sử với E+R15; +0,143 và +0,048 với T).

Kết luận cho việc lên kế hoạch: **crawl thêm dữ liệu chỉ đáng tiền nếu mô hình nền
là mô hình văn bản.** Dưới mô hình cũ, tiền crawl gần như đổ đi. Đây cũng là lý do
kỹ thuật để không vội đi crawl trước khi đổi mô hình.

> Ghi chú thực thi: trang chỉ mục chương trình mới của kenhgiaovien là **tài liệu,
> không phải thư mục** (0 liên kết bài học; trang danh mục phân trang; `/tim-kiem`
> trả 404). Muốn crawl thêm phải viết lại phần liệt kê bài học. Chưa làm.

---

## 5. Bằng chứng 4 — câu trùng: máy đã bằng người chấm chưa

Không có người chấm thứ hai, và **sẽ không có** — ràng buộc của đề tài là không
dùng mẫu người thật. Thay vào đó dùng **các cặp câu trùng**: cùng một câu hỏi xuất
hiện trong hai đề khác nhau, do hai lần soạn khác nhau gán mức. Đó là một lần chấm
lại tự nhiên, sẵn có trong dữ liệu.

**Lý — 71 cặp trùng, 69 cụm, 38 cặp khác trang**

| | người–người | máy–người | chênh (KTC 95 %) |
|---|---:|---:|---|
| R15 (cũ) | 0,391 | 0,091 | **−0,300 [−0,586; −0,035]** |
| E+R15 (mới) | 0,391 | **0,409** | +0,019 [−0,197; +0,210] |

Dòng trên là kết luận mạnh nhất của cả đợt: dưới mô hình cũ, khoảng tin cậy của
"máy kém người" **không chứa 0** — máy dở hơn người một cách có ý nghĩa. Dưới mô
hình mới, chênh lệch là +0,019 và khoảng tin cậy chứa 0: **máy khớp nhãn giáo viên
ở đúng mức hai lần soạn đề khớp nhau.**

**Sử — 53 cặp có dự đoán, 49 cụm, 24 cặp khác trang**

| | người–người | máy–người | chênh (KTC 95 %) | QWK toàn bộ câu |
|---|---:|---:|---|---:|
| R15 (cũ) | 0,355 | 0,003 | −0,352 [−0,915; +0,128] | 0,137 |
| E+R15 (mới) | 0,355 | **0,347** | −0,008 [−0,418; +0,262] | 0,358 |

Sử cũng chạm mức người, nhưng khoảng tin cậy rộng hơn nhiều vì ít cặp hơn và nhãn
lệch hơn — nên ở Sử chỉ nói được "không còn bằng chứng máy kém người", chưa nói
được "máy bằng người" như ở Lý.

Trần lý thuyết `√(QWK người–người)`: Lý 0,625, Sử 0,596. QWK của mô hình mới trên
toàn bộ câu (chia lát theo cụm câu dẫn) là Lý 0,581, Sử 0,358 — **Lý đã sát trần
này**, Sử còn cách.

---

## 6. Mô hình mới, và cách giữ khả năng đảo ngược

`tools/text_backend.py`:

- `vinai/phobert-base`, **đóng băng** (không tinh chỉnh), mean-pool, 768 chiều,
  `MAX_LEN = 256`.
- Văn bản = `stem </s> ` + các phương án **sắp theo chữ cái**, nối bằng `</s>`.
- Thiết kế = `[nhúng 768 | 15 cột viết tay]` → hồi quy logistic `C = 0,01`,
  out-of-fold 5 lát, cùng chữ ký hàm với mô hình cũ.
- `grouped_fit` dùng `GroupKFold` cho `natural_raters`.
- Cache 256 mảnh trong `.cache/phobert/`, ghi nguyên tử, an toàn khi chạy song song.

Cách bật/tắt — **không có nhánh nào bị bỏ đi, không có số cũ nào bị ghi đè**:

```bash
QDE_BACKEND=xgb15   # mặc định — mô hình cũ, ghi ra *.json
QDE_BACKEND=text    # mô hình mới, ghi ra *_pb.json
python tools/reproduce_all.py --check              # bảng cũ: khớp 72 · lệch 0
python tools/reproduce_all.py --check --backend text  # bảng mới: khớp 72 · lệch 0
python tools/backend_diff.py --md                  # bảng chênh lệch giữa hai bảng
```

Cả hai bảng mốc đều tái lập được tại thời điểm viết tài liệu này. Nếu mô hình mới
hoá ra sai hướng, quay về chỉ là bỏ biến môi trường.

---

## 7. Cái được ở lớp CAN THIỆP — cổng B1

`docs/xai_sanity_pb.json`, 39 mô hình nhãn xáo + 4 seed thật, so với
`docs/xai_sanity.json` của mô hình cũ:

| | Lý cũ | Lý mới | Sử cũ | Sử mới |
|---|---|---|---|---|
| luật CŨ (`legacy`) cấp nhầm /39 | 30 | 22 | 27 | 26 |
| luật CHẶT (`iut`) cấp nhầm /39 | 0 | **0** | 0 | 1 |
| theo nhánh, cấp nhầm ≥ 1 nhánh /39 | 3 | 4 | 4 | 3 |
| chạy thật qua luật CHẶT | không | **có** | có | **không** |
| nhánh qua ở **cả 4 seed** | num_down | **num_down + num_up** | len_down | len_up |
| p hoán vị nhánh thứ hai | 0,100 | **0,025** | 0,025 | 0,050 |

**Lý được:** `num_up` (thêm một nhiễu có số) trước đây p = 0,10, không qua; giờ
p = 0,025 ở cả bốn seed. Vì cả hai nhánh bề mặt đều qua, trục BỀ MẶT qua **luật
CHẶT tiền đăng ký** — luật nghiêm nhất, luật duy nhất có tỉ lệ cấp nhầm 0/39. Và
vì cổng không còn phải dựa vào một nhánh duy nhất, **độ phủ của chứng chỉ tăng từ
39,2 % số câu (chỉ `num_down`) lên 100 %** (trục BỀ MẶT phủ toàn bộ câu).

**Sử mất:** `len_down` trôi từ p = 0,025 lên 0,050, nên trục BỀ MẶT của Sử không
còn qua luật CHẶT, chỉ còn `len_up` qua theo nhánh. Phải nói thẳng điều này —
đây không phải một đợt thay mô hình "mọi thứ đều tốt lên".

Về **can thiệp từng câu**, hai nhánh bề mặt vẫn vượt đối chứng có ý nghĩa dưới mô
hình mới (Lý `num_up` +0,188, p ≈ 4·10⁻⁹⁶; Sử `len_up` +0,075, p ≈ 4·10⁻³³), còn
hai nhánh tri thức vẫn không (Lý `kg_near` p = 0,45; `kg_far` p = 0,70). **Kết
luận âm về trục TRI THỨC giữ nguyên qua cả hai mô hình nền** — nó không phải hệ
quả của việc chọn XGBoost.

---

## 8. Cái mất ở lớp QUY KẾT

`docs/xai_validate_*_pb.json`, so với bản cũ:

| | Lý cũ | Lý mới | Sử cũ | Sử mới |
|---|---:|---:|---:|---:|
| trần lặp lại (nửa A → nửa B) | 0,722 | 0,705 | 0,733 | 0,638 |
| độ tin cậy (Spearman–Brown) | 0,839 | 0,827 | 0,846 | 0,779 |
| **quy kết dự báo can thiệp (ρ)** | **+0,297** | **−0,050** | −0,088 | +0,047 |
| tỉ lệ so với trần | 0,349 | −0,060 | −0,103 | +0,059 |
| Shapley khối dự báo can thiệp (ρ) | +0,224 | +0,036 | +0,028 | +0,123 |

Ở Lý, quy kết từng cột từng là **kết quả dương duy nhất** của lớp quy kết (ρ = 0,30,
bằng 35 % trần). Dưới mô hình mới nó về 0. Lý do đọc được ngay từ bảng quy kết theo
khối:

| | bề mặt | tri thức | **văn bản** | tỉ trọng khối văn bản |
|---|---:|---:|---:|---:|
| Lý | 0,122 | 0,198 | 1,108 | **77,6 %** |
| Sử | 0,064 | 0,076 | 1,015 | **87,9 %** |

Gần 80–90 % khối lượng quyết định giờ nằm trong 768 chiều nhúng — một khối **không
đặt tên được**. Quy kết tuyến tính trên khối đó không tạo ra lời giải thích kiểm
chứng được, và phép kiểm chứng chéo (nửa A dự báo nửa B) bắt đúng điều đó.

Kéo theo hai con số khai thác cũng kém đi: **lời khuyên sửa đề hạ mức** rơi từ
33,6 % xuống 20,0 % (Lý) và 30,8 % xuống 12,8 % (Sử) — sửa một cột viết tay không
còn dịch được dự đoán nhiều như trước, vì cột đó không còn giữ phần lớn quyết định.
Ngược lại **sửa để nâng mức** lại dễ hơn (15,6 % → 40,4 % ở Lý).

Và `ρ(sức giải thích, entropy)` **đổi dấu** ở cả hai môn (Lý +0,293 → −0,124; Sử
+0,175 → −0,135). Nghĩa là cơ chế đằng sau mục 8b.2 của `XAI_PIPELINE.md` **không
giống nhau giữa hai mô hình nền** — phần diễn giải cơ chế ở đó chỉ đúng cho mô hình
cũ và phải viết lại, chứ không chép sang được.

Điểm sáng nhỏ: **từ chối có chọn lọc tốt lên ở cả hai môn** (Lý @20 %: 0,300 →
0,483; Sử @20 %: 0,533 → 0,700), nhưng đối chứng entropy cũng tốt lên tương ứng
(Lý 0,450 → 0,817), nên **kết luận âm ở mục 8b.1 — sức giải thích không thắng được
entropy — vẫn giữ nguyên.**

---

## 9. Điều này có nghĩa gì cho đề tài

> ⚠ **Phát biểu dưới đây đã được SỬA sau khi chạy thêm hai mô hình nền nữa.**
> Bản hai-điểm không sai, nhưng nó gộp hai thứ khác nhau lại. Xem
> `docs/BACKEND_CURVE.md` cho bản bốn điểm — nó chính xác hơn và mạnh hơn.

Phát biểu hai-điểm (24/09, giữ lại để đối chiếu):

> Trên cùng một bộ kiểm chứng tiền đăng ký, **lớp can thiệp chuyển được giữa hai
> lớp mô hình khác hẳn nhau** (cây quyết định trên đặc trưng viết tay ↔ hồi quy
> trên nhúng ngôn ngữ), trong khi **lớp quy kết thì không**: quy kết mất hết tính
> trung thực đúng lúc mô hình nền đạt mức đồng thuận của người chấm.

Chạy thêm `tfidf` (khối không đặt tên được ~50 %) và `emb` (100 %) cho thấy vế
sau **đúng cho quy kết TỪNG CỘT, sai cho quy kết THEO KHỐI**:

| Lý | xgb15 (0 %) | tfidf (50 %) | text (78 %) | emb (100 %) |
|---|---:|---:|---:|---:|
| SHAP từng cột → nửa B | +0,297 | +0,132 | −0,050 | không định nghĩa được |
| Shapley **theo khối** → nửa B | +0,224 | **+0,329** | +0,036 | không định nghĩa được |

Quy kết theo khối ở `tfidf` là **kết quả quy kết tốt nhất của cả đề tài**, cao
hơn cả mô hình nền cũ. Phát biểu đã sửa:

> **Độ phân giải của lời giải thích quyết định nó chịu được bao nhiêu độ mờ của
> mô hình nền.** Quy kết TỪNG CỘT rơi đơn điệu theo tỉ trọng khối không đặt tên
> được; quy kết THEO KHỐI thì không, và đạt đỉnh ở mô hình nền giữa. Lớp can
> thiệp giữ nguyên ở miền cấu trúc trên toàn dải 0 → 100 %.

Đánh đổi **độ chính xác ↔ khả năng giải thích** vẫn có thật và vẫn đo được, chỉ
là nó tác động lên *một loại* quy kết chứ không phải mọi loại. Bốn con số chống
đỡ: 0,375 → 0,551 QWK trên bài chưa gặp; 0,091 → 0,472 trên câu trùng (ngang
người từ `tfidf` trở đi); +0,297 → −0,050 ở quy kết từng cột; +0,224 → +0,329 ở
quy kết theo khối.

Hệ quả cho vị trí của KG trong đề tài: kết luận âm về trục TRI THỨC **giữ nguyên
qua cả bốn mô hình nền, tám ô, không ô nào `p` hoán vị < 0,05**, nên nó không
còn là "XGBoost không thấy KG" mà là một kết quả về dữ liệu và về nhãn. Việc
chuyển KG từ *phương pháp* sang *kết quả âm* trong cách kể của đề tài — **chưa
hỏi ý GVHD, phải hỏi trước khi viết.**

---

## 10. Hai sai lệch phải công bố

1. **`QDE_DONOR_SEED = 42` cho toàn bộ loạt kiểm tra tỉnh táo.** 84 lần chạy dùng
   chung một bộ câu phản thực thay vì mỗi lần rút lại. Không làm vậy thì riêng bước
   này mất hơn 10 giờ nhúng. Tác dụng thống kê: phân bố rỗng **hẹp lại**, nên phép
   kiểm **chặt hơn**, không phải dễ hơn. Trường `donor_seed` được ghi vào mọi file
   phản thực.
2. **Cổng THEO NHÁNH được chọn sau khi nhìn số.** Luật `legacy` và `iut` là tiền
   đăng ký; luật theo nhánh thì không — nó ra đời sau khi thấy `legacy` cấp nhầm
   quá nhiều. Mọi chỗ trích dẫn cổng theo nhánh phải nói rõ điều này.

---

## 11. Còn dở — chạy tiếp từ đây

**Đã xong:**

- [x] Toàn chuỗi giải thích dưới `QDE_BACKEND=text` (phản thực ×2 → kiểm tra tỉnh
      táo → chấm chéo tự nhiên → kiểm tra chéo ×2 → độ phủ → từ chối → lời khuyên).
- [x] `docs/results_frozen_pb.json` đã đóng băng, `--check --backend text` khớp 72.
- [x] `docs/results_frozen.json` vẫn khớp — không có giá trị cũ nào bị đụng.
- [x] `tools/backend_diff.py` — bảng chênh lệch giữa hai bảng mốc.
- [x] `tools/text_vs_rules.py --subject both` → `docs/text_vs_rules.json`
      (bản ghi màn hình: `docs/text_vs_rules_run.log`). Mọi bảng ở mục 2–5 lấy từ đây.
- [x] 16 số của mục 2–5 đã buộc vào `reproduce_all.py` (danh sách 56 → **72 số**),
      thêm bước `text_vs_rules` (~75′) vào `--list`/`--run`.
- [x] Cập nhật `docs/XAI_PIPELINE.md` (§10 mới + ghi chú dẫn ở §2b, §7, §8b.1–3, §9),
      `docs/RESULTS_FROZEN.md` (mục 24/09), `docs/PAPER_SKELETON.md` (§0b, chương 6b,
      B15–B18, ranh giới phát biểu), `README.md`.

- [x] **Bịt điểm yếu "chỉ có hai điểm"**: thêm hai mô hình nền `tfidf` (khối
      không đặt tên được ~50 %) và `emb` (100 %), chạy trọn chuỗi cho cả hai,
      đóng băng `results_frozen_tf.json` và `results_frozen_eo.json` — **cả bốn
      bảng đều khớp 72 · lệch 0**. Kết quả: `docs/BACKEND_CURVE.md`.
- [x] **Tìm được cơ chế thay cho §8b.2.** ρ(sức giải thích, entropy) giảm đơn
      điệu theo tỉ trọng khối không đặt tên được và đổi dấu ở **cùng một chỗ ở
      cả hai môn** — nó là hàm của độ mờ, không phải nhiễu. Xem
      `BACKEND_CURVE.md` §3.3.

**Chưa xong:**

- [ ] Viết chương 6b của bài báo (`PAPER_SKELETON.md` §0b) — đóng góp mới nhất
      và chưa có dòng nào. Nguồn đã đủ: `BACKEND_CURVE.md`.
- [ ] Hỏi GVHD: (a) chuyển KG sang kết quả âm, (b) đổi tên đề tài theo đó,
      (c) nhắm hội nghị nào.
