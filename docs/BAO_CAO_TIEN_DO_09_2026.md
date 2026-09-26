# BÁO CÁO TIẾN ĐỘ NGHIÊN CỨU KHOA HỌC

**Kỳ báo cáo:** tháng 7 → tháng 9/2026 (tiếp nối báo cáo `BAO_CAO_TIEN_DO.md`)

**Tên đề tài (đang dùng):** Ước lượng độ khó câu hỏi trắc nghiệm Lịch sử 9 bằng
Đồ thị Tri thức và Học máy

**Tên đề tài (đề xuất đổi — chờ GVHD duyệt, xem mục 7.3):** Giải thích được
(XAI) cho mức nhận thức của câu hỏi trắc nghiệm: kiểm chứng lời giải thích bằng
can thiệp phản thực, khảo sát trên bốn mô hình nền

> Mọi con số trong báo cáo này đều buộc vào một đường dẫn khoá cụ thể trong một
> file kết quả cụ thể, và kiểm lại được bằng `python tools/reproduce_all.py
> --check`. Không có số nào gõ tay.

---

## 1. Tóm tắt — giai đoạn này đã thay đổi những gì

Ba tháng qua đề tài **đổi trục nghiên cứu**, không phải chỉ làm tiếp việc cũ.
Bảng dưới là toàn bộ thay đổi, chi tiết ở các mục sau.

| Hạng mục | Trước (báo cáo tháng 8) | Sau (báo cáo này) |
|---|---|---|
| Câu hỏi nghiên cứu | *Dự đoán độ khó có chính xác không?* | *Lời giải thích có đúng không, và kiểm bằng cách nào?* |
| Nguồn "chân lý" để đối chiếu | khảo sát học sinh (đã lên kế hoạch) | **thí nghiệm can thiệp trên văn bản** — không cần người |
| Phạm vi môn | 1 môn (Sử 9) | **2 môn** (Sử 9 + Lý 9), hai miền tri thức khác nhau |
| Nguồn nhãn | 3 phiếu LLM | **nhãn giáo viên** (ma trận đề); nhãn LLM chuyển thành *đối chứng* |
| Thang nhãn | 3 lớp Dễ/TB/Khó | **4 mức NB/TH/VD/VDC** (giữ nguyên thang gốc, không gộp) |
| Mô hình nền | XGBoost trên 15 cột viết tay | **4 mô hình nền song song** (xgb15 · tfidf · text · emb) |
| Cách kiểm kết quả | chạy lại, đọc số | **72 con số đóng băng × 4 bảng mốc**, `--check` báo lỗi nếu lệch |
| Số công cụ | 1 nhánh | 38 công cụ đang dùng + **19 nhánh đã dừng** lưu nguyên trong `tools/attic/` |

**Hai lần đề tài tự bác kết quả của chính mình** trong kỳ này (mục 3.4 và 4.3) —
cả hai đều được ghi lại đầy đủ, kể cả phiên bản sai, vì đó là phần có giá trị
phương pháp luận cao nhất của đề tài.

---

## 2. Vì sao phải đổi trục — và vì sao đây là lý do kỹ thuật

### 2.1 Cái bị chặn

Muốn nói "mô hình ước lượng độ khó đúng hay sai" thì phải có **độ khó thật** để
đối chiếu. Trong đo lường giáo dục, độ khó thật của một câu là **tỉ lệ học sinh
trả lời đúng** — muốn có nó thì phải cho học sinh thật làm bài thật.

Kế hoạch đó đã được chuẩn bị: chọn 120 câu, sinh 3 đề, xin phép trường tổ chức
làm bài. **Không được duyệt.** Ràng buộc từ đó trở đi là **không dùng mẫu người
thật** — không học sinh, không giáo viên chấm, kể cả một người.

Không có tỉ lệ trả lời đúng thì không có thước để đo "ước lượng đúng hay sai".
Không lách được: mọi thứ thay thế (nhãn giáo viên, nhãn LLM) đều là **một đại
lượng khác**, không phải độ khó thực nghiệm.

### 2.2 Cái không bị chặn

Bài toán *ước lượng* cần chân lý từ bên ngoài. Bài toán **giải thích** thì không.

Lý do: đối tượng được giải thích là **dự đoán của mô hình**, chứ không phải chân
lý về học sinh. Và tính đúng đắn của một lời giải thích chứng minh được bằng
**can thiệp** — sửa đúng một thứ trong câu hỏi rồi xem dự đoán có dịch không —
chứ không cần khớp với phán đoán của ai.

