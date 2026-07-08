"""
Programmatic generator for the expanded Su9 ontology (v0.2).

Why Python instead of hand-writing TTL: 350+ entities with rich metadata
(multi-textbook lesson mapping, confidence flags, prerequisite chains) are
much easier to review as dicts. This script emits the canonical Turtle file.

Confidence levels (data property su9:confidence, 1-3):
  3 = well-established historical fact (dates, major events, key figures)
  2 = ontology metadata I'm reasonably confident about (Bloom level, abstractness)
  1 = needs teacher verification (frequencyInTextbook, appearsInLesson for new textbook series)

Usage:
    python3 build_ontology.py
    -> writes ontology/su9.ttl (overwrites v0.1)
    -> also regenerates su9.owl for Protege
"""

from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent
OUT_TTL = ROOT / "ontology" / "su9.ttl"
OUT_OWL = ROOT / "ontology" / "su9.owl"


# ======================================================================
# HEADER & SCHEMA
# ======================================================================

HEADER = """\
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix su9:  <http://su9.edu.vn/ontology#> .

<http://su9.edu.vn/ontology> a owl:Ontology ;
    rdfs:label "Ontology Lich su 9 - Cold-start Question Difficulty Estimation (v0.2)"@vi ;
    rdfs:comment "Expanded domain ontology for 9th-grade History, multi-textbook-aware."@en ;
    owl:versionInfo "0.2.0" .
"""

