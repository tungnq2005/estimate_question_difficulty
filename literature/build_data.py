"""
Van 9 ontology generator.

Schema FUNDAMENTALLY DIFFERENT from STEM subjects. Literature is about:
  - Works (tac pham) with authors, contexts, themes
  - Literary devices (bien phap tu tu) as tools of expression
  - Themes (chu de, tu tuong) as abstract meaning
  - Historical periods that shape style and content

Difficulty is NOT driven by prerequisite chains. Instead:
  (a) abstractness of theme (concrete vs symbolic/philosophical),
  (b) complexity of literary devices used (simple similes vs multilayered symbolism),
  (c) historical distance (cac tac pham co co nhieu tu co),
  (d) interpretive depth required (surface reading vs critical analysis),
  (e) genre conventions required to understand.

Classes:
  - LiteraryWork:    tac pham van hoc
  - Author:          tac gia
  - Character:       nhan vat
  - LiteraryDevice:  bien phap nghe thuat / thu phap
  - Theme:           chu de, tu tuong
  - Genre:           the loai
  - HistoricalPeriod: thoi ky van hoc
  - LessonUnit, Textbook

CAUTION: Content confidence is lower than STEM subjects. Work list varies
  between textbook editions (especially foreign literature selections).
"""

from pathlib import Path
ROOT = Path(__file__).resolve().parent

HEADER = """\
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix lit:  <http://edu.vn/lit9/ontology#> .

<http://edu.vn/lit9/ontology> a owl:Ontology ;
    rdfs:label "Ontology Ngu Van 9 - Cold-start Question Difficulty Estimation"@vi ;
    owl:versionInfo "0.1.0" .
"""

SCHEMA = """\
#################################################################
#   CLASSES
#################################################################

lit:LitEntity        a owl:Class ; rdfs:label "Thuc the Van hoc"@vi .
lit:LiteraryWork     a owl:Class ; rdfs:subClassOf lit:LitEntity ; rdfs:label "Tac pham van hoc"@vi .
lit:Author           a owl:Class ; rdfs:subClassOf lit:LitEntity ; rdfs:label "Tac gia"@vi .
lit:Character        a owl:Class ; rdfs:subClassOf lit:LitEntity ; rdfs:label "Nhan vat"@vi .
lit:LiteraryDevice   a owl:Class ; rdfs:subClassOf lit:LitEntity ; rdfs:label "Bien phap nghe thuat"@vi .
lit:Theme            a owl:Class ; rdfs:subClassOf lit:LitEntity ; rdfs:label "Chu de / Tu tuong"@vi .
lit:Genre            a owl:Class ; rdfs:subClassOf lit:LitEntity ; rdfs:label "The loai"@vi .
lit:HistoricalPeriod a owl:Class ; rdfs:subClassOf lit:LitEntity ; rdfs:label "Thoi ky van hoc"@vi .
lit:LessonUnit       a owl:Class ; rdfs:label "Bai hoc SGK"@vi .
lit:Textbook         a owl:Class ; rdfs:label "Bo SGK"@vi .

#################################################################
#   OBJECT PROPERTIES
#################################################################

lit:authoredBy a owl:ObjectProperty ;
    rdfs:domain lit:LiteraryWork ; rdfs:range lit:Author ;
    rdfs:label "sang tac boi"@vi .

lit:contains a owl:ObjectProperty ;
    rdfs:domain lit:LiteraryWork ; rdfs:range lit:Character ;
    rdfs:label "co nhan vat"@vi .

lit:uses a owl:ObjectProperty ;
    rdfs:domain lit:LiteraryWork ; rdfs:range lit:LiteraryDevice ;
    rdfs:label "su dung (nghe thuat)"@vi .

lit:expresses a owl:ObjectProperty ;
    rdfs:domain lit:LiteraryWork ; rdfs:range lit:Theme ;
    rdfs:label "the hien chu de"@vi .

lit:hasGenre a owl:ObjectProperty ;
    rdfs:domain lit:LiteraryWork ; rdfs:range lit:Genre ;
    rdfs:label "thuoc the loai"@vi .

lit:writtenIn a owl:ObjectProperty ;
    rdfs:domain lit:LiteraryWork ; rdfs:range lit:HistoricalPeriod ;
    rdfs:label "sang tac vao thoi ky"@vi .

lit:activeIn a owl:ObjectProperty ;
    rdfs:domain lit:Author ; rdfs:range lit:HistoricalPeriod ;
    rdfs:label "hoat dong vao thoi ky"@vi .

lit:relatedWork a owl:ObjectProperty , owl:SymmetricProperty ;
    rdfs:label "lien he voi tac pham"@vi .

lit:appearsInLesson a owl:ObjectProperty ; rdfs:range lit:LessonUnit ; rdfs:label "xuat hien trong bai"@vi .
lit:partOfTextbook  a owl:ObjectProperty ; rdfs:range lit:Textbook ; rdfs:label "thuoc bo SGK"@vi .

lit:similarTo a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "tuong tu"@vi .
lit:contrastsWith a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "doi lap"@vi .

#################################################################
#   DATA PROPERTIES
#################################################################

lit:abstractness a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "1=rat cu the, 5=rat truu tuong/trieu tuong"@vi .
lit:bloomLevel a owl:DatatypeProperty ; rdfs:range xsd:integer .
lit:interpretiveDepth a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "1=hieu be mat, 5=can phan tich sau, da tang nghia"@vi .
lit:historicalDistance a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "1=hien dai (it tu co), 5=trung dai (nhieu tu co, dien co)"@vi .
lit:yearWritten a owl:DatatypeProperty ; rdfs:range xsd:string .
lit:frequencyInTextbook a owl:DatatypeProperty ; rdfs:range xsd:integer .
lit:curriculumPosition a owl:DatatypeProperty ; rdfs:range xsd:integer .
lit:aliases a owl:DatatypeProperty ; rdfs:range xsd:string .
lit:confidence a owl:DatatypeProperty ; rdfs:range xsd:integer .

#################################################################
#   TEXTBOOKS
#################################################################

lit:TB_Old a lit:Textbook ; rdfs:label "SGK Ngu Van 9 (bo cu)"@vi ; lit:confidence 3 .
lit:TB_KNTT a lit:Textbook ; rdfs:label "SGK Ngu Van 9 - Ket noi tri thuc"@vi ; lit:confidence 3 .
lit:TB_CTST a lit:Textbook ; rdfs:label "SGK Ngu Van 9 - Chan troi sang tao"@vi ; lit:confidence 3 .
lit:TB_CD a lit:Textbook ; rdfs:label "SGK Ngu Van 9 - Canh Dieu"@vi ; lit:confidence 3 .
"""

