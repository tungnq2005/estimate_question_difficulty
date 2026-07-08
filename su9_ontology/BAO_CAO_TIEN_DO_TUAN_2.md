# BÁO CÁO TIẾN ĐỘ NGHIÊN CỨU (Tuần 1-2)

## Xây dựng Đồ thị Tri thức (Ontology) Lịch sử 9
## phục vụ ước lượng độ khó câu hỏi trắc nghiệm

---

## 1. Tổng quan

Mục tiêu 2 tuần qua: **Xây dựng Ontology (Đồ thị Tri thức) môn Lịch sử lớp 9** — một cơ sở tri thức có cấu trúc, mã hóa các sự kiện, nhân vật, địa danh, khái niệm và mối quan hệ giữa chúng thành dạng đồ thị (graph) có thể truy vấn và tính toán bằng máy tính.

Ontology được xây dựng theo chuẩn W3C (RDF/OWL - Turtle format), sử dụng chương trình GDPT 2018 môn Lịch sử 9 (Sách Chân trời sáng tạo).

---

## 2. Kết quả xây dựng Ontology

### 2.1 Con số tổng quan

| Chỉ số | Giá trị |
|--------|---------|
| **Tổng số thực thể (entities)** | **434** |
| **Tổng số quan hệ (edges)** | **761** |
| **Đường kính đồ thị (graph diameter)** | 12 |
| **Số lượng label/alias cho entity matching** | 434 labels + 623 aliases |
| **Số file dữ liệu Python** | 6 files |
| **Số chương đã mã hóa** | **2 chương** |

### 2.2 Phân bố các lớp thực thể

Ontology sử dụng **8 lớp (classes)** chính:

| Lớp | Số lượng | Ý nghĩa | Ví dụ |
|:---|:--------:|---------|-------|
| **Event** | 84 | Sự kiện lịch sử có mốc thời gian cụ thể | Cách mạng tháng Tám (1945), Chiến dịch Điện Biên Phủ (1954) |
| **Location** | 79 | Địa danh, không gian địa lý | Điện Biên Phủ, Hà Nội, Pari, Chiến khu Tân Trào |
| **Organization** | 76 | Tổ chức, Đảng phái, Giai cấp | Đảng Cộng sản Đông Dương, Việt Minh, Mặt trận Tổ quốc |
| **Concept** | 76 | Khái niệm, tư tưởng, khuynh hướng cốt lõi | Chủ nghĩa tư bản, Cách mạng dân tộc dân chủ, Thực dân |
| **Period** | 45 | Giai đoạn lịch sử | 1930-1931, 1945-1954, Chiến tranh lạnh |
| **Document** | 35 | Tài liệu, sách báo, hiệp ước lịch sử | Bản án chế độ thực dân Pháp, Tuyên ngôn Độc lập |
| **Person** | 24 | Nhân vật lịch sử | Hồ Chí Minh, Võ Nguyên Giáp, Phan Bội Châu |
| **Movement** | 15 | Phong trào (kéo dài qua nhiều năm) | Cần Vương, Đồng Khởi, Xô viết Nghệ Tĩnh |

### 2.3 Các loại quan hệ (Object Properties)

Ontology định nghĩa **12 loại quan hệ** kết nối các thực thể:

| Quan hệ | Số lượng | Ý nghĩa |
|:--------|:--------:|---------|
| **hasOrganization** | 136 | Sự kiện/phong trào liên quan đến tổ chức nào |
| **occursAt** | 134 | Sự kiện xảy ra tại địa danh nào |
| **occursDuring** | 127 | Sự kiện diễn ra trong giai đoạn nào |
| **involvedConcept** | 91 | Liên quan đến khái niệm/khuynh hướng nào |
| **locatedIn** | 76 | Địa danh nằm ở đâu |
| **prerequisiteOf** | 66 | Quan hệ tiền đề — sự kiện A là điều kiện cho B |
| **contrastsWith** | 62 | Tương phản/đối lập (VD: Cần Vương × Đồng Khởi về bản chất) |
| **hasPerson** | 45 | Có sự tham gia của nhân vật nào |
| **similarTo** | 8 | Tương tự nhau |
| **leads** | 7 | Dẫn đến kết quả gì |
| **directCause** | 5 | Nguyên nhân trực tiếp (VD: Khủng hoảng dầu mỏ → Suy thoái) |
| **deepCause** | 4 | Nguyên nhân sâu xa (VD: Mâu thuẫn dân tộc → Chiến tranh) |