Nói gọn: **thí nghiệm phản thực trên văn bản thay được cho khảo sát người dùng**,
mà khảo sát người dùng thì đang bị chặn.

Đây là lý do đề tài thành đề tài **XAI**: không phải vì dự đoán thất bại, mà vì
giải thích là câu hỏi **kiểm chứng được bằng tài nguyên đang có**.

### 2.3 Cái giá phải khai báo ngay, không giấu xuống mục giới hạn

Vấn đề chân lý **không biến mất, nó đổi chỗ**. Mô hình học nhãn **mức nhận thức
do giáo viên gán theo ma trận đề** (NB/TH/VD/VDC). Nên lời giải thích trả lời câu:

> **"cái gì khiến câu này được xếp mức cao trên thang NB/TH/VD/VDC"**

chứ **không** phải "cái gì khiến học sinh làm sai". Đây là một đại lượng có thật
và đáng nghiên cứu — nó quyết định đề thi ở Việt Nam trông thế nào — nhưng nó
không phải độ khó thực nghiệm. Mọi phát biểu của đề tài phải giữ đúng ranh giới
này.

### 2.4 Dữ liệu sau khi mở rộng sang 2 môn

| | môn Lý | môn Sử |
|---|---:|---:|
| số câu dùng được | **1.539** | **1.276** |
| số bài học phủ được | 53 | 34 |
| nguồn nhãn | giáo viên (ma trận đề) | giáo viên (cùng nguồn) |
| ontology | 319 thực thể / 310 cạnh (216 cạnh *tiên quyết*) | 480 thực thể / 937 cạnh |

Bộ Sử crawl ban đầu 3.152 câu nhưng **54,7% là bản sao** (đã báo cáo ở kỳ trước).
Đống bản sao đó, vốn là **lỗi rò rỉ dữ liệu**, trong kỳ này **trở thành một tài
sản đo lường** — xem mục 3.6.

---

## 3. Phương pháp đã xây dựng trong kỳ

Mỗi mục dưới đây theo cùng một khuôn: **cách làm mặc định của ngành → vì sao nó
không đủ ở đây → đề tài làm gì thay thế**.

### 3.1 Dẫn bằng CAN THIỆP, không dẫn bằng QUY KẾT

**Mặc định của ngành.** XAI dùng **quy kết đặc trưng** (SHAP, LIME): với mỗi câu,
gán cho mỗi đặc trưng một con số nói nó đóng góp bao nhiêu vào dự đoán.

**Vì sao không đủ.** Quy kết trả lời "mô hình *dựa vào* gì", và trả lời bằng cách
**tính từ cấu trúc cây**, không phải bằng cách **thử**. Trên chính bộ dữ liệu
này, tương quan giữa "SHAP gán bao nhiêu cho một trục" và "can thiệp lên trục đó
thực sự làm dự đoán đổi bao nhiêu" là **−0,051 · +0,005 · −0,008** (Lý) và
**−0,043 · −0,090 · −0,044** (Sử) — gần như độc lập hoàn toàn.

Nghĩa là một lời giải thích nghe rất hợp lý vẫn có thể **không liên quan gì** tới
cái mô hình thật sự phản ứng.

**Thay bằng.** Đổi câu hỏi: *"Nếu sửa đúng một thứ ở câu này, dự đoán có đổi
không, và đổi bao nhiêu so với mức nhiễu?"*

### 3.2 Can thiệp bằng PHƯƠNG ÁN THẬT lấy từ câu khác

**Cách dễ làm.** Sinh phương án nhiễu giả, xoá chữ, hoặc thay bằng văn bản ngẫu
nhiên.

**Vì sao không được.** Câu sau khi sửa **rơi ra ngoài phân phối** — không còn
giống một câu hỏi thật. Dự đoán dịch đi có thể chỉ vì văn bản trở nên kỳ quặc.

**Thay bằng.** Mỗi can thiệp thay **đúng một** phương án nhiễu bằng một phương án
nhiễu **thật, lấy từ câu khác** trong cùng kho. Bốn nhánh, mỗi nhánh **hứa trước
một chiều** rồi mới đo:

| nhánh | làm gì | hứa |
|---|---|---|
| `num_down` / `len_down` | bớt một nhiễu có số / rút ngắn một nhiễu | dễ đi |
| `num_up` / `len_up` | thêm một nhiễu có số / kéo dài một nhiễu | khó lên |
| `kg_near` | nhiễu mới cách đáp án đúng **1 bước** trên đồ thị tri thức | khó lên |
| `kg_far` | nhiễu mới cách **≥ 3 bước** hoặc rời mạch | dễ đi |