# ======================================================================
# DATA
# ======================================================================

# --- Historical periods ---
PERIODS = [
    # id, label, aliases, year_range, abstract, conf
    ("HP_TrungDai", "Van hoc trung dai Viet Nam (X-XIX)", "Van hoc co|Van hoc trung dai", 4, 3),
    ("HP_CanDai", "Van hoc can dai (cuoi XIX - dau XX)", "", 4, 3),
    ("HP_1930_1945", "Van hoc 1930-1945 (Tho moi, van hien thuc)", "Tho Moi|Van hoc hien thuc", 3, 3),
    ("HP_KhangChien", "Van hoc khang chien chong Phap va My (1945-1975)", "Van hoc khang chien|Van hoc cach mang", 3, 3),
    ("HP_HienDai", "Van hoc Viet Nam hien dai (sau 1975)", "Van hoc sau 1975", 3, 3),
    ("HP_NuocNgoai", "Van hoc nuoc ngoai", "Van hoc the gioi", 3, 2),
]

# --- Genres ---
GENRES = [
    ("G_TruyenTho", "Truyen tho (chu Nom)", "", 4, 3),
    ("G_TruyenNgan", "Truyen ngan", "", 2, 3),
    ("G_TieuThuyet", "Tieu thuyet", "", 3, 3),
    ("G_ThoLucBat", "Tho luc bat", "", 3, 3),
    ("G_ThoBayChuTuDo", "Tho bay chu / tho tu do", "", 3, 3),
    ("G_ThoTruTinh", "Tho tru tinh hien dai", "", 3, 3),
    ("G_Kich", "Kich noi", "", 3, 3),
    ("G_VanNghiLuan", "Van nghi luan (xa hoi, van hoc)", "", 3, 3),
    ("G_BuoiKy_TuyBut", "But ky, tuy but", "", 3, 3),
    ("G_TruyenCo", "Truyen co (nuoc ngoai)", "", 2, 2),
]

