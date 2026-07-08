"""
Hoa 9 ontology generator.

Schema philosophy:
  - Chemistry knowledge is CATEGORICAL + REACTIVE. A substance belongs to a
    class, has properties, participates in reactions.
  - Difficulty is driven by:
      (a) number of substances/reactions involved in a question,
      (b) whether it needs balancing/stoichiometry (compute-heavy),
      (c) abstraction (specific substance vs. general class behavior),
      (d) reaction-type recognition (many reaction types = more to distinguish),
      (e) multi-step synthesis (sequence of reactions).

Classes:
  - Substance:       a specific chemical (HCl, NaOH, CaCO3, C2H5OH...)
  - SubstanceClass:  type of substance (axit, bazo, muoi, kim loai...)
  - Reaction:        a specific reaction instance (HCl + NaOH -> NaCl + H2O)
  - ReactionType:    type of reaction (trung hoa, the, phan huy, OX-K...)
  - Property:        chemical/physical property
  - FunctionalGroup: -OH, -COOH, etc.
  - Process:         industrial process (dien phan NaCl, luyen thep...)
  - Concept:         general concept (hoa tri, bang tuan hoan, pH, chu ki...)
  - LessonUnit, Textbook
"""

from pathlib import Path
ROOT = Path(__file__).resolve().parent

HEADER = """\
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix chem: <http://edu.vn/chem9/ontology#> .

<http://edu.vn/chem9/ontology> a owl:Ontology ;
    rdfs:label "Ontology Hoa 9 - Cold-start Question Difficulty Estimation"@vi ;
    owl:versionInfo "0.1.0" .
"""

SCHEMA = """\
#################################################################
#   CLASSES
#################################################################

chem:ChemEntity a owl:Class ; rdfs:label "Thuc the Hoa hoc"@vi .
chem:Substance       a owl:Class ; rdfs:subClassOf chem:ChemEntity ; rdfs:label "Chat"@vi .
chem:SubstanceClass  a owl:Class ; rdfs:subClassOf chem:ChemEntity ; rdfs:label "Loai chat"@vi .
chem:Reaction        a owl:Class ; rdfs:subClassOf chem:ChemEntity ; rdfs:label "Phan ung"@vi .
chem:ReactionType    a owl:Class ; rdfs:subClassOf chem:ChemEntity ; rdfs:label "Loai phan ung"@vi .
chem:Property        a owl:Class ; rdfs:subClassOf chem:ChemEntity ; rdfs:label "Tinh chat"@vi .
chem:FunctionalGroup a owl:Class ; rdfs:subClassOf chem:ChemEntity ; rdfs:label "Nhom chuc"@vi .
chem:Process         a owl:Class ; rdfs:subClassOf chem:ChemEntity ; rdfs:label "Quy trinh san xuat"@vi .
chem:Concept         a owl:Class ; rdfs:subClassOf chem:ChemEntity ; rdfs:label "Khai niem Hoa hoc"@vi .
chem:LessonUnit      a owl:Class ; rdfs:label "Bai hoc SGK"@vi .
chem:Textbook        a owl:Class ; rdfs:label "Bo SGK"@vi .

#################################################################
#   OBJECT PROPERTIES
#################################################################

chem:prerequisiteOf a owl:ObjectProperty , owl:TransitiveProperty ; rdfs:label "la tien de cua"@vi .

chem:instanceOf a owl:ObjectProperty ;
    rdfs:domain chem:Substance ; rdfs:range chem:SubstanceClass ;
    rdfs:label "thuoc loai chat"@vi .

chem:hasProperty a owl:ObjectProperty ;
    rdfs:range chem:Property ; rdfs:label "co tinh chat"@vi .

chem:reactsWith a owl:ObjectProperty , owl:SymmetricProperty ;
    rdfs:domain chem:Substance ; rdfs:range chem:Substance ;
    rdfs:label "tac dung voi"@vi .

chem:reactant a owl:ObjectProperty ;
    rdfs:domain chem:Reaction ; rdfs:range chem:Substance ;
    rdfs:label "chat tham gia"@vi .

chem:product a owl:ObjectProperty ;
    rdfs:domain chem:Reaction ; rdfs:range chem:Substance ;
    rdfs:label "chat san pham"@vi .

chem:reactionType a owl:ObjectProperty ;
    rdfs:domain chem:Reaction ; rdfs:range chem:ReactionType ;
    rdfs:label "loai phan ung"@vi .

chem:contains a owl:ObjectProperty ;
    rdfs:domain chem:Substance ; rdfs:range chem:FunctionalGroup ;
    rdfs:label "chua nhom chuc"@vi .

chem:produces a owl:ObjectProperty ;
    rdfs:domain chem:Process ; rdfs:range chem:Substance ;
    rdfs:label "san xuat ra"@vi .

chem:appearsInLesson a owl:ObjectProperty ; rdfs:range chem:LessonUnit ; rdfs:label "xuat hien trong bai"@vi .
chem:partOfTextbook a owl:ObjectProperty ; rdfs:range chem:Textbook ; rdfs:label "thuoc bo SGK"@vi .

chem:similarTo a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "tuong tu"@vi .
chem:contrastsWith a owl:ObjectProperty , owl:SymmetricProperty ; rdfs:label "khac biet"@vi .

#################################################################
#   DATA PROPERTIES
#################################################################

chem:abstractness a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "1=chat cu the, 5=khai niem rat truu tuong (xu the hoa hoc)"@vi .
chem:bloomLevel a owl:DatatypeProperty ; rdfs:range xsd:integer .
chem:frequencyInTextbook a owl:DatatypeProperty ; rdfs:range xsd:integer .
chem:curriculumPosition a owl:DatatypeProperty ; rdfs:range xsd:integer .
chem:formula a owl:DatatypeProperty ; rdfs:range xsd:string ;
    rdfs:comment "Cong thuc hoa hoc"@vi .
chem:balancingComplexity a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "Do phuc tap can bang PTHH (1-5)"@vi .
chem:stepsInSynthesis a owl:DatatypeProperty ; rdfs:range xsd:integer ;
    rdfs:comment "So buoc trong chuoi tong hop (cho Process)"@vi .
chem:aliases a owl:DatatypeProperty ; rdfs:range xsd:string .
chem:confidence a owl:DatatypeProperty ; rdfs:range xsd:integer .

#################################################################
#   TEXTBOOKS
#################################################################

chem:TB_Old a chem:Textbook ; rdfs:label "SGK Hoa 9 (bo cu)"@vi ; chem:confidence 3 .
chem:TB_KNTT a chem:Textbook ; rdfs:label "SGK KHTN 9 - Ket noi tri thuc"@vi ; chem:confidence 3 .
chem:TB_CTST a chem:Textbook ; rdfs:label "SGK KHTN 9 - Chan troi sang tao"@vi ; chem:confidence 3 .
chem:TB_CD a chem:Textbook ; rdfs:label "SGK KHTN 9 - Canh Dieu"@vi ; chem:confidence 3 .
"""

