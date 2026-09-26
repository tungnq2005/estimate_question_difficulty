# Nhãn người vs nhãn máy, và hệ XAI chẩn đoán độ khó

Ngày: 2026-09-01. Tools: `tools/teacher_vs_llm_labels.py`, `tools/attic/explain_difficulty.py`.
Kết quả: `subjects/{history,physics}/samples/teacher_vs_llm.json`.

Tài liệu ghép ba việc: (a) kiểm nhãn bằng nguồn nhãn **người** trên cả hai môn,
(b) đóng gói mọi kết quả âm tính đã đo thành một **hệ XAI chẩn đoán**, (c) nêu rõ
hệ đó dùng được vào việc gì và KHÔNG dùng được vào việc gì.

---

## 1. Nhãn người vs nhãn máy — thiết kế ghép cặp trên hai môn

Hai môn ở hai thế đối xứng, nên cộng lại thành một phép kiểm mạnh:

| | Lịch Sử | Vật Lí |
|---|---|---|
| nhãn nền của pipeline | **máy** (`llm_vote3`, 2.137 câu) | **người** (giáo viên, 1.539 câu) |
| nguồn nhãn đối chiếu | 90 câu, **1 giáo viên** | 1.539 câu, **LLM chấm mù** (`llm_judge_physics.py`) |
| thang | 3 mức | 4 mức |

### 1.1. Đồng thuận hai nguồn — khác nhau một trời một vực

| | Lịch Sử (n=90) | Vật Lí (n=1.539) |
|---|---:|---:|
| đồng thuận tuyệt đối | 35,6% | 48,7% |
| **Cohen κ** | **+0,013** | **+0,284** |
| QWK | +0,181 | +0,540 |
| Spearman | +0,229 | +0,570 |

Ở Lý hai nguồn **theo dõi cùng một gradient** (fair). Ở Sử κ ≈ **0** — hai nguồn
**không đo cùng một thứ**.

### 1.2. ⭐ Kiểu lệch khác hẳn nhau — đây mới là phát hiện

> ⚠️ **ĐÃ SỬA — đọc cùng §1.8.** Bảng Sử dưới đây dựa trên 90 câu của **một**
> giáo viên, thang 3 mức. Một nguồn nhãn giáo viên **thứ hai, độc lập, n = 225,
> thang 4 mức** (kenhgiaovien) cho thấy người **CÓ** dùng trục hành văn
> (ρ = +0,234), chỉ là LLM dựa vào nó **gấp ~2,4 lần**. Kết luận "người không
> dùng chút nào" là **quá mạnh**.

**Lịch Sử — máy bám trục hành văn mạnh hơn người nhiều:**

| đặc trưng | ρ vs **NGƯỜI** | ρ vs **MÁY** | chênh | p(boot) |
|---|---:|---:|---:|---:|
| `len_dist_mean` | **−0,010** | **+0,362** | +0,372 | **0,002** |
| `len_correct` | −0,055 | +0,294 | +0,349 | 0,009 |
| `kg_prereq_correct` | −0,169 | +0,092 | +0,261 | **0,000** |
| `kg_prereq_distractor` | **+0,184** | −0,009 | −0,193 | **0,000** |
| `kad_path_distance_mean` | −0,042 | +0,043 | +0,086 | 0,730 |

**Vật Lí — máy bám ĐÚNG trục của người, nhưng PHÓNG ĐẠI nó:**

| đặc trưng | ρ vs **NGƯỜI** | ρ vs **MÁY** | chênh | p(boot) |
|---|---:|---:|---:|---:|
| `num_option_count` | +0,463 | **+0,615** | +0,151 | **0,000** |
| `num_answer_present` | +0,341 | +0,489 | +0,148 | **0,000** |
| `num_formula_family` | +0,284 | +0,461 | +0,177 | **0,000** |
| `kg_entity_match_coverage` | −0,339 | −0,453 | −0,115 | **0,000** |
| `kg_centrality_mean` | −0,306 | −0,450 | −0,144 | **0,000** |
| `kad_path_distance_mean` | −0,078 | −0,144 | −0,066 | 0,139 |

**Ở Vật Lí, cả 15/15 đặc trưng đều CÙNG DẤU với hai nguồn và |ρ| với nhãn máy
LỚN HƠN.** Không một ngoại lệ. Nghĩa là LLM là một **bộ khuếch đại xác định
theo bề mặt**: nó dùng đúng các dấu hiệu giáo viên dùng, nhưng dùng *triệt để
hơn*. Phần giáo viên có mà bề mặt không giải thích được chính là phần chênh lệch.

