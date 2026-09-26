# data/Chuong7/events_chuong7_bai24.py
# Bài 24: Cách mạng khoa học - kĩ thuật và xu thế toàn cầu hoá

EVENTS = [
    # Tuyến 1: Cách mạng khoa học - kĩ thuật
    {
        "id": "E_CH7_CMKHKT_DacDiem",
        "label": "Đặc điểm cuộc cách mạng khoa học - kĩ thuật hiện đại",
        "where": "L_Global", "when": "P_1945_1991",
        "content": "Khoa học trở thành lực lượng sản xuất trực tiếp: mọi phát minh kĩ thuật đều bắt nguồn từ nghiên cứu khoa học, chứ không phải ngược lại như các cuộc cách mạng công nghiệp trước đây. Diễn ra trên nhiều lĩnh vực với tốc độ và quy mô chưa từng có.",
        "achievements": "Thời gian từ phát minh khoa học đến ứng dụng vào sản xuất được rút ngắn liên tục.",
        "concepts_weighted": [("C_CachMangKHKT_HienDai", 10)]
    },
    {
        "id": "E_CH7_CMKHKT_ThanhTuu",
        "label": "Các thành tựu chủ yếu của cách mạng khoa học - kĩ thuật hiện đại",
        "aliases": "Công nghệ thông tin|Internet|Công nghệ sinh học|Bản đồ gen người|Con người lên Mặt Trăng",
        "where": "L_Global", "when": "P_Tu2001",
        "content": "Công nghệ thông tin: máy tính, Internet, điện thoại di động phát triển bùng nổ, kết nối toàn cầu; công nghệ sinh học đạt bước tiến vượt bậc (kĩ thuật di truyền, nghiên cứu giải mã gen); chinh phục vũ trụ (con người lần đầu đặt chân lên Mặt Trăng, năm 1969); năng lượng mới (năng lượng hạt nhân, năng lượng tái tạo); vật liệu mới, tự động hóa và robot.",
        "achievements": "Tạo ra bước ngoặt trong lịch sử văn minh nhân loại, đưa loài người bước sang nền văn minh trí tuệ.",
        "concepts_weighted": [("C_CachMangKHKT_HienDai", 10), ("C_KinhTeTriThuc", 8)]
    },
    {
        "id": "E_CH7_CMKHKT_TacDong",
        "label": "Tác động của cách mạng khoa học - kĩ thuật hiện đại",
        "where": "L_Global", "when": "P_Tu2001",
        "cause_direct": "Sự bùng nổ và lan tỏa nhanh chóng của các thành tựu khoa học - kĩ thuật hiện đại vào mọi lĩnh vực đời sống.",
        "content": "Tăng năng suất lao động, nâng cao mức sống và chất lượng cuộc sống con người, làm thay đổi cơ cấu dân cư, chuyển dịch cơ cấu kinh tế theo hướng dịch vụ - công nghệ cao.",
        "result": "Đồng thời gây ra hệ quả tiêu cực: ô nhiễm môi trường, biến đổi khí hậu, chế tạo vũ khí hủy diệt hàng loạt, các tai nạn lao động và dịch bệnh mới, gia tăng khoảng cách giàu - nghèo giữa các nhóm nước.",
        "limitations": "Các nước đang phát triển đối mặt nguy cơ tụt hậu về công nghệ nếu không kịp thích ứng.",
        "concepts_weighted": [("C_CachMangKHKT_HienDai", 8)]
    },
    # Tuyến 2: Toàn cầu hoá
    {
        "id": "E_CH7_ToanCauHoa_BieuHien",
        "label": "Biểu hiện của xu thế toàn cầu hóa",
        "where": "L_Global", "when": "P_Tu2001",
        "org_weighted": [("O_WTO", 8), ("O_EU", 6), ("O_ASEAN", 6), ("O_APEC", 6)],
        "cause_deep": "Cách mạng khoa học - kĩ thuật hiện đại, nhất là công nghệ thông tin, tạo điều kiện kết nối và lưu chuyển vốn, hàng hóa, lao động, tri thức trên phạm vi toàn cầu.",
        "content": "Biểu hiện trên 4 lĩnh vực chính: (1) Thương mại - kim ngạch xuất nhập khẩu hàng hóa, dịch vụ tăng nhanh, mạng lưới thương mại mở rộng; (2) Tài chính - thị trường tài chính quốc tế liên kết chặt chẽ, dòng vốn đầu tư trực tiếp nước ngoài tăng mạnh qua các công ty đa quốc gia; (3) Văn hóa - giao lưu, tiếp biến văn hóa giữa các quốc gia diễn ra sâu rộng; (4) Lao động - di cư lao động xuyên quốc gia gia tăng. Đồng thời là sự ra đời và mở rộng của các tổ chức liên kết kinh tế khu vực và toàn cầu (WTO, EU, ASEAN, APEC).",
        "concepts_weighted": [("C_ToanCauHoa", 10)]
    },
    {
        "id": "E_CH7_ToanCauHoa_TapDoanXuyenQuocGia",
        "label": "Vai trò ngày càng lớn của các công ty xuyên quốc gia",
        "aliases": "Công ty đa quốc gia|TNCs",
        "where": "L_Global", "when": "P_Tu2001",
        "content": "Các công ty xuyên quốc gia (TNCs) mở rộng mạng lưới sản xuất - kinh doanh ra nhiều quốc gia, chi phối phần lớn thương mại, đầu tư và chuyển giao công nghệ quốc tế, hình thành các chuỗi giá trị và chuỗi cung ứng toàn cầu.",
        "result": "Thúc đẩy phân công lao động quốc tế sâu rộng nhưng cũng làm gia tăng sự phụ thuộc lẫn nhau và rủi ro lan truyền khủng hoảng giữa các nền kinh tế.",
        "concepts_weighted": [("C_CongTyXuyenQuocGia", 10), ("C_ToanCauHoa", 6)]
    },
    {
        "id": "E_CH7_ToanCauHoa_ThoiCoThachThuc",
        "label": "Thời cơ và thách thức của toàn cầu hóa với các nước đang phát triển",
        "aliases": "Toàn cầu hóa và Việt Nam",
        "where": "L_VietNam", "when": "P_Tu2001",
        "content": "Thời cơ: mở rộng thị trường, thu hút vốn đầu tư và công nghệ, rút ngắn khoảng cách phát triển nếu tận dụng tốt cơ hội hội nhập. Thách thức: nguy cơ tụt hậu, cạnh tranh gay gắt, phụ thuộc kinh tế, nguy cơ đánh mất bản sắc văn hóa dân tộc nếu không có chiến lược hội nhập phù hợp.",
        "result": "Đặt ra yêu cầu các nước đang phát triển, trong đó có Việt Nam, phải vừa chủ động hội nhập vừa giữ vững độc lập, tự chủ.",
        "concepts_weighted": [("C_ToanCauHoa", 10), ("C_HoiNhapQuocTe", 8)]
    },
]