# ======================================================================
# DATA
# ======================================================================

# --- Substance classes ---
SUBSTANCE_CLASSES = [
    # id, label, aliases, abstract, conf
    ("SC_Oxit", "Oxit", "", 3, 3),
    ("SC_OxitAxit", "Oxit axit", "", 3, 3),
    ("SC_OxitBazo", "Oxit bazo", "", 3, 3),
    ("SC_OxitLuongTinh", "Oxit luong tinh", "", 4, 3),
    ("SC_OxitTrungTinh", "Oxit trung tinh", "", 4, 3),
    ("SC_Axit", "Axit", "", 3, 3),
    ("SC_AxitManh", "Axit manh", "", 3, 3),
    ("SC_AxitYeu", "Axit yeu", "", 3, 3),
    ("SC_Bazo", "Bazo", "", 3, 3),
    ("SC_BazoTan", "Bazo tan (Kiem)", "Kiem", 3, 3),
    ("SC_BazoKhongTan", "Bazo khong tan", "", 3, 3),
    ("SC_Muoi", "Muoi", "", 3, 3),
    ("SC_MuoiAxit", "Muoi axit", "", 3, 3),
    ("SC_MuoiTrungHoa", "Muoi trung hoa", "", 3, 3),
    ("SC_KimLoai", "Kim loai", "", 3, 3),
    ("SC_KimLoaiKiem", "Kim loai kiem", "", 3, 3),
    ("SC_KimLoaiKiemTho", "Kim loai kiem tho", "", 3, 3),
    ("SC_PhiKim", "Phi kim", "", 3, 3),
    ("SC_Hidrocacbon", "Hydrocarbon", "Hidro cacbon", 3, 3),
    ("SC_HCNoi", "Hydrocarbon no", "Ankan", 3, 3),
    ("SC_HCKhong", "Hydrocarbon khong no", "", 3, 3),
    ("SC_HCThom", "Hydrocarbon thom", "Aren|Benzen", 3, 3),
    ("SC_Ancol", "Ancol", "Ruou|Alcohol", 3, 3),
    ("SC_Axit_HC", "Axit huu co", "Axit cacboxylic", 3, 3),
    ("SC_Este", "Este", "Ester", 3, 3),
    ("SC_Gluxit", "Gluxit (Cacbohidrat)", "Carbohydrate", 3, 3),
    ("SC_Polime", "Polyme", "Polymer", 3, 3),
]

