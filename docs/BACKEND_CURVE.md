# Bốn mô hình nền — cái gì trong lời giải thích sống sót, và sống sót tới đâu

Công cụ: `tools/backend_curve.py` → `docs/backend_curve.json`
Bảng mốc: `docs/results_frozen{,_tf,_pb,_eo}.json` — cả bốn đều `--check` khớp 72 · lệch 0

---

## 0. Vì sao có tài liệu này

`MODEL_UPGRADE.md` so **hai** mô hình nền và rút ra "can thiệp chuyển được, quy
kết thì không". Phản biện hiển nhiên: **hai điểm thì nối đường nào cũng được.**

Nên chạy thêm hai mô hình nền nữa, cùng một bộ tiêu chí tiền đăng ký, cùng bộ
phản thực, cùng hàm `certificate()`. Bốn mô hình xếp theo một trục có nghĩa:
**bao nhiêu phần khối lượng quyết định nằm NGOÀI cột đặt tên được.**

| mô hình nền | `QDE_BACKEND` | khối không đặt tên được (Lý / Sử) |
|---|---|---:|
| XGBoost · 15 cột luật tay | `xgb15` | 0 % / 0 % |
| TF-IDF từ + ký tự · + 15 cột | `tfidf` | **49,7 % / 56,4 %** |
| PhoBERT đóng băng · + 15 cột | `text` | 77,6 % / 87,9 % |
| PhoBERT đóng băng · KHÔNG cột luật tay | `emb` | 100 % / 100 % |

`emb` là **ca giới hạn**, không phải điểm thứ tư: không còn cột đặt tên được nào
nên quy kết bằng 0 ở mọi câu, và câu hỏi *"quy kết có dự báo được can thiệp
không"* **thôi đặt ra được**. Trong bảng nó là `—`, nghĩa là *không định nghĩa
được*, KHÔNG phải *bằng 0*.

---

## 1. Bảng đầy đủ

**Lý** (1 539 câu)

| | xgb15 | tfidf | text | emb |
|---|---:|---:|---:|---:|
| khối không đặt tên được | 0,0 % | 49,7 % | 77,6 % | 100 % |
| máy–người trên câu trùng | 0,091 | 0,336 | 0,409 | **0,472** |
| QWK chia lát theo cụm | 0,380 | 0,588 | 0,581 | 0,575 |
| **can thiệp: nửa A → nửa B** | +0,722 | +0,673 | +0,705 | +0,725 |
| **QUY KẾT: SHAP → nửa B** | **+0,297** | **+0,132** | **−0,050** | — |
| QUY KẾT: % trần | 34,9 % | 16,1 % | −6,0 % | — |
| QUY KẾT: Shapley khối → B | +0,224 | **+0,329** | +0,036 | — |
| cổng B1: trục qua luật CHẶT | — | BỀ MẶT | BỀ MẶT | BỀ MẶT |
| cổng B1: nhánh vững mọi seed | `num_down` | +`num_up` | +`num_up` | +`num_up` |
| từ chối @20 % · entropy | 45,0 % | 71,7 % | 81,7 % | 78,3 % |
| từ chối @20 % · sức giải thích | 30,0 % | 38,3 % | 48,3 % | 55,0 % |
| **ρ(sức giải thích, entropy)** | **+0,293** | **+0,174** | **−0,124** | **−0,071** |
| lời khuyên hạ mức | 33,6 % | 24,8 % | 20,0 % | 17,2 % |
| lời khuyên nâng mức | 15,6 % | 26,8 % | 40,4 % | 45,2 % |

**Sử** (1 276 câu)

| | xgb15 | tfidf | text | emb |
|---|---:|---:|---:|---:|
| khối không đặt tên được | 0,0 % | 56,4 % | 87,9 % | 100 % |
| máy–người trên câu trùng | 0,003 | **0,369** | 0,347 | 0,347 |
| QWK chia lát theo cụm | 0,137 | 0,348 | 0,358 | 0,371 |
| **can thiệp: nửa A → nửa B** | +0,733 | +0,515 | +0,638 | +0,598 |
| **QUY KẾT: SHAP → nửa B** | −0,088 | +0,095 | +0,047 | — |
| QUY KẾT: % trần | −10,3 % | 13,3 % | 5,9 % | — |
| QUY KẾT: Shapley khối → B | +0,028 | **+0,173** | +0,123 | — |
| cổng B1: trục qua luật CHẶT | BỀ MẶT | — | — | — |
| cổng B1: nhánh vững mọi seed | `len_down` | `len_up` | `len_up` | `len_up` |
| từ chối @20 % · entropy | 83,3 % | 88,3 % | 88,3 % | 86,7 % |
| từ chối @20 % · sức giải thích | 53,3 % | 61,7 % | 70,0 % | 70,0 % |
| **ρ(sức giải thích, entropy)** | **+0,175** | **+0,133** | **−0,135** | **−0,099** |
| lời khuyên hạ mức | 30,8 % | 11,6 % | 12,8 % | 14,0 % |
| lời khuyên nâng mức | 15,2 % | 30,0 % | 26,0 % | 27,2 % |

