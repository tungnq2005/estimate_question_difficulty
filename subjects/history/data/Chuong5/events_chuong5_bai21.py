# data/Chuong5/events_chuong5_bai21.py
# Bài 21: Liên bang Nga và nước Mỹ từ năm 1991 đến nay

DOCUMENTS = [
    {
        "id": "D_CH5_HienPhapNga1993",
        "label": "Hiến pháp Liên bang Nga (12/1993)",
        "aliases": "Hiến pháp Nga 1993",
        "where": "L_Nga", "when": "P_1991_2000",
        "who_weighted": [("Pe_Yeltsin", 8)],
        "cause_direct": "Xung đột gay gắt giữa Tổng thống En-xin và Xô-viết tối cao (Duma) về mô hình thể chế sau khi Liên Xô tan rã, đỉnh điểm là khủng hoảng Hiến pháp tháng 10/1993.",
        "content": "Xác lập mô hình cộng hòa Tổng thống Liên bang, trao quyền lực lớn cho Tổng thống; đặt nền móng thể chế chính trị của nước Nga hậu Xô viết.",
        "result": "Chấm dứt giai đoạn tranh giành quyền lực đầu thập niên 1990, ổn định khung thể chế nhà nước Nga.",
    },
]

EVENTS = [
    # Tuyến 1: Nước Nga
    {
        "id": "E_CH5_LienBangNga_ThanhLap",
        "label": "Sự thành lập Liên bang Nga (12/1991)",
        "aliases": "Liên bang Nga ra đời",
        "where": "L_Nga", "when": "P_1991_2000",
        "who_weighted": [("Pe_Yeltsin", 10)],
        "cause_direct": "Liên Xô tan rã (12/1991); Liên bang Nga kế thừa địa vị pháp lý của Liên Xô tại Liên hợp quốc (kể cả ghế Ủy viên thường trực Hội đồng Bảo an) và trên trường quốc tế.",
        "content": "B. En-xin làm Tổng thống đầu tiên. Nước Nga tiến hành cải cách theo hướng thị trường tự do ('liệu pháp sốc'), tư nhân hóa nhanh tài sản nhà nước.",
        "result": "Kinh tế suy thoái nghiêm trọng, lạm phát phi mã đầu thập niên 1990, một bộ phận lớn tài sản quốc gia rơi vào tay giới tài phiệt mới nổi (oligarch).",
        "concepts_weighted": [("C_KinhTeThiTruong", 8)]
    },
    {
        "id": "E_CH5_Nga_KhungHoangChinhTri1990s",
        "label": "Khủng hoảng chính trị - xã hội ở Nga thập niên 1990",
        "aliases": "Khủng hoảng nước Nga thời En-xin|Chiến tranh Chechnya",
        "where": "L_Nga", "when": "P_1991_2000",
        "who_weighted": [("Pe_Yeltsin", 8)],
        "cause_deep": "Cải cách kinh tế - chính trị quá nhanh và thiếu đồng bộ sau khi Liên Xô tan rã, quyền lực trung ương suy yếu.",
        "content": "Xung đột Hiến pháp giữa Tổng thống và Quốc hội (10/1993); phong trào li khai và chiến tranh Chechnya lần thứ nhất (1994-1996) đe dọa sự toàn vẹn lãnh thổ. Kinh tế tăng trưởng âm trong suốt giai đoạn 1991-1996.",
        "result": "Vị thế cường quốc của Nga suy giảm mạnh so với thời Liên Xô, uy tín quốc tế xuống thấp. Từ năm 1997, kinh tế Nga đã bắt đầu có dấu hiệu phục hồi dù còn mong manh (trước khi tiếp tục bị ảnh hưởng bởi khủng hoảng tài chính 1998).",
    },
    {
        "id": "E_CH5_Nga_Putin_PhucHoi",
        "label": "Nước Nga phục hồi dưới thời V. Pu-tin (từ năm 2000)",
        "aliases": "Nước Nga thời Putin",
        "where": "L_Nga", "when": "P_Tu2001",
        "who_weighted": [("Pe_Putin", 10)],
        "cause_direct": "V. Pu-tin lên nắm quyền, thực hiện các biện pháp chấn chỉnh kinh tế - chính trị, tăng cường vai trò nhà nước, tận dụng giá dầu mỏ - khí đốt tăng cao, tiếp nối đà phục hồi manh nha từ năm 1997.",
        "content": "Kinh tế Nga phục hồi rõ rệt và tăng trưởng ổn định (GDP tăng khoảng 10% năm 2000), ngân sách nhà nước được củng cố, kiểm soát giới tài phiệt, vị thế quốc tế dần được khôi phục. Tăng trưởng những năm sau đó không đều, phụ thuộc nhiều vào xuất khẩu nguyên liệu và nhiên liệu (dầu mỏ, khí đốt).",
        "achievements": "Khôi phục vị thế cường quốc, là một cực quan trọng trong xu hướng đa cực đầu thế kỷ XXI.",
        "concepts_weighted": [("C_TratTuDaCuc", 6)]
    },
    {
        "id": "E_CH5_QuanHeNgaMy_NATO",
        "label": "Quan hệ Nga - Mỹ/NATO: từ hợp tác đến căng thẳng",
        "aliases": "NATO Đông tiến|Quan hệ Nga-phương Tây",
        "where": "L_Nga", "when": "P_Tu2001",
        "org_weighted": [("O_NATO", 8)],
        "cause_direct": "NATO liên tục mở rộng về phía Đông, kết nạp nhiều nước Đông Âu và Liên Xô cũ, bị Nga coi là đe dọa trực tiếp không gian an ninh chiến lược.",
        "content": "Quan hệ Nga - phương Tây chuyển từ hợp tác thận trọng đầu thập niên 1990 sang cạnh tranh, đối đầu gay gắt, đặc biệt từ khủng hoảng Ukraine (2014).",
        "result": "Góp phần định hình lại cục diện an ninh châu Âu và xu hướng đa cực hóa quan hệ quốc tế.",
        "concepts_weighted": [("C_TratTuDaCuc", 6)]
    },
    # Tuyến 2: Nước Mỹ
    {
        "id": "E_CH5_My_SieuCuongThapNien90",
        "label": "Nước Mỹ - siêu cường duy nhất và 'nền kinh tế mới' (thập niên 1990)",
        "where": "L_My", "when": "P_1991_2000",
        "org_weighted": [("O_DangDanChu_My", 5)],
        "content": "Sau khi Liên Xô tan rã, Mỹ trở thành siêu cường duy nhất, có ưu thế vượt trội về kinh tế, quân sự, khoa học - công nghệ. Kinh tế Mỹ tăng trưởng mạnh nhờ bùng nổ công nghệ thông tin và Internet ('nền kinh tế mới').",
        "result": "Mỹ theo đuổi tham vọng thiết lập trật tự thế giới đơn cực, chi phối quan hệ quốc tế.",
        "concepts_weighted": [("C_TratTuDonCuc", 10), ("C_ChienLuocToanCau", 6)]
    },
    {
        "id": "E_CH5_My_SuyThoaiChuKy",
        "label": "Các đợt suy thoái kinh tế theo chu kỳ của Mỹ (2000 đến nay)",
        "aliases": "Bong bóng dot-com|Đại suy thoái 2008-2009|Suy thoái COVID-19",
        "where": "L_My", "when": "P_Tu2001",
        "content": "Kinh tế Mỹ trải qua nhiều đợt suy thoái theo chu kỳ: bong bóng công nghệ 'dot-com' vỡ (2000-2003), khủng hoảng tài chính toàn cầu (2008-2009), và suy thoái do đại dịch COVID-19 (từ 2020).",
        "result": "Sau mỗi đợt suy thoái, kinh tế Mỹ đều phục hồi và tiếp tục duy trì vị trí nền kinh tế lớn nhất thế giới.",
    },
    {
        "id": "E_CH5_My_CongNgheCao_DanDau",
        "label": "Mỹ duy trì vị trí dẫn đầu về công nghệ cao",
        "aliases": "Công nghệ thông tin Mỹ|Hàng không vũ trụ Mỹ|Dược phẩm Mỹ|Xe điện Tesla",
        "where": "L_My", "when": "P_Tu2001",
        "content": "Mỹ tiếp tục giữ vị trí hàng đầu thế giới ở nhiều lĩnh vực công nghệ cao: hàng không vũ trụ, dược phẩm, công nghệ thông tin, và các ngành công nghệ mới như xe điện (tiêu biểu là hãng Tesla).",
        "achievements": "Củng cố sức mạnh kinh tế - công nghệ, là nền tảng duy trì vai trò cường quốc hàng đầu của Mỹ trong bối cảnh cạnh tranh với Trung Quốc.",
        "concepts_weighted": [("C_KinhTeTriThuc", 8), ("C_CachMangKHKT_HienDai", 6)]
    },
    {
        "id": "E_CH5_My_CanThiepQuanSu",
        "label": "Chính sách can thiệp quân sự của Mỹ sau Chiến tranh lạnh",
        "aliases": "Chiến tranh Vùng Vịnh|Chiến tranh Afghanistan|Chiến tranh Iraq",
        "where": "L_TrungDong", "when": "P_Tu2001",
        "org_weighted": [("L_My", 10)],
        "cause_direct": "Mỹ lấy danh nghĩa chống khủng bố và bảo vệ lợi ích chiến lược để can thiệp quân sự vào nhiều khu vực: Chiến tranh Vùng Vịnh (1991) đẩy lùi I-rắc khỏi Cô-oét; sau sự kiện 11/9/2001, phát động chiến tranh tại Afghanistan (2001) và Iraq (2003).",
        "content": "Các cuộc chiến tranh kéo dài, tốn kém, gây nhiều tranh cãi về tính chính danh, làm suy giảm sức mạnh kinh tế - quân sự và uy tín quốc tế của Mỹ.",
        "result": "Góp phần thúc đẩy xu hướng đa cực hóa quan hệ quốc tế, Mỹ dần phải chia sẻ vai trò lãnh đạo thế giới với các trung tâm quyền lực khác.",
        "concepts_weighted": [("C_ChienLuocToanCau", 8)]
    },
]

