import sys
import json
import re
from pathlib import Path
from owlready2 import *

# ==========================================
# CẤU HÌNH HỆ THỐNG
# ==========================================
# Sửa lỗi hiển thị tiếng Việt trên Windows
sys.stdout.reconfigure(encoding='utf-8')

# Đồ thị Lịch sử được sinh ra tại subjects/history/ontology/su9.owl
REPO_ROOT = Path(__file__).resolve().parents[1]
PATH_TO_OWL = REPO_ROOT / "subjects" / "history" / "ontology" / "su9.owl"
try:
    onto = get_ontology(PATH_TO_OWL.as_uri()).load()
except Exception as e:
    print(f"[LỖI] Không thể load file OWL: {e}")
    print("Hãy chạy 'python subjects/history/build.py' trước để tạo file dữ liệu!")
    sys.exit()

# Hàm chuẩn hóa lỗi gõ dấu tiếng Việt (VD: òa -> oà)
def normalize_vietnamese(text):
    if not text: return ""
    text = text.replace("òa", "oà").replace("óa", "oá").replace("ỏa", "oả").replace("õa", "oã").replace("ọa", "oạ")
    text = text.replace("ủy", "uỷ").replace("úy", "uý").replace("ủy", "uỷ").replace("ũy", "uỹ").replace("ụy", "uỵ")
    return text.lower().strip()

# ==========================================
# BƯỚC 1: XÂY DỰNG TỪ ĐIỂN TRA CỨU
# ==========================================
entity_lookup = {}
all_entities = onto.search(type = onto.Tri_thuc_Lich_su)

for entity in all_entities:
    names = []
    # Lấy Label chính
    if hasattr(entity, "label") and entity.label:
        names.extend([str(l) for l in entity.label])
        
    # Lấy các Aliases
    if hasattr(entity, "aliases") and entity.aliases:
        aliases = str(entity.aliases[0]).split("|")
        names.extend([a.strip() for a in aliases if a.strip()])
    
    # Đưa vào bộ nhớ (SỬ DỤNG LIST ĐỂ CHỨA NHIỀU THỰC THỂ CHO 1 TỪ KHÓA)
    for name in names:
        kw = normalize_vietnamese(name)
        if kw not in entity_lookup:
            entity_lookup[kw] = [] # Khởi tạo danh sách nếu từ khóa chưa tồn tại
        
        if entity not in entity_lookup[kw]:
            entity_lookup[kw].append(entity) # Thêm thực thể vào danh sách

print(f"[HỆ THỐNG] Đã nạp thành công bộ từ điển với {len(entity_lookup)} từ khóa/bí danh.")

# ==========================================
# BƯỚC 2: HÀM MAPPING THỰC THỂ (Regex)
# ==========================================
def extract_entities(text):
    text_lower = normalize_vietnamese(text)
    found = []
    
    # Ưu tiên match từ khóa dài nhất trước
    keywords = sorted(entity_lookup.keys(), key=len, reverse=True)
    temp_text = text_lower
    
    for kw in keywords:
        pattern = r'(?<!\w)' + re.escape(kw) + r'(?!\w)'
        if re.search(pattern, temp_text):
            # Lấy toàn bộ danh sách các thực thể dùng chung từ khóa này
            entities_list = entity_lookup[kw]
            for ent in entities_list:
                if ent not in found:
                    found.append(ent)
                    
            # Dùng khoảng trắng che đi phần đã match để tìm tiếp
            temp_text = re.sub(pattern, " " * len(kw), temp_text)
            
    return found

