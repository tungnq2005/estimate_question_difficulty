# data/ch4/events_ch4_bai16.py

DOCUMENTS = [
    {
        "id": "D_CH4_KeHoachNavarre",
        "label": "Kế hoạch Na-va (1953)",
        "aliases": "Kế hoạch Navarre",
        "where": "L_VietNam", "when": "P_1951_1954",
        "org_weighted": [("O_ThucDanPhap", 10), ("L_My", 9)],
        "content": "Pháp và Mỹ hi vọng giành thắng lợi quyết định trong 18 tháng. Điểm mấu chốt là tập trung quân cơ động chiến lược ở đồng bằng Bắc Bộ (44 tiểu đoàn).",
        "result": "Bị phân tán bởi Tiến công Đông - Xuân và bị đập tan hoàn toàn tại Điện Biên Phủ."
    },
    {
        "id": "D_CH4_HiepDinhGeneva",
        "label": "Hiệp định Giơ-ne-vơ (21/7/1954)",
        "aliases": "Hiệp định Geneva",
        "where": "L_Geneva", "when": "P_1951_1954",
        "org_weighted": [("O_VNDCCH", 10), ("O_ThucDanPhap", 10)],
        "cause_direct": "Thắng lợi quyết định tại Điện Biên Phủ tạo thế mạnh trên bàn đàm phán.",
        "content": "Pháp công nhận độc lập, chủ quyền, toàn vẹn lãnh thổ VN. Vĩ tuyến 17 là giới tuyến quân sự tạm thời. Tổng tuyển cử vào tháng 7/1956.",
        "achievements": "Chấm dứt chiến tranh xâm lược của Pháp, Mỹ thất bại trong âm mưu quốc tế hóa chiến tranh Đông Dương."
    }
]

EVENTS = [
    # Tuyến 1: Chính trị - Hậu phương
    {
        "id": "E_CH4_DaiHoiDang2",
        "label": "Đại hội đại biểu lần thứ II của Đảng (2/1951)",
        "aliases": "Đại hội II|Đại hội kháng chiến thắng lợi",
        "where": "L_VietNam", "when": "P_1951_1954",
        "org_weighted": [("O_DangLaoDongVN", 10)],
        "content": "Khẳng định đường lối kháng chiến, đổi tên thành Đảng Lao động Việt Nam. Đánh dấu bước trưởng thành của Đảng.",
        "concepts_weighted": [("C_KhangChienToanDien", 10)]
    },
    
    # Tuyến 2: Quân sự (Nút thắt của bài toán MCQ)
    {
        "id": "E_CH4_DongXuan_53_54",
        "label": "Cuộc Tiến công chiến lược Đông - Xuân 1953-1954",
        "aliases": "Đông Xuân 1953-1954",
        "where": "L_VietNam", "when": "P_DongXuan_53_54",
        "cause_direct": "Bộ Chính trị chủ trương tiến công những hướng địch tương đối yếu để buộc chúng phải phân tán lực lượng.",
        "content": "Tấn công Lai Châu, Trung Lào, Thượng Lào, Tây Nguyên. Buộc Pháp chia thành 5 nơi tập trung quân (ĐB Bắc Bộ, ĐBP, Xê-nô, Luông Pha-bang, Plây-ku).",
        "result": "Bước đầu làm phá sản kế hoạch Na-va.",
        "concepts_weighted": [("C_PhanTanLucLuong", 10)]
    },
    {
        "id": "E_CH4_DienBienPhu",
        "label": "Chiến dịch lịch sử Điện Biên Phủ (1954)",
        "aliases": "Chiến dịch Điện Biên Phủ|56 ngày đêm",
        "where": "L_DienBienPhu", "when": "P_DienBienPhu",
        "org_weighted": [("O_VNDCCH", 10), ("O_ThucDanPhap", 10)],
        "content": """+ Phương châm: Chuyển từ 'đánh nhanh thắng nhanh' sang 'đánh chắc, tiến chắc'.
        + Đợt 1: Tiêu diệt Him Lam và phân khu Bắc.
        + Đợt 2: Tấn công cứ điểm phía đông phân khu Trung tâm.
        + Đợt 3: Tiêu diệt khu Trung tâm và phân khu Nam. Ngày 7/5/1954 địch đầu hàng.""",
                "achievements": "Đập tan hoàn toàn Kế hoạch Na-va, xoay chuyển cục diện chiến tranh, tạo điều kiện thuận lợi cho ngoại giao.",
        "concepts_weighted": [("C_DanhChacTienChac", 10)]
    }
]