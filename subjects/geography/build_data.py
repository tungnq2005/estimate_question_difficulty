"""
Dia 9 ontology generator.

Schema philosophy:
  - Geography knowledge is SPATIAL + DESCRIPTIVE. Entities are regions,
    phenomena, resources, economic sectors, demographic features.
  - Difficulty is driven by:
      (a) number of factors required to explain a phenomenon,
      (b) spatial scope (one region vs many vs national),
      (c) abstractness (concrete place vs abstract concept like "chuyen dich co cau"),
      (d) causal reasoning depth (why does region X have industry Y?),
      (e) numerical/statistical analysis required.

Classes:
  - Region:         vung dia ly (TDMNBB, DBSH, BTB, DHNTB, TN, DNB, DBSCL, plus provinces)
  - NaturalFeature: song, nui, dong bang, bien, dao
  - Phenomenon:     hien tuong (gio mua, bao, lu, han han, xam nhap man...)
  - Resource:       tai nguyen (than, dau, nuoc, dat trong, thuy san...)
  - Industry:       nganh kinh te (cong nghiep, nong nghiep, dich vu...)
  - Crop:           loai cay trong
  - Livestock:      vat nuoi
  - Demographic:    dac diem dan cu (mat do, tang truong, co cau...)
  - Concept:        khai niem dia ly (toa do, vi do, kinh do, GDP...)
  - Process:        qua trinh (cong nghiep hoa, do thi hoa, chuyen dich co cau...)
  - LessonUnit, Textbook
"""

from pathlib import Path
ROOT = Path(__file__).resolve().parent

HEADER = """\
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix geo:  <http://edu.vn/geo9/ontology#> .

<http://edu.vn/geo9/ontology> a owl:Ontology ;
    rdfs:label "Ontology Dia 9 - Cold-start Question Difficulty Estimation"@vi ;
    owl:versionInfo "0.1.0" .
"""