Hai nhánh đầu là **đối chứng dương**: chúng đo thứ đã biết chắc là mạnh. Nếu phép
đo không bắt được cả chúng thì **phép đo hỏng**, chứ không phải đồ thị tri thức
hỏng. Hai nhánh sau mới là thứ thật sự muốn kiểm — đó là giả thuyết Vinu 2015:
*độ khó đến từ mức giống nhau giữa đáp án đúng và nhiễu*.

### 3.3 Đối chứng KHỚP, tính riêng cho từng câu

Sửa bất kỳ thứ gì cũng làm dự đoán dịch một chút. Vậy dịch bao nhiêu mới là thật?

Mỗi câu có **sàn nhiễu của chính nó**: chạy thêm nhánh `placebo` — thay một nhiễu
bất kỳ, khớp về bề mặt, **không hứa gì**. Hiệu ứng thật của một nhánh = hiệu ứng
của nó **trừ đi** sàn nhiễu của cùng câu đó.

Riêng hai nhánh tri thức có đối chứng chặt hơn (`placebo_ent`): donor buộc phải
chứa thực thể. Lý do: `placebo` thường để lọt donor không có thực thể nào, mà như
thế **bản thân nó đã là một can thiệp tri thức** — đối chứng không còn khớp.

### 3.4 ⚠️ Cổng chứng chỉ trục — và phát hiện phương pháp quan trọng nhất của kỳ

**Thiết kế.** Trước khi được **nêu tên** trong bất kỳ lời giải thích từng câu nào,
một trục phải chứng minh ở **mức quần thể** rằng nó lay chuyển được dự đoán.
Trượt cửa này thì **vĩnh viễn không được nêu tên**. Hệ quả: hệ thống có **quyền
nói "không quy được"** — một hệ XAI mà câu nào cũng giải thích được là một hệ XAI
không kiểm được gì.

**Cổng bản đầu** có hai điều kiện: `p < 0,05` so với đối chứng, **và** dịch đúng
hướng đã hứa. Nghe rất chặt.

**Phép thử.** Theo phép kiểm chuẩn của ngành (Adebayo và cộng sự, 2018 — *data
randomization test*): **xáo ngẫu nhiên nhãn**, huấn luyện lại, chạy lại toàn bộ
phản thực, rồi chấm bằng **đúng hàm cổng đó**, 39 lần cho mỗi môn. Một cái cổng
đáng tin phải **trượt** khi mô hình không học được gì.

**Kết quả — cổng bản đầu hỏng nặng:**

| | môn Lý | môn Sử |
|---|---:|---:|
| cổng bản đầu cấp chứng chỉ cho mô hình học trên **nhãn xáo** | **30/39** | **27/39** |
| cổng có thêm điều kiện hoán vị | **0/39** | **0/39** |

**Vì sao hỏng.** Với 600–1.300 cặp quan sát, Wilcoxon coi **mọi** phản ứng có hệ
thống là "có ý nghĩa" — kể cả phản ứng của mô hình học thuộc nhãn ngẫu nhiên, vì
nó vẫn phải dựa vào đặc trưng nào đó. Còn "đúng hướng" với mô hình ngẫu nhiên chỉ
là tung đồng xu, mà lại có hai nhánh để thử.

**Đã sửa.** Thêm điều kiện thứ ba: hiệu ứng theo hướng đã hứa phải **lớn hơn hiệu
ứng của mô hình học trên nhãn xáo**, ở mức `p` hoán vị < 0,05, ở **mọi seed**.

> **Một ca cụ thể, đáng kể riêng.** Dưới mô hình nền `tfidf`, nhánh `kg_near` của
> môn Lý **qua được cổng bản đầu**: Wilcoxon `p = 0,022` và **đúng hướng đã hứa**.
> Nhưng `p` hoán vị = 0,150 — hiệu ứng đó không lớn hơn hiệu ứng của một mô hình
> học trên nhãn xáo, nên cổng hiện hành chặn lại.
>
> Nghĩa là: **nếu đề tài vẫn dùng cổng bản đầu thì chỉ cần đổi mô hình nền là kết
> luận trung tâm đảo chiều.** Đây là bằng chứng sống cho mục này — mạnh hơn cả
> loạt 39 mô hình nhãn xáo, vì nó là một ca suýt lọt có thật.

### 3.5 Kiểm tra chéo — lời giải thích có lặp lại được không

Mỗi can thiệp lặp R lần với donor bốc ngẫu nhiên. Vậy kết quả có ổn định, hay chỉ
là nhiễu nghe hợp lý? Chia R lần lặp thành **hai nửa dùng donor khác nhau hoàn
toàn**; ước lượng ở nửa A phải dự báo được nửa B. Rồi hỏi **cùng câu hỏi đó với
SHAP** — đây mới là phép so công bằng.