# ==========================================
# BƯỚC 3: HÀM IN CHI TIẾT (DEEP VIEW)
# ==========================================
def inspect_question(question_text):
    print("\n" + "="*80)
    print(f"CÂU HỎI: '{question_text}'")
    print("="*80)
    
    found = extract_entities(question_text)
    
    if not found:
        print("-> [!] Không tìm thấy thực thể nào. Hệ thống chưa được dạy từ khóa này!")
        return

    # ==========================================
    # BẢN VÁ MỚI: BỘ SẮP XẾP TƯ DUY LỊCH SỬ
    # ==========================================
    def historical_sort(ent):
        # 1. Ưu tiên theo Loại thực thể (Khái niệm in trước -> Tài liệu -> Phong trào -> Sự kiện)
        class_name = ent.is_a[0].name.lower() if ent.is_a else ""
        type_order = {"concept": 1, "document": 2, "movement": 3, "event": 4}
        p1 = type_order.get(class_name, 5)

        # 2. Ưu tiên theo tiến trình thời gian/logic
        p2 = 5 # Mặc định nằm ở giữa (Diễn biến chung)
        text_check = (ent.name + " " + (ent.label[0] if ent.label else "")).lower()
        
        if "nguyên nhân" in text_check or "nguyennhan" in text_check or "bối cảnh" in text_check:
            p2 = 1
        elif "mở đầu" in text_check or "hoàn cảnh" in text_check:
            p2 = 2
        elif "đối đầu" in text_check:
            p2 = 3
        elif "chạy đua" in text_check or "đỉnh cao" in text_check:
            p2 = 4
        elif "kết thúc" in text_check or "hậu quả" in text_check or "hauqua" in text_check or "ý nghĩa" in text_check or "sụp đổ" in text_check:
            p2 = 9
            
        return (p1, p2)

    # Áp dụng sắp xếp cho danh sách kết quả tìm được
    found = sorted(found, key=historical_sort)
    # ==========================================

    for ent in found:
        class_name = ent.is_a[0].name if ent.is_a else "Unknown"
        print(f"\n● [{class_name.upper()}]: {ent.label[0]} (ID: {ent.name})")
        
        # 1. Gom tất cả thuộc tính
        props_data = {}
        has_weights = hasattr(ent, "weightsJson") and ent.weightsJson
        
        # Danh sách đen: Bỏ qua các thuộc tính không cần in
        ignore_props = ["label", "aliases", "status"]
        if has_weights:
            # Nếu đã có bảng Rank, ẩn các dòng lặp này đi cho gọn
            ignore_props.extend(["hasPerson", "hasOrganization", "involvedConcept"])
            
        for prop in ent.get_properties():
            p_name = prop.name
            p_vals = prop[ent]
            if p_vals and p_name not in ignore_props:
                props_data[p_name] = p_vals[0]
                
        # 2. Thứ tự hiển thị logic lịch sử
        logical_order = [
            "occursAt", "occursDuring", "hasContext", "hasCauseDeep", 
            "hasCauseDirect", "hasCause", "hasContent", "hasAchievements", 
            "hasResult", "hasLimitations", "weightsJson"
        ]
        
        # 3. Hàm in giá trị thông minh
        # 3. Hàm in giá trị thông minh (Đã vá lỗi IndexError và lỗi thụt lề)
        def print_val(p_name, val):
            if p_name == "weightsJson":
                print(f"   ➤ Trọng số kết nối (Rank):")
                weights = json.loads(val)
                for tid, rank in weights.items():
                    target = onto.search_one(iri=f"*{tid}")
                    
                    # BẢN VÁ LỖI INDEX ERROR: Kiểm tra an toàn trước khi lấy Label
                    if target and hasattr(target, "label") and target.label:
                        t_name = target.label[0]
                    elif target and hasattr(target, "name"):
                        t_name = target.name
                    else:
                        t_name = str(tid) # Nếu không có gì, in thẳng ID ra
                        
                    print(f"      ◦ [{rank}/10] --> {t_name}")
            else:
                # Trích xuất giá trị hiển thị
                if hasattr(val, "label") and val.label:
                    display_val = val.label[0]
                elif hasattr(val, "name"):
                    display_val = val.name
                else:
                    display_val = str(val)
                
                # Xóa URL xấu xí nếu quên khai báo ID
                if "http://su9.edu.vn/ontology#" in display_val:
                    id_name = display_val.split("#")[-1]
                    display_val = f"[CHƯA KHAI BÁO ID: {id_name}]"
                
                # Căn lề đẹp mắt (Đã sửa lỗi dòng thứ 2 bị thụt quá sâu)
                if "\n" in display_val:
                    # Lọc bỏ các khoảng trắng thừa ở đầu dòng trước khi nối lại
                    lines = [line.strip() for line in display_val.split("\n") if line.strip()]
                    display_val = "\n      " + "\n      ".join(lines)
                
                # Dịch các thuộc tính đồ thị sang Tiếng Việt
                vi_props = {
                    "occursAt": "Địa điểm",
                    "occursDuring": "Thời gian",
                    "hasContext": "Bối cảnh",
                    "hasCauseDeep": "Nguyên nhân sâu xa",
                    "hasCauseDirect": "Nguyên nhân trực tiếp",
                    "hasCause": "Nguyên nhân",
                    "hasContent": "Nội dung / Diễn biến",
                    "hasAchievements": "Thành tựu / Ý nghĩa",
                    "hasResult": "Kết quả",
                    "hasLimitations": "Hạn chế",
                    "prerequisiteOf": "Là tiền đề của",
                    "directCause": "Là nguyên nhân trực tiếp của",
                    "deepCause": "Là nguyên nhân sâu xa của",
                    "similarTo": "Tương đồng với",
                    "contrastsWith": "Đối lập với",
                    "hasPerson": "Nhân vật liên quan",
                    "hasOrganization": "Tổ chức liên quan",
                    "involvedConcept": "Khái niệm cốt lõi"
                }
                print_name = vi_props.get(p_name, p_name)
                
                print(f"   ➤ {print_name}: {display_val}")

        # 4. In theo thứ tự ưu tiên
        for key in logical_order:
            if key in props_data:
                print_val(key, props_data[key])
                del props_data[key]
                
        # 5. In các thuộc tính còn lại (liên kết đồ thị)
        for key, val in props_data.items():
            print_val(key, val)
            
        # ==========================================
        # 6. TRUY XUẤT NGƯỢC (REVERSE LOOKUP)
        # ==========================================
        print(f"   ➤ [LIÊN KẾT NGƯỢC] Các sự kiện/đối tượng liên quan:")
        related_count = 0
        for other in onto.search(type=onto.Tri_thuc_Lich_su):
            if other == ent: continue
            is_related = False
            
            # Kiểm tra trong weightsJson
            if hasattr(other, "weightsJson") and other.weightsJson:
                try:
                    w_data = json.loads(other.weightsJson[0])
                    if ent.name in w_data:
                        is_related = True
                except:
                    pass
                    
            # Kiểm tra trong các Object Property khác
            if not is_related:
                for prop in other.get_properties():
                    if ent in prop[other]:
                        is_related = True
                        break
                        
            if is_related:
                related_count += 1
                c_name = other.is_a[0].name if other.is_a else "Unknown"
                print(f"      ♦ [{c_name.upper()}] {other.label[0]}")
                
        if related_count == 0:
            print("      (Chưa có sự kiện nào liên kết tới thực thể này)")