# --- Specific substances ---
SUBSTANCES = [
    # id, label, formula, aliases, class_id, freq, abstract, conf
    # Oxit
    ("S_CaO", "Canxi oxit", "CaO", "Voi song", "SC_OxitBazo", 12, 1, 3),
    ("S_SO2", "Luu huynh dioxit", "SO2", "Khi sunfuro", "SC_OxitAxit", 10, 1, 3),
    ("S_SO3", "Luu huynh trioxit", "SO3", "", "SC_OxitAxit", 6, 1, 3),
    ("S_CO2", "Cacbon dioxit", "CO2", "Khi cacbonic", "SC_OxitAxit", 12, 1, 3),
    ("S_CO", "Cacbon monoxit", "CO", "", "SC_OxitTrungTinh", 6, 1, 3),
    ("S_P2O5", "Diphotpho pentaoxit", "P2O5", "", "SC_OxitAxit", 5, 1, 3),
    ("S_Al2O3", "Nhom oxit", "Al2O3", "", "SC_OxitLuongTinh", 6, 1, 3),
    ("S_Fe2O3", "Sat(III) oxit", "Fe2O3", "", "SC_OxitBazo", 8, 1, 3),
    ("S_CuO", "Dong(II) oxit", "CuO", "", "SC_OxitBazo", 6, 1, 3),
    ("S_Na2O", "Natri oxit", "Na2O", "", "SC_OxitBazo", 5, 1, 3),
    # Axit
    ("S_HCl", "Axit clohidric", "HCl", "", "SC_AxitManh", 15, 1, 3),
    ("S_H2SO4", "Axit sunfuric", "H2SO4", "", "SC_AxitManh", 15, 1, 3),
    ("S_HNO3", "Axit nitric", "HNO3", "", "SC_AxitManh", 10, 1, 3),
    ("S_H2CO3", "Axit cacbonic", "H2CO3", "", "SC_AxitYeu", 5, 1, 3),
    ("S_H3PO4", "Axit photphoric", "H3PO4", "", "SC_AxitYeu", 3, 1, 3),
    ("S_H2SO3", "Axit sunfuro", "H2SO3", "", "SC_AxitYeu", 3, 1, 3),
    ("S_CH3COOH", "Axit axetic", "CH3COOH", "Giam", "SC_Axit_HC", 12, 1, 3),
    # Bazo
    ("S_NaOH", "Natri hidroxit", "NaOH", "Xut", "SC_BazoTan", 15, 1, 3),
    ("S_KOH", "Kali hidroxit", "KOH", "", "SC_BazoTan", 8, 1, 3),
    ("S_CaOH2", "Canxi hidroxit", "Ca(OH)2", "Voi toi", "SC_BazoTan", 10, 1, 3),
    ("S_BaOH2", "Bari hidroxit", "Ba(OH)2", "", "SC_BazoTan", 5, 1, 3),
    ("S_CuOH2", "Dong(II) hidroxit", "Cu(OH)2", "", "SC_BazoKhongTan", 5, 1, 3),
    ("S_FeOH3", "Sat(III) hidroxit", "Fe(OH)3", "", "SC_BazoKhongTan", 5, 1, 3),
    ("S_AlOH3", "Nhom hidroxit", "Al(OH)3", "", "SC_BazoKhongTan", 6, 1, 3),
    # Muoi
    ("S_NaCl", "Natri clorua", "NaCl", "Muoi an", "SC_MuoiTrungHoa", 15, 1, 3),
    ("S_CaCO3", "Canxi cacbonat", "CaCO3", "Da voi", "SC_MuoiTrungHoa", 12, 1, 3),
    ("S_NaHCO3", "Natri hidrocacbonat", "NaHCO3", "Thuoc muoi", "SC_MuoiAxit", 5, 1, 3),
    ("S_Na2CO3", "Natri cacbonat", "Na2CO3", "Soda", "SC_MuoiTrungHoa", 5, 1, 3),
    ("S_CuSO4", "Dong(II) sunfat", "CuSO4", "", "SC_MuoiTrungHoa", 8, 1, 3),
    ("S_FeCl3", "Sat(III) clorua", "FeCl3", "", "SC_MuoiTrungHoa", 5, 1, 3),
    ("S_BaSO4", "Bari sunfat", "BaSO4", "", "SC_MuoiTrungHoa", 4, 1, 3),
    # Kim loai
    ("S_Na", "Natri", "Na", "", "SC_KimLoaiKiem", 10, 1, 3),
    ("S_K", "Kali", "K", "", "SC_KimLoaiKiem", 6, 1, 3),
    ("S_Ca", "Canxi", "Ca", "", "SC_KimLoaiKiemTho", 8, 1, 3),
    ("S_Mg", "Magie", "Mg", "", "SC_KimLoai", 8, 1, 3),
    ("S_Al", "Nhom", "Al", "", "SC_KimLoai", 10, 1, 3),
    ("S_Fe", "Sat", "Fe", "", "SC_KimLoai", 15, 1, 3),
    ("S_Cu", "Dong", "Cu", "", "SC_KimLoai", 8, 1, 3),
    ("S_Zn", "Kem", "Zn", "", "SC_KimLoai", 6, 1, 3),
    ("S_Ag", "Bac", "Ag", "", "SC_KimLoai", 4, 1, 3),
    ("S_Au", "Vang", "Au", "", "SC_KimLoai", 3, 1, 3),
    # Phi kim
    ("S_Cl2", "Clo", "Cl2", "", "SC_PhiKim", 10, 1, 3),
    ("S_O2", "Oxi", "O2", "", "SC_PhiKim", 12, 1, 3),
    ("S_H2", "Hidro", "H2", "", "SC_PhiKim", 12, 1, 3),
    ("S_N2", "Nito", "N2", "", "SC_PhiKim", 5, 1, 3),
    ("S_C_element", "Cacbon", "C", "", "SC_PhiKim", 8, 1, 3),
    ("S_S_element", "Luu huynh", "S", "", "SC_PhiKim", 6, 1, 3),
    # Hydrocarbon
    ("S_CH4", "Metan", "CH4", "Khi bun|Khi mo dau", "SC_HCNoi", 10, 1, 3),
    ("S_C2H4", "Etilen", "C2H4", "Ethylene", "SC_HCKhong", 8, 1, 3),
    ("S_C2H2", "Axetilen", "C2H2", "Acetylene", "SC_HCKhong", 8, 1, 3),
    ("S_C6H6", "Benzen", "C6H6", "Benzene", "SC_HCThom", 8, 1, 3),
    # Dan xuat hydrocarbon
    ("S_C2H5OH", "Ancol etylic", "C2H5OH", "Ruou etylic|Ethanol", "SC_Ancol", 12, 1, 3),
    ("S_CH3OH", "Metanol", "CH3OH", "", "SC_Ancol", 3, 1, 3),
    ("S_EsteC2H5", "Etyl axetat", "CH3COOC2H5", "", "SC_Este", 4, 1, 3),
    # Gluxit
    ("S_Glucose", "Glucoz", "C6H12O6", "Glucozo|Glucose", "SC_Gluxit", 8, 1, 3),
    ("S_Saccarose", "Saccaroz", "C12H22O11", "Saccarozo|Sucrose", "SC_Gluxit", 6, 1, 3),
    ("S_TinhBot", "Tinh bot", "(C6H10O5)n", "", "SC_Gluxit", 6, 1, 3),
    ("S_Xenluloz", "Xenluloz", "(C6H10O5)n", "Xenlulozo|Cellulose", "SC_Gluxit", 5, 1, 3),
    # Polyme
    ("S_Poli_Ethylene", "Polietilen", "(-CH2-CH2-)n", "PE", "SC_Polime", 3, 2, 3),
    ("S_Poli_VinylClorua", "Polivinyl clorua", "(-CH2-CHCl-)n", "PVC", "SC_Polime", 3, 2, 3),
    # Water & base
    ("S_H2O", "Nuoc", "H2O", "", None, 20, 1, 3),
]