**Một chi tiết kỹ thuật quan trọng.** Nửa B là phép đo **có nhiễu**, độ tin cậy
ρ(A,B) ≈ 0,72. Theo lý thuyết đo lường cổ điển, một đại lượng *không nhiễu* tương
quan tối đa với nửa B là **√ρ**, không phải ρ. Lấy ρ làm trần thì **nghiêng có
lợi cho SHAP** — nên đề tài dùng √ρ, tức **tự đặt thanh cao hơn cho chính mình**.

### 3.6 Cặp câu trùng làm "người chấm thứ hai" — không tốn gì, không cần xin phép

Muốn biết mô hình chấm tốt tới đâu thì phải so với người. Nhưng không được dùng
người.

**Thay bằng** các **cặp câu trùng**: cùng một câu xuất hiện trong hai đề khác
nhau, do **hai lần soạn khác nhau** gán mức. Đó chính là một lần chấm lại tự
nhiên, sẵn có trong dữ liệu. Đống bản sao từng là **lỗi rò rỉ** (mục 2.4) nay
thành **thước đo**, cho hai con số:

- **người–người**: hai lần soạn khớp nhau bao nhiêu → **0,391 (Lý) / 0,355 (Sử)**
- **trần của mọi mô hình** = √(người–người) → **0,625 / 0,596**

Không mô hình nào vượt được trần này, vì bản thân nhãn đã dao động.

### 3.7 Nâng cấp mô hình nền — đo trước khi đổi, không đoán

Mô hình nền cũ là XGBoost trên **15 cột viết tay**. Nó **không thích nghi**: gặp
bài học chưa từng thấy thì chấm kém. Trước khi đổi, chạy `tools/text_vs_rules.py`
so bốn cách biểu diễn trên cùng lát cắt (QWK, đánh giá trên **bài chưa từng gặp**):

| | môn Lý | môn Sử |
|---|---:|---:|
| 15 cột viết tay | 0,375 | 0,138 |
| TF-IDF (mô hình văn bản rẻ nhất) | **0,506** | **0,266** |
| PhoBERT đóng băng | 0,543 | 0,361 |
| PhoBERT + 15 cột | **0,551** | **0,362** |

Ngay cả TF-IDF — đếm từ, không huấn luyện gì — cũng bỏ xa 15 cột viết tay. **Chỗ
nghẽn nằm ở cách biểu diễn câu hỏi, không nằm ở lượng nhãn.**

Ba lựa chọn thiết kế, mỗi lựa chọn có lý do cụ thể:

1. **Giữ nguyên 15 cột cũ**, dù thêm chúng gần như không tăng độ chính xác
   (0,543 → 0,551). Lý do: **lớp giải thích cần chúng** — đó là những đại lượng
   nói được thành lời với giáo viên. Bỏ chúng thì máy quy trách nhiệm theo cột,
   định nghĩa trục và phép can thiệp đều phải viết lại.
2. **Đóng băng, không tinh chỉnh.** Mô hình nền là **đối tượng được giải thích**,
   không phải sản phẩm. Nó phải tất định, rẻ, cache được, tái lập được.
3. **Sắp xếp phương án theo chữ cái** trước khi ghép thành văn bản, nên mô hình
   **không biết phương án nào đúng**. Không phải chi tiết vụn: nó có nghĩa là
   **dữ liệu crawl thêm mà không kèm đáp án vẫn dùng được**.

### 3.8 Bốn mô hình nền — vì hai điểm thì nối đường nào cũng được

Sau khi đổi sang PhoBERT, có hai điểm đo. Phản biện hiển nhiên: *hai điểm thì vẽ
đường gì cũng được.* Nên chạy trọn chuỗi trên **bốn** mô hình nền, xếp theo một
trục có nghĩa — **bao nhiêu phần khối lượng quyết định nằm NGOÀI các cột đặt tên
được**:

| mô hình nền | mô tả | khối không đặt tên được (Lý/Sử) |
|---|---|---:|
| `xgb15` | XGBoost, 15 cột viết tay | 0% / 0% |
| `tfidf` | TF-IDF + 15 cột đó | 49,7% / 56,4% |
| `text` | PhoBERT đóng băng + 15 cột đó | 77,6% / 87,9% |
| `emb` | PhoBERT đóng băng, **không** cột viết tay | 100% / 100% |

