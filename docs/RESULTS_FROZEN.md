# Bảng kết quả đóng băng — cách hội đồng kiểm chứng

Công cụ: `tools/reproduce_all.py`
Bảng mốc: **bốn bảng song song**, mỗi mô hình nền một bảng —
`docs/results_frozen{,_tf,_pb,_eo}.json`. Xem mục 5, mục ngày 24/09/2026.

---

## 1. Vấn đề

Mọi con số trong báo cáo nằm rải trong nhiều file JSON, do nhiều công cụ khác
nhau sinh ra, ở nhiều thời điểm khác nhau. Không có gì bảo đảm rằng chạy lại
hôm nay vẫn ra đúng số đã viết — và nếu một hôm nào đó số trôi đi thì cũng
không ai biết.

`tools/reproduce_all.py` biến bảng kết quả của báo cáo thành một **bài kiểm tra
hồi quy**: 72 con số được trích dẫn, mỗi con số buộc vào một đường dẫn khoá cụ
thể trong một file cụ thể, kèm dung sai và chỗ nó được dẫn.

```bash
python tools/reproduce_all.py --list     # kế hoạch: bước nào chạy lại được
python tools/reproduce_all.py --check    # đối chiếu số hiện có với mốc
python tools/reproduce_all.py --run      # chạy lại toàn bộ bước offline
python tools/reproduce_all.py --freeze   # ghi số hiện tại làm mốc mới
```

`--check` thoát với mã 1 nếu có số lệch, nên cắm được vào CI.

---

## 2. Hai loại bước, tách bạch

| loại | số bước | thời gian | chạy lại? |
|---|---:|---:|---|
| **đóng băng (LLM)** | 3 | — | **không** — tốn tiền, không tái lập bit-by-bit |
| **offline** | 15 | ~166 phút | có, seed 42 cố định |

Ba bước LLM (`llm_answer_key`, `llm_solution_trace`, `llm_judge_labels`) sinh ra
**dữ liệu đầu vào**, không sinh ra kết luận. Đầu ra của chúng nằm trong repo
dưới dạng JSON và được coi như dữ liệu đã thu thập, giống như bộ câu hỏi crawl
về. `--list` chỉ kiểm tra file còn đó.

Phân tách này quan trọng khi trình bày với hội đồng: **không có kết luận nào
của đề tài phụ thuộc vào việc gọi lại mô hình ngôn ngữ**. Mười lăm bước offline
đọc JSON đã đóng băng và tái tạo lại toàn bộ bảng số. Bước `xai_sanity` (~20
phút, 84 lần chạy phản thực song song) phải chạy **trước** các bước XAI, vì
cổng chứng chỉ trục đọc phân bố rỗng của nó.

---

## 3. Tái lập có thật không

Chạy lại `operation_axis` (XGBoost out-of-fold, 5 lát, seed 42) rồi `--check`:
kết quả ghi ở mục 5 bên dưới. Đây là phép thử đáng làm vì XGBoost với
`tree_method` mặc định và nhiều luồng có thể cho kết quả lệch nhẹ giữa các lần
chạy trên cùng một máy.

Dung sai được đặt theo nguyên tắc: **rộng bằng mức mà kết luận vẫn giữ nguyên**,
không phải bằng độ chính xác của máy. Ví dụ `t = 21,53` cho dung sai ±0,5 vì
kết luận là "t rất lớn", không phải "t bằng đúng 21,53"; còn `n_prereq_edges`
cho dung sai 0 vì nó là phép đếm.

---

## 4. Số nào bị buộc, và buộc vào đâu