SCHEMA = """\
#################################################################
#   CLASSES
#################################################################

su9:HistoricalEntity a owl:Class ; rdfs:label "Thuc the lich su"@vi .
su9:Event a owl:Class ; rdfs:subClassOf su9:HistoricalEntity ; rdfs:label "Su kien"@vi .
su9:Person a owl:Class ; rdfs:subClassOf su9:HistoricalEntity ; rdfs:label "Nhan vat"@vi .
su9:Location a owl:Class ; rdfs:subClassOf su9:HistoricalEntity ; rdfs:label "Dia diem"@vi .
su9:Period a owl:Class ; rdfs:subClassOf su9:HistoricalEntity ; rdfs:label "Thoi ky"@vi .
su9:Organization a owl:Class ; rdfs:subClassOf su9:HistoricalEntity ; rdfs:label "To chuc"@vi .
su9:Movement a owl:Class ; rdfs:subClassOf su9:HistoricalEntity ; rdfs:label "Phong trao"@vi .
su9:Document a owl:Class ; rdfs:subClassOf su9:HistoricalEntity ; rdfs:label "Van kien / Hiep dinh"@vi .
su9:Concept a owl:Class ; rdfs:subClassOf su9:HistoricalEntity ; rdfs:label "Khai niem lich su"@vi .
su9:LessonUnit a owl:Class ; rdfs:label "Bai hoc trong SGK"@vi .
su9:Textbook a owl:Class ; rdfs:label "Bo sach giao khoa"@vi .

#################################################################
#   OBJECT PROPERTIES
#################################################################

su9:occursAt a owl:ObjectProperty ; rdfs:domain su9:Event ; rdfs:range su9:Location ; rdfs:label "dien ra tai"@vi .
su9:occursDuring a owl:ObjectProperty ; rdfs:domain su9:Event ; rdfs:range su9:Period ; rdfs:label "dien ra trong thoi ky"@vi .
su9:participatesIn a owl:ObjectProperty ; rdfs:domain su9:Person ; rdfs:range su9:Event ; rdfs:label "tham gia"@vi .
su9:leads a owl:ObjectProperty ; rdfs:subPropertyOf su9:participatesIn ; rdfs:label "lanh dao"@vi .
su9:causes a owl:ObjectProperty ; rdfs:label "la nguyen nhan cua"@vi .
su9:directCause a owl:ObjectProperty ; rdfs:subPropertyOf su9:causes ; rdfs:label "nguyen nhan truc tiep"@vi .
su9:deepCause a owl:ObjectProperty ; rdfs:subPropertyOf su9:causes ; rdfs:label "nguyen nhan sau xa"@vi .
su9:resultsFrom a owl:ObjectProperty ; owl:inverseOf su9:causes ; rdfs:label "la ket qua cua"@vi .
su9:prerequisiteOf a owl:ObjectProperty , owl:TransitiveProperty ; rdfs:label "la tien de cua"@vi .
su9:similarTo a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "tuong dong voi"@vi .
su9:contrastsWith a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "doi lap voi"@vi .
su9:belongsToLesson a owl:ObjectProperty ; rdfs:range su9:LessonUnit ; rdfs:label "thuoc bai"@vi .
su9:appearsInLesson a owl:ObjectProperty ; rdfs:range su9:LessonUnit ; rdfs:label "xuat hien trong bai"@vi ;
    rdfs:comment "Many-to-many, one entity can appear in multiple lessons across textbooks."@en .
su9:partOfTextbook a owl:ObjectProperty ; rdfs:range su9:Textbook ; rdfs:label "thuoc bo SGK"@vi .
su9:derivesFrom a owl:ObjectProperty , owl:TransitiveProperty ; rdfs:label "ke thua tu"@vi .
su9:signed a owl:ObjectProperty ; rdfs:domain su9:Person ; rdfs:range su9:Document ; rdfs:label "ky ket"@vi .
su9:locatedIn a owl:ObjectProperty , owl:TransitiveProperty ; rdfs:domain su9:Location ; rdfs:range su9:Location ; rdfs:label "nam trong"@vi .
su9:memberOf a owl:ObjectProperty ; rdfs:domain su9:Person ; rdfs:range su9:Organization ; rdfs:label "thanh vien cua"@vi .
su9:involvedConcept a owl:ObjectProperty ; rdfs:label "lien quan den khai niem"@vi .

#################################################################
#   DATA PROPERTIES
#################################################################

su9:bloomLevel a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "muc do Bloom"@vi ;
    rdfs:comment "1=Biet, 2=Hieu, 3=Van dung, 4=Van dung cao."@vi .
su9:abstractness a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "do truu tuong 1-5"@vi .
su9:frequencyInTextbook a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "tan suat SGK (estimate)"@vi .
su9:curriculumPosition a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "vi tri chuong trinh"@vi .
su9:startYear a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "nam bat dau"@vi .
su9:endYear a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "nam ket thuc"@vi .
su9:aliases a owl:DatatypeProperty ; rdfs:range xsd:string ; rdfs:label "ten goi khac (cach nhau |)"@vi .
su9:confidence a owl:DatatypeProperty ; rdfs:range xsd:integer ; rdfs:label "do tin cay 1-3"@vi ;
    rdfs:comment "3=chac chan, 2=hop ly, 1=can giao vien kiem tra."@vi .

#################################################################
#   TEXTBOOKS (Bo SGK)
#################################################################

su9:TB_Old a su9:Textbook ;
    rdfs:label "SGK Lich su 9 (bo cu, truoc 2021)"@vi ;
    su9:aliases "Bo cu|SGK 2002" ;
    su9:confidence 3 .

su9:TB_KNTT a su9:Textbook ;
    rdfs:label "SGK Lich su va Dia li 9 - Ket noi tri thuc (2024)"@vi ;
    su9:aliases "KNTT|Ket noi tri thuc" ;
    su9:confidence 3 .

su9:TB_CTST a su9:Textbook ;
    rdfs:label "SGK Lich su va Dia li 9 - Chan troi sang tao (2024)"@vi ;
    su9:aliases "CTST|Chan troi sang tao" ;
    su9:confidence 3 .

su9:TB_CD a su9:Textbook ;
    rdfs:label "SGK Lich su va Dia li 9 - Canh Dieu (2024)"@vi ;
    su9:aliases "CD|Canh Dieu" ;
    su9:confidence 3 .
"""


# ======================================================================
# DATA DEFINITIONS
# ======================================================================

# --- Periods ---
PERIODS = [
    # (id, label, aliases, start, end, abstractness, confidence)
    ("P_WWII", "Chien tranh the gioi thu hai 1939-1945", "CTTG II|WWII", 1939, 1945, 2, 3),
    ("P_1919_1930", "Viet Nam 1919-1930", "", 1919, 1930, 3, 3),
    ("P_1930_1945", "Viet Nam 1930-1945", "", 1930, 1945, 3, 3),
    ("P_1945_1946", "VN nam dau sau CMT8 1945-1946", "", 1945, 1946, 3, 3),
    ("P_1946_1954", "Khang chien chong Phap 1946-1954", "", 1946, 1954, 3, 3),
    ("P_1954_1960", "VN sau Geneva 1954-1960", "", 1954, 1960, 3, 3),
    ("P_1961_1965", "Chien tranh dac biet 1961-1965", "", 1961, 1965, 3, 3),
    ("P_1965_1968", "Chien tranh cuc bo 1965-1968", "", 1965, 1968, 3, 3),
    ("P_1969_1973", "VN hoa chien tranh 1969-1973", "", 1969, 1973, 3, 3),
    ("P_1973_1975", "Giai phong mien Nam 1973-1975", "", 1973, 1975, 3, 3),
    ("P_1975_1986", "VN truoc Doi moi 1975-1986", "", 1975, 1986, 3, 3),
    ("P_1986_2000", "VN thoi ky Doi moi 1986-2000", "", 1986, 2000, 3, 3),
    ("P_ColdWar", "Chien tranh Lanh 1947-1991", "Cold War", 1947, 1991, 4, 3),
    ("P_Post1991", "The gioi sau Chien tranh Lanh", "", 1991, 2000, 4, 3),
    ("P_1945_1954", "Khang chien chong Phap 1945-1954", "", 1945, 1954, 3, 3),
    ("P_1954_1975", "Khang chien chong My 1954-1975", "", 1954, 1975, 3, 3),
    ("P_1975_2000", "VN 1975-2000", "", 1975, 2000, 3, 3),
]

