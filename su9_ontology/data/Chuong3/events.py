# data/ch3/events_ch3.py

DOCUMENTS = [
    {
        "id": "D_CH3_HocThuyetTruman",
        "label": "Học thuyết Tru-man (3/1947)",
        "aliases": "Học thuyết Tru-man|Học thuyết Truman",
        "where": "L_My", "when": "P_1947_1989",
        "who_weighted": [("Pe_Truman", 10)],
        "org_weighted": [("O_PheTBCN", 10)],
        "cause": "Sự bất đồng giữa Mỹ và Liên Xô trong việc giải quyết hậu quả WWII (vấn đề Đông Âu và chia cắt Đức).",
        "content": "Tổng thống Mỹ Tru-man công bố quan điểm chống lại chủ nghĩa cộng sản.",
        "result": "Đánh dấu sự chuyển hướng sang chính sách đối đầu với Liên Xô của Mỹ, khởi đầu Chiến tranh lạnh.",
        "concepts_weighted": [("C_ChienTranhLanh", 10)]
    },
    {
        "id": "D_CH3_KeHoachMarshall",
        "label": "Kế hoạch Mác-san (1947)",
        "aliases": "Kế hoạch Mác-san|Kế hoạch Marshall",
        "where": "L_TayAu", "when": "P_1947_1989",
        "org_weighted": [("O_PheTBCN", 10)],
        "content": "Mỹ đầu tư khoảng 13 tỉ USD cho 16 nước Tây Âu phục hồi kinh tế nhằm lôi kéo đồng minh.",
        "concepts_weighted": [("C_DoiDauHaiCuc", 8)]
    },
    {
        "id": "D_CH3_BaoCaoZhdanov",
        "label": "Bản báo cáo của Giơ-đa-nốp (9/1947)",
        "aliases": "Bản báo cáo của Giơ-đa-nốp|Zhdanov",
        "where": "L_BaLan", "when": "P_1947_1989",
        "who_weighted": [("Pe_Zhdanov", 10)],
        "org_weighted": [("O_PheXHCN", 10)],
        "content": "Đại diện Liên Xô tuyên bố thế giới đã chia thành hai phe: phe đế quốc (Mỹ lãnh đạo) và phe XHCN (Liên Xô làm trụ cột).",
        "concepts_weighted": [("C_DoiDauHaiCuc", 10)]
    },
    {
        "id": "D_CH3_ChienLuocToanCau",
        "label": "Chiến lược toàn cầu của Mỹ",
        "aliases": "Học thuyết toàn cầu|Bá chủ thế giới",
        "where": "L_My", "when": "P_1945_1991",
        "org_weighted": [("O_PheTBCN", 10)],
        "content": "Mục tiêu: Chống phá phe XHCN, đàn áp phong trào GPDT, làm bá chủ thế giới.",
        "involvedConcept": "C_ChienLuocToanCau"
    },
    {
        "id": "D_CH3_ThoaThuanMaastricht",
        "label": "Thỏa thuận thành lập Liên minh châu Âu (1991)",
        "aliases": "Thành lập EU|Hiệp ước Maastricht",
        "where": "L_TayAu", "when": "P_1973_1991",
        "org_weighted": [("O_EU", 10)],
        "content": "Quyết định xây dựng thị trường tiền tệ (đồng Euro) và nhất thể hóa chính trị Tây Âu.",
        "result": "Đặt nền móng cho quá trình nhất thể hóa châu Âu toàn diện.",
        "involvedConcept": "C_NhatTheHoa"
    },
    {
        "id": "D_CH3_HiepUocAnNinhMyNhat",
        "label": "Hiệp ước an ninh Mỹ - Nhật (1951)",
        "aliases": "Hiệp ước an ninh Mỹ-Nhật",
        "where": "L_NhatBan", "when": "P_1945_1973",
        "org_weighted": [("O_PheTBCN", 10)],
        "content": "Cho phép Mỹ đặt căn cứ quân sự. Nhật Bản được bảo hộ hạt nhân để tập trung phát triển kinh tế.",
    },
    {
        "id": "D_CH3_KeHoachMountbatten",
        "label": "Kế hoạch Mao-bát-tơn (1947)",
        "aliases": "Kế hoạch Mountbatten|Chia cắt Ấn Độ",
        "where": "L_AnDo", "when": "P_1945_1950",
        "content": "Chia Ấn Độ thành 2 quốc gia tự trị dựa trên tôn giáo: Ấn Độ (Ấn Độ giáo) và Pa-ki-xtan (Hồi giáo).",
    },
    {
        "id": "D_CH3_HiepUocBali",
        "label": "Hiệp ước Ba-li (2/1976)",
        "aliases": "Hiệp ước thân thiện và hợp tác Đông Nam Á",
        "where": "L_DongNamA", "when": "P_1973_1991",
        "org_weighted": [("O_ASEAN", 10)],
        "content": "Xác định những nguyên tắc cơ bản trong quan hệ giữa các nước ASEAN.",
        "result": "Đánh dấu sự khởi sắc của ASEAN, chuyển từ hợp tác lỏng lẻo sang chặt chẽ."
    },
]

