"""
Part 3: Prerequisite/causal/similarity edges + Turtle emitter.
Cấu trúc mạng lưới Đồ thị tri thức cho Chương 1 (1918 - 1945).
"""

# ======================================================================
# PREREQUISITES: Chuỗi logic sư phạm "Muốn hiểu Y phải biết X trước"
# ======================================================================

PREREQUISITES = [
    # Chuỗi cách mạng và khủng hoảng thế giới
    ("M_CachMang_ChauAu_1918_1923", "E_ThanhLapQuocTeCongSan"),
    ("M_CachMang_ChauAu_1918_1923", "D_NEP_1921"),
    ("E_KhungHoangKinhTe_1929_1933", "D_NewDeal_1932"),
    ("E_KhungHoangKinhTe_1929_1933", "E_PhatXitHoa_ChauAu_1929_1933"),
    ("E_KhungHoangKinhTe_1929_1933", "E_NhatBan_PhatXitHoa_1933_1945"),
    
    # Chuỗi tiến trình Chiến tranh thế giới thứ 2
    ("E_PhatXitHoa_ChauAu_1929_1933", "E_WWII_NguyenNhan_TongQuat"),
    ("E_NhatBan_PhatXitHoa_1933_1945", "E_WWII_NguyenNhan_TongQuat"),
    ("E_WWII_NguyenNhan_TongQuat", "E_WWII_GiaiDoan1_1939_1941"),
    ("E_WWII_GiaiDoan1_1939_1941", "D_TuyenNgonLienHopQuoc_1942"),
    ("D_TuyenNgonLienHopQuoc_1942", "E_WWII_GiaiDoan2_1942_1945"),
    ("E_WWII_GiaiDoan2_1942_1945", "E_WWII_HauQua_YNGhia"),
    
    # Chuỗi giải phóng dân tộc
    ("M_NguTu_1919", "M_GiaiPhongDanToc_DongNamA_1918_1945"),
    ("E_WWII_GiaiDoan2_1942_1945", "E_GiaiPhong_DongNamA_1945"),
    
    ("O_NamDongThuXa", "E_CH2_ThanhLapVNQDD"),
    ("O_HoiPhucViet", "E_CH2_ThanhLapTanViet"),
    ("M_CH2_CongNhan_1919_1925", "M_CH2_CongNhan_1925_1930"),
    
    ("E_CH2_DaiHoiTours_1920", "C_ChuNghiaMacLenin"), # Đại hội Tua là tiền đề đến với Mác-Lênin
    ("D_CH2_DuongKachMenh", "E_CH2_BaToChucCongSan_1929"), # Lý luận chuẩn bị cho thực tiễn
    ("E_CH2_BaToChucCongSan_1929", "E_CH2_HoiNghiThanhLapDang_1930"), # 3 tổ chức là tiền đề lập Đảng
    
    ("M_CH2_PhongTrao_1930_1931", "E_CH2_XoVietNgheTinh"), # Xô viết là đỉnh cao của phong trào 30-31
    ("O_QuocTeCongSan", "E_CH2_HoiNghiTW_7_1936"), # Đại hội 7 QTCS định hướng cho Đảng CSVN
    ("E_CH2_HoiNghiTW_7_1936", "M_CH2_PhongTraoDanChu_1936_1939"), # Nghị quyết TW định hướng phong trào
    ("M_CH2_PhongTrao_1930_1931", "C_TapDuotCachMang"), # Cuộc tập dượt thứ nhất
    ("M_CH2_PhongTraoDanChu_1936_1939", "C_TapDuotCachMang"),
    
    ("E_CH2_HoiNghiTW_11_1939", "E_CH2_HoiNghiTW_8_1941"), # Định hướng từ 1939 được hoàn chỉnh năm 1941
    ("E_CH2_HoiNghiTW_8_1941", "E_CH2_ThanhLapVietMinh_1941"),
    ("E_CH2_ThanhLapVNTTGPQ_1944", "E_CH2_HoiNghiQuanSuBacKi"), # Có VNTTGPQ rồi mới thống nhất thành VN Giải phóng quân
    ("E_CH2_NhatDaoChinhPhap_1945", "D_CH2_ChiThiNhatPhapBanNhau"), # Sự kiện lịch sử -> Ra chỉ thị
    ("D_CH2_ChiThiNhatPhapBanNhau", "M_CH2_CaoTraoKhangNhat"), # Chỉ thị -> Phát động cao trào
    
    ("D_CH3_HocThuyetTruman", "D_CH3_KeHoachMarshall"), # Có học thuyết mới có kế hoạch kinh tế
    ("D_CH3_KeHoachMarshall", "E_CH3_DoiDauKinhTe_ChinhTri"),
    ("D_CH3_BaoCaoZhdanov", "E_CH3_DoiDauKinhTe_ChinhTri"),
    
    ("E_CH3_LienXo_CaiTo_1985", "E_CH3_LienXo_TanRa_1991"), # Cải tổ thất bại là tiền đề dẫn đến tan rã
    ("E_CH3_LienXo_CaiTo_1985", "E_CH3_DongAu_TanRa_1989"),
    
    ("D_CH3_KeHoachMarshall", "E_CH3_TayAu_QuanHeVoiMy"), # Viện trợ dẫn đến lệ thuộc
    ("E_CH3_KinhTeMy_HoangKim", "D_CH3_ChienLuocToanCau"), # Giàu có dẫn đến tham nhũng bá chủ
    ("C_KhungHoangNangLuong", "P_1973_1991"),
    
    ("O_EEC", "O_EU"),
    ("E_CH3_CachMangCuba_DienBien", "M_CH3_MyLaTinh_ChongDocTai"), # Thắng lợi Cu-ba kéo theo phong trào khu vực
    ("O_CheDoBatista", "E_CH3_CachMangCuba_DienBien"),           # Có áp bức có đấu tranh
    ("O_PhongTrao26_7", "E_CH3_CachMangCuba_DienBien"),
    
    ("D_CH3_HiepUocAnNinhMyNhat", "E_CH3_NhatBan_KinhTeThanKi"), # Có an ninh mới rảnh tay làm kinh tế
    ("D_CH3_KeHoachMountbatten", "L_Pakistan"), # Kế hoạch đẻ ra quốc gia
    ("E_CH3_ASEAN_ThanhLap", "D_CH3_HiepUocBali"),
    
    ("E_CH4_TongTuyenCu", "O_QuocHoiKhoa1"), # Phải bầu cử mới ra Quốc hội
    ("O_QuocHoiKhoa1", "D_CH4_HienPhap1946"), # Quốc hội mới đẻ ra Hiến pháp
    ("D_CH4_HiepUocHoaPhap", "D_CH4_HiepDinhSoBo"), # Pháp bắt tay Tưởng -> Ta phải ký Sơ bộ với Pháp
    ("D_CH4_HiepDinhSoBo", "D_CH4_TamUoc14_9"),
    
    ("E_CH4_ChienDauDoThi", "L_VietBac"), # Giam chân địch để rút lên Việt Bắc
    ("E_CH4_VietBac1947", "C_DanhLauDai"), # Thắng Việt Bắc buộc Pháp phải chuyển sang đánh lâu dài
    ("D_CH4_KeHoachRevers", "E_CH4_BienGioi1950"), # Kế hoạch của Pháp là nguyên nhân ta mở chiến dịch Biên giới
    ("E_CH4_BienGioi1950", "C_TheChuDong"),
    
    ("D_CH4_KeHoachNavarre", "E_CH4_DongXuan_53_54"), # Na-va ra đời thì ta mới mở Đông-Xuân để phá
    ("E_CH4_DongXuan_53_54", "E_CH4_DienBienPhu"), # Đông Xuân thành công, điều được địch thì mới đánh Điện Biên Phủ
    ("E_CH4_DienBienPhu", "D_CH4_HiepDinhGeneva"),
    
    ("D_CH5_Luat1059", "D_CH5_NghiQuyet15"), # Địch tàn bạo -> Ta phải ra Nghị quyết
    ("D_CH5_NghiQuyet15", "M_CH5_DongKhoi"), # Có đường lối -> Mới bùng nổ Đồng khởi
    ("M_CH5_DongKhoi", "O_MTDTGPMNVN"), # Thắng lợi Đồng khởi -> Đẻ ra Mặt trận (20/12/1960)
    ("M_CH5_DongKhoi", "C_ChienTranhDacBiet"), # Ta thắng Đồng khởi -> Mỹ cay cú đẻ ra Chiến tranh Đặc biệt
    ("E_CH5_ApBac", "E_CH5_BinhGia"),
    
    ("E_CH5_MauThan1968", "P_1969_1973"), # Đánh Mậu Thân -> Mỹ thất bại Cục bộ -> Phải chuyển sang VN hóa
    
    # Khối Hiệp định Paris:
    ("E_CH5_DienBienPhuTrenKhong", "D_CH5_HiepDinhParis1973"), # Đập nát B52 -> Buộc ký Hiệp định
    ("D_CH5_HiepDinhParis1973", "E_CH5_PhuocLong1975"), # Mỹ cút -> Ngụy suy yếu -> Ta thử lửa ở Phước Long
    
    # Khối Đại thắng Mùa Xuân (Sắp xếp thứ tự thời gian, MCQs rất hay hỏi):
    ("E_CH5_PhuocLong1975", "E_CH5_ChienDichTayNguyen"),
    ("E_CH5_ChienDichTayNguyen", "L_HueDaNang"),
    ("L_HueDaNang", "E_CH5_ChienDichHoChiMinh"),
    ("E_CH6_KhungHoangKinhTe", "D_CH6_DaiHoiDang6"), # Bị khủng hoảng nên BẮT BUỘC phải Đổi mới
    ("C_ThongNhatNhaNuoc", "E_CH6_KhungHoangKinhTe"),
    ("C_KhungHoangDongAu", "D_CH6_DaiHoiDang6_ChiTiet"), 
    ("D_CH6_DaiHoiDang6_ChiTiet", "E_CH6_ThucHienDoiMoi_86_91"),
    ("C_BaChuongTrinhKinhTe", "E_CH6_ThucHienDoiMoi_86_91"),
    
    ("E_CH5_KhungBo11_9", "L_TrungDong"), # 11/9 là nguyên nhân Mỹ đánh Trung Đông
    ("E_CH5_KhungHoangTaiChinh2008", "E_CH5_DaCuc_HinhThanh"),
]

