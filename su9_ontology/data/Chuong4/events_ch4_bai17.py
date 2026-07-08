# data/ch5/events_ch5_bai17.py

DOCUMENTS = [
    {
        "id": "D_CH5_Luat1059",
        "label": "Luật 10/59",
        "where": "L_MienNam", "when": "P_1954_1965",
        "org_weighted": [("O_ChinhQuyenDiem", 10)],
        "content": "Thiết lập máy chém khắp miền Nam, giết hại vô số người vô tội, đẩy mâu thuẫn lên tột đỉnh.",
    },
    {
        "id": "D_CH5_NghiQuyet15",
        "label": "Nghị quyết Trung ương 15 (Đầu 1959)",
        "aliases": "Hội nghị Ban Chấp hành Trung ương Đảng lần thứ 15",
        "where": "L_VietNam", "when": "P_1954_1965",
        "content": "Xác định con đường cơ bản: sử dụng bạo lực cách mạng đánh đổ chính quyền Mỹ - Diệm.",
        "involvedConcept": "C_BaoLucCachMang"
    }
]

MOVEMENTS = [
    {
        "id": "M_CH5_DongKhoi",
        "label": "Phong trào Đồng khởi (1959-1960)",
        "aliases": "Đồng khởi|Đồng khởi Bến Tre",
        "where": "L_BenTre", "when": "P_1959_1960",
        "cause_direct": "Sự soi sáng của Nghị quyết 15 trước ách kìm kẹp tàn bạo của Luật 10/59.",
        "content": "Từ Bến Tre lan ra khắp Nam Bộ, Tây Nguyên. Quần chúng nổi dậy phá thế kìm kẹp.",
        "result": "Làm lung lay tận gốc chính quyền Diệm. Đánh dấu cách mạng chuyển từ thế giữ gìn lực lượng sang thế tiến công.",
    }
]

EVENTS = [
    # ================= TUYẾN 1: MIỀN BẮC =================
    {
        "id": "E_CH5_CaiCachRuongDat",
        "label": "Hoàn thành Cải cách ruộng đất (1954-1957)",
        "where": "L_MienBac", "when": "P_1954_1965",
        "content": "Tịch thu ruộng đất chia cho dân nghèo. Thực hiện khẩu hiệu 'Người cày có ruộng'. Giai cấp địa chủ bị xóa bỏ.",
    },
    {
        "id": "E_CH5_ChiVienMienNam",
        "label": "Miền Bắc chi viện cho miền Nam",
        "aliases": "Mở đường Trường Sơn|Nghĩa vụ hậu phương",
        "where": "L_TruongSon", "when": "P_1954_1965",
        "content": "Mở tuyến đường Trường Sơn (1959). Cung cấp hàng vạn cán bộ, vũ khí, lương thực cho tiền tuyến.",
        "concepts_weighted": [("C_HauPhuongTienTuyen", 10)]
    },

    # ================= TUYẾN 2: MIỀN NAM CHỐNG CHIẾN TRANH ĐẶC BIỆT =================
    {
        "id": "E_CH5_ApBac",
        "label": "Chiến thắng Ấp Bắc (2/1/1963)",
        "where": "L_MienNam", "when": "P_1961_1965",
        "org_weighted": [("O_MTDTGPMNVN", 10)],
        "achievements": "Chứng tỏ quân dân miền Nam hoàn toàn có khả năng đánh bại chiến lược 'Chiến tranh đặc biệt'.",
        "involvedConcept": "C_ChienTranhDacBiet"
    },
    {
        "id": "E_CH5_BinhGia",
        "label": "Chiến thắng Bình Giã (12/1964)",
        "where": "L_MienNam", "when": "P_1961_1965",
        "achievements": "Làm phá sản VỀ CƠ BẢN chiến lược 'Chiến tranh đặc biệt' của Mỹ.",
        "involvedConcept": "C_ChienTranhDacBiet"
    },
    {
        "id": "E_CH5_PhaApChienLuoc",
        "label": "Phong trào phá Ấp chiến lược",
        "aliases": "Chống phá bình định",
        "where": "L_MienNam", "when": "P_1961_1965",
        "content": "Quần chúng kiên quyết bám đất giữ làng, phá vỡ 'xương sống' của Chiến tranh đặc biệt.",
        "involvedConcept": "C_ApChienLuoc"
    }
]