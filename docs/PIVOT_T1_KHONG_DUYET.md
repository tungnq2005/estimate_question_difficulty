# Chuyển hướng nghiên cứu: T1 không được duyệt (08/2026)

*Ghi lại quyết định, lý do và thiết kế thay thế. Nội dung file này sẽ đi thẳng
vào chương Phương pháp + mục Hạn chế của luận văn — không được giấu việc đổi
thiết kế giữa chừng, vì hội đồng chắc chắn hỏi "vì sao không có học sinh thật".*

---

## 1. Sự kiện

**T1 (xin phép nhà trường tổ chức cho ~150 học sinh làm bài khảo sát) KHÔNG
được duyệt.** Đây là rủi ro số 1 đã ghi sẵn trong kế hoạch 15 tuần, kèm điều
kiện kích hoạt phương án dự phòng — nên đây là **quyết định đã định trước**,
không phải ứng biến vá víu.

**Hệ quả trực tiếp:** không có p-value (tỉ lệ trả lời đúng) từ học sinh thật.
Mất hoàn toàn nguồn ground truth tâm trắc học mà ba đóng góp ban đầu dựa vào.

## 2. Cái gì mất, cái gì còn

| Nguồn nhãn | T1 chặn? | Ghi chú |
|---|---|---|
| p-value từ ~150 HS làm bài qua trường | ❌ **mất** | cần phê duyệt thể chế |
| Nhãn giáo viên (T7) | ✅ **còn** | nhờ 1-2 GV Sử điền form — lời nhờ cá nhân, không cần xin phép trường. **Đây là nguồn nhãn PHI-LLM duy nhất còn lại.** |
| Nhãn 3-phiếu LLM (`llm_vote3`) | ✅ còn | 3.152 câu, nhưng chính nó là *đối tượng bị kiểm toán*, không dùng làm ground truth được |
| Phản hồi mô phỏng bằng LLM đóng vai HS | ✅ còn | không phụ thuộc ai duyệt |

**Điểm mấu chốt phải giữ:** nếu mất nốt nhãn giáo viên thì toàn bộ đề tài trở
thành *LLM kiểm toán LLM* — lập luận vòng tròn, không bảo vệ được. Vì vậy T7
được **nâng từ việc phụ lên việc bắt buộc**.

## 3. Ba đóng góp sau khi chỉnh (đổi thứ tự ưu tiên, không đổi bản chất)

1. **Bộ dữ liệu + ontology tiếng Việt công khai** — *từ phụ thành CHÍNH*.
   3.152 MCQ Lịch sử có nhãn + ontology 480 thực thể / 937 quan hệ + code
   pipeline. Không công trình QDET tiếng Việt nào tồn tại trong văn liệu quốc
   tế (survey ACM CSUR 2023 liệt kê Anh 33 / Đức 3 / Trung 2 / Pháp 1 / Nga 1,
   không có Việt). Đóng góp này **không phụ thuộc bất kỳ phê duyệt nào**.

2. **Kiểm toán nhãn LLM** — vẫn là đóng góp thực nghiệm mạnh nhất, chỉ **đổi
   ground truth**: dùng *nhãn giáo viên* (thật, phi-LLM) + *thiết kế 20 cặp câu
   đối chứng khuôn mẫu* thay cho p-value. Lập luận không đổi: nếu giáo viên gán
   **khác mức** cho cặp câu mà LLM gán **cùng mức**, đó là bằng chứng trực tiếp
   nhãn LLM bám khuôn mẫu câu hỏi chứ không bám độ khó nội dung.

3. **Khung Cold→Warm + k\*** — hạ từ *kết quả thực nghiệm* xuống **đóng góp
   phương pháp luận + minh hoạ trên dữ liệu mô phỏng**. Mọi con số dẫn xuất
   phải ghi rõ "trên phản hồi mô phỏng" ở mọi vị trí xuất hiện.

## 4. Vì sao mô phỏng học sinh KHÔNG phải lập luận vòng tròn

Đây là câu hội đồng sẽ hỏi, phải trả lời được bằng văn liệu:

Acquaye et al. 2026 (arXiv:2601.09953) phân biệt rõ **hai tác vụ khác nhau về
bản chất**:

- **LLM chấm trực tiếp độ khó** (*direct judging*) — chính là `llm_vote3` của
  nhóm. Bài này chỉ ra phương pháp đó cho kết quả **kém**.