# --- Locations ---
# (id, label, aliases, located_in, abstractness, confidence)
LOCATIONS = [
    # Vietnam
    ("L_VietNam", "Viet Nam", "", None, 1, 3),
    ("L_HaNoi", "Ha Noi", "", "L_VietNam", 1, 3),
    ("L_SaiGon", "Sai Gon", "TP Ho Chi Minh|TP HCM|Gia Dinh", "L_VietNam", 1, 3),
    ("L_Hue", "Hue", "", "L_VietNam", 1, 3),
    ("L_DaNang", "Da Nang", "", "L_VietNam", 1, 3),
    ("L_HaiPhong", "Hai Phong", "", "L_VietNam", 1, 3),
    ("L_DienBienPhu", "Dien Bien Phu", "", "L_VietNam", 1, 3),
    ("L_VietBac", "Viet Bac", "Can cu dia Viet Bac", "L_VietNam", 2, 3),
    ("L_TanTrao", "Tan Trao", "", "L_VietNam", 1, 3),
    ("L_PacBo", "Pac Bo", "", "L_VietNam", 1, 3),
    ("L_BaDinh", "Quang truong Ba Dinh", "", "L_HaNoi", 1, 3),
    ("L_MienBac", "Mien Bac Viet Nam", "", "L_VietNam", 2, 3),
    ("L_MienNam", "Mien Nam Viet Nam", "", "L_VietNam", 2, 3),
    ("L_NgheTinh", "Nghe Tinh", "Nghe An|Ha Tinh", "L_VietNam", 1, 3),
    ("L_QuangTri", "Quang Tri", "", "L_VietNam", 1, 3),
    ("L_BuonMaThuot", "Buon Ma Thuot", "", "L_VietNam", 1, 3),
    ("L_TrungBo", "Trung Bo", "Mien Trung", "L_VietNam", 2, 3),
    ("L_NamBo", "Nam Bo", "", "L_VietNam", 2, 3),
    ("L_BacBo", "Bac Bo", "", "L_VietNam", 2, 3),
    # World - Europe
    ("L_LienXo", "Lien Xo", "Soviet Union|USSR|Lien bang Xo Viet", None, 2, 3),
    ("L_Nga", "Nga", "Russia|Lien bang Nga", None, 1, 3),
    ("L_Moskva", "Moskva", "Moscow|Mat-xco-va", "L_LienXo", 1, 3),
    ("L_TayAu", "Tay Au", "", None, 2, 3),
    ("L_DongAu", "Dong Au", "", None, 2, 3),
    ("L_Phap", "Phap", "", "L_TayAu", 1, 3),
    ("L_Paris", "Paris", "Pa-ri", "L_Phap", 1, 3),
    ("L_Anh", "Anh", "United Kingdom|UK", "L_TayAu", 1, 3),
    ("L_Duc", "Duc", "Germany|Germany", "L_TayAu", 1, 3),
    ("L_Berlin", "Berlin", "Bec-lin", "L_Duc", 1, 3),
    ("L_DongDuc", "Cong hoa Dan chu Duc", "CHDC Duc|Dong Duc", None, 2, 3),
    ("L_TayDuc", "Cong hoa Lien bang Duc", "CHLB Duc|Tay Duc", None, 2, 3),
    ("L_Italia", "Italia", "Italy|Y", "L_TayAu", 1, 3),
    ("L_BaLan", "Ba Lan", "Poland", "L_DongAu", 1, 3),
    ("L_Hungary", "Hungary", "Hung-ga-ri", "L_DongAu", 1, 3),
    ("L_Tiep", "Tiep Khac", "Czechoslovakia", "L_DongAu", 1, 3),
    ("L_Geneva", "Geneva", "Gio-ne-vo|Geneve", None, 1, 3),
    # World - Americas
    ("L_My", "Nuoc My", "Hoa Ky|USA", None, 1, 3),
    ("L_Washington", "Washington", "", "L_My", 1, 3),
    ("L_Cuba", "Cuba", "", None, 1, 3),
    ("L_MyLatinh", "My Latinh", "", None, 2, 3),
    ("L_Chile", "Chile", "Chi-le", "L_MyLatinh", 1, 3),
    ("L_Brazil", "Brazil", "Bra-xin", "L_MyLatinh", 1, 3),
    # World - Asia
    ("L_TrungQuoc", "Trung Quoc", "China", None, 1, 3),
    ("L_BacKinh", "Bac Kinh", "Beijing", "L_TrungQuoc", 1, 3),
    ("L_NhatBan", "Nhat Ban", "Japan", None, 1, 3),
    ("L_Tokyo", "Tokyo", "To-ky-o", "L_NhatBan", 1, 3),
    ("L_Hiroshima", "Hiroshima", "Hi-ro-si-ma", "L_NhatBan", 1, 3),
    ("L_TrieuTien", "Trieu Tien", "Korea|Ban dao Trieu Tien", None, 1, 3),
    ("L_BacTrieuTien", "CHDCND Trieu Tien", "Bac Trieu Tien|North Korea", None, 2, 3),
    ("L_NamTrieuTien", "Han Quoc", "Nam Trieu Tien|South Korea", None, 2, 3),
    ("L_AnDo", "An Do", "India", None, 1, 3),
    ("L_DongNamA", "Dong Nam A", "Southeast Asia", None, 2, 3),
    ("L_Lao", "Lao", "", "L_DongNamA", 1, 3),
    ("L_Campuchia", "Cam-pu-chia", "Kampuchea|Cambodia", "L_DongNamA", 1, 3),
    ("L_Indonesia", "In-do-ne-xi-a", "Indonesia", "L_DongNamA", 1, 3),
    ("L_Thailand", "Thai Lan", "Thailand", "L_DongNamA", 1, 3),
    ("L_Malaysia", "Ma-lai-xi-a", "Malaysia", "L_DongNamA", 1, 3),
    ("L_Singapore", "Xinh-ga-po", "Singapore", "L_DongNamA", 1, 3),
    ("L_Philippines", "Phi-lip-pin", "Philippines", "L_DongNamA", 1, 3),
    ("L_Myanmar", "My-an-ma", "Myanmar|Burma", "L_DongNamA", 1, 3),
    # World - Africa
    ("L_ChauPhi", "Chau Phi", "Africa", None, 2, 3),
    ("L_AiCap", "Ai Cap", "Egypt", "L_ChauPhi", 1, 3),
    ("L_Angieri", "An-gie-ri", "Algeria", "L_ChauPhi", 1, 3),
    ("L_NamPhi", "Nam Phi", "South Africa", "L_ChauPhi", 1, 3),
]

