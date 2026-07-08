"""
Ly 9 ontology generator.

Schema similar to Toan (logical + formula-heavy) but with PHYSICAL quantities,
units, experimental setups, and phenomena distinct from mathematical abstraction.

Difficulty drivers:
  (a) number of formulas needed simultaneously,
  (b) abstractness (concrete device -> abstract principle like energy conservation),
  (c) multi-step derivation (I from circuit, then P from I, then A from P and t),
  (d) unit conversion requirements,
  (e) vector reasoning (force direction, field lines).

Classes:
  - Law:              dinh luat vat li (Ohm, Jun-Lenxo, bao toan nang luong...)
  - Formula:          cong thuc tinh toan
  - Quantity:         dai luong vat li (I, U, R, P, A, Q, f, d...)
  - Unit:             don vi (A, V, Ohm, W, J, m...)
  - Phenomenon:       hien tuong (khuc xa, cam ung dien tu, tan sac...)
  - Concept:          khai niem (mach noi tiep, tieu cu, anh that...)
  - Device:           dung cu / thiet bi (vol ke, am pe ke, thau kinh...)
  - Method:           phuong phap giai
  - ProblemType:      dang toan
  - ExperimentSetup:  bo thi nghiem (bo ke thu nghiem dinh luat Ohm...)
  - LessonUnit, Textbook
"""

from pathlib import Path
ROOT = Path(__file__).resolve().parent

HEADER = """\
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix phys: <http://edu.vn/phys9/ontology#> .

<http://edu.vn/phys9/ontology> a owl:Ontology ;
    rdfs:label "Ontology Ly 9 - Cold-start Question Difficulty Estimation"@vi ;
    owl:versionInfo "0.1.0" .
"""

SCHEMA = """\
#################################################################
#   CLASSES
#################################################################

phys:PhysEntity      a owl:Class ; rdfs:label "Thuc the Vat li"@vi .
phys:Law             a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Dinh luat"@vi .
phys:Formula         a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Cong thuc"@vi .
phys:Quantity        a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Dai luong"@vi .
phys:Unit            a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Don vi"@vi .
phys:Phenomenon      a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Hien tuong"@vi .
phys:Concept         a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Khai niem"@vi .
phys:Device          a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Dung cu / Thiet bi"@vi .
phys:Method          a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Phuong phap"@vi .
phys:ProblemType     a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Dang toan"@vi .
phys:ExperimentSetup a owl:Class ; rdfs:subClassOf phys:PhysEntity ; rdfs:label "Bo thi nghiem"@vi .
phys:LessonUnit      a owl:Class ; rdfs:label "Bai hoc SGK"@vi .
phys:Textbook        a owl:Class ; rdfs:label "Bo SGK"@vi .

#################################################################
#   OBJECT PROPERTIES
#################################################################

phys:prerequisiteOf a owl:ObjectProperty , owl:TransitiveProperty ; rdfs:label "la tien de cua"@vi .
phys:uses a owl:ObjectProperty ; rdfs:label "su dung"@vi .

phys:measures a owl:ObjectProperty ;
    rdfs:domain phys:Device ; rdfs:range phys:Quantity ;
    rdfs:label "do dai luong"@vi .

phys:hasUnit a owl:ObjectProperty ;
    rdfs:domain phys:Quantity ; rdfs:range phys:Unit ;
    rdfs:label "co don vi"@vi .

phys:relatesQuantities a owl:ObjectProperty ;
    rdfs:domain phys:Formula ; rdfs:range phys:Quantity ;
    rdfs:label "lien he cac dai luong"@vi .

phys:derivedFrom a owl:ObjectProperty ;
    rdfs:domain phys:Formula ; rdfs:range phys:Law ;
    rdfs:label "suy ra tu"@vi .

phys:explainedBy a owl:ObjectProperty ;
    rdfs:domain phys:Phenomenon ; rdfs:range phys:Law ;
    rdfs:label "giai thich boi"@vi .

phys:solves a owl:ObjectProperty ;
    rdfs:domain phys:Method ; rdfs:range phys:ProblemType ;
    rdfs:label "giai duoc dang"@vi .

phys:usedIn a owl:ObjectProperty ;
    rdfs:domain phys:Device ; rdfs:range phys:ExperimentSetup ;
    rdfs:label "duoc dung trong"@vi .

phys:appearsInLesson a owl:ObjectProperty ; rdfs:range phys:LessonUnit ; rdfs:label "xuat hien trong bai"@vi .
phys:partOfTextbook a owl:ObjectProperty ; rdfs:range phys:Textbook ; rdfs:label "thuoc bo SGK"@vi .

phys:similarTo a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "tuong tu"@vi .
phys:contrastsWith a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "doi lap"@vi .

#################################################################
#   DATA PROPERTIES
#################################################################

phys:abstractness a owl:DatatypeProperty ; rdfs:range xsd:integer .
phys:bloomLevel a owl:DatatypeProperty ; rdfs:range xsd:integer .
phys:symbolicDensity a owl:DatatypeProperty ; rdfs:range xsd:integer .
phys:applicationSteps a owl:DatatypeProperty ; rdfs:range xsd:integer .
phys:requiresVectorReasoning a owl:DatatypeProperty ; rdfs:range xsd:boolean ;
    rdfs:comment "Doi hoi suy luan vector (phuong, chieu)?"@vi .
phys:symbol a owl:DatatypeProperty ; rdfs:range xsd:string .
phys:frequencyInTextbook a owl:DatatypeProperty ; rdfs:range xsd:integer .
phys:curriculumPosition a owl:DatatypeProperty ; rdfs:range xsd:integer .
phys:aliases a owl:DatatypeProperty ; rdfs:range xsd:string .
phys:confidence a owl:DatatypeProperty ; rdfs:range xsd:integer .

#################################################################
#   TEXTBOOKS
#################################################################

phys:TB_Old a phys:Textbook ; rdfs:label "SGK Vat li 9 (bo cu)"@vi ; phys:confidence 3 .
phys:TB_KNTT a phys:Textbook ; rdfs:label "SGK KHTN 9 - Ket noi tri thuc"@vi ; phys:confidence 3 .
phys:TB_CTST a phys:Textbook ; rdfs:label "SGK KHTN 9 - Chan troi sang tao"@vi ; phys:confidence 3 .
phys:TB_CD a phys:Textbook ; rdfs:label "SGK KHTN 9 - Canh Dieu"@vi ; phys:confidence 3 .
"""