- **LLM đóng vai học sinh làm bài** rồi khớp IRT — đạt tương quan **0,75-0,82**
  với tỉ lệ trả lời đúng thật (NAEP).

Dùng cái sau để kiểm toán cái trước là hợp lệ vì chúng là hai tác vụ khác nhau,
có hồ sơ thiên lệch khác nhau — không phải cùng một phép đo tự xác nhận. Tuy
vậy **vẫn phải nêu rõ đây là hạn chế**: cả hai đều là LLM, và tương quan
0,75-0,82 là kết quả của bài gốc trên miền toán tiếng Anh, **không phải** kết
quả của nhóm trên miền Sử tiếng Việt.

## 5. Chi tiết triển khai mô phỏng (`tools/attic/llm_student_sim.py`)

Khác hoàn toàn `tools/attic/llm_persona_pilot.py` (file cũ chỉ là phán đoán thủ công
độ đặc thù δ rồi suy ra đúng/sai bằng hàm bậc thang — **không có LLM nào thật
sự trả lời câu hỏi**). File mới cho LLM **thực sự làm bài**.

**Model:** `deepseek-v4-flash`, **TẮT chế độ suy luận** (`thinking: disabled`).
Đây là lựa chọn có chủ đích, không phải để tiết kiệm chi phí:

- deepseek-v4-* mặc định là model suy luận, sinh ~56 token cân nhắc trước khi
  trả lời. Đo thực tế cho thấy khi bật suy luận, persona "học lực Yếu" vẫn lập
  luận ra đáp án đúng → tỉ lệ đúng kịch trần ở cả 5 mức → p-value mất phương
  sai → vô dụng.
- Học sinh thật trong phòng thi trả lời theo phản xạ, không cân nhắc 56 token.
- Đúng tinh thần phát hiện của Acquaye 2026: model càng ít "nghĩ kỹ" càng mô
  phỏng học sinh tốt (bài gốc: Gemma yếu hơn *dự đoán độ khó thật tốt hơn* model
  mạnh, vì "sai giống học sinh" hơn).

**Bốn cơ chế chống thiên lệch** (thiếu bất kỳ cái nào là số đo vô nghĩa):

1. **Mù hoàn toàn** — prompt không chứa nhãn độ khó, không chứa lời giải
   (`notes`), không đánh dấu đâu là đáp án đúng.
2. **Xáo phương án** tất định theo `(item, persona, rep)` — khử thiên lệch vị
   trí (LLM hay chọn A / chọn đáp án dài nhất). Tất định để tái lập được.
3. **Nhiều lần lặp ở temperature = 1,0** — p-value có phương sai thật thay vì
   một hàm bậc thang tất định.
4. **Tên học sinh đa dạng** cho từng persona (Acquaye 2026: dùng tên thật cho
   kết quả tốt hơn ID vô danh).

**Kiểm định hiệu lực tự động** (script tự chạy sau mỗi lần thu thập): tương
quan hạng ρ giữa mức năng lực τ và tỉ lệ đúng; độ trải giữa mức cao nhất và
thấp nhất; tỉ lệ đúng của mức yếu nhất (phải xuống gần vùng đoán bừa); và mọi
đảo chiều được đối chiếu với 2·sai-số-chuẩn để phân biệt nhiễu lấy mẫu với
hỏng thật. Nếu không đạt, script báo rõ thay vì im lặng cho ra số vô nghĩa.

**Ghi chú về việc siết prompt.** Bản prompt đầu tiên cho persona "Yếu" đạt tỉ
lệ đúng 0,611 — quá cao, đúng kiểu hỏng kinh điển "LLM không chịu đóng vai
dốt". Sau khi viết lại system prompt (nói thẳng *"nhiệm vụ của bạn không phải
là trả lời đúng"*, mô tả cụ thể hành vi đoán bừa, gắn mỗi persona với một điểm
trung bình môn cụ thể), đo lại trên 20 câu × 3 lần lặp:

| | prompt v1 | prompt v2 |
|---|---|---|
| τ=1 (Yếu) | 0,611 | **0,483** |
| τ=4 (Khá) | 0,833 | 0,883 |
| độ trải τ1→τ4 | 22 điểm | **40 điểm** |

Việc siết prompt này **phải được báo cáo**, vì nó là một bậc tự do của người
nghiên cứu (researcher degree of freedom) — không được trình bày như thể prompt
đầu tiên đã chạy tốt.