# ======================================================================
# CAUSAL EDGES: Cạnh Nhân quả (Trực tiếp & Sâu xa)
# ======================================================================

CAUSES_DIRECT = [
    ("E_KhungHoangKinhTe_1929_1933", "D_NewDeal_1932"),
    ("E_KhungHoangKinhTe_1929_1933", "E_PhatXitHoa_ChauAu_1929_1933"),
    ("E_KhungHoangKinhTe_1929_1933", "E_NhatBan_PhatXitHoa_1933_1945"),
    ("C_ChinhSachThoaHiep", "E_WWII_GiaiDoan1_1939_1941"),
    ("D_TuyenNgonLienHopQuoc_1942", "E_WWII_GiaiDoan2_1942_1945"),
    
    ("O_HVNCMTN", "E_CH2_ThanhLapTanViet"), # HVNCMTN ảnh hưởng làm Tân Việt chuyển hướng vô sản
    ("E_CH2_ThanhLapVNQDD", "C_BaoDongAmSat"),
    
    ("O_QuocTeCongSan", "E_CH2_HoiNghiThanhLapDang_1930"),
    
    ("E_CH2_PhapNhatBocLot", "C_NanDoi1945"),
    ("M_CH2_CaoTraoKhangNhat", "C_TapDuotCachMang"),
    
    ("D_CH3_HocThuyetTruman", "C_ChienTranhLanh"),
    ("C_DaNguyenChinhTri", "E_CH3_DongAu_TanRa_1989"),
]

