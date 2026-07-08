"""
Part 3: Prerequisite/causal/similarity edges + Turtle emitter.
This is the PAPER-CRITICAL part: the graph structure that feeds prerequisite_depth,
semantic_distance, and centrality features.
"""

# ======================================================================
# PREREQUISITES: "To understand X, you should already know Y" => Y prerequisiteOf X
# Curated by hand based on pedagogical sequencing in SGK.
# ======================================================================

PREREQUISITES = [
    # NAQ thread 1911 -> 1920 -> 1925 -> 1930
    ("E_NAQTimDuongCuuNuoc", "E_NAQGuiYeuSach1919"),
    ("E_NAQGuiYeuSach1919", "E_NAQDocLuanCuongLenin"),
    ("E_NAQDocLuanCuongLenin", "E_NAQTuHoTuanBan1920"),
    ("E_NAQTuHoTuanBan1920", "E_ThanhLapHoiVNCMThanhNien"),
    ("E_ThanhLapHoiVNCMThanhNien", "E_BaoThanhNien"),
    ("E_BaoThanhNien", "E_DuongKachMenh"),
    ("E_DuongKachMenh", "E_DD_CSD_TL"),
    ("E_ThanhLapHoiVNCMThanhNien", "E_AN_CSD_TL"),
    ("E_ThanhLapHoiVNCMThanhNien", "E_DD_CSLien_TL"),
    # 3 to chuc CS -> Dang ra doi
    ("E_DD_CSD_TL", "E_HoiNghiThanhLapDang"),
    ("E_AN_CSD_TL", "E_HoiNghiThanhLapDang"),
    ("E_DD_CSLien_TL", "E_HoiNghiThanhLapDang"),
    # Dang ra doi -> cac phong trao tiep theo
    ("E_HoiNghiThanhLapDang", "E_XoVietNgheTinh"),
    ("E_XoVietNgheTinh", "E_DaiHoi1_1935"),
    ("E_HoiNghiThanhLapDang", "E_PhongTraoDanChu"),
    # 1939-1945
    ("E_PhongTraoDanChu", "E_HoiNghi6_1939"),
    ("E_HoiNghi6_1939", "E_KhoiNghiaBacSon"),
    ("E_HoiNghi6_1939", "E_KhoiNghiaNamKi"),
    ("E_KhoiNghiaBacSon", "E_HoiNghi8_1941"),
    ("E_KhoiNghiaNamKi", "E_HoiNghi8_1941"),
    ("E_HoiNghi8_1941", "E_ThanhLapVietMinh"),
    ("E_ThanhLapVietMinh", "E_ThanhLapVNTuyenTruyenGPQ"),
    ("E_NhatDaoChinhPhap1945", "E_CaoTraoKhangNhat"),
    ("E_ThanhLapVNTuyenTruyenGPQ", "E_CaoTraoKhangNhat"),
    ("E_CaoTraoKhangNhat", "E_HoiNghiTanTrao"),
    ("E_HoiNghiTanTrao", "E_CachMangThangTam"),
    # CMT8 chain
    ("E_CachMangThangTam", "E_KhoiNghiaHaNoi_1945"),
    ("E_CachMangThangTam", "E_KhoiNghiaHue_1945"),
    ("E_CachMangThangTam", "E_KhoiNghiaSaiGon_1945"),
    ("E_KhoiNghiaHaNoi_1945", "E_TuyenNgonDocLap"),
    # 1945-1946
    ("E_TuyenNgonDocLap", "E_DoiDauVoiThuTrongGiac"),
    ("E_DoiDauVoiThuTrongGiac", "E_BauCuQuocHoi1946"),
    ("E_DoiDauVoiThuTrongGiac", "E_HiepDinhSoBo_SK"),
    ("E_HiepDinhSoBo_SK", "E_KCToanQuoc1946"),
    # KC chong Phap chain
    ("E_KCToanQuoc1946", "E_ChienDichVietBac1947"),
    ("E_ChienDichVietBac1947", "E_ChienDichBienGioi1950"),
    ("E_ChienDichBienGioi1950", "E_DaiHoi2_1951"),
    ("E_ChienDichBienGioi1950", "E_ChienDichHoaBinh"),
    ("E_ChienDichHoaBinh", "E_ChienDichTayBac"),
    ("E_ChienDichTayBac", "E_DienBienPhu1954"),
    ("E_DienBienPhu1954", "E_HiepDinhGeneva_SK"),
    # KC chong My chain
    ("E_HiepDinhGeneva_SK", "E_PhongTraoDongKhoi"),
    ("E_PhongTraoDongKhoi", "E_MTDTGP_TL"),
    ("E_PhongTraoDongKhoi", "E_DaiHoi3_1960"),
    ("E_MTDTGP_TL", "E_ApBac1963"),
    ("E_ApBac1963", "E_VanQuyetLiet65"),
    ("E_VanQuyetLiet65", "E_MauThan1968"),
    ("E_MauThan1968", "E_DienBienPhuTrenKhong"),
    ("E_DienBienPhuTrenKhong", "E_HiepDinhParis_SK"),
    ("E_HiepDinhParis_SK", "E_ChienDichTayNguyen"),
    ("E_ChienDichTayNguyen", "E_ChienDichHue_DaNang"),
    ("E_ChienDichHue_DaNang", "E_GPMienNam1975"),
    # Sau 1975
    ("E_GPMienNam1975", "E_TongTuyenCu_1976"),
    ("E_TongTuyenCu_1976", "E_DoiTen_CHXHCN"),
    ("E_DoiTen_CHXHCN", "E_ChienTranhBienGioiTN"),
    ("E_ChienTranhBienGioiTN", "E_ChienTranhBienGioiBac"),
    ("E_ChienTranhBienGioiBac", "E_DaiHoi6_1986"),
    ("E_DaiHoi6_1986", "E_VNGiaNhapASEAN_SK"),
    ("E_VNGiaNhapASEAN_SK", "E_VNGiaNhapWTO"),
    # World: Ianta -> Cold War -> Collapse
    ("E_CTTG2_KetThuc", "E_HoiNghiIanta"),
    ("E_HoiNghiIanta", "C_TratTuHaiCuc"),
    ("E_HoiNghiIanta", "E_ThanhLapLHQ"),
    ("E_KeHoachMarshallSK", "E_NATO_TL"),
    ("C_TratTuHaiCuc", "E_NATO_TL"),
    ("E_SEV_TL", "E_Warsaw_TL"),
    ("E_NATO_TL", "E_Warsaw_TL"),
    ("C_TratTuHaiCuc", "C_ChienTranhLanh"),
    ("E_LienXoBomHN_1949", "C_ChienTranhLanh"),
    ("C_ChienTranhLanh", "E_CaiToGorbachev"),
    ("E_CaiToGorbachev", "E_BerlinWallFall"),
    ("E_BerlinWallFall", "E_LienXoTanRa"),
    ("E_LienXoTanRa", "C_DaCucDaTrungTam"),
    # World: China
    ("E_CTTG2_KetThuc", "E_CHND_TQ_TL"),
    ("E_CHND_TQ_TL", "E_CaiCachTQ1978"),
    # World: ASEAN
    ("E_ThanhLapASEAN", "E_VNGiaNhapASEAN_SK"),
    # World: Cuba
    ("E_CMCuba1959", "M_GPDT_MyLatinh"),
    ("E_NamChauPhi1960", "M_GPDT_ChauPhi"),
    # WWII
    ("E_CTTG2_BungNo", "E_NgaySamChauAu"),
    ("E_NgaySamChauAu", "E_TranHiroshima"),
    ("E_TranHiroshima", "E_CTTG2_KetThuc"),
    # Concept chains
    ("C_ChuNghiaTuBan", "C_ChuNghiaDeQuoc"),
    ("C_ChuNghiaDeQuoc", "C_ChuNghiaThucDan"),
    ("C_ChuNghiaThucDan", "C_HeThongThuocDia"),
    ("C_HeThongThuocDia", "C_PhiThucDanHoa"),
    ("C_CachMangVoSan", "C_CachMangDanToc"),
    ("C_CachMangDanToc", "C_CachMangXHCN"),
    ("C_CNMacLenin", "C_CachMangVoSan"),
    ("C_CNMacLenin", "C_TuTuongHCM"),
    ("C_KinhTeKeHoachHoa", "C_DoiMoi"),
    ("C_DoiMoi", "C_KinhTeThiTruong"),
    ("C_KinhTeThiTruong", "C_HoiNhapQuocTe"),
    ("C_CMKHKT", "C_ToanCauHoa"),
    ("C_ToanCauHoa", "C_KhuVucHoa"),
    ("C_ChienTranhDacBiet", "C_ChienTranhCucBo"),
    ("C_ChienTranhCucBo", "C_VNHoaChienTranh"),
    ("C_PhatXit", "C_DongMinhChongPhatXit"),
]

