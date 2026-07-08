DOCUMENTS = [
    {
        "id": "D_CH6_KyHopThuNhat_QH6",
        "label": "Kỳ họp thứ nhất Quốc hội khóa VI (6-7/1976)",
        "where": "L_VietNam", "when": "P_1976_1985",
        "org_weighted": [("O_QuocHoiKhoa6", 10)],
        "content": "Quyết định tên nước là CHXHCN Việt Nam, Quốc kì, Quốc ca, đổi tên Sài Gòn thành TP. Hồ Chí Minh.",
        "achievements": "Hoàn thành quá trình thống nhất đất nước về mặt nhà nước.",
        "involvedConcept": "C_ThongNhatNhaNuoc"
    },
    {
        "id": "D_CH6_DaiHoiDang6",
        "label": "Đại hội đại biểu toàn quốc lần thứ VI (12/1986)",
        "aliases": "Đại hội VI|Đại hội Đổi mới",
        "where": "L_VietNam", "when": "P_1986_1991",
        "cause_deep": "Đất nước khủng hoảng kinh tế xã hội trầm trọng. Thế giới có nhiều thay đổi lớn.",
        "content": "Đề ra đường lối Đổi mới toàn diện, trọng tâm là đổi mới kinh tế (xóa bao cấp, phát triển kinh tế hàng hóa nhiều thành phần).",
        "involvedConcept": "C_DoiMoiKinhTe"
    },
    {
        "id": "D_CH6_HienPhap1980",
        "label": "Hiến pháp năm 1980",
        "where": "L_VietNam", "when": "P_1976_1985",
        "org_weighted": [("O_DangCS_VN", 10)],
        "content": "Hiến pháp mới của nước CHXHCN Việt Nam được thông qua (tháng 12/1980), thể chế hóa đường lối xây dựng CNXH trong cả nước.",
    },
    {
        "id": "D_CH6_DaiHoiDang6_ChiTiet", # Bản nâng cấp chi tiết của ĐH 6
        "label": "Đường lối Đổi mới tại Đại hội VI (12/1986)",
        "aliases": "Nội dung đường lối Đổi mới",
        "where": "L_VietNam", "when": "P_1986_1991",
        "cause_deep": "Nguyên nhân khách quan: Khủng hoảng ở Liên Xô/Đông Âu, CM KH-KT, xu thế toàn cầu hóa. Nguyên nhân chủ quan: Sai lầm trong kế hoạch 5 năm (1976-1985) gây khủng hoảng trầm trọng.",
        "content": """+ Quan điểm: Đổi mới toàn diện, đồng bộ, TRỌNG TÂM LÀ KINH TẾ. Đổi mới không phải là thay đổi mục tiêu CNXH mà là đổi mới hình thức, biện pháp.
        + Kinh tế: Xóa bỏ bao cấp; Xây dựng kinh tế hàng hóa nhiều thành phần (cơ chế thị trường); Kêu gọi đầu tư nước ngoài.
        + Chính trị: Xây dựng Nhà nước pháp quyền XHCN.""",
        "concepts_weighted": [("C_KinhTeThiTruong_XHCN", 10)]
    },
]

EVENTS = [
    # Tuyến bảo vệ Tổ quốc
    {
        "id": "E_CH6_BaoVeTayNam",
        "label": "Bảo vệ biên giới Tây Nam (1978-1979)",
        "where": "L_BienGioiTayNam", "when": "P_1976_1985",
        "org_weighted": [("O_KhmerDo", 10)],
        "content": "Quân đội VN tổng phản công đánh bại quân Pôn Pốt xâm lược.",
        "achievements": "Giữ vững chủ quyền, tạo thời cơ cho cách mạng Campuchia."
    },
    {
        "id": "E_CH6_BaoVePhiaBac",
        "label": "Bảo vệ biên giới phía Bắc (1979)",
        "where": "L_BienGioiPhiaBac", "when": "P_1976_1985",
        "content": "Quân dân các tỉnh biên giới phía Bắc kiên cường chiến đấu chống 60 vạn quân Trung Quốc tấn công.",
    },
    {
        "id": "E_CH6_HaiChienGacMa",
        "label": "Bảo vệ chủ quyền tại đảo Gạc Ma (3/1988)",
        "where": "L_TruongSa", "when": "P_1986_1991",
        "content": "Chiến sĩ Hải quân Việt Nam anh dũng hi sinh chiến đấu chống quân đội Trung Quốc tấn công bãi ngầm Gạc Ma.",
    },
    
    # Tuyến Kinh tế xã hội
    {
        "id": "E_CH6_KhungHoangKinhTe",
        "label": "Khủng hoảng kinh tế - xã hội (Trước 1986)",
        "where": "L_VietNam", "when": "P_1976_1985",
        "cause_direct": "Duy trì quá lâu cơ chế tập trung quan liêu, bao cấp.",
        "content": "Lạm phát tăng phi mã (774%), thiếu thốn lương thực, thực phẩm trầm trọng.",
        "involvedConcept": "C_BaoCap"
    },
    {
        "id": "E_CH6_GiaNhapLHQ",
        "label": "Việt Nam gia nhập Liên hợp quốc (1977)",
        "where": "L_Global", "when": "P_1976_1985",
        "org_weighted": [("O_LienHopQuoc", 10)],
        "achievements": "Phát triển quan hệ ngoại giao, nâng cao vị thế của Việt Nam trên trường quốc tế sau ngày thống nhất.",
    },
    {
        "id": "E_CH6_ThucHienDoiMoi_86_91",
        "label": "Kết quả bước đầu công cuộc Đổi mới (1986-1991)",
        "where": "L_VietNam", "when": "P_1986_1991",
        "content": "Thực hiện tốt 'Ba chương trình kinh tế' (Lương thực, Hàng tiêu dùng, Hàng xuất khẩu). Tăng cường quyền làm chủ của nhân dân, mở rộng đối ngoại.",
        "limitations": "Đất nước chưa ra khỏi khủng hoảng, lạm phát còn cao, phân hóa giàu nghèo gia tăng.",
        "achievements": "Khẳng định sự lãnh đạo đúng đắn của Đảng, phục hồi sản xuất, kiềm chế lạm phát.",
        "concepts_weighted": [("C_BaChuongTrinhKinhTe", 10)]
    }
]