# --- Reaction Types ---
REACTION_TYPES = [
    ("RT_TrungHoa", "Phan ung trung hoa", "", 3, 2, 3),
    ("RT_PhanHuy", "Phan ung phan huy", "", 3, 2, 3),
    ("RT_HoaHop", "Phan ung hoa hop", "", 3, 2, 3),
    ("RT_The", "Phan ung the", "", 3, 2, 3),
    ("RT_TraoDoi", "Phan ung trao doi", "", 3, 2, 3),
    ("RT_OXK", "Phan ung oxi hoa - khu", "OXK", 4, 3, 3),
    ("RT_Cong", "Phan ung cong", "", 3, 2, 3),
    ("RT_TrungHop", "Phan ung trung hop", "", 4, 3, 3),
    ("RT_ThuyPhan", "Phan ung thuy phan", "", 4, 3, 3),
    ("RT_Este_Hoa", "Phan ung este hoa", "", 4, 3, 3),
    ("RT_LenMen", "Phan ung len men", "", 3, 2, 3),
    ("RT_Chay", "Phan ung chay", "Dot chay", 2, 2, 3),
]

# --- Properties ---
PROPERTIES = [
    ("P_TanTrongNuoc", "Tan trong nuoc", "", 2, 2, 3),
    ("P_PhanUngVoiAxit", "Phan ung voi axit", "", 3, 2, 3),
    ("P_PhanUngVoiBazo", "Phan ung voi bazo", "", 3, 2, 3),
    ("P_PhanUngVoiOxi", "Phan ung voi oxi (chay)", "", 2, 2, 3),
    ("P_PhanUngVoiNuoc", "Phan ung voi nuoc", "", 3, 2, 3),
    ("P_PhanUngVoiKimLoai", "Phan ung voi kim loai", "", 3, 2, 3),
    ("P_LamDoiMauQT", "Lam doi mau quy tim", "", 2, 2, 3),
    ("P_DoiMauPhenolphthalein", "Doi mau phenolphtalein", "", 2, 2, 3),
    ("P_TacDungVoiPhiKim", "Tac dung voi phi kim", "", 3, 2, 3),
    ("P_DienPhanDuocDDND", "Dien phan duoc dung dich", "", 4, 3, 3),
]

# --- Functional Groups ---
FUNCTIONAL_GROUPS = [
    ("FG_OH", "Nhom hidroxyl -OH", "-OH", 3, 3),
    ("FG_COOH", "Nhom cacboxyl -COOH", "-COOH", 4, 3),
    ("FG_Este_Link", "Lien ket este -COO-", "-COO-", 4, 3),
    ("FG_DoiLK", "Lien ket doi C=C", "", 3, 3),
    ("FG_BaLK", "Lien ket ba C=C=C", "Lien ket ba", 3, 3),
    ("FG_Vong6", "Vong benzen", "", 4, 3),
]