SCHEMA = """\
#################################################################
#   CLASSES
#################################################################

geo:GeoEntity a owl:Class ; rdfs:label "Thuc the Dia ly"@vi .
geo:Region         a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Vung dia ly"@vi .
geo:NaturalFeature a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Dac diem tu nhien"@vi .
geo:Phenomenon     a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Hien tuong"@vi .
geo:Resource       a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Tai nguyen"@vi .
geo:Industry       a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Nganh kinh te"@vi .
geo:Crop           a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Loai cay trong"@vi .
geo:Livestock      a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Vat nuoi"@vi .
geo:Demographic    a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Dac diem dan cu"@vi .
geo:Concept        a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Khai niem dia ly"@vi .
geo:Process        a owl:Class ; rdfs:subClassOf geo:GeoEntity ; rdfs:label "Qua trinh"@vi .
geo:LessonUnit     a owl:Class ; rdfs:label "Bai hoc SGK"@vi .
geo:Textbook       a owl:Class ; rdfs:label "Bo SGK"@vi .

#################################################################
#   OBJECT PROPERTIES
#################################################################

geo:prerequisiteOf a owl:ObjectProperty , owl:TransitiveProperty ; rdfs:label "la tien de cua"@vi .

geo:locatedIn a owl:ObjectProperty , owl:TransitiveProperty ;
    rdfs:domain geo:GeoEntity ; rdfs:range geo:Region ;
    rdfs:label "nam trong"@vi .

geo:adjacentTo a owl:ObjectProperty , owl:SymmetricProperty ;
    rdfs:domain geo:Region ; rdfs:range geo:Region ;
    rdfs:label "giap voi"@vi .

geo:occursIn a owl:ObjectProperty ;
    rdfs:domain geo:Phenomenon ; rdfs:range geo:Region ;
    rdfs:label "xay ra tai"@vi .

geo:hasResource a owl:ObjectProperty ;
    rdfs:domain geo:Region ; rdfs:range geo:Resource ;
    rdfs:label "co tai nguyen"@vi .

geo:specializesIn a owl:ObjectProperty ;
    rdfs:domain geo:Region ; rdfs:range geo:Industry ;
    rdfs:label "the manh nganh"@vi .

geo:grownIn a owl:ObjectProperty ;
    rdfs:domain geo:Crop ; rdfs:range geo:Region ;
    rdfs:label "duoc trong tai"@vi .

geo:raisedIn a owl:ObjectProperty ;
    rdfs:domain geo:Livestock ; rdfs:range geo:Region ;
    rdfs:label "duoc nuoi tai"@vi .

geo:causes a owl:ObjectProperty ; rdfs:label "gay ra"@vi .
geo:affectedBy a owl:ObjectProperty ; owl:inverseOf geo:causes ; rdfs:label "bi anh huong boi"@vi .

geo:appearsInLesson a owl:ObjectProperty ; rdfs:range geo:LessonUnit ; rdfs:label "xuat hien trong bai"@vi .
geo:partOfTextbook a owl:ObjectProperty ; rdfs:range geo:Textbook ; rdfs:label "thuoc bo SGK"@vi .

geo:similarTo a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "tuong tu"@vi .
geo:contrastsWith a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "khac biet"@vi .

#################################################################
#   DATA PROPERTIES
#################################################################

geo:abstractness a owl:DatatypeProperty ; rdfs:range xsd:integer .
geo:bloomLevel a owl:DatatypeProperty ; rdfs:range xsd:integer .
geo:frequencyInTextbook a owl:DatatypeProperty ; rdfs:range xsd:integer .
geo:curriculumPosition a owl:DatatypeProperty ; rdfs:range xsd:integer .
geo:spatialScope a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "1=dia phuong, 2=vung, 3=ca nuoc, 4=khu vuc, 5=toan cau"@vi .
geo:explanatoryFactors a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "So nhan to can de giai thich hien tuong (1-5)"@vi .
geo:aliases a owl:DatatypeProperty ; rdfs:range xsd:string .
geo:confidence a owl:DatatypeProperty ; rdfs:range xsd:integer .

#################################################################
#   TEXTBOOKS
#################################################################

geo:TB_Old a geo:Textbook ; rdfs:label "SGK Dia 9 (bo cu)"@vi ; geo:confidence 3 .
geo:TB_KNTT a geo:Textbook ; rdfs:label "SGK LS&DL 9 - Ket noi tri thuc"@vi ; geo:confidence 3 .
geo:TB_CTST a geo:Textbook ; rdfs:label "SGK LS&DL 9 - Chan troi sang tao"@vi ; geo:confidence 3 .
geo:TB_CD a geo:Textbook ; rdfs:label "SGK LS&DL 9 - Canh Dieu"@vi ; geo:confidence 3 .
"""

# ======================================================================
# DATA
# ======================================================================

# --- Regions (7 vung + VN + cac tinh lon) ---
REGIONS = [
    # id, label, aliases, scope, freq, abstract, conf
    ("R_VietNam", "Viet Nam", "", 3, 30, 1, 3),
    # 7 vung kinh te
    ("R_TDMNBB", "Trung du va mien nui Bac Bo", "TDMNBB", 2, 20, 2, 3),
    ("R_DBSH", "Dong bang song Hong", "DBSH", 2, 25, 2, 3),
    ("R_BTB", "Bac Trung Bo", "BTB", 2, 20, 2, 3),
    ("R_DHNTB", "Duyen hai Nam Trung Bo", "DHNTB", 2, 18, 2, 3),
    ("R_TN", "Tay Nguyen", "", 2, 20, 2, 3),
    ("R_DNB", "Dong Nam Bo", "DNB", 2, 22, 2, 3),
    ("R_DBSCL", "Dong bang song Cuu Long", "DBSCL|Tay Nam Bo", 2, 25, 2, 3),
    # Cac tieu vung
    ("R_DongBac", "Dong Bac (thuoc TDMNBB)", "", 1, 6, 2, 3),
    ("R_TayBac", "Tay Bac (thuoc TDMNBB)", "", 1, 6, 2, 3),
    # Cac thanh pho lon
    ("R_HaNoi", "Ha Noi", "", 1, 12, 1, 3),
    ("R_HCM", "TP Ho Chi Minh", "TP HCM|Sai Gon", 1, 12, 1, 3),
    ("R_HaiPhong", "Hai Phong", "", 1, 6, 1, 3),
    ("R_DaNang", "Da Nang", "", 1, 6, 1, 3),
    ("R_CanTho", "Can Tho", "", 1, 5, 1, 3),
    # Khu vuc, bien
    ("R_BienDong", "Bien Dong", "", 4, 10, 2, 3),
    ("R_DongNamA", "Dong Nam A", "", 4, 8, 2, 3),
    # Cac vinh, dao
    ("R_VinhBacBo", "Vinh Bac Bo", "", 3, 4, 1, 3),
    ("R_QuanDaoHoangSa", "Quan dao Hoang Sa", "", 3, 4, 1, 3),
    ("R_QuanDaoTruongSa", "Quan dao Truong Sa", "", 3, 4, 1, 3),
    ("R_PhuQuoc", "Phu Quoc", "", 2, 3, 1, 3),
]