# ======================================================================
# CAUSAL EDGES (su9:directCause / su9:deepCause)
# ======================================================================

CAUSES_DIRECT = [
    ("E_DienBienPhu1954", "E_HiepDinhGeneva_SK"),
    ("E_DienBienPhuTrenKhong", "E_HiepDinhParis_SK"),
    ("E_HiepDinhParis_SK", "E_GPMienNam1975"),
    ("E_GPMienNam1975", "E_TongTuyenCu_1976"),
    ("E_NhatDaoChinhPhap1945", "E_CaoTraoKhangNhat"),
    ("E_CTTG2_KetThuc", "E_CachMangThangTam"),
    ("E_CachMangThangTam", "E_TuyenNgonDocLap"),
    ("E_DaiHoi6_1986", "C_DoiMoi"),
    ("E_CaiToGorbachev", "E_LienXoTanRa"),
    ("E_BerlinWallFall", "E_LienXoTanRa"),
    ("E_TranHiroshima", "E_CTTG2_KetThuc"),
    ("E_HoiNghiIanta", "E_ThanhLapLHQ"),
    ("E_KeHoachMarshallSK", "E_NATO_TL"),
    ("E_NATO_TL", "E_Warsaw_TL"),
]

CAUSES_DEEP = [
    ("C_ChuNghiaThucDan", "E_NAQTimDuongCuuNuoc"),
    ("C_CNMacLenin", "E_HoiNghiThanhLapDang"),
    ("E_CTTG2_BungNo", "E_HoiNghi6_1939"),
    ("E_HoiNghi8_1941", "E_CachMangThangTam"),
    ("E_HoiNghiIanta", "C_ChienTranhLanh"),
    ("C_ChienTranhLanh", "E_LienXoTanRa"),
    ("C_KinhTeKeHoachHoa", "E_DaiHoi6_1986"),
    ("C_PhatXit", "E_CTTG2_BungNo"),
    ("M_DanChu_36_39", "E_CachMangThangTam"),
    ("M_CM_30_31", "M_DanChu_36_39"),
    ("C_HeThongThuocDia", "M_GPDT_ChauA"),
    ("C_HeThongThuocDia", "M_GPDT_ChauPhi"),
    ("C_HeThongThuocDia", "M_GPDT_MyLatinh"),
]