### 2.4 Dữ liệu mở rộng (Data Properties)

Mỗi thực thể được gán thêm các thuộc tính định lượng:

| Annotation | Số lượng | Mô tả |
|:-----------|:--------:|-------|
| **abstractness (mức độ trừu tượng)** | 298 | Thang 1-5: 1 = sự kiện cụ thể, 5 = khái niệm trừu tượng |
| **bloomLevel (cấp độ tư duy)** | 74 | Thang 1-6 theo thang Bloom |
| **frequencyInTextbook** | 174 | Tần suất xuất hiện trong SGK (khung 1-10) |
| **aliases (bí danh)** | 623 | Các tên gọi khác (VD: Nguyễn Ái Quốc ↔ Bác Hồ ↔ Nguyễn Tất Thành) |
| **weightsJson (trọng số)** | 113 | Ma trận trọng số liên kết giữa các cặp entity |
| **startYear / endYear** | 45 | Mốc thời gian (Period + Event) |

### 2.5 Cấu trúc thư mục dữ liệu

```
su9_ontology/
├── build_main.py                # Script build: đọc data/ → xuất su9.ttl + su9.owl
├── view.py                      # CLI tra cứu tương tác (timeline, reverse lookup)
├── output/
│   ├── su9.ttl                  # Ontology chuẩn Turtle (~1.5MB)
│   └── su9.owl                  # Ontology chuẩn OWL (mở bằng Protégé)
└── data/
    ├── global_entities/         # Thực thể dùng chung (không phụ thuộc chương)
    │   ├── periods_locations.py   # 45 giai đoạn + 79 địa danh
    │   ├── persons_orgs.py        # 24 nhân vật + 76 tổ chức
    │   ├── concepts.py            # 76 khái niệm cốt lõi
    │   └── relationships_global.py # Quan hệ xuyên suốt
    ├── ch1/
    │   └── events_ch1.py        # Chương 1: Thế giới 1918-1945 (sự kiện + quan hệ)
    └── ch2/
        └── events_ch2.py        # Chương 2: Việt Nam 1918-1945 (sự kiện + quan hệ)
```

### 2.6 Tiện ích tra cứu

Đi kèm ontology là công cụ CLI **view.py** hỗ trợ:
- **Truy vấn trực tiếp**: Gõ tên sự kiện → hiển thị bối cảnh, diễn biến, nhân vật liên quan
- **Reverse Lookup**: Gõ tên nhân vật → liệt kê tất cả sự kiện có sự tham gia
- **Timeline Scanner**: Lệnh `time 1930 1945` → quét toàn bộ sự kiện trong khoảng thời gian

---

## 3. Đóng góp khoa học

1. **Ontology Lịch sử 9 đầu tiên** cho giáo dục phổ thông Việt Nam:
   - Mã hóa theo chuẩn W3C (Turtle/OWL), có thể tái sử dụng, mở rộng
   - Truy vấn được bằng SPARQL hoặc thư viện RDF
   
2. **Thiết kế dữ liệu phân tách Global & Local:**
   - Global: thực thể dùng chung (Bác Hồ, Pháp, Khái niệm...) — không trùng lặp
   - Local: sự kiện theo từng bài học — dễ dàng mở rộng lên 100+ chương

3. **Tích hợp annotation giáo dục:**
   - abstractness (mức trừu tượng) — phục vụ đo độ khó nhận thức
   - bloomLevel (thang Bloom) — phục vụ phân loại câu hỏi theo tư duy
   - weightsJson — phục vụ tính toán mức độ liên quan giữa các thực thể

---

## 4. Dự kiến 2 tuần tới

| Hạng mục | Chi tiết |
|----------|---------|
| **Mở rộng ontology** | Thêm Chương 3: Việt Nam 1945-1975 (kháng chiến chống Mỹ) |
| **Xây dựng pipeline đo độ khó** | Phát triển mô-đun tính 33 features từ KG (Jaccard + RSI + KG Structure) |
| **Tích hợp Embedding** | Cài PyTorch, tính Knowledge Entropy + PhoBERT cosine similarity |
| **Huấn luyện mô hình** | Thu thập MCQ samples → huấn luyện XGBoost phân loại Easy/Medium/Hard |

---

*Báo cáo được tạo ngày 03/05/2026*