# --- Persons ---
# (id, label, aliases, frequency, abstractness, confidence)
PERSONS = [
    ("Pe_HoChiMinh", "Ho Chi Minh", "Nguyen Ai Quoc|NAQ|Nguyen Tat Thanh|Bac Ho", 80, 1, 3),
    ("Pe_VoNguyenGiap", "Vo Nguyen Giap", "Dai tuong Vo Nguyen Giap", 15, 1, 3),
    ("Pe_TranPhu", "Tran Phu", "Tong Bi thu Tran Phu", 6, 1, 3),
    ("Pe_LeHongPhong", "Le Hong Phong", "", 4, 1, 3),
    ("Pe_NguyenVanCu", "Nguyen Van Cu", "Tong Bi thu Nguyen Van Cu", 4, 1, 3),
    ("Pe_HaHuyTap", "Ha Huy Tap", "", 3, 1, 3),
    ("Pe_TruongChinh", "Truong Chinh", "Dang Xuan Khu", 6, 1, 3),
    ("Pe_LeDuan", "Le Duan", "Tong Bi thu Le Duan", 8, 1, 3),
    ("Pe_PhamVanDong", "Pham Van Dong", "Thu tuong Pham Van Dong", 5, 1, 3),
    ("Pe_NguyenChiThanh", "Nguyen Chi Thanh", "Dai tuong Nguyen Chi Thanh", 3, 1, 2),
    ("Pe_VanTienDung", "Van Tien Dung", "Dai tuong Van Tien Dung", 3, 1, 2),
    ("Pe_PhanBoiChau", "Phan Boi Chau", "", 5, 1, 3),
    ("Pe_PhanChauTrinh", "Phan Chau Trinh", "Phan Chu Trinh", 5, 1, 3),
    ("Pe_NguyenThaiHoc", "Nguyen Thai Hoc", "", 4, 1, 3),
    ("Pe_LyTuTrong", "Ly Tu Trong", "", 3, 1, 3),
    ("Pe_TonDucThang", "Ton Duc Thang", "Bac Ton", 3, 1, 3),
    ("Pe_Lenin", "Lenin", "V.I. Lenin|Vla-di-mia Le-nin", 8, 1, 3),
    ("Pe_Stalin", "Stalin", "I.V. Stalin|I-o-sif Sta-lin", 5, 1, 3),
    ("Pe_Khrushchev", "Khrushchev", "Khơ-rut-sốp", 3, 1, 2),
    ("Pe_Brezhnev", "Brezhnev", "Brê-giơ-nhép", 2, 1, 2),
    ("Pe_Gorbachev", "Gorbachev", "Gooc-ba-chop|M. Gorbachev", 6, 1, 3),
    ("Pe_Yeltsin", "Yeltsin", "En-xin|B. Yeltsin", 2, 1, 2),
    ("Pe_Putin", "Putin", "V. Putin|Pu-tin", 3, 1, 2),
    ("Pe_MaoTrachDong", "Mao Trach Dong", "Mao Zedong", 5, 1, 3),
    ("Pe_DangTieuBinh", "Dang Tieu Binh", "Deng Xiaoping|Đặng Tiểu Bình", 4, 1, 3),
    ("Pe_Nehru", "Nehru", "Jawaharlal Nehru|Ne-ru", 3, 1, 3),
    ("Pe_Gandhi", "Gandhi", "Mahatma Gandhi|Găng-đi", 3, 1, 3),
    ("Pe_Sukarno", "Sukarno", "Xu-các-nô", 2, 1, 2),
    ("Pe_Roosevelt", "Roosevelt", "F.D. Roosevelt|Ru-dơ-ven", 3, 1, 3),
    ("Pe_Truman", "Truman", "Harry Truman|Tru-man", 3, 1, 3),
    ("Pe_Eisenhower", "Eisenhower", "Dwight Eisenhower|Ai-xen-hao", 2, 1, 2),
    ("Pe_Kennedy", "Kennedy", "J.F. Kennedy|Ken-nơ-đi", 3, 1, 3),
    ("Pe_Johnson", "Johnson", "Lyndon Johnson|Giôn-xơn", 3, 1, 2),
    ("Pe_Nixon", "Nixon", "Richard Nixon|Ních-xơn", 4, 1, 3),
    ("Pe_Churchill", "Churchill", "Winston Churchill|Sớc-sin", 2, 1, 3),
    ("Pe_DeGaulle", "De Gaulle", "Sac-lơ Đờ-gôn|Charles de Gaulle", 2, 1, 2),
    ("Pe_FidelCastro", "Phi-den Cat-xto-ro", "Fidel Castro", 5, 1, 3),
    ("Pe_CheGuevara", "Che Guevara", "Che Ghê-va-ra", 2, 1, 2),
    ("Pe_NelsonMandela", "Nelson Mandela", "N. Man-de-la", 3, 1, 3),
    ("Pe_Nasser", "Nasser", "Na-xe|Gamal Abdel Nasser", 2, 1, 2),
    ("Pe_KimNhatThanh", "Kim Nhat Thanh", "Kim Il-sung", 2, 1, 2),
    ("Pe_Ngothrungdiem", "Ngo Dinh Diem", "", 4, 1, 3),
    ("Pe_NguyenVanThieu", "Nguyen Van Thieu", "", 3, 1, 3),
    ("Pe_DuongVanMinh", "Duong Van Minh", "", 3, 1, 3),
    ("Pe_AngSan", "Aung San", "Ong-xan", 1, 1, 2),
]

