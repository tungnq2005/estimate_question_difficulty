# Khung bài báo — gộp tài liệu thành cấu trúc viết được

Mục đích: mọi tài liệu rời trong `docs/` được xếp vào đúng một chỗ trong bài,
mỗi bảng/hình được buộc vào file JSON sinh ra nó, và những chỗ **còn thiếu**
được nêu tên thay vì để phát hiện lúc đang viết.

---

## 0. Khung đã chuyển — đọc mục này trước

**Bản trước của tài liệu này lấy A2/H2 làm luận điểm chính** ("độ khó ở miền
cấu trúc do LOẠI thao tác nhận thức quyết định"), đẩy lớp giải thích xuống một
chương ngắn. Khung đã chuyển: **XAI là mạch chính**, các kết quả về trục trở
thành *nội dung mà lời giải thích nói ra*.

**Vì sao chuyển.** Bài toán *dự đoán* độ khó cần ground truth là tỉ lệ trả lời
đúng của học sinh thật — đang bị chặn vì T1 không được duyệt, và không có cách
nào lách. Bài toán *giải thích* thì không cần: đối tượng được giải thích là dự
đoán của mô hình, và tính đúng đắn của lời giải thích được chứng minh bằng
**can thiệp** chứ không bằng việc khớp với phán đoán của người. Đó chính là chỗ
thí nghiệm phản thực thay được cho user study với giáo viên — nguồn lực cũng
đang bị chặn.

**Cái giá phải khai báo.** Vấn đề ground truth không biến mất, nó **đổi chỗ**.
Mô hình học nhãn *mức nhận thức do giáo viên gán theo ma trận đề*, nên lời giải
thích trả lời câu **"cái gì khiến câu này được xếp mức cao trên thang
NB/TH/VD/VDC"**, không phải "cái gì khiến học sinh làm sai". Đây là một
construct có thật và đáng nghiên cứu — nó là thứ quyết định đề thi trông thế nào
trong thực tế Việt Nam — nhưng phải nói rõ ngay ở tóm tắt, không để đến phần
giới hạn.

**Cái không đổi.** Không phép đo nào phải làm lại. Mọi con số trong bảng đóng
băng giữ nguyên. Chỉ đổi thứ tự kể và cái mà tên đề tài hứa.

### 0b. Cập nhật 24/09/2026 — đóng góp mạnh hơn một bậc

Toàn bộ pipeline vừa được chạy lại trên **ba mô hình nền nữa**, với **cùng một
bộ tiêu chí tiền đăng ký, cùng bộ phản thực, cùng hàm `certificate()`**. Bốn mô
hình xếp trên một trục có nghĩa — **tỉ trọng khối lượng quyết định nằm ngoài cột
đặt tên được**: `xgb15` 0 % → `tfidf` ~50 % → `text` ~78–88 % → `emb` 100 %.
Chi tiết: `MODEL_UPGRADE.md` (vì sao đổi) và **`BACKEND_CURVE.md` (bản bốn điểm,
phát biểu cuối)**; ánh xạ vào pipeline: `XAI_PIPELINE.md` §10.

Điều này đổi **loại** đóng góp của bài, không chỉ đổi số:

| | trước 24/09 | sau |
|---|---|---|
| phát biểu về lớp giải thích | "kiểm chứng được **trên một mô hình**" | "kiểm chứng được, và **đo được cái gì chuyển được sang mô hình khác**" |
| kết luận âm về KG | có thể bị phản biện: "tại chọn XGBoost" | **giữ nguyên ở 8/8 ô** (4 mô hình nền × 2 môn) — không còn là tạo tác của mô hình |
| chất lượng mô hình được giải thích | máy–người trên câu trùng 0,091 / 0,003 | **0,472 / 0,369** — ngang người–người (0,391 / 0,355) từ `tfidf` trở đi |
| quy kết TỪNG CỘT | Lý đạt 35 % trần | **rơi đơn điệu** theo độ mờ, về 0 |
| quy kết THEO KHỐI | Lý +0,224 | **+0,329 ở `tfidf`** — cao hơn cả bản cũ |
| số điểm đo | 1 | **4**, trải 0 → 100 % độ mờ |

Phát biểu mới, và nó là thứ nên nằm ở tóm tắt:

> **Độ phân giải của lời giải thích quyết định nó chịu được bao nhiêu độ mờ của
> mô hình nền.** Quy kết TỪNG CỘT rơi đơn điệu khi khối không đặt tên được phình
> ra; quy kết THEO KHỐI thì không, và đạt đỉnh ở mô hình nền giữa. Lớp can thiệp
> giữ nguyên trên toàn dải ở miền cấu trúc.

Đây là một đánh đổi **độ chính xác ↔ khả năng giải thích** đo bằng số trên cùng
một bộ tiêu chí, chứ không phải nhận định. Nó vá đúng lỗ hổng phản biện lớn nhất
của bản trước (*"kết luận của các bạn có phải chỉ đúng cho XGBoost không?"*), và
bản bốn điểm vá nốt cái thứ hai (*"hai điểm thì nối đường nào cũng được"*).

**Một ca đáng đưa vào bài, không phải phụ lục:** dưới `tfidf`, nhánh `kg_near`
của môn Lý QUA luật chứng chỉ gốc (Wilcoxon p = 0,022, đúng hướng đã hứa) nhưng
p hoán vị = 0,150. Tức là **nếu đề tài vẫn dùng luật cũ thì chỉ cần đổi mô hình
nền là kết luận trung tâm đảo chiều.** Đây là bằng chứng sống cho việc vì sao
cổng phải có điều kiện hoán vị — mạnh hơn cả loạt 39 mô hình nhãn xáo, vì nó là
một ca suýt lọt có thật chứ không phải mô phỏng.

**Cái phải hỏi GVHD trước khi viết:** dưới khung này, KG chuyển từ *phương pháp*
sang *kết quả âm đã được lặp lại*. Tên đề tài phải đổi theo. Chưa hỏi.

---

## 1. Tên và tóm tắt

**Tên đề xuất.** *Lớp giải thích tự kiểm chứng cho độ khó câu hỏi trắc nghiệm:
bằng chứng can thiệp từ đồ thị tri thức trên hai miền môn học*

Tên hiện tại ("Ước lượng độ khó câu hỏi trắc nghiệm bằng Đồ thị Tri thức và Học
máy") hứa một hệ **ước lượng** — đúng thứ mà đề tài không có ground truth để
chứng minh. Tên mới hứa đúng cái làm được.

**Sau 24/09 (xem §0b), tên trên vẫn còn hứa hơi quá:** "bằng chứng can thiệp từ
đồ thị tri thức" nghe như KG là phương pháp, trong khi KG giờ là **kết quả âm đã
lặp lại ở bốn mô hình nền**. Hai phương án thay, chờ GVHD chốt:

- *Cái gì trong lời giải thích sống sót khi đổi mô hình? Kiểm chứng bằng can
  thiệp trên bốn mô hình nền và hai miền môn học* — nhấn đóng góp phương pháp.
- *Lời giải thích chịu được bao nhiêu độ mờ của mô hình? Can thiệp, quy kết
  theo khối và quy kết từng cột dưới bốn mô hình nền* — nhấn kết quả.

**Năm câu của tóm tắt** (thứ tự này, mỗi câu một việc):

1. Ước lượng độ khó cold-start bị chặn bởi ground truth; **giải thích** thì
   kiểm chứng được mà không cần dữ liệu học sinh — nêu luôn construct đang
   giải thích là thang nhận thức của ma trận đề.
2. Phê phán đang có với XAI trong giáo dục: quy kết đặc trưng "chỉ mở một cửa
   sổ hẹp" và **không tự mang bằng chứng về độ tin của chính nó**.
3. Đề xuất: pipeline 5 bước dẫn bằng **can thiệp tối thiểu trên văn bản thật**,
   có nhánh đối chứng khớp, có quyền nói "không đủ căn cứ".
4. Kết quả kiểm chứng: lời giải thích can thiệp có độ tin cậy **0,84 / 0,85**;
   quy kết SHAP chỉ đạt **35% / ≈ 0%** trần √ρ tuỳ bộ dữ liệu (biến thể Shapley
   công bằng nhất còn thấp hơn) — và nhìn từ ngoài không phân biệt được nó đang
   ở đâu trên thang đó.
5. **Chạy lại toàn bộ trên bốn mô hình nền** trải từ 0 % tới 100 % khối lượng
   quyết định nằm ngoài cột đặt tên được: lớp can thiệp giữ nguyên, quy kết
   **từng cột** rơi đơn điệu (35 % trần → 0), quy kết **theo khối** thì không
   và đạt đỉnh ở mô hình nền giữa. Đánh đổi độ chính xác ↔ khả năng giải thích
   đo bằng số, và **độ phân giải của lời giải thích quyết định nó chịu được bao
   nhiêu độ mờ**.
6. Kết quả nội dung: lời giải thích nói khác nhau theo miền — trục thao tác ở
   miền cấu trúc (17,5% khoảng cách trong cùng bài, đối chứng 0,85%), trục tri
   thức ở miền tự sự (62,5%), và giả thuyết Vinu 2015 bị bác ở cả hai, ở miền
   cấu trúc còn **đảo dấu** — **kết luận âm này lặp lại ở cả bốn mô hình nền.**

*(Tóm tắt nay 6 câu. Nếu hội nghị giới hạn độ dài, gộp câu 1 và 2 — đừng bỏ
câu 5, đó là câu phân biệt bài này với các bài XAI-giáo-dục một-mô-hình.)*

---

## 2. Bản đồ chương → tài liệu nguồn

| chương | nội dung | nguồn đã có | trạng thái |
|---|---|---|---|
| 1. Mở đầu | vì sao giải thích chứ không dự đoán; construct đang giải thích; bối cảnh thang NB/TH/VD/VDC | `PIVOT_T1_KHONG_DUYET.md` §1–3 + mục 0 trên | **viết mới** |
| 2. Công trình liên quan | QDE + ontology (9 nguồn đã xác minh DOI); phê phán XAI giáo dục 2025–2026 | `RELATED_WORK.md` §1–4 | **dùng gần như nguyên**, cần bổ sung nhánh XAI |
| 3. Dữ liệu & ontology | 1.539 câu Lý + 1.276 câu Sử, hai ontology, sinh đáp án + kiểm mù | `HISTORY_MERGE.md`, `PHYSICS_EXPERIMENT.md` §2–3, `answer_key_report.json` | gộp lại, viết mới phần đáp án |
| **4. Phương pháp — pipeline 5 bước** | chứng chỉ trục · can thiệp từng câu · sàn nhiễu riêng câu · quy kết có kiểm chứng · phát ngôn có quyền im lặng | `XAI_PIPELINE.md` **toàn bộ**, `COUNTERFACTUAL_VALIDITY.md` §3 | **chương lõi, cần viết mới** |
| **5. Kết quả 1 — trục nào tồn tại (B1)** | 8 nhánh × 2 môn qua cửa đối chứng khớp; Vinu bị bác; độ phủ 41,1%/46,5% | `counterfactual_validity*.json`, `xai_coverage*.json`, `COUNTERFACTUAL_VALIDITY.md` §4 | dùng gần như nguyên |
| **6. Kết quả 2 — lời giải thích có đáng tin không** | kiểm tra chéo nửa A/B (độ tin cậy 0,84/0,85); SHAP 35%/≈0% trần √ρ; kiểm tra tỉnh táo cổng B1 bằng nhãn xáo; **khai thác: từ chối có chọn lọc (rỗng) và lời khuyên sửa đề (được)** | `xai_validate*.json`, `xai_selective*.json`, `xai_recourse*.json`, `XAI_PIPELINE.md` §7 + §8b | **đóng góp phương pháp mạnh nhất** |
| **7. Kết quả 3 — hai miền nói khác nhau** | thao tác ở Lý qua ba cửa; tri thức ở Sử 62,5%; trục tri thức đảo dấu; bề mặt là tạo tác của người gán nhãn | `OPERATION_AXIS.md` §1–5, `axis_evidence.json`, `label_source_axes.json` | **cần tách hai miền**, hiện viết theo mạch so sánh |
| 8. Bàn luận & giới hạn | construct đang giải thích; không dữ liệu học sinh; không người chấm thứ hai; độ phủ | `PIVOT_T1_KHONG_DUYET.md` §6, `XAI_PIPELINE.md` §9, `LLM_JUDGE_PHYSICS.md` caveat | gộp lại |
| **6b. Kết quả 4 — cái gì sống sót khi đổi mô hình nền** | bốn mô hình nền trải 0→100 % độ mờ: can thiệp giữ, quy kết từng cột rơi đơn điệu, quy kết theo khối thì không; kết luận âm về KG lặp lại ở 8/8 ô; ca suýt lọt `kg_near`@`tfidf` | **`BACKEND_CURVE.md`**, `MODEL_UPGRADE.md`, `XAI_PIPELINE.md` §10, `backend_curve.json` | **viết mới — đóng góp mới nhất** |
| 9. Tái lập | 18 bước, tách LLM/offline, **hai** bảng mốc × 72 số bị buộc | `RESULTS_FROZEN.md` | **dùng nguyên** |

Thay đổi so với bản trước: chương 4 lên thành chương lõi; ba chương kết quả
chia theo **câu hỏi nghiên cứu** (trục nào tồn tại → lời giải thích có tin được
không → hai miền nói gì) thay vì chia theo **môn**. Hai miền vẫn không so sánh
chéo — chúng nằm cạnh nhau trong chương 7 như hai lần áp dụng cùng một phương
pháp, không phải hai đối thủ.

Tài liệu **không** vào bài, giữ làm phụ lục nội bộ: `PIPELINE_REDESIGN_PLAN.md`,
`DEFERRED.md`, `VERIFY.md`, `BAO_CAO_TIEN_DO*.md` (nhật ký), `TOM_TAT_BAI_BAO.md`
(ghi chú đọc).

---

## 3. Bảng và hình — buộc vào nguồn sinh ra chúng

| # | bảng/hình | vào chương | file nguồn | công cụ sinh |
|---|---|---|---|---|
| H1 | **Sơ đồ pipeline 5 bước** | 4 | — | **THIẾU: chưa vẽ** |
| B1 | Đặc tả dữ liệu hai mảng (n, phân bố 4 mức, nguồn nhãn) | 3 | `mcq_kenhgiaovien.json` ×2 | — (đếm) |
| B2 | Chất lượng đáp án sinh tự động: kiểm mù, tỉ lệ khớp | 3 | `answer_key_report.json` | `llm_answer_key.py` |
| B3 | **Chứng chỉ trục** — 8 nhánh × (Δ, vượt đối chứng, p, đúng hướng) | 5 | `counterfactual_validity*.json` | `xai_difficulty.py --step 1` |
| B9 | Độ phủ can thiệp theo nhánh và theo trục | 5 | `xai_coverage*.json` | `xai_difficulty.py --coverage` |
| B8 | **Kiểm tra chéo XAI** — độ tin cậy Spearman–Brown, trần √ρ, SHAP cây vs Shapley khối trên E[y], KTC bootstrap | 6 | `xai_validate*.json` | `xai_difficulty.py --validate` |
| B13 | **Kiểm tra tỉnh táo cổng B1** — luật cũ vs luật hoán vị trên 39 mô hình nhãn xáo; p hoán vị từng nhánh; ổn định qua seed | 5 | `docs/xai_sanity.json` | `xai_sanity.py` |
| B14 | **Người chấm tự nhiên** — người–người vs máy–người trên cùng câu trùng, trần √, **bốn mô hình nền** | 3 / 6b / 8 | `docs/natural_raters{,_tf,_pb,_eo}.json` | `natural_raters.py` |
| B11 | Đường cong độ phủ ↔ độ chính xác: sức giải thích vs entropy | 6 | `xai_selective*.json` | `xai_difficulty.py --selective` |
| B12 | Sửa tối thiểu làm hệ xếp lại mức, theo hướng | 6 | `xai_recourse*.json` | `xai_difficulty.py --recourse` |
| H2 | Ví dụ chẩn đoán một câu (kgv_0138), 5 phần | 6 | — | `xai_difficulty.py --step 5 --id` |
| B4 | Trục thao tác qua ba cửa (t trong bài, tỉ lệ cặp, can thiệp) | 7 | `axis_evidence.json` | `axis_evidence.py` |
| B5 | Rã đóng góp KG theo kênh (ΔAUC tầng cao vs ΔQWK) | 7 | `operation_axis.json` | `operation_axis.py` |
| B7 | Giữ trục theo nguồn nhãn (bề mặt 37% vs KG 74%) | 7 | `label_source_axes.json` | `label_source_axes.py` |
| B6 | Trước/sau: QWK · AUC · recall VDC, hai mảng | 7 phụ lục | `operation_axis.json`, `ablation_full*.json` | `operation_axis.py`, `ablate_full.py` |
| **B15** | **Bốn mô hình × hai lát cắt** (ngẫu nhiên vs bài chưa gặp), QWK/AUC/acc — luật tay là chỗ nghẽn | 6b | `docs/text_vs_rules.json` | `text_vs_rules.py` |
| **B16** | **Đường cong học theo số BÀI** (25/50/100%) — thêm dữ liệu đáng hay không | 6b | `docs/text_vs_rules.json` | `text_vs_rules.py` |
| **B17** | **72 số, `xgb15` so `text`** — 41 giữ nguyên, 31 đổi, 2 đổi dấu | 6b | `results_frozen*.json` | `backend_diff.py` |
| **B18** | **Bốn mô hình nền × 14 chỉ số** — bảng chính của chương 6b | 6b | `docs/backend_curve.json` | `backend_curve.py` |
| **H3** | **Quy kết theo tỉ trọng khối không đặt tên được** — 2 đường (từng cột ↓, theo khối ↛) × 2 môn, 4 điểm | 6b | `docs/backend_curve.json` | **THIẾU: chưa vẽ** |
| **H4** | **ρ(sức giải thích, entropy) theo tỉ trọng** — đổi dấu cùng chỗ ở cả hai môn | 6b | `docs/backend_curve.json` | **THIẾU: chưa vẽ** |
| **B19** | **p hoán vị của 2 nhánh KG × 4 mô hình nền × 2 môn** — 8 ô, không ô nào < 0,05 | 5 / 6b | `docs/xai_sanity*.json` | `backend_curve.py` |
| B10 | Bảng 72 số đóng băng × **bốn** mô hình nền | 9 | `results_frozen{,_tf,_pb,_eo}.json` | `reproduce_all.py --check` |

B6 xuống phụ lục: dưới khung mới, chỉ số dự báo (QWK/AUC) không còn là kết quả
chính — chúng chỉ dùng để chứng minh mô hình được giải thích là mô hình *có
học được gì đó*, chứ không phải để cạnh tranh với văn liệu.

---

## 4. Còn thiếu — làm trước khi viết

Xếp theo mức chặn:

1. **Chương 4 chưa tồn tại và giờ là chương lõi.** Phần phương pháp hiện nằm
   rải ở `XAI_PIPELINE.md` và `COUNTERFACTUAL_VALIDITY.md` với hai giọng khác
   nhau. Đây là chương người phản biện đọc kỹ nhất, và dưới khung mới nó gánh
   phần đóng góp. *Chặn: cả bài.*
2. **H1 chưa vẽ.** Dưới khung mới sơ đồ pipeline là hình số 1 của bài, không
   còn là minh hoạ phụ. Hiện chỉ có dạng ASCII trong `XAI_PIPELINE.md` §1.
   *Chặn: chương 4.*
3. **Chương 7 đang viết theo mạch so sánh hai môn.** `OPERATION_AXIS.md` dựng
   để trả lời "vì sao môn tự nhiên khác môn xã hội"; khung mới cần nó ở dạng
   "cùng một phương pháp, hai lần áp dụng, kết quả khác nhau". Phải viết lại
   phần dẫn và phần chốt. *Chặn: chương 7.*
4. **Chương 1 phải viết mới hoàn toàn** — bản cũ mở bài theo hướng dự đoán.
5. **Tên đề tài** cần chốt lại với GVHD trước khi viết tóm tắt.
6. **Chương 6b chưa tồn tại** (§0b) — đóng góp mới nhất và chưa có một dòng nào.
   Nguồn đã đủ (`BACKEND_CURVE.md` là bản nháp gần nhất), thiếu phần đặt vấn đề:
   vì sao "cái gì sống sót khi đổi mô hình nền" là câu hỏi đáng hỏi chứ không
   phải một phép kiểm phụ. *Chặn: tóm tắt câu 5.*
7. **H3 và H4 chưa vẽ** — hai hình của chương 6b. Dữ liệu đã có sẵn trong
   `docs/backend_curve.json`, chỉ thiếu hình. *Chặn: chương 6b.*
8. **Ba câu hỏi cho GVHD, chưa hỏi:** (a) chuyển KG từ phương pháp sang kết quả
   âm; (b) đổi tên đề tài theo đó; (c) nhắm hội nghị nào — điều này quyết định
   độ dài và việc có cần phần user study hay không.

Không chặn, làm sau nếu còn thời gian: gộp `explain_difficulty.py` vào
`xai_difficulty.py` (hai công cụ đang trùng vai, và công cụ cũ vẫn dẫn bằng
SHAP — để nguyên thì mâu thuẫn với chính chương 6); rà tay 32 nhóm câu trùng
có nhãn không theo đa số.

---

## 5. Ranh giới phát biểu — cái được nói và cái không

Danh sách đầy đủ ở `RELATED_WORK.md` §6. Những cái dễ lỡ tay nhất khi viết:

**Không được nói**

- ~~"Hệ thống dự đoán được độ khó"~~ — nhãn là **mức nhận thức** giáo viên gán
  theo ma trận đề, không phải tỉ lệ trả lời đúng. Dưới khung mới đây là lỗi
  nặng nhất có thể mắc, vì nó phá đúng cái luận điểm biện minh cho pivot.
- ~~"Lời giải thích cho biết vì sao học sinh làm sai câu này"~~ — cùng lý do.
  Câu đúng: *"vì sao câu này được xếp mức cao trên thang của ma trận đề"*.
- ~~"Lời giải thích giúp mô hình biết khi nào nó không biết"~~ — đã thử và
  KHÔNG được (§8b.1). Ở miền tự sự sức giải thích còn đi cùng chiều với sai lệch
  (ρ +0,138 dưới cổng theo nhánh; +0,249 dưới cổng cũ). Câu đúng: *sức giải thích không phải tín hiệu tự tin*.
- ~~"SHAP không trung thực"~~ — ở miền cấu trúc, **dưới mô hình nền cũ**, SHAP
  đạt 35% trần √ρ (ρ +0,297, p=2e−4). Câu đúng: *SHAP không tự nói cho ta biết
  nó đang ở đâu trên thang đó* — khoảng một phần ba trần ở mảng này, 0 ở mảng
  kia, nhìn từ ngoài không phân biệt được. (Không dùng "41%" — con số cũ, tính
  với trần sai.) **Dưới mô hình nền mới con số này về 0** (ρ −0,050), nên mọi
  lần nêu "35%" phải kèm tên mô hình nền, nếu không là nói quá.
- ~~"Mô hình khớp nhãn ngang một người chấm thứ hai"~~ — đúng/sai **tuỳ mô hình
  nền**, nên phải nói rõ đang nói mô hình nào. Đo trên CÙNG các câu trùng
  (`natural_raters.py`): mô hình **cũ** máy–người 0,091 so với người–người 0,391
  ở Lý, chênh −0,300 [−0,59; −0,04] → *mô hình còn xa trần*. Mô hình **mới**
  0,409, chênh +0,019 [−0,20; +0,21] → được nói *"khớp nhãn giáo viên ở đúng mức
  hai lần soạn đề khớp nhau"*, và **chỉ được nói thế cho mô hình mới**. Ở Sử
  khoảng tin cậy rộng (−0,42; +0,26) nên chỉ nói được *không còn bằng chứng máy
  kém người*, chưa nói được *máy bằng người*.
- ~~"Trục bề mặt đạt chứng chỉ cả hai chiều"~~ / ~~"vượt đối chứng ở p < 0,05 là
  đủ để chứng chỉ"~~ — luật đó cấp chứng chỉ cho 30/39 (Lý), 27/39 (Sử) mô hình
  học trên nhãn xáo (`xai_sanity.py`). Câu đúng: *chiều bớt vượt mọi mô hình
  nhãn xáo ở cả hai môn; chiều thêm thì không chắc*. **Đã chốt cổng theo nhánh**
  (XAI_PIPELINE §2b) — khi viết phải khai rõ luật được chọn SAU khi thấy số, kèm
  kết quả của luật chặt định trước (Lý mất chứng chỉ, Sử đạt 1/4 seed).
- ~~"Đồ thị tri thức không giúp ích cho ước lượng độ khó"~~ — quá rộng. Đúng
  là: *giả thuyết đáp án ↔ nhiễu* bị bác; khối KG vẫn có +0,021 AUC tầng cao ở
  miền cấu trúc sau khi trừ phần rút gọn được về đếm khái niệm.
- ~~"Trục kiến thức không có tác dụng"~~ — nó **đảo dấu theo miền**: Sử t=+2,87,
  Lý t=−3,22. Đảo dấu là kết quả, không phải vắng mặt.
- ~~"Đổi sang mô hình văn bản thì mọi thứ tốt lên"~~ — SAI, và là chỗ dễ lỡ tay
  nhất của phần mới. Quy kết mất tính trung thực, lời khuyên hạ mức rơi gần một
  nửa, Sử **mất** luật CHẶT, và ρ(sức giải thích, entropy) đổi dấu ở cả hai môn.
  Câu đúng: *can thiệp chuyển được, quy kết thì không*.
- ~~"Trước 2024 chưa ai dùng KG cho QDE"~~ — sai, 4 công trình trong survey +
  Venugopal 2020.

**Được nói, kèm điều kiện**

- Mọi con số của lớp giải thích phải kèm **tên mô hình nền** (`xgb15` hay
  `text`). Bảng đối chiếu: `python tools/backend_diff.py`. 31/72 số đổi giữa hai
  mô hình, trong đó **2 số đổi dấu** — không có số nào được phép nêu trần trụi.
- Mọi con số `_pb` phải kèm khai báo `QDE_DONOR_SEED=42` ở loạt kiểm tra tỉnh táo
  (`MODEL_UPGRADE.md` §10): phân bố rỗng hẹp lại ⇒ phép kiểm chặt hơn.
- "QWK 0,551 trên bài chưa gặp" — phải giữ mệnh đề *bài chưa gặp* và nói rõ đây
  là **bài khác trong cùng một nguồn**, không phải bộ dữ liệu khác. Không so
  trực tiếp với mức rơi ≈ 0,28 của Faraji 2026.

- "Trục thao tác giải thích 17,5% khoảng cách độ khó giữa hai câu **cùng bài**"
  — phải giữ nguyên mệnh đề *cùng bài*, bỏ đi là sai.
- "Đối chứng 0,85%" phải đi kèm mỗi lần nêu 17,5%, nếu không con số mất nghĩa.
- Mọi kết luận về trục KG ở mức từng câu chỉ có giá trị trên **41,1% (Lý) /
  46,5% (Sử)** số câu dựng được phản thực — và tập đó đã lệch về phía câu bám
  sát chương trình. Với phần còn lại, phán quyết đúng là *chưa biết*.
- Gherardi 2024: "giảm MAE **tới** 8%" (*up to*), không phải "giảm 8%".

---

## 6. Thứ tự viết đề xuất

Chương **4 → 6 → 6b → 5 → 7 → 3 → 8 → 9 → 1 → 2 → tóm tắt**.

Bắt đầu từ chương 4 vì dưới khung mới nó là đóng góp, và ba chương kết quả chỉ
là nó chạy ra số. Rồi chương 6 ngay sau — chương này là lý do phương pháp tồn
tại, viết sớm để biết chương 4 phải nhấn gì. Chương 6b đi liền sau 6 vì nó là
chương 6 chạy lần thứ hai trên một mô hình khác; viết rời hai chỗ thì sẽ phải
nhắc lại toàn bộ bộ tiêu chí.

Lý do vẫn để chương 1 và tóm tắt sau cùng: phần mở đầu phải hứa đúng cái các
chương kết quả giao được, mà điều đó chỉ biết chắc sau khi viết xong chúng —
và bài học từ lần đổi khung này là hứa trước thì phải viết lại.
