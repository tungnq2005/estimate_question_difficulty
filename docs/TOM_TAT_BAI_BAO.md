# Tóm tắt các bài báo nền tảng & hướng phát triển đề tài

*Đọc từ toàn văn (không phải từ abstract). Mục đích: (A) hiểu người ta đã làm
gì; (B) tìm hướng đi tổng quát/sâu hơn cho đề tài.*

---

# PHẦN A — TÓM TẮT TỪNG BÀI

## A1. Survey nền tảng — Benedetto et al. 2022/2023

> *"A Survey on Recent Approaches to Question Difficulty Estimation from Text"*,
> ACM Computing Surveys 55(9):178. DOI 10.1145/3556538. **(35 trang, đã đọc toàn văn)**

**Đây là tấm bản đồ của cả lĩnh vực.** Khảo sát 38 công trình 2015–2021.

**Cách survey chia lĩnh vực làm 2 nửa:**

| | **LA — Language Assessment** (đánh giá năng lực ngôn ngữ) | **CKA — Content Knowledge Assessment** (đánh giá kiến thức nội dung) |
|---|---|---|
| Độ khó đến từ đâu | **Bản thân ngôn ngữ**: từ vựng, cú pháp, độ dài | **Chủ đề kiến thức** được hỏi; cách diễn đạt chỉ ảnh hưởng phụ |
| Phương pháp thịnh hành | Đặc trưng ngôn ngữ học, chỉ số readability | Học sâu end-to-end, đặc trưng học được |
| Cỡ dữ liệu trung bình | 3.975 câu | **28.700 câu** |

**Đề tài của nhóm thuộc CKA.** Và đây là câu quan trọng nhất của survey đối
với nhóm (trích nguyên văn):

> *"in CKA the majority of the difficulty is related to the **topics that are
> assessed** by each question, and only influenced by the wording. Therefore,
> accurate models in CKA need to be able to **model the semantics of the
> question** in order to perform QDET."*

→ **Chính survey khẳng định:** với môn kiến thức nội dung (như Lịch sử), độ khó
nằm ở *tri thức được hỏi*, không phải ở câu chữ. Đây là **luận cứ mạnh nhất
biện minh cho hướng dùng ontology** của nhóm — nó không phải sở thích cá nhân
mà là điều lĩnh vực đã chỉ ra.

**Bốn công trình dùng KG (bảng 15 của survey mô tả nguyên văn):**

| Mã | Bài | Định nghĩa độ khó theo survey |
|---|---|---|
| [107] | Vinu 2015 | *"Difficulty is defined as the **similarity between the correct choice and the distractors**"* |
| [89] | Seyler 2017 | Logistic regression 15 đặc trưng: (i) *entity salience* (đại diện cho độ phổ biến của thực thể), (ii) *coherence của cặp thực thể* (xu hướng cùng xuất hiện trong một ngữ cảnh) |
| [29] | Faizan 2018 | *"average popularity of the entities in the question"* tính từ KG bắt buộc; văn bản chỉ dùng cho NER |
| [55] | Kumar 2019 | *"confidence and selectivity of the question"* tính từ KG bắt buộc; văn bản chỉ dùng cho NER |

**⚠️ PHÁT HIỆN QUAN TRỌNG — cần biết để định vị đúng:** định nghĩa của
**Vinu 2015** (*độ khó = độ tương tự giữa đáp án đúng và đáp án nhiễu*) **chính
là ý tưởng cốt lõi** của nhóm ta (nhóm đặc trưng Jaccard). Vậy ý tưởng gốc
**không mới**. Cái mới của nhóm là: đo nó **trên ontology theo chương trình
học** (không phải KG bách khoa) + **kết hợp tín hiệu ngôn ngữ (PhoBERT)** +
**học có giám sát** thay vì công thức tay + **giải thích được** + **câu hỏi
thật của giáo viên**. Nêu thẳng điều này trong bài báo là **điểm cộng** (chứng
tỏ nắm văn liệu), giấu đi mà bị hội đồng phát hiện thì mất uy tín.

**Một chi tiết đắt giá từ Bảng 13:** cả 4 công trình KG đều có cột *"QDE final
target" = ✗* — nghĩa là ước lượng độ khó chỉ là **mục tiêu trung gian** trong
bài toán sinh câu hỏi tự động, **không phải mục tiêu cuối cùng**. Nhóm ta đặt
QDE làm mục tiêu chính → khác biệt về bản chất bài toán.