| con số | file | dung sai | dẫn ở |
|---|---|---:|---|
| Lý · trục thao tác, t trong cùng bài | `axis_evidence.json` | 0,5 | BC 1.1 KQ1 |
| Lý · trục thao tác, tỉ lệ cặp thắng | `axis_evidence.json` | 0,01 | BC 1.1 KQ1 |
| Lý · can thiệp khối thao tác, tỉ trọng | `axis_evidence.json` | 0,02 | BC 1.1 KQ1 |
| Lý · đối chứng `kad_path_distance` | `axis_evidence.json` | 0,01 | BC 1.1 KQ1 |
| Lý · trục tri thức chạy ngược, t | `axis_evidence.json` | 0,5 | BC 1.1 KQ3 |
| Lý · AUC tầng cao, thao tác+vết giải | `operation_axis.json` | 0,02 | BC 1.1 KQ2 |
| Lý · QWK, thao tác+vết giải | `operation_axis.json` | 0,03 | BC 1.1 KQ2 |
| Lý · nền bề mặt, QWK | `operation_axis.json` | 0,03 | BC 1.1 KQ2 |
| Lý · số cạnh `prerequisiteOf` | `operation_axis.json` | 0 | BC 1.1 |
| Lý · phản thực `num_down` vượt đối chứng | `counterfactual_validity.json` | 0,02 | XAI B1 |
| Lý · `kg_near` đi đúng hướng (dưới 50%) | `counterfactual_validity.json` | 0,03 | XAI B1 |
| Lý · XAI trần lặp lại | `xai_validate.json` | 0,06 | XAI kiểm tra chéo |
| Lý · XAI, SHAP dự báo nửa B | `xai_validate.json` | 0,08 | XAI kiểm tra chéo |
| Sử · can thiệp khối tri thức, tỉ trọng | `axis_evidence.json` | 0,03 | BC 1.2 |
| Sử · đối chứng `kad_path_distance` | `axis_evidence.json` | 0,01 | BC 1.2 |
| Sử · trục tri thức, t trong cùng ô | `axis_evidence.json` | 0,4 | BC 1.2 |
| Sử · giữ trục bề mặt khi đổi nguồn nhãn | `label_source_axes.json` | 0,05 | BC 1.2 |
| Sử · giữ trục KG khi đổi nguồn nhãn | `label_source_axes.json` | 0,08 | BC 1.2 |
| Sử · phản thực `len_up` vượt đối chứng | `counterfactual_validity_gv.json` | 0,02 | XAI B1 |
| Sử · XAI trần lặp lại | `xai_validate_gv.json` | 0,06 | XAI kiểm tra chéo |
| Sử · XAI, SHAP dự báo nửa B | `xai_validate_gv.json` | 0,08 | XAI kiểm tra chéo |
| Lý · độ phủ trục TRI THỨC | `xai_coverage.json` | 0,01 | XAI độ phủ |
| Lý · độ phủ trục BỀ MẶT | `xai_coverage.json` | 0,01 | XAI độ phủ |
| Sử · độ phủ trục TRI THỨC | `xai_coverage_gv.json` | 0,01 | XAI độ phủ |
| Sử · độ phủ trục BỀ MẶT | `xai_coverage_gv.json` | 0,01 | XAI độ phủ |
| Lý · độ phủ nhánh `num_down` (cổng theo nhánh) | `xai_coverage.json` | 0,01 | XAI độ phủ |
| Sử · độ phủ nhánh `len_down` (cổng theo nhánh) | `xai_coverage_gv.json` | 0,01 | XAI độ phủ |
| *(10 số khai thác 8b.1–8b.3: xem `CLAIMS` trong `reproduce_all.py`)* | `xai_selective*.json`, `xai_recourse*.json` | 0,06–0,08 | XAI khai thác |
| Lý · độ tin cậy lời giải thích (Spearman–Brown) | `xai_validate.json` | 0,05 | XAI kiểm tra chéo |
| Lý · SHAP cây, tỉ lệ trần √ρ | `xai_validate.json` | 0,10 | XAI kiểm tra chéo |
| Lý · Shapley khối trên E[y] dự báo nửa B | `xai_validate.json` | 0,08 | XAI kiểm tra chéo |
| Sử · độ tin cậy lời giải thích (Spearman–Brown) | `xai_validate_gv.json` | 0,05 | XAI kiểm tra chéo |
| Sử · Shapley khối trên E[y] dự báo nửa B | `xai_validate_gv.json` | 0,08 | XAI kiểm tra chéo |
| Lý · người–người trên câu trùng (QWK) | `natural_raters.json` | 0,001 | Nhãn |
| Lý · máy–người trên CÙNG câu trùng (QWK) | `natural_raters.json` | 0,05 | Nhãn |
| Sử · người–người trên câu trùng (QWK) | `natural_raters.json` | 0,001 | Nhãn |
| Sử · máy–người trên CÙNG câu trùng (QWK) | `natural_raters.json` | 0,05 | Nhãn |
| Lý · luật CŨ cấp nhầm cho mô hình nhãn xáo (/39) | `xai_sanity.json` | 5 | XAI kiểm tra tỉnh táo |
| Lý · luật CHẶT cấp nhầm (/39) | `xai_sanity.json` | 1 | XAI kiểm tra tỉnh táo |
| Lý · theo nhánh, cấp nhầm ≥ 1 nhánh (/39) | `xai_sanity.json` | 2 | XAI kiểm tra tỉnh táo |
| Lý · p hoán vị `num_down` | `xai_sanity.json` | 0,02 | XAI kiểm tra tỉnh táo |
| Lý · p hoán vị `num_up` | `xai_sanity.json` | 0,04 | XAI kiểm tra tỉnh táo |
| Sử · luật CŨ cấp nhầm cho mô hình nhãn xáo (/39) | `xai_sanity.json` | 5 | XAI kiểm tra tỉnh táo |
| Sử · luật CHẶT cấp nhầm (/39) | `xai_sanity.json` | 1 | XAI kiểm tra tỉnh táo |
| Sử · theo nhánh, cấp nhầm ≥ 1 nhánh (/39) | `xai_sanity.json` | 2 | XAI kiểm tra tỉnh táo |
| Sử · p hoán vị `len_down` | `xai_sanity.json` | 0,02 | XAI kiểm tra tỉnh táo |
| Sử · p hoán vị `len_up` | `xai_sanity.json` | 0,02 | XAI kiểm tra tỉnh táo |
| Lý/Sử · bài chưa gặp, 15 cột viết tay (QWK) | `text_vs_rules.json` | 0,03–0,04 | MODEL_UPGRADE §3 |
| Lý/Sử · bài chưa gặp, PhoBERT + 15 cột (QWK) | `text_vs_rules.json` | 0,03–0,05 | MODEL_UPGRADE §3 |
| Lý · lát ngẫu nhiên, 15 cột viết tay / TF-IDF | `text_vs_rules.json` | 0,03 | MODEL_UPGRADE §2 |
| Lý/Sử · đường cong 25% số bài, 2 mô hình | `text_vs_rules.json` | 0,03–0,06 | MODEL_UPGRADE §4 |
| Lý/Sử · câu trùng, người–người | `text_vs_rules.json` | 0,01 | MODEL_UPGRADE §5 |
| Lý/Sử · câu trùng, máy–người, 2 mô hình | `text_vs_rules.json` | 0,03–0,04 | MODEL_UPGRADE §5 |

