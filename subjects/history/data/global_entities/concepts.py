
# Format: (id, label, aliases, freq, abstractness, bloom, confidence)
CONCEPTS = [
    ("C_KhungHoangKinhTe", "Khủng hoảng kinh tế", "Khủng hoảng thừa", 15, 4, 3, 3),
    ("C_ChuNghiaPhatXit", "Chủ nghĩa phát xít", "Phát xít", 18, 5, 3, 3),
    ("C_KinhTeThiTruong", "Kinh tế thị trường", "Tự do buôn bán", 10, 5, 3, 3),
    ("C_SuCanThiepCuaNhaNuoc", "Sự can thiệp của nhà nước", "Kinh tế vĩ mô", 8, 4, 3, 3),
    ("C_KhuynhHuongVoSan", "Khuynh hướng vô sản", "Cách mạng vô sản", 12, 5, 3, 3),
    ("C_KhuynhHuongTuSan", "Khuynh hướng tư sản", "Cách mạng tư sản", 10, 5, 3, 3),
    ("C_ChinhSachThoaHiep", "Chính sách thỏa hiệp nhượng bộ", "Dung túng phát xít", 8, 5, 3, 3),
    ("C_GiaiPhongDanToc", "Giải phóng dân tộc", "Độc lập dân tộc", 15, 5, 3, 3),
    ("C_HeThongVersaillesWashington", "Hệ thống Véc-xai - Oa-sinh-tơn", "", 12, 5, 3, 3),
    ("C_ChienTranhChinhNghia", "Chiến tranh chính nghĩa", "Chính nghĩa", 10, 5, 3, 3),
    ("C_ChienTranhPhiNghia", "Chiến tranh phi nghĩa", "Phi nghĩa", 10, 5, 3, 3),
    ("C_PhatXitHoa", "Quá trình phát xít hóa", "Chạy đua vũ trang", 15, 5, 3, 3),
    #chapter 2
    ("C_ChanHungNoiHoa", "Chấn hưng nội hóa, bài trừ ngoại hóa", "Bài trừ ngoại hóa", 8, 4, 3, 3),
    ("C_KhuynhHuongTuSan", "Khuynh hướng dân chủ tư sản", "Cách mạng dân chủ tư sản|Dân chủ tư sản", 15, 5, 3, 3),
    ("C_KhuynhHuongVoSan", "Khuynh hướng vô sản", "Cách mạng vô sản|Vô sản", 15, 5, 3, 3),
    ("C_BaoDongAmSat", "Bạo động, ám sát cá nhân", "Khủng bố cá nhân", 7, 4, 3, 3),
    ("C_BaiCong", "Bãi công", "Đình công|Lãn công|Phá hợp đồng", 10, 3, 3),
    
    ("C_ChuNghiaMacLenin", "Chủ nghĩa Mác-Lê-nin", "Mác-Lê-nin|Mác - Lênin", 15, 5, 3, 3),
    ("C_CachMangVoSan", "Cách mạng vô sản", "Con đường cách mạng vô sản", 15, 5, 3, 3),
    ("C_CachMangTuSanDanQuyen", "Tư sản dân quyền cách mạng", "Cách mạng tư sản dân quyền", 12, 5, 3, 3),
    ("C_ThoDiaCachMang", "Thổ địa cách mạng", "Cách mạng ruộng đất", 10, 5, 3, 3),
    
    ("C_LienMinhCongNong", "Liên minh công - nông", "Khối liên minh công-nông", 12, 4, 3, 3),
    ("C_DanSinhDanChu", "Dân sinh, dân chủ", "Tự do, dân sinh, dân chủ, cơm áo, hòa bình", 10, 4, 3, 3),
    ("C_DauTranhNghiTruong", "Đấu tranh nghị trường", "Nghị trường", 9, 4, 3, 3),
    ("C_DauTranhBaoChi", "Đấu tranh báo chí", "Lĩnh vực báo chí|Đấu tranh công khai", 9, 4, 3, 3),
    ("C_TapDuotCachMang", "Cuộc tập dượt cho Cách mạng", "Cuộc diễn tập|Bài học kinh nghiệm", 15, 5, 3, 3),
    
    ("C_KinhTeChiHuy", "Kinh tế chỉ huy", "Chính sách kinh tế chỉ huy", 8, 4, 3, 3),
    ("C_NanDoi1945", "Nạn đói năm 1945", "Nạn đói nghiêm trọng|Nhổ lúa trồng đay", 12, 3, 3),
    ("C_KhoiNghiaVuTrang", "Khởi nghĩa vũ trang", "Đấu tranh vũ trang", 15, 5, 3, 3),
    ("C_KhoiNghiaTungPhan", "Khởi nghĩa từng phần", "", 10, 5, 3, 3),
    ("C_TongKhoiNghia", "Tổng khởi nghĩa", "Tổng khởi nghĩa giành chính quyền", 15, 5, 3, 3),
    ("C_PhaKhoThoc", "Phá kho thóc, giải quyết nạn đói", "Phá kho thóc", 12, 4, 3, 3),
    
    ("C_ThoiCoCachMang", "Thời cơ cách mạng", "Thời cơ tổng khởi nghĩa", 15, 4, 3, 3),
    ("C_DocLapTuDo", "Kỷ nguyên độc lập, tự do", "Độc lập, tự do", 15, 5, 3, 3),
    ("C_DangCamQuyen", "Đảng cầm quyền", "Đảng lãnh đạo chính quyền", 12, 5, 3, 3),
    
    ("C_ChienTranhLanh", "Chiến tranh lạnh", "Tình trạng Chiến tranh lạnh", 20, 5, 3, 3),
    ("C_DoiDauHaiCuc", "Đối đầu hai cực", "Thế giới hai cực|Chia thành hai phe", 15, 5, 3, 3),
    ("C_ChayDuaVuTrang", "Chạy đua vũ trang", "Chạy đua vũ trang hạt nhân", 15, 4, 3, 3),
    ("C_ChienTranhCucBo", "Chiến tranh cục bộ", "Các cuộc chiến tranh cục bộ", 12, 4, 3, 3),
    
    ("C_CaiTo", "Công cuộc cải tổ", "Cải tổ toàn diện|Perestroika", 15, 4, 3, 3),
    ("C_DaNguyenChinhTri", "Đa nguyên chính trị", "Đa đảng", 10, 5, 3, 3),
    ("C_KhungHoangToanDien", "Khủng hoảng toàn diện", "Khủng hoảng kinh tế - xã hội", 15, 5, 3, 3),
    ("C_CheDoXHCNTansRa", "Chế độ XHCN sụp đổ", "Chế độ XHCN tan rã", 20, 5, 3, 3),
    
    ("C_ChienLuocToanCau", "Chiến lược toàn cầu", "Mưu đồ bá chủ thế giới", 18, 5, 3, 3),
    ("C_NhatTheHoa", "Nhất thể hóa châu Âu", "Liên kết khu vực", 15, 4, 3, 3),
    ("C_KhungHoangNangLuong", "Khủng hoảng năng lượng 1973", "Khủng hoảng dầu mỏ", 15, 4, 3, 3),
    ("C_ChuNghiaTuBan", "Chủ nghĩa Tư bản hiện đại", "CNTB", 20, 5, 3, 3),
    ("C_LucDiaBungChay", "Lục địa bùng cháy", "Phong trào GPDT Mỹ La-tinh", 18, 5, 3, 3),
    ("C_CheDoDocTaiQuanSu", "Chế độ độc tài quân sự", "Chủ nghĩa thực dân mới", 15, 5, 3, 3),
    
    ("C_PhatTrienThanKi", "Sự phát triển thần kì", "Phép màu kinh tế", 15, 4, 3, 3),
    ("C_CNXH_DacSacTrungQuoc", "CNXH đặc sắc Trung Quốc", "Chủ nghĩa xã hội mang màu sắc Trung Quốc", 15, 4, 3, 3),
    ("C_CachMangXanh", "Cách mạng xanh", "Cách mạng nông nghiệp Ấn Độ", 12, 4, 3, 3),
    
    ("C_NganCanTreoSoiToc", "Tình thế ngàn cân treo sợi tóc", "Muôn vàn khó khăn|Giặc đói, giặc dốt, giặc ngoại xâm", 20, 5, 3, 3),
    ("C_HoaDeTien", "Sách lược Hòa để tiến", "Nhân nhượng có nguyên tắc|Mềm dẻo ngoại giao", 18, 5, 3, 3),
    ("C_ChinhQuyenDanChu", "Chính quyền dân chủ nhân dân", "Chính quyền hợp pháp", 15, 4, 3, 3),
    
    ("C_DuongLoiKhangChien", "Đường lối kháng chiến chống Pháp", "Toàn dân, toàn diện, trường kì, tự lực cánh sinh", 20, 5, 3, 3),
    ("C_DanhNhanhThangNhanh", "Chiến lược Đánh nhanh thắng nhanh", "Đánh chớp nhoáng", 15, 4, 3, 3),
    ("C_DanhLauDai", "Chiến lược Đánh trường kì", "Đánh lâu dài", 15, 4, 3, 3),
    ("C_TheChuDong", "Thế chủ động trên chiến trường", "Chủ động tiến công", 18, 5, 3, 3),
    
    ("C_KhangChienToanDien", "Kháng chiến toàn diện", "Chính trị, kinh tế, văn hóa, giáo dục", 15, 4, 3, 3),
    ("C_DanhChacTienChac", "Đánh chắc, tiến chắc", "Phương châm tác chiến Điện Biên Phủ", 20, 5, 3, 3),
    ("C_PhanTanLucLuong", "Phân tán lực lượng địch", "Điều địch để đánh địch", 18, 5, 3, 3),
    
    ("C_HauPhuongTienTuyen", "Quan hệ Hậu phương - Tiền tuyến", "Miền Bắc chi viện miền Nam", 20, 5, 3, 3),
    ("C_BaoLucCachMang", "Bạo lực cách mạng", "Đấu tranh chính trị kết hợp vũ trang", 18, 5, 3, 3),
    ("C_ChienTranhDacBiet", "Chiến tranh đặc biệt", "Dùng người Việt đánh người Việt", 18, 5, 3, 3),
    ("C_ApChienLuoc", "Ấp chiến lược", "Quốc sách bình định của Mỹ", 15, 4, 3, 3),
    
    ("C_ChienTranhCucBo", "Chiến lược Chiến tranh cục bộ", "Tiến hành bằng quân Mỹ là chủ yếu", 20, 5, 3, 3),
    ("C_VietNamHoaChienTranh", "Chiến lược Việt Nam hóa chiến tranh", "Tiến hành bằng quân Sài Gòn là chủ yếu", 20, 5, 3, 3),
    ("C_DienBienPhuTrenKhong", "Điện Biên Phủ trên không", "Đánh bại B-52", 18, 5, 3, 3),
    ("C_TongTienCong", "Tổng tiến công và nổi dậy", "Tiến công quân sự kết hợp nổi dậy của quần chúng", 20, 5, 3, 3),
    
    ("C_ThongNhatNhaNuoc", "Thống nhất đất nước về mặt Nhà nước", "Thống nhất Nhà nước", 15, 5, 3, 3),
    ("C_BaoCap", "Cơ chế tập trung quan liêu, bao cấp", "Kinh tế chỉ huy|Bao cấp", 18, 5, 3, 3),
    ("C_DoiMoiKinhTe", "Kinh tế hàng hóa nhiều thành phần", "Kinh tế thị trường định hướng XHCN", 20, 5, 3, 3),
    ("C_BaChuongTrinhKinhTe", "Ba chương trình kinh tế lớn", "Lương thực thực phẩm, Hàng tiêu dùng, Hàng xuất khẩu", 18, 5, 3, 3),
    ("C_KinhTeThiTruong_XHCN", "Kinh tế hàng hóa nhiều thành phần", "Cơ chế thị trường có sự quản lí của Nhà nước", 20, 5, 3, 3),
    ("C_KhungHoangDongAu", "Khủng hoảng ở Liên Xô và Đông Âu", "Khủng hoảng XHCN", 15, 4, 3, 3),
    
    ("C_TratTuDonCuc", "Trật tự thế giới đơn cực", "Mỹ là siêu cường duy nhất", 20, 5, 3, 3),
    ("C_TratTuDaCuc", "Trật tự thế giới đa cực", "Nhiều trung tâm cạnh tranh quyền lực", 20, 5, 3, 3),
    ("C_VanhDaiConDuong", "Chiến lược Vành đai, Con đường", "Hệ thống kinh tế lấy Trung Quốc làm trung tâm", 15, 4, 3, 3),
]