# ======================================================================
# SIMILARITY & CONTRAST (for so-sanh questions)
# ======================================================================

SIMILARITIES = [
    # Parallel campaigns
    ("E_ChienDichVietBac1947", "E_ChienDichBienGioi1950"),
    ("E_ChienDichBienGioi1950", "E_DienBienPhu1954"),
    ("E_DienBienPhu1954", "E_DienBienPhuTrenKhong"),
    ("E_HiepDinhGeneva_SK", "E_HiepDinhParis_SK"),
    ("D_HiepDinhGeneva1954", "D_HiepDinhParis1973"),
    # Parallel revolutions
    ("E_CachMangThangTam", "E_CMCuba1959"),
    ("E_CachMangThangTam", "E_CHND_TQ_TL"),
    # Parallel concepts
    ("C_ChienTranhDacBiet", "C_ChienTranhCucBo"),
    ("C_ChienTranhCucBo", "C_VNHoaChienTranh"),
    # Parallel blocks
    ("O_SEV", "O_EEC"),
    ("O_NATO", "O_Warsaw"),
    # Parallel uprisings
    ("E_KhoiNghiaBacSon", "E_KhoiNghiaNamKi"),
]

CONTRASTS = [
    ("C_ChuNghiaTuBan", "C_ChuNghiaXaHoi"),
    ("C_CachMangTuSan", "C_CachMangVoSan"),
    ("O_NATO", "O_Warsaw"),
    ("L_BacTrieuTien", "L_NamTrieuTien"),
    ("L_DongDuc", "L_TayDuc"),
    ("C_KinhTeKeHoachHoa", "C_KinhTeThiTruong"),
    ("O_VNDCCH", "O_VNCH"),
]

# ======================================================================
# PERSON PARTICIPATION
# ======================================================================