EVENTS = [
    {
        "id": "E_CH3_NguyenNhan_ChienTranhLanh",
        "label": "Nguyên nhân bùng nổ Chiến tranh lạnh",
        "aliases": "Chiến tranh lạnh|Nguyên nhân Chiến tranh lạnh|Học thuyết Tru-man|Báo cáo Giơ-đa-nốp",
        "where": "L_Global", "when": "P_1947_1989",
        "who_weighted": [("Pe_Truman", 10), ("Pe_Zhdanov", 9)],
        "org_weighted": [("O_PheTBCN", 10), ("O_PheXHCN", 10)],
        "cause_deep": "Sự đối lập về hệ tư tưởng và mục tiêu chiến lược giữa Mỹ (TBCN) và Liên Xô (XHCN).",
        "cause_direct": "Bất đồng sâu sắc trong việc giải quyết hậu quả WWII (vấn đề Đông Âu và chia cắt nước Đức).",
        "content": """+ Tháng 3/1947: Tổng thống Mỹ Tru-man công khai chống chủ nghĩa cộng sản, khởi xướng Chiến tranh lạnh.
      + Tháng 9/1947: Đại diện Liên Xô (Giơ-đa-nốp) tuyên bố thế giới đã chia thành 2 phe đối lập.""",
        "result": "Mỹ tiến hành chính sách thù địch về mọi mặt chống Liên Xô, mở màn Chiến tranh lạnh kéo dài hơn 40 năm.",
        "concepts_weighted": [("C_ChienTranhLanh", 10), ("C_DoiDauHaiCuc", 10)]
    },
    {
        "id": "E_CH3_DoiDauKinhTe_ChinhTri",
        "label": "Sự đối đầu về Kinh tế và Chính trị - Quân sự",
        "aliases": "Chiến tranh lạnh|Thành lập NATO|Thành lập SEV|Thành lập Vác-sa-va|Kế hoạch Mác-san",
        "where": "L_Global", "when": "P_1947_1989",
        "org_weighted": [("O_PheTBCN", 10), ("O_PheXHCN", 10), ("O_NATO", 9), ("O_SEV", 9), ("O_Warsaw", 9)],
        "content": """+ Kinh tế: Mỹ thực hiện Kế hoạch Mác-san (1947) viện trợ Tây Âu. Liên Xô lập Hội đồng Tương trợ kinh tế - SEV (1949).
      + Chính trị-quân sự: Mỹ lập Tổ chức Hiệp ước Bắc Đại Tây Dương - NATO (1949). Liên Xô lập Hiệp ước Vác-sa-va (1955).""",
        "result": "Xác lập cục diện hai cực, hai phe đối đầu gay gắt trên mọi lĩnh vực.",
        "concepts_weighted": [("C_DoiDauHaiCuc", 10), ("C_ChienTranhLanh", 10)]
    },
    {
        "id": "E_CH3_ChayDuaVuTrang_KhongGian",
        "label": "Chạy đua vũ trang và Khoa học công nghệ",
        "aliases": "Chiến tranh lạnh|Chế tạo bom nguyên tử|Phóng vệ tinh nhân tạo|Chạy đua vũ trang",
        "where": "L_Global", "when": "P_1947_1989",
        "org_weighted": [("O_PheTBCN", 10), ("O_PheXHCN", 10)],
        "content": """+ Mỹ: Chế tạo thành công bom nguyên tử (1945), phóng vệ tinh nhân tạo (1958).
      + Liên Xô: Chế tạo thành công bom nguyên tử (1949), phóng vệ tinh nhân tạo (1957).""",
        "limitations": "Dồn nguồn lực khổng lồ cho quốc phòng, tạo nguy cơ bùng nổ chiến tranh hạt nhân hủy diệt toàn cầu.",
        "concepts_weighted": [("C_ChayDuaVuTrang", 10), ("C_ChienTranhLanh", 10)]
    },
    {
        "id": "E_CH3_HauQua_ChienTranhLanh",
        "label": "Hậu quả của Chiến tranh lạnh",
        "aliases": "Chiến tranh lạnh|Hậu quả Chiến tranh lạnh|Chấm dứt Chiến tranh lạnh",
        "where": "L_Global", "when": "P_1947_1989",
        "cause_deep": "Sự đối đầu căng thẳng kéo dài hơn 40 năm giữa hai siêu cường Mỹ và Liên Xô.",
        "content": "Thế giới luôn trong tình trạng căng thẳng; Chi phí quốc phòng tăng cao kìm hãm kinh tế; Gây ra các cuộc chiến tranh cục bộ đẫm máu (Đông Nam Á, Đông Bắc Á, Trung Đông).",
        "result": "Năm 1989, Chiến tranh lạnh chính thức chấm dứt. Thế giới chuyển dần sang xu thế hòa hoãn.",
        "concepts_weighted": [("C_ChienTranhCucBo", 10), ("C_ChienTranhLanh", 10)]
    },
    
    {
        "id": "E_CH3_LienXo_PhatTrien_1945_1975",
        "label": "Liên Xô xây dựng và phát triển CNXH (1945-1975)",
        "aliases": "Thành tựu của Liên Xô|Phóng vệ tinh nhân tạo|Tàu vũ trụ",
        "where": "L_LienXo", "when": "P_1950_1975",
        "org_weighted": [("O_DangCSLienXo", 10)],
        "context": "Từ 1946-1950, Liên Xô hoàn thành khôi phục kinh tế. Từ 1950-1975 tiến hành xây dựng cơ sở vật chất cho CNXH.",
        "achievements": """+ Kinh tế: Cường quốc công nghiệp thứ 2 thế giới (sau Mỹ).
        + Khoa học: Nước đầu tiên phóng vệ tinh nhân tạo (1957) và tàu vũ trụ có người lái (1961).
        + Xã hội: Xây dựng hệ thống phúc lợi, y tế, giáo dục phát triển cao.
        + Đối ngoại: Là trụ cột của phe XHCN, bảo vệ hòa bình thế giới.""",
        "concepts_weighted": [("C_DoiDauHaiCuc", 8)] # Nhắc lại khái niệm Đối đầu hai cực
    },
    {
        "id": "E_CH3_LienXo_CaiTo_1985",
        "label": "Công cuộc cải tổ của Goóc-ba-chốp (1985)",
        "aliases": "Cải tổ ở Liên Xô",
        "where": "L_LienXo", "when": "P_1985_1991",
        "who_weighted": [("Pe_Gorbachev", 10)],
        "cause": """+ Phát triển không đồng bộ (quá tập trung công nghiệp nặng).
        + Nông nghiệp thiếu hụt.
        + Giá dầu thế giới sụt giảm mạnh đẩy kinh tế vào khủng hoảng.""",
        "content": "Năm 1985, M. Goóc-ba-chốp thực hiện cải tổ toàn diện về kinh tế và chính trị.",
        "result": "Thiếu đồng bộ và hiệu quả, đẩy Liên Xô lún sâu vào khủng hoảng, rối loạn.",
        "concepts_weighted": [("C_CaiTo", 10), ("C_KhungHoangToanDien", 10)]
    },
    {
        "id": "E_CH3_LienXo_TanRa_1991",
        "label": "Sự tan rã của Liên bang Xô viết (1991)",
        "aliases": "Liên Xô sụp đổ|Chấm dứt chế độ XHCN ở Liên Xô|Cộng đồng SNG",
        "where": "L_LienXo", "when": "P_1985_1991",
        "who_weighted": [("Pe_Gorbachev", 10)],
        "org_weighted": [("O_DangCSLienXo", 10), ("O_SNG", 10)],
        "cause_direct": "Cuộc đảo chính lật đổ Goóc-ba-chốp (8/1991) thất bại gây hậu quả nghiêm trọng.",
        "content": """+ Đảng Cộng sản Liên Xô bị đình chỉ hoạt động.
        + Ngày 21/12/1991: Kí Hiệp định giải tán Liên bang, lập Cộng đồng SNG.
        + Ngày 25/12/1991: Goóc-ba-chốp từ chức Tổng thống.""",
        "result": "Chế độ XHCN chấm dứt tại Liên Xô.",
        "concepts_weighted": [("C_CheDoXHCNTansRa", 10)]
    },

    # ================= Tuyến 2: ĐÔNG ÂU =================
    {
        "id": "E_CH3_DongAu_PhatTrien_1945_1975",
        "label": "Đông Âu xây dựng CNXH (1945-1975)",
        "aliases": "Thành tựu của Đông Âu|Nhà nước dân chủ nhân dân",
        "where": "L_DongAu", "when": "P_1950_1975",
        "org_weighted": [("O_SEV", 9)], # Thuộc tổ chức SEV
        "context": "Từ 1944-1946, lập các nhà nước dân chủ nhân dân. Đông Đức lập nước năm 1949.",
        "achievements": """+ Kinh tế: Nông nghiệp cơ giới hóa; công nghiệp phát triển (đặc biệt là Tiệp Khắc, Đông Đức).
        + Xã hội: Xóa bỏ giai cấp bóc lột, y tế miễn phí, giáo dục phát triển.
        + Đối ngoại: Thuộc phe XHCN, thiết lập quan hệ chặt chẽ với Liên Xô.""",
        "result": "Đạt nhiều thành tựu lớn, tăng trưởng khá nhanh với sự giúp đỡ của Liên Xô (SEV)."
    },
    {
        "id": "E_CH3_DongAu_TanRa_1989",
        "label": "Sự sụp đổ của chế độ XHCN ở Đông Âu (1989)",
        "aliases": "Đông Âu sụp đổ",
        "where": "L_DongAu", "when": "P_1985_1991",
        "cause": "Tình hình chính trị phức tạp, khủng hoảng lây lan từ Liên Xô.",
        "content": "Ban lãnh đạo Đông Âu phải thực hiện đa nguyên chính trị, tổ chức tuyển cử tự do.",
        "result": "Các thế lực chống CNXH thắng cử, chế độ XHCN bị xóa bỏ ở Đông Âu.",
        "concepts_weighted": [("C_DaNguyenChinhTri", 10), ("C_CheDoXHCNTansRa", 10)]
    },
    
    # ==================================
    {
        "id": "E_CH3_KinhTeMy_HoangKim",
        "label": "Thời kì hoàng kim của kinh tế Mỹ (1945-1973)",
        "aliases": "Kinh tế Mỹ sau WWII",
        "where": "L_My", "when": "P_1945_1973",
        "cause": "Thu lợi nhuận từ chiến tranh, ít tổn thất, áp dụng KH-KT.",
        "content": "Nước Mỹ trở thành trung tâm kinh tế - tài chính duy nhất và lớn nhất thế giới.",
        "result": "Tạo tiềm lực để Mỹ triển khai Chiến lược toàn cầu.",
        "concepts_weighted": [("C_ChuNghiaTuBan", 10)]
    },
    {
        "id": "E_CH3_My_KetThucChienTranhLanh",
        "label": "Mỹ tuyên bố chấm dứt Chiến tranh lạnh (1989)",
        "aliases": "Gặp gỡ Malta",
        "where": "L_Global", "when": "P_1973_1991",
        "who_weighted": [("Pe_Gorbachev", 9)],
        "content": "Mỹ và Liên Xô cùng tuyên bố chấm dứt đối đầu, chuyển sang đối thoại.",
        "result": "Trật tự hai cực I-an-ta bắt đầu tan rã.",
        "concepts_weighted": [("C_ChienTranhLanh", 10)]
    },

    # ================= Tuyến: TÂY ÂU =================
    {
        "id": "E_CH3_TayAu_LienKetKhuVuc",
        "label": "Quá trình liên kết khu vực ở Tây Âu",
        "aliases": "Thành lập EEC|Liên kết châu Âu",
        "where": "L_TayAu", "when": "P_1950_1973",
        "org_weighted": [("O_EEC", 10), ("O_EU", 10)],
        "content": """+ 1951: Cộng đồng Than - Thép châu Âu.
        + 1957: Cộng đồng Kinh tế châu Âu (EEC).
        + 1991: Liên minh châu Âu (EU).""",
        "result": "Tây Âu trở thành một trong ba trung tâm kinh tế - tài chính của thế giới.",
        "concepts_weighted": [("C_NhatTheHoa", 10)]
    },
    {
        "id": "E_CH3_TayAu_QuanHeVoiMy",
        "label": "Sự thay đổi trong quan hệ Tây Âu - Mỹ",
        "aliases": "Lệ thuộc Mỹ|Thoát ly Mỹ",
        "where": "L_TayAu", "when": "P_1945_1991",
        "content": """+ 1945-1950: Liên minh chặt chẽ, lệ thuộc Mỹ (Kế hoạch Mác-san, NATO).
        + 1950-1973: Anh tiếp tục liên minh, Pháp tìm cách giảm lệ thuộc vào Mỹ.""",
        "result": "Khẳng định xu hướng đa cực trong thế giới tư bản."
    },
    
    {
        "id": "E_CH3_CachMangCuba_DienBien",
        "label": "Cách mạng Cu-ba (1952-1959)",
        "aliases": "Lá cờ đầu Mỹ La-tinh",
        "where": "L_Cuba", "when": "P_1952_1959",
        "who_weighted": [("Pe_FidelCastro", 10), ("Pe_Batista", 9)],
        "org_weighted": [("O_PhongTrao26_7", 10), ("O_CheDoBatista", 10)],
        "cause_direct": "3/1952, Ba-ti-xta thiết lập chế độ độc tài quân sự tay sai Mỹ.",
        "content": """+ 26/7/1953: Tấn công pháo đài Môn-ca-đa.
        + 11/1956: Đổ bộ tàu Gran-ma, lập căn cứ địa.
        + 1/1/1959: Giải phóng La Ha-ba-na, cách mạng thắng lợi.""",
        "result": "Lật đổ độc tài, xác lập chủ quyền dân tộc, cổ vũ 'Lục địa bùng cháy'.",
        "concepts_weighted": [("C_LucDiaBungChay", 9)]
    },
    {
        "id": "E_CH3_Cuba_XayDungCNXH",
        "label": "Thành tựu xây dựng Chủ nghĩa xã hội ở Cu-ba",
        "aliases": "Cu-ba sau 1961",
        "where": "L_Cuba", "when": "P_Tu1961",
        "achievements": """+ Kinh tế: Đa dạng hóa nông nghiệp, cơ giới hóa, phát triển công nghiệp chế tạo.
        + Xã hội: Giáo dục, y tế phát triển hàng đầu khu vực.""",
        "concepts_weighted": [("C_ChuNghiaXaHoi", 10)]
    },
    
    # ================= TUYẾN: NHẬT BẢN =================
    {
        "id": "E_CH3_NhatBan_CaiCach",
        "label": "Cải cách dân chủ ở Nhật Bản (1945-1952)",
        "where": "L_NhatBan", "when": "P_1945_1952",
        "org_weighted": [("O_SCAP", 10)],
        "content": "SCAP thủ tiêu chủ nghĩa quân phiệt, thiết lập dân chủ tư sản đại nghị, khôi phục kinh tế.",
    },
    {
        "id": "E_CH3_NhatBan_KinhTeThanKi",
        "label": "Sự phát triển kinh tế thần kì của Nhật Bản",
        "aliases": "Kinh tế Nhật Bản thập niên 60",
        "where": "L_NhatBan", "when": "P_1960s",
        "content": "Kinh tế tăng trưởng vượt Tây Âu, vươn lên thứ 2 thế giới. Đầu 1970s trở thành một trong 3 trung tâm kinh tế - tài chính toàn cầu.",
        "cause_deep": "Coi KH-CN là đòn bẩy, tập trung ứng dụng dân dụng (mua bằng sáng chế).",
        "concepts_weighted": [("C_PhatTrienThanKi", 10)]
    },

    # ================= TUYẾN: TRUNG QUỐC =================
    {
        "id": "E_CH3_TrungQuoc_LapQuoc",
        "label": "Sự ra đời của nước CHND Trung Hoa (1949)",
        "where": "L_TrungQuoc", "when": "P_1946_1949",
        "who_weighted": [("Pe_MaoTrachDong", 10)],
        "content": "Sau nội chiến (1946-1949), Đảng Cộng sản thắng lợi. Ngày 1/10/1949, nước CHND Trung Hoa ra đời.",
    },
    {
        "id": "E_CH3_TrungQuoc_KhungHoang",
        "label": "Giai đoạn đường lối sai lầm của Trung Quốc (1958-1976)",
        "aliases": "Đại nhảy vọt|Đại cách mạng văn hóa vô sản|Ba ngọn cờ hồng",
        "where": "L_TrungQuoc", "when": "P_1958_1976",
        "who_weighted": [("Pe_MaoTrachDong", 10)],
        "content": "Thực hiện 'Ba ngọn cờ hồng' và 'Cách mạng văn hóa' nhằm đẩy nhanh tiến lên CNXH và triệt tiêu tàn dư tư bản.",
        "limitations": "Gây thảm họa, đất nước bị tàn phá nặng nề, kinh tế đình đốn."
    },
    {
        "id": "E_CH3_TrungQuoc_CaiCachMoCua",
        "label": "Công cuộc Cải cách - Mở cửa ở Trung Quốc (Từ 1978)",
        "where": "L_TrungQuoc", "when": "P_1978_nay",
        "who_weighted": [("Pe_DangTieuBinh", 10)],
        "content": "Lấy phát triển kinh tế làm trọng tâm, xây dựng đất nước giàu mạnh.",
        "result": "Tình hình ổn định, kinh tế phát triển mạnh mẽ.",
        "concepts_weighted": [("C_CNXH_DacSacTrungQuoc", 10)]
    },

    # ================= TUYẾN: ẤN ĐỘ =================
    {
        "id": "E_CH3_AnDo_PhatTrien",
        "label": "Thành tựu xây dựng đất nước của Ấn Độ (1950-1991)",
        "where": "L_AnDo", "when": "P_1950_1991",
        "content": """+ Kinh tế: Cách mạng xanh (tự túc và xuất khẩu lương thực). CN nặng lọt top 10 thế giới.
        + KH-CN: Chế tạo bom nguyên tử (1974), phóng vệ tinh (1975).
        + Đối ngoại: Trung lập, hòa bình.""",
        "concepts_weighted": [("C_CachMangXanh", 10)]
    },

    # ================= TUYẾN: ASEAN =================
    {
        "id": "E_CH3_ASEAN_ThanhLap",
        "label": "Sự ra đời của ASEAN (1967)",
        "aliases": "Thành lập ASEAN",
        "where": "L_DongNamA", "when": "P_1960s",
        "org_weighted": [("O_ASEAN", 10)],
        "content": "Ngày 8/8/1967 tại Băng Cốc (Thái Lan), 5 nước (In-đô, Mã Lai, Phi, Xin, Thái) thành lập ASEAN.",
        "cause_direct": "Nhu cầu hợp tác phát triển kinh tế và hạn chế ảnh hưởng của các cường quốc bên ngoài."
    },
]

MOVEMENTS = [
    {
        "id": "M_CH3_MyLaTinh_ChongDocTai",
        "label": "Phong trào đấu tranh chống chế độ độc tài ở Mỹ La-tinh",
        "aliases": "Lục địa bùng cháy",
        "where": "L_MyLaTinh", "when": "P_1945_1991",
        "content": "Cuộc đấu tranh chống chế độ độc tài quân sự và sự can thiệp của Mỹ nổ ra mạnh mẽ sau 1959.",
        "achievements": "Lật đổ chính quyền độc tài ở nhiều nước, thành lập chính quyền dân chủ tiến bộ.",
        "concepts_weighted": [("C_LucDiaBungChay", 10), ("C_CheDoDocTaiQuanSu", 10)]
    }
]