# --- Concepts ---
CONCEPTS = [
    ("C_HoaTri", "Hoa tri", "", 3, 2, 3),
    ("C_PTHH", "Phuong trinh hoa hoc", "PTHH", 3, 2, 3),
    ("C_CanBangPTHH", "Can bang phuong trinh hoa hoc", "Can bang PTHH", 3, 3, 3),
    ("C_BangTuanHoan", "Bang tuan hoan cac nguyen to hoa hoc", "BTH", 4, 3, 3),
    ("C_ChuKi", "Chu ki (BTH)", "", 4, 3, 3),
    ("C_NhomA", "Nhom A trong BTH", "", 4, 3, 3),
    ("C_DinhLuatTuanHoan", "Dinh luat tuan hoan", "", 5, 3, 3),
    ("C_DayHoatDongKimLoai", "Day hoat dong hoa hoc cua kim loai", "Day hoat dong", 4, 3, 3),
    ("C_DieuChe_KL_1", "Dieu che kim loai (luyen kim)", "", 4, 3, 3),
    ("C_pH", "Do pH cua dung dich", "pH", 3, 2, 3),
    ("C_MolKhoiLuong", "Mol va khoi luong mol", "", 3, 2, 3),
    ("C_NongDoDungDich", "Nong do dung dich (C%, CM)", "", 3, 2, 3),
    ("C_SuChuyenHoa_DongDang", "Su chuyen hoa cac chat huu co", "", 4, 3, 3),
    ("C_DongPhan", "Dong phan", "", 4, 3, 3),
]

# --- Processes (quy trinh san xuat) ---
PROCESSES = [
    ("PR_DienPhanNaCl", "Dien phan dung dich NaCl bao hoa", "San xuat NaOH", 3, 4, 3, 3),
    ("PR_LuyenGang", "Luyen gang trong lo cao", "", 4, 4, 3, 3),
    ("PR_LuyenThep", "Luyen thep tu gang", "", 4, 4, 3, 3),
    ("PR_SanXuat_H2SO4", "San xuat H2SO4 cong nghiep", "", 3, 4, 3, 3),
    ("PR_SanXuat_NH3", "San xuat NH3 (tong hop Haber)", "", 3, 4, 3, 2),
    ("PR_LenMenRuou", "Len men ruou etylic tu tinh bot", "", 3, 3, 3, 3),
    ("PR_LenMenGiam", "Len men giam tu ruou", "", 2, 3, 2, 3),
    ("PR_SanXuat_Voi", "Nung voi (San xuat voi song)", "", 2, 2, 2, 3),
    ("PR_SanXuatXiMang", "San xuat xi mang", "", 3, 3, 2, 3),
    ("PR_SanXuatThuyTinh", "San xuat thuy tinh", "", 2, 3, 2, 3),
]

# --- Reactions (phan ung cu the - cac vi du quan trong) ---
REACTIONS = [
    # id, label, aliases, reaction_type, balancing_complexity, bloom, conf
    ("R_NaOH_HCl", "NaOH + HCl -> NaCl + H2O", "Trung hoa manh", "RT_TrungHoa", 1, 2, 3),
    ("R_CaO_H2O", "CaO + H2O -> Ca(OH)2", "Voi song + nuoc", "RT_HoaHop", 1, 2, 3),
    ("R_CO2_CaOH2", "CO2 + Ca(OH)2 -> CaCO3 + H2O", "CO2 lam duc nuoc voi", "RT_TraoDoi", 2, 2, 3),
    ("R_CaCO3_Nhiet", "CaCO3 -> CaO + CO2 (t)", "Nung da voi", "RT_PhanHuy", 1, 2, 3),
    ("R_Zn_HCl", "Zn + 2HCl -> ZnCl2 + H2", "Kem + axit", "RT_The", 1, 2, 3),
    ("R_Fe_CuSO4", "Fe + CuSO4 -> FeSO4 + Cu", "Sat day dong", "RT_The", 1, 2, 3),
    ("R_Fe_HCl", "Fe + 2HCl -> FeCl2 + H2", "Sat + axit loang", "RT_The", 1, 2, 3),
    ("R_Cu_H2SO4dac", "Cu + 2H2SO4d -> CuSO4 + SO2 + 2H2O", "Cu + H2SO4 dac nong", "RT_OXK", 3, 3, 3),
    ("R_Al_NaOH", "2Al + 2NaOH + 2H2O -> 2NaAlO2 + 3H2", "Nhom + kiem", "RT_OXK", 3, 3, 3),
    ("R_CH4_Cl2", "CH4 + Cl2 -> CH3Cl + HCl (as)", "Metan + clo", "RT_The", 2, 3, 3),
    ("R_C2H4_Br2", "C2H4 + Br2 -> C2H4Br2", "Etilen mat mau brom", "RT_Cong", 1, 2, 3),
    ("R_C2H2_H2", "C2H2 + 2H2 -> C2H6 (Ni)", "Cong hidro", "RT_Cong", 1, 2, 3),
    ("R_C2H5OH_Na", "2C2H5OH + 2Na -> 2C2H5ONa + H2", "Ruou + natri", "RT_The", 2, 3, 3),
    ("R_CH3COOH_NaOH", "CH3COOH + NaOH -> CH3COONa + H2O", "Axit axetic + kiem", "RT_TrungHoa", 1, 2, 3),
    ("R_CH3COOH_C2H5OH", "CH3COOH + C2H5OH -> CH3COOC2H5 + H2O", "Este hoa", "RT_Este_Hoa", 1, 3, 3),
    ("R_Glucose_Fermentation", "C6H12O6 -> 2C2H5OH + 2CO2", "Len men ruou", "RT_LenMen", 2, 2, 3),
    ("R_C_O2", "C + O2 -> CO2", "Dot cacbon", "RT_Chay", 1, 1, 3),
    ("R_H2_O2", "2H2 + O2 -> 2H2O", "Hidro chay", "RT_Chay", 1, 1, 3),
    ("R_SO2_O2_V2O5", "2SO2 + O2 -> 2SO3 (V2O5)", "Oxi hoa SO2", "RT_OXK", 2, 3, 3),
]