# ======================================================================
# DATA
# ======================================================================

# --- Laws ---
LAWS = [
    # id, label, aliases, abstract, bloom, conf
    ("L_Ohm", "Dinh luat Om (Ohm)", "Dinh luat Om", 3, 2, 3),
    ("L_JunLenxo", "Dinh luat Jun-Lenxo", "Jun-Len-xo", 3, 2, 3),
    ("L_BaoToanNL", "Dinh luat bao toan va chuyen hoa nang luong", "BTNL|Bao toan nang luong", 4, 3, 3),
    ("L_KhucXaAnhSang", "Dinh luat khuc xa anh sang", "", 3, 2, 3),
    ("L_CamUngDienTu", "Hien tuong cam ung dien tu (Faraday)", "Faraday", 3, 3, 3),
    ("L_NhiemTu", "Quy tac nhiem tu cua dong dien (ban tay phai)", "Quy tac ban tay phai", 3, 3, 3),
    ("L_BanTayTrai", "Quy tac ban tay trai (luc tu)", "Ban tay trai", 3, 3, 3),
    ("L_TruyenThangAS", "Dinh luat truyen thang anh sang (on tap)", "", 2, 2, 3),
    ("L_PhanXaAS", "Dinh luat phan xa anh sang (on tap)", "", 2, 2, 3),
    ("L_MayBienThe", "Cong thuc may bien the U1/U2 = N1/N2", "", 3, 2, 3),
]

# --- Formulas ---
FORMULAS = [
    # id, label, aliases, symdens, steps, abstract, conf
    ("F_Ohm", "U = I.R (Dinh luat Om)", "", 3, 1, 3, 3),
    ("F_R_U_I", "R = U / I", "", 2, 1, 3, 3),
    ("F_NoiTiep_R", "R_td = R1 + R2 (mach noi tiep)", "", 3, 1, 3, 3),
    ("F_SongSong_R", "1/R_td = 1/R1 + 1/R2 (mach song song)", "", 4, 2, 3, 3),
    ("F_NoiTiep_U", "U = U1 + U2 (mach noi tiep)", "", 2, 1, 3, 3),
    ("F_NoiTiep_I", "I = I1 = I2 (mach noi tiep)", "", 2, 1, 2, 3),
    ("F_SongSong_U", "U = U1 = U2 (mach song song)", "", 2, 1, 2, 3),
    ("F_SongSong_I", "I = I1 + I2 (mach song song)", "", 2, 1, 3, 3),
    ("F_R_DayDan", "R = rho.L / S (dien tro day dan)", "", 4, 2, 4, 3),
    ("F_CongSuat", "P = U.I", "", 2, 1, 3, 3),
    ("F_CongSuat_2", "P = I^2.R = U^2/R", "", 3, 2, 3, 3),
    ("F_DienNang", "A = P.t = U.I.t", "", 3, 2, 3, 3),
    ("F_JunLenxo", "Q = I^2.R.t (toa nhiet)", "", 3, 2, 3, 3),
    ("F_MayBT", "U1/U2 = N1/N2 (may bien the)", "", 3, 1, 3, 3),
    ("F_ThauKinh_HoiTu", "1/f = 1/d + 1/d' (thau kinh hoi tu)", "", 4, 2, 4, 3),
    ("F_DoBoi_AnhThau", "h'/h = d'/d (do phong dai)", "", 3, 2, 3, 3),
    ("F_KhucXa_Sin", "Quan he goc toi va goc khuc xa (dinh tinh)", "", 3, 2, 3, 3),
]

