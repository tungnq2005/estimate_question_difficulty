# data/ch5/events_ch5_bai18.py

DOCUMENTS = [
    {
        "id": "D_CH5_HiepDinhParis1973",
        "label": "Hiệp định Pa-ri (1973)",
        "aliases": "Hiệp định Paris",
        "where": "L_Global", "when": "P_1969_1973",
        "cause_direct": "Mỹ thất bại nặng nề tại trận Điện Biên Phủ trên không (12/1972).",
        "content": "Mỹ buộc phải chấm dứt chiến tranh, rút hết quân viễn chinh và quân chư hầu về nước.",
        "achievements": "Làm thay đổi căn bản so sánh lực lượng ở miền Nam có lợi cho cách mạng (Mỹ cút, mở đường cho ngụy nhào).",
    }
]

EVENTS = [
    # ================= TUYẾN 1: ĐÁNH BẠI CHIẾN TRANH CỤC BỘ =================
    {
        "id": "E_CH5_VanTuong1965",
        "label": "Trận Vạn Tường (8/1965)",
        "where": "L_VanTuong", "when": "P_1965_1968",
        "org_weighted": [("O_MTDTGPMNVN", 10), ("O_QuanMy", 10)],
        "achievements": "Mở đầu cao trào 'Tìm Mỹ mà đánh, lùng ngụy mà diệt', chứng tỏ ta có thể đánh thắng quân viễn chinh Mỹ.",
        "involvedConcept": "C_ChienTranhCucBo"
    },
    {
        "id": "E_CH5_MauThan1968",
        "label": "Tổng tiến công và nổi dậy Xuân Mậu Thân (1968)",
        "aliases": "Mậu Thân 1968",
        "where": "L_MienNam", "when": "P_1965_1968",
        "content": "Đánh bất ngờ vào đêm giao thừa, nhằm vào các cơ quan đầu não của địch ở các đô thị.",
        "result": "Buộc Mỹ phải tuyên bố 'phi Mỹ hóa' chiến tranh, ngừng ném bom miền Bắc và ngồi vào bàn đàm phán Paris.",
        "involvedConcept": "C_ChienTranhCucBo"
    },

    # ================= TUYẾN 2: ĐÁNH BẠI VIỆT NAM HÓA & CHIẾN TRANH PHÁ HOẠI =================
    {
        "id": "E_CH5_TienCong1972",
        "label": "Tiến công chiến lược năm 1972",
        "aliases": "Mùa hè đỏ lửa 1972",
        "where": "L_MienNam", "when": "P_1969_1973",
        "achievements": "Giáng đòn nặng nề vào chiến lược VN hóa chiến tranh, buộc Mỹ phải tuyên bố 'Mỹ hóa' trở lại.",
        "involvedConcept": "C_VietNamHoaChienTranh"
    },
    {
        "id": "E_CH5_DienBienPhuTrenKhong",
        "label": "Trận Điện Biên Phủ trên không (12/1972)",
        "aliases": "12 ngày đêm",
        "where": "L_HaNoiHaiPhong", "when": "P_1969_1973",
        "content": "Bắn rơi nhiều máy bay B52 của Mỹ tập kích vào Hà Nội, Hải Phòng.",
        "result": "Buộc Mỹ phải trở lại bàn hội nghị và ký Hiệp định Pa-ri.",
        "concepts_weighted": [("C_DienBienPhuTrenKhong", 10)]
    },

    # ================= TUYẾN 3: ĐẠI THẮNG MÙA XUÂN 1975 =================
    {
        "id": "E_CH5_PhuocLong1975",
        "label": "Chiến thắng Phước Long (1/1975)",
        "where": "L_MienNam", "when": "P_1973_1975",
        "achievements": "Trận trinh sát chiến lược, giúp Bộ Chính trị củng cố quyết tâm giải phóng miền Nam trong năm 1975."
    },
    {
        "id": "E_CH5_ChienDichTayNguyen",
        "label": "Chiến dịch Tây Nguyên (3/1975)",
        "where": "L_TayNguyen", "when": "P_1973_1975",
        "content": "Đánh đòn điểm huyệt ở Buôn Ma Thuột. Quân địch hoảng loạn rút chạy.",
        "achievements": "Chuyển cuộc kháng chiến từ thế tiến công chiến lược sang Tổng tiến công chiến lược trên toàn miền Nam.",
        "involvedConcept": "C_TongTienCong"
    },
    {
        "id": "E_CH5_ChienDichHoChiMinh",
        "label": "Chiến dịch Hồ Chí Minh (4/1975)",
        "where": "L_SaiGon", "when": "P_1973_1975",
        "content": "11h30 ngày 30/4, xe tăng tiến vào Dinh Độc Lập, bắt toàn bộ nội các chính quyền Sài Gòn.",
        "achievements": "Kết thúc thắng lợi cuộc kháng chiến chống Mỹ cứu nước.",
        "involvedConcept": "C_TongTienCong"
    }
]