CAUSES_DEEP = [
    ("C_HeThongVersaillesWashington", "E_WWII_NguyenNhan_TongQuat"),
    ("C_KhungHoangKinhTe", "E_WWII_NguyenNhan_TongQuat"),
    ("E_ThanhLapQuocTeCongSan", "M_GiaiPhongDanToc_DongNamA_1918_1945"),
    ("C_KhungHoangKinhTe", "M_CH2_PhongTrao_1930_1931"),
]

# ======================================================================
# SIMILARITY & CONTRAST (Dùng cho dạng câu hỏi So sánh / Tính Jaccard)
# ======================================================================

SIMILARITIES = [
    # Hai chính sách cùng bản chất nhà nước can thiệp để cứu vãn kinh tế
    ("D_NEP_1921", "D_NewDeal_1932"),
    
    # Quá trình phát xít hóa ở 2 châu lục
    ("E_PhatXitHoa_ChauAu_1929_1933", "E_NhatBan_PhatXitHoa_1933_1945"),
    
    # Hai khuynh hướng cứu nước ở châu Á
    ("C_KhuynhHuongVoSan", "C_KhuynhHuongTuSan"),
    ("E_CH3_LienXo_TanRa_1991", "E_CH3_DongAu_TanRa_1989"),
]

CONTRASTS = [
    ("O_LienHopQuoc_WW2", "O_PhePhatXit"),
    ("C_ChienTranhChinhNghia", "C_ChienTranhPhiNghia"),
    
    ("E_CH2_ThanhLapVNQDD", "E_CH2_ThanhLapTanViet"),
    
    ("O_PheTBCN", "O_PheXHCN"),
    ("D_CH3_KeHoachMarshall", "O_SEV"), # Kinh tế đối đầu
    ("O_NATO", "O_Warsaw"),             # Quân sự đối đầu
    ("Pe_Truman", "Pe_Zhdanov"),
    ("O_NATO", "O_Warsaw"), # Bài 9 & 11 liên kết
    ("O_DangDanChu_My", "O_DangCongHoa_My"),
    ("L_My", "O_EU"),
    
    ("Pe_FidelCastro", "Pe_Batista"),
    ("O_PhongTrao26_7", "O_CheDoBatista"),
    ("L_My", "L_Cuba"),
    
    ("E_CH3_TrungQuoc_KhungHoang", "E_CH3_TrungQuoc_CaiCachMoCua"), # Đường lối tàn phá VS Đường lối phục hồi
    ("Pe_MaoTrachDong", "Pe_DangTieuBinh"),
    
    ("O_THDQ", "L_ViTuyen16_Nam"), 
    ("O_QuanAnh", "L_ViTuyen16_Bac"),
    
    # Mục đích ngoại giao
    ("D_CH4_HiepDinhSoBo", "O_THDQ"),
    ("C_DanhNhanhThangNhanh", "C_DanhLauDai"), 
    ("E_CH4_VietBac1947", "E_CH4_BienGioi1950"),
    
    ("D_CH4_KeHoachNavarre", "C_PhanTanLucLuong"), 
    ("C_DanhNhanhThangNhanh", "C_DanhChacTienChac"),
    
    ("L_MienBac", "L_MienNam"),
    
    ("C_ChienTranhCucBo", "C_VietNamHoaChienTranh"),
    ("O_QuanMy", "O_QuanSaiGon"),
    ("E_CH5_MauThan1968", "E_CH5_TienCong1972"),
    
    ("C_BaoCap", "C_DoiMoiKinhTe"), 
    ("E_CH5_ChienDichHoChiMinh", "C_ThongNhatNhaNuoc"),
    ("D_CH6_DaiHoiDang6_ChiTiet", "C_BaoCap"),
    
    ("C_TratTuDonCuc", "C_TratTuDaCuc"),
    ("P_1991_2000", "C_TratTuDaCuc"),
    ("L_Nga", "O_NATO"),
]