# --- Quantities ---
QUANTITIES = [
    # id, label, symbol, unit_id, abstract, conf
    ("Q_CuongDoDongDien", "Cuong do dong dien", "I", "U_Ampe", 2, 3),
    ("Q_HieuDienThe", "Hieu dien the", "U", "U_Von", 2, 3),
    ("Q_DienTro", "Dien tro", "R", "U_Ohm", 2, 3),
    ("Q_DienTroSuat", "Dien tro suat", "rho", "U_OhmMet", 3, 3),
    ("Q_CongSuatDien", "Cong suat dien", "P", "U_Oat", 2, 3),
    ("Q_DienNang", "Dien nang (cong dong dien)", "A", "U_Jun", 2, 3),
    ("Q_NhietLuong", "Nhiet luong", "Q", "U_Jun", 2, 3),
    ("Q_ChieuDaiDay", "Chieu dai day dan", "L", "U_Met", 1, 3),
    ("Q_TietDienDay", "Tiet dien day", "S", "U_MetVuong", 2, 3),
    ("Q_ThoiGian", "Thoi gian", "t", "U_Giay", 1, 3),
    ("Q_TieuCu", "Tieu cu", "f", "U_Met", 2, 3),
    ("Q_KhoangCachVat", "Khoang cach tu vat den thau kinh", "d", "U_Met", 2, 3),
    ("Q_KhoangCachAnh", "Khoang cach tu anh den thau kinh", "d'", "U_Met", 2, 3),
    ("Q_SoVongDay", "So vong day cuon so cap / thu cap", "N", None, 2, 3),
    ("Q_NhietDung", "Nhiet dung rieng", "c", "U_JouleKgK", 3, 2),
]

# --- Units ---
UNITS = [
    ("U_Ampe", "Ampe (A)", "A", 3),
    ("U_Von", "Von (V)", "V", 3),
    ("U_Ohm", "Om (Ohm)", "Ohm", 3),
    ("U_OhmMet", "Om.met (Ohm.m)", "Ohm.m", 3),
    ("U_Oat", "Oat (W)", "W", 3),
    ("U_Jun", "Jun (J)", "J", 3),
    ("U_KilowattGio", "Kilowatt gio (kWh)", "kWh", 3),
    ("U_Met", "Met (m)", "m", 3),
    ("U_MetVuong", "Met vuong (m^2)", "m^2", 3),
    ("U_Giay", "Giay (s)", "s", 3),
    ("U_JouleKgK", "J/(kg.K)", "J/(kg.K)", 2),
]

# --- Phenomena ---
PHENOMENA = [
    # id, label, aliases, abstract, bloom, conf
    ("PH_KhucXa", "Khuc xa anh sang", "", 3, 3, 3),
    ("PH_PhanXa", "Phan xa anh sang (on tap)", "", 2, 2, 3),
    ("PH_TanSac", "Tan sac anh sang", "", 3, 3, 3),
    ("PH_TrongThay", "Trong thay anh cua vat qua thau kinh", "", 3, 3, 3),
    ("PH_CamUngDienTu_PH", "Cam ung dien tu", "", 4, 3, 3),
    ("PH_TuTruongCuaDongDien", "Tu truong cua dong dien", "", 3, 3, 3),
    ("PH_TacDungTuCuaDongDien", "Tac dung tu cua dong dien", "", 3, 3, 3),
    ("PH_LucDienTu", "Luc dien tu tac dung len day dan", "", 3, 3, 3),
    ("PH_TruyenTaiDienNang", "Hao phi khi truyen tai dien nang xa", "", 4, 3, 3),
    ("PH_DoanMachHoTai", "Doan mach ngan gay qua tai", "", 3, 3, 3),
    ("PH_MatCan_MatLao", "Mat can, mat lao", "Tat cua mat", 3, 3, 3),
    ("PH_AnhSangMau", "Tong hop va phan tich anh sang mau", "", 3, 3, 3),
    ("PH_TacDungNhietAS", "Tac dung nhiet, quang, sinh cua anh sang", "", 3, 2, 3),
]