# --- Organizations ---
ORGANIZATIONS = [
    # id, label, aliases, frequency, abstractness, confidence
    ("O_DangCongSanVN", "Dang Cong san Viet Nam", "DCSVN|Dang Cong san Dong Duong|Dang", 50, 2, 3),
    ("O_VietMinh", "Mat tran Viet Minh", "Viet Minh|VN Doc lap Dong minh", 25, 2, 3),
    ("O_LienVietMatTran", "Mat tran Lien Viet", "Lien Viet", 6, 2, 3),
    ("O_VNDCCH", "Nuoc Viet Nam Dan chu Cong hoa", "VNDCCH|VN Dan chu Cong hoa", 30, 2, 3),
    ("O_CHXHCN_VN", "Cong hoa Xa hoi chu nghia Viet Nam", "CHXHCN VN", 10, 2, 3),
    ("O_MTDTGP", "Mat tran Dan toc Giai phong mien Nam VN", "MTDTGP MNVN|MTDTGP", 8, 2, 3),
    ("O_CPCMLT", "Chinh phu Cach mang Lam thoi CHMN VN", "CPCMLT|CPCM Lam thoi", 5, 2, 3),
    ("O_VNCH", "Viet Nam Cong hoa", "Chinh quyen Sai Gon|VNCH", 8, 2, 3),
    ("O_VNQDD", "Viet Nam Quoc dan Dang", "VNQDD", 4, 2, 3),
    ("O_TanViet", "Tan Viet Cach mang Dang", "Tan Viet", 3, 2, 3),
    ("O_DongDuongCSD", "Dong Duong Cong san Dang", "", 3, 2, 3),
    ("O_AnNamCSD", "An Nam Cong san Dang", "", 3, 2, 3),
    ("O_DongDuongCSLien", "Dong Duong Cong san Lien doan", "", 2, 2, 3),
    ("O_HoiVNCMThanhNien", "Hoi Viet Nam Cach mang Thanh nien", "Hoi VNCMTN", 6, 2, 3),
    ("O_VNGiaiPhongQuan", "Viet Nam Giai phong quan", "VNGPQ", 4, 2, 3),
    ("O_QuanDoiNhanDanVN", "Quan doi Nhan dan Viet Nam", "QDND VN", 15, 2, 3),
    ("O_QuocTeCongSan", "Quoc te Cong san", "Quoc te III|Comintern", 5, 3, 3),
    ("O_LHQ", "Lien Hop Quoc", "UN|LHQ", 12, 2, 3),
    ("O_HoiDongBaoAn", "Hoi dong Bao an LHQ", "", 3, 3, 3),
    ("O_ASEAN", "ASEAN", "Hiep hoi cac quoc gia Dong Nam A", 15, 3, 3),
    ("O_NATO", "Khoi NATO", "NATO|Khoi Bac Dai Tay Duong", 7, 3, 3),
    ("O_Warsaw", "Khoi Vacsava", "Warsaw Pact|Hiep uoc Vacsava", 6, 3, 3),
    ("O_SEV", "Hoi dong Tuong tro Kinh te SEV", "SEV|COMECON", 5, 3, 3),
    ("O_EU", "Lien minh chau Au", "EU|Lien minh Chau Au", 8, 3, 3),
    ("O_EEC", "Cong dong Kinh te chau Au", "EEC|Khoi Thi truong chung chau Au", 5, 3, 3),
    ("O_G7", "Nhom G7", "G7|Nhom 7 nuoc cong nghiep phat trien", 3, 3, 3),
    ("O_WTO", "To chuc Thuong mai The gioi", "WTO", 4, 3, 3),
    ("O_APEC", "Dien dan Hop tac Kinh te chau A-Thai Binh Duong", "APEC", 3, 3, 3),
    ("O_IMF", "Quy Tien te Quoc te", "IMF", 2, 3, 2),
    ("O_WB", "Ngan hang The gioi", "World Bank|WB", 2, 3, 2),
    ("O_AU", "Lien minh chau Phi", "AU|Lien minh Chau Phi", 2, 3, 2),
    ("O_OAU", "To chuc Thong nhat chau Phi", "OAU", 2, 3, 2),
    ("O_NAM", "Phong trao Khong lien ket", "NAM|Khong lien ket", 3, 4, 3),
    ("O_Quocdan_Dang_TQ", "Quoc dan Dang Trung Quoc", "Kuomintang|KMT", 2, 2, 3),
    ("O_DCS_TQ", "Dang Cong san Trung Quoc", "Communist Party of China", 5, 2, 3),
]

