# Còn bao nhiêu hiệu năng bỏ trên bàn — và có nên nhặt không

Công cụ: `tools/perf_headroom.py` · kết quả: `docs/perf_headroom.json`,
`docs/leak_check.json`

```bash
python tools/perf_headroom.py --subject both     # so 5 cấu hình
python tools/perf_headroom.py --leak --subject both   # kiểm rò rỉ bản sao
```

---

## 1. Chỗ lệch đã phát hiện

Nhãn NB/TH/VD/VDC là thang **có thứ tự**, nhưng `fit_out_of_fold` học nó bằng
XGBoost multiclass — coi 4 mức là 4 lớp rời rạc, không biết VD gần VDC hơn là
gần NB. Trong khi thước đo chính (QWK) lại phạt theo **bình phương** khoảng
cách. Hàm mất mát và thước đo đang lệch nhau.

Năm cấu hình, cùng 5 lát, cùng seed 42, cùng 15 cột mà lớp giải thích đang dùng:

### Vật lí (1.539 câu)

| cấu hình | QWK | AUC cao | macroF1 | acc | recVD | recVDC |
|---|---:|---:|---:|---:|---:|---:|
| **A · multiclass (đang dùng)** | 0,406 | **0,765** | 0,347 | 0,376 | 0,376 | 0,187 |
| B · + cân trọng số lớp | 0,430 | 0,767 | 0,351 | 0,372 | 0,188 | **0,534** |
| C · hồi quy + làm tròn | 0,403 | 0,756 | 0,309 | 0,392 | **0,559** | 0,009 |
| D · hồi quy + ngưỡng phân vị | 0,467 | 0,756 | **0,381** | 0,391 | 0,322 | 0,352 |
| **E · D + tinh chỉnh** | **0,471** | 0,761 | 0,374 | 0,382 | 0,322 | 0,347 |

### Lịch sử (1.276 câu)

| cấu hình | QWK | AUC cao | macroF1 | acc | recVD | recVDC |
|---|---:|---:|---:|---:|---:|---:|
| **A · multiclass (đang dùng)** | 0,164 | **0,648** | 0,365 | **0,638** | 0,000 | 0,057 |
| B · + cân trọng số lớp | 0,171 | 0,632 | **0,410** | 0,615 | 0,099 | 0,172 |
| C · hồi quy + làm tròn | 0,199 | 0,586 | 0,321 | 0,571 | 0,074 | 0,000 |
| D · hồi quy + ngưỡng phân vị | 0,186 | 0,586 | 0,356 | 0,536 | 0,086 | 0,138 |
| **E · D + tinh chỉnh** | **0,215** | 0,584 | 0,371 | 0,545 | **0,136** | 0,138 |

Ngưỡng ở D/E học từ **phân bố nhãn của lát huấn luyện** rồi mới áp lên lát kiểm
— không nhìn nhãn kiểm, nên không rò rỉ.

---

## 2. Kết quả: có headroom, nhưng hai thước đo bất đồng

Cải thiện QWK có thật: **+0,064 (Lý)**, **+0,051 (Sử)**. Nhưng **AUC tầng cao đi
xuống**, và ở môn Sử đi xuống gần đúng bằng phần QWK thu được (−0,064).

Không cấu hình nào thắng cả hai. Hồi quy có thứ tự xếp hạng 4 mức khớp hơn;
multiclass tách tầng cao (VD+VDC vs NB+TH) tốt hơn. **Phải chọn theo việc định
dùng con số vào đâu** — và đó đúng là câu đã hỏi GVHD trong báo cáo (dẫn bằng AUC
tầng cao hay QWK). Câu trả lời không còn là chuyện trình bày, nó quyết định luôn
cấu hình mô hình.

---

## 3. Kiểm rò rỉ bản sao — nghi ngờ KHÔNG đúng

Bộ Sử có `dup_group`/`is_canonical` và đang lọc; bộ Lý **không có hai trường
đó**, nên đặt ra nghi vấn các bản sao vừa nằm ở tập huấn luyện vừa nằm ở tập
kiểm, làm số của môn Lý cao hơn thực tế. Đã kiểm:

| | Lý | Sử |
|---|---:|---:|
| nhóm trùng câu dẫn (chuẩn hoá) | 101 nhóm · 222 câu (14,4%) | 0 |
| trong đó cùng đáp án | 74/101 | — |
| trong đó **cùng nhãn** | **50/101** | — |
| QWK khi buộc bản sao cùng lát | 0,398 (**−0,009**) | 0,154 (−0,010) |
| AUC khi buộc bản sao cùng lát | 0,757 (−0,008) | 0,669 (+0,021) |

**Không có rò rỉ đáng kể.** Chỉ một nửa số nhóm trùng câu dẫn là bản sao thật —
nửa còn lại là câu khác nhau tình cờ chung câu dẫn (khác đáp án hoặc khác nhãn),
tức không phải bản sao. Và buộc mọi bản sao vào cùng một lát chỉ làm QWK đổi
−0,009 / −0,010, nằm trong nhiễu.

Bộ lọc `is_canonical` của môn Sử hoạt động đúng: 0 nhóm trùng còn sót.

---

## 4. Quyết định: KHÔNG đổi sang E

Lý do không phải vì +0,05 QWK không đáng, mà vì **cái giá không tương xứng với
vai trò của con số đó**:

- Đổi mô hình thì **toàn bộ lớp giải thích phải chạy lại** — chứng chỉ trục,
  kiểm tra chéo, độ phủ, từ chối có chọn lọc, lời khuyên sửa đề — vì tất cả đo
  phản ứng của *mô hình cụ thể đó*. Và toàn bộ bảng số đóng băng phải đóng băng lại.
- Dưới khung XAI đã chốt, chỉ số dự báo là **phụ lục** (bảng B6 trong
  `PAPER_SKELETON.md`), dùng để chứng minh mô hình *có học được gì đó*, không
  phải để cạnh tranh với văn liệu.
- Và E đánh đổi mất AUC tầng cao, thứ đề tài đang cân nhắc lấy làm chỉ số dẫn.

**Chỗ đáng cân nhắc là B (cân trọng số lớp), riêng cho môn Lý.** Nó giữ nguyên
kiến trúc multiclass — `predict_proba`, entropy, SHAP và pipeline can thiệp
không đổi bản chất — giữ AUC gần như nguyên (0,765 → 0,767), mà recall VDC
**tăng gần gấp ba** (0,187 → 0,534). Đây là điểm yếu dễ bị chất vấn nhất, vì VDC
là mức ít câu nhất và cũng là mức đáng quan tâm nhất.

Ở môn Sử thì B không rõ ràng: QWK +0,006 nhưng AUC −0,017. Không đủ để đổi.

**Trạng thái:** chưa áp dụng gì. Đây là hồ sơ đo đạc để quyết định, không phải
thay đổi đã thực hiện. Bảng số đóng băng vẫn ứng với cấu hình A.