# --- Devices ---
DEVICES = [
    ("DV_AmpeKe", "Ampe ke", "", 1, 3),
    ("DV_VonKe", "Von ke", "", 1, 3),
    ("DV_DienTro", "Dien tro", "", 1, 3),
    ("DV_BienTro", "Bien tro (con chay)", "", 2, 3),
    ("DV_BongDen", "Bong den day toc", "", 1, 3),
    ("DV_Pin", "Pin / nguon dien", "", 1, 3),
    ("DV_ThauKinhHT", "Thau kinh hoi tu", "TKHT", 2, 3),
    ("DV_ThauKinhPK", "Thau kinh phan ki", "TKPK", 2, 3),
    ("DV_GuongPhang", "Guong phang (on tap)", "", 1, 3),
    ("DV_MayAnh", "May anh", "", 2, 3),
    ("DV_KinhLup", "Kinh lup", "", 2, 3),
    ("DV_NamCham", "Nam cham", "", 1, 3),
    ("DV_DongCoDien1C", "Dong co dien mot chieu", "", 3, 3),
    ("DV_MayPhatDien", "May phat dien xoay chieu", "", 3, 3),
    ("DV_MayBienThe", "May bien the", "May bien ap", 3, 3),
    ("DV_DongHoDoDien", "Dong ho do dien (cong to)", "Cong to dien", 2, 3),
    ("DV_LangKinh", "Lang kinh (tan sac)", "", 2, 3),
    ("DV_MatNguoi", "Mat nguoi (cau tao quang hoc)", "", 2, 3),
]

# --- Concepts ---
CONCEPTS = [
    ("C_MachNoiTiep", "Doan mach noi tiep", "", 2, 2, 3),
    ("C_MachSongSong", "Doan mach song song", "", 2, 2, 3),
    ("C_MachHonHop", "Doan mach hon hop", "", 3, 3, 3),
    ("C_TuTruong", "Tu truong", "", 4, 3, 3),
    ("C_DuongSucTu", "Duong suc tu", "", 3, 3, 3),
    ("C_TuPhoDongDien", "Tu pho cua dong dien", "", 3, 3, 3),
    ("C_NhiemTu_KL", "Su nhiem tu cua kim loai", "", 3, 3, 3),
    ("C_DongDienXoayChieu", "Dong dien xoay chieu", "", 3, 3, 3),
    ("C_TieuDiem", "Tieu diem cua thau kinh", "", 3, 3, 3),
    ("C_TrucChinh", "Truc chinh cua thau kinh", "", 2, 2, 3),
    ("C_AnhThat", "Anh that (qua thau kinh)", "", 3, 3, 3),
    ("C_AnhAo", "Anh ao (qua thau kinh)", "", 3, 3, 3),
    ("C_CauToaAS", "Cau tao anh sang trang", "", 3, 3, 3),
    ("C_NangLuong", "Nang luong va cac dang nang luong", "", 4, 3, 3),
    ("C_ChuyenHoaNL", "Su chuyen hoa nang luong", "", 4, 3, 3),
    ("C_CongDongDien_KN", "Cong cua dong dien", "Dien nang tieu thu", 3, 2, 3),
    ("C_AnToanDien", "An toan khi su dung dien", "", 2, 2, 3),
    ("C_TietKiemDienNang", "Tiet kiem dien nang", "", 2, 2, 3),
]

# --- Methods ---
METHODS = [
    ("M_GiaiMachNoiTiep", "Giai mach noi tiep (tinh I, U, R)", "", 3, 3, 2, 3),
    ("M_GiaiMachSongSong", "Giai mach song song", "", 4, 3, 3, 3),
    ("M_GiaiMachHonHop", "Giai mach hon hop", "", 5, 4, 3, 3),
    ("M_TinhDienNang_CSuat", "Tinh dien nang va cong suat tieu thu", "", 3, 3, 2, 3),
    ("M_TinhQ_JunLenxo", "Tinh nhiet luong toa ra theo Jun-Lenxo", "", 3, 3, 2, 3),
    ("M_QuyTacBanTayPhai", "Xac dinh chieu duong suc tu (quy tac ban tay phai)", "", 3, 3, 3, 3),
    ("M_QuyTacBanTayTrai", "Xac dinh chieu luc tu (ban tay trai)", "", 4, 3, 3, 3),
    ("M_VeAnhQuaTKHT", "Ve anh cua vat qua thau kinh hoi tu", "", 3, 3, 3, 3),
    ("M_VeAnhQuaTKPK", "Ve anh cua vat qua thau kinh phan ki", "", 3, 3, 3, 3),
    ("M_TinhAnhBangCongThuc", "Tinh vi tri va do cao cua anh bang cong thuc", "", 4, 4, 3, 3),
    ("M_TinhMayBienThe", "Tinh toan voi may bien the", "", 3, 3, 2, 3),
]