PREREQUISITES = [
    ("E_CH5_LienBangNga_ThanhLap", "E_CH5_Nga_KhungHoangChinhTri1990s"),
    ("E_CH5_Nga_KhungHoangChinhTri1990s", "E_CH5_Nga_Putin_PhucHoi"),
    ("E_CH5_Nga_Putin_PhucHoi", "E_CH5_QuanHeNgaMy_NATO"),
    ("D_CH5_HienPhapNga1993", "E_CH5_Nga_Putin_PhucHoi"),
]

SIMILARITIES = [
    ("E_CH5_Nga_Putin_PhucHoi", "E_CH5_DaCuc_HinhThanh"),
    ("E_CH5_QuanHeNgaMy_NATO", "E_CH5_DaCuc_HinhThanh"),
]

CONTRASTS = [
    ("E_CH5_LienBangNga_ThanhLap", "E_CH5_My_SieuCuongThapNien90"),
    ("E_CH5_My_SieuCuongThapNien90", "E_CH5_My_CanThiepQuanSu"),
    ("E_CH5_Nga_KhungHoangChinhTri1990s", "E_CH5_Nga_Putin_PhucHoi"),
    ("E_CH5_My_SuyThoaiChuKy", "E_CH5_My_CongNgheCao_DanDau"),
]

CAUSES_DIRECT = [
    ("E_CH5_My_CanThiepQuanSu", "E_CH5_QuanHeNgaMy_NATO"),
]

PREREQUISITES += [
    ("E_CH5_My_SieuCuongThapNien90", "E_CH5_My_SuyThoaiChuKy"),
    ("E_CH5_My_SuyThoaiChuKy", "E_CH5_My_CongNgheCao_DanDau"),
]