# --- Natural features ---
NATURAL_FEATURES = [
    # id, label, aliases, freq, abstract, conf
    ("NF_HoangLienSon", "Day Hoang Lien Son", "", 4, 2, 3),
    ("NF_Phansipan", "Phan-xi-pang", "Fansipan", 3, 1, 3),
    ("NF_TruongSon", "Day Truong Son", "", 5, 2, 3),
    ("NF_TaySonNguyen", "Tay Nguyen (dia hinh)", "", 4, 2, 3),
    ("NF_DBSH_Plain", "Dong bang Bac Bo", "", 5, 2, 3),
    ("NF_DBSCL_Plain", "Dong bang Nam Bo", "", 5, 2, 3),
    ("NF_SongHong", "Song Hong", "", 6, 1, 3),
    ("NF_SongMekong", "Song Me Kong", "Song Cuu Long", 8, 1, 3),
    ("NF_SongDongNai", "Song Dong Nai", "", 3, 1, 3),
    ("NF_SongDa", "Song Da", "", 3, 1, 3),
    ("NF_BienDong_NF", "Bien Dong (vi tri)", "", 6, 2, 3),
    ("NF_BacHaiDuong", "Bo bien Viet Nam", "Duong bo bien", 6, 2, 3),
    ("NF_KhiHauNhietDoi", "Khi hau nhiet doi am gio mua", "Nhiet doi gio mua", 8, 3, 3),
]

# --- Phenomena ---
PHENOMENA = [
    # id, label, aliases, scope, factors, freq, abstract, bloom, conf
    ("PH_GioMua", "Gio mua", "", 3, 3, 10, 3, 2, 3),
    ("PH_Bao", "Bao", "", 3, 3, 6, 2, 2, 3),
    ("PH_Lu", "Lu, lu quet", "Lu lut", 3, 3, 6, 2, 2, 3),
    ("PH_HanHan", "Han han", "", 3, 3, 5, 2, 2, 3),
    ("PH_XamNhapMan", "Xam nhap man", "", 3, 4, 6, 3, 3, 3),
    ("PH_BienDoiKhiHau", "Bien doi khi hau", "BDKH", 5, 5, 8, 4, 3, 3),
    ("PH_MatDatCanhTac", "Mat dat canh tac", "", 3, 3, 3, 3, 3, 2),
    ("PH_OnhiemMoiTruong", "O nhiem moi truong", "", 3, 3, 5, 3, 2, 3),
    ("PH_ChuyenDichCoCauKT", "Chuyen dich co cau kinh te", "", 3, 4, 10, 4, 3, 3),
    ("PH_DoThiHoa", "Do thi hoa", "", 3, 3, 6, 3, 2, 3),
]