# ======================================================================
# PERSON PARTICIPATION (Trích xuất nhanh để kết nối Đồ thị)
# Chú ý: Ở kiến trúc V3, bạn có thể loop qua field "who_weighted" để 
# tự động sinh ra mảng này, hoặc khai báo tĩnh ở đây để dễ kiểm soát.
# ======================================================================

PARTICIPATES = [
    ("Pe_Lenin", "D_NEP_1921", "leads"),
    ("Pe_Lenin", "E_ThanhLapQuocTeCongSan", "leads"),
    ("Pe_Roosevelt", "D_NewDeal_1932", "leads"),
    ("Pe_Hitler", "E_PhatXitHoa_ChauAu_1929_1933", "leads"),
    ("Pe_Hitler", "E_WWII_NguyenNhan_TongQuat", "leads"),
    ("Pe_Mussolini", "E_PhatXitHoa_ChauAu_1929_1933", "leads"),
    ("Pe_Gandhi", "M_DauTranh_AnDo_Interwar", "leads"),
    ("Pe_Sukarno", "E_GiaiPhong_DongNamA_1945", "leads"),
]

# ======================================================================
# INVOLVED CONCEPTS (Khái niệm liên quan)
# Tương tự PARTICIPATES, có thể sinh tự động từ "concepts_weighted"
# ======================================================================