# --- Problem Types ---
PROBLEM_TYPES = [
    ("PT_TinhR_Ohm", "Tinh dien tro tu U, I (Om)", "", 2, 2, 3),
    ("PT_TinhU_TuongDuong", "Tinh dien tro tuong duong cua mach", "", 3, 3, 3),
    ("PT_MachHonHop_IUR", "Phan tich mach hon hop tim I, U, R", "", 4, 4, 3),
    ("PT_TinhCongSuat", "Tinh cong suat thiet bi", "", 2, 2, 3),
    ("PT_TinhDienNangTieuThu", "Tinh dien nang tieu thu trong thoi gian t", "", 3, 3, 3),
    ("PT_NhietLuongJun", "Tinh nhiet luong toa ra (Jun-Lenxo)", "", 3, 3, 3),
    ("PT_XacDinhChieuLuc_BTT", "Xac dinh chieu luc tu bang ban tay trai", "", 3, 3, 3),
    ("PT_ChieuDongDienCamUng", "Xac dinh chieu dong dien cam ung", "", 4, 4, 3),
    ("PT_VeAnhQuaTK", "Ve anh cua vat qua thau kinh", "", 3, 3, 3),
    ("PT_TinhViTriAnh", "Tinh vi tri va do cao cua anh", "", 4, 3, 3),
    ("PT_MayBienThe_UN", "Tinh toan may bien the (U, N)", "", 3, 2, 3),
    ("PT_HaoPhiTTDN", "Tinh hao phi tren duong day truyen tai", "", 4, 3, 3),
]

# --- Experiment setups ---
EXPERIMENTS = [
    ("E_DoDinhLuatOhm", "Do su phu thuoc I vao U (kiem chung Ohm)", "", 3, 3),
    ("E_DoRDayDan", "Do dien tro day dan theo L, S, vat lieu", "", 3, 3),
    ("E_JunLenxo", "Kiem chung dinh luat Jun-Lenxo", "", 3, 2),
    ("E_TuPho", "Quan sat tu pho nam cham va dong dien", "", 2, 3),
    ("E_CamUng", "Phat hien hien tuong cam ung dien tu", "", 3, 3),
    ("E_ThauKinh", "Kho sat anh qua thau kinh", "", 3, 3),
    ("E_TanSacAS", "Kiem chung su tan sac anh sang bang lang kinh", "", 3, 3),
]

print(f'Ly: {len(LAWS)} laws, {len(FORMULAS)} formulas, {len(QUANTITIES)} quantities, '
      f'{len(UNITS)} units, {len(PHENOMENA)} phen, {len(DEVICES)} devices, '
      f'{len(CONCEPTS)} concepts, {len(METHODS)} methods, {len(PROBLEM_TYPES)} PT, '
      f'{len(EXPERIMENTS)} exps')


# ======================================================================
# LESSONS
# ======================================================================
LESSONS_OLD = [
    # Chuong I: Dien hoc
    (1, "Su phu thuoc cua cuong do dong dien vao hieu dien the"),
    (2, "Dien tro cua day dan - Dinh luat Om"),
    (3, "Thuc hanh: Xac dinh dien tro"),
    (4, "Doan mach noi tiep"),
    (5, "Doan mach song song"),
    (6, "Bai tap van dung dinh luat Om"),
    (7, "Su phu thuoc cua dien tro vao chieu dai day dan"),
    (8, "Su phu thuoc cua dien tro vao tiet dien day dan"),
    (9, "Su phu thuoc cua dien tro vao vat lieu lam day"),
    (10, "Bien tro - Dien tro dung trong ky thuat"),
    (11, "Cong suat dien"),
    (12, "Dien nang - Cong cua dong dien"),
    (13, "Bai tap cong suat va cong cua dong dien"),
    (14, "Thuc hanh: Xac dinh cong suat"),
    (15, "Dinh luat Jun - Lenxo"),
    (16, "Bai tap van dung Jun - Lenxo"),
    (17, "Thuc hanh: Kiem nghiem Jun-Lenxo"),
    (18, "Su dung an toan va tiet kiem dien"),
    (19, "Tong ket chuong I"),
    # Chuong II: Dien tu hoc
    (20, "Nam cham vinh cuu"),
    (21, "Tac dung tu cua dong dien - Tu truong"),
    (22, "Tu pho - Duong suc tu"),
    (23, "Tu truong cua ong day co dong dien chay qua"),
    (24, "Su nhiem tu cua sat, thep - Nam cham dien"),
    (25, "Ung dung cua nam cham"),
    (26, "Luc dien tu"),
    (27, "Dong co dien mot chieu"),
    (28, "Thuc hanh"),
    (29, "Hien tuong cam ung dien tu"),
    (30, "Dieu kien xuat hien dong dien cam ung"),
    (31, "Dong dien xoay chieu"),
    (32, "May phat dien xoay chieu"),
    (33, "Cac tac dung cua dong dien xoay chieu - Do cuong do va hieu dien the xoay chieu"),
    (34, "Truyen tai dien nang di xa"),
    (35, "May bien the"),
    (36, "Thuc hanh: Van hanh may phat va may bien the"),
    (37, "Tong ket chuong II"),
    # Chuong III: Quang hoc
    (38, "Hien tuong khuc xa anh sang"),
    (39, "Quan he giua goc toi va goc khuc xa"),
    (40, "Thau kinh hoi tu"),
    (41, "Anh cua mot vat tao boi thau kinh hoi tu"),
    (42, "Thau kinh phan ki"),
    (43, "Anh cua mot vat tao boi thau kinh phan ki"),
    (44, "Thuc hanh: Do tieu cu thau kinh hoi tu"),
    (45, "Su tao anh trong may anh"),
    (46, "Mat"),
    (47, "Mat can va mat lao"),
    (48, "Kinh lup"),
    (49, "Anh sang trang va anh sang mau"),
    (50, "Su phan tich anh sang trang"),
    (51, "Su tron cac anh sang mau"),
    (52, "Mau sac cac vat duoi anh sang trang va anh sang mau"),
    (53, "Cac tac dung cua anh sang"),
    (54, "Thuc hanh"),
    (55, "Tong ket chuong III"),
    # Chuong IV: Bao toan nang luong
    (56, "Nang luong va su chuyen hoa nang luong"),
    (57, "Dinh luat bao toan nang luong"),
    (58, "San xuat dien nang - Nhiet dien va thuy dien"),
    (59, "Dien gio - Dien mat troi - Dien hat nhan"),
    (60, "Tong ket cuoi nam"),
]