# --- Resources ---
RESOURCES = [
    ("RE_Than", "Than da", "Than", 2, 6, 1, 3),
    ("RE_DauKhi", "Dau mo va khi dot", "Dau khi", 2, 8, 2, 3),
    ("RE_Boxit", "Bo xit", "", 2, 5, 1, 3),
    ("RE_Sat", "Quang sat", "", 2, 4, 1, 3),
    ("RE_Apatit", "A-pa-tit", "Apatit", 1, 3, 1, 3),
    ("RE_DatBazan", "Dat bazan", "", 2, 6, 2, 3),
    ("RE_DatPhuSa", "Dat phu sa", "", 2, 8, 2, 3),
    ("RE_RungNhietDoi", "Rung nhiet doi", "", 3, 6, 2, 3),
    ("RE_RungNganMan", "Rung ngap man", "", 3, 5, 2, 3),
    ("RE_ThuySanBien", "Thuy san bien", "", 3, 8, 2, 3),
    ("RE_ThuySanNuocNgot", "Thuy san nuoc ngot", "", 3, 4, 2, 3),
    ("RE_TiemNangThuyDien", "Tiem nang thuy dien", "Thuy nang", 3, 6, 3, 3),
    ("RE_TiemNangDuLich", "Tiem nang du lich", "", 3, 5, 3, 3),
]

# --- Industries ---
INDUSTRIES = [
    ("I_NongNghiep", "Nong nghiep", "", 2, 20, 2, 3),
    ("I_TrongTrot", "Trong trot", "", 2, 15, 2, 3),
    ("I_ChanNuoi", "Chan nuoi", "", 2, 8, 2, 3),
    ("I_LamNghiep", "Lam nghiep", "", 2, 6, 2, 3),
    ("I_ThuySan", "Thuy san", "Nganh thuy san", 2, 8, 2, 3),
    ("I_CongNghiep", "Cong nghiep", "", 2, 20, 2, 3),
    ("I_CN_KhaiThac", "Cong nghiep khai thac", "", 3, 6, 2, 3),
    ("I_CN_CheBien_LTTP", "Che bien luong thuc thuc pham", "", 3, 8, 2, 3),
    ("I_CN_DetMay", "Det may", "", 3, 6, 2, 3),
    ("I_CN_CoKhi", "Co khi - dien tu", "", 3, 4, 2, 3),
    ("I_CN_HoaChat", "Hoa chat, vat lieu xay dung", "", 3, 5, 2, 3),
    ("I_DichVu", "Dich vu", "", 2, 10, 2, 3),
    ("I_GiaoThong", "Giao thong van tai", "", 2, 8, 2, 3),
    ("I_BuuChinh", "Buu chinh vien thong", "", 2, 4, 2, 3),
    ("I_DuLich", "Du lich", "Nganh du lich", 2, 8, 2, 3),
    ("I_ThuongMai", "Thuong mai (noi thuong, ngoai thuong)", "", 2, 8, 2, 3),
]

# --- Crops ---
CROPS = [
    ("CR_Lua", "Cay lua", "Lua nuoc", 12, 1, 3),
    ("CR_NgoKhoai", "Cay ngo, khoai", "", 5, 1, 3),
    ("CR_CaPhe", "Ca phe", "", 8, 1, 3),
    ("CR_CaoSu", "Cao su", "", 8, 1, 3),
    ("CR_Che", "Che", "", 5, 1, 3),
    ("CR_Dieu", "Dieu", "", 4, 1, 3),
    ("CR_HoTieu", "Ho tieu", "", 4, 1, 3),
    ("CR_CayAnQua", "Cay an qua nhiet doi", "", 5, 2, 3),
    ("CR_CayCongNghiep_NgayNgan", "Cay cong nghiep ngan ngay (lac, mia, dau tuong)", "", 5, 2, 3),
]

# --- Livestock ---
LIVESTOCK = [
    ("LV_TrauBo", "Trau, bo", "", 6, 1, 3),
    ("LV_Lon", "Lon", "", 6, 1, 3),
    ("LV_GiaCam", "Gia cam (ga, vit)", "", 5, 1, 3),
]

