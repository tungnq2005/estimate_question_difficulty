"""
Main driver (V4 - Decentralized Folders Version): 
Quét tự động toàn bộ thư mục data/, cộng dồn dữ liệu từ các chương,
và xuất ra định dạng Turtle (.ttl) / OWL (.owl).
"""

import sys
import json
import glob
from pathlib import Path

# Sửa lỗi hiển thị tiếng Việt trên terminal Windows
sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent

# ======================================================================
# 1. LOAD DATA TỰ ĐỘNG (Quét mọi file .py trong thư mục data/)
# ======================================================================

# Khởi tạo các danh sách tổng (Master Lists)
PERIODS, LOCATIONS, PERSONS, ORGANIZATIONS, CONCEPTS = [], [], [], [], []
MOVEMENTS, DOCUMENTS, EVENTS = [], [], []
PREREQUISITES, CAUSES_DIRECT, CAUSES_DEEP = [], [], []
SIMILARITIES, CONTRASTS, PARTICIPATES, INVOLVED_CONCEPTS = [], [], [], []

data_dir = ROOT / "data"
# Tìm tất cả file .py trong thư mục data và các thư mục con
data_files = glob.glob(str(data_dir / "**" / "*.py"), recursive=True)

print("--- ĐANG NẠP DỮ LIỆU TỪ HỆ THỐNG FILE ---")
for filepath in data_files:
    local_ns = {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            exec(f.read(), local_ns)
        
        # Gộp dữ liệu Tĩnh (Global & Concepts) bằng cách nối mảng
        if "PERIODS" in local_ns: PERIODS.extend(local_ns["PERIODS"])
        if "LOCATIONS" in local_ns: LOCATIONS.extend(local_ns["LOCATIONS"])
        if "PERSONS" in local_ns: PERSONS.extend(local_ns["PERSONS"])
        if "ORGANIZATIONS" in local_ns: ORGANIZATIONS.extend(local_ns["ORGANIZATIONS"])
        if "CONCEPTS" in local_ns: CONCEPTS.extend(local_ns["CONCEPTS"])
        
        # Gộp dữ liệu Động (Events theo chương)
        if "MOVEMENTS" in local_ns: MOVEMENTS.extend(local_ns["MOVEMENTS"])
        if "DOCUMENTS" in local_ns: DOCUMENTS.extend(local_ns["DOCUMENTS"])
        if "EVENTS" in local_ns: EVENTS.extend(local_ns["EVENTS"])
        
        # Gộp Quan hệ đồ thị
        if "PREREQUISITES" in local_ns: PREREQUISITES.extend(local_ns["PREREQUISITES"])
        if "CAUSES_DIRECT" in local_ns: CAUSES_DIRECT.extend(local_ns["CAUSES_DIRECT"])
        if "CAUSES_DEEP" in local_ns: CAUSES_DEEP.extend(local_ns["CAUSES_DEEP"])
        if "SIMILARITIES" in local_ns: SIMILARITIES.extend(local_ns["SIMILARITIES"])
        if "CONTRASTS" in local_ns: CONTRASTS.extend(local_ns["CONTRASTS"])
        if "PARTICIPATES" in local_ns: PARTICIPATES.extend(local_ns["PARTICIPATES"])
        if "INVOLVED_CONCEPTS" in local_ns: INVOLVED_CONCEPTS.extend(local_ns["INVOLVED_CONCEPTS"])

        # Hiển thị đường dẫn gọn gọn để dễ xem log
        short_path = Path(filepath).relative_to(ROOT)
        print(f"  [+] Đã nạp: {short_path}")
    except Exception as e:
        print(f"  [!] Lỗi khi nạp {filepath}: {e}")

print(f"-> Tổng cộng đã nạp: {len(EVENTS)} Sự kiện, {len(DOCUMENTS)} Tài liệu, {len(MOVEMENTS)} Phong trào, {len(PERSONS)} Nhân vật.\n")


# ======================================================================
# 2. SCHEMA & TURTLE EMITTERS
# ======================================================================
HEADER = """\
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix su9:  <http://su9.edu.vn/ontology#> .

<http://su9.edu.vn/ontology> a owl:Ontology .
"""

SCHEMA = """
# --- Khai báo Classes ---
su9:Tri_thuc_Lich_su a owl:Class .
su9:Period a owl:Class ; rdfs:subClassOf su9:Tri_thuc_Lich_su .
su9:Location a owl:Class ; rdfs:subClassOf su9:Tri_thuc_Lich_su .
su9:Person a owl:Class ; rdfs:subClassOf su9:Tri_thuc_Lich_su .
su9:Organization a owl:Class ; rdfs:subClassOf su9:Tri_thuc_Lich_su .
su9:Concept a owl:Class ; rdfs:subClassOf su9:Tri_thuc_Lich_su .
su9:Event a owl:Class ; rdfs:subClassOf su9:Tri_thuc_Lich_su .
su9:Document a owl:Class ; rdfs:subClassOf su9:Tri_thuc_Lich_su .
su9:Movement a owl:Class ; rdfs:subClassOf su9:Tri_thuc_Lich_su .

# --- Khai báo Object Properties (Cạnh nối thực thể - thực thể) ---
su9:occursAt a owl:ObjectProperty .
su9:occursDuring a owl:ObjectProperty .
su9:hasPerson a owl:ObjectProperty .
su9:hasOrganization a owl:ObjectProperty .
su9:involvedConcept a owl:ObjectProperty .
su9:prerequisiteOf a owl:ObjectProperty .
su9:directCause a owl:ObjectProperty .
su9:deepCause a owl:ObjectProperty .
su9:similarTo a owl:ObjectProperty .
su9:contrastsWith a owl:ObjectProperty .
su9:locatedIn a owl:ObjectProperty .
su9:leads a owl:ObjectProperty .
su9:participatesIn a owl:ObjectProperty .
su9:memberOf a owl:ObjectProperty .

# --- Khai báo Datatype Properties (Thuộc tính văn bản/số) ---
su9:hasContext a owl:DatatypeProperty .
su9:hasCause a owl:DatatypeProperty .
su9:hasCauseDeep a owl:DatatypeProperty .
su9:hasCauseDirect a owl:DatatypeProperty .
su9:hasContent a owl:DatatypeProperty .
su9:hasResult a owl:DatatypeProperty .
su9:hasAchievements a owl:DatatypeProperty .
su9:hasLimitations a owl:DatatypeProperty .
su9:weightsJson a owl:DatatypeProperty .
su9:aliases a owl:DatatypeProperty .
su9:status a owl:DatatypeProperty .
su9:startYear a owl:DatatypeProperty .
su9:endYear a owl:DatatypeProperty .
su9:abstractness a owl:DatatypeProperty .
su9:bloomLevel a owl:DatatypeProperty .
su9:frequencyInTextbook a owl:DatatypeProperty .
su9:confidence a owl:DatatypeProperty .
"""

def quote(s: str) -> str:
    """Escape string for Turtle literal."""
    if not isinstance(s, str): return ""
    # CODE MỚI: Giữ lại dấu xuống dòng bằng cách escape nó (\n -> \\n)
    return s.replace("\\", "\\\\").replace('"', '\\"').replace('\n', '\\n')

def emit_static_entity(class_name, row):
    """
    Hàm xử lý chung cho các Tuple tĩnh (Location, Person, Concept...).
    Tự động xử lý các field phụ thuộc vào class_name:
      - Period:   (id, label, aliases, start, end, abstractness, confidence)
      - Location: (id, label, aliases, located_in, abstractness, confidence) 
                  lưu ý: located_in là ID location cha (optional)
      - Person:   (id, label, aliases, frequency, abstractness, confidence)
      - Organization: (id, label, aliases, frequency, abstractness, confidence)
      - Concept:  (id, label, aliases, freq, abstractness, bloom, confidence)
    """
    eid = row[0]
    label = row[1]
    aliases = row[2] if len(row) > 2 and row[2] else ""
    
    # Lấy thêm các field nếu có
    extra = {}
    has_extra = False
    if class_name == "Period" and len(row) >= 7:
        has_extra = True
        # (id, label, aliases, start, end, abstractness, confidence)
        if row[3]: extra["startYear"] = row[3]
        if row[4]: extra["endYear"] = row[4]
        if row[5]: extra["abstractness"] = row[5]
        if row[6]: extra["confidence"] = row[6]
    elif class_name == "Location" and len(row) >= 6:
        has_extra = True
        # (id, label, aliases, located_in, abstractness, confidence)
        if row[3]: extra["locatedIn"] = row[3]
        if row[4]: extra["abstractness"] = row[4]
        if row[5]: extra["confidence"] = row[5]
    elif class_name in ("Person", "Organization") and len(row) >= 6:
        has_extra = True
        # (id, label, aliases, frequency, abstractness, confidence)
        if row[3]: extra["frequencyInTextbook"] = row[3]
        if row[4]: extra["abstractness"] = row[4]
        if row[5]: extra["confidence"] = row[5]
    elif class_name == "Concept" and len(row) >= 7:
        has_extra = True
        # (id, label, aliases, freq, abstractness, bloom, confidence)
        if row[3]: extra["frequencyInTextbook"] = row[3]
        if row[4]: extra["abstractness"] = row[4]
        if row[5]: extra["bloomLevel"] = row[5]
        if row[6]: extra["confidence"] = row[6]
    
    out = [f"su9:{eid} a su9:{class_name} ;",
           f'    rdfs:label "{quote(label)}"@vi ;']
    if aliases:
        out.append(f'    su9:aliases "{quote(aliases)}" ;')
    
    # Xuất các field phụ ra TTL
    if has_extra:
        if "startYear" in extra:
            out.append(f"    su9:startYear {extra['startYear']} ;")
        if "endYear" in extra:
            out.append(f"    su9:endYear {extra['endYear']} ;")
        if "locatedIn" in extra:
            out.append(f"    su9:locatedIn su9:{extra['locatedIn']} ;")
        if "frequencyInTextbook" in extra:
            out.append(f"    su9:frequencyInTextbook {extra['frequencyInTextbook']} ;")
        if "abstractness" in extra:
            out.append(f"    su9:abstractness {extra['abstractness']} ;")
        if "bloomLevel" in extra:
            out.append(f"    su9:bloomLevel {extra['bloomLevel']} ;")
        if "confidence" in extra:
            out.append(f"    su9:confidence {extra['confidence']} ;")
    
    out.append("    su9:status \"Active\" .")
    return "\n".join(out)

def emit_dynamic_entity(class_name, data_dict):
    """
    Hàm xử lý chuẩn cho Event/Document/Movement dạng DICTIONARY.
    Tự động bung các trường cause, content, result và mảng _weighted.
    """
    eid = data_dict["id"]
    out = [f"su9:{eid} a su9:{class_name} ;",
           f'    rdfs:label "{quote(data_dict.get("label", ""))}"@vi ;']
    
    # 1. Các trường cơ bản
    if data_dict.get("aliases"):
        out.append(f'    su9:aliases "{quote(data_dict["aliases"])}" ;')
    if data_dict.get("where"):
        out.append(f"    su9:occursAt su9:{data_dict['where']} ;")
    if data_dict.get("when"):
        out.append(f"    su9:occursDuring su9:{data_dict['when']} ;")
    
    # 2. Xử lý Văn bản (NLP)
    text_fields = {
        "context": "su9:hasContext",
        "cause": "su9:hasCause",
        "cause_deep": "su9:hasCauseDeep",
        "cause_direct": "su9:hasCauseDirect",
        "content": "su9:hasContent",
        "result": "su9:hasResult",
        "achievements": "su9:hasAchievements",
        "limitations": "su9:hasLimitations"
    }
    for dict_key, turtle_prop in text_fields.items():
        if data_dict.get(dict_key):
            out.append(f'    {turtle_prop} "{quote(data_dict[dict_key])}" ;')

    # 3. Xử lý mảng trọng số _weighted
    weights_db = {}
    
    if "who_weighted" in data_dict:
        for pid, rank in data_dict["who_weighted"]:
            out.append(f"    su9:hasPerson su9:{pid} ;")
            weights_db[pid] = rank
            
    if "org_weighted" in data_dict:
        for oid, rank in data_dict["org_weighted"]:
            out.append(f"    su9:hasOrganization su9:{oid} ;")
            weights_db[oid] = rank
            
    if "concepts_weighted" in data_dict:
        for cid, rank in data_dict["concepts_weighted"]:
            out.append(f"    su9:involvedConcept su9:{cid} ;")
            weights_db[cid] = rank

    # 4. Lưu toàn bộ trọng số vào 1 chuỗi JSON duy nhất
    if weights_db:
        json_str = json.dumps(weights_db)
        out.append(f'    su9:weightsJson "{quote(json_str)}" ;')

    # Xóa dấu chấm phẩy cuối cùng và đóng Entity
    out[-1] = out[-1][:-1] + "."
    return "\n".join(out)


# ======================================================================
# 3. BUILD QUY TRÌNH
# ======================================================================
def main() -> None:
    out = [HEADER, SCHEMA]
    print("--- Đang khởi tạo các thực thể Tĩnh ---")
    out.append("\n### PERIODS ###")
    for row in PERIODS: out.append(emit_static_entity("Period", row))
    
    out.append("\n### LOCATIONS ###")
    for row in LOCATIONS: out.append(emit_static_entity("Location", row))
    
    out.append("\n### PERSONS & ORGS ###")
    for row in PERSONS: out.append(emit_static_entity("Person", row))
    for row in ORGANIZATIONS: out.append(emit_static_entity("Organization", row))
    
    out.append("\n### CONCEPTS ###")
    for row in CONCEPTS: out.append(emit_static_entity("Concept", row))

    print("--- Đang phân tích các thực thể Động (Có trọng số) ---")
    out.append("\n### MOVEMENTS ###")
    for d in MOVEMENTS: out.append(emit_dynamic_entity("Movement", d))

    out.append("\n### DOCUMENTS ###")
    for d in DOCUMENTS: out.append(emit_dynamic_entity("Document", d))

    out.append("\n### EVENTS ###")
    for d in EVENTS: out.append(emit_dynamic_entity("Event", d))

    print("--- Đang thiết lập các liên kết Đồ thị (Graph Edges) ---")
    out.append("\n### PREREQUISITES ###")
    for a, b in PREREQUISITES: out.append(f"su9:{a} su9:prerequisiteOf su9:{b} .")

    out.append("\n### CAUSAL EDGES ###")
    for a, b in CAUSES_DIRECT: out.append(f"su9:{a} su9:directCause su9:{b} .")
    for a, b in CAUSES_DEEP: out.append(f"su9:{a} su9:deepCause su9:{b} .")

    out.append("\n### SIMILARITIES & CONTRASTS ###")
    for a, b in SIMILARITIES: out.append(f"su9:{a} su9:similarTo su9:{b} .")
    for a, b in CONTRASTS: out.append(f"su9:{a} su9:contrastsWith su9:{b} .")

    out.append("\n### PARTICIPATES (Static mappings) ###")
    for p, e, rel in PARTICIPATES: out.append(f"su9:{p} su9:{rel} su9:{e} .")

    # Ghi ra file .ttl
    ttl_path = ROOT / "output" / "su9.ttl"
    ttl_path.parent.mkdir(exist_ok=True) # Tạo folder output nếu chưa có
    ttl_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\n[OK] Đã ghi thành công file Turtle: {ttl_path}")

    # Parse và xuất ra định dạng OWL bằng rdflib
    try:
        from rdflib import Graph
        g = Graph()
        g.parse(str(ttl_path), format="turtle")
        owl_path = ROOT / "output" / "su9.owl"
        g.serialize(destination=str(owl_path), format="xml")
        print(f"[OK] Đã xuất thành công file OWL cho Protégé: {owl_path}  ({len(g)} triples)")
    except ImportError:
        print("[INFO] Thư viện 'rdflib' chưa được cài đặt. Không thể tạo file .owl.")

if __name__ == "__main__":
    main()