LESSONS_KNTT = [(i, f"KNTT Bai {i}") for i in range(1, 36)]
LESSONS_CTST = [(i, f"CTST Bai {i}") for i in range(1, 36)]
LESSONS_CD   = [(i, f"CD Bai {i}") for i in range(1, 36)]

# ======================================================================
# RELATIONSHIPS
# ======================================================================

# Quantity -> Unit
HAS_UNIT = [(q[0], q[3]) for q in QUANTITIES if q[3]]

# Device measures Quantity
MEASURES = [
    ("DV_AmpeKe", "Q_CuongDoDongDien"),
    ("DV_VonKe", "Q_HieuDienThe"),
    ("DV_DongHoDoDien", "Q_DienNang"),
]

# Formula relates Quantities (which quantities does each formula involve?)
RELATES = [
    ("F_Ohm", "Q_CuongDoDongDien"), ("F_Ohm", "Q_HieuDienThe"), ("F_Ohm", "Q_DienTro"),
    ("F_R_U_I", "Q_DienTro"), ("F_R_U_I", "Q_HieuDienThe"), ("F_R_U_I", "Q_CuongDoDongDien"),
    ("F_NoiTiep_R", "Q_DienTro"),
    ("F_SongSong_R", "Q_DienTro"),
    ("F_R_DayDan", "Q_DienTro"), ("F_R_DayDan", "Q_DienTroSuat"),
    ("F_R_DayDan", "Q_ChieuDaiDay"), ("F_R_DayDan", "Q_TietDienDay"),
    ("F_CongSuat", "Q_CongSuatDien"), ("F_CongSuat", "Q_HieuDienThe"), ("F_CongSuat", "Q_CuongDoDongDien"),
    ("F_CongSuat_2", "Q_CongSuatDien"), ("F_CongSuat_2", "Q_CuongDoDongDien"), ("F_CongSuat_2", "Q_DienTro"),
    ("F_DienNang", "Q_DienNang"), ("F_DienNang", "Q_CongSuatDien"), ("F_DienNang", "Q_ThoiGian"),
    ("F_JunLenxo", "Q_NhietLuong"), ("F_JunLenxo", "Q_CuongDoDongDien"),
    ("F_JunLenxo", "Q_DienTro"), ("F_JunLenxo", "Q_ThoiGian"),
    ("F_MayBT", "Q_HieuDienThe"), ("F_MayBT", "Q_SoVongDay"),
    ("F_ThauKinh_HoiTu", "Q_TieuCu"), ("F_ThauKinh_HoiTu", "Q_KhoangCachVat"), ("F_ThauKinh_HoiTu", "Q_KhoangCachAnh"),
    ("F_DoBoi_AnhThau", "Q_KhoangCachVat"), ("F_DoBoi_AnhThau", "Q_KhoangCachAnh"),
]

# Formula derivedFrom Law
DERIVED_FROM = [
    ("F_Ohm", "L_Ohm"),
    ("F_R_U_I", "L_Ohm"),
    ("F_CongSuat", "L_Ohm"),
    ("F_CongSuat_2", "L_Ohm"),
    ("F_JunLenxo", "L_JunLenxo"),
    ("F_MayBT", "L_MayBienThe"),
]