# --- Authors ---
AUTHORS = [
    # id, label, aliases, period_id, abstract, freq, conf
    ("A_NguyenDu", "Nguyen Du", "Thanh Hien|Nguyen Du", "HP_TrungDai", 3, 15, 3),
    ("A_NguyenDinhChieu", "Nguyen Dinh Chieu", "Do Chieu", "HP_TrungDai", 3, 8, 3),
    ("A_NguyenDu_Cu", "Nguyen Du (Nguyen Du cua the ky XV)", "", "HP_TrungDai", 3, 0, 1),  # disambiguation note
    ("A_NguyenDu_NamXuong", "Nguyen Du (Truyen Ky Man Luc)", "Nguyen Du", "HP_TrungDai", 3, 3, 1),  # actually Nguyen Du
    ("A_NgoGiaVanPhai", "Ngo gia van phai", "", "HP_TrungDai", 3, 5, 3),
    ("A_ChinhHuu", "Chinh Huu", "", "HP_KhangChien", 3, 6, 3),
    ("A_PhamTienDuat", "Pham Tien Duat", "", "HP_KhangChien", 3, 6, 3),
    ("A_NguyenDuy", "Nguyen Duy", "", "HP_HienDai", 3, 6, 3),
    ("A_BangViet", "Bang Viet", "", "HP_HienDai", 3, 5, 3),
    ("A_NguyenKhoaDiem", "Nguyen Khoa Diem", "", "HP_KhangChien", 3, 5, 3),
    ("A_HuyCan", "Huy Can", "", "HP_1930_1945", 3, 6, 3),
    ("A_HuuThinh", "Huu Thinh", "", "HP_HienDai", 3, 5, 3),
    ("A_ThanhHai", "Thanh Hai", "", "HP_HienDai", 3, 5, 3),
    ("A_VienPhuong", "Vien Phuong", "", "HP_HienDai", 3, 5, 3),
    ("A_YPhuong", "Y Phuong", "", "HP_HienDai", 3, 5, 3),
    ("A_CheLanVien", "Che Lan Vien", "", "HP_HienDai", 3, 5, 3),
    ("A_KimLan", "Kim Lan", "", "HP_KhangChien", 3, 6, 3),
    ("A_NguyenThanhLong", "Nguyen Thanh Long", "", "HP_KhangChien", 3, 5, 3),
    ("A_NguyenQuangSang", "Nguyen Quang Sang", "", "HP_KhangChien", 3, 6, 3),
    ("A_NguyenMinhChau", "Nguyen Minh Chau", "", "HP_HienDai", 3, 5, 3),
    ("A_LeMinhKhue", "Le Minh Khue", "", "HP_HienDai", 3, 5, 3),
    ("A_NguyenHuyTuong", "Nguyen Huy Tuong", "", "HP_KhangChien", 3, 4, 3),
    ("A_LuuQuangVu", "Luu Quang Vu", "", "HP_HienDai", 3, 4, 3),
    ("A_Maupassant", "Guy de Maupassant (Mo-pa-xang)", "Mo-pa-xang", "HP_NuocNgoai", 3, 3, 2),
    ("A_Gorki", "Maksim Gor-ki", "Maxim Gorki|Mac-xim Goroki", "HP_NuocNgoai", 3, 3, 2),
    ("A_DanielDefoe", "Daniel Defoe (Di-phoi)", "Di-phoi", "HP_NuocNgoai", 3, 3, 2),
    ("A_LaPhongTen", "Jean de La Fontaine (La Phong-ten)", "La Phong-ten", "HP_NuocNgoai", 3, 3, 2),
]