# --- Demographic ---
DEMOGRAPHIC = [
    ("DM_MatDoDanSo", "Mat do dan so", "", 8, 3, 2, 3),
    ("DM_TangTruongDanSo", "Tang truong dan so", "", 6, 3, 2, 3),
    ("DM_CoCauDanSoTheoTuoi", "Co cau dan so theo tuoi", "", 5, 4, 3, 3),
    ("DM_CoCauDanToc", "Co cau dan toc (54 dan toc)", "", 5, 3, 2, 3),
    ("DM_ChatLuongCuocSong", "Chat luong cuoc song", "", 4, 4, 3, 3),
    ("DM_PhanBoDanCu", "Phan bo dan cu", "", 8, 4, 3, 3),
    ("DM_LaoDongVaViecLam", "Lao dong va viec lam", "", 6, 4, 3, 3),
]

# --- Concepts ---
CONCEPTS = [
    ("C_VT_DiaLyVN", "Vi tri dia ly Viet Nam", "VTDL", 8, 3, 2, 3),
    ("C_LanhTho", "Lanh tho Viet Nam", "", 5, 3, 2, 3),
    ("C_KinhDoVoiDo", "Kinh do - vi do", "", 4, 3, 2, 3),
    ("C_BanDo", "Ban do va he thong ky hieu", "", 3, 3, 2, 3),
    ("C_GDP", "Tong san pham trong nuoc GDP", "GDP", 5, 4, 3, 3),
    ("C_GDP_BinhQuan", "GDP binh quan dau nguoi", "", 3, 4, 3, 3),
    ("C_NenKinhTeNhieuThanhPhan", "Nen kinh te nhieu thanh phan", "", 3, 4, 3, 3),
    ("C_CNHDH", "Cong nghiep hoa - hien dai hoa", "CNH-HDH", 6, 4, 3, 3),
    ("C_ChuyenDichCoCauLaoDong", "Chuyen dich co cau lao dong", "", 4, 4, 3, 3),
    ("C_HoiNhapKinhTeQT", "Hoi nhap kinh te quoc te", "", 5, 4, 3, 3),
    ("C_PTBenVung", "Phat trien ben vung", "", 4, 5, 3, 3),
]

# --- Processes ---
PROCESSES = [
    ("PR_CongNghiepHoa", "Qua trinh CNH-HDH", "", 4, 8, 3, 3),
    ("PR_DoThiHoa", "Qua trinh do thi hoa", "", 3, 6, 3, 3),
    ("PR_ChuyenDichCoCauKT", "Chuyen dich co cau kinh te", "", 4, 8, 3, 3),
    ("PR_HoiNhapASEAN", "Hoi nhap ASEAN cua VN", "", 4, 4, 3, 3),
    ("PR_HoiNhapQT", "Hoi nhap quoc te, gia nhap WTO", "", 5, 4, 3, 3),
]

print(f"Dia: {len(REGIONS)} regions, {len(NATURAL_FEATURES)} NF, {len(PHENOMENA)} phen, "
      f"{len(RESOURCES)} res, {len(INDUSTRIES)} ind, {len(CROPS)} crops, "
      f"{len(LIVESTOCK)} LV, {len(DEMOGRAPHIC)} demo, {len(CONCEPTS)} concepts, "
      f"{len(PROCESSES)} proc")