INVOLVED_CONCEPTS = [
    ("D_NEP_1921", "C_KinhTeThiTruong"),
    ("D_NewDeal_1932", "C_SuCanThiepCuaNhaNuoc"),
    ("D_NewDeal_1932", "C_KhungHoangKinhTe"),
    ("E_KhungHoangKinhTe_1929_1933", "C_KhungHoangKinhTe"),
    ("E_PhatXitHoa_ChauAu_1929_1933", "C_ChuNghiaPhatXit"),
    ("E_NhatBan_PhatXitHoa_1933_1945", "C_PhatXitHoa"),
    ("E_WWII_GiaiDoan1_1939_1941", "C_ChinhSachThoaHiep"),
    ("E_WWII_HauQua_YNGhia", "C_ChienTranhChinhNghia"),
    ("M_CachMang_ChauAu_1918_1923", "C_KhuynhHuongVoSan"),
    ("M_GiaiPhongDanToc_DongNamA_1918_1945", "C_GiaiPhongDanToc"),
    ("O_QuanPhietNhat", "C_ChuNghiaPhatXit"),
    ("O_PhePhatXit", "C_ChuNghiaPhatXit"),
    
    ("E_CH2_ThanhLapVNQDD", "C_KhuynhHuongTuSan"),
    ("E_CH2_ThanhLapTanViet", "C_KhuynhHuongVoSan"),
    ("M_CH2_CongNhan_1925_1930", "C_BaiCong"),
    
    ("D_CH2_CuongLinhChinhTri_1930", "C_CachMangTuSanDanQuyen"),
    ("D_CH2_CuongLinhChinhTri_1930", "C_CachMangVoSan"),
    ("E_CH2_HoiNghiThanhLapDang_1930", "C_CachMangVoSan"),
    
    ("E_CH2_XoVietNgheTinh", "C_LienMinhCongNong"),
    ("E_CH2_HoiNghiTW_7_1936", "C_DanSinhDanChu"),
    
    ("E_CH2_HoiNghiTW_8_1941", "C_KhoiNghiaVuTrang"),
    ("D_CH2_ChiThiNhatPhapBanNhau", "C_KhoiNghiaTungPhan"),
    ("M_CH2_CaoTraoKhangNhat", "C_PhaKhoThoc"),
    
    ("E_CH3_DoiDauKinhTe_ChinhTri", "C_DoiDauHaiCuc"),
    ("E_CH3_HauQua_ChienTranhLanh", "C_ChienTranhCucBo"),
    ("E_CH3_LienXo_CaiTo_1985", "C_KhungHoangToanDien"),
    ("E_CH3_LienXo_TanRa_1991", "C_CheDoXHCNTansRa"),
    ("E_CH3_DongAu_TanRa_1989", "C_CheDoXHCNTansRa"),
    
    ("E_CH3_KinhTeMy_HoangKim", "C_ChuNghiaTuBan"),
    ("E_CH3_TayAu_LienKetKhuVuc", "C_NhatTheHoa"),
    
    ("O_THDQ", "C_NganCanTreoSoiToc"),
    ("O_ThucDanPhap", "C_NganCanTreoSoiToc"),
    ("E_CH4_DietGiacDoi", "C_NganCanTreoSoiToc"),
    ("E_CH4_DietGiacDot", "C_NganCanTreoSoiToc"),
    ("E_CH4_GiaiQuyetTaiChinh", "C_NganCanTreoSoiToc"),
    ("E_CH4_VietBac1947", "C_DanhNhanhThangNhanh"), # Liên kết để chỉ ra sự phá sản của chiến lược này
    ("D_CH4_LoiKeuGoiTQKC", "C_DuongLoiKhangChien"),
    ("D_CH4_KhangChienNhatDinhThangLoi", "C_DuongLoiKhangChien"),
    ("E_CH4_DienBienPhu", "D_CH4_KeHoachNavarre"),
    
    ("C_ApChienLuoc", "C_ChienTranhDacBiet"),
    
    ("C_ChienTranhCucBo", "O_QuanMy"),
    ("C_VietNamHoaChienTranh", "O_QuanSaiGon"),
    ("E_CH6_KhungHoangKinhTe", "C_BaoCap"),
    
    ("L_TrungQuoc", "C_VanhDaiConDuong"),
]

print(f"  + {len(PREREQUISITES)} prereq, {len(CAUSES_DIRECT)} direct-cause, "
      f"{len(CAUSES_DEEP)} deep-cause, {len(SIMILARITIES)} similar, "
      f"{len(CONTRASTS)} contrast, {len(PARTICIPATES)} participation, "
      f"{len(INVOLVED_CONCEPTS)} involved-concept")