**Các kết luận/khuyến nghị khác của survey (rất hữu ích):**

1. **Mọi thành phần của câu hỏi đều ảnh hưởng độ khó** — với MCQ, *cả đáp án
   đúng lẫn đáp án nhiễu* đều tác động. → ủng hộ trực tiếp thiết kế đặc trưng
   Jaccard/distractor-confusion của nhóm.
2. **Dữ liệu bổ trợ cùng chủ đề giúp mô hình hiểu miền** (giáo trình, sách, bản
   ghi bài giảng). → ontology dựng từ SGK chính là dạng dữ liệu bổ trợ này.
3. **Mạng neural end-to-end tốt nhất cho CKA nhưng bị giới hạn bởi cỡ dữ liệu**;
   survey viết: *"A promising alternative, which can be trained on **less
   data**, are keyword-based approaches"*. → **biện minh cho lựa chọn
   XGBoost trên đặc trưng tường minh** của nhóm với 3.152 câu (nhỏ so với mức
   trung bình 28.700 của CKA).
4. **⚠️ Cảnh báo về metric:** *"only a few papers use metrics that are not
   affected by the imbalance classes... which is a problem worth addressing,
   for instance by **avoiding the use of accuracy** and using more robust
   metrics."* → Nhóm đang báo cáo accuracy làm số chính, mà dữ liệu **mất cân
   bằng** (Khó chỉ 16,4%). **Phải bổ sung QWK / macro-F1 / balanced metric.**
5. **Thiếu dataset và code công khai** là vấn đề lớn của lĩnh vực; survey kêu
   gọi cộng đồng chia sẻ code. → **cơ hội đóng góp** cho nhóm (xem C4).
6. **Hướng nghiên cứu survey tự đề xuất** (trích): *"A solution could be for
   these data-driven models to be **combined with features extracted from the
   question text in hybrid approaches which allow continuous QDET updating as
   student data comes in** for new items."* → xem C1, đây là hướng tổng quát
   nhất.

---

## A2. Bài gần nhất về ý tưởng — MDPI MAKE 2026 (KG + LLM + độ khó giải thích được)

> *"Generating Multiple-Choice Knowledge Questions with Interpretable Difficulty
> Estimation using Knowledge Graphs and LLMs"*, MAKE 8(5), DOI 10.3390/make8050137
> (arXiv:2604.10748).

**Rất giống hướng nhóm ta, cần đọc kỹ và trích dẫn.**

- **KG dựng hoàn toàn tự động bằng LLM:** GPT-4o + LangChain `LLMGraphTransformer`
  trích bộ ba (chủ thể–quan hệ–đối tượng) từ 100 bài Wikipedia phổ biến nhất,
  lưu vào Neo4j, tính degree centrality + node embedding (FastRP). **Schema-free**
  — không cần thiết kế lược đồ thủ công.
- **Sinh MCQ:** chọn 40 nút centrality cao làm đáp án đúng; distractor lấy từ KG
  bằng duyệt BFS, cùng kiểu ngữ nghĩa; LLM sinh câu dẫn; LLM kiểm tra distractor
  không vô tình đúng.
- **9 tín hiệu độ khó** (chuẩn hóa [0,1]): số bước suy luận (1-hop/2-hop), có
  thêm bộ ba phụ hay không, độ sâu distractor trong KG, **độ tương tự node
  embedding giữa distractor và đáp án đúng**, **tỉ số tương tự văn bản
  distractor–stem so với đáp-án-đúng–stem**, degree centrality, **chỉ số dễ đọc
  Flesch**, đếm distractor trước "khoảng trống lớn nhất" trong dãy cosine, và
  cờ "stem chứa dữ kiện ngoài đồ thị".
- **"Giải thích được" = phân rã độ khó thành 9 tín hiệu có tên** rồi hồi quy —
  **XGBoost cho kết quả tốt nhất** (giống nhóm ta!).
- **Nhãn thật từ người dùng:** 156 MCQ, ~38 người trả lời/câu, ground truth =
  tỉ lệ trả lời sai. Kết quả: RMSE 0,12–0,13; R² 0,52–0,58; Spearman ρ 64–66%.
  Đặc trưng quan trọng nhất: **độ tương tự embedding văn bản** và **độ dễ đọc**.
- **Hạn chế họ tự nêu:** chỉ 156 câu; chỉ kiến thức tổng quát Wikipedia; chưa
  thử miền chuyên biệt.

