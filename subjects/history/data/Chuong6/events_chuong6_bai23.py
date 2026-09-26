# data/Chuong6/events_chuong6_bai23.py
# Bài 23: Công cuộc Đổi mới ở Việt Nam từ năm 1991 đến nay

DOCUMENTS = [
    {
        "id": "D_CH6_HiepDinhThuongMaiVietMy",
        "label": "Hiệp định Thương mại song phương Việt Nam - Hoa Kỳ (BTA, 2000)",
        "aliases": "Hiệp định BTA",
        "where": "L_VietNam", "when": "P_1991_2000",
        "cause_direct": "Nhu cầu mở rộng quan hệ kinh tế - thương mại với Mỹ sau khi hai nước bình thường hóa quan hệ ngoại giao (1995).",
        "content": "Ký kết năm 2000, có hiệu lực năm 2001, mở đường cho hàng hóa Việt Nam tiếp cận thị trường Mỹ theo quy chế quan hệ thương mại bình thường.",
        "result": "Kim ngạch xuất khẩu của Việt Nam sang Mỹ tăng vọt, đặt nền tảng quan trọng trước khi Việt Nam gia nhập WTO.",
        "involvedConcept": "C_HoiNhapQuocTe"
    },
]

EVENTS = [
    # Tuyến 1: Hội nhập đối ngoại
    {
        "id": "E_CH6_BinhThuongHoaVietMy",
        "label": "Bình thường hóa quan hệ Việt Nam - Hoa Kỳ (1995)",
        "where": "L_VietNam", "when": "P_1991_2000",
        "cause_direct": "Kết quả của quá trình đấu tranh ngoại giao kiên trì cùng với đường lối đối ngoại đổi mới, đa phương hóa, đa dạng hóa của Việt Nam sau Đại hội VI, VII.",
        "content": "Tháng 7/1995, Việt Nam và Hoa Kỳ chính thức thiết lập quan hệ ngoại giao, mở ra giai đoạn hợp tác kinh tế - thương mại giữa hai nước.",
        "achievements": "Phá thế bao vây, cấm vận, mở rộng không gian đối ngoại cho công cuộc Đổi mới.",
        "concepts_weighted": [("C_HoiNhapQuocTe", 10)]
    },
    {
        "id": "E_CH6_VietNam_GiaNhapASEAN",
        "label": "Việt Nam gia nhập ASEAN (7/1995)",
        "where": "L_VietNam", "when": "P_1991_2000",
        "org_weighted": [("O_ASEAN", 10)],
        "content": "Việt Nam chính thức trở thành thành viên thứ 7 của ASEAN, đánh dấu bước hội nhập khu vực quan trọng đầu tiên sau thời kỳ đổi mới.",
        "result": "Tạo tiền đề để Việt Nam tiếp tục hội nhập sâu rộng vào các tổ chức khu vực và quốc tế khác.",
        "concepts_weighted": [("C_HoiNhapQuocTe", 10)]
    },
    {
        "id": "E_CH6_VietNam_ThamGiaAPEC",
        "label": "Việt Nam gia nhập APEC (11/1998)",
        "where": "L_VietNam", "when": "P_1991_2000",
        "org_weighted": [("O_APEC", 10)],
        "content": "Việt Nam trở thành thành viên chính thức của Diễn đàn Hợp tác Kinh tế châu Á - Thái Bình Dương, mở rộng quan hệ hợp tác kinh tế với các nền kinh tế lớn trong khu vực.",
        "concepts_weighted": [("C_HoiNhapQuocTe", 8)]
    },
    {
        "id": "E_CH6_VietNam_GiaNhapWTO",
        "label": "Việt Nam gia nhập Tổ chức Thương mại Thế giới - WTO (1/2007)",
        "where": "L_VietNam", "when": "P_Tu2001",
        "org_weighted": [("O_WTO", 10)],
        "cause_deep": "Yêu cầu hội nhập sâu vào nền kinh tế toàn cầu để thu hút đầu tư, mở rộng thị trường xuất khẩu, đẩy mạnh công nghiệp hóa - hiện đại hóa đất nước.",
        "content": "Sau 11 năm đàm phán, tháng 1/2007 Việt Nam chính thức trở thành thành viên thứ 150 của WTO.",
        "result": "Kim ngạch xuất nhập khẩu và thu hút đầu tư nước ngoài tăng mạnh, kinh tế Việt Nam hội nhập toàn diện vào chuỗi giá trị toàn cầu.",
        "concepts_weighted": [("C_HoiNhapQuocTe", 10), ("C_ToanCauHoa", 6)]
    },
    # Tuyến 2: Đường lối trong nước
    {
        "id": "E_CH6_DaiHoiDang_KienDinhDoiMoi",
        "label": "Các kỳ Đại hội Đảng kiên định và bổ sung đường lối Đổi mới (Đại hội VII đến XIII)",
        "aliases": "Đại hội VII|Đại hội VIII|Đại hội IX|Đại hội X|Đẩy mạnh công nghiệp hóa hiện đại hóa",
        "where": "L_VietNam", "when": "P_Tu2001",
        "org_weighted": [("O_DangCS_VN", 10)],
        "who_weighted": [("Pe_NguyenVanLinh", 4), ("Pe_VoVanKiet", 4)],
        "content": "Từ Đại hội VII (1991) trở đi, Đảng Cộng sản Việt Nam liên tục bổ sung, hoàn thiện đường lối Đổi mới: xác định mục tiêu 'dân giàu, nước mạnh, xã hội công bằng, dân chủ, văn minh', đẩy mạnh công nghiệp hóa - hiện đại hóa, chủ động hội nhập kinh tế quốc tế, xây dựng nền kinh tế thị trường định hướng xã hội chủ nghĩa.",
        "concepts_weighted": [("C_KinhTeThiTruong_XHCN", 8)]
    },
    {
        "id": "E_CH6_DoiMoi_ThanhTuu",
        "label": "Thành tựu và hạn chế của công cuộc Đổi mới (từ 1991 đến nay)",
        "where": "L_VietNam", "when": "P_Tu2001",
        "org_weighted": [("O_DangCS_VN", 10)],
        "content": "Kinh tế tăng trưởng liên tục, chuyển từ nền kinh tế kế hoạch hóa tập trung sang kinh tế thị trường định hướng xã hội chủ nghĩa; năm 2008 Việt Nam chính thức thoát khỏi nhóm nước thu nhập thấp, gia nhập nhóm nước có thu nhập trung bình. GDP năm 2019 gấp khoảng 12,5 lần so với năm 2001; công nghiệp và dịch vụ chiếm khoảng 70% GDP (2020). Đời sống nhân dân được cải thiện rõ rệt, tỉ lệ hộ nghèo giảm mạnh; đến năm 2020, Việt Nam thiết lập quan hệ ngoại giao với 189/193 quốc gia thành viên Liên hợp quốc.",
        "achievements": "Từ một nước nghèo, thiếu lương thực, Việt Nam trở thành nước có thu nhập trung bình, là một trong những nước xuất khẩu gạo, nông sản hàng đầu thế giới; nằm trong nhóm quốc gia có chỉ số phát triển con người (HDI) cao.",
        "limitations": "Chất lượng tăng trưởng, năng suất lao động, năng lực cạnh tranh của nền kinh tế còn nhiều hạn chế; nguy cơ tụt hậu và các thách thức về môi trường, phân hóa giàu nghèo vẫn hiện hữu.",
        "concepts_weighted": [("C_KinhTeThiTruong_XHCN", 10), ("C_DoiMoiKinhTe", 8)]
    },
]

PREREQUISITES = [
    ("E_CH6_BinhThuongHoaVietMy", "D_CH6_HiepDinhThuongMaiVietMy"),
    ("D_CH6_HiepDinhThuongMaiVietMy", "E_CH6_VietNam_GiaNhapWTO"),
    ("E_CH6_VietNam_GiaNhapASEAN", "E_CH6_VietNam_ThamGiaAPEC"),
    ("E_CH6_VietNam_ThamGiaAPEC", "E_CH6_VietNam_GiaNhapWTO"),
    ("E_CH6_DaiHoiDang_KienDinhDoiMoi", "E_CH6_VietNam_GiaNhapWTO"),
    ("E_CH6_VietNam_GiaNhapWTO", "E_CH6_DoiMoi_ThanhTuu"),
]

SIMILARITIES = [
    ("E_CH6_VietNam_GiaNhapASEAN", "E_CH5_DongNamA_ASEAN_MoRong"),
]

CAUSES_DEEP = [
    ("D_CH6_DaiHoiDang6", "E_CH6_DaiHoiDang_KienDinhDoiMoi"),
    ("E_CH6_DaiHoiDang_KienDinhDoiMoi", "E_CH6_DoiMoi_ThanhTuu"),
]
