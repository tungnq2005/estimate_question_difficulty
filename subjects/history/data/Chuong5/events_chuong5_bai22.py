# data/Chuong5/events_chuong5_bai22.py
# Bài 22: Châu Á từ năm 1991 đến nay

DOCUMENTS = [
    {
        "id": "D_CH5_HienChuongASEAN",
        "label": "Hiến chương ASEAN (11/2007)",
        "aliases": "Hiến chương ASEAN",
        "where": "L_DongNamA", "when": "P_Tu2001",
        "org_weighted": [("O_ASEAN", 10)],
        "content": "Văn kiện pháp lý đầu tiên xác lập tư cách pháp nhân cho ASEAN, quy định nguyên tắc, mục tiêu và bộ máy tổ chức hoạt động.",
        "result": "Tạo cơ sở pháp lý và thể chế quan trọng để xây dựng Cộng đồng ASEAN (thành lập năm 2015).",
    },
]

EVENTS = [
    # Tuyến 1: Đông Á - Trung Quốc
    {
        "id": "E_CH5_TrungQuoc_TroiDay",
        "label": "Trung Quốc trỗi dậy mạnh mẽ (từ 1991 đến nay)",
        "aliases": "Sự trỗi dậy của Trung Quốc",
        "where": "L_TrungQuoc", "when": "P_Tu2001",
        "who_weighted": [("Pe_DangTieuBinh", 6), ("Pe_TapCanBinh", 8)],
        "org_weighted": [("O_DangCongSan_TQ", 10)],
        "cause_direct": "Tiếp tục đường lối cải cách mở cửa từ năm 1978, thu hút mạnh đầu tư nước ngoài, đẩy mạnh xuất khẩu và ứng dụng khoa học - công nghệ.",
        "content": "Kinh tế Trung Quốc tăng trưởng liên tục với tốc độ cao nhất thế giới trong giai đoạn 1980-2010, gia nhập WTO (2001); đầu thế kỷ XXI kinh tế Trung Quốc xếp thứ 6 thế giới, đến năm 2010 vượt Nhật Bản trở thành nền kinh tế lớn thứ hai thế giới. Từ năm 2010, Trung Quốc bắt đầu điều chỉnh mô hình tăng trưởng, chuyển dần từ dựa vào xuất khẩu - chế tạo sang thúc đẩy tiêu dùng nội địa. Trung Quốc triển khai Sáng kiến Vành đai - Con đường (BRI) nhằm mở rộng ảnh hưởng kinh tế - chính trị toàn cầu.",
        "achievements": "Trở thành một trong những trung tâm quyền lực chính của xu hướng thế giới đa cực đầu thế kỷ XXI.",
        "concepts_weighted": [("C_CNXH_DacSacTrungQuoc", 10), ("C_VanhDaiConDuong", 10), ("C_TratTuDaCuc", 6)]
    },
    {
        "id": "E_CH5_TrungQuoc_ThuHoiHongKongMaCao",
        "label": "Trung Quốc thu hồi Hồng Kông (1997) và Ma Cao (1999)",
        "aliases": "Hồng Kông trở về Trung Quốc|Ma Cao trở về Trung Quốc",
        "where": "L_HongKong", "when": "P_1991_2000",
        "cause_direct": "Kết quả đàm phán ngoại giao giữa Trung Quốc với Anh (Tuyên bố chung Trung - Anh 1984) và Bồ Đào Nha, chấm dứt chế độ thuộc địa/nhượng địa kéo dài hơn một thế kỷ.",
        "content": "Anh trao trả Hồng Kông (7/1997), Bồ Đào Nha trao trả Ma Cao (12/1999) cho Trung Quốc, áp dụng mô hình 'một quốc gia, hai chế độ'.",
        "result": "Trung Quốc hoàn thành thu hồi các vùng lãnh thổ bị chiếm đóng từ thời cận đại, nâng cao vị thế và sự toàn vẹn lãnh thổ quốc gia.",
    },
    # Tuyến 2: Đông Bắc Á phát triển
    {
        "id": "E_CH5_NhatBanHanQuoc_PhatTrien",
        "label": "Nhật Bản, Hàn Quốc và các nền kinh tế công nghiệp mới phục hồi và phát triển",
        "aliases": "Các con rồng châu Á",
        "where": "L_Asia", "when": "P_Tu2001",
        "content": "Nhật Bản phục hồi sau giai đoạn suy thoái cuối thế kỷ XX, từ đầu những năm 2000 tiếp tục là một trung tâm tài chính hàng đầu thế giới; Hàn Quốc phục hồi mạnh mẽ sau khủng hoảng tài chính châu Á 1997. Cùng với Xin-ga-po, Đài Loan, Hồng Kông ('4 con rồng châu Á'), các nền kinh tế này tiếp tục đi đầu về công nghệ và công nghiệp chế tạo.",
        "concepts_weighted": [("C_PhatTrienThanKi", 8)]
    },
    {
        "id": "E_CH5_DongA_ThachThucXaHoi",
        "label": "Thách thức xã hội ở các nền kinh tế Đông Á",
        "aliases": "Già hóa dân số Nhật Bản|Thất nghiệp thanh niên Hàn Quốc|Phân hóa giàu nghèo Trung Quốc",
        "where": "L_Asia", "when": "P_Tu2001",
        "content": "Bên cạnh thành tựu kinh tế, các nước Đông Bắc Á đối mặt nhiều thách thức xã hội: Trung Quốc với tình trạng phân hóa giàu - nghèo gia tăng, Nhật Bản với tình trạng già hóa dân số nghiêm trọng, Hàn Quốc với khó khăn việc làm cho thanh niên; nạn tham nhũng vẫn là vấn đề nan giải ở cả Trung Quốc và Hàn Quốc.",
        "limitations": "Các thách thức này đặt ra yêu cầu cải cách xã hội song song với duy trì tăng trưởng kinh tế.",
    },
    # Tuyến 3: Đông Nam Á
    {
        "id": "E_CH5_ChauA_KhungHoangTaiChinh1997",
        "label": "Khủng hoảng tài chính - tiền tệ châu Á (1997)",
        "aliases": "Khủng hoảng tài chính châu Á 1997",
        "where": "L_DongNamA", "when": "P_1991_2000",
        "cause_direct": "Bắt nguồn từ Thái Lan (thả nổi đồng baht, 7/1997) do dòng vốn đầu cơ ngắn hạn rút ồ ạt, lan nhanh sang Hàn Quốc, Indonesia, Malaysia, Philippines và nhiều nền kinh tế Đông Á khác.",
        "content": "Đồng tiền mất giá mạnh, thị trường chứng khoán sụp đổ, nhiều doanh nghiệp phá sản, tăng trưởng kinh tế khu vực sụt giảm nghiêm trọng.",
        "result": "Bộc lộ những rủi ro của mô hình tăng trưởng dựa vào vốn vay ngắn hạn nước ngoài, thúc đẩy cải cách hệ thống tài chính - ngân hàng ở nhiều nước châu Á.",
        "concepts_weighted": [("C_KhungHoangTaiChinhChauA", 10)]
    },
    {
        "id": "E_CH5_DongNamA_DanChuHoa",
        "label": "Chuyển đổi chính trị theo hướng dân chủ hóa ở Đông Nam Á",
        "aliases": "Cách mạng Indonesia 1998|Phong trào dân chủ Philippines|Phong trào dân chủ Thái Lan|Cải cách Myanmar",
        "where": "L_DongNamA", "when": "P_1991_2000",
        "content": "Nhiều quốc gia Đông Nam Á chuyển đổi từ chế độ độc tài sang chế độ dân chủ, tiêu biểu là Indonesia sau cuộc cách mạng năm 1998 (Tổng thống Xu-hác-tô từ chức). Các phong trào dân chủ, đòi cải cách chính trị diễn ra mạnh mẽ ở Philippines và Thái Lan. Myanmar có một số bước tiến cải cách chính trị nhưng vẫn còn nhiều thách thức.",
        "result": "Vai trò của các tổ chức xã hội dân sự ngày càng được đề cao trong việc thúc đẩy dân chủ hóa khu vực.",
        "concepts_weighted": [("C_DanChuHoa", 10)]
    },
    {
        "id": "E_CH5_DongNamA_ASEAN_MoRong",
        "label": "Đông Nam Á và ASEAN mở rộng, xây dựng Cộng đồng ASEAN",
        "aliases": "ASEAN mở rộng thành ASEAN 10",
        "where": "L_DongNamA", "when": "P_1991_2000",
        "org_weighted": [("O_ASEAN", 10)],
        "content": "Sau khi kết nạp Việt Nam (1995), Lào và Myanmar (1997), Campuchia (1999), ASEAN hoàn thành mục tiêu trở thành tổ chức khu vực gồm 10 quốc gia Đông Nam Á. Năm 2015, Cộng đồng ASEAN chính thức được thành lập trên 3 trụ cột chính trị - an ninh, kinh tế, văn hóa - xã hội.",
        "achievements": "Đông Nam Á chuyển từ đối đầu sang hợp tác, trở thành khu vực phát triển năng động, có vai trò ngày càng lớn trong cấu trúc khu vực châu Á - Thái Bình Dương.",
        "concepts_weighted": [("C_HoiNhapQuocTe", 8)]
    },
    # Tuyến 4: Nam Á
    {
        "id": "E_CH5_AnDo_PhatTrien",
        "label": "Ấn Độ cải cách kinh tế và vươn lên thành cường quốc",
        "where": "L_AnDo", "when": "P_1991_2000",
        "cause_direct": "Cải cách kinh tế theo hướng tự do hóa, mở cửa thị trường từ năm 1991.",
        "content": "Ấn Độ phát triển theo hướng khác Trung Quốc: tập trung chủ yếu vào dịch vụ và công nghệ thông tin thay vì chế tạo - xuất khẩu, nên tốc độ tăng trưởng nhìn chung thấp hơn Trung Quốc trong cùng giai đoạn. Ấn Độ đẩy mạnh phát triển công nghệ thông tin, đồng thời thúc đẩy đầu tư hạ tầng và tiếp tục cải cách kinh tế, trở thành một trong những nền kinh tế lớn và tăng trưởng nhanh nhất thế giới.",
        "concepts_weighted": [("C_KinhTeTriThuc", 8)]
    },
]