# Phenomenon explainedBy Law
EXPLAINED_BY = [
    ("PH_KhucXa", "L_KhucXaAnhSang"),
    ("PH_PhanXa", "L_PhanXaAS"),
    ("PH_CamUngDienTu_PH", "L_CamUngDienTu"),
    ("PH_TuTruongCuaDongDien", "L_NhiemTu"),
    ("PH_LucDienTu", "L_BanTayTrai"),
    ("PH_TruyenTaiDienNang", "L_JunLenxo"),
    ("PH_MatCan_MatLao", "L_KhucXaAnhSang"),
]

# Device usedIn Experiment
USED_IN = [
    ("DV_AmpeKe", "E_DoDinhLuatOhm"), ("DV_VonKe", "E_DoDinhLuatOhm"),
    ("DV_DienTro", "E_DoDinhLuatOhm"), ("DV_BienTro", "E_DoDinhLuatOhm"),
    ("DV_DienTro", "E_DoRDayDan"),
    ("DV_NamCham", "E_TuPho"),
    ("DV_NamCham", "E_CamUng"),
    ("DV_ThauKinhHT", "E_ThauKinh"), ("DV_ThauKinhPK", "E_ThauKinh"),
    ("DV_LangKinh", "E_TanSacAS"),
]

# Method solves ProblemType
SOLVES = [
    ("M_GiaiMachNoiTiep", "PT_TinhU_TuongDuong"),
    ("M_GiaiMachSongSong", "PT_TinhU_TuongDuong"),
    ("M_GiaiMachHonHop", "PT_MachHonHop_IUR"),
    ("M_TinhDienNang_CSuat", "PT_TinhCongSuat"),
    ("M_TinhDienNang_CSuat", "PT_TinhDienNangTieuThu"),
    ("M_TinhQ_JunLenxo", "PT_NhietLuongJun"),
    ("M_QuyTacBanTayTrai", "PT_XacDinhChieuLuc_BTT"),
    ("M_QuyTacBanTayPhai", "PT_ChieuDongDienCamUng"),
    ("M_VeAnhQuaTKHT", "PT_VeAnhQuaTK"),
    ("M_VeAnhQuaTKPK", "PT_VeAnhQuaTK"),
    ("M_TinhAnhBangCongThuc", "PT_TinhViTriAnh"),
    ("M_TinhMayBienThe", "PT_MayBienThe_UN"),
    ("M_TinhDienNang_CSuat", "PT_HaoPhiTTDN"),
]

# Uses (one entity references another)
USES = [
    ("F_CongSuat_2", "F_Ohm"),
    ("F_JunLenxo", "L_JunLenxo"),
    ("F_MayBT", "L_MayBienThe"),
    ("M_GiaiMachHonHop", "M_GiaiMachNoiTiep"),
    ("M_GiaiMachHonHop", "M_GiaiMachSongSong"),
]