# --- Literary Works (noi dung chinh) ---
WORKS = [
    # id, label, aliases, author_id, period_id, genre_id, year, abstract, interpret, hist_dist, freq, conf
    ("W_TruyenKieu", "Truyen Kieu", "Doan truong tan thanh", "A_NguyenDu", "HP_TrungDai", "G_TruyenTho", "~1820", 4, 5, 5, 20, 3),
    ("W_ChuyenNguoiConGaiNX", "Chuyen nguoi con gai Nam Xuong", "", "A_NguyenDu_NamXuong", "HP_TrungDai", "G_TruyenNgan", "~XVI", 4, 4, 5, 8, 3),
    ("W_HoangLeNhatThongChi_14", "Hoang Le nhat thong chi - Hoi thu 14", "", "A_NgoGiaVanPhai", "HP_TrungDai", "G_TieuThuyet", "~XIX", 3, 3, 5, 5, 3),
    ("W_LucVanTien_CuuKNN", "Luc Van Tien cuu Kieu Nguyet Nga (trich)", "", "A_NguyenDinhChieu", "HP_TrungDai", "G_TruyenTho", "~1860", 3, 3, 4, 5, 3),
    ("W_DongChi", "Dong chi", "", "A_ChinhHuu", "HP_KhangChien", "G_ThoBayChuTuDo", "1948", 3, 3, 2, 8, 3),
    ("W_BaiThoTDXKK", "Bai tho ve tieu doi xe khong kinh", "", "A_PhamTienDuat", "HP_KhangChien", "G_ThoTruTinh", "1969", 3, 3, 2, 8, 3),
    ("W_AnhTrang", "Anh trang", "", "A_NguyenDuy", "HP_HienDai", "G_ThoTruTinh", "1978", 4, 4, 2, 7, 3),
    ("W_BepLua", "Bep lua", "", "A_BangViet", "HP_HienDai", "G_ThoTruTinh", "1963", 3, 4, 2, 6, 3),
    ("W_KhucHatRu", "Khuc hat ru nhung em be lon tren lung me", "", "A_NguyenKhoaDiem", "HP_KhangChien", "G_ThoTruTinh", "1971", 3, 3, 2, 6, 3),
    ("W_DoanThuyenDanhCa", "Doan thuyen danh ca", "", "A_HuyCan", "HP_KhangChien", "G_ThoTruTinh", "1958", 3, 3, 2, 6, 3),
    ("W_SangThu", "Sang thu", "", "A_HuuThinh", "HP_HienDai", "G_ThoTruTinh", "1977", 3, 3, 2, 6, 3),
    ("W_MuaXuanNhoNho", "Mua xuan nho nho", "", "A_ThanhHai", "HP_HienDai", "G_ThoTruTinh", "1980", 3, 4, 2, 6, 3),
    ("W_ViengLangBac", "Vieng lang Bac", "", "A_VienPhuong", "HP_HienDai", "G_ThoTruTinh", "1976", 3, 4, 2, 6, 3),
    ("W_NoiVoiCon", "Noi voi con", "", "A_YPhuong", "HP_HienDai", "G_ThoTruTinh", "~1980", 3, 4, 2, 5, 3),
    ("W_ConCo", "Con co", "", "A_CheLanVien", "HP_HienDai", "G_ThoTruTinh", "1962", 4, 5, 2, 5, 3),
    ("W_Lang", "Lang", "", "A_KimLan", "HP_KhangChien", "G_TruyenNgan", "1948", 2, 3, 2, 7, 3),
    ("W_LangLeSaPa", "Lang le Sa Pa", "", "A_NguyenThanhLong", "HP_KhangChien", "G_TruyenNgan", "1970", 2, 3, 2, 6, 3),
    ("W_ChiecLuocNga", "Chiec luoc nga", "", "A_NguyenQuangSang", "HP_KhangChien", "G_TruyenNgan", "1966", 2, 3, 2, 7, 3),
    ("W_BenQue", "Ben que", "", "A_NguyenMinhChau", "HP_HienDai", "G_TruyenNgan", "1985", 3, 4, 2, 5, 3),
    ("W_NhungNgoiSao_XX", "Nhung ngoi sao xa xoi", "", "A_LeMinhKhue", "HP_HienDai", "G_TruyenNgan", "1971", 2, 3, 2, 6, 3),
    ("W_BacSon", "Bac Son (trich)", "", "A_NguyenHuyTuong", "HP_KhangChien", "G_Kich", "1946", 2, 3, 2, 4, 3),
    ("W_ToiVaChungTa", "Toi va chung ta (trich)", "", "A_LuuQuangVu", "HP_HienDai", "G_Kich", "1984", 3, 3, 2, 4, 3),
    ("W_BoCuaXiMong", "Bo cua Xi-mong", "Bo cua Xi-Mong", "A_Maupassant", "HP_NuocNgoai", "G_TruyenNgan", "1879", 2, 3, 3, 4, 2),
    ("W_NhungDuaTreGorki", "Nhung dua tre (trich Thoi tho au)", "", "A_Gorki", "HP_NuocNgoai", "G_TruyenCo", "1913-14", 2, 3, 2, 3, 2),
    ("W_RobinsonCruxo", "Ro-bin-xon Cru-xo (trich)", "Robinson Crusoe", "A_DanielDefoe", "HP_NuocNgoai", "G_TieuThuyet", "1719", 2, 3, 3, 3, 2),
    ("W_ChoSoiVaCuu_LPT", "Cho soi va cuu trong tho ngu ngon cua La Phong-ten", "", "A_LaPhongTen", "HP_NuocNgoai", "G_VanNghiLuan", "~XVII", 3, 3, 3, 3, 2),
]

