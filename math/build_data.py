"""
Toan 9 ontology generator.

Schema philosophy:
  - Mathematics is LOGICAL, not temporal. Prerequisites encode "you must know X
    before you can prove/use Y".
  - Difficulty in math = (a) depth of logical prerequisite chain,
    (b) number of objects manipulated simultaneously,
    (c) abstractness (numeric -> symbolic -> abstract structures),
    (d) multi-step vs one-step application,
    (e) required reasoning type (compute / prove / counterexample).

Classes (all subClassOf MathEntity):
  - Definition:   toán học định nghĩa một khái niệm
  - Theorem:      mệnh đề đã chứng minh, có thể áp dụng
  - Formula:      công thức tính toán cụ thể
  - Concept:      khái niệm tổng quát (hàm số, đường tròn...)
  - ProblemType:  dạng toán (giải phương trình bậc 2, chứng minh tiếp tuyến...)
  - Method:       phương pháp giải (phương pháp thế, đặt ẩn phụ, Vi-ét...)
  - Object:       đối tượng hình học/đại số cụ thể (tam giác vuông, parabol...)
  - LessonUnit:   bài học trong SGK
  - Textbook:     bộ sách
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent

HEADER = """\
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix math: <http://edu.vn/math9/ontology#> .

<http://edu.vn/math9/ontology> a owl:Ontology ;
    rdfs:label "Ontology Toan 9 - Cold-start Question Difficulty Estimation"@vi ;
    owl:versionInfo "0.1.0" .
"""

SCHEMA = """\
#################################################################
#   CLASSES
#################################################################

math:MathEntity a owl:Class ; rdfs:label "Thuc the Toan hoc"@vi .
math:Definition a owl:Class ; rdfs:subClassOf math:MathEntity ; rdfs:label "Dinh nghia"@vi .
math:Theorem    a owl:Class ; rdfs:subClassOf math:MathEntity ; rdfs:label "Dinh li"@vi .
math:Formula    a owl:Class ; rdfs:subClassOf math:MathEntity ; rdfs:label "Cong thuc"@vi .
math:Concept    a owl:Class ; rdfs:subClassOf math:MathEntity ; rdfs:label "Khai niem"@vi .
math:ProblemType a owl:Class ; rdfs:subClassOf math:MathEntity ; rdfs:label "Dang toan"@vi .
math:Method     a owl:Class ; rdfs:subClassOf math:MathEntity ; rdfs:label "Phuong phap"@vi .
math:Object     a owl:Class ; rdfs:subClassOf math:MathEntity ; rdfs:label "Doi tuong"@vi .
math:LessonUnit a owl:Class ; rdfs:label "Bai hoc SGK"@vi .
math:Textbook   a owl:Class ; rdfs:label "Bo SGK"@vi .

#################################################################
#   OBJECT PROPERTIES
#################################################################

# Logical prerequisite - "to understand X you must know Y"
math:prerequisiteOf a owl:ObjectProperty , owl:TransitiveProperty ;
    rdfs:label "la tien de cua"@vi .

# Theorem uses/depends on other theorems or definitions
math:uses a owl:ObjectProperty ; rdfs:label "su dung"@vi .
math:provedUsing a owl:ObjectProperty ; rdfs:subPropertyOf math:uses ; rdfs:label "chung minh bang"@vi .

# Method solves ProblemType
math:solves a owl:ObjectProperty ;
    rdfs:domain math:Method ; rdfs:range math:ProblemType ;
    rdfs:label "giai duoc dang"@vi .

# Formula computes a quantity of an Object
math:appliesTo a owl:ObjectProperty ;
    rdfs:domain math:Formula ; rdfs:range math:Object ;
    rdfs:label "ap dung cho"@vi .

# Generalization / specialization
math:generalizes a owl:ObjectProperty ; rdfs:label "tong quat hoa"@vi .
math:specialCaseOf a owl:ObjectProperty ; owl:inverseOf math:generalizes ; rdfs:label "truong hop dac biet cua"@vi .

# Curriculum
math:appearsInLesson a owl:ObjectProperty ; rdfs:range math:LessonUnit ; rdfs:label "xuat hien trong bai"@vi .
math:partOfTextbook a owl:ObjectProperty ; rdfs:range math:Textbook ; rdfs:label "thuoc bo SGK"@vi .