# Prerequisites (pedagogical order)
PREREQUISITES = [
    # Dien hoc chain
    ("Q_CuongDoDongDien", "Q_HieuDienThe"),
    ("Q_HieuDienThe", "Q_DienTro"),
    ("Q_DienTro", "L_Ohm"),
    ("L_Ohm", "F_Ohm"),
    ("F_Ohm", "F_R_U_I"),
    ("F_R_U_I", "M_GiaiMachNoiTiep"),
    ("F_R_U_I", "M_GiaiMachSongSong"),
    ("M_GiaiMachNoiTiep", "F_NoiTiep_R"),
    ("M_GiaiMachSongSong", "F_SongSong_R"),
    ("M_GiaiMachNoiTiep", "M_GiaiMachHonHop"),
    ("M_GiaiMachSongSong", "M_GiaiMachHonHop"),
    ("F_NoiTiep_R", "C_MachNoiTiep"),
    ("F_SongSong_R", "C_MachSongSong"),
    ("C_MachNoiTiep", "C_MachHonHop"),
    ("C_MachSongSong", "C_MachHonHop"),
    # R day dan
    ("L_Ohm", "F_R_DayDan"),
    ("F_R_DayDan", "DV_BienTro"),
    # Cong suat, dien nang
    ("L_Ohm", "F_CongSuat"),
    ("F_CongSuat", "F_CongSuat_2"),
    ("F_CongSuat", "F_DienNang"),
    ("F_DienNang", "C_CongDongDien_KN"),
    ("C_CongDongDien_KN", "C_TietKiemDienNang"),
    ("F_CongSuat", "L_JunLenxo"),
    ("L_JunLenxo", "F_JunLenxo"),
    ("F_JunLenxo", "M_TinhQ_JunLenxo"),
    ("M_TinhQ_JunLenxo", "PT_NhietLuongJun"),
    # An toan dien
    ("L_JunLenxo", "C_AnToanDien"),
    # Dien tu chain
    ("DV_NamCham", "C_TuTruong"),
    ("C_TuTruong", "C_DuongSucTu"),
    ("C_DuongSucTu", "C_TuPhoDongDien"),
    ("PH_TacDungTuCuaDongDien", "L_NhiemTu"),
    ("L_NhiemTu", "C_NhiemTu_KL"),
    ("C_TuTruong", "PH_LucDienTu"),
    ("PH_LucDienTu", "L_BanTayTrai"),
    ("L_BanTayTrai", "M_QuyTacBanTayTrai"),
    ("M_QuyTacBanTayTrai", "PT_XacDinhChieuLuc_BTT"),
    ("L_BanTayTrai", "DV_DongCoDien1C"),
    ("PH_CamUngDienTu_PH", "L_CamUngDienTu"),
    ("L_CamUngDienTu", "M_QuyTacBanTayPhai"),
    ("M_QuyTacBanTayPhai", "PT_ChieuDongDienCamUng"),
    ("L_CamUngDienTu", "C_DongDienXoayChieu"),
    ("C_DongDienXoayChieu", "DV_MayPhatDien"),
    ("DV_MayPhatDien", "DV_MayBienThe"),
    ("DV_MayBienThe", "L_MayBienThe"),
    ("L_MayBienThe", "F_MayBT"),
    ("F_MayBT", "M_TinhMayBienThe"),
    ("M_TinhMayBienThe", "PT_MayBienThe_UN"),
    ("DV_MayBienThe", "PH_TruyenTaiDienNang"),
    ("PH_TruyenTaiDienNang", "PT_HaoPhiTTDN"),
    # Quang hoc chain
    ("L_TruyenThangAS", "L_PhanXaAS"),
    ("L_PhanXaAS", "L_KhucXaAnhSang"),
    ("L_KhucXaAnhSang", "PH_KhucXa"),
    ("PH_KhucXa", "DV_ThauKinhHT"),
    ("DV_ThauKinhHT", "C_TieuDiem"),
    ("DV_ThauKinhHT", "C_TrucChinh"),
    ("C_TieuDiem", "Q_TieuCu"),
    ("DV_ThauKinhHT", "PH_TrongThay"),
    ("PH_TrongThay", "C_AnhThat"),
    ("PH_TrongThay", "C_AnhAo"),
    ("DV_ThauKinhHT", "M_VeAnhQuaTKHT"),
    ("M_VeAnhQuaTKHT", "PT_VeAnhQuaTK"),
    ("F_ThauKinh_HoiTu", "M_TinhAnhBangCongThuc"),
    ("M_TinhAnhBangCongThuc", "PT_TinhViTriAnh"),
    ("DV_ThauKinhHT", "DV_ThauKinhPK"),
    ("DV_ThauKinhPK", "M_VeAnhQuaTKPK"),
    ("DV_ThauKinhHT", "DV_MayAnh"),
    ("DV_ThauKinhHT", "DV_MatNguoi"),
    ("DV_MatNguoi", "PH_MatCan_MatLao"),
    ("DV_ThauKinhHT", "DV_KinhLup"),
    ("C_CauToaAS", "PH_TanSac"),
    ("PH_TanSac", "PH_AnhSangMau"),
    ("PH_AnhSangMau", "PH_TacDungNhietAS"),
    # Bao toan nang luong
    ("C_NangLuong", "C_ChuyenHoaNL"),
    ("C_ChuyenHoaNL", "L_BaoToanNL"),
]

# Similarities
SIMILARITIES = [
    ("DV_ThauKinhHT", "DV_ThauKinhPK"),
    ("DV_MayPhatDien", "DV_DongCoDien1C"),  # cung nguyen ly
    ("PH_PhanXa", "PH_KhucXa"),
    ("C_MachNoiTiep", "C_MachSongSong"),
    ("F_JunLenxo", "F_CongSuat_2"),
    ("DV_AmpeKe", "DV_VonKe"),
]

CONTRASTS = [
    ("C_MachNoiTiep", "C_MachSongSong"),
    ("DV_ThauKinhHT", "DV_ThauKinhPK"),
    ("C_AnhThat", "C_AnhAo"),
    ("PH_MatCan_MatLao", "DV_MatNguoi"),  # tat vs binh thuong
    ("DV_MayPhatDien", "DV_DongCoDien1C"),  # dao nguoc chuc nang
]

print(f'  + {len(HAS_UNIT)} hasUnit, {len(MEASURES)} measures, {len(RELATES)} relates, '
      f'{len(DERIVED_FROM)} derived, {len(EXPLAINED_BY)} explained, {len(USED_IN)} usedIn, '
      f'{len(SOLVES)} solves, {len(USES)} uses, {len(PREREQUISITES)} prereq, '
      f'{len(SIMILARITIES)} sim, {len(CONTRASTS)} contrast')
