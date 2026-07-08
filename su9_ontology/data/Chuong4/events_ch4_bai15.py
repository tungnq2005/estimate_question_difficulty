# data/ch4/events_ch4_bai15.py

DOCUMENTS = [
    {
        "id": "D_CH4_LoiKeuGoiTQKC",
        "label": "Lời kêu gọi toàn quốc kháng chiến (19/12/1946)",
        "aliases": "Lời kêu gọi của Hồ Chủ tịch",
        "where": "L_VietNam", "when": "P_1946_1950",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "cause_direct": "Pháp gửi tối hậu thư (17/12/1946) đòi tước vũ khí tự vệ và kiểm soát Hà Nội.",
        "content": "Phát động toàn quốc kháng chiến chống thực dân Pháp xâm lược.",
        "involvedConcept": "C_DuongLoiKhangChien"
    },
    {
        "id": "D_CH4_KhangChienNhatDinhThangLoi",
        "label": "Tác phẩm Kháng chiến nhất định thắng lợi (9/1947)",
        "where": "L_VietNam", "when": "P_1946_1950",
        "who_weighted": [("Pe_TruongChinh", 10)],
        "content": "Giải thích rõ nội dung cơ bản của đường lối kháng chiến: toàn dân, toàn diện, trường kì, tự lực cánh sinh.",
        "involvedConcept": "C_DuongLoiKhangChien"
    },
    {
        "id": "D_CH4_KeHoachRevers",
        "label": "Kế hoạch Rơ-ve (1949)",
        "aliases": "Kế hoạch Revers",
        "where": "L_VietNam", "when": "P_1946_1950",
        "org_weighted": [("O_ThucDanPhap", 10), ("L_My", 8)],
        "content": "Tăng cường phòng thủ Đường số 4, lập hành lang Đông - Tây nhằm khóa chặt biên giới Việt - Trung, chuẩn bị tiến công Việt Bắc lần 2.",
        "result": "Bị phá sản hoàn toàn sau Chiến dịch Biên giới thu - đông 1950."
    }
]

EVENTS = [
    {
        "id": "E_CH4_ChienDauDoThi",
        "label": "Cuộc chiến đấu ở các đô thị phía Bắc vĩ tuyến 16 (1946-1947)",
        "aliases": "Chiến đấu ở Hà Nội|Toàn quốc kháng chiến bùng nổ",
        "where": "L_ViTuyen16_Bac", "when": "P_1946_1950",
        "org_weighted": [("O_VNDCCH", 10), ("O_ThucDanPhap", 10)],
        "content": "Quân dân ta chủ động tiến công, giam chân địch trong thành phố suốt gần 3 tháng.",
        "result": "Tiêu hao sinh lực địch, bảo vệ cơ quan đầu não và quân chủ lực rút lên Việt Bắc an toàn.",
    },
    {
        "id": "E_CH4_VietBac1947",
        "label": "Chiến dịch Việt Bắc thu - đông năm 1947",
        "aliases": "Chiến dịch Việt Bắc 1947",
        "where": "L_VietBac", "when": "P_ThuDong1947",
        "org_weighted": [("O_VNDCCH", 10), ("O_ThucDanPhap", 10)],
        "cause_direct": "Pháp huy động 12.000 quân tiến công Việt Bắc nhằm tiêu diệt đầu não kháng chiến, kết thúc nhanh chiến tranh.",
        "content": "Ta phục kích chặn đánh địch trên Đường số 4 (Bản Sao, đèo Bông Lau) và trên sông Lô (Đoan Hùng, Khe Lau).",
        "result": "Bảo vệ an toàn cơ quan đầu não. Bộ đội chủ lực ngày càng trưởng thành.",
        "achievements": "Làm thất bại hoàn toàn chiến lược 'Đánh nhanh thắng nhanh' của Pháp.",
        "concepts_weighted": [("C_DanhLauDai", 10)]
    },
    {
        "id": "E_CH4_BienGioi1950",
        "label": "Chiến dịch Biên giới thu - đông năm 1950",
        "aliases": "Chiến dịch Biên giới 1950",
        "where": "L_DuongSo4", "when": "P_ThuDong1950",
        "org_weighted": [("O_VNDCCH", 10), ("O_ThucDanPhap", 10)],
        "cause_deep": "Sự lớn mạnh của phe XHCN tạo chỗ dựa cho ta. Mỹ can thiệp sâu giúp Pháp đẻ ra Kế hoạch Rơ-ve.",
        "content": "Đảng chủ trương mở chiến dịch. Trận mở màn đánh vào Đông Khê (9/1950). Sau 1 tháng, Pháp rút khỏi toàn bộ Đường số 4 (Cao Bằng, Thất Khê...).",
        "achievements": "Giải phóng vùng biên giới rộng lớn. Chọc thủng hành lang Đông-Tây, làm phá sản Kế hoạch Rơ-ve.",
        "result": "Quân đội ta giành được thế chủ động trên chiến trường chính Bắc Bộ, mở ra bước phát triển mới của cuộc kháng chiến.",
        "concepts_weighted": [("C_TheChuDong", 10)]
    }
]