Mười sáu dòng cuối (`text_vs_rules.json`) **không có bản có hậu tố** — một file
chứa cả bốn mô hình, nên cả bốn bảng mốc đọc chung và giá trị giống hệt nhau ở
cả bốn. Cố ý như vậy: đó là hồ sơ **so** các họ mô hình với nhau, không phải kết
quả **của** một họ.

Nguyên tắc chọn: mỗi kết luận trong báo cáo phải có ít nhất một số bị buộc,
**kể cả nhóm đối chứng**. Hai dòng `kad_path_distance ⟨đối chứng⟩` nằm trong
bảng đúng vì lý do đó: nếu một ngày đối chứng đột nhiên lên cao thì thiết kế
đã hỏng, và `--check` phải báo.

---

## 5. Kết quả chạy lại

### 07/09/2026 — `--run --only operation_axis`

Chạy lại bước có XGBoost out-of-fold (5 lát, seed 42, hai môn), mất **131 giây**.
Tám con số lấy từ `operation_axis.json` đối chiếu lại:

| con số | mốc | chạy lại | lệch |
|---|---:|---:|---:|
| AUC tầng cao, thao tác+vết giải | 0,8350 | 0,8350 | +0,0000 |
| QWK, thao tác+vết giải | 0,5569 | 0,5569 | +0,0000 |
| nền bề mặt, QWK | 0,3709 | 0,3709 | +0,0000 |
| số cạnh `prerequisiteOf` | 216 | 216 | 0 |