# ======================================================================
# LESSONS (bo cu)
# ======================================================================
LESSONS_OLD = [
    # Dia li dan cu
    (1, "Cong dong cac dan toc Viet Nam"),
    (2, "Dan so va gia tang dan so"),
    (3, "Phan bo dan cu va cac loai hinh quan cu"),
    (4, "Lao dong va viec lam. Chat luong cuoc song"),
    # Dia li kinh te chung
    (5, "Qua trinh phat trien kinh te"),
    (6, "Su phat trien nen kinh te Viet Nam"),
    (7, "Cac nhan to anh huong den su phat trien va phan bo nong nghiep"),
    (8, "Su phat trien va phan bo nong nghiep"),
    (9, "Su phat trien va phan bo lam nghiep, thuy san"),
    (10, "Cac nhan to anh huong den su phat trien va phan bo cong nghiep"),
    (11, "Su phat trien va phan bo cong nghiep"),
    (12, "Vai tro, dac diem phat trien va phan bo dich vu"),
    (13, "Giao thong van tai, buu chinh vien thong"),
    (14, "Thuong mai va du lich"),
    # Dia li cac vung kinh te
    (15, "Vung TDMNBB (bai 17 SGK)"),
    (16, "Vung TDMNBB - kinh te"),
    (17, "Vung DBSH - tu nhien, dan cu"),
    (18, "Vung DBSH - kinh te"),
    (19, "Vung BTB - tu nhien, dan cu"),
    (20, "Vung BTB - kinh te"),
    (21, "Vung DHNTB - tu nhien, dan cu"),
    (22, "Vung DHNTB - kinh te"),
    (23, "Vung TN - tu nhien, dan cu"),
    (24, "Vung TN - kinh te"),
    (25, "Vung DNB - tu nhien, dan cu"),
    (26, "Vung DNB - kinh te (tiep)"),
    (27, "Vung DBSCL - tu nhien, dan cu"),
    (28, "Vung DBSCL - kinh te"),
    # Dia li dia phuong + bien dao
    (29, "Phat trien tong hop kinh te va bao ve tai nguyen, moi truong bien dao"),
    (30, "Dia li dia phuong"),
]

LESSONS_KNTT = [(i, f"KNTT Bai {i}") for i in range(1, 26)]
LESSONS_CTST = [(i, f"CTST Bai {i}") for i in range(1, 26)]
LESSONS_CD   = [(i, f"CD Bai {i}") for i in range(1, 26)]


# ======================================================================
# RELATIONSHIPS
# ======================================================================

LOCATED_IN = [
    # Tieu vung -> vung lon
    ("R_DongBac", "R_TDMNBB"),
    ("R_TayBac", "R_TDMNBB"),
    # Thanh pho -> vung
    ("R_HaNoi", "R_DBSH"),
    ("R_HaiPhong", "R_DBSH"),
    ("R_DaNang", "R_DHNTB"),
    ("R_HCM", "R_DNB"),
    ("R_CanTho", "R_DBSCL"),
    # Vung -> VN
    ("R_TDMNBB", "R_VietNam"),
    ("R_DBSH", "R_VietNam"),
    ("R_BTB", "R_VietNam"),
    ("R_DHNTB", "R_VietNam"),
    ("R_TN", "R_VietNam"),
    ("R_DNB", "R_VietNam"),
    ("R_DBSCL", "R_VietNam"),
    # Dao -> vung
    ("R_QuanDaoHoangSa", "R_BienDong"),
    ("R_QuanDaoTruongSa", "R_BienDong"),
    ("R_VinhBacBo", "R_BienDong"),
    # VN -> DNA
    ("R_VietNam", "R_DongNamA"),
]

ADJACENT_TO = [
    ("R_TDMNBB", "R_DBSH"),
    ("R_DBSH", "R_BTB"),
    ("R_BTB", "R_DHNTB"),
    ("R_DHNTB", "R_TN"),
    ("R_TN", "R_DNB"),
    ("R_DNB", "R_DBSCL"),
]

HAS_RESOURCE = [
    ("R_TDMNBB", "RE_Than"),
    ("R_TDMNBB", "RE_Boxit"),
    ("R_TDMNBB", "RE_Apatit"),
    ("R_TDMNBB", "RE_Sat"),
    ("R_TDMNBB", "RE_TiemNangThuyDien"),
    ("R_DBSH", "RE_DatPhuSa"),
    ("R_TN", "RE_DatBazan"),
    ("R_TN", "RE_TiemNangThuyDien"),
    ("R_TN", "RE_RungNhietDoi"),
    ("R_DNB", "RE_DauKhi"),
    ("R_DNB", "RE_DatBazan"),
    ("R_DBSCL", "RE_DatPhuSa"),
    ("R_DBSCL", "RE_ThuySanNuocNgot"),
    ("R_DBSCL", "RE_RungNganMan"),
    ("R_BTB", "RE_ThuySanBien"),
    ("R_DHNTB", "RE_ThuySanBien"),
    ("R_DHNTB", "RE_TiemNangDuLich"),
    ("R_BienDong", "RE_ThuySanBien"),
    ("R_BienDong", "RE_DauKhi"),
]