Ở Lịch Sử thì không phải khuếch đại — là **đổi trục**.

### 1.3. ⭐ Chuyển giao: mô hình học nhãn máy có đoán được nhãn người không?

| | Lịch Sử | Vật Lí |
|---|---:|---:|
| so với **nhãn máy** | κ +0,221 · QWK +0,254 | κ +0,423 · QWK +0,605 |
| so với **nhãn người** | **κ −0,006** · QWK −0,017 | **κ +0,155** · QWK +0,401 |
| acc vs baseline lớp đông | 0,433 vs **0,500** (thua) | 0,398 vs 0,331 (vượt) |

**Pipeline Sử mang đúng 0 thông tin về phán đoán giáo viên.** Pipeline Lý mang
thông tin thật nhưng yếu (κ +0,155).

### 1.4. Kết luận mục 1

> **LLM là bộ KHUẾCH ĐẠI trục bề mặt, ở cả hai miền — mức khuếch đại khác nhau.**
> Lý: LLM dùng đúng trục của giáo viên, |ρ| lớn hơn ở **15/15** đặc trưng.
> Sử: LLM dựa vào trục hành văn **gấp ~2,4 lần** người (+0,572 so với +0,234,
> chênh p < 0,001) — mạnh hơn hẳn mức khuếch đại ở Lý.
>
> Hệ quả **không** đổi: nhãn LLM Sử không dùng làm chuẩn được, vì bất đồng dồn
> vào **tầng cao** (xem §1.8) đúng chỗ quan trọng nhất khi ra đề.

*(Bản trước kết luận "giáo viên Sử không dùng trục hành văn chút nào" dựa trên
n = 90 của một người; nguồn thứ hai ở §1.8 bác điều đó — xem §1.8.)*

Điều này chỉ thấy được khi có **một môn tự nhiên và một môn xã hội**.

### 1.5. Hạn chế bắt buộc nêu

- **Sử: n = 90, MỘT giáo viên, chỉ 7 câu "Khó".** Không có độ tin liên-người-chấm.
- κ ≈ 0 chỉ nói hai nguồn **bất đồng**, **không chứng minh giáo viên đúng**.
  Phân xử cần tỉ lệ trả lời đúng của học sinh — vẫn là nút thắt cũ.
- Hai môn dùng **thang khác nhau** (3 vs 4 mức) và **vai trò nguồn nhãn đảo
  nhau**, nên κ của hai môn **không so trực tiếp được**; chỉ so được *kiểu lệch*.
- 15 phép so sánh mỗi môn ⇒ ngưỡng Bonferroni p < 0,0033.
- Nhãn LLM Lý do `deepseek-v4-pro` chấm mù; nhãn LLM Sử là `llm_vote3` 3 phiếu.
  Hai quy trình khác nhau, có thể góp phần vào chênh lệch.

### 1.6. Khi KHÔNG có người chấm thứ hai — làm được gì (`tools/label_reliability.py`)

Cách chuẩn để biết "ai đúng" là mời người chấm thứ hai. Không có. Bốn phép sau
là những gì làm được mà không cần thêm người.

**A. Phân xử bằng mô phỏng học sinh — KHÔNG kết luận được.**
76 câu có đủ ba nguồn (giáo viên · LLM · p-value mô phỏng). Tương quan với "độ
khó hành vi" (1 − p):

| nguồn | ρ (n=76) | ρ chỉ câu phân biệt tốt (n=45) |
|---|---:|---:|
| nhãn GIÁO VIÊN | −0,081 (p = 0,49) | −0,246 (p = 0,10) |
| nhãn LLM | +0,214 (p = 0,064) | +0,105 (p = 0,49) |

Không phép nào đạt ý nghĩa. Mô phỏng có hiệu ứng trần đã biết (p trung bình
0,72 so với đề thật 0,5–0,6) và 31/76 câu có discrimination < 0,2 — quá cùn để
phân xử ở mức từng câu. **Và dùng một proxy LLM để bênh nhãn LLM sẽ là lập luận
vòng tròn**, nên kể cả khi ρ = +0,21 có ý nghĩa thì cũng không dùng được.

**B. ⭐ Test-retest của LLM — phép thay thế tốt nhất.**
Bộ dữ liệu có **715 nhóm nội dung trùng**, mỗi bản được chấm riêng ⇒ so phiếu
giữa các bản trùng chính là **đo lại cùng một giám khảo trên cùng nội dung**.