print(f"Hoa: {len(SUBSTANCE_CLASSES)} classes, {len(SUBSTANCES)} substances, "
      f"{len(REACTIONS)} reactions, {len(REACTION_TYPES)} rxn types, "
      f"{len(PROPERTIES)} props, {len(FUNCTIONAL_GROUPS)} FGs, {len(CONCEPTS)} concepts, "
      f"{len(PROCESSES)} processes")


# ======================================================================
# LESSONS (approximated - bo cu)
# ======================================================================
LESSONS_OLD = [
    # Chuong I: Cac loai hop chat vo co
    (1, "Tinh chat hoa hoc cua oxit"), (2, "Mot so oxit quan trong"),
    (3, "Tinh chat hoa hoc cua axit"), (4, "Mot so axit quan trong"),
    (5, "Luyen tap: tinh chat cua oxit va axit"), (6, "Thuc hanh: tinh chat hoa hoc"),
    (7, "Tinh chat hoa hoc cua bazo"), (8, "Mot so bazo quan trong (NaOH, Ca(OH)2)"),
    (9, "Tinh chat hoa hoc cua muoi"), (10, "Mot so muoi quan trong"),
    (11, "Phan bon hoa hoc"), (12, "Moi quan he giua cac loai hop chat vo co"),
    (13, "Luyen tap chuong I"), (14, "Thuc hanh"),
    # Chuong II: Kim loai
    (15, "Tinh chat vat li cua kim loai"), (16, "Tinh chat hoa hoc cua kim loai"),
    (17, "Day hoat dong hoa hoc cua kim loai"), (18, "Nhom"),
    (19, "Sat"), (20, "Hop kim: gang, thep"),
    (21, "Su an mon kim loai"), (22, "Luyen tap chuong II"),
    (23, "Thuc hanh"),
    # Chuong III: Phi kim. Bang tuan hoan
    (24, "Tinh chat cua phi kim"), (25, "Clo"), (26, "Cacbon"),
    (27, "Cac oxit cua cacbon"), (28, "Axit cacbonic va muoi cacbonat"),
    (29, "Silic. Cong nghiep silicat"), (30, "So luoc bang tuan hoan cac nguyen to hoa hoc"),
    (31, "Luyen tap chuong III"), (32, "Thuc hanh"),
    # Chuong IV: Hidrocacbon
    (33, "Khai niem ve hop chat huu co va hoa hoc huu co"),
    (34, "Cau tao phan tu hop chat huu co"),
    (35, "Metan"), (36, "Etilen"), (37, "Axetilen"),
    (38, "Benzen"), (39, "Dau mo va khi thien nhien"),
    (40, "Nhien lieu"), (41, "Luyen tap chuong IV"), (42, "Thuc hanh"),
    # Chuong V: Dan xuat hidrocacbon. Polime
    (43, "Ruou etylic"), (44, "Axit axetic"), (45, "Moi lien he giua etilen, ruou etylic, axit axetic"),
    (46, "Chat beo"), (47, "Luyen tap ruou, axit, chat beo"), (48, "Thuc hanh"),
    (49, "Glucoz"), (50, "Saccaroz"), (51, "Tinh bot, xenluloz"),
    (52, "Protein"), (53, "Polime"), (54, "Thuc hanh"),
    (55, "On tap cuoi nam"),
]

LESSONS_KNTT = [(i, f"KNTT Bai {i}") for i in range(1, 31)]
LESSONS_CTST = [(i, f"CTST Bai {i}") for i in range(1, 31)]
LESSONS_CD   = [(i, f"CD Bai {i}") for i in range(1, 31)]


# ======================================================================
# RELATIONSHIPS
# ======================================================================

# Substance instanceOf SubstanceClass - built from S_* rows above
INSTANCE_OF = [(sid, cls) for (sid, _, _, _, cls, _, _, _) in SUBSTANCES if cls]

# Has property
HAS_PROPERTY = [
    ("SC_Axit", "P_LamDoiMauQT"),
    ("SC_Axit", "P_PhanUngVoiBazo"),
    ("SC_Axit", "P_PhanUngVoiKimLoai"),
    ("SC_BazoTan", "P_DoiMauPhenolphthalein"),
    ("SC_BazoTan", "P_TanTrongNuoc"),
    ("SC_Bazo", "P_PhanUngVoiAxit"),
    ("SC_KimLoai", "P_PhanUngVoiOxi"),
    ("SC_KimLoai", "P_PhanUngVoiPhiKim"),
    ("SC_KimLoaiKiem", "P_PhanUngVoiNuoc"),
    ("SC_KimLoaiKiemTho", "P_PhanUngVoiNuoc"),
    ("SC_OxitAxit", "P_PhanUngVoiBazo"),
    ("SC_OxitBazo", "P_PhanUngVoiAxit"),
    ("SC_OxitLuongTinh", "P_PhanUngVoiAxit"),
    ("SC_OxitLuongTinh", "P_PhanUngVoiBazo"),
]