SPECIALIZES_IN = [
    ("R_TDMNBB", "I_CN_KhaiThac"),
    ("R_TDMNBB", "I_LamNghiep"),
    ("R_DBSH", "I_TrongTrot"),
    ("R_DBSH", "I_CN_CheBien_LTTP"),
    ("R_DBSH", "I_CN_CoKhi"),
    ("R_BTB", "I_LamNghiep"),
    ("R_BTB", "I_ThuySan"),
    ("R_DHNTB", "I_ThuySan"),
    ("R_DHNTB", "I_DuLich"),
    ("R_TN", "I_TrongTrot"),  # ca phe, cao su
    ("R_TN", "I_CongNghiep"),  # thuy dien, che bien
    ("R_DNB", "I_CongNghiep"),
    ("R_DNB", "I_CN_CoKhi"),
    ("R_DNB", "I_CN_HoaChat"),
    ("R_DNB", "I_DichVu"),
    ("R_DBSCL", "I_TrongTrot"),
    ("R_DBSCL", "I_ThuySan"),
    ("R_DBSCL", "I_CN_CheBien_LTTP"),
]

GROWN_IN = [
    ("CR_Lua", "R_DBSH"),
    ("CR_Lua", "R_DBSCL"),
    ("CR_CaPhe", "R_TN"),
    ("CR_CaoSu", "R_DNB"),
    ("CR_CaoSu", "R_TN"),
    ("CR_Che", "R_TDMNBB"),
    ("CR_Dieu", "R_DNB"),
    ("CR_HoTieu", "R_DNB"),
    ("CR_HoTieu", "R_TN"),
    ("CR_CayAnQua", "R_DBSCL"),
    ("CR_CayAnQua", "R_DNB"),
    ("CR_CayCongNghiep_NgayNgan", "R_DBSH"),
    ("CR_CayCongNghiep_NgayNgan", "R_BTB"),
]

RAISED_IN = [
    ("LV_TrauBo", "R_TDMNBB"),
    ("LV_TrauBo", "R_BTB"),
    ("LV_Lon", "R_DBSH"),
    ("LV_Lon", "R_DBSCL"),
    ("LV_GiaCam", "R_DBSH"),
    ("LV_GiaCam", "R_DBSCL"),
]

OCCURS_IN = [
    ("PH_GioMua", "R_VietNam"),
    ("PH_Bao", "R_BTB"),
    ("PH_Bao", "R_DHNTB"),
    ("PH_Lu", "R_DBSCL"),
    ("PH_Lu", "R_BTB"),
    ("PH_HanHan", "R_TN"),
    ("PH_HanHan", "R_DHNTB"),
    ("PH_XamNhapMan", "R_DBSCL"),
]

CAUSES = [
    ("NF_KhiHauNhietDoi", "PH_GioMua"),
    ("PH_GioMua", "PH_Bao"),
    ("PH_BienDoiKhiHau", "PH_XamNhapMan"),
    ("PH_BienDoiKhiHau", "PH_HanHan"),
    ("C_CNHDH", "PR_ChuyenDichCoCauKT"),
    ("C_CNHDH", "PR_DoThiHoa"),
    ("PR_HoiNhapASEAN", "PR_HoiNhapQT"),
]