PREREQUISITES = [
    ("E_CH7_CMKHKT_DacDiem", "E_CH7_CMKHKT_ThanhTuu"),
    ("E_CH7_CMKHKT_ThanhTuu", "E_CH7_CMKHKT_TacDong"),
    ("E_CH7_ToanCauHoa_BieuHien", "E_CH7_ToanCauHoa_TapDoanXuyenQuocGia"),
    ("E_CH7_ToanCauHoa_TapDoanXuyenQuocGia", "E_CH7_ToanCauHoa_ThoiCoThachThuc"),
]

CAUSES_DEEP = [
    ("E_CH7_CMKHKT_TacDong", "E_CH7_ToanCauHoa_BieuHien"),
]

SIMILARITIES = [
    ("E_CH7_ToanCauHoa_ThoiCoThachThuc", "E_CH6_VietNam_GiaNhapWTO"),
    ("E_CH7_ToanCauHoa_BieuHien", "E_CH5_TrungQuoc_TroiDay"),
    ("E_CH7_ToanCauHoa_TapDoanXuyenQuocGia", "E_CH5_ChauA_KhungHoangTaiChinh1997"),
]

CONTRASTS = [
    ("E_CH7_CMKHKT_DacDiem", "E_CH7_ToanCauHoa_ThoiCoThachThuc"),
]
