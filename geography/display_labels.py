"""
Display labels with proper Vietnamese diacritics for the verification form.
Maps ontology ID -> display label (with diacritics) for teacher readability.
"""

DISPLAY_LABELS = {
    # Regions
    'R_VietNam': 'Việt Nam',
    'R_TDMNBB': 'Trung du và miền núi Bắc Bộ',
    'R_DBSH': 'Đồng bằng sông Hồng',
    'R_BTB': 'Bắc Trung Bộ',
    'R_DHNTB': 'Duyên hải Nam Trung Bộ',
    'R_TN': 'Tây Nguyên',
    'R_DNB': 'Đông Nam Bộ',
    'R_DBSCL': 'Đồng bằng sông Cửu Long',
    'R_DongBac': 'Đông Bắc (thuộc TDMNBB)',
    'R_TayBac': 'Tây Bắc (thuộc TDMNBB)',
    'R_HaNoi': 'Hà Nội',
    'R_HCM': 'TP Hồ Chí Minh',
    'R_HaiPhong': 'Hải Phòng',
    'R_DaNang': 'Đà Nẵng',
    'R_CanTho': 'Cần Thơ',
    'R_BienDong': 'Biển Đông',
    'R_DongNamA': 'Đông Nam Á',
    'R_VinhBacBo': 'Vịnh Bắc Bộ',
    'R_QuanDaoHoangSa': 'Quần đảo Hoàng Sa',
    'R_QuanDaoTruongSa': 'Quần đảo Trường Sa',
    'R_PhuQuoc': 'Phú Quốc',

    # Natural features
    'NF_HoangLienSon': 'Dãy Hoàng Liên Sơn',
    'NF_Phansipan': 'Phan-xi-păng',
    'NF_TruongSon': 'Dãy Trường Sơn',
    'NF_TaySonNguyen': 'Cao nguyên Tây Nguyên',
    'NF_DBSH_Plain': 'Đồng bằng Bắc Bộ',
    'NF_DBSCL_Plain': 'Đồng bằng Nam Bộ',
    'NF_SongHong': 'Sông Hồng',
    'NF_SongMekong': 'Sông Mê Kông (sông Cửu Long)',
    'NF_SongDongNai': 'Sông Đồng Nai',
    'NF_SongDa': 'Sông Đà',
    'NF_BienDong_NF': 'Biển Đông (vị trí)',
    'NF_BacHaiDuong': 'Bờ biển Việt Nam',
    'NF_KhiHauNhietDoi': 'Khí hậu nhiệt đới ẩm gió mùa',

    # Phenomena
    'PH_GioMua': 'Gió mùa',
    'PH_Bao': 'Bão',
    'PH_Lu': 'Lũ, lũ quét',
    'PH_HanHan': 'Hạn hán',
    'PH_XamNhapMan': 'Xâm nhập mặn',
    'PH_BienDoiKhiHau': 'Biến đổi khí hậu',
    'PH_MatDatCanhTac': 'Mất đất canh tác',
    'PH_OnhiemMoiTruong': 'Ô nhiễm môi trường',
    'PH_ChuyenDichCoCauKT': 'Chuyển dịch cơ cấu kinh tế',
    'PH_DoThiHoa': 'Đô thị hóa',

    # Resources
    'RE_Than': 'Than đá',
    'RE_DauKhi': 'Dầu mỏ và khí đốt',
    'RE_Boxit': 'Bô-xít',
    'RE_Sat': 'Quặng sắt',
    'RE_Apatit': 'A-pa-tít',
    'RE_DatBazan': 'Đất badan',
    'RE_DatPhuSa': 'Đất phù sa',
    'RE_RungNhietDoi': 'Rừng nhiệt đới',
    'RE_RungNganMan': 'Rừng ngập mặn',
    'RE_ThuySanBien': 'Thủy sản biển',
    'RE_ThuySanNuocNgot': 'Thủy sản nước ngọt',
    'RE_TiemNangThuyDien': 'Tiềm năng thủy điện',
    'RE_TiemNangDuLich': 'Tiềm năng du lịch',

    # Industries
    'I_NongNghiep': 'Nông nghiệp',
    'I_TrongTrot': 'Trồng trọt',
    'I_ChanNuoi': 'Chăn nuôi',
    'I_LamNghiep': 'Lâm nghiệp',
    'I_ThuySan': 'Thủy sản',
    'I_CongNghiep': 'Công nghiệp',
    'I_CN_KhaiThac': 'Công nghiệp khai thác',
    'I_CN_CheBien_LTTP': 'Chế biến lương thực-thực phẩm',
    'I_CN_DetMay': 'Dệt may',
    'I_CN_CoKhi': 'Cơ khí - điện tử',
    'I_CN_HoaChat': 'Hóa chất, vật liệu xây dựng',
    'I_DichVu': 'Dịch vụ',
    'I_GiaoThong': 'Giao thông vận tải',
    'I_BuuChinh': 'Bưu chính viễn thông',
    'I_DuLich': 'Du lịch',
    'I_ThuongMai': 'Thương mại (nội thương, ngoại thương)',

    # Crops
    'CR_Lua': 'Cây lúa',
    'CR_NgoKhoai': 'Cây ngô, khoai',
    'CR_CaPhe': 'Cà phê',
    'CR_CaoSu': 'Cao su',
    'CR_Che': 'Chè',
    'CR_Dieu': 'Điều',
    'CR_HoTieu': 'Hồ tiêu',
    'CR_CayAnQua': 'Cây ăn quả nhiệt đới',
    'CR_CayCongNghiep_NgayNgan': 'Cây công nghiệp ngắn ngày (lạc, mía, đậu tương)',

    # Livestock
    'LV_TrauBo': 'Trâu, bò',
    'LV_Lon': 'Lợn',
    'LV_GiaCam': 'Gia cầm (gà, vịt)',

    # Demographic
    'DM_MatDoDanSo': 'Mật độ dân số',
    'DM_TangTruongDanSo': 'Tăng trưởng dân số',
    'DM_CoCauDanSoTheoTuoi': 'Cơ cấu dân số theo tuổi',
    'DM_CoCauDanToc': 'Cơ cấu dân tộc (54 dân tộc)',
    'DM_ChatLuongCuocSong': 'Chất lượng cuộc sống',
    'DM_PhanBoDanCu': 'Phân bố dân cư',
    'DM_LaoDongVaViecLam': 'Lao động và việc làm',

    # Concepts
    'C_VT_DiaLyVN': 'Vị trí địa lý Việt Nam',
    'C_LanhTho': 'Lãnh thổ Việt Nam',
    'C_KinhDoVoiDo': 'Kinh độ - vĩ độ',
    'C_BanDo': 'Bản đồ và hệ thống ký hiệu',
    'C_GDP': 'Tổng sản phẩm trong nước (GDP)',
    'C_GDP_BinhQuan': 'GDP bình quân đầu người',
    'C_NenKinhTeNhieuThanhPhan': 'Nền kinh tế nhiều thành phần',
    'C_CNHDH': 'Công nghiệp hóa - hiện đại hóa',
    'C_ChuyenDichCoCauLaoDong': 'Chuyển dịch cơ cấu lao động',
    'C_HoiNhapKinhTeQT': 'Hội nhập kinh tế quốc tế',
    'C_PTBenVung': 'Phát triển bền vững',

    # Processes
    'PR_CongNghiepHoa': 'Quá trình CNH-HĐH',
    'PR_DoThiHoa': 'Quá trình đô thị hóa',
    'PR_ChuyenDichCoCauKT': 'Chuyển dịch cơ cấu kinh tế',
    'PR_HoiNhapASEAN': 'Hội nhập ASEAN của Việt Nam',
    'PR_HoiNhapQT': 'Hội nhập quốc tế, gia nhập WTO',
}
