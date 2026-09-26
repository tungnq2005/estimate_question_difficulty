# Related Work & Khoảng trống nghiên cứu

*Trả lời hai câu hỏi của GVHD (07/2026): (1) việc đưa ontology/KG vào ước lượng
độ khó câu hỏi đã có ai làm chưa, khác biệt của nhóm là gì; (2) phương pháp có
tổng quát hóa sang môn khác được không.*

*Mọi khẳng định dưới đây đã được kiểm chứng đối kháng trên nguồn sơ cấp (trích
nguyên văn khi cần); các mục "lưu ý trung thực" là những gì KHÔNG được phép
viết quá tay.*

---

## 1. Đã có ai dùng ontology/KG cho ước lượng độ khó câu hỏi chưa?

**Có, nhưng rất thưa.** Tài liệu định vị chuẩn của lĩnh vực là survey:

> Benedetto, Cremonesi, Caines, Buttery, Cappelli, Giussani, Turrin.
> *"A Survey on Recent Approaches to Question Difficulty Estimation from Text"*,
> **ACM Computing Surveys** 55(9), art. 178 (DOI 10.1145/3556538, online 2022).

Survey khảo sát **38 công trình** (từ 2015) về Question Difficulty Estimation
from Text (QDET), trong đó chỉ **4 công trình dùng Knowledge Graph** (mục
6.1.3, Table 8):

| # | Công trình | Venue | Phương pháp | Kết quả |
|---|---|---|---|---|
| 1 | Vinu et al. 2015 | J. Web Semantics 34 | Sinh MCQ từ domain ontology; độ khó = độ tương tự đáp án đúng–nhiễu trên KG (Closeness/LSR) | 3 lớp, acc 65,3% (baseline ngẫu nhiên 33,3%) |
| 2 | Seyler et al. 2017 | ACM SIGIR ICTIR | Câu hỏi sinh từ KG; logistic regression 15 đặc trưng entity salience + coherence | nhị phân, acc 66,4% / 500 câu |
| 3 | Faizan & Lohmann 2018 | WIMS | Sinh MCQ từ slide bài giảng qua DBpedia; độ khó = nghịch đảo PageRank | đồng thuận người đánh giá 61,6% |
| 4 | Kumar et al. 2019 | ISWC | Sinh câu hỏi multi-hop có kiểm soát độ khó; confidence + selectivity | acc 60–68% |

Nhận xét then chốt của chính survey về cả 4 công trình này (trích nguyên văn):

> *"in all these papers, the text of the questions (and possibly the text of
> the choices) is used for Named Entity Recognition (NER) only... the
> difficulty does not really depend on the verbalization of the question but
> only on the nodes of the graph and the links between them."*

Tức là: cả 4 công trình chỉ dùng văn bản để **định vị nút trên đồ thị**; độ
khó hoàn toàn không phụ thuộc **cách diễn đạt** câu hỏi. Ngoài ra, cả 4 đều
xuất phát từ bài toán **sinh câu hỏi từ KG** (ước lượng độ khó cho câu hỏi
máy sinh), không phải chấm độ khó cho câu hỏi thật do giáo viên soạn.

**Các công trình sau survey (2020–2024) — bắt buộc trích dẫn khi viết báo cáo:**

| # | Công trình | Venue | Phương pháp | Khác biệt chính với nhóm |
|---|---|---|---|---|
| 5 | Venugopal & Kumar 2020, *"Difficulty-level modeling of ontology-based factual questions"* | Semantic Web (IOS) 11(6):1023–1036, DOI 10.3233/SW-200381 | Metric ontology (popularity, selectivity, coherence, specificity) + IRT + 3 mô hình logistic theo nhóm năng lực; 520 câu, 4 miền; acc CV 76,7–84,2% | Câu hỏi **máy sinh từ chính ontology** (không phải MCQ thật); nhãn neo theo IRT + chuyên gia phân nhóm người học; không PLM, không tiếng Việt, không XAI |
| 6 | Gherardi, Benedetto, Matera, Buttery 2024, *"Using Knowledge Graphs to Improve QDE from Text"* | **AIED 2024**, LNCS 14830:293–301, DOI 10.1007/978-3-031-64299-9_24 | Ghép thông tin KG vào mô hình QDE văn bản (BERT); dataset Eedi; **MAE giảm tới 8%** | KG dùng như **taxonomy chủ đề** bổ trợ mô hình BERT hộp đen; bài toán **hồi quy** độ khó liên tục; tiếng Anh |
| 7 | Wei & Hao 2024, *"KG Based Absolute Difficulty Prediction of MCQ"* (KGNN-ADP) | IEEE ICETIS 2024:720–727, DOI 10.1109/ICETIS61828.2024.10593775 | Bi-LSTM trích văn bản + KG lấy knowledge points; dự đoán độ khó tuyệt đối (knowledge + option difficulty) | Mạng neural **khó giải thích**; tiếng Trung; không có cơ chế RSI/Jaccard đa mức trên distractor. *Lưu ý: venue hạng thấp — trích kèm ngữ cảnh* |
| 8 | MDPI MAKE 2026 (DOI 10.3390/make8050137) — sinh MCQ + ước lượng độ khó giải thích được bằng KG+LLM | MAKE 8(5) | **Chưa đọc toàn văn** — cần đối chiếu chi tiết vì gần hướng nhóm nhất về "KG + độ khó giải thích được" | (việc cần làm) |