PREREQUISITES = [
    # VT dia ly -> moi thu khac
    ("C_VT_DiaLyVN", "NF_KhiHauNhietDoi"),
    ("C_VT_DiaLyVN", "C_LanhTho"),
    ("C_KinhDoVoiDo", "C_VT_DiaLyVN"),
    ("C_BanDo", "C_VT_DiaLyVN"),
    # Dan cu
    ("DM_MatDoDanSo", "DM_PhanBoDanCu"),
    ("DM_TangTruongDanSo", "DM_CoCauDanSoTheoTuoi"),
    ("DM_PhanBoDanCu", "DM_LaoDongVaViecLam"),
    ("DM_LaoDongVaViecLam", "DM_ChatLuongCuocSong"),
    # Kinh te chung
    ("C_NenKinhTeNhieuThanhPhan", "C_CNHDH"),
    ("C_CNHDH", "PR_CongNghiepHoa"),
    ("C_CNHDH", "C_ChuyenDichCoCauLaoDong"),
    ("C_ChuyenDichCoCauLaoDong", "PH_ChuyenDichCoCauKT"),
    ("I_NongNghiep", "I_TrongTrot"),
    ("I_NongNghiep", "I_ChanNuoi"),
    ("I_NongNghiep", "I_LamNghiep"),
    ("I_NongNghiep", "I_ThuySan"),
    ("I_CongNghiep", "I_CN_KhaiThac"),
    ("I_CongNghiep", "I_CN_CheBien_LTTP"),
    ("I_CongNghiep", "I_CN_DetMay"),
    ("I_DichVu", "I_GiaoThong"),
    ("I_DichVu", "I_DuLich"),
    ("I_DichVu", "I_ThuongMai"),
    # Vung -> cac vung
    ("R_VietNam", "R_TDMNBB"),
    ("R_VietNam", "R_DBSH"),
    ("R_VietNam", "R_BTB"),
    # Kinh te vung
    ("R_TDMNBB", "I_CN_KhaiThac"),
    ("RE_DatBazan", "CR_CaPhe"),
    ("RE_DatPhuSa", "CR_Lua"),
    ("RE_TiemNangThuyDien", "I_CongNghiep"),
    ("RE_ThuySanBien", "I_ThuySan"),
    # Bien dao
    ("R_BienDong", "R_QuanDaoHoangSa"),
    ("R_BienDong", "R_QuanDaoTruongSa"),
    # Hoi nhap
    ("C_HoiNhapKinhTeQT", "PR_HoiNhapASEAN"),
    ("PR_HoiNhapASEAN", "PR_HoiNhapQT"),
    ("C_PTBenVung", "PH_BienDoiKhiHau"),
    # GDP
    ("C_GDP", "C_GDP_BinhQuan"),
]

SIMILARITIES = [
    ("R_DBSH", "R_DBSCL"),   # 2 dong bang lon
    ("R_TDMNBB", "R_TN"),     # 2 vung cao nguyen/mien nui
    ("R_BTB", "R_DHNTB"),     # 2 vung duyen hai mien Trung
    ("PH_Bao", "PH_Lu"),       # thien tai lien quan
    ("CR_CaPhe", "CR_CaoSu"),  # cay CN lau nam
    ("CR_Lua", "CR_NgoKhoai"), # luong thuc
]

CONTRASTS = [
    ("R_DBSH", "R_TDMNBB"),   # dong bang vs mien nui
    ("R_DNB", "R_DBSCL"),     # cong nghiep vs nong nghiep
    ("R_HaNoi", "R_HCM"),     # 2 do thi
    ("NF_DBSH_Plain", "NF_TruongSon"),
    ("CR_Lua", "CR_CaPhe"),   # luong thuc vs cay CN
]

print(f"  + {len(LOCATED_IN)} locatedIn, {len(ADJACENT_TO)} adjacent, "
      f"{len(HAS_RESOURCE)} hasResource, {len(SPECIALIZES_IN)} specializes, "
      f"{len(GROWN_IN)} grown, {len(RAISED_IN)} raised, {len(OCCURS_IN)} occurs, "
      f"{len(CAUSES)} causes, {len(PREREQUISITES)} prereq, "
      f"{len(SIMILARITIES)} sim, {len(CONTRASTS)} contrast")