| | n | đồng thuận | κ |
|---|---:|---:|---:|
| phiếu #1 | 715 | 87,7% | **+0,806** |
| phiếu #2 | 715 | 85,5% | +0,772 |
| phiếu #3 | 715 | 86,3% | +0,780 |
| **gộp** | **2.145** | **86,5%** | **+0,786** (QWK +0,887) |

**Đây là điều thay được cho giáo viên thứ hai:** LLM là công cụ đo **khá ổn
định** (κ ≈ 0,79). Vì vậy κ(GV, LLM) = +0,013 **không giải thích được bằng "LLM
chấm bừa"** — hai nguồn lệch nhau **có hệ thống**, tức **đo hai thứ khác nhau**.
Nó vẫn không nói ai đúng, nhưng loại bỏ được cách đọc "chỉ là nhiễu".

⚠️ Ở tầng **nhãn cuối** các bản trùng khớp **100%** — đừng đọc thành "LLM hoàn
hảo". Đó là hiện vật của việc gộp phiếu theo nhóm (mục C).

**C. Kiểm toàn vẹn nhãn — phát hiện một chỗ cần ghi rõ.**

| | kết quả |
|---|---|
| câu KHÔNG trùng (1.422) | **0** câu có nhãn khác đa số phiếu của chính nó |
| nhóm trùng (715) | 683 (**95,5%**) giải thích được bằng "nhãn = đa số TOÀN NHÓM" |
| còn lại | **32 nhóm (4,5%)** không theo quy tắc đa số nào |

Quy trình gán nhãn **lành** ở câu đơn. Nhãn trong nhóm trùng được **gộp ở mức
nhóm** — hợp lý (nhiều phiếu hơn) nhưng **phải ghi rõ trong luận văn**, vì nó
giải thích vì sao 3,2% câu có nhãn khác đa số phiếu riêng. 32 nhóm còn lại nên
rà tay.

**D. Nhãn giáo viên có học được không — phép KHÔNG đủ lực.**

| nhãn | acc | baseline | κ |
|---|---:|---:|---:|
| GIÁO VIÊN | 0,389 | 0,500 | −0,123 |
| LLM (**đối chứng**) | 0,367 | 0,411 | +0,034 |

Đối chứng cho thấy phép hỏng vì cỡ mẫu: nhãn LLM — thứ ta **biết** là học được
(κ +0,221 khi huấn luyện trên 2.047 câu) — cũng sập ở n = 90. **Không được kết
luận "nhãn giáo viên là nhiễu".**


### 1.7. Kết luận khi không có người chấm thứ hai

- **Không** chứng minh được ai đúng.
- **Có** chứng minh được LLM là công cụ đo ổn định (κ ≈ 0,79) ⇒ bất đồng là **có
  hệ thống**.
- Phát biểu **đứng được**: hai nguồn **đo hai thứ khác nhau**; pipeline Sử tái
  tạo nhãn LLM và không tái tạo phán đoán của giáo viên này.
- Phát biểu **KHÔNG đứng được**: *"pipeline Sử đo sai độ khó"* — cần tỉ lệ trả
  lời đúng của học sinh thật mới nói được.

---

### 1.8. ⭐ Nguồn nhãn GIÁO VIÊN thứ hai cho môn Sử — 1.279 câu

Tìm được `kenhgiaovien.com/tai-lieu/trac-nghiem-lich-su-9` — **đúng loại nguồn
đã cứu môn Lý**: 34 bài, mỗi bài chia sẵn 4 phần NHẬN BIẾT / THÔNG HIỂU / VẬN
DỤNG / VẬN DỤNG CAO có ghi rõ số câu, do **giáo viên soạn theo ma trận đề**,
độc lập hoàn toàn với đề tài.

`tools/crawl/crawl_kenhgiaovien.py --subject history` → **1.339 câu**, 0 bài lỗi,
khử trùng còn **1.279 nội dung khác nhau** (chỉ 4,5% trùng — sạch hơn hẳn bộ
vietjack 54,7%). `tools/link_history_labels.py` ghép đáp án từ vietjack cho
**236 câu** (17,6%).

Đây là thay đổi lớn về vị thế của môn Sử: từ **90 câu** nhãn người lên
**1.279 câu** nhãn người.

| nhãn giáo viên (canonical) | NB 521 · TH 590 · VD 81 · VDC 87 |
|---|---|

**Ghép cặp nhãn GIÁO VIÊN vs nhãn LLM (n = 225, thang 4 mức):**