---

## 2. Cái đứng vững ở CẢ BỐN

**(a) Kết luận âm về trục TRI THỨC.** `kg_near` và `kg_far` không qua cổng hoán
vị ở bất kỳ mô hình nền nào, hai môn — tám ô, không ô nào `p < 0,05`:

| p hoán vị | xgb15 | tfidf | text | emb |
|---|---:|---:|---:|---:|
| Lý `kg_near` | 0,675 | 0,150 | 0,350 | 0,725 |
| Lý `kg_far` | 0,650 | 0,875 | 0,625 | 0,775 |
| Sử `kg_near` | 0,325 | 0,350 | 0,575 | 0,650 |
| Sử `kg_far` | 0,775 | 0,575 | 0,975 | 0,975 |

Giả thuyết Vinu 2015 bị bác ở **hai miền môn học × bốn họ mô hình**. Không còn
đường nào để nói *"tại các bạn chọn XGBoost"*.

**(b) Và đây là chỗ cổng hoán vị chứng minh nó đáng tồn tại.** Dưới `tfidf`,
nhánh `kg_near` của môn Lý có Wilcoxon `p = 0,022` **và đúng hướng đã hứa** —
tức là **nó QUA luật §2 gốc**. Nhưng `p` hoán vị là 0,150: hiệu ứng đó không
lớn hơn hiệu ứng của một mô hình học trên nhãn xáo. Nếu đề tài vẫn dùng luật cũ
thì chỉ cần đổi mô hình nền là kết luận trung tâm **đảo chiều**. Cổng hoán vị
giữ nó đứng yên. Đây là bằng chứng tốt nhất cho §2b, tốt hơn cả loạt 39 mô hình
nhãn xáo, vì nó là một ca suýt lọt có thật.

**(c) Entropy luôn thắng sức giải thích.** Bốn mô hình nền × hai môn = tám ô,
ô nào entropy cũng cho độ chính xác @20 % cao hơn. Kết luận âm ở §8b.1 không
phải đặc tính của một mô hình.

**(d) Lớp can thiệp không phụ thuộc mô hình nền — ở môn Lý.** Độ lặp lại nửa A
→ nửa B: 0,722 / 0,673 / 0,705 / 0,725 trên một dải tỉ trọng 0 → 100 %. Ở môn
Sử thì có dao động (0,733 / 0,515 / 0,638 / 0,598), nên phát biểu đúng mức là
*"ổn định ở miền cấu trúc, dao động ở miền tự sự"*, không phải *"ổn định"*.

---

## 3. Cái ĐỔI theo tỉ trọng khối không đặt tên được

### 3.1 Quy kết TỪNG CỘT rơi đều — nhưng chỉ ở nơi nó từng có gì để mất

Môn Lý, SHAP → nửa B theo tỉ trọng: **+0,297 (0 %) → +0,132 (50 %) → −0,050
(78 %) → không định nghĩa được (100 %)**. Đơn điệu giảm trên cả ba điểm đo được.

Môn Sử **không có xu hướng đó**, vì ở `xgb15` nó đã là −0,088 — không còn gì để
mất. Phải nói rõ điều này thay vì gộp hai môn lại thành một đường.

### 3.2 Quy kết theo KHỐI thì KHÔNG rơi — và đây là kết quả ngược với dự đoán

| Shapley khối → nửa B | xgb15 | tfidf | text | emb |
|---|---:|---:|---:|---:|
| Lý | +0,224 | **+0,329** | +0,036 | — |
| Sử | +0,028 | **+0,173** | +0,123 | — |

`tfidf` cho **kết quả quy kết tốt nhất của cả đề tài**, ở cả hai môn, cao hơn cả
`xgb15`. Giả thuyết đơn giản *"khối không đặt tên được phình ra thì quy kết tệ
đi"* **sai với quy kết theo khối**.

Phát biểu đúng mức sau khi có bốn điểm:

> Không phải mọi quy kết đều rơi khi mô hình nền mờ đi. **Quy kết TỪNG CỘT** rơi
> đơn điệu theo tỉ trọng khối không đặt tên được; **quy kết THEO KHỐI** thì
> không, và nó đạt đỉnh ở mô hình nền giữa. Độ phân giải của lời giải thích —
> từng cột hay từng khối — quyết định nó chịu được bao nhiêu độ mờ.

Đây là phát biểu mạnh hơn và cụ thể hơn bản hai-điểm, và nó chỉ ra được việc
nên làm: **giữ quy kết ở mức KHỐI, đừng rã tới từng cột**, khi mô hình nền không
phải mô hình trên đặc trưng viết tay.

### 3.3 Cơ chế thay cho §8b.2 — tìm được rồi

`XAI_PIPELINE.md` §8b.2 giải thích *sức giải thích* bằng **khoảng cách tới ranh
giới quyết định**, dựa vào ρ(sức giải thích, entropy) **dương**. Dưới mô hình
`text` nó âm, và tài liệu bỏ ngỏ chưa có cơ chế thay.