# Similarity for comparison questions
math:similarTo a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "tuong tu"@vi .
math:contrastsWith a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "doi lap"@vi .

#################################################################
#   DATA PROPERTIES
#################################################################

math:abstractness a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "1=cu the (so cu the, hinh ve), 5=rat truu tuong (bat ki, tong quat)"@vi .
math:bloomLevel a owl:DatatypeProperty ; rdfs:range xsd:integer .
math:symbolicDensity a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "So luong ky hieu / bien / thong so trong cong thuc (1-5)"@vi .
math:applicationSteps a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "So buoc trung binh de ap dung cong thuc/phuong phap (1-5)"@vi .
math:reasoningType a owl:DatatypeProperty ; rdfs:range xsd:string ;
    rdfs:comment "compute | prove | construct | counterexample | analyze"@vi .
math:frequencyInTextbook a owl:DatatypeProperty ; rdfs:range xsd:integer .
math:curriculumPosition a owl:DatatypeProperty ; rdfs:range xsd:integer .
math:aliases a owl:DatatypeProperty ; rdfs:range xsd:string .
math:confidence a owl:DatatypeProperty ; rdfs:range xsd:integer .

#################################################################
#   TEXTBOOKS
#################################################################

math:TB_Old a math:Textbook ; rdfs:label "SGK Toan 9 (bo cu)"@vi ; math:confidence 3 .
math:TB_KNTT a math:Textbook ; rdfs:label "SGK Toan 9 - Ket noi tri thuc"@vi ; math:confidence 3 .
math:TB_CTST a math:Textbook ; rdfs:label "SGK Toan 9 - Chan troi sang tao"@vi ; math:confidence 3 .
math:TB_CD a math:Textbook ; rdfs:label "SGK Toan 9 - Canh Dieu"@vi ; math:confidence 3 .
"""

# ======================================================================
# DATA
# ======================================================================

# --- DEFINITIONS ---
DEFINITIONS = [
    # id, label, aliases, abstractness, conf
    ("D_CanBacHai", "Can bac hai cua so khong am", "Can bac 2", 3, 3),
    ("D_CanBacHaiSoHoc", "Can bac hai so hoc", "", 3, 3),
    ("D_HamSoBacNhat", "Ham so bac nhat y=ax+b", "", 3, 3),
    ("D_HamSoBac2", "Ham so bac hai y=ax^2 (a khac 0)", "", 3, 3),
    ("D_HeSoGoc", "He so goc cua duong thang", "", 3, 3),
    ("D_PhuongTrinhBac2", "Phuong trinh bac hai mot an", "PT bac 2", 3, 3),
    ("D_HePhuongTrinh", "He hai phuong trinh bac nhat hai an", "", 3, 3),
    ("D_Parabol", "Parabol y=ax^2", "", 3, 3),
    ("D_DuongTron", "Duong tron", "", 2, 3),
    ("D_TiepTuyen", "Tiep tuyen cua duong tron", "", 3, 3),
    ("D_CungTron", "Cung tron", "", 2, 3),
    ("D_DayCung", "Day cung cua duong tron", "", 2, 3),
    ("D_GocNoiTiep", "Goc noi tiep", "", 3, 3),
    ("D_GocOTam", "Goc o tam", "", 3, 3),
    ("D_TuGiacNoiTiep", "Tu giac noi tiep", "", 3, 3),
    ("D_HinhTru", "Hinh tru", "", 2, 3),
    ("D_HinhNon", "Hinh non", "", 2, 3),
    ("D_HinhCau", "Hinh cau", "", 2, 3),
    ("D_CungChuong", "Cung chuong", "", 3, 3),
    ("D_Biet_PTB2", "Biet thuc delta cua PT bac 2", "Delta", 3, 3),
]

# --- THEOREMS ---
THEOREMS = [
    # id, label, aliases, abstractness, bloom, conf
    ("T_Pythagoras", "Dinh li Pythagoras (toan 8, nhac lai)", "Pi-ta-go", 3, 2, 3),
    ("T_Thales", "Dinh li Ta-let", "Thales", 3, 2, 3),
    ("T_ThalesDaoNguoc", "Dinh li Ta-let dao nguoc", "", 3, 3, 3),
    ("T_VietaQuan", "Dinh li Vi-et", "Vi-et thuan", 4, 3, 3),
    ("T_VietaDao", "Dinh li Vi-et dao", "", 4, 3, 3),
    ("T_TTHamSoBacNhat", "Tinh chat ham so bac nhat", "", 3, 2, 3),
    ("T_TTHamSoBac2", "Tinh chat ham so bac 2", "", 3, 2, 3),
    ("T_HeThucLuong", "He thuc luong trong tam giac vuong", "HSL", 4, 3, 3),
    ("T_TTTiepTuyen", "Tinh chat hai tiep tuyen cat nhau", "", 3, 2, 3),
    ("T_LienHeCungVaDay", "Lien he giua cung va day", "", 3, 2, 3),
    ("T_GocNoiTiep_TT", "Dinh li goc noi tiep", "", 4, 3, 3),
    ("T_GocTaoBoiTTVaDay", "Goc tao boi tiep tuyen va day cung", "", 4, 3, 3),
    ("T_GocCoDinhONgoaiHinhTron", "Goc co dinh ngoai duong tron", "", 4, 3, 2),
    ("T_TuGiacNoiTiepDK", "Dieu kien tu giac noi tiep", "", 4, 3, 3),
    ("T_DuongTronNoiTiep", "Dinh li duong tron noi tiep da giac deu", "", 3, 2, 3),
    ("T_DiaLuongCan", "Quy tac nhan/chia can bac hai", "", 3, 2, 3),
    ("T_Lien_HamSo_Parabol", "Vi tri tuong doi duong thang - parabol", "", 4, 3, 3),
    ("T_DK_PTB2_CoNghiem", "Dieu kien co nghiem cua PT bac 2", "delta >= 0", 3, 2, 3),
]

# --- FORMULAS ---
FORMULAS = [
    # id, label, aliases, symbolic_density, steps, abstractness, conf
    ("F_Delta", "Delta = b^2 - 4ac", "", 3, 1, 3, 3),
    ("F_NghiemPTB2", "Nghiem x = (-b ± sqrt(Delta)) / 2a", "", 4, 2, 3, 3),
    ("F_VietaTong", "Tong nghiem S = -b/a", "Vi-et tong", 2, 1, 3, 3),
    ("F_VietaTich", "Tich nghiem P = c/a", "Vi-et tich", 2, 1, 3, 3),
    ("F_DoDaiCung", "Do dai cung l = pi*R*n/180", "", 4, 2, 3, 3),
    ("F_DienTichHinhQuat", "Dien tich hinh quat S = pi*R^2*n/360", "", 4, 2, 3, 3),
    ("F_ChuViDuongTron", "Chu vi duong tron C = 2*pi*R", "", 2, 1, 2, 3),
    ("F_DienTichHinhTron", "Dien tich hinh tron S = pi*R^2", "", 2, 1, 2, 3),
    ("F_DTXQHinhTru", "Dien tich xung quanh hinh tru S_xq = 2*pi*R*h", "", 3, 1, 3, 3),
    ("F_TheTichHinhTru", "The tich hinh tru V = pi*R^2*h", "", 3, 1, 3, 3),
    ("F_DTXQHinhNon", "Dien tich xung quanh hinh non S_xq = pi*R*l", "", 3, 1, 3, 3),
    ("F_TheTichHinhNon", "The tich hinh non V = (1/3)*pi*R^2*h", "", 4, 1, 3, 3),
    ("F_DienTichHinhCau", "Dien tich mat cau S = 4*pi*R^2", "", 3, 1, 3, 3),
    ("F_TheTichHinhCau", "The tich hinh cau V = (4/3)*pi*R^3", "", 4, 1, 3, 3),
    ("F_HSL_BinhPhuong_TGV", "b^2 = a*b', c^2 = a*c' (HSL trong TGV)", "", 3, 2, 3, 3),
    ("F_HSL_DuongCao_TGV", "h^2 = b'*c' (HSL trong TGV)", "", 3, 2, 3, 3),
    ("F_HamSoBacNhat", "y = ax + b", "", 2, 1, 3, 3),
    ("F_HamSoBac2_DonGian", "y = ax^2", "", 2, 1, 3, 3),
    ("F_KhoangCach2Diem", "d = sqrt((x1-x2)^2 + (y1-y2)^2)", "", 4, 2, 3, 3),
]

# --- CONCEPTS ---
CONCEPTS = [
    # id, label, aliases, abstractness, bloom, conf
    ("C_SoThuc", "So thuc", "", 3, 1, 3),
    ("C_SoVoTi", "So vo ti", "", 4, 2, 3),
    ("C_HamSo", "Ham so", "", 4, 2, 3),
    ("C_DoThiHamSo", "Do thi ham so", "", 3, 2, 3),
    ("C_HamSoDongBien", "Ham so dong bien", "", 3, 2, 3),
    ("C_HamSoNghichBien", "Ham so nghich bien", "", 3, 2, 3),
    ("C_HeTrucToaDo", "He truc toa do Oxy", "", 2, 2, 3),
    ("C_NghiemPT", "Nghiem cua phuong trinh", "", 3, 2, 3),
    ("C_DongQui", "Ba duong thang dong qui", "", 3, 3, 2),
    ("C_CanhGocQuanHe_TGV", "Quan he canh-goc trong TGV", "", 3, 2, 3),
    ("C_DuongCao_TGV", "Duong cao trong tam giac vuong", "", 2, 2, 3),
    ("C_VTDT_VoiDuongTron", "Vi tri tuong doi cua duong thang va duong tron", "VTDT-DT", 3, 2, 3),
    ("C_VT2DuongTron", "Vi tri tuong doi cua hai duong tron", "", 3, 2, 3),
    ("C_DuongTronNoiTiep_DaGiac", "Duong tron noi/ngoai tiep da giac", "", 3, 3, 3),
    ("C_TamGiacNoiTiep", "Tam giac noi tiep duong tron", "", 3, 3, 3),
    ("C_DaGiacDeu", "Da giac deu", "", 3, 2, 3),
    ("C_HinhLangTru", "Hinh lang tru dung (nhac lai)", "", 2, 2, 3),
    ("C_ThetichKhoi_TronXoay", "The tich khoi tron xoay", "", 4, 3, 2),
]

# --- METHODS (phuong phap giai) ---
METHODS = [
    # id, label, aliases, steps, abstractness, bloom, conf
    ("M_KhaiCan", "Khai phuong tich, thuong", "", 2, 3, 2, 3),
    ("M_TrucCanMau", "Truc can thuc o mau", "", 3, 3, 2, 3),
    ("M_HeThePPThe", "Phuong phap the (giai he PT)", "PP the", 3, 3, 3, 3),
    ("M_HeThePPCong", "Phuong phap cong dai so (giai he PT)", "PP cong", 3, 3, 3, 3),
    ("M_DatAnPhu", "Dat an phu", "", 4, 4, 3, 3),
    ("M_VietaNhamNghiem", "Nham nghiem bang Vi-et", "", 3, 3, 3, 3),
    ("M_VeDoThiParabol", "Ve do thi parabol", "", 3, 3, 2, 3),
    ("M_VeDoThiDTB1", "Ve do thi ham so bac nhat", "", 2, 3, 2, 3),
    ("M_TimDieuKienDinhTH", "Tim dieu kien co nghiem/nghiem chung", "", 4, 4, 3, 3),
    ("M_ChungMinhTiepTuyen", "Chung minh duong thang la tiep tuyen", "", 3, 3, 3, 3),
    ("M_ChungMinhTuGiacNoiTiep", "Chung minh tu giac noi tiep", "", 4, 4, 3, 3),
    ("M_ChungMinhDongQui", "Chung minh 3 diem thang hang / 3 duong dong qui", "", 4, 4, 4, 3),
    ("M_TinhGoc_DuongTron", "Tinh goc lien quan duong tron", "", 3, 3, 3, 3),
    ("M_TinhDienTich_HinhKhongGian", "Tinh dien tich/the tich hinh khong gian", "", 3, 3, 2, 3),
    ("M_GiaiToanThucTe", "Giai bai toan thuc te bang PT/HPT", "", 4, 3, 3, 3),
]

# --- PROBLEM TYPES (dang toan) ---
PROBLEM_TYPES = [
    # id, label, aliases, abstractness, bloom, conf
    ("PT_RutGonBieuThucCan", "Rut gon bieu thuc chua can", "", 3, 3, 3),
    ("PT_GiaiPTVoCan", "Giai phuong trinh vo ti (co can)", "PT chua can", 4, 3, 3),
    ("PT_GiaiHPTBac1_2An", "Giai he phuong trinh bac nhat 2 an", "HPT bac 1", 3, 2, 3),
    ("PT_GiaiPTBac2", "Giai phuong trinh bac hai", "", 3, 2, 3),
    ("PT_TrungGianQuaPhuongTrinhBac2", "Dua ve PT bac 2 (trung gian)", "", 4, 3, 3),
    ("PT_BieuDienDoThi", "Ve do thi va xac dinh vi tri tuong doi", "", 3, 3, 3),
    ("PT_TimCucTriBang_BieuThuc", "Tim GTLN-GTNN cua bieu thuc", "GTLN GTNN", 5, 4, 3),
    ("PT_DinhLyHamSoBacNhat", "Bai toan ve ham so bac nhat", "", 3, 3, 3),
    ("PT_DinhLyHamSoBac2", "Bai toan ve ham so bac hai va parabol", "", 4, 3, 3),
    ("PT_DinhLyTimThamSo", "Tim tham so de PT thoa dieu kien", "", 5, 4, 3),
    ("PT_BaiToanThucTe", "Giai bai toan bang cach lap PT/HPT", "", 4, 3, 3),
    ("PT_ChungMinhHinhHoc_DuongTron", "Chung minh hinh hoc lien quan duong tron", "", 4, 3, 3),
    ("PT_TinhGoc_TamGiac_DuongTron", "Tinh goc/do dai trong tam giac va duong tron", "", 3, 3, 3),
    ("PT_TinhHinhKhongGian", "Tinh dai luong hinh tru, non, cau", "", 3, 2, 3),
    ("PT_ChungMinh_TQNoi", "Chung minh tu giac noi tiep duong tron", "", 4, 3, 3),
]

# --- OBJECTS (doi tuong hinh hoc/dai so) ---
OBJECTS = [
    ("O_TamGiacVuong", "Tam giac vuong", "TGV", 2, 3),
    ("O_DuongTron_DT", "Duong tron cu the", "", 2, 3),
    ("O_HinhTron", "Hinh tron", "", 2, 3),
    ("O_DuongThang_2D", "Duong thang trong mat phang", "", 2, 3),
    ("O_Parabol_DT", "Parabol cu the", "", 3, 3),
    ("O_TuGiac", "Tu giac", "", 2, 3),
    ("O_HinhTru_DT", "Hinh tru cu the", "", 2, 3),
    ("O_HinhNon_DT", "Hinh non cu the", "", 2, 3),
    ("O_HinhCau_DT", "Hinh cau cu the", "", 2, 3),
    ("O_BieuThucCan", "Bieu thuc chua can", "", 3, 3),
]

print(f"Toan: {len(DEFINITIONS)} defs, {len(THEOREMS)} theorems, {len(FORMULAS)} formulas, "
      f"{len(CONCEPTS)} concepts, {len(METHODS)} methods, {len(PROBLEM_TYPES)} problem types, "
      f"{len(OBJECTS)} objects")


# ======================================================================
# LESSON UNITS (approximated - needs verification)
# ======================================================================
LESSONS_OLD = [
    # Chuong I: Can bac hai
    (1, "Can bac hai"), (2, "Can thuc bac hai va hang dang thuc"),
    (3, "Lien he phep nhan - phep khai phuong"), (4, "Lien he phep chia - phep khai phuong"),
    (5, "Bien doi don gian bieu thuc chua can"), (6, "Rut gon bieu thuc chua can thuc bac hai"),
    # Chuong II: Ham so bac nhat
    (7, "Nhac lai, bo sung khai niem ham so"), (8, "Ham so bac nhat"),
    (9, "Do thi ham so y=ax+b"), (10, "Duong thang song song, duong thang cat nhau"),
    (11, "He so goc cua duong thang y=ax+b"),
    # Chuong III: He PT bac nhat 2 an
    (12, "Phuong trinh bac nhat hai an"), (13, "He hai PT bac nhat hai an"),
    (14, "Giai he PT bang pp the"), (15, "Giai he PT bang pp cong dai so"),
    (16, "Giai bai toan bang cach lap he PT"),
    # Chuong IV: Ham so y=ax^2, PT bac 2
    (17, "Ham so y=ax^2 (a khac 0)"), (18, "Do thi ham so y=ax^2"),
    (19, "Phuong trinh bac 2 mot an"), (20, "Cong thuc nghiem cua PT bac 2"),
    (21, "He thuc Vi-et va ung dung"), (22, "PT qui ve PT bac 2"),
    (23, "Giai bai toan bang cach lap PT"),
    # Hinh hoc - Chuong I: He thuc luong
    (24, "He thuc luong trong tam giac vuong"), (25, "Ty so luong giac goc nhon"),
    # Hinh hoc - Chuong II: Duong tron
    (26, "Su xac dinh duong tron"), (27, "Duong kinh va day cua duong tron"),
    (28, "Lien he day va khoang cach den tam"), (29, "Vi tri tuong doi cua duong thang va duong tron"),
    (30, "Dau hieu nhan biet tiep tuyen"), (31, "Tinh chat hai tiep tuyen cat nhau"),
    (32, "Vi tri tuong doi cua hai duong tron"),
    # Hinh hoc - Chuong III: Goc va duong tron
    (33, "Goc o tam, so do cung"), (34, "Lien he cung va day"),
    (35, "Goc noi tiep"), (36, "Goc tao boi tia tiep tuyen va day cung"),
    (37, "Goc co dinh ben trong/ngoai duong tron"), (38, "Cung chua goc"),
    (39, "Tu giac noi tiep"), (40, "Duong tron ngoai/noi tiep da giac deu"),
    (41, "Do dai duong tron, cung tron"), (42, "Dien tich hinh tron, hinh quat"),
    # Hinh hoc - Chuong IV: Hinh tru, non, cau
    (43, "Hinh tru, dien tich xung quanh, the tich"),
    (44, "Hinh non, hinh non cut"),
    (45, "Hinh cau, dien tich mat cau, the tich"),
]

# New textbook series - approximated, needs verification
LESSONS_KNTT = [(i, f"KNTT Bai {i}") for i in range(1, 36)]  # placeholder
LESSONS_CTST = [(i, f"CTST Bai {i}") for i in range(1, 36)]
LESSONS_CD   = [(i, f"CD Bai {i}") for i in range(1, 36)]


# ======================================================================
# RELATIONSHIPS - the critical part for difficulty
# ======================================================================

# Prerequisite chains
PREREQUISITES = [
    # Can bac hai
    ("D_CanBacHai", "D_CanBacHaiSoHoc"),
    ("D_CanBacHaiSoHoc", "T_DiaLuongCan"),
    ("T_DiaLuongCan", "M_KhaiCan"),
    ("M_KhaiCan", "M_TrucCanMau"),
    ("M_TrucCanMau", "PT_RutGonBieuThucCan"),
    ("PT_RutGonBieuThucCan", "PT_GiaiPTVoCan"),
    # Ham so bac nhat
    ("C_HamSo", "D_HamSoBacNhat"),
    ("D_HamSoBacNhat", "T_TTHamSoBacNhat"),
    ("T_TTHamSoBacNhat", "D_HeSoGoc"),
    ("D_HamSoBacNhat", "F_HamSoBacNhat"),
    ("F_HamSoBacNhat", "M_VeDoThiDTB1"),
    ("M_VeDoThiDTB1", "PT_DinhLyHamSoBacNhat"),
    # He PT
    ("D_HamSoBacNhat", "D_HePhuongTrinh"),
    ("D_HePhuongTrinh", "M_HeThePPThe"),
    ("D_HePhuongTrinh", "M_HeThePPCong"),
    ("M_HeThePPThe", "PT_GiaiHPTBac1_2An"),
    ("M_HeThePPCong", "PT_GiaiHPTBac1_2An"),
    ("PT_GiaiHPTBac1_2An", "PT_BaiToanThucTe"),
    # Ham so bac 2, PT bac 2
    ("D_HamSoBac2", "D_Parabol"),
    ("D_Parabol", "F_HamSoBac2_DonGian"),
    ("F_HamSoBac2_DonGian", "M_VeDoThiParabol"),
    ("M_VeDoThiParabol", "T_Lien_HamSo_Parabol"),
    ("D_HamSoBac2", "D_PhuongTrinhBac2"),
    ("D_PhuongTrinhBac2", "D_Biet_PTB2"),
    ("D_Biet_PTB2", "F_Delta"),
    ("F_Delta", "F_NghiemPTB2"),
    ("F_NghiemPTB2", "PT_GiaiPTBac2"),
    ("F_NghiemPTB2", "T_DK_PTB2_CoNghiem"),
    ("T_DK_PTB2_CoNghiem", "PT_DinhLyTimThamSo"),
    ("PT_GiaiPTBac2", "PT_TrungGianQuaPhuongTrinhBac2"),
    ("T_VietaQuan", "F_VietaTong"),
    ("T_VietaQuan", "F_VietaTich"),
    ("F_VietaTong", "M_VietaNhamNghiem"),
    ("F_VietaTich", "M_VietaNhamNghiem"),
    ("M_VietaNhamNghiem", "PT_DinhLyTimThamSo"),
    ("T_Lien_HamSo_Parabol", "PT_DinhLyHamSoBac2"),
    # He thuc luong trong TGV
    ("T_Pythagoras", "T_HeThucLuong"),
    ("T_HeThucLuong", "F_HSL_BinhPhuong_TGV"),
    ("T_HeThucLuong", "F_HSL_DuongCao_TGV"),
    # Duong tron
    ("D_DuongTron", "D_CungTron"),
    ("D_DuongTron", "D_DayCung"),
    ("D_DayCung", "T_LienHeCungVaDay"),
    ("D_DuongTron", "D_TiepTuyen"),
    ("D_TiepTuyen", "T_TTTiepTuyen"),
    ("T_TTTiepTuyen", "M_ChungMinhTiepTuyen"),
    ("D_DuongTron", "C_VTDT_VoiDuongTron"),
    ("C_VTDT_VoiDuongTron", "M_ChungMinhTiepTuyen"),
    ("D_DuongTron", "C_VT2DuongTron"),
    # Goc va duong tron
    ("D_CungTron", "D_GocOTam"),
    ("D_GocOTam", "D_GocNoiTiep"),
    ("D_GocNoiTiep", "T_GocNoiTiep_TT"),
    ("T_GocNoiTiep_TT", "T_GocTaoBoiTTVaDay"),
    ("T_GocNoiTiep_TT", "M_TinhGoc_DuongTron"),
    ("M_TinhGoc_DuongTron", "PT_TinhGoc_TamGiac_DuongTron"),
    ("D_TuGiacNoiTiep", "T_TuGiacNoiTiepDK"),
    ("T_TuGiacNoiTiepDK", "M_ChungMinhTuGiacNoiTiep"),
    ("M_ChungMinhTuGiacNoiTiep", "PT_ChungMinh_TQNoi"),
    ("T_GocNoiTiep_TT", "M_ChungMinhTuGiacNoiTiep"),
    # Hinh tru, non, cau
    ("D_HinhTru", "F_DTXQHinhTru"),
    ("D_HinhTru", "F_TheTichHinhTru"),
    ("D_HinhNon", "F_DTXQHinhNon"),
    ("D_HinhNon", "F_TheTichHinhNon"),
    ("D_HinhCau", "F_DienTichHinhCau"),
    ("D_HinhCau", "F_TheTichHinhCau"),
    ("F_TheTichHinhTru", "M_TinhDienTich_HinhKhongGian"),
    ("M_TinhDienTich_HinhKhongGian", "PT_TinhHinhKhongGian"),
    # Chu vi, dien tich duong tron
    ("D_DuongTron", "F_ChuViDuongTron"),
    ("D_DuongTron", "F_DienTichHinhTron"),
    ("F_ChuViDuongTron", "F_DoDaiCung"),
    ("F_DienTichHinhTron", "F_DienTichHinhQuat"),
    # Cross-domain: bai toan thuc te
    ("M_GiaiToanThucTe", "PT_BaiToanThucTe"),
]

# Uses relationships (theorem uses other theorems for proof)
USES = [
    ("T_VietaDao", "T_VietaQuan"),
    ("T_HeThucLuong", "T_Pythagoras"),
    ("T_GocTaoBoiTTVaDay", "T_GocNoiTiep_TT"),
    ("F_NghiemPTB2", "F_Delta"),
    ("F_VietaTong", "F_NghiemPTB2"),
    ("F_VietaTich", "F_NghiemPTB2"),
    ("T_TTTiepTuyen", "D_TiepTuyen"),
]

# Method solves ProblemType
SOLVES = [
    ("M_HeThePPThe", "PT_GiaiHPTBac1_2An"),
    ("M_HeThePPCong", "PT_GiaiHPTBac1_2An"),
    ("M_DatAnPhu", "PT_TrungGianQuaPhuongTrinhBac2"),
    ("M_DatAnPhu", "PT_GiaiPTVoCan"),
    ("M_VietaNhamNghiem", "PT_GiaiPTBac2"),
    ("M_VietaNhamNghiem", "PT_DinhLyTimThamSo"),
    ("M_TrucCanMau", "PT_RutGonBieuThucCan"),
    ("M_VeDoThiParabol", "PT_DinhLyHamSoBac2"),
    ("M_VeDoThiDTB1", "PT_DinhLyHamSoBacNhat"),
    ("M_ChungMinhTiepTuyen", "PT_ChungMinhHinhHoc_DuongTron"),
    ("M_ChungMinhTuGiacNoiTiep", "PT_ChungMinh_TQNoi"),
    ("M_TinhGoc_DuongTron", "PT_TinhGoc_TamGiac_DuongTron"),
    ("M_TinhDienTich_HinhKhongGian", "PT_TinhHinhKhongGian"),
    ("M_GiaiToanThucTe", "PT_BaiToanThucTe"),
]

# Formula applies to Object
APPLIES_TO = [
    ("F_HSL_BinhPhuong_TGV", "O_TamGiacVuong"),
    ("F_HSL_DuongCao_TGV", "O_TamGiacVuong"),
    ("F_ChuViDuongTron", "O_DuongTron_DT"),
    ("F_DienTichHinhTron", "O_HinhTron"),
    ("F_DoDaiCung", "O_DuongTron_DT"),
    ("F_DienTichHinhQuat", "O_HinhTron"),
    ("F_DTXQHinhTru", "O_HinhTru_DT"),
    ("F_TheTichHinhTru", "O_HinhTru_DT"),
    ("F_DTXQHinhNon", "O_HinhNon_DT"),
    ("F_TheTichHinhNon", "O_HinhNon_DT"),
    ("F_DienTichHinhCau", "O_HinhCau_DT"),
    ("F_TheTichHinhCau", "O_HinhCau_DT"),
    ("F_HamSoBacNhat", "O_DuongThang_2D"),
    ("F_HamSoBac2_DonGian", "O_Parabol_DT"),
]

# Similarity & contrast
SIMILARITIES = [
    ("M_HeThePPThe", "M_HeThePPCong"),       # 2 pp giai he PT
    ("F_VietaTong", "F_VietaTich"),           # 2 he thuc Vi-et
    ("D_HinhTru", "D_HinhNon"),                # 2 hinh khoi tron xoay
    ("T_Thales", "T_ThalesDaoNguoc"),
]
CONTRASTS = [
    ("C_HamSoDongBien", "C_HamSoNghichBien"),
    ("M_HeThePPThe", "M_HeThePPCong"),  # same problem but different approach
]

print(f"  + {len(PREREQUISITES)} prereq, {len(USES)} uses, {len(SOLVES)} solves, "
      f"{len(APPLIES_TO)} applies, {len(SIMILARITIES)} similar, {len(CONTRASTS)} contrast")