đồng thuận 54,2% · **κ +0,256** · **QWK +0,092**

| GV \ LLM | NB | TH | VD | VDC |
|---|---:|---:|---:|---:|
| **NB** (57) | 42 | 14 | 1 | 0 |
| **TH** (140) | 25 | 79 | 27 | 9 |
| **VD** (12) | 7 | 4 | 1 | 0 |
| **VDC** (16) | 11 | 4 | 1 | 0 |

⭐ **κ vừa phải nhưng QWK ≈ 0** — dấu hiệu bất đồng **dồn vào tầng CAO**:
trong 28 câu giáo viên gán VD/VDC, LLM chỉ gán VD/VDC cho **2 câu (7,1%)**, và
**18 câu bị hạ thẳng xuống NB**. Đây là bản Sử của điểm mù VDC đã đo ở Lý
(recall 11%) — nhưng **nặng hơn**: ở Lý là bỏ sót, ở Sử là **đảo ngược**.

**Tương quan ghép cặp (n = 225, bootstrap 2.000, Bonferroni p < 0,0033):**

| đặc trưng | ρ vs NGƯỜI | ρ vs MÁY | chênh | p |
|---|---:|---:|---:|---:|
| `len_dist_mean` | **+0,234** | **+0,572** | +0,339 | **0,000** |
| `len_correct` | +0,183 | +0,544 | +0,361 | **0,000** |
| `kg_prereq_correct` | −0,142 | +0,015 | +0,157 | **0,000** |
| `len_stem` | +0,257 | +0,360 | +0,103 | 0,245 |
| `kad_path_distance_mean` | −0,023 | −0,012 | +0,011 | 0,952 |

**Sửa lại kết luận §1.2/§1.4:** giáo viên **có** dùng trục hành văn (+0,234),
không phải bằng 0 như bộ 90 câu gợi ý. Điều **vẫn đúng và nay mạnh hơn** (hai
nguồn người độc lập, hai thang đo): **LLM dựa vào trục hành văn nhiều hơn người
một cách có ý nghĩa** — chênh +0,37 (n=90) và +0,34 (n=225), cả hai p < 0,01.
Và `kad_path_distance_mean` vẫn ≈ 0 với **cả hai** nguồn.

**Hạn chế:** (a) phân bố lệch nặng — VD+VDC chỉ 13% (Lý: 38%); (b) hai nguồn
người dùng hai thang khác nhau nên κ không so trực tiếp được.

### 1.9. Đáp án cho bộ Sử — sinh bằng LLM, nhưng **có đo** (`tools/llm_answer_key.py`)

Trang kenhgiaovien đăng câu hỏi + nhãn mức độ, **không** đăng đáp án. Nhãn độ khó
— thứ đề tài cần — là của giáo viên; chỉ mỗi đáp án phải sinh. Phải tách bạch hai
thứ đó khi viết báo cáo.

Đáp án Sử **ít khách quan hơn** đáp án Lý: nhiều câu dạng *"nguyên nhân chủ yếu
nhất"*, *"ý nghĩa quan trọng nhất"*. Nên không được mặc định LLM đúng như bản làm
cho môn Lý. Lần này có thứ môn Lý không có: **211 câu đã ghép được đáp án NGƯỜI**
từ vietjack ⇒ **tập kiểm chứng mù**, chạy trước khi tiêu lượt gọi cho hơn 1.000
câu còn lại.

Hai biện pháp thiết kế:

- **Xáo phương án tất định** theo hash id — mô hình không bám được vào *"đáp án
  hay nằm ở vị trí B"*. (Đã tự kiểm ánh xạ chữ cái → vị trí gốc bằng oracle giả:
  45 câu × 2 lượt, 0 lỗi.)
- **Hai lượt xáo khác nhau**; hai lượt lệch ⇒ cờ `answer_agree=false`.

| trên 211 câu đáp án NGƯỜI | n | chính xác |
|---|---:|---:|
| lượt 0 | 211 | 87,7% |
| lượt 1 | 211 | 89,6% |
| hai lượt **KHỚP** | 192 (91,0%) | **92,7%** |
| hai lượt **LỆCH** | 19 | **36,8%** (đoán mò = 25%) |

Dòng cuối là dòng đáng giá: cờ `answer_agree` **tự khai báo** câu đáng ngờ. Không
phải "LLM đúng 88%", mà "**92,7% trên phần LLM tự nhận là chắc, và phần nó tự
nhận là không chắc thì đúng là không đáng tin**". Trên bộ sinh thật, 85/1.079 câu
(7,9%) bị gắn cờ, và **cờ không lệch theo mức độ nhận thức** (χ² = 6,72; p =
0,082) ⇒ loại chúng không làm thiên lệch phân bố nhãn.