**Khớp tuyệt đối.** XGBoost trên máy này tất định với seed cố định — không có
trôi số cần dung sai. Dung sai trong bảng mục 4 vì thế là biên an toàn cho việc
đổi máy / đổi phiên bản thư viện, không phải để che nhiễu đang có.

Toàn bộ 21 số: **khớp 21 · lệch 0**.

### 07/09/2026 — `--run --only xai_coverage`

Bước mới, 62 giây. Bốn số độ phủ khớp tuyệt đối. Bảng lên **25 số**.

### 07/09/2026 — thêm hai bước khai thác

`xai_selective` và `xai_recourse` (mục 8b của `XAI_PIPELINE.md`). Bảng lên
**35 số**. Nguyên tắc chọn số ở đây khác các bước trước một điểm đáng nêu:
**đối chứng entropy cũng bị buộc**, không chỉ số của phương pháp mình. Kết luận
"sức giải thích thua entropy" chỉ đứng khi entropy THẬT SỰ đi lên — nếu một ngày
cả hai cùng đi xuống thì phép đo hỏng chứ không phải kết luận đúng.

Bốn số cơ chế (`rho_strength_entropy`, `rho_strength_abserr` × 2 môn) bị buộc vì
kết luận của mục 8b.2 dựa trực tiếp vào chúng — đặc biệt ρ = +0,249 ở môn Sử,
thứ gánh phát biểu "sức giải thích đi sai hướng" sau khi khoảng tin cậy của hiệu
số độ chính xác tỏ ra không ổn định giữa các lần chạy.

Vì sao độ phủ phải bị buộc: mọi kết luận từng câu về trục TRI THỨC chỉ có giá
trị trên 41,1% (Lý) / 46,5% (Sử) số câu dựng được phản thực. Nếu một ngày con
số này tụt mà không ai biết thì phạm vi của kết luận đã đổi trong im lặng.

### 11/09/2026 — tăng độ tin cậy số liệu: hai bước mới, ba đính chính

- **`xai_validate` chạy lại** (seed 42, hai môn, ~4 phút/môn): 4 số cũ khớp
  tuyệt đối. Thêm độ tin cậy Spearman–Brown (0,84 / 0,85), trần đúng √ρ, biến
  thể Shapley theo khối trên E[y], khoảng tin cậy bootstrap. **Đính chính:**
  "SHAP đạt 41% trần" tính với trần sai (ρ thay vì √ρ) → đúng là 35%.
- **`natural_raters`** (bước mới, ~1 phút): câu trùng làm người chấm tự nhiên.
  **Đính chính:** câu "mô hình ngang một người chấm thứ hai" sai — trên cùng các
  câu, máy 0,091 so với người–người 0,391 (Lý).
- **`xai_sanity`** (bước mới, 84 lần chạy phản thực, 10 tiến trình song song,
  275 + 780 giây): luật cổng B1 cấp chứng chỉ cho 30/39 (Lý), 27/39 (Sử) mô
  hình học trên nhãn xáo. **Đính chính:** luật cổng không đủ; luật mới đang chờ
  quyết (`XAI_PIPELINE.md` §2b). Cổng trong mã giữ luật cũ nên các số khai thác
  chưa đổi.
- `counterfactual_validity.py` thêm cờ `--permute-labels`; lần chạy mặc định
  không đổi (các số B1 khớp).
- `--freeze`: bảng lên **54 số** (thêm 19: 5 kiểm tra chéo · 4 người chấm tự
  nhiên · 10 kiểm tra tỉnh táo). `--check`: khớp 54 · lệch 0. Hợp lệ theo mục
  6: thêm số mới có chủ ý; 35 số cũ không đổi giá trị.

### 11/09/2026 (tiếp) — chốt cổng THEO NHÁNH, chạy lại hai bước khai thác