# --- Movements ---
MOVEMENTS = [
    ("M_DongDu", "Phong trao Dong Du", "", 4, 3, 3),
    ("M_CanVuong", "Phong trao Can Vuong", "", 3, 3, 3),
    ("M_DuyTan", "Phong trao Duy Tan", "", 3, 3, 3),
    ("M_CM_19_25", "Phong trao cach mang VN 1919-1925", "", 6, 3, 3),
    ("M_CM_30_31", "Phong trao cach mang 1930-1931", "Xo Viet Nghe Tinh", 10, 3, 3),
    ("M_DanChu_36_39", "Phong trao dan chu 1936-1939", "Cuoc van dong dan chu", 10, 3, 3),
    ("M_KhangNhat", "Phong trao khang Nhat cuu nuoc", "", 5, 3, 3),
    ("M_DongKhoi", "Phong trao Dong Khoi", "Cao trao Dong Khoi 1959-1960", 7, 3, 3),
    ("M_GPDT_ChauA", "Phong trao GPDT chau A sau 1945", "", 8, 4, 3),
    ("M_GPDT_ChauPhi", "Phong trao GPDT chau Phi", "", 5, 4, 3),
    ("M_GPDT_MyLatinh", "Phong trao GPDT My Latinh", "", 5, 4, 3),
    ("M_KhongLienKet", "Phong trao Khong lien ket", "NAM", 4, 4, 3),
    ("M_CongNhan_VN_Post1918", "Phong trao cong nhan VN sau 1918", "", 5, 3, 3),
    ("M_ChongMy_MienNam", "Phong trao chong My o mien Nam", "", 10, 3, 3),
    ("M_ThiDuaYeuNuoc", "Phong trao thi dua yeu nuoc", "", 4, 3, 2),
]