## 5b. KẾT QUẢ THỰC NGHIỆM (chạy 12/08/2026, 4.996 lượt, 50 lượt/câu × 100 câu)

*Toàn bộ số dưới đây đã được chạy lại ở hai cỡ mẫu (20 và 50 lượt/câu) và
**ổn định** — đây là bằng chứng chúng không phải nhiễu lấy mẫu.*

### 5b.1. Hiệu lực của mô phỏng

| Chỉ số | Giá trị | Ngưỡng |
|---|---|---|
| Tương quan hạng ρ(mức năng lực τ, tỉ lệ đúng) | **+1,000** | đơn điệu hoàn hảo |
| Độ trải τ=1 → τ=5 | 0,348 | đủ phương sai |
| KR-20 theo 3 đề | 0,783 / 0,802 / 0,844 | ≥ 0,70 ✓ |
| Câu có độ phân biệt < 0,2 | 39/100 | ⚠ nêu là hạn chế |
| p_sim trung bình | 0,713 | ⚠ **hiệu ứng sàn** (xem 6.6) |

### 5b.2. E1 — Nhãn LLM đo cái gì? (`tools/e1_label_audit.py`)

**(a) Tương quan trực tiếp:** `corr(llm_vote3, p_sim)` = Pearson −0,258 /
Spearman −0,264. Đúng chiều nhưng **yếu**.

**(b) ⭐ Phép đo chốt hạ — "khuôn mẫu câu dẫn đoán được gì?"** Huấn luyện mô
hình chỉ dùng n-gram *câu dẫn* (không chạm nội dung tri thức) trên 2.047 câu
(đã loại câu khảo sát + bản trùng theo `dup_group`), rồi chấm trên 100 câu:

| Khớp với | Kết quả |
|---|---|
| **nhãn LLM** | accuracy 0,530 vs đoán lớp đa số 0,420 → **+11,0 điểm** |
| **p_sim** | Pearson +0,040 · Spearman +0,091 → **≈ 0** |

→ Cách *hành văn* câu hỏi đoán được nhãn LLM rõ rệt trên mức ngẫu nhiên, nhưng
gần như **không** đoán được học sinh làm đúng hay sai. Đây là bằng chứng trực
tiếp nhất cho luận điểm nhãn LLM mã hoá **dạng câu hỏi**, không mã hoá **độ khó
nội dung**.

**(c) ⭐ Phát hiện mạnh hơn cả thiết kế ban đầu — nhãn LLM không thu hẹp được
độ khó thật.** Hai câu bất kỳ được LLM gán **cùng một mức** vẫn chênh nhau
trung bình **22,2 điểm phần trăm** tỉ lệ làm đúng, trong khi sàn nhiễu do lấy
mẫu chỉ **6,1 điểm**. Ưu điểm so với thiết kế cặp đối chứng: kết luận này áp
dụng cho **toàn bộ tập nhãn**, không phải 20 cặp được chọn lọc.

**(d) ❌ KẾT QUẢ ÂM TÍNH — thiết kế 20 cặp câu đối chứng KHÔNG hoạt động.**
Đây là hạng mục trung tâm của kế hoạch gốc và nó **thất bại**, phải báo cáo:

| | \|Δp_sim\| |
|---|---|
| 20 cặp đối chứng đã thiết kế | 0,188 |
| Hai câu ngẫu nhiên **cùng nhãn LLM** (null, 5.000 hoán vị) | 0,222 |
| | **p = 0,774** |

Các cặp đối chứng **không** lệch nhiều hơn cặp ngẫu nhiên. Proxy
`kg_centrality_mean` dùng để chọn cặp "trọng tâm SGK vs chi tiết ngoài lề" đã
**không bắt trúng** thứ nó định bắt. ⇒ Không được trình bày 20 cặp này như
bằng chứng đặc biệt; dùng phép đo (c) trên toàn tập thay thế.

*Ghi chú phương pháp:* bản đầu dùng Wilcoxon signed-rank là **sai kiểm định** —
nó kiểm "A có hệ thống cao hơn B không", trong khi giả thuyết cần kiểm là
"\|Δ\| có lớn hơn mức ngẫu nhiên không" (dấu của Δ vô nghĩa vì nhãn A/B trong
cặp là tuỳ ý). Đã thay bằng kiểm định hoán vị với null đúng.