**Bài học cho nhóm:** (a) **LLM dựng KG tự động là khả thi và đã được công bố**
— đây là chỗ dựa cho lộ trình hạ chi phí ontology; (b) họ mạnh hơn nhóm ở khâu
**nhãn thật từ người trả lời**, yếu hơn ở **quy mô dữ liệu (156 vs 3.152)** và
**miền chuyên biệt theo chương trình học**; (c) trùng lặp về ý tưởng "phân rã
độ khó thành tín hiệu có tên + XGBoost" → nhóm **phải trích dẫn** và nêu rõ
điểm khác (ontology theo SGK, tiếng Việt, câu hỏi thật của giáo viên).

---

## A3. Venugopal & Kumar 2020 — độ khó theo nhóm năng lực người học

> Semantic Web 11(6):1023–1036. DOI 10.3233/SW-200381.

- Ước lượng độ khó cho câu hỏi **sinh tự động từ ontology**.
- Luận điểm chính: *"a given question is perceived differently by learners of
  various proficiencies"* — **cùng một câu hỏi khó/dễ khác nhau tùy trình độ
  người học**.
- Phương pháp: các metric ontology (popularity, selectivity, coherence,
  specificity) → **3 mô hình logistic regression cho 3 nhóm người học**
  (beginner / intermediate / expert) → dùng **IRT** để tổng hợp ra độ khó chung.
- Kết quả: accuracy CV 76,7% / 78,6% / 84,2% cho 3 nhóm (520 câu, 4 miền).

**Bài học:** đây là bài duy nhất xử lý nghiêm túc chuyện **độ khó có tính tương
đối theo người học** — một chiều mà nhóm ta đang bỏ qua hoàn toàn (nhóm coi độ
khó là thuộc tính tuyệt đối của câu hỏi). Xem hướng C2.

---

## A4. Gherardi et al. AIED 2024 — KG cải thiện QDE từ văn bản

> AIED 2024, LNCS 14830:293–301. DOI 10.1007/978-3-031-64299-9_24.

- Đề xuất **2 cách nhúng thông tin KG vào mô hình QDE văn bản sẵn có**.
- Dataset **Eedi** (công khai, độ khó liên tục kiểu IRT từ dữ liệu học sinh thật).
- Kết quả: **giảm MAE tới 8%** so với baseline mạnh nhất (BERT-based QDE).
- KG ở đây là **taxonomy chủ đề** của đề thi, không phải ontology miền dày.
0
**Bài học:** đây là bằng chứng bình duyệt (AIED — hội nghị uy tín) rằng **thêm
thông tin KG vào mô hình văn bản thì cải thiện được**. Nhóm nên **trích làm chỗ
dựa cho giả thuyết**, đồng thời nêu khác biệt: nhóm dùng ontology dày hơn và
đặt bài toán phân loại thay vì hồi quy.

---

## A5. Wei & Hao 2024 — KGNN-ADP

> IEEE ICETIS 2024:720–727. DOI 10.1109/ICETIS61828.2024.10593775.
> *(Hội nghị hạng thấp — trích dẫn kèm ngữ cảnh, đừng dựa quá nhiều.)*

- Bi-LSTM trích biểu diễn văn bản + KG lấy "knowledge points" liên quan; dự
  đoán độ khó tuyệt đối theo 2 trục: **knowledge difficulty** + **option difficulty**.
- Câu đắt giá để trích trong phần mở đầu báo cáo: *"models for the difficulty
  prediction of MCQ mostly rely only on the features of the question,
  **neglecting the relationship between a question and the involved knowledge
  points** and the connections among these knowledge points."*

**Bài học:** cách chia độ khó thành **2 thành phần** (khó do kiến thức vs khó do
phương án) là một khung phân rã hay, gần với XAI của nhóm.

---

## A6. Thuy, Loginova & Benoit 2025 — tính thứ tự của nhãn độ khó

> EvalLAC'25 @ AIED 2025 (arXiv:2507.00736).

- **Phê phán:** *"the literature has neglected the ordinal nature of the task,
  relying on classification or discretized regression models"* — và các metric
  hiện dùng **không xử lý mất cân bằng lớp** nên đánh giá bị lệch.
- **Đề xuất 1 — Balanced DRPS:** metric xử lý đồng thời *tính thứ tự* và *mất
  cân bằng lớp*.