# --- Documents ---
DOCUMENTS = [
    ("D_CuongLinh1930", "Cuong linh chinh tri dau tien 1930", "Chanh cuong van tat", 7, 4, 3),
    ("D_SachLuoc1930", "Sach luoc van tat 1930", "", 4, 4, 3),
    ("D_LuanCuong1030", "Luan cuong chinh tri 10/1930", "", 6, 4, 3),
    ("D_TuyenNgonDocLap", "Tuyen ngon Doc lap 2/9/1945", "", 10, 3, 3),
    ("D_HienPhap1946", "Hien phap 1946", "", 4, 3, 3),
    ("D_HiepDinhSoBo", "Hiep dinh So bo 6/3/1946", "", 5, 3, 3),
    ("D_TamUocPaxtiNo", "Tam uoc 14/9/1946", "Tam uoc Pa-ri", 3, 3, 3),
    ("D_LoiKeuGoiKCTQ", "Loi keu goi toan quoc khang chien 12/1946", "", 5, 3, 3),
    ("D_KhangChienTruongKi", "Tac pham Khang chien nhat dinh thang loi", "", 3, 3, 2),
    ("D_HiepDinhGeneva1954", "Hiep dinh Geneva 1954", "Hiep dinh Gio-ne-vo|Hiep dinh Geneve", 12, 3, 3),
    ("D_HiepDinhParis1973", "Hiep dinh Paris 1973", "Hiep dinh Pa-ri", 10, 3, 3),
    ("D_HienPhap1959", "Hien phap 1959", "", 3, 3, 3),
    ("D_HienPhap1980", "Hien phap 1980", "", 3, 3, 3),
    ("D_HienPhap1992", "Hien phap 1992", "", 3, 3, 3),
    ("D_DiChucHCM", "Di chuc Ho Chi Minh", "", 4, 3, 3),
    ("D_NghiQuyet15", "Nghi quyet 15 (1/1959)", "", 4, 4, 3),
    ("D_HienChuongLHQ", "Hien chuong Lien Hop Quoc", "", 3, 3, 3),
    ("D_HocThuyetTruman", "Hoc thuyet Truman 1947", "", 4, 4, 3),
    ("D_KeHoachMarshall", "Ke hoach Marshall", "", 3, 3, 3),
    ("D_HiepDinhHelsinki", "Hiep dinh Helsinki 1975", "", 2, 3, 2),
]