# ==========================================
# BƯỚC 4: HÀM QUÉT TRỤC THỜI GIAN (TIMELINE)
# ==========================================
def scan_timeline(start_year, end_year):
    print("\n" + "="*80)
    print(f"ĐANG QUÉT CÁC SỰ KIỆN TỪ NĂM {start_year} ĐẾN {end_year}...")
    print("="*80)
    
    count = 0
    for ent in onto.search(type=onto.Tri_thuc_Lich_su):
        class_name = ent.is_a[0].name if ent.is_a else ""
        
        # Chỉ quét Sự kiện, Phong trào và Tài liệu
        if class_name in ["Event", "Movement", "Document"]:
            text_pool = ""
            for prop in ["label", "hasContext", "hasContent", "hasCause", "hasResult", "hasAchievements"]:
                if hasattr(ent, prop) and getattr(ent, prop):
                    text_pool += " " + str(getattr(ent, prop)[0])
            
            # Tìm năm trong văn bản
            found_year = False
            for y in range(int(start_year), int(end_year) + 1):
                if str(y) in text_pool:
                    found_year = True
                    break
                    
            if found_year:
                count += 1
                print(f"  ♦ [{class_name.upper()}] {ent.label[0]}")
                
    if count == 0:
        print("  (Không tìm thấy dữ kiện nào trong khoảng thời gian này)")
    else:
        print(f"\n-> Đã tìm thấy {count} mảnh ghép lịch sử.")

# ==========================================
# CHẠY TƯƠNG TÁC (INTERACTIVE CLI)
# ==========================================
if __name__ == "__main__":
    print("\n" + "*"*60)
    print("* HỆ THỐNG ĐỒ THỊ TRI THỨC LỊCH SỬ 9 - ĐÃ SẴN SÀNG! *")
    print("*"*60)
    print("- Gõ từ khóa sự kiện/nhân vật để tra cứu (VD: Bác Hồ, Xô viết)")
    print("- Gõ 'time [năm 1] [năm 2]' để quét dòng thời gian (VD: time 1930 1945)")
    print("- Gõ 'exit' hoặc 'quit' để thoát chương trình.\n")
    
    while True:
        try:
            cau_hoi = input("\n[Bạn] ❯ ").strip()
            if cau_hoi.lower() in ['exit', 'quit', 'thoát']:
                print("Hẹn gặp lại!")
                break
            
            # Xử lý lệnh TIMELINE
            if cau_hoi.lower().startswith("time "):
                parts = cau_hoi.split()
                if len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
                    scan_timeline(int(parts[1]), int(parts[2]))
                else:
                    print("-> Cú pháp sai. Hãy gõ theo mẫu: time 1930 1945")
            # Xử lý câu hỏi thông thường
            elif cau_hoi:
                inspect_question(cau_hoi)
                
        except KeyboardInterrupt:
            print("\nHẹn gặp lại!")
            break