- **Đề xuất 2 — OrderedLogitNN:** đưa mô hình ordered logit từ kinh tế lượng
  vào mạng neural; tốt hơn rõ rệt trên tác vụ phức tạp (thử trên RACE++, ARC).

**Bài học — áp dụng trực tiếp:** nhóm đang phân loại 3 lớp Dễ/TB/Khó bằng
XGBoost coi 3 nhãn như **danh nghĩa** (đoán nhầm Dễ→Khó bị phạt bằng đoán nhầm
Dễ→TB) — đúng thứ bị phê phán. Cộng với cảnh báo metric của survey (A1, mục 4),
đây là **việc phải sửa**: dùng mục tiêu ordinal + báo cáo QWK/Balanced DRPS.

---

## A7. Acquaye et al. 2026 — mô phỏng học sinh bằng LLM

> arXiv:2601.09953 *(preprint đang bình duyệt)*.

- Thay vì hỏi LLM "câu này khó không", họ **cho LLM đóng vai học sinh** lớp
  4/8/12 theo các mức năng lực, để cả "lớp học ảo" làm bài, rồi **khớp IRT** lên
  kết quả mô phỏng để rút ra tham số độ khó.
- Tương quan với tỉ lệ trả lời đúng thật (NAEP): **0,75 / 0,76 / 0,82**.
- **Phát hiện then chốt:** LLM **chấm trực tiếp** độ khó cho kết quả *kém*;
  chỉ mô phỏng học sinh mới hiệu quả.
- Chi tiết thú vị: dùng **tên học sinh đa dạng** (phân tầng giới tính/sắc tộc)
  cho kết quả tốt hơn dùng ID; và **mô hình toán yếu hơn (Gemma) lại dự đoán độ
  khó thật tốt hơn** mô hình mạnh — vì nó "sai giống học sinh" hơn.

**Bài học:** nhãn 3-phiếu của nhóm **chính là direct judging** — dạng bị bài này
chỉ ra là kém tin cậy. Đây vừa là rủi ro phải thừa nhận, vừa là **cơ hội thí
nghiệm rất hay** (xem C3).

---

# PHẦN B — BỨC TRANH CHUNG RÚT RA

1. **Lĩnh vực đang nghiêng hẳn về học sâu thuần văn bản**, và survey nhận xét
   nghiên cứu QDET đang *"shifting from techniques grounded in linguistic and
   education theory towards approaches solely based on recent ML models"*.
   → Hướng của nhóm (tri thức có cấu trúc + giải thích được) là **đi ngược
   dòng có chủ đích**, và chính survey nói CKA cần mô hình hóa *ngữ nghĩa/chủ đề*
   → nhóm có chỗ đứng.
2. **KG trong QDE vẫn rất thưa và luôn ở vai phụ** (4/38 bài, đều là mục tiêu
   trung gian của sinh câu hỏi). Chưa ai đặt KG làm trung tâm cho **câu hỏi
   thật của giáo viên**.
3. **Chuẩn đánh giá của lĩnh vực còn yếu** — thiếu dataset công khai, thiếu code,
   metric chưa xử lý mất cân bằng. → vừa là rủi ro (khó so sánh) vừa là **cơ hội
   đóng góp**.
4. **Nhãn độ khó là điểm yếu chung của mọi công trình** — người thì dùng chuyên
   gia (đắt, chủ quan), người dùng dữ liệu học sinh (không có lúc cold-start),
   người dùng LLM (mới, đang bị nghi ngờ).

---

# PHẦN C — HƯỚNG TỔNG QUÁT/SÂU HƠN CHO ĐỀ TÀI

*Xếp theo tỉ lệ (giá trị khoa học) / (công sức bỏ ra).*

## C1. ⭐ Cold-start → warm-start: khung cập nhật liên tục *(hướng tổng quát nhất)*

**Chính survey đề xuất hướng này** và chưa ai làm: kết hợp mô hình đặc trưng
văn bản/tri thức (dùng khi câu hỏi còn mới, chưa ai làm) với dữ liệu trả lời
của học sinh khi nó bắt đầu về, **cập nhật liên tục**.

Nâng đề tài từ *"ước lượng độ khó lúc cold-start"* thành *"khung ước lượng độ
khó theo vòng đời câu hỏi"*: ngày 0 dùng KG-features → có 30 lượt trả lời thì
trộn → có 300 lượt thì IRT chiếm ưu thế. Nghiên cứu được câu hỏi hay: **cần bao
nhiêu lượt trả lời thì đặc trưng tri thức hết giá trị?** — đó là một đóng góp
định lượng, tổng quát, không phụ thuộc môn hay ngôn ngữ.