Điểm đáng giá: chính KGNN-ADP 2024 **xác nhận khoảng trống** nhóm nhắm tới
(trích abstract): *"Currently, models for the difficulty prediction of MCQ
mostly rely only on the features of the question, neglecting the relationship
between a question and the involved knowledge points and the connections
among these knowledge points."*

**Về tiếng Việt:** survey ghi nhận ngôn ngữ các công trình: Anh 33, Đức 3,
Trung 2, Pháp 1, Nga 1 — **không có công trình tiếng Việt nào** (từ "Vietnam"
xuất hiện 0 lần). *Lưu ý trung thực: đây là kết quả từ survey + các đợt tìm
kiếm quốc tế; chưa rà soát hệ thống venue nội địa (RIVF, VLSP, KSE, tạp chí
đại học) — nên ghi là "theo hiểu biết của chúng tôi".*

---

## 2. Khoảng trống nghiên cứu & 5 luận điểm khác biệt

**Khoảng trống:** chưa có công trình nào nằm ở **giao của cả 5 trục** sau.
Không luận điểm nào đứng một mình là "chưa ai làm"; sự khác biệt nằm ở tổ hợp.

1. **Lai ghép hai nguồn tín hiệu.** Bốn công trình KG trong survey chỉ dùng
   văn bản cho NER — độ khó thuần cấu trúc đồ thị. Nhóm kết hợp đặc trưng đồ
   thị (Jaccard 3 mức, RSI, distractor confusion) **với** đặc trưng ngữ nghĩa
   PhoBERT (entropy trên không gian thực thể, cosine stem–đáp án) trong một
   vector 34 chiều. *(Gherardi 2024 cũng lai KG+text nhưng theo kiểu taxonomy
   chủ đề + BERT hộp đen — phải đối chiếu riêng, không được nói "chưa ai lai".)*

2. **Học có giám sát trên đặc trưng tường minh + XAI.** Thay vì heuristic
   (Vinu/Faizan/Kumar) hoặc neural hộp đen (KGNN-ADP, Gherardi), nhóm dùng
   XGBoost trên 34 đặc trưng đặt tên được, kèm phân rã giải thích 4 thành phần
   (TO/EO/SC/DC) — giáo viên đọc được *vì sao* câu khó. *(Lưu ý: Seyler 2017
   có dùng học máy — logistic regression — nên không viết "cả 4 đều heuristic".)*

3. **Nguồn tri thức: ontology miền dày dựng thủ công theo SGK** (434 thực thể,
   761 quan hệ, 8 lớp, 12 kiểu quan hệ, có annotation sư phạm: Bloom,
   abstractness, tần suất SGK) — thay vì KG bách khoa tổng quát
   (DBpedia/YAGO/Wikipedia) hay taxonomy chủ đề mỏng.

4. **Đối tượng và điều kiện: MCQ thật do người soạn, cold-start thuần.**
   Vinu/Venugopal ước lượng độ khó cho câu hỏi **máy sinh từ ontology**; nhãn
   của Venugopal neo theo IRT/nhóm năng lực người học. Nhóm chấm độ khó cho
   ngân hàng câu hỏi thật (3.152 câu), không có bất kỳ dữ liệu trả lời nào.

5. **Ngôn ngữ và miền: tiếng Việt, Lịch sử phổ thông, đa môn.** Không công
   trình QDET tiếng Việt nào trong văn liệu quốc tế; cộng kiến trúc 5 cụm môn
   cho 7 môn lớp 9 (mục 3).

**So sánh kết quả — CẬP NHẬT 07/2026, đọc kỹ:** 4 công trình KG trong survey
đạt 60–68% so với nhãn người đánh giá. Con số 75,6% nhóm từng báo cáo **đã bị
huỷ bỏ**: bộ dữ liệu chứa 54,7% bản sao gây rò rỉ giữa các fold. Sau khử trùng
lặp (2.147 câu duy nhất), kết quả trung thực là **61,6%** cho mô hình đầy đủ —
và baseline TF-IDF thuần văn bản đạt **69,9%**, tức **cao hơn**. Xem mục 5.

---

## 3. Phương pháp có tổng quát hóa sang môn khác không?

*Cách đặt vấn đề: "tổng quát hóa phương pháp" không phải câu hỏi triết học —
nó là câu hỏi kỹ thuật-kinh tế: **muốn áp dụng cho một môn mới thì phải làm
những bước gì, bước nào tốn công nhất, và chi phí đó có hạ được không?**
Điểm nghẽn thẳng thắn: phương pháp cần ontology theo SGK, mà dựng ontology
thủ công thì cồng kềnh. Lập luận dưới đây trả lời trực diện vào điểm nghẽn đó.*

### 3.1. Phương pháp = quy trình 4 bước chuẩn, phần lớn đã tái dùng được nguyên vẹn

Khi áp dụng cho một môn mới, quy trình gồm 4 bước với chi phí biên rất khác nhau:

| Bước | Việc phải làm cho môn MỚI | Chi phí biên thực tế |
|---|---|---|
| 1. Schema cụm (lớp thực thể, kiểu quan hệ, đặc trưng riêng) | Chọn 1 trong 5 cụm có sẵn | **≈ 0** — đã thiết kế xong cả 5 cụm; chỉ môn có hình thái tri thức hoàn toàn mới mới cần cụm mới |
| 2. Nạp thể hiện (instance) tri thức theo SGK | Soạn danh sách thực thể + quan hệ | **Điểm nghẽn** — chi tiết ở 3.2, lời giải ở 3.3 |
| 3. Engine trích đặc trưng + huấn luyện | Không phải viết gì | **= 0** — engine tự phát hiện lớp/cạnh từ ontology (auto-discovery); bằng chứng thực tế: 6 môn ngoài Sử chạy được mà **không sửa một dòng code engine nào** |
| 4. Dữ liệu câu hỏi + nhãn | Thu thập + gán nhãn 3 phiếu + giáo viên duyệt | Quy trình đã chuẩn hóa và kiểm chứng ở môn Sử (3.152 câu, đồng thuận 89,8%) — lặp lại máy móc được |

Nói cách khác: **phương pháp không phải "code cho môn Sử"** — nó là một engine
môn-bất-biến cộng một hợp đồng dữ liệu tối thiểu (thực thể có nhãn/bí danh +
quan hệ có kiểu). Mọi môn thỏa hợp đồng đó đều cắm vào được. Cơ sở lý thuyết
chung (độ khó ≈ độ dễ-nhầm-lẫn giữa các đáp án trên cấu trúc tri thức + mức
chỉ dẫn của stem + độ rộng tri thức; thang NB/TH/VD/VDC của Bộ GD-ĐT định
nghĩa theo thao tác tư duy, không theo nội dung môn) chỉ cần nêu ngắn gọn 1
đoạn — trọng tâm là quy trình.

### 3.2. Định lượng điểm nghẽn: dựng ontology tốn bao nhiêu thật?

Số liệu thật của dự án:

- **Sử (bản chủ lực, làm kỹ nhất):** 434 thực thể + 761 quan hệ + annotation
  sư phạm — đây là mức "trần" về công sức.
- **6 môn còn lại:** mỗi môn chỉ 74–159 thực thể, 94–242 quan hệ — đã đủ để
  pipeline chạy và tính đặc trưng. Mỗi ontology này thực tế được soạn trong
  **thời gian tính bằng ngày, không bằng tháng** (một file dữ liệu Python vài
  trăm dòng).
- Quan trọng: chi phí này là **một lần cho mỗi môn** (ontology theo SGK dùng
  lại cho mọi ngân hàng câu hỏi của môn đó), không phải chi phí lặp lại theo
  từng câu hỏi.

### 3.3. Lời giải cho điểm nghẽn: bán tự động hóa dựng ontology (human-in-the-loop)

Việc dựng KG giáo dục từ tài liệu học tập **đã có cả một nhánh văn liệu**,
tức không phải nhóm tự hứa suông:

- **KnowEdu** (Chen, Lu, Zheng, Chen, Yang — IEEE Access 6:31553–31563, 2018,
  DOI 10.1109/ACCESS.2018.2839607): hệ thống tự động dựng KG giáo dục — trích
  khái niệm giảng dạy bằng neural sequence labeling, trích quan hệ giữa khái
  niệm bằng association rule mining trên dữ liệu học tập.
- **Prerequisite relation learning** (Pan, Li, Li, Tang — ACL 2017, P17-1133):
  tự động học quan hệ tiên quyết giữa các khái niệm từ nội dung khóa học —
  đúng loại cạnh `prerequisiteOf` mà cụm Toán–Lý của nhóm cần.
