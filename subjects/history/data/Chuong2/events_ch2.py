MOVEMENTS = [
    {
        "id": "M_CH2_DauTranhTuSan_1919_1923",
        "label": "Phong trào đấu tranh của giai cấp tư sản (1919-1923)",
        "aliases": "Chấn hưng nội hoá|Chống độc quyền cảng Sài Gòn|Phong trào tư sản",
        "where": "L_SaiGon", "when": "P_1918_1930",
        "org_weighted": [("O_TuSanVN", 10)],
        "content": "Đi đầu trong phong trào 'chấn hưng nội hoá, bài trừ ngoại hoá' (1919). Đấu tranh chống tư bản Pháp độc quyền cảng Sài Gòn và xuất cảng lúa gạo ở Nam Kỳ (1923).",
        "concepts_weighted": [("C_ChanHungNoiHoa", 10)]
    },
    {
        "id": "M_CH2_DauTranhTieuTuSan_1925_1926",
        "label": "Phong trào đấu tranh của tiểu tư sản (1925-1926)",
        "aliases": "Đòi thả Phan Bội Châu|Truy điệu Phan Châu Trinh|Tiểu tư sản đấu tranh",
        "where": "L_VietNam", "when": "P_1918_1930",
        "who_weighted": [("Pe_PhanBoiChau", 9), ("Pe_NguyenAnNinh", 8), ("Pe_PhanChauTrinh", 9)],
        "org_weighted": [("O_TieuTuSan", 10), ("O_NamDongThuXa", 7), ("O_HoiPhucViet", 7)],
        "content": "Lập nhà xuất bản tiến bộ (Cường học thư xã, Nam Đồng thư xã), ra báo (Chuông rè, An Nam trẻ). Tổ chức đòi thả Phan Bội Châu (1925), Nguyễn An Ninh (1926), đám tang Phan Châu Trinh (1926)."
    },
    {
        "id": "M_CH2_CongNhan_1919_1925",
        "label": "Phong trào công nhân (1919-1925)",
        "aliases": "Công nhân 1919-1925|Công nhân Nam Định|Công nhân Cẩm Phả",
        "where": "L_VietNam", "when": "P_1919_1925",
        "org_weighted": [("O_CongNhanVN", 10)],
        "content": "Diễn ra lẻ tẻ. Chủ yếu phá hợp đồng, bỏ trốn, lãn công đòi quyền lợi kinh tế tại Nam Định, Cẩm Phả, Hà Nội.",
        "limitations": "Chưa có tổ chức và lãnh đạo thống nhất, mang tính tự phát."
    },
    {
        "id": "M_CH2_CongNhan_1925_1930",
        "label": "Phong trào công nhân (1925-1930)",
        "aliases": "Bãi công Ba Son|Công nhân Phú Riềng|Công nhân 1925-1930",
        "where": "L_VietNam", "when": "P_1925_1930",
        "org_weighted": [("O_CongNhanVN", 10), ("O_CongHoi", 9)],
        "content": "Nổ ra nhiều nơi, có tổ chức và lãnh đạo (Công hội). Mục đích kết hợp đòi quyền lợi kinh tế và mục đích chính trị rõ ràng. Tiêu biểu: Ba Son (Sài Gòn), Phú Riềng (Bình Phước), A-vi-a (Hà Nội).",
        "concepts_weighted": [("C_BaiCong", 10)]
    },
    {
        "id": "M_CH2_PhongTrao_1930_1931",
        "label": "Phong trào cách mạng 1930-1931",
        "aliases": "Phong trào 1930-1931|Cách mạng 1930-1931",
        "where": "L_VietNam", "when": "P_1930_1931",
        "org_weighted": [("O_DangCongSanVN", 10), ("O_CongNhanVN", 9)],
        "cause": "Ảnh hưởng khủng hoảng 1929-1933; Mâu thuẫn dân tộc và giai cấp sâu sắc; Đảng Cộng sản vừa ra đời đã kịp thời lãnh đạo.",
        "content": "Bùng nổ từ đầu năm 1930. Từ tháng 5/1930, phát triển mạnh mẽ cả nước. Đỉnh cao tháng 9, 10/1930 ở Nghệ An và Hà Tĩnh.",
        "achievements": "Khẳng định vai trò lãnh đạo của Đảng; Hình thành khối liên minh công-nông.",
        "limitations": "Bị thực dân Pháp khủng bố tàn bạo, phong trào tạm thời lắng xuống từ đầu năm 1931.",
        "concepts_weighted": [("C_LienMinhCongNong", 10), ("C_TapDuotCachMang", 9)]
    },
    {
        "id": "M_CH2_PhongTraoDanChu_1936_1939",
        "label": "Phong trào dân chủ 1936-1939",
        "aliases": "Phong trào dân chủ 1936-1939|Phong trào 1936-1939|Phong trào dân chủ",
        "where": "L_VietNam", "when": "P_1936_1939",
        "org_weighted": [("O_DangCongSanVN", 10), ("O_MatTranDanChuDongDuong", 10)],
        "cause": "Quốc tế Cộng sản chủ trương lập Mặt trận Nhân dân chống phát xít. Ở Pháp, Mặt trận Nhân dân lên cầm quyền thi hành chính sách tiến bộ.",
        "content": "Diễn ra sôi nổi với các hình thức: Phong trào Đông Dương đại hội (mít tinh, đón Gô-đa), Đấu tranh nghị trường, Đấu tranh báo chí.",
        "result": "Buộc chính quyền thực dân nhượng bộ một số yêu sách dân sinh, dân chủ. Chấm dứt khi CTTG 2 bùng nổ (9/1939).",
        "achievements": "Là phong trào quần chúng rộng lớn, buộc Pháp nhượng bộ. Đảng tích lũy kinh nghiệm đấu tranh công khai, hợp pháp.",
        "concepts_weighted": [("C_DanSinhDanChu", 10), ("C_DauTranhNghiTruong", 8), ("C_DauTranhBaoChi", 8), ("C_TapDuotCachMang", 10)]
    },
    {
        "id": "M_CH2_CacCuocNoiDay_1940_1941",
        "label": "Các cuộc nổi dậy đầu tiên (1940-1941)",
        "aliases": "Khởi nghĩa Bắc Sơn|Khởi nghĩa Nam Kì|Binh biến Đô Lương",
        "where": "L_VietNam", "when": "P_1939_1945",
        "cause": "Chính sách thống trị tàn bạo của Pháp-Nhật làm mâu thuẫn dân tộc gay gắt.",
        "content": "Bao gồm khởi nghĩa Bắc Sơn (9/1940), Nam Kì (11/1940) và binh biến Đô Lương (1/1941).",
        "result": "Báo hiệu thời kì đấu tranh vũ trang, khởi nghĩa vũ trang giành chính quyền."
    },
    {
        "id": "M_CH2_CaoTraoKhangNhat",
        "label": "Cao trào Kháng Nhật cứu nước",
        "aliases": "Cao trào Kháng Nhật cứu nước|Kháng Nhật cứu nước|Tiền khởi nghĩa",
        "where": "L_VietNam", "when": "P_Mar_Aug_1945",
        "org_weighted": [("O_DangCongSanVN", 10), ("O_VietMinh", 9), ("O_VNTTGPQ", 8)],
        "content": "Phát triển mạnh mẽ. Ở Việt Bắc: giải phóng hàng loạt xã, châu. Ở Bắc Kì và Bắc Trung Kì: dấy lên phong trào 'Phá kho thóc, giải quyết nạn đói'.",
        "achievements": "Là cuộc tập dượt lần thứ ba của Đảng và quần chúng cho Cách mạng tháng Tám.",
        "concepts_weighted": [("C_PhaKhoThoc", 10), ("C_TapDuotCachMang", 10)]
    },
    {
        "id": "M_CH2_TongKhoiNghiaThangTam",
        "label": "Tổng khởi nghĩa tháng Tám năm 1945",
        "aliases": "Cách mạng tháng Tám|Tổng khởi nghĩa",
        "where": "L_VietNam", "when": "P_Aug_1945",
        "who_weighted": [("Pe_HoChiMinh", 10), ("Pe_VoNguyenGiap", 9)],
        "org_weighted": [("O_DangCongSanVN", 10), ("O_VietMinh", 10), ("O_VN_GiaiPhongQuan", 9)],
        "cause": "Khách quan: Nhật đầu hàng Đồng minh tạo thời cơ. Chủ quan: Sự lãnh đạo của Đảng, chuẩn bị chu đáo 15 năm và sự đồng lòng của toàn dân.",
        "content": "Bắt đầu chiều 16/8 tại Thái Nguyên. Các mốc thắng lợi: Bắc Giang, Hải Dương, Hà Tĩnh, Quảng Nam (18/8), Hà Nội (19/8), Huế (23/8), Sài Gòn (25/8). Đồng Nai Thượng, Hà Tiên giành cq cuối cùng (28/8).",
        "achievements": "Phá tan xiềng xích nô lệ Pháp - Nhật, lật nhào ngai vàng phong kiến. Lập nước Việt Nam Dân chủ Cộng hòa. Đảng trở thành Đảng cầm quyền.",
        "result": "Góp phần chiến thắng chủ nghĩa phát xít. Cổ vũ mạnh mẽ phong trào giải phóng dân tộc thế giới, nhất là Lào và Campuchia.",
        "concepts_weighted": [("C_ThoiCoCachMang", 10), ("C_DocLapTuDo", 10), ("C_DangCamQuyen", 10)]
    },
    
    
]
DOCUMENTS = [
    {
        "id": "D_CH2_YeuSachAnNam",
        "label": "Yêu sách của nhân dân An Nam (1919)",
        "aliases": "Bản Yêu sách của nhân dân An Nam|Yêu sách 8 điểm",
        "where": "L_Versailles", "when": "P_1918_1930",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "content": "Tháng 6/1919, Nguyễn Ái Quốc gửi bản Yêu sách tới Hội nghị Véc-xai đòi các quyền tự do, dân chủ, bình đẳng cho nhân dân An Nam."
    },
    {
        "id": "D_CH2_BaoNguoiCungKho",
        "label": "Báo Người cùng khổ (1922)",
        "aliases": "Người cùng khổ|Le Paria",
        "where": "L_Phap", "when": "P_1918_1930",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "content": "Nguyễn Ái Quốc làm Chủ nhiệm kiêm chủ bút, xuất bản năm 1922 để vạch trần tội ác của chủ nghĩa đế quốc."
    },
    {
        "id": "D_CH2_DuongKachMenh",
        "label": "Tác phẩm Đường Kách mệnh (1927)",
        "aliases": "Đường Kách mệnh|Sách Đường Kách mệnh",
        "where": "L_HongKong", "when": "P_1918_1930",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "org_weighted": [("O_HVNCMTN", 9)],
        "content": "Tập hợp các bài giảng của Nguyễn Ái Quốc trong các lớp đào tạo cán bộ tại Quảng Châu. Là tài liệu lí luận nền tảng cho cách mạng Việt Nam."
    },
    {
        "id": "D_CH2_CuongLinhChinhTri_1930",
        "label": "Cương lĩnh chính trị đầu tiên của Đảng",
        "aliases": "Cương lĩnh chính trị đầu tiên|Chính cương vắn tắt|Sách lược vắn tắt|Điều lệ vắn tắt",
        "where": "L_HongKong", "when": "P_1930",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "content": "Xác định đường lối: làm tư sản dân quyền và thổ địa cách mạng để tiến tới xã hội cộng sản. Nhiệm vụ: Đánh đổ Pháp, phong kiến, giành độc lập, lập chính phủ công-nông-binh.",
        "concepts_weighted": [("C_CachMangTuSanDanQuyen", 10), ("C_ThoDiaCachMang", 10), ("C_CachMangVoSan", 9)]
    },
    {
        "id": "D_CH2_VanDeDanCay",
        "label": "Cuốn sách Vấn đề dân cày (1938)",
        "aliases": "Vấn đề dân cày",
        "where": "L_VietNam", "when": "P_1936_1939",
        "who_weighted": [("Pe_TruongChinh", 10), ("Pe_VoNguyenGiap", 10)],
        "content": "Giới thiệu chủ nghĩa Mác-Lê-nin và chính sách của Đảng, được lưu hành rộng rãi trong thời kì đấu tranh báo chí công khai."
    },
    {
        "id": "D_CH3_ChiThiNhatPhap",
        "label": "Chỉ thị Nhật - Pháp bắn nhau và hành động của chúng ta",
        "aliases": "Nhật-Pháp bắn nhau và hành động của chúng ta",
        "where": "L_VietNam", "when": "P_Mar_Aug_1945",
        "org_weighted": [("O_DangCongSanVN", 10)],
        "cause": "Tối 9/3/1945, Nhật đảo chính Pháp độc chiếm Đông Dương.",
        "content": "Phát động cao trào 'Kháng Nhật cứu nước' làm tiền đề cho cuộc tổng khởi nghĩa.",
        "concepts_weighted": [("C_KhoiNghiaTungPhan", 10)]
    },
    {
        "id": "D_CH2_QuanLenhSo1",
        "label": "Quân lệnh số 1",
        "aliases": "Lệnh Tổng khởi nghĩa",
        "where": "L_VietNam", "when": "P_Aug_1945",
        "org_weighted": [("O_UyBanKhoiNghia", 10)],
        "content": "Ban bố ngày 13/8/1945 bởi Uỷ ban Khởi nghĩa toàn quốc, chính thức phát lệnh Tổng khởi nghĩa trong cả nước."
    },
    {
        "id": "D_CH2_TuyenNgonDocLap",
        "label": "Tuyên ngôn Độc lập (1945)",
        "aliases": "Bản Tuyên ngôn Độc lập",
        "where": "L_BaDinh", "when": "P_Sep_1945",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "org_weighted": [("O_ChinhPhuLamThoi", 10)],
        "content": "Được Chủ tịch Hồ Chí Minh soạn thảo và đọc tại Quảng trường Ba Đình ngày 2/9/1945, khai sinh ra nước Việt Nam Dân chủ Cộng hoà.",
        "concepts_weighted": [("C_DocLapTuDo", 10)]
    },
]