Cả bốn dùng **cùng bộ tiêu chí đã đăng ký trước, cùng bộ phản thực, cùng hàm
cổng**. `emb` là **ca giới hạn**, không phải điểm thứ tư: không còn cột đặt tên
được nào, nên câu hỏi "quy kết có dự báo được can thiệp không" **thôi đặt ra
được** — đó là *không định nghĩa được*, chứ không phải *bằng 0*.

---

## 4. Kết quả thu được

### 4.1 Về NỘI DUNG — hai miền môn học nói khác nhau

**Môn Lý (miền cấu trúc): trục THAO TÁC là trục thật.** Trục thao tác = số bước
biến đổi cần làm để ra đáp án (đọc từ ontology tiên quyết + vết giải).

| | giá trị |
|---|---:|
| `t` giữa hai câu **cùng một bài** | **21,53** |
| tỉ lệ cặp câu xếp đúng chiều | **90,5%** |
| tỉ trọng khi can thiệp cả khối | **17,5%** |
| *đối chứng* (`kad_path_distance`) | **0,85%** |

Mệnh đề *"cùng một bài"* là bắt buộc, bỏ đi là sai. Và con số đối chứng 0,85%
phải đi kèm mỗi lần nêu 17,5%, nếu không thì 17,5% mất nghĩa.

**Môn Sử (miền tự sự): trục TRI THỨC mới là trục có tỉ trọng** — 62,5% khi can
thiệp cả khối (đối chứng 1,8%), `t = +2,87` giữa hai câu cùng ô ma trận.

**Giả thuyết Vinu 2015 bị bác ở cả hai miền.** Ở môn Lý nó không chỉ trượt mà còn
**đảo dấu** (`t = −3,22`): nhiễu **gần** đáp án hơn lại làm câu **dễ đi**. Kết
luận âm này **lặp lại ở cả 8 ô** — bốn mô hình nền × hai môn, không ô nào có `p`
hoán vị < 0,05:

| `p` hoán vị | xgb15 | tfidf | text | emb |
|---|---:|---:|---:|---:|
| Lý `kg_near` | 0,675 | 0,150 | 0,350 | 0,725 |
| Lý `kg_far` | 0,650 | 0,875 | 0,625 | 0,775 |
| Sử `kg_near` | 0,325 | 0,350 | 0,575 | 0,650 |
| Sử `kg_far` | 0,775 | 0,575 | 0,975 | 0,975 |

Nên nó **không phải** là "XGBoost không thấy đồ thị tri thức". Nó là một kết quả
về **dữ liệu và về nhãn**, độc lập với mô hình nền.

**Một kết quả đáng chú ý về chính nhãn:** đổi nguồn nhãn (giáo viên ↔ LLM) thì
trục tri thức **giữ được 74,3%**, còn trục bề mặt chỉ giữ **37,4%**. Nghĩa là
trục bề mặt phần lớn là **tạo tác của người gán nhãn**, không phải thuộc tính của
câu hỏi.

### 4.2 Về LỚP GIẢI THÍCH — cái gì đáng tin, cái gì không

| | môn Lý | môn Sử |
|---|---:|---:|
| can thiệp: nửa A dự báo nửa B | **+0,722** | **+0,733** |
| độ tin cậy khi dùng đủ R lần lặp | **0,839** | **0,846** |
| trần cho mọi đại lượng dự báo nửa B | 0,850 | 0,856 |
| **quy kết SHAP dự báo nửa B** | **+0,297** | **−0,088** |
| SHAP đạt bao nhiêu % trần | **34,9%** | ≈ 0 |

Đọc: **lời giải thích bằng can thiệp lặp lại được** (0,72–0,73, độ tin cậy
0,84–0,85). **Quy kết SHAP chỉ bắt được khoảng một phần ba** ở môn Lý và **không
bắt được gì** ở môn Sử.

Phát biểu đúng mức — đây là ranh giới hay bị lỡ tay:

> Không được nói *"SHAP không trung thực"*. Phải nói: **SHAP không tự nói cho ta
> biết nó đang ở đâu trên thang trung thực** — một phần ba trần ở bộ này, 0 ở bộ
> kia, và nhìn từ ngoài không phân biệt được.

**Hai kết quả âm của lớp khai thác** (đã thử, không được):

- **Dùng lời giải thích làm cơ chế từ chối trả lời: KHÔNG ĐƯỢC.** Giữ lại 20% câu
  "tự tin nhất": xếp theo entropy cho 45,0% / 83,3% độ chính xác; xếp theo sức
  giải thích chỉ cho 30,0% / 53,3%. **Entropy — thứ có sẵn, không tốn gì — thắng
  ở cả tám ô** (4 mô hình nền × 2 môn).