# --- Concepts ---
CONCEPTS = [
    # id, label, aliases, freq, abstractness, bloom, confidence
    ("C_ChuNghiaThucDan", "Chu nghia thuc dan", "CN thuc dan", 25, 5, 2, 3),
    ("C_ChuNghiaDeQuoc", "Chu nghia de quoc", "CN de quoc", 18, 5, 2, 3),
    ("C_ChuNghiaTuBan", "Chu nghia tu ban", "CNTB", 20, 5, 2, 3),
    ("C_ChuNghiaXaHoi", "Chu nghia xa hoi", "CNXH", 30, 5, 2, 3),
    ("C_ChuNghiaCongSan", "Chu nghia cong san", "", 10, 5, 3, 3),
    ("C_CNMacLenin", "Chu nghia Mac-Lenin", "Chu nghia Mac Lenin", 12, 5, 3, 3),
    ("C_TuTuongHCM", "Tu tuong Ho Chi Minh", "", 8, 5, 3, 3),
    ("C_CachMangVoSan", "Cach mang vo san", "", 12, 5, 3, 3),
    ("C_CachMangTuSan", "Cach mang tu san", "CMTB", 8, 5, 3, 3),
    ("C_CachMangDanToc", "Cach mang dan toc dan chu nhan dan", "CM DTDCND", 15, 5, 3, 3),
    ("C_CachMangXHCN", "Cach mang xa hoi chu nghia", "CM XHCN", 10, 5, 3, 3),
    ("C_GiaiCapCongNhan", "Giai cap cong nhan", "", 8, 4, 2, 3),
    ("C_GiaiCapNongDan", "Giai cap nong dan", "", 6, 4, 2, 3),
    ("C_GiaiCapTuSan", "Giai cap tu san", "", 5, 4, 2, 3),
    ("C_MatTranDanToc", "Mat tran dan toc thong nhat", "", 8, 4, 2, 3),
    ("C_DoiMoi", "Duong loi Doi moi", "Cong cuoc Doi moi", 12, 3, 2, 3),
    ("C_KinhTeThiTruong", "Kinh te thi truong dinh huong XHCN", "", 6, 5, 3, 3),
    ("C_KinhTeKeHoachHoa", "Kinh te ke hoach hoa tap trung", "Co che quan li bao cap", 5, 5, 3, 3),
    ("C_CongNghiepHoa", "Cong nghiep hoa hien dai hoa", "CNH HDH", 5, 4, 2, 3),
    ("C_HopTacHoa", "Hop tac hoa nong nghiep", "", 4, 4, 2, 3),
    ("C_CaiCachRuongDat", "Cai cach ruong dat", "", 6, 3, 2, 3),
    ("C_ChienTranhLanh", "Chien tranh Lanh", "Cold War", 15, 4, 2, 3),
    ("C_TratTuHaiCuc", "Trat tu hai cuc Ianta", "Trat tu hai cuc|Hai cuc I-an-ta", 10, 5, 3, 3),
    ("C_DaCucDaTrungTam", "Da cuc da trung tam", "Trat tu the gioi moi|Da cuc", 5, 5, 3, 3),
    ("C_ToanCauHoa", "Toan cau hoa", "Globalization", 8, 5, 3, 3),
    ("C_CMKHKT", "Cach mang khoa hoc - ky thuat", "CM KHKT", 10, 3, 2, 3),
    ("C_CachMangCongNghiep4", "Cach mang cong nghe 4.0", "CMCN 4.0", 4, 4, 3, 2),
    ("C_PhiThucDanHoa", "Phi thuc dan hoa", "Giai phong dan toc|GPDT", 12, 4, 3, 3),
    ("C_HeThongThuocDia", "He thong thuoc dia", "", 6, 4, 2, 3),
    ("C_DongMinhChongPhatXit", "Dong minh chong phat xit", "", 5, 3, 2, 3),
    ("C_PhatXit", "Chu nghia phat xit", "CN phat xit", 5, 4, 2, 3),
    ("C_ChienTranhCucBo", "Chien tranh cuc bo", "", 6, 3, 2, 3),
    ("C_ChienTranhDacBiet", "Chien tranh dac biet", "", 6, 3, 2, 3),
    ("C_VNHoaChienTranh", "Viet Nam hoa chien tranh", "", 6, 3, 2, 3),
    ("C_ChienLuoc3Mui", "Chien luoc 3 mui giap cong", "", 3, 4, 3, 2),
    ("C_BaoVaChongBao", "Bao vay va chong bao vay kinh te", "", 3, 4, 3, 2),
    ("C_HoiNhapQuocTe", "Hoi nhap quoc te", "", 5, 4, 3, 2),
    ("C_KhuVucHoa", "Khu vuc hoa", "", 3, 4, 3, 2),
    ("C_CMXanh", "Cach mang xanh", "", 3, 3, 2, 2),
    ("C_ChienTranhNhanDan", "Chien tranh nhan dan", "", 5, 4, 3, 3),
]

print(f"Defined: {len(PERIODS)} periods, {len(LOCATIONS)} locations, "
      f"{len(PERSONS)} persons, {len(ORGANIZATIONS)} orgs, "
      f"{len(MOVEMENTS)} movements, {len(DOCUMENTS)} docs, {len(CONCEPTS)} concepts")