- **LLM cho KG giáo dục** (ví dụ "Educational Knowledge Graph Creation and
  Augmentation via LLMs", ITS 2024, DOI 10.1007/978-3-031-63031-6_25): hướng
  mới nhất — dùng LLM sinh/mở rộng KG giáo dục.

Kế hoạch cụ thể của nhóm: **LLM trích thực thể + quan hệ từ SGK → giáo viên
kiểm định** — đúng mẫu hình đã kiểm chứng thành công ở khâu gán nhãn (LLM làm
số lượng, con người xác nhận chất lượng, cờ `needs_review` cho chỗ phân vân).
Pilot đo được ngay: cho LLM dựng lại **một chương Sử** đã có bản tay, đo
precision/recall so với bản tay → ra con số "tự động hóa được bao nhiêu %".

**Trade-off có chủ đích (phải nói rõ với hội đồng):** có con đường rẻ hơn là
dùng KG bách khoa sẵn có (DBpedia/Wikidata) — chính là cách 4 công trình trong
survey [1] và Gherardi 2024 [7] đã làm — nhưng văn liệu cho thấy tín hiệu thu
được yếu (60–68%, KG mỏng so với chương trình học). Ontology theo SGK đắt hơn
nhưng chính là nguồn sức mạnh của phương pháp. Vậy câu trả lời đúng cho "cồng
kềnh" **không phải bỏ ontology, mà là hạ chi phí dựng nó** — và chi phí này
đã chứng minh là hạ được (74–159 thực thể/môn là đủ chạy) và còn hạ tiếp được
(bán tự động hóa).

### 3.4. Kế hoạch kiểm chứng khả kiểm sai

- **TN0 — Pilot dựng ontology bán tự động:** LLM dựng lại 1 chương Sử, đo
  precision/recall vs bản tay → định lượng % công sức tiết kiệm cho môn mới.
- **TN1 — Lặp lại trên môn thứ hai** (đề xuất: Địa — cùng cụm đáp án cụm-từ
  với Sử, tái dùng pipeline nguyên vẹn): thu thập + gán nhãn 3 phiếu như quy
  trình Sử. *Tiêu chí thành công định trước:* mô hình dùng đặc trưng tri thức
  vượt baseline thuần văn bản (PhoBERT fine-tune) trên môn mới, đánh giá bằng
  GroupKFold chặn rò rỉ trùng lặp ngay từ đầu — không đặt mục tiêu accuracy
  tuyệt đối nào trước khi có baseline.
- **TN2 — Ổn định cơ chế:** so thứ hạng tầm quan trọng của 3 nhóm đặc trưng
  (dễ-nhầm-lẫn / chỉ dẫn / độ rộng) giữa hai môn — nếu giữ thứ hạng, giả
  thuyết chung được củng cố ở mức cơ chế.
- **TN3 — Chuyển giao:** train trên Sử, đánh giá zero-shot trên môn 2 với các
  đặc trưng bất biến; đo mức suy giảm để định lượng phần tri thức chung.

**Văn liệu định vị:** Benedetto (AIED 2023 [9]) chỉ ra hầu hết nghiên cứu QDET
làm trong "silo" đơn miền, hiệu năng phụ thuộc miền rõ rệt. Câu trả lời của
nhóm không phải một tuyên bố trừu tượng mà là một quy trình 4 bước có bảng
chi phí biên, một điểm nghẽn được nêu tên kèm lộ trình hạ chi phí có văn liệu
chống lưng, và bộ thí nghiệm TN0–TN3 có tiêu chí bác bỏ định trước.

---

## 4. Hai phê phán phương pháp luận từ văn liệu 2025–2026 (cần chủ động thừa nhận)

1. **Nhãn LLM chấm trực tiếp (direct judging).** Acquaye, Huang, Carpuat,
   Rudinger (arXiv:2601.09953, 01/2026, preprint đang bình duyệt): LLM chấm
   trực tiếp độ khó cho kết quả kém; **mô phỏng lớp học** (LLM role-play học
   sinh theo mức năng lực rồi khớp IRT) đạt tương quan 0,75–0,82 với tỉ lệ
   đúng thật (NAEP, môn toán). → Nhãn 3-vote của nhóm là một dạng direct
   judging: cần nêu như **hạn chế** + kế hoạch kiểm chứng (giáo viên duyệt
   124 câu `needs_review` và lớp Khó; cân nhắc pilot IRT nhỏ hoặc mô phỏng
   học sinh). *Lưu ý: kết quả trên miền toán, không phổ quát tuyệt đối.*

2. **Tính thứ tự (ordinality) của nhãn.** Thuy, Loginova, Benoit (EvalLAC'25
   @ AIED 2025, arXiv:2507.00736): văn liệu QDE mức rời rạc bỏ qua tính thứ
   tự Dễ<TB<Khó, chỉ dùng classification thường — đúng mẫu hình XGBoost 3 lớp
   của nhóm. → Hướng cải tiến: mục tiêu ordinal (ordered logit / ordinal
   objective) trên cùng 34 đặc trưng.

**Baseline bắt buộc cho ablation** (đã có trong kế hoạch, văn liệu củng cố):
Benedetto (AIED 2023) cho thấy Transformer fine-tune là baseline mạnh nhất
trên cả ba miền được khảo sát → phải so XGBoost-KG với **PhoBERT fine-tune
thuần văn bản** trên cùng bộ dữ liệu đã khử trùng lặp (2.147 câu duy nhất,
GroupKFold) để định lượng giá trị gia tăng thật của ontology — TF-IDF tuyến
tính đã cho thấy văn bản thuần vượt pipeline tri thức (mục 5), nên PhoBERT
fine-tune gần như chắc sẽ còn vượt xa hơn; câu hỏi mở là ontology có cộng
thêm được gì khi **kết hợp** (stacking) với nó hay không. (BEA 2024 Shared Task cũng cho thấy với dữ liệu nhỏ transformer có
thể không vượt baseline — dữ liệu 3.152 câu của nhóm nằm ở vùng phải kiểm
chứng thực nghiệm.)

---

## 5. Phát hiện rò rỉ dữ liệu và nhãn bề mặt (07/2026) — kết quả trung thực

Sau khi khớp lại toàn bộ 3.152 câu theo nội dung (`tools/dedup.py`), phát hiện
bộ dữ liệu chỉ có **2.147 nội dung câu hỏi khác nhau** — **54,7%** số câu là
bản sao (crawl trùng lặp từ nhiều trang mirror cùng một ngân hàng gốc). Đánh
giá 5-fold CV ngẫu nhiên trước đó để bản sao rơi vào cả tập train lẫn test,
mô hình học thuộc lòng thay vì học quy luật → mọi chỉ số bị thổi phồng.

**Kết quả trước/sau khi chặn rò rỉ (khử trùng lặp, 5-fold CV cùng seed):**

| Mô hình | Accuracy (còn rò rỉ) | Accuracy (đã khử) |
|---|---|---|
| XGBoost 41 đặc trưng (đầy đủ) | 75,6% | **61,6%** |
| Chỉ đặc trưng tri thức (KG+KAD) | 74,7% | **55,9%** |
| TF-IDF + Logistic (chỉ văn bản) | 82,2% | **69,9%** |

Hai quan sát cần báo cáo trung thực với hội đồng:

1. **TF-IDF thuần văn bản vượt toàn bộ pipeline tri thức** (69,9% so với
   61,6%) sau khi loại rò rỉ — pipeline KG hiện tại chưa chứng minh được giá
   trị gia tăng so với một baseline rẻ hơn nhiều.
2. **Cụm từ quyết định nhãn TF-IDF là khuôn mẫu câu hỏi, không phải nội
   dung tri thức**: "quốc gia nào"/"nước nào"/"năm" → Dễ; "nguyên nhân"/
   "không phải là" → Trung bình; "điểm tương đồng"/"so với"/"điểm khác
   biệt" → Khó. Đây là bằng chứng thực nghiệm độc lập, cùng hướng với
   Acquaye et al. 2026 [11]: LLM chấm trực tiếp có xu hướng mã hoá *dạng
   câu hỏi* hơn là *độ khó thật của nội dung*.

Hệ quả cho thiết kế nghiên cứu: (a) mọi đánh giá từ đây về sau bắt buộc dùng
tập đã khử trùng lặp hoặc GroupKFold theo `dup_group`; (b) cần nhãn tham
chiếu độc lập với LLM (khảo sát học sinh + giáo viên xác nhận, đang tiến
hành) trước khi kết luận pipeline tri thức có tác dụng hay không; (c) baseline
TF-IDF/PhoBERT fine-tune là ngưỡng bắt buộc phải vượt qua, không phải tuỳ chọn.

---

## 6. Các diễn đạt BỊ BÁC khi kiểm chứng — KHÔNG dùng trong báo cáo

- ~~"Trước 2024 chưa ai dùng KG cho QDE"~~ (sai — 4 công trình trong survey + Venugopal 2020).
- ~~"Cả 4 công trình KG đều là heuristic, không học máy"~~ (Seyler 2017 dùng logistic regression).
- ~~"Nghiên cứu so sánh 2023 không có phương pháp KG nên củng cố khoảng trống"~~ (lập luận sai hướng).
- Khi trích Gherardi 2024: viết "giảm MAE **tới** 8%" (up to), không phải "giảm 8%".
- Khi trích survey: "38 công trình", không phải "hơn 40".

## Nguồn chính (đã xác minh từng mục: tên bài, tác giả, venue, DOI)

1. L. Benedetto, P. Cremonesi, A. Caines, P. Buttery, A. Cappelli, A. Giussani,
   R. Turrin. *"A Survey on Recent Approaches to Question Difficulty Estimation
   from Text."* ACM Computing Surveys 55(9), art. 178, 2023 (online 2022).
   DOI: 10.1145/3556538.
2. E.V. Vinu, P. Sreenivasa Kumar. *"A novel approach to generate MCQs from
   domain ontology: Considering DL semantics and open-world assumption."*
   Journal of Web Semantics 34:40–54, 2015. DOI: 10.1016/j.websem.2015.05.005.
3. D. Seyler, M. Yahya, K. Berberich. *"Knowledge Questions from Knowledge
   Graphs."* ACM SIGIR ICTIR 2017 (arXiv:1610.09935).
4. A. Faizan, S. Lohmann. *"Automatic Generation of Multiple Choice Questions
   from Slide Content using Linked Data."* WIMS 2018, art. 32:1–8.
5. V. Kumar, Y. Hua, G. Ramakrishnan, G. Qi, L. Gao, Y.-F. Li.
   *"Difficulty-Controllable Multi-hop Question Generation from Knowledge
   Graphs."* ISWC 2019, LNCS 11778:382–398. DOI: 10.1007/978-3-030-30793-6_22.
6. V.E. Venugopal, P.S. Kumar. *"Difficulty-level modeling of ontology-based
   factual questions."* Semantic Web 11(6):1023–1036, 2020. DOI: 10.3233/SW-200381.
7. E. Gherardi, L. Benedetto, M. Matera, P. Buttery. *"Using Knowledge Graphs
   to Improve Question Difficulty Estimation from Text."* AIED 2024,
   LNCS 14830:293–301. DOI: 10.1007/978-3-031-64299-9_24.
8. L. Wei, G.-S. Hao. *"Knowledge Graph Based Absolute Difficulty Prediction
   of Multiple Choice Question."* IEEE ICETIS 2024:720–727.
   DOI: 10.1109/ICETIS61828.2024.10593775.
9. L. Benedetto. *"A quantitative study of NLP approaches to question
   difficulty estimation."* AIED 2023. DOI: 10.1007/978-3-031-36336-8_67
   (arXiv:2305.10236).
10. T.N.D. Thuy, E. Loginova, D.F. Benoit. *"Ordinality in Discrete-level
    Question Difficulty Estimation: Introducing Balanced DRPS and
    OrderedLogitNN."* EvalLAC'25 @ AIED 2025, CEUR-WS Vol-4006
    (arXiv:2507.00736).
11. C. Acquaye, J. Huang, M. Carpuat, R. Rudinger. *"Take Out Your
    Calculators: Estimating the Real Difficulty of Question Items with LLM
    Student Simulations."* arXiv:2601.09953, 2026 (preprint đang bình duyệt).
12. (Cần đọc toàn văn) MDPI Machine Learning and Knowledge Extraction 8(5),
    2026. DOI: 10.3390/make8050137 (arXiv:2604.10748) — sinh MCQ + độ khó
    giải thích được bằng KG+LLM.
13. P. Chen, Y. Lu, V.W. Zheng, X. Chen, B. Yang. *"KnowEdu: A System to
    Construct Knowledge Graph for Education."* IEEE Access 6:31553–31563,
    2018. DOI: 10.1109/ACCESS.2018.2839607.
14. L. Pan, C. Li, J. Li, J. Tang. *"Prerequisite Relation Learning for
    Concepts in MOOCs."* ACL 2017 (P17-1133).
15. *"Educational Knowledge Graph Creation and Augmentation via LLMs."*
    Generative Intelligence and Intelligent Tutoring Systems (ITS) 2024.
    DOI: 10.1007/978-3-031-63031-6_25.

---

## 7. Cập nhật 09/2026 — văn liệu cho khung "giải thích, không cần người"

*Bối cảnh: đề tài không có mẫu người nào (không học sinh, không giáo viên chấm).
Mục này trả lời: hướng XAI hiện tại có đứng được trong văn liệu không, và chỗ
nào phải đổi. Mỗi nguồn đã được mở ra kiểm; chỗ nào mới đọc tóm tắt thì ghi rõ.*

### 7.1. Nhãn mức nhận thức KHÔNG phải độ khó thực nghiệm

- **Hamamoto Filho et al. 2020** (São Paulo Med J; 119 câu, 771 sinh viên):
  độ khó giữa các mức Bloom không khác nhau (F = 0,993; p = 0,374), tương
  quan ρ = 0,172 (p = 0,06). Hội đồng chuyên gia đoán độ khó chỉ khớp **54%**,
  dù xếp đúng thứ tự (độ khó trung bình 0,28 / 0,37 / 0,49; p < 0,01).
- **Zotos et al. 2025** (workshop AISEER @ ECAI 2025): giảng viên phân biệt
  câu dễ/khó kém, thua cả việc hỏi thẳng Gemini 2.5 (câu Đúng/Sai, mạng nơ-ron
  và học máy). *Mới đọc tóm tắt.*

→ Thứ đề tài giải thích là **mức nhận thức giáo viên gán**, và văn liệu cho
thấy nó không trùng với độ khó thực nghiệm. Phải gọi đúng tên construct.

### 7.2. Người gán mức nhận thức vốn không khớp nhau — và dữ liệu đề tài cũng vậy

- **Karpen & Welch 2016** (Curr. Pharm. Teach. Learn. 8(6):885–888): với 6 mức
  Bloom, độ tin cậy giữa người chấm 0,25, độ đúng 46,0%; gộp còn 3 mức thì độ
  đúng lên 81,8%. *Chỉ 6 câu ví dụ — phải trích kèm cỡ mẫu.*
- **Người chấm tự nhiên trong dữ liệu đề tài** (`tools/natural_raters.py` →
  `docs/natural_raters.json`): cùng một câu (câu dẫn, phương án, đáp án y hệt)
  xuất hiện hai lần và được gán nhãn riêng. Máy được đo trên **chính các câu
  đó**, chia lát theo nhóm câu dẫn (không bản sao nào vừa học vừa kiểm).
  Bootstrap 2.000 lần theo nhóm, seed 42:

| | Lý (71 cặp · 69 nhóm) | Sử (53 cặp · 49 nhóm) |
|---|---:|---:|
| người ↔ người, 4 mức — QWK | 0,391 [0,20; 0,58] | 0,355 [−0,05; 0,81] |
| người ↔ người, khớp tuyệt đối | 46,5% | 75,5% |
| người ↔ người, 2 tầng NB+TH / VD+VDC — κ | 0,431 [0,19; 0,66] | 0,493 [−0,05; 1,00] |
| **máy ↔ người, cùng các câu đó — QWK** | **0,091** [−0,10; 0,28] | **0,003** [−0,23; 0,27] |
| **chênh máy − người** | **−0,300** [−0,59; −0,04] | −0,352 [−0,93; +0,11] |
| trần mô hình hoàn hảo ≈ √(người ↔ người) | 0,625 | 0,596 |
| (tham chiếu) máy ↔ nhãn trên toàn bộ câu, chia lát theo nhóm | 0,380 | 0,137 |

→ Độ tin cậy nhãn cùng tầm với văn liệu Bloom. Gộp tầng chỉ làm κ nhích (0,39 →
0,43 ở Lý, khoảng tin cậy chồng nhau) — ủng hộ **yếu** cho việc dẫn bằng AUC
tầng cao.

⚠️ **Đính chính (09/2026).** Bản trước của mục này viết *"ở môn Lý, mô hình khớp
nhãn ngang mức nhãn khớp với chính nó"*. Phép so đó đặt số của mô hình trên
**toàn bộ** câu (chia lát ngẫu nhiên, 0,406) cạnh số người–người trên **riêng**
71 cặp câu trùng — hai tập câu khác nhau. Đo lại trên **cùng** các câu, máy chỉ
đạt 0,091, kém một lần gán nhãn khác có ý nghĩa ở môn Lý. **Mô hình không ngang
người chấm thứ hai, và còn xa trần.** Không dùng câu cũ.

*Giới hạn: cặp ít; câu bị lặp có thể là loại câu đặc biệt (máy làm trên chúng
kém hẳn mức chung 0,380); cùng một website nên đây là độ nhất quán của quy trình
gán nhãn, chưa hẳn của hai giáo viên độc lập.*

### 7.3. Đánh giá XAI không cần người là một cấp được công nhận

- **Doshi-Velez & Kim 2017** (arXiv:1702.08608): ba cấp đánh giá —
  *application-grounded* (chuyên gia, việc thật), *human-grounded* (người
  thường, việc đơn giản hoá), *functionally-grounded* (không người, dùng đại
  lượng thay thế). Đề tài nằm ở cấp thứ ba.
- **Nauta et al. 2023** (ACM Computing Surveys; arXiv:2201.08164): rà hơn 300
  bài giới thiệu phương pháp XAI — 1/3 chỉ đánh giá bằng ví dụ minh hoạ, 1/5 có
  người dùng. Đề xuất 12 thuộc tính (Co-12) để đánh giá định lượng.

→ Không có người **không phải** lỗ hổng phương pháp; lỗ hổng là đánh giá bằng
ví dụ minh hoạ. Pipeline đã đo định lượng. Đề xuất ánh xạ (cần đối chiếu định
nghĩa Co-12 trong bài gốc trước khi viết):

| thuộc tính Co-12 | số liệu đã có |
|---|---|
| Correctness | can thiệp vs mức nhiễu (B2–B4); SHAP vs can thiệp (§0b, §7 XAI_PIPELINE); **kiểm tra tỉnh táo cổng B1 bằng mô hình nhãn xáo** (Adebayo et al. 2018 — `xai_sanity.py`) |
| Consistency | kiểm tra chéo hai nửa ρ ≈ 0,72–0,73 → độ tin cậy Spearman–Brown 0,84–0,85; chứng chỉ trục giữ nguyên qua 4 seed |
| Confidence | "KHÔNG KẾT LUẬN" + thử từ chối có chọn lọc (kết quả âm/không) |
| Contrastivity | lời khuyên sửa đề (recourse) |
| Coherence | trục có lý thuyết đỡ (7.5) |
| Completeness (một phần) | độ phủ phản thực 41–100% |

### 7.4. Can thiệp bằng ví dụ thật có văn liệu đỡ; SHAP thì không

- **CEBaB** (Abraham et al., NeurIPS 2022; arXiv:2205.14140): benchmark có phản
  thực do người viết làm chân lý. Nguyên văn: *"our approximate counterfactual
  baseline proves to be the best method at capturing both the direction and
  magnitude of the effects"* — thắng gần hết các phương pháp, kể cả TCAV,
  ConceptSHAP, CausaLM, INLP. "Approximate counterfactual" = lấy **ví dụ thật**
  trong dữ liệu mang giá trị khái niệm đích. Phép sửa bằng nhiễu thật lấy từ câu
  khác của đề tài cùng họ với cách này.
- **Công trình gần nhất giải thích bằng SHAP, không kiểm faithfulness:**
  Şakiroğlu, Güvenir, Kaya 2026 (MAKE 8(5); arXiv:2604.10748 — mục 8 ở §1, nay
  đã đọc) — 9 tín hiệu KG + văn bản, 156 câu Wikipedia tiếng Anh, ~38 lượt trả
  lời/câu, ρ = 0,643 với tỉ lệ sai thật; phần giải thích là XGBoost + SHAP,
  không có kiểm tra faithfulness. Cùng mẫu hình: *"Novel Feature-Based
  Difficulty Prediction Method for Mathematics Items Using XGBoost-Based SHAP
  Model"* (Mathematics 12(10):1455, 2024 — mới đọc tiêu đề).

→ Vị trí đóng góp rõ nhất: trên hai miền của đề tài, SHAP chỉ bắt được một phần
nhỏ phản ứng thật khi can thiệp — Lý 35% [18%; 51%], Sử ≈ 0% của trần √ρ kiểm
tra chéo; biến thể công bằng nhất (Shapley theo khối, trên chính E[y], nghĩa can
thiệp) còn thấp hơn: 26% / 3% — tức lớp giải thích mà các công trình gần nhất
đang dùng cần được kiểm, và đề tài đưa ra cách kiểm. *(Bản trước ghi "41% / 0%"
— tính với trần sai ρ thay vì √ρ, nghiêng có lợi cho SHAP.)*

### 7.5. Lý thuyết đỡ cho các trục — bằng chứng trên người học là MƯỢN, không phải của đề tài

- **Trục TRI THỨC** ← Alsubait, Parsia, Sattler (KI 2015, DOI
  10.1007/s13218-015-0405-9): lý thuyết điều khiển độ khó MCQ bằng **độ tương
  tự đáp án–nhiễu trên ontology**; theo chính các tác giả, một nghiên cứu sau với
  học sinh trong điều kiện thi thật xác nhận kết quả. MAKE 2026 dùng cùng giả
  định (nhiễu càng gần/giống đáp án càng khó).
- **Trục THAO TÁC (Lý)** ← Embretson & Daniel 2008 (Psychology Science
  Quarterly 50(3)): các nguồn phức tạp nhận thức dự báo độ khó câu toán.

→ Cách viết đúng: *"hướng tác động lớp giải thích tìm thấy trùng với hướng văn
liệu đã đo trên người học"*. Không viết "đề tài chứng minh trên học sinh".

### 7.6. Hướng không cần người nhưng KHÔNG khuyến nghị lúc này

| hướng | văn liệu | vì sao chưa |
|---|---|---|
| Mô phỏng lớp học bằng LLM | Acquaye 2026 (§4): ρ 0,75–0,82 trên NAEP toán; SMART (arXiv:2507.05129) cần dữ liệu thật để căn chỉnh | tốn lượt gọi LLM; chưa ai kiểm cho Sử/Lý tiếng Việt; chỉ thêm một construct nữa |
| Đám đông nhân tạo | Lalor, Wu, Yu 2019 (EMNLP, D19-1434): IRT từ phản hồi của nhiều mô hình, tương quan trung bình–lớn với tham số từ người (NLI, sentiment) | cần nhiều mô hình giải được đề tiếng Việt; chưa kiểm cho miền này |
| Dữ liệu công khai có người trả lời | NBME/BEA 2024 (667 câu USMLE; phải xin, NBME duyệt bản thảo trước khi công bố); CMCQRD (tiếng Anh; trang lưu trữ ghi all-rights-reserved) | chỉ kiểm được phương pháp, không kiểm được kết luận cho Sử/Lý lớp 9; trục TRI THỨC không mang sang được |

### 7.7. Kết luận cho định hướng

**Không đổi phương pháp — đổi phát biểu.** Giải thích *mức nhận thức giáo viên
gán*, không phải độ khó với học sinh; đánh giá ở cấp functionally-grounded.
Ba đóng góp đứng được mà không cần người, và phần lớn số liệu đã có:

1. Độ tin cậy của nhãn (người chấm tự nhiên) đặt cạnh văn liệu Bloom.
2. SHAP không khớp can thiệp — kiểu bằng chứng CEBaB, phản biện trực tiếp lớp
   giải thích của công trình gần nhất.
3. Đánh giá định lượng lớp giải thích theo Co-12.

Bỏ khỏi kế hoạch: user study, khảo sát, tinh chỉnh hiệu năng (trần ≈ 0,63).

### Nguồn bổ sung (09/2026)

16. P.T. Hamamoto Filho et al. *"Relationships between Bloom's taxonomy,
    judges' estimation of item difficulty and psychometric properties of items
    from a progress test."* São Paulo Medical Journal, 2020. PMID 32321103.
    https://pmc.ncbi.nlm.nih.gov/articles/PMC9673841/
17. L. Zotos et al. *"NLP Methods May Actually Be Better Than Professors at
    Estimating Question Difficulty."* AISEER @ ECAI 2025. arXiv:2508.03294.
18. S.C. Karpen, A.C. Welch. *"Assessing the inter-rater reliability and
    accuracy of pharmacy faculty's Bloom's Taxonomy classifications."* Currents
    in Pharmacy Teaching and Learning 8(6):885–888, 2016.
19. F. Doshi-Velez, B. Kim. *"Towards A Rigorous Science of Interpretable
    Machine Learning."* arXiv:1702.08608, 2017.
20. M. Nauta et al. *"From Anecdotal Evidence to Quantitative Evaluation
    Methods: A Systematic Review on Evaluating Explainable AI."* ACM Computing
    Surveys, 2023. arXiv:2201.08164.
21. E.D. Abraham, K. D'Oosterlinck, A. Feder et al. *"CEBaB: Estimating the
    Causal Effects of Real-World Concepts on NLP Model Behavior."* NeurIPS
    2022. arXiv:2205.14140.
22. M.C. Şakiroğlu, H.A. Güvenir, K. Kaya. *"Generating Multiple-Choice
    Knowledge Questions with Interpretable Difficulty Estimation using
    Knowledge Graphs and Large Language Models."* MAKE 8(5), 2026.
    arXiv:2604.10748.
23. *"Novel Feature-Based Difficulty Prediction Method for Mathematics Items
    Using XGBoost-Based SHAP Model."* Mathematics 12(10):1455, 2024.
    DOI: 10.3390/math12101455.
24. T. Alsubait, B. Parsia, U. Sattler. *"Ontology-Based Multiple Choice
    Question Generation."* KI – Künstliche Intelligenz, 2015.
    DOI: 10.1007/s13218-015-0405-9.
25. S.E. Embretson, R.C. Daniel. *"Understanding and quantifying cognitive
    complexity level in mathematical problem solving items."* Psychology
    Science Quarterly 50(3), 2008.
26. J.P. Lalor, H. Wu, H. Yu. *"Learning Latent Parameters without Human
    Response Patterns: Item Response Theory with Artificial Crowds."*
    EMNLP-IJCNLP 2019 (D19-1434).
27. NBME. *BEA 2024 Shared Task Data.* https://www.nbme.org/bea-2024-shared-task-data
28. J. Adebayo, J. Gilmer, M. Muelly, I. Goodfellow, M. Hardt, B. Kim.
    *"Sanity Checks for Saliency Maps."* NeurIPS 2018. arXiv:1810.03292.
    — phép "data randomization test" dùng cho `tools/xai_sanity.py`.