- **Độ phủ có hạn.** Trục tri thức chỉ đo được ở **41,1% câu Lý / 46,5% câu Sử** —
  phần còn lại phán quyết đúng là *"chưa biết"*, không phải *"không có tác dụng"*.

**Một kết quả dương dùng được:** biến lời giải thích thành **lời khuyên sửa đề**.
Sửa tối thiểu (thay đúng một nhiễu) làm hệ xếp câu xuống mức thấp hơn ở **33,6%
(Lý) / 30,8% (Sử)** số câu — và chỉ đi qua nhánh **đã đạt chứng chỉ**.

### 4.3 ⚠️ Kết quả mới nhất — và nó SỬA LẠI một phát biểu trước đó của đề tài

Môn Lý, bốn mô hình nền xếp theo tỉ trọng khối không đặt tên được:

| | xgb15 · 0% | tfidf · 50% | text · 78% | emb · 100% |
|---|---:|---:|---:|---:|
| máy–người trên câu trùng | 0,091 | 0,336 | 0,409 | **0,472** |
| **can thiệp: nửa A → nửa B** | +0,722 | +0,673 | +0,705 | +0,725 |
| **quy kết TỪNG CỘT → nửa B** | **+0,297** | **+0,132** | **−0,050** | không định nghĩa được |
| **quy kết THEO KHỐI → nửa B** | +0,224 | **+0,329** | +0,036 | — |
| ρ(sức giải thích, entropy) | +0,293 | +0,174 | −0,124 | −0,071 |

Bốn điều đọc được:

1. **Lớp can thiệp không phụ thuộc mô hình nền** — 0,722 / 0,673 / 0,705 / 0,725
   trên toàn dải 0 → 100%.
2. **Quy kết TỪNG CỘT rơi đơn điệu** theo độ mờ: +0,297 → +0,132 → −0,050.
3. **Quy kết THEO KHỐI thì KHÔNG rơi** — và đạt **đỉnh ở mô hình nền giữa**
   (+0,329 ở Lý, +0,173 ở Sử), cao hơn cả mô hình cũ. Điều này **ngược với dự
   đoán** và là lý do phát biểu hai-điểm trước đó phải sửa.
4. **Cơ chế đằng sau "sức giải thích" đo được**: ρ với entropy giảm đơn điệu và
   **đổi dấu ở cùng một chỗ trong cả hai môn**. Nó là hàm của độ mờ, không phải
   nhiễu, không phải đặc tính của môn.

**Phát biểu cũ (SAI một nửa, giữ lại để đối chiếu):** *"mô hình càng mờ thì quy
kết càng chết"*.

**Phát biểu đã sửa:**

> **Độ phân giải của lời giải thích quyết định nó chịu được bao nhiêu độ mờ của
> mô hình nền.** Quy kết *từng cột* rơi đơn điệu khi khối không đặt tên được phình
> ra; quy kết *theo khối* thì không. Lớp *can thiệp* giữ nguyên trên toàn dải.

Hệ quả thực hành: **khi mô hình nền không phải mô hình trên đặc trưng viết tay,
hãy giữ quy kết ở mức KHỐI, đừng rã tới từng cột.**

### 4.4 Chất lượng của chính mô hình được giải thích

| | mô hình cũ | mô hình mới |
|---|---:|---:|
| Lý · QWK trên **bài chưa từng gặp** | 0,375 | **0,551** |
| Sử · QWK trên **bài chưa từng gặp** | 0,138 | **0,362** |
| Lý · máy–người trên câu trùng | 0,091 | **0,409** *(người–người 0,391)* |
| Sử · máy–người trên câu trùng | 0,003 | **0,347** *(người–người 0,355)* |

Dòng thứ ba là kết luận đáng kể nhất: dưới mô hình cũ, khoảng tin cậy 95% của
"máy kém người" là **−0,300 [−0,586; −0,035]** — **không chứa 0**, tức máy dở hơn
người một cách có ý nghĩa. Dưới mô hình mới, chênh lệch là **+0,019 [−0,197;
+0,210]**: **máy khớp nhãn giáo viên ở đúng mức hai lần soạn đề khớp nhau**.

Ở môn Sử khoảng tin cậy rộng hơn nhiều (53 cặp trùng so với 71 ở Lý), nên chỉ nói
được *"không còn bằng chứng máy kém người"*, chưa nói được *"máy bằng người"*.

**Đường cong học trả lời câu "crawl thêm dữ liệu có đáng không":**

