# data/ch4/events_ch4_bai14.py

DOCUMENTS = [
    {
        "id": "D_CH4_HienPhap1946",
        "label": "Bản Hiến pháp đầu tiên (9/11/1946)",
        "aliases": "Hiến pháp 1946",
        "where": "L_VietNam", "when": "P_1945_1946",
        "org_weighted": [("O_QuocHoiKhoa1", 10)],
        "content": "Bản Hiến pháp đầu tiên của nước VNDCCH được Quốc hội thông qua.",
        "result": "Khẳng định tính hợp pháp của chính quyền mới."
    },
    {
        "id": "D_CH4_HiepUocHoaPhap",
        "label": "Hiệp ước Hoa - Pháp (28/2/1946)",
        "aliases": "Hiệp ước Hoa-Pháp|Pháp bắt tay với Tưởng",
        "where": "L_Global", "when": "P_1945_1946",
        "org_weighted": [("O_THDQ", 10), ("O_ThucDanPhap", 10)],
        "content": "Pháp nhượng cho Tưởng một số quyền lợi ở Trung Quốc để đổi lấy quyền đưa quân ra Bắc Việt Nam thay Tưởng giải giáp quân Nhật.",
        "result": "Đặt nhân dân ta trước hai con đường: đánh Pháp ngay hoặc hòa hoãn để đẩy quân Tưởng về nước."
    },
    {
        "id": "D_CH4_HiepDinhSoBo",
        "label": "Hiệp định Sơ bộ (6/3/1946)",
        "aliases": "Mùng 6 tháng 3",
        "where": "L_VietNam", "when": "P_1945_1946",
        "org_weighted": [("O_VNDCCH", 10), ("O_ThucDanPhap", 10)],
        "cause_direct": "Sự ra đời của Hiệp ước Hoa - Pháp buộc ta phải chọn sách lược 'Hòa để tiến'.",
        "content": "Pháp công nhận VN là quốc gia tự do. VN đồng ý cho 15.000 quân Pháp ra Bắc thay Tưởng và rút dần trong 5 năm.",
        "result": "Đẩy được 20 vạn quân Tưởng về nước, tranh thủ thời gian chuẩn bị lực lượng.",
        "involvedConcept": "C_HoaDeTien"
    },
    {
        "id": "D_CH4_TamUoc14_9",
        "label": "Bản Tạm ước (14/9/1946)",
        "aliases": "Tạm ước 14/9",
        "where": "L_Global", "when": "P_1945_1946",
        "org_weighted": [("O_VNDCCH", 10), ("O_ThucDanPhap", 10)],
        "cause_direct": "Cuộc đàm phán chính thức tại Phông-ten-nơ-blô thất bại do Pháp ngoan cố.",
        "content": "Chủ tịch Hồ Chí Minh ký với Pháp bản Tạm ước, tiếp tục nhượng cho Pháp một số quyền lợi kinh tế, văn hóa.",
        "result": "Kéo dài thêm thời gian hòa hoãn để xây dựng lực lượng.",
        "involvedConcept": "C_HoaDeTien"
    }
]

EVENTS = [
    # Tuyến 1: Chính trị & Đối nội
    {
        "id": "E_CH4_TongTuyenCu",
        "label": "Tổng tuyển cử bầu Quốc hội khóa I (6/1/1946)",
        "aliases": "Bầu cử Quốc hội đầu tiên",
        "where": "L_VietNam", "when": "P_1945_1946",
        "content": "Hơn 300 đại biểu được bầu vào Quốc hội. Thành lập Chính phủ liên hiệp kháng chiến.",
        "concepts_weighted": [("C_ChinhQuyenDanChu", 10)]
    },
    
    # Tuyến 2: Diệt giặc đói, dốt, tài chính (Các biện pháp)
    {
        "id": "E_CH4_DietGiacDoi",
        "label": "Giải quyết nạn đói",
        "aliases": "Diệt giặc đói|Hũ gạo cứu đói|Ngày đồng tâm",
        "where": "L_VietNam", "when": "P_1945_1946",
        "content": "Trước mắt: Nhường cơm sẻ áo, lập hũ gạo cứu đói. Lâu dài: Tăng gia sản xuất.",
    },
    {
        "id": "E_CH4_DietGiacDot",
        "label": "Xóa nạn mù chữ",
        "aliases": "Diệt giặc dốt|Bình dân học vụ",
        "where": "L_VietNam", "when": "P_1945_1946",
        "org_weighted": [("O_NhaBinhDanHocVu", 10)],
        "content": "Hơn 90% dân số mù chữ. Ngày 8/9/1945, lập Nha Bình dân học vụ.",
    },
    {
        "id": "E_CH4_GiaiQuyetTaiChinh",
        "label": "Giải quyết khó khăn tài chính",
        "aliases": "Tuần lễ vàng|Quỹ độc lập|Tiền Việt Nam",
        "where": "L_VietNam", "when": "P_1945_1946",
        "content": "Phát động 'Quỹ độc lập', 'Tuần lễ vàng'. Tháng 11/1946, lưu hành tiền Việt Nam.",
    },

    # Tuyến 3: Kháng chiến ở Nam Bộ
    {
        "id": "E_CH4_PhapXamLuocNamBo",
        "label": "Pháp trở lại xâm lược Nam Bộ (23/9/1945)",
        "aliases": "Pháp đánh Nam Bộ|Kháng chiến Nam Bộ",
        "where": "L_SaiGonChoLon", "when": "P_1945_1946",
        "org_weighted": [("O_ThucDanPhap", 10), ("O_QuanAnh", 8)],
        "content": "Được quân Anh giúp sức, Pháp đánh úp trụ sở UB Hành chính Nam Bộ. Nhân dân Nam Bộ anh dũng kháng chiến.",
        "result": "Giam chân quân Pháp tại miền Nam trong nhiều tháng.",
    }
]