EVENTS = [
    {
        "id": "E_CH2_ThanhLapVNQDD",
        "label": "Việt Nam Quốc dân Đảng (1927-1930)",
        "aliases": "Thành lập Việt Nam Quốc dân Đảng|VNQDĐ ra đời|Khởi nghĩa Yên Bái",
        "where": "L_VietNam", "when": "P_1918_1930",
        "who_weighted": [("Pe_NguyenThaiHoc", 10), ("Pe_PhoDucChinh", 8)],
        "org_weighted": [("O_VNQDD", 10), ("O_NamDongThuXa", 8), ("O_TuSanVN", 7)],
        "context": "Thành lập tháng 12/1927 trên cơ sở hạt nhân là Nam Đồng thư xã.",
        "cause": "Theo khuynh hướng cách mạng dân chủ tư sản. Mục tiêu đánh đuổi giặc Pháp, thiết lập dân quyền.",
        "content": "Sử dụng phương pháp bạo động, ám sát cá nhân. Tổ chức cuộc khởi nghĩa Yên Bái (tháng 2/1930).",
        "result": "Thất bại, đảng tan rã. Chứng tỏ khuynh hướng dân chủ tư sản đã hoàn toàn bất lực trước nhiệm vụ cứu nước.",
        "concepts_weighted": [("C_KhuynhHuongTuSan", 10), ("C_BaoDongAmSat", 9)]
    },
    {
        "id": "E_CH2_ThanhLapTanViet",
        "label": "Tân Việt Cách mạng đảng (1928)",
        "aliases": "Đảng Tân Việt|Tân Việt Cách mạng đảng|Hội Phục Việt đổi tên",
        "where": "L_TrungKy", "when": "P_1918_1930",
        "org_weighted": [("O_TanViet", 10), ("O_HoiPhucViet", 8), ("O_HVNCMTN", 9), ("O_TieuTuSan", 8)],
        "context": "Tháng 7/1928, Hội Phục Việt đổi tên thành Tân Việt Cách mạng đảng, hoạt động chủ yếu ở Trung Kì.",
        "content": "Giới thiệu sách báo tiến bộ, truyền bá chủ nghĩa Mác-Lê-nin. Cử đảng viên dự huấn luyện của Hội VN Cách mạng Thanh niên.",
        "result": "Từ khuynh hướng dân chủ tư sản ban đầu chuyển dần sang khuynh hướng vô sản.",
        "concepts_weighted": [("C_KhuynhHuongVoSan", 9), ("C_KhuynhHuongTuSan", 5)]
    },
    {
        "id": "E_CH2_DaiHoiTours_1920",
        "label": "Nguyễn Ái Quốc dự Đại hội Tua (1920)",
        "aliases": "Đại hội Tua|Bỏ phiếu tán thành Quốc tế Cộng sản",
        "where": "L_Tours", "when": "P_1918_1930",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "org_weighted": [("O_DangXaHoiPhap", 8), ("O_DangCongSanPhap", 9), ("O_QuocTeCongSan", 9)],
        "content": "Tháng 12/1920, bỏ phiếu tán thành gia nhập Quốc tế Cộng sản và tham gia lập Đảng CS Pháp.",
        "result": "Bước ngoặt: Nguyễn Ái Quốc chuyển từ chủ nghĩa yêu nước đến chủ nghĩa Mác-Lênin, đi theo cách mạng vô sản.",
        "concepts_weighted": [("C_ChuNghiaMacLenin", 10), ("C_CachMangVoSan", 10)]
    },
    {
        "id": "E_CH2_BaToChucCongSan_1929",
        "label": "Sự ra đời ba tổ chức cộng sản (1929)",
        "aliases": "Ba tổ chức cộng sản|Ba tổ chức cộng sản ra đời",
        "where": "L_VietNam", "when": "P_1918_1930",
        "org_weighted": [("O_DDCSD", 10), ("O_ANCSD", 10), ("O_DDCSLD", 10), ("O_HVNCMTN", 8), ("O_TanViet", 8)],
        "context": "Năm 1928-1929, phong trào cách mạng phát triển mạnh, đòi hỏi phải có Đảng Cộng sản lãnh đạo.",
        "content": "Tháng 6/1929: Đông Dương CSĐ (Bắc Kì). Tháng 8/1929: An Nam CSĐ (Nam Kì). Tháng 9/1929: Đông Dương CS Liên đoàn (Sài Gòn).",
        "result": "Chứng tỏ sự trưởng thành của giai cấp công nhân. Tuy nhiên hoạt động riêng rẽ gây nguy cơ chia rẽ lớn.",
    },
    {
        "id": "E_CH2_HoiNghiThanhLapDang_1930",
        "label": "Hội nghị thành lập Đảng Cộng sản Việt Nam",
        "aliases": "Thành lập Đảng Cộng sản Việt Nam|Đảng Cộng sản Việt Nam ra đời|Hội nghị hợp nhất",
        "where": "L_HongKong", "when": "P_1930",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "org_weighted": [("O_DangCongSanVN", 10), ("O_QuocTeCongSan", 9)],
        "cause_direct": "Sự chia rẽ của 3 tổ chức cộng sản đòi hỏi phải hợp nhất.",
        "content": "Đầu năm 1930 tại Hương Cảng, Nguyễn Ái Quốc chủ trì hội nghị hợp nhất thành Đảng Cộng sản Việt Nam và thông qua Cương lĩnh chính trị đầu tiên.",
        "achievements": "Chấm dứt khủng hoảng về đường lối cứu nước và giai cấp lãnh đạo.",
        "result": "Là bước chuẩn bị tất yếu đầu tiên cho những bước phát triển nhảy vọt về sau của cách mạng Việt Nam."
    },
    {
        "id": "E_CH2_XoVietNgheTinh",
        "label": "Đỉnh cao Xô viết Nghệ-Tĩnh",
        "aliases": "Xô viết Nghệ-Tĩnh|Xô viết Nghệ Tĩnh|Chính quyền Xô viết",
        "where": "L_NgheTinh", "when": "P_1930_1931",
        "org_weighted": [("O_ChinhQuyenXoViet", 10)],
        "context": "Thuộc phong trào cách mạng 1930-1931. Biểu tình của nông dân làm bộ máy tay sai tê liệt.",
        "content": "Chính quyền nhân dân lập ra dưới hình thức xô viết. Chính trị: ban bố quyền tự do. Kinh tế: chia ruộng đất, bãi bỏ thuế vô lí. Văn hóa: dạy chữ Quốc ngữ.",
        "result": "Là đỉnh cao của phong trào, chứng tỏ sức mạnh của quần chúng khi có Đảng lãnh đạo."
    },
    {
        "id": "E_CH2_HoiNghiTW_7_1936",
        "label": "Hội nghị Trung ương Đảng (7/1936)",
        "aliases": "Hội nghị tháng 7/1936|Chủ trương đấu tranh 1936-1939",
        "where": "L_VietNam", "when": "P_1936_1939",
        "org_weighted": [("O_DangCongSanVN", 10), ("O_MatTranDanChuDongDuong", 9)],
        "cause": "Tình hình thế giới thay đổi (nguy cơ phát xít) và phong trào trong nước dần phục hồi.",
        "content": "Xác định nhiệm vụ trước mắt là chống chế độ phản động thuộc địa, chống phát xít. Đòi dân sinh, dân chủ, hòa bình. Thành lập Mặt trận Dân chủ Đông Dương.",
        "concepts_weighted": [("C_DanSinhDanChu", 10)]
    },
    {
        "id": "E_CH2_PhapNhatBocLot",
        "label": "Tình hình Việt Nam dưới ách Pháp - Nhật",
        "aliases": "Kinh tế chỉ huy|Nhổ lúa trồng đay|Ách thống trị của Pháp-Nhật",
        "where": "L_VietNam", "when": "P_1939_1945",
        "org_weighted": [("O_ThucDanPhap", 10), ("O_QuanPhietNhat", 10)],
        "content": "Pháp thực thi 'Kinh tế chỉ huy', Nhật bắt 'nhổ lúa trồng đay', thủ tiêu dân chủ, phát xít hóa bộ máy.",
        "result": "Gây ra nạn đói nghiêm trọng cuối 1944 đầu 1945, làm mâu thuẫn dân tộc lên đến đỉnh điểm.",
        "concepts_weighted": [("C_KinhTeChiHuy", 10), ("C_NanDoi1945", 10)]
    },
    {
        "id": "E_CH2_HoiNghiTW_11_1939",
        "label": "Hội nghị Ban Chấp hành Trung ương Đảng (11/1939)",
        "aliases": "Hội nghị tháng 11/1939|Hội nghị Bà Điểm",
        "where": "L_HocMon", "when": "P_1939_1945",
        "who_weighted": [("Pe_NguyenVanCu", 10)],
        "org_weighted": [("O_DangCongSanVN", 10)],
        "content": "Xác định nhiệm vụ của cách mạng lúc này là giải phóng dân tộc, đánh đổ Pháp và tay sai để giành độc lập."
    },
    {
        "id": "E_CH2_HoiNghiTW_8_1941",
        "label": "Hội nghị Trung ương Đảng lần thứ 8 (5/1941)",
        "aliases": "Hội nghị tháng 5/1941|Hội nghị Pác Bó|Hội nghị TW 8",
        "where": "L_CaoBang", "when": "P_1939_1945",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "org_weighted": [("O_DangCongSanVN", 10)],
        "content": "Giải quyết vấn đề dân tộc trong từng nước Đông Dương. Chuẩn bị khởi nghĩa vũ trang là nhiệm vụ trung tâm. Hình thái: từ khởi nghĩa từng phần lên tổng khởi nghĩa.",
        "achievements": "Hoàn chỉnh chuyển hướng chiến lược cách mạng, đưa nhiệm vụ giải phóng dân tộc lên hàng đầu.",
        "concepts_weighted": [("C_KhoiNghiaVuTrang", 10), ("C_KhoiNghiaTungPhan", 10), ("C_TongKhoiNghia", 10)]
    },
    {
        "id": "E_CH2_ThanhLapVietMinh_1941",
        "label": "Thành lập Mặt trận Việt Minh (19/5/1941)",
        "aliases": "Mặt trận Việt Minh ra đời",
        "where": "L_CaoBang", "when": "P_1939_1945",
        "org_weighted": [("O_VietMinh", 10), ("O_DangCongSanVN", 9)],
        "content": "Thành lập nhằm tập hợp đông đảo nhân dân. Các tổ chức quần chúng gọi là Hội Cứu quốc. Thu hút đông đảo quần chúng tham gia chuẩn bị tổng khởi nghĩa."
    },
    {
        "id": "E_CH2_ThanhLapVNTTGPQ_1944",
        "label": "Thành lập Đội VN Tuyên truyền Giải phóng quân",
        "aliases": "Thành lập Việt Nam Tuyên truyền Giải phóng quân|22/12/1944",
        "where": "L_CaoBang", "when": "P_1939_1945",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "org_weighted": [("O_VNTTGPQ", 10)],
        "content": "Thành lập ngày 22/12/1944 theo chỉ thị của Hồ Chí Minh. Ngay sau đó đánh thắng 2 trận Phay Khắt và Nà Ngần."
    },
    {
        "id": "E_CH2_NhatDaoChinhPhap_1945",
        "label": "Nhật đảo chính Pháp (9/3/1945)",
        "aliases": "Nhật đảo chính Pháp|9/3/1945",
        "where": "L_VietNam", "when": "P_1939_1945",
        "org_weighted": [("O_QuanPhietNhat", 10), ("O_ThucDanPhap", 10)],
        "cause": "Chiến tranh thế giới 2 sắp kết thúc, Pháp ráo riết chờ cơ hội phản công Nhật.",
        "content": "Tối 9/3/1945, Nhật tiến hành đảo chính Pháp trên toàn Đông Dương, Pháp đầu hàng."
    },
    {
        "id": "E_CH2_HoiNghiQuanSuBacKi",
        "label": "Hội nghị Quân sự Bắc Kì (4/1945)",
        "aliases": "Hội nghị Quân sự Bắc Kì",
        "where": "L_BacKy", "when": "P_Mar_Aug_1945",
        "org_weighted": [("O_VN_GiaiPhongQuan", 10), ("O_CuuQuocQuan", 8), ("O_VNTTGPQ", 8)],
        "content": "Quyết định thống nhất Cứu quốc quân và VNTT Giải phóng quân thành Việt Nam Giải phóng quân, xây dựng căn cứ địa kháng Nhật."
    },
    {
        "id": "E_CH2_ThanhLapKhuGiaiPhong",
        "label": "Thành lập Khu giải phóng Việt Bắc (5/1945)",
        "aliases": "Khu giải phóng Việt Bắc|Tân Trào",
        "where": "L_VietBac", "when": "P_Mar_Aug_1945",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "content": "Tháng 5/1945, Hồ Chí Minh về Tân Trào. Khu giải phóng Việt Bắc được thành lập, trở thành căn cứ địa chính của cách mạng cả nước."
    },
    {
        "id": "E_CH2_NhatDauHangDongMinh",
        "label": "Nhật Bản đầu hàng Đồng minh (15/8/1945)",
        "aliases": "Phát xít Nhật đầu hàng|15/8/1945",
        "where": "L_Global", "when": "P_Aug_1945",
        "who_weighted": [("Pe_TranTrongKim", 8)],
        "org_weighted": [("O_QuanPhietNhat", 10), ("O_LienHopQuoc_WW2", 10)],
        "content": "Quân Nhật ở Đông Dương rệu rã, Chính phủ thân Nhật hoang mang cực độ, trong khi Đồng minh chưa vào.",
        "result": "Tạo ra thời cơ 'ngàn năm có một' để tổng khởi nghĩa giành chính quyền.",
        "concepts_weighted": [("C_ThoiCoCachMang", 10)]
    },
    {
        "id": "E_CH2_HoiNghiTanTrao_8_1945",
        "label": "Hội nghị toàn quốc của Đảng (14-15/8/1945)",
        "aliases": "Hội nghị Tân Trào|Hội nghị toàn quốc",
        "where": "L_TuyenQuang", "when": "P_Aug_1945",
        "org_weighted": [("O_DangCongSanVN", 10)],
        "content": "Thông qua kế hoạch lãnh đạo toàn dân tổng khởi nghĩa, quyết định chính sách đối nội, đối ngoại sau khi giành chính quyền."
    },
    {
        "id": "E_CH2_QuocDanDaiHoiTanTrao",
        "label": "Đại hội Quốc dân Tân Trào (16-17/8/1945)",
        "aliases": "Đại hội Quốc dân",
        "where": "L_TuyenQuang", "when": "P_Aug_1945",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "org_weighted": [("O_VietMinh", 10), ("O_ChinhPhuLamThoi", 10)],
        "content": "Tán thành chủ trương Tổng khởi nghĩa, thông qua 10 chính sách Việt Minh, cử ra Uỷ ban Dân tộc giải phóng Việt Nam do Hồ Chí Minh làm Chủ tịch."
    },
    {
        "id": "E_CH2_BaoDaiThoaiVi",
        "label": "Vua Bảo Đại thoái vị (30/8/1945)",
        "aliases": "Bảo Đại thoái vị",
        "where": "L_Hue", "when": "P_Aug_1945",
        "who_weighted": [("Pe_BaoDai", 10)],
        "content": "Ngày 30/8/1945, vua Bảo Đại tuyên bố thoái vị và trao ấn kiếm cho đại diện chính quyền cách mạng.",
        "result": "Đánh dấu chế độ phong kiến Việt Nam hoàn toàn sụp đổ."
    },
    {
        "id": "E_CH2_QuocKhanh2_9",
        "label": "Lễ Độc lập ngày 2/9/1945",
        "aliases": "Ngày 2/9|Nước Việt Nam Dân chủ Cộng hoà ra đời",
        "where": "L_BaDinh", "when": "P_Sep_1945",
        "who_weighted": [("Pe_HoChiMinh", 10)],
        "org_weighted": [("O_ChinhPhuLamThoi", 10)],
        "content": "Hồ Chí Minh đọc Tuyên ngôn Độc lập, chính thức khai sinh nước Việt Nam Dân chủ Cộng hòa.",
        "concepts_weighted": [("C_DocLapTuDo", 10)]
    },
]