| % số bài huấn luyện | 15 cột viết tay | PhoBERT + 15 cột |
|---:|---:|---:|
| 25% (Lý) | 0,340 | 0,454 |
| 100% (Lý) | 0,375 | **0,551** |
| 25% (Sử) | 0,159 | 0,317 |
| 100% (Sử) | **0,138** ⟵ đi xuống | **0,362** |

Mô hình cũ **phẳng ở Lý và đi xuống ở Sử** — thêm bài học không cứu được nó. Mô
hình mới vẫn đang dốc lên. Nên **crawl thêm dữ liệu chỉ đáng tiền nếu mô hình nền
là mô hình văn bản.**

---

## 5. Hạ tầng tái lập và dọn dẹp mã nguồn

### 5.1 Đóng băng 72 con số

**Vấn đề.** Mọi con số của báo cáo nằm rải trong nhiều file JSON, do nhiều công cụ
sinh ra ở nhiều thời điểm. Không có gì bảo đảm chạy lại hôm nay vẫn ra đúng số đã
viết, và nếu số trôi đi thì không ai biết.

**Đã làm.** Biến bảng kết quả thành một **bài kiểm tra hồi quy**: 72 con số, mỗi
con số buộc vào một đường dẫn khoá cụ thể trong một file cụ thể, kèm dung sai và
kèm chỗ nó được trích dẫn. `--check` thoát với mã lỗi nếu có số lệch. Dung sai đặt
theo nguyên tắc **rộng bằng mức mà kết luận vẫn giữ nguyên**, không phải bằng độ
chính xác của máy.

Bốn mô hình nền → **bốn bảng mốc song song**, cả bốn hiện đều `khớp 72 · lệch 0`.

### 5.2 Kế hoạch chạy lại

| nhóm bước | số bước | ghi chú |
|---|---:|---|
| **ĐÓNG BĂNG** — cần LLM, **không** chạy lại | 3 | sinh đáp án · sinh vết giải · chấm nhãn đối chứng |
| **OFFLINE** — tất định, chạy lại được | 15 | ~166 phút, seed 42 cố định |

Điểm này quan trọng khi trình bày: **không kết luận nào của đề tài phụ thuộc vào
việc gọi lại mô hình ngôn ngữ.** Mười lăm bước offline đọc JSON đã đóng băng và
tái tạo lại toàn bộ bảng số.

```bash
python tools/reproduce_all.py --list                    # xem kế hoạch
python tools/reproduce_all.py --check                   # đối chiếu 72 số
python tools/reproduce_all.py --check --backend tfidf   # và text, emb
python tools/backend_curve.py                           # bảng kết quả chính
python tools/reproduce_all.py --run                     # chạy lại toàn bộ (~166′)
```

### 5.3 Dọn mã nguồn

- **38 công cụ đang dùng** trong `tools/`, có `tools/README.md` mô tả từng cái.
- **19 công cụ của các nhánh đã dừng** chuyển vào `tools/attic/` — **không xoá**,
  vì nhánh thất bại cũng là bằng chứng. `tools/attic/README.md` ghi rõ từng file
  đã dùng để làm gì và vì sao dừng. Trước khi chuyển đã dựng đồ thị import để xác
  nhận **không công cụ đang dùng nào phụ thuộc vào chúng**; sau khi chuyển, cả
  bốn `--check` vẫn qua.
- **Tài liệu**: thêm `docs/TONG_QUAN.md` (đọc trước, đủ nắm toàn bộ đề tài),
  `docs/BACKEND_CURVE.md`, `docs/MODEL_UPGRADE.md`, `docs/README.md`. Mọi liên
  kết nội bộ giữa các file docs đã được kiểm bằng script.

### 5.4 Sản phẩm bàn giao trong kỳ

| Muốn xem | Đọc |
|---|---|
| toàn cảnh đề tài (bối cảnh → kỹ thuật → tác động → kết quả) | `docs/TONG_QUAN.md` |
| phương pháp XAI đầy đủ | `docs/XAI_PIPELINE.md` |
| kết quả bốn mô hình nền | `docs/BACKEND_CURVE.md` |
| vì sao đổi mô hình nền | `docs/MODEL_UPGRADE.md` |
| thiết kế thí nghiệm phản thực | `docs/COUNTERFACTUAL_VALIDITY.md` |
| cách hội đồng kiểm chứng | `docs/RESULTS_FROZEN.md` |
| ranh giới phát biểu, văn liệu | `docs/RELATED_WORK.md`, `docs/PAPER_SKELETON.md` |
| các nhánh đã dừng và vì sao | `tools/attic/README.md` |

---

## 6. Giới hạn và sai lệch — phải đọc kèm mọi kết quả ở trên

