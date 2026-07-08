# 🇻🇳 Đồ thị Tri thức Lịch sử 9 (History 9 Knowledge Graph)

Dự án xây dựng **Hệ thống Đồ thị tri thức (Ontology)** tự động hoá dành cho môn Lịch sử lớp 9 (Sách Chân trời sáng tạo). Hệ thống mã hóa các sự kiện, nhân vật, giai đoạn và tài liệu lịch sử thành mạng lưới dữ liệu ngữ nghĩa (Semantic Web) có thể truy vấn thông minh.

Dự án hiện tại đã hoàn thiện mô hình hóa **Chương 1 (Thế giới 1918-1945)** và **Chương 2 (Việt Nam 1918-1945)**.

---

## 🌟 Tính năng nổi bật

* **Kiến trúc Dữ liệu V4 (Global & Local):** Phân tách thông minh giữa thực thể dùng chung (Bác Hồ, Pháp, Mỹ, Khái niệm...) và sự kiện cục bộ theo từng bài học. Tránh trùng lặp ID và dễ dàng mở rộng lên 100+ chương.
* **Đúc Ontology Tự động:** Tự động quét (`glob`), cộng dồn (`extend`) và biên dịch dữ liệu Python thành chuẩn **Turtle (.ttl)** và **OWL (.owl)** của W3C.
* **Deep Inspector (Soi chi tiết):** Hiển thị các sự kiện theo đúng trật tự logic lịch sử (Bối cảnh $\rightarrow$ Nguyên nhân $\rightarrow$ Nội dung $\rightarrow$ Kết quả $\rightarrow$ Trọng số).
* **Reverse Lookup (Truy xuất ngược):** Nhập tên một nhân vật/địa danh (VD: `Bác Hồ`), máy tính sẽ tự động liệt kê TẤT CẢ các sự kiện, phong trào có sự góp mặt của nhân vật đó.
* **Timeline Scanner (Cỗ máy thời gian):** Tìm kiếm toàn bộ dữ kiện lịch sử xảy ra trong một khoảng thời gian tuỳ ý (VD: `time 1930 1945`).
* **Smart NLP:** Tự động khử nhiễu lỗi gõ dấu tiếng Việt (òa/oà) và hỗ trợ vô số bí danh (aliases) cho mỗi thực thể.

---

## 📂 Cấu trúc Thư mục

```text
su9_ontology/
├── build_main.py             # Script tự động quét data và đúc ra file .ttl / .owl
├── view.py                   # Cỗ máy truy vấn tương tác (CLI)
├── output/                   # Chứa file kết quả
│   ├── su9.ttl               # File đồ thị chuẩn Turtle
│   └── su9.owl               # File OWL (Mở bằng Protégé)
└── data/                     # Kho dữ liệu thô (Python)
    ├── global_entities/      # Thực thể tĩnh dùng chung toàn hệ thống
    │   ├── periods_locations.py
    │   ├── persons_orgs.py
    │   ├── concepts.py
    │   └── relationships_global.py
    ├── ch1/                  # Dữ liệu Chương 1 (Thế giới 1918 - 1945)
    │   └── events_ch1.py
    └── ch2/                  # Dữ liệu Chương 2 (Việt Nam 1918 - 1945)
        └── events_ch2.py


⚙️ Cài đặt & Khởi chạy
1. Cài đặt thư viện yêu cầu:
Hệ thống sử dụng rdflib để xuất file OWL và owlready2 để truy vấn Đồ thị.

Bash
pip install rdflib owlready2
2. Biên dịch Dữ liệu (Build):
Mỗi khi bạn thêm hoặc sửa dữ liệu trong thư mục data/, hãy chạy lệnh này để hệ thống nạp lại Đồ thị:

Bash
python build_main.py
(Kết quả: Hệ thống sẽ báo [OK] Đã ghi thành công file...)

3. Truy vấn Tri thức (View):
Chạy giao diện tương tác CLI:

Bash
python view.py
💡 Hướng dẫn Truy vấn (CLI)
Khi chạy view.py, bạn có thể tương tác với lịch sử qua các lệnh sau:

Trực tiếp hỏi tên Sự kiện / Khái niệm:
[Bạn] ❯ Tổng khởi nghĩa tháng Tám
Hệ thống sẽ hiển thị bối cảnh, diễn biến, ý nghĩa và liệt kê các nhân vật/tổ chức liên quan.

Sử dụng tính năng Truy xuất ngược:
[Bạn] ❯ Nguyễn Ái Quốc (hoặc Bác Hồ)
Hệ thống sẽ hiển thị thông tin của Bác và mọi sự kiện (Đại hội Tua, Hội nghị thành lập Đảng, Tuyên ngôn Độc lập...) liên quan đến Bác trong toàn bộ chương trình.

Quét dòng thời gian (Timeline):
[Bạn] ❯ time 1930 1931
Hệ thống sẽ quét sâu vào nội dung mọi văn bản và liệt kê toàn bộ sự kiện diễn ra trong mốc năm này (VD: Xô viết Nghệ-Tĩnh, Phong trào cách mạng 1930-1931...)

🛠 Lớp thực thể (Schema)
Hệ thống được thiết kế theo chuẩn hướng đối tượng với các Class chính:

Period: Giai đoạn lịch sử

Location: Địa danh, không gian

Person: Nhân vật lịch sử

Organization: Tổ chức, Đảng phái, Giai cấp

Concept: Khái niệm, khuynh hướng cốt lõi

Document: Tài liệu, sách báo, hiệp ước

Event: Sự kiện (có mốc thời gian cụ thể)

Movement: Phong trào (kéo dài qua nhiều năm)