*Chi phí:* cần một đợt thu dữ liệu trả lời nhỏ (1 lớp, ~40 học sinh, ~50 câu là
đã chạy được thí nghiệm mồi).

## C2. ⭐ Độ khó tương đối theo người học

Vấn đề Venugopal 2020 nêu mà nhóm đang bỏ qua: *cùng câu hỏi, học sinh giỏi
thấy dễ, học sinh yếu thấy khó*. Hiện nhóm coi độ khó là thuộc tính tuyệt đối.

Mở rộng: dự đoán **hàm độ khó theo trình độ** thay vì một nhãn. Cách rẻ: yêu
cầu mô hình xuất **phân phối xác suất trên 3 mức** thay vì 1 nhãn cứng, rồi
diễn giải theo nhóm năng lực. Đây cũng là cầu nối tự nhiên sang IRT.

## C3. ⭐ Kiểm chứng nhãn bằng mô phỏng học sinh (thí nghiệm rẻ, giá trị phòng thủ cao)

Theo Acquaye 2026: cho LLM đóng vai học sinh lớp 9 các mức học lực làm 3.152
câu Sử → khớp IRT → so với nhãn 3-phiếu hiện có. Ba kịch bản đều có giá trị:
- Tương quan cao → nhãn được củng cố bằng phương pháp độc lập.
- Tương quan thấp → phát hiện nhãn có vấn đề **trước khi hội đồng phát hiện**.
- Dù sao cũng có một **so sánh 3 nguồn nhãn** (LLM direct / LLM mô phỏng /
  giáo viên) — bản thân nó là một đóng góp nhỏ đáng công bố.

*Chi phí:* thấp, chỉ cần chạy LLM, không cần học sinh thật.

## C4. Công bố dataset + code (đóng góp hạ tầng, survey kêu gọi trực tiếp)

Survey nêu **thiếu dataset và code công khai** là vấn đề của cả lĩnh vực. Nhóm
đang có thứ chưa ai có: **3.152 MCQ Lịch sử tiếng Việt có nhãn 4 mức + ontology
434 thực thể + code pipeline**. Công bố dưới dạng benchmark tiếng Việt đầu tiên
cho QDE = đóng góp được trích dẫn lâu dài, và gần như **không tốn thêm công**
(chỉ cần dọn dẹp + giấy phép + mô tả).

## C5. Sửa phần đánh giá (bắt buộc, rẻ)

- Thêm **QWK / macro-F1 / Balanced DRPS**, không chỉ accuracy (survey mục 4 +
  Thuy 2025).
- Thử **mục tiêu ordinal** thay classification thường.
- **Ablation** KG-features vs PhoBERT thuần vs kết hợp *(vẫn là thí nghiệm quan
  trọng nhất)*.

## C6. Hạ chi phí dựng ontology bằng LLM (trả lời đúng câu hỏi tổng quát hóa)

MDPI 2026 đã chứng minh LLM dựng KG schema-free chạy được. Nhóm làm phiên bản
có kiểm soát: **LLM trích thực thể/quan hệ từ SGK → giáo viên duyệt**, đo
precision/recall so với bản dựng tay của một chương Sử. Ra được con số kiểu
*"tự động hóa được 70% công sức"* → biến điểm yếu "ontology cồng kềnh" thành
một kết quả nghiên cứu.

---

## Gợi ý thứ tự thực hiện

| Ưu tiên | Việc | Vì sao |
|---|---|---|
| 1 | **C5 — Ablation + metric đúng** | Quyết định giá trị bài báo; rẻ; làm được ngay |
| 2 | **C3 — Mô phỏng học sinh kiểm chứng nhãn** | Vá điểm yếu lớn nhất (nhãn LLM); rẻ |
| 3 | **C6 — Pilot LLM dựng ontology** | Trả lời trực tiếp câu hỏi của GVHD về tổng quát hóa |
| 4 | **C4 — Công bố dataset/code** | Gần như miễn phí, giá trị lâu dài |
| 5 | **C1 — Khung cold→warm** | Tham vọng nhất, nâng tầm đề tài; cần dữ liệu học sinh |
| 6 | **C2 — Độ khó theo trình độ** | Chiều nghiên cứu mới; làm sau khi có C1 |