1. **Không giải thích độ khó với học sinh thật.** Nhãn là mức nhận thức giáo viên
   gán, không phải tỉ lệ trả lời đúng. Đây là giới hạn nặng nhất và **không vá
   được bằng kỹ thuật**.
2. **Không kết luận nhân quả về nhận thức.** "Sửa độ dài phương án làm dự đoán
   dịch 0,14 mức" là mệnh đề về **mô hình**, không phải về đầu học sinh.
3. **Không thay phán đoán giáo viên** — dùng được như gợi ý, không dùng để thay.
4. **Bản thân nhãn chỉ khớp ~0,4.** Trần của mọi mô hình là 0,625 / 0,596. Đây là
   giới hạn của dữ liệu, không phải của phương pháp.
5. **Một nguồn dữ liệu duy nhất, hai môn.** Chưa biết kết quả có chuyển sang nguồn
   khác không.
6. **Ít cặp câu trùng** (71 ở Lý, 53 ở Sử) nên khoảng tin cậy rộng, nhất là ở Sử.
7. **Chỉ hai trục can thiệp được bằng văn bản.** Độ phức tạp lời giải nằm ngoài bề
   mặt câu hỏi và chưa vào được khung này.

**Hai sai lệch phải công bố cùng mọi con số:**

1. **`QDE_DONOR_SEED=42`** cho toàn loạt kiểm tra tỉnh táo — 84 lần chạy dùng
   chung một bộ phản thực thay vì rút lại mỗi lần (nếu không thì riêng bước này
   mất hơn 10 giờ). Tác dụng: phân bố rỗng **hẹp lại** ⇒ phép kiểm **chặt hơn**,
   không phải dễ hơn.
2. **Cổng THEO NHÁNH được chọn SAU khi nhìn số.** Hai cổng kia (`legacy`, `iut`)
   là tiền đăng ký; cổng theo nhánh thì không — nó ra đời sau khi thấy cổng gốc
   cấp nhầm quá nhiều. Mọi chỗ trích dẫn phải nói rõ điều này.

---

## 7. Kế hoạch tiếp theo và ba câu hỏi cần GVHD quyết

### 7.1 Việc kỹ thuật còn lại

| Hạng mục | Chi tiết |
|---|---|
| **Viết chương 6b của bài báo** | phần "lời giải thích chịu được bao nhiêu độ mờ" (mục 4.3) — dữ liệu đã có đủ trong `docs/backend_curve.json`, chỉ còn viết |
| **Vẽ hình H3** | quy kết theo độ mờ — 2 đường (từng cột · theo khối) × 2 môn |
| **Vẽ hình H4** | ρ(sức giải thích, entropy) đổi dấu cùng chỗ ở hai môn |
| **Nguồn dữ liệu thứ hai** | kiểm kết quả có chuyển sang ngân hàng đề khác không (giới hạn số 5) |

### 7.2 Việc KHÔNG làm nữa, và lý do

- **Không crawl thêm dữ liệu trước khi chốt mô hình nền** — đường cong học (mục
  4.4) cho thấy dưới mô hình cũ, tiền crawl gần như đổ đi.
- **Không theo đuổi ngưỡng accuracy** — trần của mọi mô hình là 0,625 / 0,596,
  đặt mục tiêu cao hơn là đặt mục tiêu vào nhiễu của nhãn.
- **Không dùng lời giải thích làm cơ chế từ chối trả lời** — entropy thắng ở cả
  tám ô, đây là kết quả âm đã kiểm đủ.

### 7.3 Ba câu hỏi cần GVHD quyết

1. **Đồ thị tri thức nên đứng ở đâu trong đề tài?** Kết quả hiện tại: trục tri
   thức **bị bác ở 8/8 ô**. Đề xuất chuyển KG từ vị trí *phương pháp chính* sang
   vị trí **kết quả âm đã lặp lại được** — đây là một đóng góp thật (bác một giả
   thuyết có trong văn liệu), nhưng nó đổi hẳn cấu trúc bài báo.
2. **Có đổi tên đề tài theo hướng XAI không?** Tên hiện tại nói "ước lượng độ khó
   bằng đồ thị tri thức", cả hai vế đều không còn mô tả đúng việc đang làm. Tên
   đề xuất ở đầu báo cáo này.
3. **Nhắm hội nghị nào?** Ảnh hưởng tới độ dài, ngôn ngữ và mức chi tiết cần viết
   cho phần phương pháp.

---

*Báo cáo lập ngày 25/09/2026. Mọi con số kiểm lại được bằng*
`python tools/reproduce_all.py --check`.