# --- Characters ---
CHARACTERS = [
    # id, label, work_id, abstract, conf
    ("CH_ThuyKieu", "Thuy Kieu", "W_TruyenKieu", 3, 3),
    ("CH_ThuyVan", "Thuy Van", "W_TruyenKieu", 3, 3),
    ("CH_KimTrong", "Kim Trong", "W_TruyenKieu", 3, 3),
    ("CH_MaGiamSinh", "Ma Giam Sinh", "W_TruyenKieu", 3, 3),
    ("CH_TuHai", "Tu Hai", "W_TruyenKieu", 3, 3),
    ("CH_HoanThu", "Hoan Thu", "W_TruyenKieu", 3, 3),
    ("CH_VuNuong", "Vu Nuong (Vu Thi Thiet)", "W_ChuyenNguoiConGaiNX", 3, 3),
    ("CH_TruongSinh", "Truong Sinh", "W_ChuyenNguoiConGaiNX", 3, 3),
    ("CH_LucVanTien", "Luc Van Tien", "W_LucVanTien_CuuKNN", 3, 3),
    ("CH_KieuNguyetNga", "Kieu Nguyet Nga", "W_LucVanTien_CuuKNN", 3, 3),
    ("CH_NguoiLinh_DC", "Anh linh (trong Dong chi)", "W_DongChi", 3, 3),
    ("CH_NguoiLai_TDXKK", "Nguoi lai xe Truong Son", "W_BaiThoTDXKK", 3, 3),
    ("CH_OngHai", "Ong Hai", "W_Lang", 2, 3),
    ("CH_AnhThanhNien", "Anh thanh nien (lam khi tuong)", "W_LangLeSaPa", 2, 3),
    ("CH_OngSau", "Ong Sau (cha be Thu)", "W_ChiecLuocNga", 2, 3),
    ("CH_BeThu", "Be Thu", "W_ChiecLuocNga", 2, 3),
    ("CH_NhiBenQue", "Nhi (Ben que)", "W_BenQue", 3, 3),
    ("CH_PhuongDinh", "Phuong Dinh (Nhung ngoi sao xa xoi)", "W_NhungNgoiSao_XX", 2, 3),
    ("CH_Thao", "Thao (Nhung ngoi sao xa xoi)", "W_NhungNgoiSao_XX", 2, 3),
    ("CH_NhoNgoiSao", "Nho (Nhung ngoi sao xa xoi)", "W_NhungNgoiSao_XX", 2, 3),
    ("CH_XiMong", "Xi-mong", "W_BoCuaXiMong", 2, 2),
    ("CH_PhiLip", "Bac Phi-lip", "W_BoCuaXiMong", 2, 2),
]

# --- Literary Devices ---
DEVICES = [
    # id, label, aliases, abstract, conf
    ("LD_SoSanh", "So sanh (tu tu)", "", 2, 3),
    ("LD_NhanHoa", "Nhan hoa", "", 2, 3),
    ("LD_AnDu", "An du", "", 3, 3),
    ("LD_HoanDu", "Hoan du", "", 3, 3),
    ("LD_DiepNgu", "Diep ngu", "", 2, 3),
    ("LD_DiepCauTruc", "Diep cau truc", "", 3, 3),
    ("LD_DaoNgu", "Dao ngu (dao trat tu)", "", 3, 3),
    ("LD_LietKe", "Liet ke", "", 2, 3),
    ("LD_DoiLap", "Tuong phan / doi lap", "", 3, 3),
    ("LD_CauHoiTuTu", "Cau hoi tu tu", "", 3, 3),
    ("LD_NoiQuaQuaPhong", "Noi qua, cuong dieu", "Phong dai", 3, 3),
    ("LD_NoiGiamNoiTranh", "Noi giam, noi tranh", "", 3, 3),
    ("LD_Choi_Chu", "Choi chu", "", 4, 3),
    ("LD_DienCo", "Dien co, dien tich", "", 4, 3),
    ("LD_TuongTrung", "Tuong trung / bieu tuong", "Bieu tuong", 4, 3),
    ("LD_TruongTu_Vong", "Truong tu vung", "", 3, 3),
    ("LD_TuLay", "Tu lay (goi cam giac)", "", 2, 3),
    ("LD_TuTuongHinh", "Tu tuong hinh, tu tuong thanh", "", 2, 3),
]

