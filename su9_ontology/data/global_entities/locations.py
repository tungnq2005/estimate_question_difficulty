# Format: (id, label, aliases, located_in, abstractness, confidence)
LOCATIONS = [
    # Cấp châu lục / Khu vực / Thế giới
    ("L_Global", "Thế giới", "Toàn cầu|Quốc tế", None, 4, 3),
    ("L_Europe", "Châu Âu", "Europe", None, 3, 3),
    ("L_Asia", "Châu Á", "Asia", None, 3, 3),
    ("L_BacPhi", "Bắc Phi", "North Africa", None, 2, 3),
    ("L_DongNamA", "Đông Nam Á", "Southeast Asia", "L_Asia", 2, 3),
    ("L_DongDuong", "Đông Dương", "Bán đảo Đông Dương", "L_Asia", 3, 3),

    # Cấp Quốc gia
    ("L_LienXo", "Liên Xô", "USSR|Liên bang Xô viết", None, 2, 3),
    ("L_Nga", "Nước Nga Xô viết", "Nga", "L_LienXo", 1, 3),
    ("L_My", "Mỹ", "Hoa Kỳ|USA", None, 1, 3),
    ("L_Duc", "Đức", "Germany", "L_Europe", 1, 3),
    ("L_Italia", "I-ta-li-a", "Ý", "L_Europe", 1, 3),
    ("L_NhatBan", "Nhật Bản", "Japan", "L_Asia", 1, 3),
    ("L_TrungQuoc", "Trung Quốc", "Nước Cộng hoà Nhân dân Trung Hoa|PRC|China", "L_Asia", 1, 3),
    ("L_AnDo", "Ấn Độ", "India", "L_Asia", 1, 3),
    ("L_VietNam", "Việt Nam", "", "L_DongNamA", 1, 3),
    ("L_Indonesia", "In-đô-nê-xi-a", "", "L_DongNamA", 1, 3),
    ("L_BaLan", "Ba Lan", "Poland", "L_Europe", 1, 3),
    ("L_Phap", "Pháp", "France|Nước Pháp", "L_Europe", 1, 3), # Đã gộp
    ("L_Anh", "Anh", "UK", "L_Europe", 1, 3),

    # Cấp Vùng miền Việt Nam
    ("L_BacKy", "Bắc Kỳ", "Bắc Kì", "L_VietNam", 2, 3),
    ("L_TrungKy", "Trung Kỳ", "Trung Kì", "L_VietNam", 2, 3),
    ("L_NamKy", "Nam Kỳ", "Nam Kì", "L_VietNam", 2, 3),
    ("L_VietBac", "Khu giải phóng Việt Bắc", "Căn cứ địa Việt Bắc|Cao-Bắc-Lạng", "L_BacKy", 2, 3),
    ("L_NgheTinh", "Nghệ An - Hà Tĩnh", "Nghệ Tĩnh|Nghệ An và Hà Tĩnh", "L_TrungKy", 1, 3),

    # Cấp Thành phố / Tỉnh / Địa danh chiến lược
    ("L_Moscow", "Mát-xcơ-va", "Moscow", "L_LienXo", 1, 3),
    ("L_Stalingrad", "Xta-lin-grát", "Stalingrad", "L_LienXo", 1, 3),
    ("L_Leningrad", "Lê-nin-grát", "Leningrad", "L_LienXo", 1, 3),
    ("L_PearlHarbor", "Trân Châu Cảng", "Hawaii", "L_My", 1, 3),
    ("L_Washington", "Oa-sinh-tơn", "Washington", "L_My", 1, 3),
    ("L_Normandy", "Noóc-măng-đi", "Normandy", "L_Phap", 1, 3),
    ("L_Berlin", "Béc-lin", "Berlin", "L_Duc", 1, 3),
    ("L_Hiroshima_Nagasaki", "Hi-rô-si-ma & Na-ga-xa-ki", "", "L_NhatBan", 1, 3),
    ("L_BacKinh", "Bắc Kinh", "Beijing", "L_TrungQuoc", 1, 3),
    ("L_ManChau", "Mãn Châu", "Đông Bắc Trung Quốc", "L_TrungQuoc", 1, 3),
    ("L_Versailles", "Véc-xai", "Hội nghị Véc-xai", "L_Phap", 1, 3),
    ("L_Tours", "Tua", "Đại hội Tua", "L_Phap", 1, 3),
    ("L_HongKong", "Hương Cảng", "Hương Cảng (Trung Quốc)|Trung Quốc", "L_Asia", 1, 3),
    
    # Địa danh Việt Nam chi tiết
    ("L_SaiGon", "Sài Gòn", "Cảng Sài Gòn|Ba Son", "L_NamKy", 1, 3),
    ("L_HaNoi", "Hà Nội", "Xưởng A-vi-a|Nhà máy rượu Hà Nội", "L_VietNam", 1, 3),
    ("L_NamDinh", "Nam Định", "Nhà máy dệt Nam Định", "L_VietNam", 1, 3),
    ("L_QuangNinh", "Quảng Ninh", "Mỏ than Cẩm Phả", "L_VietNam", 1, 3),
    ("L_BinhPhuoc", "Bình Phước", "Phú Riềng", "L_NamKy", 1, 3),
    ("L_YenBai", "Yên Bái", "", "L_VietNam", 1, 3), # Đã xóa trùng
    ("L_VinhBenThuy", "Vinh - Bến Thủy", "Vinh-Bến Thuỷ|Trường Thi", "L_NgheTinh", 1, 3),
    ("L_LangSon", "Lạng Sơn", "Bắc Sơn", "L_VietNam", 1, 3),
    ("L_DoLuong", "Đô Lương (Nghệ An)", "Đô Lương", "L_NgheTinh", 1, 3),
    ("L_HocMon", "Bà Điểm (Hóc Môn)", "Bà Điểm|Gia Định", "L_SaiGon", 1, 3), # Đã sửa ID thành L_HocMon
    ("L_CaoBang", "Cao Bằng", "Pác Bó|Phay Khắt|Nà Ngần", "L_VietNam", 1, 3),
    ("L_TuyenQuang", "Tuyên Quang", "Tân Trào", "L_VietNam", 1, 3),
    ("L_ThaiNguyen", "Thái Nguyên", "Thị xã Thái Nguyên", "L_BacKy", 1, 3),
    ("L_Hue", "Huế", "Cố đô Huế", "L_TrungKy", 1, 3),
    ("L_BaDinh", "Quảng trường Ba Đình", "Ba Đình", "L_HaNoi", 1, 3),
    
    ("L_DongAu", "Đông Âu", "Các nước Đông Âu", "L_Europe", 2, 3),
    ("L_TayAu", "Tây Âu", "Các nước Tây Âu|16 nước Tây Âu", "L_Europe", 2, 3),
    
    ("L_DongDuc", "Đông Đức", "Cộng hoà Dân chủ Đức", "L_DongAu", 1, 3),
    ("L_TiepKhac", "Tiệp Khắc", "", "L_DongAu", 1, 3),
    
    ("L_MyLaTinh", "Mỹ La-tinh", "Khu vực Mỹ La-tinh|Lục địa bùng cháy", "L_Global", 3, 3),
    ("L_Cuba", "Cu-ba", "Cộng hòa Cu-ba|Cuba", "L_MyLaTinh", 1, 3),
    
    ("L_AnDo", "Ấn Độ", "Cộng hòa Ấn Độ|India", "L_Asia", 1, 3),
    ("L_DongNamA", "Đông Nam Á", "Khu vực Đông Nam Á|SEA", "L_Asia", 2, 3),
    ("L_Pakistan", "Pa-ki-xtan", "Pakistan", "L_Asia", 1, 3),
    
    ("L_ViTuyen16_Bac", "Từ vĩ tuyến 16 trở ra Bắc", "Miền Bắc|Bắc vĩ tuyến 16", "L_VietNam", 1, 3),
    ("L_ViTuyen16_Nam", "Từ vĩ tuyến 16 trở vào Nam", "Miền Nam|Nam vĩ tuyến 16|Nam Bộ", "L_VietNam", 1, 3),
    ("L_SaiGonChoLon", "Sài Gòn - Chợ Lớn", "Sài Gòn", "L_ViTuyen16_Nam", 1, 3),
    
    ("L_VietBac", "Căn cứ địa Việt Bắc", "Chiến khu Việt Bắc|Thủ đô kháng chiến", "L_ViTuyen16_Bac", 2, 3),
    ("L_DuongSo4", "Đường số 4", "Hệ thống phòng ngự Đường số 4", "L_ViTuyen16_Bac", 1, 3),
    ("L_DongKhe", "Đông Khê", "Cứ điểm Đông Khê", "L_DuongSo4", 1, 3),
    
    ("L_DienBienPhu", "Điện Biên Phủ", "Tập đoàn cứ điểm Điện Biên Phủ|Lòng chảo Điện Biên", "L_ViTuyen16_Bac", 1, 3),
    ("L_Geneva", "Giơ-ne-vơ (Thụy Sĩ)", "Geneva", "L_Global", 1, 3),
    ("L_ViTuyen17", "Vĩ tuyến 17", "Sông Bến Hải", "L_VietNam", 1, 3),
    
    ("L_MienBac", "Miền Bắc Việt Nam", "Miền Bắc|Bắc vĩ tuyến 17", "L_VietNam", 1, 3),
    ("L_MienNam", "Miền Nam Việt Nam", "Miền Nam|Nam vĩ tuyến 17", "L_VietNam", 1, 3),
    ("L_BenTre", "Bến Tre", "Tỉnh Bến Tre|Xứ Dừa", "L_MienNam", 1, 3),
    ("L_TruongSon", "Đường Trường Sơn", "Tuyến đường Hồ Chí Minh", "L_VietNam", 2, 3),
    
    ("L_VanTuong", "Vạn Tường (Quảng Ngãi)", "Vạn Tường", "L_MienNam", 1, 3),
    ("L_TayNguyen", "Tây Nguyên", "Địa bàn Tây Nguyên", "L_MienNam", 2, 3),
    ("L_HueDaNang", "Huế - Đà Nẵng", "Trị - Thiên", "L_MienNam", 2, 3),
    ("L_SaiGon", "Sài Gòn (Gia Định)", "Dinh Độc Lập", "L_MienNam", 1, 3),
    ("L_HaNoiHaiPhong", "Hà Nội, Hải Phòng", "Bầu trời Hà Nội", "L_MienBac", 2, 3),
    
    ("L_BienGioiTayNam", "Biên giới Tây Nam", "Tây Nam Bộ", "L_VietNam", 1, 3),
    ("L_BienGioiPhiaBac", "Biên giới phía Bắc", "Các tỉnh phía Bắc", "L_VietNam", 1, 3),
    ("L_TruongSa", "Quần đảo Trường Sa", "Đảo Gạc Ma|Trường Sa", "L_VietNam", 1, 3),
    
    ("L_Nga", "Liên bang Nga", "Nga|Russia", "L_Global", 1, 3),
    ("L_TrungDong", "Khu vực Trung Đông", "Afghanistan và Iraq", "L_Global", 2, 3),
]