# Contains functional group
CONTAINS = [
    ("S_C2H5OH", "FG_OH"),
    ("S_CH3OH", "FG_OH"),
    ("S_CH3COOH", "FG_COOH"),
    ("S_EsteC2H5", "FG_Este_Link"),
    ("S_C2H4", "FG_DoiLK"),
    ("S_C2H2", "FG_BaLK"),
    ("S_C6H6", "FG_Vong6"),
]

# Reaction reactants/products - built from REACTIONS plus explicit lists
# For demo we'll add a few explicit ones
REACTION_REACTANTS = [
    ("R_NaOH_HCl", "S_NaOH"), ("R_NaOH_HCl", "S_HCl"),
    ("R_CaO_H2O", "S_CaO"), ("R_CaO_H2O", "S_H2O"),
    ("R_CO2_CaOH2", "S_CO2"), ("R_CO2_CaOH2", "S_CaOH2"),
    ("R_CaCO3_Nhiet", "S_CaCO3"),
    ("R_Zn_HCl", "S_Zn"), ("R_Zn_HCl", "S_HCl"),
    ("R_Fe_CuSO4", "S_Fe"), ("R_Fe_CuSO4", "S_CuSO4"),
    ("R_Fe_HCl", "S_Fe"), ("R_Fe_HCl", "S_HCl"),
    ("R_Al_NaOH", "S_Al"), ("R_Al_NaOH", "S_NaOH"), ("R_Al_NaOH", "S_H2O"),
    ("R_CH4_Cl2", "S_CH4"), ("R_CH4_Cl2", "S_Cl2"),
    ("R_C2H4_Br2", "S_C2H4"),
    ("R_C2H5OH_Na", "S_C2H5OH"), ("R_C2H5OH_Na", "S_Na"),
    ("R_CH3COOH_NaOH", "S_CH3COOH"), ("R_CH3COOH_NaOH", "S_NaOH"),
    ("R_CH3COOH_C2H5OH", "S_CH3COOH"), ("R_CH3COOH_C2H5OH", "S_C2H5OH"),
    ("R_Glucose_Fermentation", "S_Glucose"),
    ("R_C_O2", "S_C_element"), ("R_C_O2", "S_O2"),
    ("R_H2_O2", "S_H2"), ("R_H2_O2", "S_O2"),
    ("R_SO2_O2_V2O5", "S_SO2"), ("R_SO2_O2_V2O5", "S_O2"),
]

REACTION_PRODUCTS = [
    ("R_NaOH_HCl", "S_NaCl"), ("R_NaOH_HCl", "S_H2O"),
    ("R_CaO_H2O", "S_CaOH2"),
    ("R_CO2_CaOH2", "S_CaCO3"), ("R_CO2_CaOH2", "S_H2O"),
    ("R_CaCO3_Nhiet", "S_CaO"), ("R_CaCO3_Nhiet", "S_CO2"),
    ("R_Zn_HCl", "S_H2"),
    ("R_Fe_CuSO4", "S_Cu"),
    ("R_Fe_HCl", "S_H2"),
    ("R_Cu_H2SO4dac", "S_CuSO4"), ("R_Cu_H2SO4dac", "S_SO2"), ("R_Cu_H2SO4dac", "S_H2O"),
    ("R_Al_NaOH", "S_H2"),
    ("R_C2H4_Br2", None), ("R_CH3COOH_NaOH", "S_H2O"),
    ("R_CH3COOH_C2H5OH", "S_EsteC2H5"), ("R_CH3COOH_C2H5OH", "S_H2O"),
    ("R_Glucose_Fermentation", "S_C2H5OH"), ("R_Glucose_Fermentation", "S_CO2"),
    ("R_C_O2", "S_CO2"),
    ("R_H2_O2", "S_H2O"),
    ("R_SO2_O2_V2O5", "S_SO3"),
]
REACTION_PRODUCTS = [(a, b) for a, b in REACTION_PRODUCTS if b]  # filter None

# Process -> Substance produced
PRODUCES = [
    ("PR_DienPhanNaCl", "S_NaOH"),
    ("PR_LuyenGang", "S_Fe"),
    ("PR_LuyenThep", "S_Fe"),
    ("PR_SanXuat_H2SO4", "S_H2SO4"),
    ("PR_LenMenRuou", "S_C2H5OH"),
    ("PR_LenMenGiam", "S_CH3COOH"),
    ("PR_SanXuat_Voi", "S_CaO"),
]