# --- Themes ---
THEMES = [
    ("T_TinhYeuQueHuong", "Tinh yeu que huong, dat nuoc", "", 3, 3),
    ("T_TinhDongChi", "Tinh dong chi, dong doi", "", 3, 3),
    ("T_TinhCamGiaDinh", "Tinh cam gia dinh (me con, cha con, ba chau)", "", 3, 3),
    ("T_ThanPhanPhuNu", "Than phan nguoi phu nu phong kien", "", 4, 3),
    ("T_VeDepNguoiLaoDong", "Ve dep nguoi lao dong", "", 3, 3),
    ("T_VeDepNguoiLinh", "Ve dep nguoi linh cach mang", "", 3, 3),
    ("T_LongYeuNuoc", "Long yeu nuoc", "", 3, 3),
    ("T_KhaoVongHoaBinh", "Khao vong hoa binh, cuoc song yen am", "", 4, 3),
    ("T_CaiThienSungSuc", "Cai thien va cai ac; cong ly", "", 4, 3),
    ("T_SuCoDon_TrietLy", "Su co don, triet ly nhan sinh", "", 5, 3),
    ("T_Bien_VoTan", "Thien nhien - bien ca, vu tru", "", 3, 3),
    ("T_SuChuyenGiao", "Su chuyen giao the he, truyen thong", "", 3, 3),
    ("T_ChiToDuc", "Chi hieu, dao lam nguoi", "", 3, 3),
    ("T_SuHySinh_KC", "Su hy sinh vi dat nuoc", "", 3, 3),
    ("T_NguoiMe", "Hinh anh nguoi me", "", 3, 3),
]

print(f'Van: {len(AUTHORS)} authors, {len(WORKS)} works, {len(CHARACTERS)} chars, '
      f'{len(DEVICES)} devices, {len(THEMES)} themes, {len(GENRES)} genres, {len(PERIODS)} periods')


# ======================================================================
# LESSONS
# ======================================================================
LESSONS_OLD = [
    (1, "Phong cach Ho Chi Minh"),
    (2, "Cac phuong cham hoi thoai"),
    (3, "Dau tranh cho mot the gioi hoa binh"),
    (4, "Tuyen bo the gioi ve su song con..."),
    (5, "Chuyen nguoi con gai Nam Xuong"),
    (6, "Xung ho trong hoi thoai"),
    (7, "Chuyen cu trong phu chua Trinh"),
    (8, "Hoang Le nhat thong chi - Hoi thu 14"),
    (9, "Truyen Kieu cua Nguyen Du"),
    (10, "Chi em Thuy Kieu (trich TK)"),
    (11, "Canh ngay xuan (trich TK)"),
    (12, "Kieu o lau Ngung Bich (trich TK)"),
    (13, "Ma Giam Sinh mua Kieu (trich TK)"),
    (14, "Thuy Kieu bao an bao oan (trich TK)"),
    (15, "Luc Van Tien cuu Kieu Nguyet Nga"),
    (16, "Luc Van Tien gap nan"),
    (17, "Dong chi (Chinh Huu)"),
    (18, "Bai tho ve tieu doi xe khong kinh (Pham Tien Duat)"),
    (19, "Doan thuyen danh ca (Huy Can)"),
    (20, "Bep lua (Bang Viet)"),
    (21, "Khuc hat ru nhung em be lon tren lung me"),
    (22, "Anh trang (Nguyen Duy)"),
    (23, "Lang (Kim Lan)"),
    (24, "Lang le Sa Pa (Nguyen Thanh Long)"),
    (25, "Chiec luoc nga (Nguyen Quang Sang)"),
    (26, "Co huong (Lo Tan)"),
    (27, "Nhung dua tre (Gorki)"),
    (28, "Ban ve doc sach"),
    (29, "Tieng noi cua van nghe"),
    (30, "Chuan bi hanh trang vao the ky moi"),
    (31, "Cho soi va cuu trong tho ngu ngon La Phong-ten"),
    (32, "Con co (Che Lan Vien)"),
    (33, "Mua xuan nho nho (Thanh Hai)"),
    (34, "Vieng lang Bac (Vien Phuong)"),
    (35, "Sang thu (Huu Thinh)"),
    (36, "Noi voi con (Y Phuong)"),
    (37, "May va song (Tago)"),
    (38, "Ben que (Nguyen Minh Chau)"),
    (39, "Nhung ngoi sao xa xoi (Le Minh Khue)"),
    (40, "Ro-bin-xon Cru-xo"),
    (41, "Bo cua Xi-mong"),
    (42, "Con cho Bac (Giac Lon-don)"),
    (43, "Bac Son (Nguyen Huy Tuong)"),
    (44, "Toi va chung ta (Luu Quang Vu)"),
    (45, "Tong ket phan van hoc"),
]

LESSONS_KNTT = [(i, f"KNTT Bai {i}") for i in range(1, 26)]
LESSONS_CTST = [(i, f"CTST Bai {i}") for i in range(1, 26)]
LESSONS_CD   = [(i, f"CD Bai {i}") for i in range(1, 26)]


# ======================================================================
# RELATIONSHIPS
# ======================================================================

# Author active in period
AUTHOR_ACTIVE_IN = [(a[0], a[3]) for a in AUTHORS if a[3]]

# Work authoredBy Author
AUTHORED_BY = [(w[0], w[3]) for w in WORKS]