Bốn điểm cho thấy nó **không phải nhiễu — nó bám theo tỉ trọng**:

| ρ(sức giải thích, entropy) | 0 % | ~50 % | ~78–88 % | 100 % |
|---|---:|---:|---:|---:|
| Lý | +0,293 | +0,174 | −0,124 | −0,071 |
| Sử | +0,175 | +0,133 | −0,135 | −0,099 |

Giảm đơn điệu và **đổi dấu ở cùng một chỗ trong cả hai môn** — giữa `tfidf` và
`text`. Cơ chế viết lại được:

> *Sức giải thích* đo khoảng cách tới ranh giới quyết định **chỉ khi phần lớn
> quyết định còn nằm trong các cột đặt tên được**. Khi khối không đặt tên được
> chiếm quá nửa, cái đo được không còn là khoảng cách tới ranh giới nữa: câu mà
> các cột luật tay còn lay chuyển được lại chính là câu mà **khối văn bản chưa
> quyết chắc**, nên nó đi **ngược** với entropy.

Ngưỡng nằm đâu đó giữa 50 % và 78 %. Bốn điểm không định vị chính xác hơn được,
và không nên giả vờ là định vị được.

### 3.4 Lời khuyên sửa đề đổi CHIỀU

Môn Lý, đơn điệu trên cả bốn: hạ mức **33,6 → 24,8 → 20,0 → 17,2 %**, nâng mức
**15,6 → 26,8 → 40,4 → 45,2 %**. Mô hình nền càng mờ thì sửa một cột luật tay
càng khó kéo dự đoán **xuống** và càng dễ đẩy nó **lên**.

Điều này có hệ quả thực dụng, vì hạ mức mới là việc người soạn đề cần: **lời
khuyên sửa đề hoạt động tốt nhất ở mô hình nền có đặc trưng viết tay giữ phần
lớn quyết định** — tức đúng mô hình chấm kém nhất. Một đánh đổi nữa, đo được.

---

## 4. Phát biểu cuối, sau khi có bốn điểm

Bản hai-điểm ở `MODEL_UPGRADE.md` §9 nói "can thiệp chuyển được, quy kết thì
không". Bốn điểm cho phép nói chính xác hơn, và **phải sửa lại** cho đúng:

> Trên cùng một bộ tiêu chí tiền đăng ký chạy qua bốn mô hình nền trải từ 0 %
> tới 100 % khối lượng quyết định nằm ngoài cột đặt tên được:
>
> 1. **Kết luận âm chuyển được hoàn toàn** — trục TRI THỨC trượt ở cả 8 ô, và
>    một ca suýt lọt dưới luật cũ cho thấy cổng hoán vị là thứ giữ nó đứng yên.
> 2. **Lớp can thiệp chuyển được** ở miền cấu trúc; dao động ở miền tự sự.
> 3. **Quy kết TỪNG CỘT rơi đơn điệu** theo độ mờ — ở nơi nó từng có gì để mất.
> 4. **Quy kết THEO KHỐI thì không rơi**, và đạt đỉnh ở mô hình nền giữa.
> 5. **Cơ chế của "sức giải thích" đổi dấu** ở cùng một ngưỡng độ mờ trong cả
>    hai môn — nó là hàm của độ mờ, không phải của môn hay của kiến trúc.

Cái này khác hẳn một bài "chúng tôi đổi sang BERT và số đẹp hơn".

---

## 5. Cách chạy lại

```bash
for B in tfidf text emb; do QDE_BACKEND=$B python tools/counterfactual_validity.py --subject physics; done
QDE_BACKEND=tfidf python tools/xai_sanity.py --workers 5     # phải chạy TRƯỚC các bước XAI
python tools/backend_curve.py                                # gộp bảng
python tools/reproduce_all.py --check --backend tfidf        # khớp 72 · lệch 0
```

Cả chuỗi cho một mô hình nền mất ~25 phút (`tfidf`) / ~23 phút (`emb`) trên máy
này, vì vector PhoBERT đã cache trong `.cache/phobert/`.

**Hai sai lệch phải công bố** — giống hệt mô hình `text`, xem `MODEL_UPGRADE.md`
§10: `QDE_DONOR_SEED=42` cho toàn loạt kiểm tra tỉnh táo (phân bố rỗng hẹp lại ⇒
phép kiểm chặt hơn), và cổng THEO NHÁNH được chọn sau khi nhìn số.

Thêm một lựa chọn phải khai báo, riêng cho `tfidf`: **`C = 16` chọn một lần trên
nhãn THẬT** bằng lưới 1 / 4 / 16 / 64 / 256 (`tools/pick_c_tfidf.py`), rồi dùng
y hệt cho cả 39 mô hình nhãn xáo. Không được dò lại `C` ở mỗi lần chạy — làm vậy
thì mô hình nhãn xáo cũng được chỉnh riêng cho dữ liệu của nó và phép kiểm tỉnh
táo mất nghĩa. Cực đại nằm **trong** lưới (QWK trung bình hai môn 0,4478 ·
0,4675 · **0,4798** · 0,4715 · 0,4597), không phải giá trị mép.