Người dùng chọn cổng theo nhánh (`GATE = "arms"`, `XAI_PIPELINE.md` §2b). Đây là
**đổi phương pháp có chủ ý**, nên đóng băng lại hợp lệ theo mục 6.

- Chạy lại `xai_selective` và `xai_recourse` (seed 42, cấu hình cũ). Ba số lệch
  khỏi mốc, đều do đổi cổng: Lý ρ(sức giải thích, entropy) 0,198 → 0,293; Sử
  ρ(sức giải thích, |sai lệch|) 0,249 → 0,138 (vẫn dương, p = 0,017); Lý sửa
  được xuống mức thấp hơn 51,2% → 33,6%. Các số khai thác khác nằm trong dung
  sai; entropy không phụ thuộc cổng nên không đổi. Kết luận §8b.1–§8b.3 giữ chiều.
- `xai_validate`, `xai_coverage` và các bước B1 không phụ thuộc cổng — không chạy lại.
- Thêm 2 số độ phủ theo nhánh (Lý `num_down` 39,2%, Sử `len_down` 99,7%): phạm vi
  mà trục BỀ MẶT còn nói được dưới cổng mới.
- `--freeze`: **56 số**; `--check`: khớp 56 · lệch 0.

### 24/09/2026 — bảng mốc THỨ HAI cho mô hình nền mới

Đổi mô hình nền của lớp giải thích (lý do và bằng chứng: `docs/MODEL_UPGRADE.md`).
Đây là đổi phương pháp lớn nhất từ trước tới nay, nên **không** đóng băng đè lên
bảng cũ. Thay vào đó dựng **hai bảng song song**:

| `QDE_BACKEND` | mô hình | đầu ra | bảng mốc | `--check` |
|---|---|---|---|---|
| `xgb15` (mặc định) | XGBoost, 15 cột viết tay | `*.json` | `results_frozen.json` | **khớp 72 · lệch 0** |
| `tfidf` | TF-IDF + 15 cột đó | `*_tf.json` | `results_frozen_tf.json` | **khớp 72 · lệch 0** |
| `text` | PhoBERT đóng băng + 15 cột đó | `*_pb.json` | `results_frozen_pb.json` | **khớp 72 · lệch 0** |
| `emb` | PhoBERT đóng băng, KHÔNG cột luật tay | `*_eo.json` | `results_frozen_eo.json` | **khớp 72 · lệch 0** |

```bash
python tools/reproduce_all.py --check                   # bảng cũ
python tools/reproduce_all.py --check --backend tfidf   # và text, emb
python tools/backend_diff.py                            # 72 số: cái nào đổi
python tools/backend_curve.py                           # bảng bốn mô hình nền
```

Bốn mô hình nền xếp theo **tỉ trọng khối lượng quyết định nằm ngoài cột đặt tên
được** (0 % → ~50 % → ~78–88 % → 100 %) — đó là trục của `docs/BACKEND_CURVE.md`.

**Một con số có thể là `null` CÓ CHỦ Ý.** Mô hình nền `emb` không nhận cột luật
tay nào, nên mọi đại lượng quy kết là *không định nghĩa được*, không phải *bằng
0*. `--check` phân biệt hai ca này: `null` khớp `null` là **khớp**, `null` gặp
một con số là **lệch**.

`resolve()` trong `reproduce_all.py` tự dùng bản `_pb` khi có, nên **cùng một
danh sách con số** được đối chiếu ở cả hai chế độ — không có số nào được chọn
sau khi nhìn kết quả.

Cùng lúc, danh sách trích dẫn **tăng từ 56 lên 72 số**: thêm 16 số của hồ sơ đo
đạc `docs/text_vs_rules.json` (bước `text_vs_rules`, ~75′) — bốn mô hình × hai
lát cắt, hai đầu đường cong học, và cặp câu trùng. Trước đây chúng chỉ nằm trong
tài liệu, không có `--check` bảo vệ. Hai bảng mốc được đóng băng lại **sau khi**
`--check` xác nhận 56 số cũ còn khớp, nên 56 giá trị cũ giữ nguyên từng chữ số.

**41/72 số giữ nguyên giữa hai mô hình nền, 31 số đổi.** Ba nhóm, theo chiều:

- **Tốt lên:** máy–người trên câu trùng (Lý 0,091 → 0,409; Sử 0,003 → 0,347);
  Lý `p` hoán vị `num_up` 0,100 → 0,025 (trục BỀ MẶT của Lý qua luật CHẶT); cả
  bốn số từ chối có chọn lọc @20%.
- **Kém đi:** quy kết mất tính trung thực (Lý SHAP → nửa B +0,297 → −0,050;
  Shapley khối +0,224 → +0,036); lời khuyên hạ mức (Lý 33,6% → 20,0%; Sử
  30,8% → 12,8%); Sử `p` hoán vị `len_down` 0,025 → 0,050 (mất luật CHẶT).
- **Đổi dấu — phải đọc kỹ:** ρ(sức giải thích, entropy) ở cả hai môn
  (Lý +0,293 → −0,124; Sử +0,175 → −0,135). Cơ chế ở `XAI_PIPELINE.md` §8b.2 là
  phát biểu về **mô hình nền cũ**, không chuyển sang mô hình mới được.

Sai lệch phải công bố cùng mọi số `_tf` / `_pb` / `_eo`: loạt kiểm tra tỉnh táo
chạy với `QDE_DONOR_SEED=42` (84 lần chạy dùng chung một bộ phản thực). Phân bố
rỗng hẹp lại ⇒ phép kiểm **chặt hơn**, không phải dễ hơn. Riêng `_tf` thêm một
lựa chọn: `C = 16` chọn một lần trên nhãn thật (`tools/pick_c_tfidf.py`), dùng y
hệt cho cả 39 mô hình nhãn xáo.

### 24/09/2026 (tiếp) — hai mô hình nền nữa, để có BỐN điểm thay vì hai

Bản hai-điểm ở trên chịu đúng một phản biện: **hai điểm thì nối đường nào cũng
được.** Đã chạy thêm `tfidf` và `emb` trọn chuỗi, đóng băng thành hai bảng mốc
nữa. Kết quả và phát biểu cuối: `docs/BACKEND_CURVE.md`. Ba điều đáng ghi ở đây:

- **Kết luận âm về KG giữ ở cả 8 ô** (4 mô hình nền × 2 môn), và có một ca suýt
  lọt: dưới `tfidf`, `kg_near` của Lý QUA luật §2 gốc (Wilcoxon p = 0,022, đúng
  hướng) nhưng p hoán vị = 0,150. **Cổng hoán vị là thứ giữ kết luận trung tâm
  đứng yên khi đổi mô hình nền** — bằng chứng tốt nhất cho mục §2b của
  `XAI_PIPELINE.md`.
- **Phát biểu hai-điểm đã được SỬA.** "Quy kết không chuyển được" chỉ đúng cho
  quy kết TỪNG CỘT; quy kết THEO KHỐI không rơi và đạt đỉnh ở `tfidf`
  (Lý +0,329, Sử +0,173 — cao hơn cả `xgb15`).
- **Cơ chế bỏ ngỏ ở §8b.2 đã tìm được**: ρ(sức giải thích, entropy) giảm đơn
  điệu theo tỉ trọng và đổi dấu ở cùng một chỗ ở cả hai môn.

*(cập nhật mục này sau mỗi lần chạy `--run` toàn bộ)*

---

## 6. Khi nào được `--freeze` lại

Chỉ khi **cố ý** đổi phương pháp, và phải ghi lý do vào mục 5 kèm ngày. Đóng
băng lại để "cho nó khớp" sau khi thấy số lệch là làm hỏng toàn bộ mục đích của
công cụ — lúc đó bảng không còn kiểm được gì.

Trình tự đúng khi `--check` báo lệch:

1. tìm ra **vì sao** số đổi (đổi mã? đổi dữ liệu? nhiễu?)
2. nếu là nhiễu và nằm trong dung sai hợp lý → nới dung sai, ghi lý do
3. nếu là đổi phương pháp có chủ ý → sửa số trong báo cáo **trước**, rồi
   `--freeze`
4. nếu không giải thích được → đó là lỗi, không phải là mốc mới