⚠️ **Bắt buộc nêu trong báo cáo:** "gold" ở đây là đáp án vietjack — cũng là đáp
án người đăng trên mạng, **không phải chuẩn tuyệt đối**. Một phần trong 26 câu
"sai" có thể là vietjack sai. Vậy **87,7% là cận dưới**, không phải ước lượng
điểm.

**Kết quả:** 1.279/1.279 câu canonical có đáp án (211 người + 1.068 LLM). Ba câu
bị loại vì **trang nguồn in trùng phương án** (4 phương án nhưng chỉ 3 nội dung ⇒
không tồn tại đáp án duy nhất) — gắn cờ `option_defect`, còn **1.276 câu dùng
được**.

### 1.10. ⚠️ Một lỗi ghép dữ liệu đã sửa — và bài học

Bản ghép đầu (`link_history_labels.py`) chép nguyên `correct` **và** `distractors`
của vietjack sang câu kenhgiaovien khi câu dẫn trùng. Nhưng **câu dẫn trùng không
bảo đảm bộ phương án trùng**:

| | |
|---|---:|
| khớp đúng từng chữ | 184 |
| khớp mờ (cùng ý, khác diễn đạt) → soi về phương án gốc | 27 |
| **lệch hẳn — hai đề khác nhau tình cờ trùng câu dẫn** | **25 → gỡ** |

25 câu đó đang mang bộ phương án của **một đề khác** với đề mà giáo viên gán
nhãn. Mọi đặc trưng nhiễu loạn tính trên chúng — `len_dist_mean`,
`jaccard_kg_max/mean`, `kad_path_distance_mean`, tức **đúng những đại lượng vận
hành hoá giả thuyết Vinu** — đều là rác. Đã gỡ và soi lại toàn bộ về đúng bộ
phương án gốc; giờ 100% câu có đáp án đều thoả `correct ∈ options` của chính nó.

**Bài học lặp lại lần thứ hai trong đề tài này** (lần đầu: khối đặc trưng KG
thiếu 4 cột, §xem `docs/COUNTERFACTUAL_VALIDITY.md`): sai sót âm thầm ở tầng dữ
liệu không làm chương trình đổ, nó chỉ làm kết luận sai. Nên mỗi bước ghép dữ
liệu từ nay đều phải có **một phép kiểm toàn vẹn chạy được** —
ở đây là `correct ∈ options`, `len(distractors) == 3`, `correct ∉ distractors`.

## 2. Hệ XAI chẩn đoán — `tools/attic/explain_difficulty.py`

Thay vì xuất một nhãn, hệ xuất **chẩn đoán bốn phần**:

| phần | nội dung |
|---|---|
| 1. DỰ ĐOÁN | mức + phân phối xác suất + entropy chuẩn hoá; entropy > 0,80 ⇒ **KHÔNG KẾT LUẬN** |
| 2. RÃ TRỤC | đóng góp trục **bề mặt** và trục **tri thức**, đo bằng *hai* cách: quy kết \|SHAP\| và chiếm chỗ ΔE[y] |
| 3. HIỆU CHỈNH | đối chiếu quy kết với **hiệu lực can thiệp đã đo** — phần cốt lõi |
| 4. ĐIỂM MÙ | những gì hệ **không** thấy, kèm số đo |

Mọi con số hiệu chỉnh **đọc từ file kết quả thí nghiệm**, không hard-code — sửa
thí nghiệm thì lời giải thích tự đổi theo. Mục 4 tự đổi kết luận theo môn:
Sử in *"KHÔNG dùng thay phán đoán giáo viên"* (κ chuyển giao −0,006), Lý in
*"dùng được như GỢI Ý, không thay thế"* (κ +0,155).

Ví dụ thật (`su9_vj_0191`): quy kết dành **54%** cho trục tri thức, nhưng bỏ cả
trục tri thức chỉ đổi E[y] **+0,005**, so với **+0,067** của trục bề mặt. Mục 3
in thẳng: *"can thiệp cho thấy trục đó không lay chuyển dự đoán theo hướng giả
thuyết; đọc phần tri thức như 'câu này có nhắc khái niệm trong chương trình
không', KHÔNG phải 'các phương án dễ nhầm tới mức nào'."*