PARTICIPATES = [
    # Ho Chi Minh thread
    ("Pe_HoChiMinh", "E_NAQTimDuongCuuNuoc", "leads"),
    ("Pe_HoChiMinh", "E_NAQGuiYeuSach1919", "leads"),
    ("Pe_HoChiMinh", "E_NAQDocLuanCuongLenin", "leads"),
    ("Pe_HoChiMinh", "E_NAQTuHoTuanBan1920", "leads"),
    ("Pe_HoChiMinh", "E_ThanhLapHoiVNCMThanhNien", "leads"),
    ("Pe_HoChiMinh", "E_BaoThanhNien", "leads"),
    ("Pe_HoChiMinh", "E_DuongKachMenh", "leads"),
    ("Pe_HoChiMinh", "E_HoiNghiThanhLapDang", "leads"),
    ("Pe_HoChiMinh", "E_HoiNghi8_1941", "leads"),
    ("Pe_HoChiMinh", "E_ThanhLapVietMinh", "leads"),
    ("Pe_HoChiMinh", "E_HoiNghiTanTrao", "leads"),
    ("Pe_HoChiMinh", "E_CachMangThangTam", "leads"),
    ("Pe_HoChiMinh", "E_TuyenNgonDocLap", "leads"),
    ("Pe_HoChiMinh", "E_KCToanQuoc1946", "leads"),
    ("Pe_HoChiMinh", "E_DaiHoi2_1951", "leads"),
    # Vo Nguyen Giap
    ("Pe_VoNguyenGiap", "E_ThanhLapVNTuyenTruyenGPQ", "leads"),
    ("Pe_VoNguyenGiap", "E_ChienDichVietBac1947", "leads"),
    ("Pe_VoNguyenGiap", "E_ChienDichBienGioi1950", "leads"),
    ("Pe_VoNguyenGiap", "E_DienBienPhu1954", "leads"),
    # Tran Phu
    ("Pe_TranPhu", "E_HoiNghiThanhLapDang", "participatesIn"),
    # Le Duan, Truong Chinh
    ("Pe_LeDuan", "E_DaiHoi3_1960", "leads"),
    ("Pe_LeDuan", "E_DaiHoi6_1986", "participatesIn"),
    ("Pe_TruongChinh", "E_DaiHoi6_1986", "leads"),
    # Van Tien Dung
    ("Pe_VanTienDung", "E_GPMienNam1975", "leads"),
    # Historical predecessors
    ("Pe_PhanBoiChau", "M_DongDu", "leads"),
    ("Pe_PhanChauTrinh", "M_DuyTan", "leads"),
    ("Pe_NguyenThaiHoc", "E_KhoiNghiaYenBai", "leads"),
    # World leaders
    ("Pe_Stalin", "E_HoiNghiIanta", "participatesIn"),
    ("Pe_Roosevelt", "E_HoiNghiIanta", "participatesIn"),
    ("Pe_Churchill", "E_HoiNghiIanta", "participatesIn"),
    ("Pe_Truman", "E_TranHiroshima", "participatesIn"),
    ("Pe_Gorbachev", "E_CaiToGorbachev", "leads"),
    ("Pe_Gorbachev", "E_LienXoTanRa", "participatesIn"),
    ("Pe_MaoTrachDong", "E_CHND_TQ_TL", "leads"),
    ("Pe_DangTieuBinh", "E_CaiCachTQ1978", "leads"),
    ("Pe_FidelCastro", "E_CMCuba1959", "leads"),
    ("Pe_NelsonMandela", "E_XoaBoApartheid", "leads"),
    ("Pe_Nixon", "E_DienBienPhuTrenKhong", "participatesIn"),
]

# Involved concepts
INVOLVED_CONCEPTS = [
    ("E_HoiNghiThanhLapDang", "C_CNMacLenin"),
    ("E_HoiNghiThanhLapDang", "C_CachMangVoSan"),
    ("E_HoiNghiThanhLapDang", "C_CachMangDanToc"),
    ("E_TuyenNgonDocLap", "C_CachMangDanToc"),
    ("E_CachMangThangTam", "C_CachMangDanToc"),
    ("E_DaiHoi6_1986", "C_DoiMoi"),
    ("E_DaiHoi6_1986", "C_KinhTeThiTruong"),
    ("E_MauThan1968", "C_ChienTranhCucBo"),
    ("E_ApBac1963", "C_ChienTranhDacBiet"),
    ("E_DienBienPhuTrenKhong", "C_VNHoaChienTranh"),
    ("E_HoiNghiIanta", "C_TratTuHaiCuc"),
    ("E_NATO_TL", "C_ChienTranhLanh"),
    ("E_Warsaw_TL", "C_ChienTranhLanh"),
    ("E_LienXoTanRa", "C_DaCucDaTrungTam"),
    ("E_CMKHKT_BungNo", "C_CMKHKT"),
    ("E_CMKHKT_BungNo", "C_ToanCauHoa"),
    ("M_DongDu", "C_CachMangTuSan"),
    ("M_CM_30_31", "C_CachMangVoSan"),
    ("M_KhongLienKet", "C_ChienTranhLanh"),
    ("E_XoVietNgheTinh", "C_CachMangVoSan"),
]

print(f"  + {len(PREREQUISITES)} prereq, {len(CAUSES_DIRECT)} direct-cause, "
      f"{len(CAUSES_DEEP)} deep-cause, {len(SIMILARITIES)} similar, "
      f"{len(CONTRASTS)} contrast, {len(PARTICIPATES)} participation, "
      f"{len(INVOLVED_CONCEPTS)} involved-concept")