# Prerequisites (pedagogical order)
PREREQUISITES = [
    # Chuong I: hop chat vo co
    ("SC_Oxit", "SC_Axit"),
    ("SC_Oxit", "SC_Bazo"),
    ("SC_Axit", "SC_Muoi"),
    ("SC_Bazo", "SC_Muoi"),
    ("C_HoaTri", "C_PTHH"),
    ("C_PTHH", "C_CanBangPTHH"),
    ("C_CanBangPTHH", "R_NaOH_HCl"),
    # Oxit chain
    ("SC_OxitBazo", "S_CaO"),
    ("SC_OxitAxit", "S_CO2"),
    ("S_CaO", "R_CaO_H2O"),
    ("R_CaO_H2O", "S_CaOH2"),
    # Axit chain
    ("SC_Axit", "S_HCl"),
    ("SC_Axit", "S_H2SO4"),
    ("S_HCl", "R_NaOH_HCl"),
    ("S_HCl", "R_Zn_HCl"),
    # Muoi
    ("SC_Muoi", "S_NaCl"),
    ("SC_Muoi", "S_CaCO3"),
    ("S_CaCO3", "R_CaCO3_Nhiet"),
    # Kim loai chain
    ("SC_KimLoai", "C_DayHoatDongKimLoai"),
    ("C_DayHoatDongKimLoai", "R_Fe_CuSO4"),
    ("C_DayHoatDongKimLoai", "C_DieuChe_KL_1"),
    ("C_DieuChe_KL_1", "PR_LuyenGang"),
    ("PR_LuyenGang", "PR_LuyenThep"),
    ("SC_KimLoai", "S_Al"),
    ("SC_KimLoai", "S_Fe"),
    ("S_Al", "R_Al_NaOH"),
    # Phi kim
    ("SC_PhiKim", "S_Cl2"),
    ("SC_PhiKim", "S_C_element"),
    ("S_C_element", "R_C_O2"),
    ("R_C_O2", "S_CO2"),
    ("S_CO2", "S_H2CO3"),
    ("S_H2CO3", "S_Na2CO3"),
    ("S_C_element", "C_BangTuanHoan"),
    ("C_BangTuanHoan", "C_ChuKi"),
    ("C_BangTuanHoan", "C_NhomA"),
    ("C_NhomA", "C_DinhLuatTuanHoan"),
    # Hydrocarbon chain
    ("C_SuChuyenHoa_DongDang", "SC_Hidrocacbon"),
    ("SC_Hidrocacbon", "SC_HCNoi"),
    ("SC_Hidrocacbon", "SC_HCKhong"),
    ("SC_Hidrocacbon", "SC_HCThom"),
    ("SC_HCNoi", "S_CH4"),
    ("SC_HCKhong", "S_C2H4"),
    ("SC_HCKhong", "S_C2H2"),
    ("SC_HCThom", "S_C6H6"),
    ("S_CH4", "R_CH4_Cl2"),
    ("S_C2H4", "R_C2H4_Br2"),
    # Dan xuat
    ("S_C2H4", "S_C2H5OH"),
    ("SC_Ancol", "S_C2H5OH"),
    ("S_C2H5OH", "R_C2H5OH_Na"),
    ("S_C2H5OH", "S_CH3COOH"),
    ("SC_Axit_HC", "S_CH3COOH"),
    ("S_CH3COOH", "R_CH3COOH_NaOH"),
    ("S_CH3COOH", "R_CH3COOH_C2H5OH"),
    ("R_CH3COOH_C2H5OH", "S_EsteC2H5"),
    ("SC_Este", "S_EsteC2H5"),
    # Glucose chain
    ("SC_Gluxit", "S_Glucose"),
    ("S_Glucose", "R_Glucose_Fermentation"),
    ("R_Glucose_Fermentation", "S_C2H5OH"),
    ("S_Glucose", "S_Saccarose"),
    ("S_Glucose", "S_TinhBot"),
    # Polymer
    ("S_C2H4", "S_Poli_Ethylene"),
    # Process chain
    ("PR_LenMenRuou", "S_C2H5OH"),
    ("PR_LenMenGiam", "S_CH3COOH"),
    ("PR_LenMenRuou", "PR_LenMenGiam"),
    ("S_C2H5OH", "PR_LenMenGiam"),
]

# Similarities
SIMILARITIES = [
    ("S_CH4", "S_C2H4"),      # 2 hydrocarbon co ban
    ("S_C2H4", "S_C2H2"),     # 2 HC khong no
    ("S_HCl", "S_H2SO4"),     # 2 axit manh
    ("S_NaOH", "S_KOH"),      # 2 kiem
    ("SC_Oxit", "SC_Muoi"),
    ("R_Fe_CuSO4", "R_Zn_HCl"),  # 2 pu the
]

CONTRASTS = [
    ("SC_Axit", "SC_Bazo"),
    ("SC_OxitAxit", "SC_OxitBazo"),
    ("SC_HCNoi", "SC_HCKhong"),
    ("RT_HoaHop", "RT_PhanHuy"),
    ("RT_The", "RT_TraoDoi"),
    ("S_Glucose", "S_Saccarose"),  # mono vs disaccharide
]

print(f"  + {len(INSTANCE_OF)} instance-of, {len(HAS_PROPERTY)} has-prop, "
      f"{len(CONTAINS)} contains, {len(REACTION_REACTANTS)} reactants, "
      f"{len(REACTION_PRODUCTS)} products, {len(PRODUCES)} produces, "
      f"{len(PREREQUISITES)} prereq, {len(SIMILARITIES)} similar, "
      f"{len(CONTRASTS)} contrast")