### Vì sao là đóng góp, không phải một tính năng

Ba công trình đã chiếm ô "XGBoost + SHAP dự đoán và giải thích độ khó"
(Mathematics 12(10):1455 · MAKE 8(5):137 · AI 7(7):249). Cái khác ở đây là **lời
giải thích tự mang bằng chứng về độ tin của chính nó**: mỗi trục báo kèm hiệu
lực can thiệp đo được, và hệ nói thẳng trục nào **không** được tin. Đó là câu
trả lời cho phê phán của *Frontiers in Education 2026* rằng feature attribution
chỉ mở "a small window of insight".

---

## 3. ⚠️ Một cạm bẫy trong chính công cụ này

`--summary` định lượng khoảng lệch quy kết ↔ chiếm chỗ:

| môn | tỉ trọng KG theo quy kết | theo chiếm chỗ | chênh |
|---|---:|---:|---:|
| Lịch Sử | 28,6% | 32,4% | −3,8% |
| Vật Lí | 46,5% | 70,7% | −24,2% |

**Không được đọc thành "SHAP nói thiếu vai trò ontology".** Nhóm KG có **10 cột**,
nhóm bề mặt **5 cột**; thay cả nhóm bằng trung vị thì nhóm nhiều cột tự nhiên gây
nhiễu loạn lớn hơn ⇒ tỉ trọng chiếm chỗ **thiên vị nhóm lớn**. Hai cách chỉ dùng
để **thấy chúng bất đồng ở mức nào**.

Phép hiệu chỉnh **đáng tin** là mục 3 của chẩn đoán từng câu — đối chiếu **hiệu
lực can thiệp**, vì can thiệp sửa đúng **một phương án** nên không lệch theo số cột.

Ghi lại cạm bẫy này thay vì lặng lẽ bỏ, vì nó minh hoạ đúng luận điểm của đề tài:
**một chỉ số giải thích trông hợp lý vẫn có thể là hiện vật của thiết kế đo.**

---

## 4. Kết luận

1. **Bệnh lý nhãn LLM phụ thuộc miền** — khuếch đại đúng trục ở Lý (15/15 đặc
   trưng cùng dấu, |ρ| lớn hơn), đổi hẳn trục ở Sử (hành văn: +0,36 với máy,
   **−0,01** với người, p = 0,002).
2. **Pipeline Sử không chuyển giao sang phán đoán người** (κ = −0,006, thua
   baseline). Mọi con số Sử phải đọc là *"tái tạo nhãn LLM"*.
3. **Ontology không phải thứ gây lệch giữa hai nguồn nhãn.** Ở Sử, hai đặc trưng
   duy nhất bám nhãn giáo viên hơn đều là đặc trưng KG. Nhưng đại lượng của giả
   thuyết gốc (`kad_path_distance_mean`) ≈ 0 với **cả hai** nguồn, ở **cả hai môn**.
4. **Hệ XAI nên xuất chẩn đoán kèm mức đáng tin, không xuất nhãn.** Ba kết quả
   âm tính của đề tài trở thành **nội dung** của lời giải thích, thay vì bị giấu
   ở mục Hạn chế.

## 5. Việc mở

- ✅ **Đã có nguồn nhãn giáo viên thứ hai cho Sử** (§1.8, 1.279 câu) — không
  cần xin ai. ✅ **Đáp án đã sinh xong và đã đo** (§1.9): 1.276 câu dùng được.
  Việc mở kế tiếp: **chạy lại toàn bộ pipeline** (`counterfactual_validity`,
  `ablate_full`, `explain_difficulty`) trên bộ 1.276 câu **nhãn người** này thay
  vì bộ vietjack nhãn LLM — mọi kết luận về môn Sử hiện đang đứng trên nhãn máy.
- Giáo viên thứ hai chấm *cùng một bộ câu* vẫn còn giá trị (đo độ tin
  liên-người-chấm trực tiếp) — **hiện không có**; §1.6 là những gì thay thế được, và nó đi xa nhất tới mức "bất đồng có hệ
  thống", không tới được "ai đúng".
- Rà tay **32 nhóm** ở §1.6-C, và ghi quy tắc gộp nhãn theo nhóm vào chương
  Phương pháp.
- Cân bằng số cột giữa hai nhóm để phép chiếm chỗ hết thiên vị (§3).
- Kiểm xem phần giáo viên "có thêm" ở Lý (chênh giữa ρ người và ρ máy) có dự
  báo được không — nếu có, đó chính là phần độ khó nằm ngoài bề mặt.