# Work writtenIn Period
WRITTEN_IN = [(w[0], w[4]) for w in WORKS]

# Work hasGenre Genre
HAS_GENRE = [(w[0], w[5]) for w in WORKS]

# Work contains Character
CONTAINS_CHAR = [(c[2], c[0]) for c in CHARACTERS]  # (work, char)

# Work uses LiteraryDevice — manually curated (subset of important pairings)
WORK_USES_DEVICE = [
    # Truyen Kieu - most literary-rich
    ("W_TruyenKieu", "LD_AnDu"), ("W_TruyenKieu", "LD_SoSanh"),
    ("W_TruyenKieu", "LD_DienCo"), ("W_TruyenKieu", "LD_NhanHoa"),
    ("W_TruyenKieu", "LD_DiepNgu"), ("W_TruyenKieu", "LD_DoiLap"),
    ("W_TruyenKieu", "LD_TruongTu_Vong"), ("W_TruyenKieu", "LD_TuongTrung"),
    # Chuyen nguoi con gai NX
    ("W_ChuyenNguoiConGaiNX", "LD_TuongTrung"),
    ("W_ChuyenNguoiConGaiNX", "LD_DoiLap"),
    # Dong chi
    ("W_DongChi", "LD_SoSanh"), ("W_DongChi", "LD_DiepNgu"),
    ("W_DongChi", "LD_LietKe"), ("W_DongChi", "LD_TuongTrung"),
    # Bai tho tieu doi xe khong kinh
    ("W_BaiThoTDXKK", "LD_DiepNgu"), ("W_BaiThoTDXKK", "LD_TuongTrung"),
    ("W_BaiThoTDXKK", "LD_DiepCauTruc"),
    # Anh trang
    ("W_AnhTrang", "LD_NhanHoa"), ("W_AnhTrang", "LD_AnDu"),
    ("W_AnhTrang", "LD_TuongTrung"),
    # Bep lua
    ("W_BepLua", "LD_DiepNgu"), ("W_BepLua", "LD_TuongTrung"),
    ("W_BepLua", "LD_TuLay"),
    # Doan thuyen danh ca
    ("W_DoanThuyenDanhCa", "LD_NhanHoa"), ("W_DoanThuyenDanhCa", "LD_SoSanh"),
    ("W_DoanThuyenDanhCa", "LD_NoiQuaQuaPhong"),
    # Sang thu
    ("W_SangThu", "LD_NhanHoa"), ("W_SangThu", "LD_AnDu"),
    ("W_SangThu", "LD_TuLay"),
    # Mua xuan nho nho
    ("W_MuaXuanNhoNho", "LD_AnDu"), ("W_MuaXuanNhoNho", "LD_TuongTrung"),
    ("W_MuaXuanNhoNho", "LD_DiepNgu"),
    # Vieng lang Bac
    ("W_ViengLangBac", "LD_AnDu"), ("W_ViengLangBac", "LD_TuongTrung"),
    ("W_ViengLangBac", "LD_NhanHoa"),
    # Noi voi con
    ("W_NoiVoiCon", "LD_AnDu"), ("W_NoiVoiCon", "LD_DiepNgu"),
    # Con co
    ("W_ConCo", "LD_TuongTrung"), ("W_ConCo", "LD_DiepNgu"),
    # Khuc hat ru
    ("W_KhucHatRu", "LD_DiepNgu"), ("W_KhucHatRu", "LD_AnDu"),
    # Tieu thuyet / truyen ngan - less device-heavy per se
    ("W_Lang", "LD_DoiLap"),
    ("W_ChiecLuocNga", "LD_DoiLap"),
    ("W_NhungNgoiSao_XX", "LD_LietKe"),
]