### 5b.3. E3 — Cold→Warm (`tools/attic/coldwarm.py`)

MAE(k) với α chọn bằng CV, 50 lượt/câu:

| prior | α | k=0 | k=1 | k=3 | k=10 | k=25 |
|---|---|---|---|---|---|---|
| (a) KG | 2 | 0,2094 | 0,1779 | 0,1450 | 0,1058 | 0,0878 |
| (b) văn bản | 2 | 0,2441 | 0,1909 | 0,1523 | 0,1093 | 0,0895 |
| (c) vô thông tin | 4 | **0,1771** | 0,1567 | 0,1364 | 0,1036 | 0,0854 |

**k\* = 0.** Prior vô thông tin (trung bình toàn cục) tốt hơn cả hai prior mô
hình ngay từ k=0.

### 5b.4. Chẩn đoán k\*=0: "không có tín hiệu" hay "sai hiệu chuẩn"? (`tools/prior_diagnosis.py`)

MAE trộn lẫn hai loại sai khác hẳn nhau về hệ quả — **sai thứ hạng** (prior
không biết câu nào khó hơn, kết luận nặng) và **sai mức/hiệu chuẩn** (xếp hạng
đúng nhưng lệch thang, sửa được). Phải tách trước khi kết luận:

| prior | Pearson | Spearman | MAE gốc | MAE sau hiệu chuẩn lại |
|---|---|---|---|---|
| **KG** | +0,141 | **+0,151** | 0,2065 | 0,2369 |
| **văn bản (TF-IDF)** | +0,085 | **+0,019** | 0,2417 | 0,2346 |
| trung bình toàn cục | — | — | **0,1700** | 0,1700 |

*Sàn nhiễu MAE = 0,0433 — mọi chênh lệch nhỏ hơn mức này không diễn giải được.*

Hai kết luận:

1. **Một phần k\*=0 là lỗi hiệu chuẩn.** `CLASS_TO_P` trong `coldwarm.py` là
   hằng số cứng {Dễ:0,85 · TB:0,55 · Khó:0,25}, mức trung bình ngụ ý 0,550,
   trong khi p_sim trung bình 0,713 — lệch 0,16. Nhưng **sau khi hiệu chuẩn
   lại, prior-KG vẫn thua** (0,2369 ≥ 0,1700), nên kết luận "chưa đủ giá trị
   thực dụng" vẫn đứng vững.
2. **⭐ ĐẢO NGƯỢC THỨ HẠNG so với khi chấm trên nhãn LLM** — phát hiện đáng giá
   nhất của cả phiên:

| Chấm trên | Văn bản (TF-IDF) | Tri thức (KG) |
|---|---|---|
| **nhãn LLM** (5-fold, chống rò rỉ) | **70,3%** accuracy | 60,6% — *thua đậm* |
| **hiệu suất làm bài mô phỏng** | Spearman **+0,019** — *sụp về 0* | **+0,151** — *giữ tín hiệu* |

Đây đúng là điều kế hoạch E2 dự đoán có thể xảy ra: nhãn LLM mã hoá khuôn mẫu
— thứ TF-IDF bắt hoàn hảo; độ khó thật phụ thuộc nội dung — thứ TF-IDF mù tịt.
Nó **khớp và củng cố** kết quả 5b.2 bằng một phép đo hoàn toàn độc lập.

**⚠ Không được thổi phồng:** cả hai prior đều **yếu tuyệt đối** và **đều thua
trung bình toàn cục** về MAE. Phát biểu đúng là *"đặc trưng tri thức giữ được
tín hiệu thứ hạng yếu ở nơi đặc trưng văn bản mất sạch"*, **không phải**
*"KG thắng"*.

## 6. Hạn chế bắt buộc nêu trong luận văn

1. Không có dữ liệu trả lời của học sinh thật; mọi p-value là **mô phỏng**.
2. Tương quan 0,75-0,82 là của Acquaye 2026 trên miền toán tiếng Anh — nhóm
   **chưa** kiểm chứng được con số tương đương cho Sử tiếng Việt (muốn kiểm
   chứng thì lại cần đúng thứ T1 bị chặn).
3. Prompt persona đã qua tinh chỉnh có chủ đích (mục 5) — cần nêu rõ.
4. Nhãn giáo viên có cỡ mẫu nhỏ (1-2 GV × ~120 câu) và không tính được độ tin
   cậy liên-người-chấm nếu chỉ có 1 giáo viên.