PREREQUISITES = [
    ("E_CH5_ChauA_KhungHoangTaiChinh1997", "E_CH5_DongNamA_ASEAN_MoRong"),
    ("E_CH5_ChauA_KhungHoangTaiChinh1997", "E_CH5_NhatBanHanQuoc_PhatTrien"),
    ("D_CH5_HienChuongASEAN", "E_CH5_DongNamA_ASEAN_MoRong"),
    ("E_CH5_TrungQuoc_ThuHoiHongKongMaCao", "E_CH5_TrungQuoc_TroiDay"),
    ("E_CH5_DongNamA_DanChuHoa", "E_CH5_DongNamA_ASEAN_MoRong"),
    ("E_CH5_TrungQuoc_TroiDay", "E_CH5_DongA_ThachThucXaHoi"),
    ("E_CH5_NhatBanHanQuoc_PhatTrien", "E_CH5_DongA_ThachThucXaHoi"),
]

SIMILARITIES = [
    ("E_CH5_TrungQuoc_TroiDay", "E_CH5_DaCuc_HinhThanh"),
    ("E_CH5_NhatBanHanQuoc_PhatTrien", "E_CH5_AnDo_PhatTrien"),
    ("E_CH5_DongNamA_DanChuHoa", "E_CH5_DongNamA_ASEAN_MoRong"),
]

CONTRASTS = [
    ("E_CH5_TrungQuoc_TroiDay", "E_CH5_DongNamA_ASEAN_MoRong"),
    ("E_CH5_ChauA_KhungHoangTaiChinh1997", "E_CH5_TrungQuoc_TroiDay"),
    ("E_CH5_TrungQuoc_TroiDay", "E_CH5_DongA_ThachThucXaHoi"),
]