# Work expresses Theme
WORK_EXPRESSES = [
    ("W_TruyenKieu", "T_ThanPhanPhuNu"),
    ("W_TruyenKieu", "T_CaiThienSungSuc"),
    ("W_TruyenKieu", "T_ChiToDuc"),
    ("W_ChuyenNguoiConGaiNX", "T_ThanPhanPhuNu"),
    ("W_ChuyenNguoiConGaiNX", "T_ChiToDuc"),
    ("W_LucVanTien_CuuKNN", "T_CaiThienSungSuc"),
    ("W_LucVanTien_CuuKNN", "T_ChiToDuc"),
    ("W_HoangLeNhatThongChi_14", "T_LongYeuNuoc"),
    ("W_DongChi", "T_TinhDongChi"),
    ("W_DongChi", "T_VeDepNguoiLinh"),
    ("W_BaiThoTDXKK", "T_TinhDongChi"),
    ("W_BaiThoTDXKK", "T_VeDepNguoiLinh"),
    ("W_AnhTrang", "T_SuChuyenGiao"),
    ("W_AnhTrang", "T_SuCoDon_TrietLy"),
    ("W_BepLua", "T_TinhCamGiaDinh"),
    ("W_BepLua", "T_NguoiMe"),
    ("W_KhucHatRu", "T_NguoiMe"),
    ("W_KhucHatRu", "T_TinhCamGiaDinh"),
    ("W_DoanThuyenDanhCa", "T_VeDepNguoiLaoDong"),
    ("W_DoanThuyenDanhCa", "T_Bien_VoTan"),
    ("W_SangThu", "T_SuCoDon_TrietLy"),
    ("W_MuaXuanNhoNho", "T_TinhYeuQueHuong"),
    ("W_MuaXuanNhoNho", "T_KhaoVongHoaBinh"),
    ("W_ViengLangBac", "T_LongYeuNuoc"),
    ("W_ViengLangBac", "T_TinhCamGiaDinh"),
    ("W_NoiVoiCon", "T_TinhCamGiaDinh"),
    ("W_NoiVoiCon", "T_TinhYeuQueHuong"),
    ("W_ConCo", "T_NguoiMe"),
    ("W_ConCo", "T_TinhCamGiaDinh"),
    ("W_Lang", "T_LongYeuNuoc"),
    ("W_Lang", "T_TinhYeuQueHuong"),
    ("W_LangLeSaPa", "T_VeDepNguoiLaoDong"),
    ("W_LangLeSaPa", "T_TinhYeuQueHuong"),
    ("W_ChiecLuocNga", "T_TinhCamGiaDinh"),
    ("W_ChiecLuocNga", "T_SuHySinh_KC"),
    ("W_BenQue", "T_SuCoDon_TrietLy"),
    ("W_NhungNgoiSao_XX", "T_VeDepNguoiLinh"),
    ("W_NhungNgoiSao_XX", "T_SuHySinh_KC"),
    ("W_BacSon", "T_LongYeuNuoc"),
    ("W_BoCuaXiMong", "T_TinhCamGiaDinh"),
    ("W_NhungDuaTreGorki", "T_TinhCamGiaDinh"),
]

# Related works (pairs often compared)
RELATED = [
    ("W_DongChi", "W_BaiThoTDXKK"),   # 2 bai tho ve nguoi linh
    ("W_BepLua", "W_KhucHatRu"),       # 2 bai tho ve ba/me
    ("W_MuaXuanNhoNho", "W_ViengLangBac"),  # cung thoi ky & chu de cach mang
    ("W_Lang", "W_LangLeSaPa"),        # 2 truyen ngan khang chien
    ("W_ChiecLuocNga", "W_NhungNgoiSao_XX"),  # 2 truyen ngan khang chien My
]

# Similarities (pairs with shared traits for comparison questions)
SIMILARITIES = [
    ("W_DongChi", "W_BaiThoTDXKK"),
    ("W_BepLua", "W_KhucHatRu"),
    ("W_BepLua", "W_NoiVoiCon"),    # tinh gia dinh
    ("W_MuaXuanNhoNho", "W_ViengLangBac"),
    ("CH_VuNuong", "CH_ThuyKieu"),    # 2 nhan vat phu nu trung dai
    ("A_NguyenDu", "A_NguyenDinhChieu"),  # 2 tac gia trung dai
    ("LD_AnDu", "LD_HoanDu"),
    ("LD_SoSanh", "LD_NhanHoa"),
]

# Contrasts
CONTRASTS = [
    ("W_DongChi", "W_BaiThoTDXKK"),   # same theme, khac phong cach
    ("W_TruyenKieu", "W_LucVanTien_CuuKNN"),  # 2 truyen tho cung trung dai nhung khac
    ("CH_ThuyKieu", "CH_MaGiamSinh"),  # nhan vat thien/ac
    ("LD_SoSanh", "LD_AnDu"),          # 2 bien phap tuong doi khac nhau
    ("T_VeDepNguoiLinh", "T_ThanPhanPhuNu"),
]

print(f'  + {len(AUTHOR_ACTIVE_IN)} active-in, {len(AUTHORED_BY)} authored, '
      f'{len(WRITTEN_IN)} written-in, {len(HAS_GENRE)} genre, '
      f'{len(CONTAINS_CHAR)} chars, {len(WORK_USES_DEVICE)} uses-device, '
      f'{len(WORK_EXPRESSES)} themes, {len(RELATED)} related, '
      f'{len(SIMILARITIES)} sim, {len(CONTRASTS)} contrast')