5. Mô phỏng dùng 5 persona rời rạc, không phải phân phối năng lực liên tục như
   IRT chuẩn. 50 "học sinh" thực chất là 5 mức năng lực × 10 lần lặp, nên số
   **cỡ mẫu hiệu dụng nhỏ hơn 50** — độ phân biệt từng câu tính như thể 50 học
   sinh độc lập là **lạc quan**.
6. **Hiệu ứng sàn của mô phỏng:** p_sim trung bình 0,713, cao hơn đề trắc
   nghiệm thật ở Việt Nam (thường 0,5–0,6). Persona yếu nhất vẫn đúng ~0,52
   thay vì ~0,35 như học sinh yếu thật. Hệ quả: thang p_sim bị nén ở phía trên,
   và mọi phép đo MAE tuyệt đối (E3) bị ảnh hưởng — các phép đo dựa trên **thứ
   hạng** (Spearman) chịu ảnh hưởng ít hơn nên đáng tin hơn ở đây.
7. **Thiết kế 20 cặp câu đối chứng không hoạt động** (mục 5b.2d) — một hạng mục
   trung tâm của kế hoạch gốc phải bỏ; nêu thẳng thay vì lặng lẽ không nhắc tới.
8. Ma trận đặc trưng dùng cho E3/chẩn đoán (`.cache/history_canonical.features.csv`)
   được sinh **trước** khi hoàn thiện ontology Bài 21–24. Ảnh hưởng dự kiến nhỏ
   (độ phủ thực thể chỉ tăng 0,340→0,354 ở nhóm chương mới, chiếm ~5% tập), nhưng
   **phải sinh lại và chạy lại trước khi đưa số vào luận văn**.

## 7. Việc còn lại theo thứ tự

| # | Việc | Trạng thái |
|---|---|---|
| 1 | Thu nhãn giáo viên trên ~120 câu (form đã dựng sẵn) | ⏳ **đang chờ — đường găng duy nhất còn lại** |
| 2 | Chạy `llm_student_sim.py` đủ 100 câu | ✅ xong (4.996 lượt, 50 lượt/câu) |
| 3 | `item_analysis.py` → p-value, KR-20, độ phân biệt | ✅ xong (mục 5b.1) |
| 4 | E1: kiểm toán nhãn LLM | ✅ xong phần không cần GV (5b.2); phần phân định H_a/H_b **chờ (1)** |
| 5 | E3: `coldwarm.py` → k\* + chẩn đoán prior | ✅ xong (5b.3, 5b.4) |
| 6 | Sinh lại ma trận đặc trưng với ontology đầy đủ rồi chạy lại (4)(5) | ⬜ trước khi viết luận văn |
| 7 | Nhánh đối chứng: chạy lại với `--thinking` bật để kiểm chứng phát hiện "model càng ít nghĩ càng mô phỏng tốt" của Acquaye trên tiếng Việt | ⬜ rẻ, giá trị đối chứng cao |
| 8 | Công bố dataset + ontology + code (đóng góp #1) | ⬜ không phụ thuộc gì |

### 7.1. Vì sao nhãn giáo viên là đường găng thật sự

Toàn bộ kết quả 5b hiện **chưa phân định được hai giả thuyết cạnh tranh**, vì
cả nhãn LLM lẫn phản hồi mô phỏng đều do LLM sinh ra:

| | Dự đoán nếu đúng |
|---|---|
| **H_a** — nhãn LLM đo sai độ khó *(điều ta muốn kết luận)* | \|corr(GV, p_sim)\| **≫** \|corr(LLM, p_sim)\| = 0,264 |
| **H_b** — mô phỏng đo sai độ khó *(chưa loại trừ)* | \|corr(GV, p_sim)\| ≈ 0,264, **cả hai đều thấp** |

Nhãn giáo viên là nguồn phi-LLM **duy nhất** phá được vòng tròn này. Phép phân
định đã cài sẵn trong `tools/e1_label_audit.py`; khi có file GV chỉ cần:

```
python tools/e1_label_audit.py \
    --responses subjects/history/samples/student_responses.LLMSIM_API.csv \
    --teacher <file_GV_export.json>
```

Script tự tính thêm: corr(GV, p_sim), corr(LLM, GV), Cohen's κ giữa LLM và GV,
κ giữa các GV (nếu có ≥2 người chấm), và in thẳng kết luận phân định H_a/H_b.
