# -*- coding: utf-8 -*-
"""Pilot mô phỏng "học sinh LLM" cho 20 cặp câu đối chứng (T2) — KHÔNG gọi
API bên ngoài, không cần API key/chi phí. Toàn bộ δ (độ đặc thù nội dung)
dưới đây là NHẬN ĐỊNH THỦ CÔNG của Claude (agent đang chạy phiên này) sau khi
đọc trực tiếp nội dung 40 câu hỏi — ĐỘC LẬP với kg_centrality_mean (proxy đã
dùng để CHỌN các cặp này ở tools/make_test_forms.py), để tránh vòng lặp
tự-xác-nhận (dùng lại đúng proxy đã dùng để chọn câu, rồi "phát hiện" ra
đúng thứ đã cài vào).

⚠️ ĐÂY LÀ PILOT ĐỊNH TÍNH, KHÔNG PHẢI GROUND TRUTH: là phán đoán hành vi của
MỘT LLM (Claude) đóng vai học sinh, không phải học sinh lớp 9 thật. Có cùng
họ rủi ro với nhãn llm_vote3 (thiên lệch của LLM), nhưng khác về BẢN CHẤT
tác vụ: llm_vote3 là LLM tự đánh giá độ khó (judgment trực tiếp — chính là
nguồn gây thiên lệch theo khuôn mẫu câu hỏi đã phát hiện); pilot này là LLM
mô phỏng HÀNH VI TRẢ LỜI của nhiều mức năng lực khác nhau dựa trên độ đặc thù
nội dung — một tác vụ khác, có thể bộc lộ thiên lệch khác hoặc không. Phải
nêu rõ giới hạn này khi báo cáo, KHÔNG được trình bày như dữ liệu học sinh
thật.

QUY TẮC MÔ PHỎNG (minh bạch, không phải "hộp đen"):
  - 5 persona theo mức năng lực τ = 1..5 (Yếu, TB-yếu, TB, Khá, Giỏi).
  - Mỗi câu có δ = độ đặc thù/khó nội dung (1=kiến thức đầu bài SGK ai cũng
    biết .. 5=phân tích/so sánh tinh vi hoặc chi tiết rất hẹp), CỘNG THÊM +1
    nếu câu dạng phủ định ("không phải"/"không đúng"/"ngoại trừ" — dạng này
    khó hơn cùng nội dung vì phải xác định mệnh đề SAI giữa các mệnh đề đúng).
  - gap = τ_persona − δ_hiệu_dụng. Số câu đúng trên 2 lần lặp:
      gap <= -2  -> 0/2 đúng (đoán ngẫu nhiên 4 phương án, không biết)
      gap in {-1, 0} -> 1/2 đúng (biết một phần / phân vân)
      gap >= 1   -> 2/2 đúng (nắm chắc)
    Đây là một hàm bậc thang đơn giản hoá — KHÔNG phải mô hình IRT chuẩn, chỉ
    đủ để tạo tín hiệu định tính cho pilot quy mô nhỏ này.

Output:
  - subjects/history/samples/student_responses.LLMSIM.csv  (schema giống hệt
    student_responses.csv thật — nạp thẳng được vào tools/item_analysis.py)
  - In bảng so sánh p_sim trong từng cặp + kết luận thống kê thô (paired test)

Usage:
    python tools/llm_persona_pilot.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]

PERSONAS = [1, 2, 3, 4, 5]  # τ: Yếu, TB-yếu, TB, Khá, Giỏi
N_REPEATS = 2

# ĐỘ ĐẶC THÙ NỘI DUNG (δ, đã cộng +1 cho câu phủ định) — lý do ngắn gọn cho
# TỪNG câu, dựa trên đọc nội dung thật, không dùng lại proxy centrality.
# Định dạng: item_id: (delta, "lý do")
DELTA = {
    # Pair 1 [ket_qua/Medium]
    "su9_vj_1958": (4, "phủ định + phân biệt 'kết quả' và 'nguyên nhân/bối cảnh' của cuộc chiến biên giới Tây Nam (ít nổi bật hơn narrative Liên Xô sụp đổ)"),
    "su9_vj_1838": (2, "cải tổ Gorbachev thất bại là mốc RẤT nổi bật trong narrative 'Liên Xô khủng hoảng -> tan rã', được nhắc đi nhắc lại"),
    # Pair 2 [nguyen_nhan/Hard]
    "su9_vj_1780": (5, "phân biệt 'yêu cầu khách quan của CMVN' và 'hạn chế các con đường cứu nước trước' là phân tích sử học tinh vi, khó ngay cả với HS khá"),
    "su9_vj_0149": (2, "'áp dụng KHKT' là câu trả lời chuẩn, học thuộc lòng rất phổ biến cho câu hỏi kinh điển 'nguyên nhân kinh tế Mỹ phát triển'"),
    # Pair 3 [quoc_gia_nao/Easy]
    "su9_vj_0039": (1, "3 nước ĐNA giành độc lập sớm nhất (Indo/VN/Lào) là sự kiện biểu tượng, dạy đi dạy lại nhiều lần"),
    "su9_vj_0045": (3, "tên 3 vùng lãnh thổ phân biệt chủng tộc ở châu Phi là chi tiết địa danh cụ thể, ít được nhấn mạnh bằng"),
    # Pair 4 [so_sanh/Hard]
    "su9_vj_0629": (5, "so sánh tinh vi giữa hành động của Pônpốt và Trung Quốc ở 2 chiến trường khác nhau — chi tiết hẹp"),
    "su9_vj_0054": (3, "so sánh phong trào GPDT trước/sau CTTG2 (khác biệt về 'kết quả') là chủ đề so sánh lớn, dạy thường xuyên"),
    # Pair 5 [y_nghia/Medium]
    "su9_vj_2838": (3, "lý giải vì sao khởi nghĩa đô thị quyết định — câu hỏi phân tích chuẩn mực, quen thuộc"),
    "su9_vj_0434": (4, "ý nghĩa tên gọi 'Đội VN Tuyên truyền GPQ' là chi tiết diễn giải hẹp, dễ bị bỏ qua khi ôn tập"),
    # Pair 6 [khong_phai/Hard]
    "su9_vj_0354": (6, "phủ định + đòi hỏi nhớ CHÍNH XÁC cách Cương lĩnh 1930 đặt trọng số nhiệm vụ dân tộc/dân chủ — học thuật tinh vi"),
    "su9_vj_0427": (5, "phủ định + phân biệt ý nghĩa của 'cao trào kháng Nhật' với các mốc liền kề (Nhật đảo chính, Tổng khởi nghĩa)"),
    # Pair 7 [khong_phai/Medium]
    "su9_vj_0265": (3, "phủ định nhưng dựa trên chủ đề rất nổi bật ('chính sách ngu dân' của Pháp), suy luận loại trừ dễ"),
    "su9_vj_0114": (4, "phủ định + bẫy thời gian ('hiện nay' vs quá khứ thuộc địa) — cần tinh ý hơn"),
    # Pair 8 [nguyen_nhan/Medium]
    "su9_vj_2963": (2, "phân loại nguyên nhân khách quan/chủ quan là dạng bài rất chuẩn, luyện tập nhiều"),
    "su9_vj_0143": (3, "phủ định nhẹ trên cùng danh sách 'nguyên nhân kinh tế Mỹ' (đã quen thuộc) nhưng cần nhận diện câu không khớp logic"),
    # Pair 9 [ket_qua/Easy] — KHÔNG có gap kỳ vọng: cả 2 đều là sự kiện nổi bật
    "su9_vj_1963": (2, "thành tựu lương thực thời Đổi Mới là mốc rất nổi bật, hay được nhắc"),
    "su9_vj_2253": (2, "'hoàn thành trước thời hạn' là câu trả lời mẫu quen thuộc về kế hoạch 5 năm Liên Xô"),
    # Pair 10 [su_kien_nao/Easy]
    "su9_vj_2924": (4, "dễ nhầm sự kiện Plây-cu (2/1965) với sự kiện Vịnh Bắc Bộ (1964) nổi tiếng hơn nhiều — bẫy gây nhiễu thật sự"),
    "su9_vj_0097": (2, "binh biến Ai Cập 1952 là mốc mở đầu kinh điển, hay được dạy như điểm khởi đầu chương"),
    # Pair 11 [vai_tro/Hard] — cả 2 đều khó tương đương (đúng như nhãn)
    "su9_vj_0448": (5, "phủ định + bẫy thời gian (Hiệp định Sơ bộ 1946 nằm NGOÀI phạm vi CM tháng 8 1945)"),
    "su9_vj_0451": (5, "phủ định + đòi hỏi phân biệt vai trò Việt Minh với vai trò Đảng/Đồng minh — tinh vi"),
    # Pair 12 [su_kien_nao/Medium]
    "su9_vj_1874": (2, "Hiệp định Paris về Campuchia là mốc rất nổi bật trong chương 'ASEAN mở rộng'"),
    "su9_vj_2139": (4, "1 trong 4 sự kiện tương tự về hoạt động đầu của NAQ ở Pháp — dễ nhầm lẫn giữa các mốc"),
    # Pair 13 [quoc_gia_nao/Medium]
    "su9_vj_3052": (4, "phủ định + cần loại trừ 3 nước đều là điểm nóng Chiến tranh lạnh kinh điển — suy luận nhiều bước"),
    "su9_vj_1823": (2, "Mỹ ủng hộ Tây Đức là suy luận trực tiếp từ khối liên minh Chiến tranh lạnh, khá hiển nhiên"),
    # Pair 14 [su_kien_nao/Hard]
    "su9_vj_2246": (3, "Chiến tranh Triều Tiên là 'cuộc đụng đầu đầu tiên' được nhắc khá thường xuyên dù nhãn LLM là Hard"),
    "su9_vj_2196": (5, "phải phân biệt CHÍNH XÁC giữa 4 hội nghị TW Đảng liền kề theo số thứ tự — bẫy học thuộc kinh điển"),
    # Pair 15 [y_nghia/Hard]
    "su9_vj_2540": (5, "phủ định + đáp án đúng là câu mơ hồ không thuộc danh sách ý nghĩa chuẩn hay được liệt kê"),
    "su9_vj_3025": (4, "ý nghĩa phong trào Vô sản hóa là điểm khá cụ thể trong 1 chương nhỏ, không phải trọng tâm lớn"),
    # Pair 16 [khong_phai/Easy] — cả 2 đều là fact học vẹt quen thuộc
    "su9_vj_0016": (3, "phủ định trên 1 con số xếp hạng học thuộc lòng rất quen (Liên Xô đứng THỨ HAI, không phải đứng đầu)"),
    "su9_vj_0641": (3, "phủ định trên bộ ba 'lương thực/tiêu dùng/xuất khẩu' học thuộc lòng rất quen, dễ loại trừ"),
    # Pair 17 [vai_tro/Medium]
    "su9_vj_0206": (1, "vai trò LHQ 'duy trì hoà bình an ninh' gần như kiến thức phổ thông, không cần học sâu"),
    "su9_vj_2827": (4, "phân biệt VN Giải phóng quân với 3 tổ chức vũ trang tiền thân — chi tiết tổ chức hẹp"),
    # Pair 18 [so_sanh/Medium]
    "su9_vj_0151": (2, "chủ đề Mỹ theo đuổi trật tự thế giới có lợi là luận điểm tổng kết lớn, lặp lại nhiều"),
    "su9_vj_0311": (1, "NAQ đi sang PHƯƠNG TÂY khác Phan Bội Châu là MỘT TRONG những so sánh biểu tượng nhất chương trình"),
    # Pair 19 [so_sanh/Easy] — cả 2 đều nổi bật
    "su9_vj_1857": (2, "Mỹ độc quyền vũ khí nguyên tử sau CTTG2 là fact rất nổi bật"),
    "su9_vj_2535": (2, "tương phản đô thị/rừng núi giữa 2 chiến dịch lớn khá trực quan, hay được nhắc khi ôn so sánh"),
    # Pair 20 [y_nghia/Easy]
    "su9_vj_2913": (1, "Điện Biên Phủ là chiến dịch biểu tượng nhất toàn chương trình Sử 9"),
    "su9_vj_2385": (4, "Đông Khê là 1 trận đánh CỤ THỂ trong chiến dịch lớn hơn — chi tiết hẹp so với tên cả chiến dịch"),
}


# ---------------------------------------------------------------------------
# MẪU NGẪU NHIÊN (không chọn có chủ đích) — 30 câu, phân tầng đều theo nhãn
# LLM (10 Easy / 10 Medium / 10 Hard), rút từ pool 120 câu (test_forms.json)
# TRỪ 40 câu đã dùng ở 20 cặp đối chứng bên trên. Mục đích: đo corr(nhãn LLM,
# p_sim) trên một mẫu KHÔNG bị thiên lệch bởi cách chọn cặp đối chứng — cặp
# đối chứng được CHỌN CÓ CHỦ ĐÍCH để bộc lộ bất đồng, nên corr đo trên riêng
# 40 câu đó không đại diện cho toàn bộ pool. seed=7 khi rút mẫu (script chọn
# mẫu không lưu lại ở đây, nhưng danh sách id dưới đây tái lập được).
RANDOM_SAMPLE_DELTA = {
    # Easy
    "su9_vj_0348": (4, "phủ định (ngoại trừ) + đòi hỏi nhớ CHÍNH XÁC 3 văn kiện thuộc Cương lĩnh, dễ nhầm với 'Bản án chế độ thực dân Pháp' (tác phẩm nổi tiếng KHÁC của NAQ, dễ ngộ nhận là cùng bộ)"),
    "su9_vj_2343": (1, "diệt chủng Khơ-me đỏ là fact biểu tượng, cực kỳ nổi bật"),
    "su9_vj_2714": (1, "quan hệ đối đầu Mỹ-Xô là nền tảng của cả chương Chiến tranh lạnh, ai cũng biết"),
    "su9_vj_2875": (4, "tên phong trào kinh tế 1952 cụ thể, dễ nhầm với các phong trào tên gọi tương tự (giảm tô, thi đua yêu nước, Tuần lễ vàng)"),
    "su9_vj_0477": (2, "cụm từ 'toàn dân toàn diện trường kỳ tự lực cánh sinh' là cụm từ HỌC THUỘC LÒNG nổi tiếng nhất chương kháng chiến chống Pháp"),
    "su9_vj_0154": (3, "phân biệt 'đối tác toàn diện' và 'đối tác chiến lược' là thuật ngữ ngoại giao cụ thể, dễ lẫn"),
    "su9_vj_1755": (4, "phủ định nhẹ + đòi hỏi biết vùng nào Hồng quân LX giải phóng, vùng nào do Đồng minh Tây phương — chi tiết địa-chính trị"),
    "su9_vj_3121": (1, "Đổi Mới trọng tâm kinh tế là fact được nhắc nhiều nhất về ĐH VI"),
    "su9_vj_2102": (3, "lực lượng chủ chốt VNQDĐ là chi tiết tổ chức cụ thể, không phải trọng tâm lớn"),
    "su9_vj_2651": (1, "Liên Xô ưu tiên công nghiệp nặng là fact kinh điển về công nghiệp hóa XHCN"),
    # Medium
    "su9_vj_2935": (4, "điểm mới về NGOẠI GIAO của 'VN hóa chiến tranh' là phân tích so sánh khá tinh vi"),
    "su9_vj_0521": (5, "phủ định + bẫy thời gian (đáp án đúng là hành động XẢY RA SAU khi kế hoạch Nava bị đảo lộn, không phải trước)"),
    "su9_vj_0676": (2, "mục tiêu SEV là câu trả lời mang tính khái quát/hiển nhiên, có thể suy luận đúng mà không cần nhớ chính xác"),
    "su9_vj_1749": (4, "phải phân biệt CHÍNH XÁC giữa 4 trận đánh nổi tiếng của Mặt trận Xô-Đức, dễ nhầm"),
    "su9_vj_2857": (2, "giai đoạn 'bước đầu xây dựng CNXH' của Trung Quốc là mốc phân kỳ tương đối nổi bật"),
    "su9_vj_0415": (2, "Hội nghị TW8 đặt nhiệm vụ giải phóng dân tộc lên hàng đầu là fact rất nổi bật, hay được nhắc"),
    "su9_vj_2250": (2, "xu hướng hòa hoãn Mỹ-Xô cuối Chiến tranh lạnh là mạch truyện chính, quen thuộc"),
    "su9_vj_0242": (2, "'KHKT là nhân tố quyết định' là luận điểm tổng kết quen thuộc, hay lặp lại"),
    "su9_vj_0407": (2, "nhiệm vụ giải phóng dân tộc 1939-1945 là fact rất nổi bật, cùng mạch với Hội nghị TW8"),
    "su9_vj_2505": (4, "dễ nhầm mốc 7/2/1965 với 'sự kiện Vịnh Bắc Bộ' 1964 nổi tiếng hơn — cùng dạng bẫy như câu Plây-cu ở cặp 10"),
    # Hard
    "su9_vj_2191": (4, "kết nối bài học 2 giai đoạn cách mạng khác nhau — tổng hợp phân tích, không phải fact đơn lẻ"),
    "su9_vj_2903": (3, "đáp án đúng là phát biểu khái quát/an toàn ('quan hệ hữu cơ') dễ đoán đúng qua loại trừ dù không nhớ chi tiết"),
    "su9_vj_0274": (6, "phủ định + đòi hỏi hiểu luận điểm sử học tinh vi (QHSX phong kiến KHÔNG bị xóa bỏ mà tồn tại song song với QHSX tư bản thực dân)"),
    "su9_vj_1771": (5, "so sánh tư tưởng cốt lõi (tư sản vs vô sản) giữa 2 tổ chức cách mạng — phân tích tinh vi"),
    "su9_vj_3082": (5, "điểm tương đồng giữa 2 chính quyền cách mạng khác thời kỳ — chi tiết so sánh hẹp"),
    "su9_vj_2874": (4, "phân biệt tinh vi nhiệm vụ CM giữa 2 giai đoạn liền kề (1951-1953 vs 1946-1950)"),
    "su9_vj_2784": (5, "phải chọn ĐÚNG 1 trong 4 luận điểm cùng đúng về Cương lĩnh — phân biệt tinh vi giữa các ý đều hợp lý"),
    "su9_vj_0093": (4, "phủ định nhưng đáp án đúng có 'tell' ngôn ngữ phóng đại ('lớn nhất hành tinh') dễ nhận ra là sai qua đọc kỹ, dù vẫn cần suy luận"),
    "su9_vj_0464": (2, "'ngoại xâm và nội phản' là 1 trong các khó khăn 'ngàn cân treo sợi tóc' RẤT nổi bật sau CM tháng 8"),
    "su9_vj_2531": (5, "so sánh âm mưu chiến lược giữa 2 đợt phá hoại miền Bắc — phân tích tinh vi, dễ nhầm 2 giai đoạn"),
}


def correct_count(tau: int, delta: int) -> int:
    gap = tau - delta
    if gap <= -2:
        return 0
    if gap in (-1, 0):
        return 1
    return 2


def build_responses(delta_dict: dict, tag: str) -> pd.DataFrame:
    rows = []
    for item_id, (delta, _reason) in delta_dict.items():
        for tau in PERSONAS:
            n_correct = correct_count(tau, delta)
            for rep in range(N_REPEATS):
                is_correct = 1 if rep < n_correct else 0
                rows.append({
                    "student_id": f"llmsim_{tag}_p{tau}_r{rep+1}",
                    "form": f"LLMSIM_{tag}",
                    "item_id": item_id,
                    "correct": is_correct,
                })
    return pd.DataFrame(rows)


def label_corr(p_sim: pd.Series, ids: list, all_q: dict) -> dict:
    lab2id = {"Easy": 0, "Medium": 1, "Hard": 2}
    y = np.array([lab2id[all_q[i]["difficulty"]] for i in ids])
    p = np.array([p_sim[i] for i in ids])
    pearson = float(np.corrcoef(y, p)[0, 1])
    ry, rp = pd.Series(y).rank().values, pd.Series(p).rank().values
    spearman = float(np.corrcoef(ry, rp)[0, 1])
    return {"n": len(ids), "pearson": pearson, "spearman": spearman}


def main() -> None:
    import json
    crawled = {r["id"]: r for r in json.loads(
        (REPO / "subjects" / "history" / "samples" / "mcq_crawled.json").read_text(encoding="utf-8"))}
    samples = {r["id"]: r for r in json.loads(
        (REPO / "subjects" / "history" / "samples" / "mcq_samples.json").read_text(encoding="utf-8"))}
    all_q = {**samples, **crawled}
    tf = json.loads((REPO / "subjects" / "history" / "samples" / "test_forms.json")
                    .read_text(encoding="utf-8"))

    df_pairs = build_responses(DELTA, "pairs")
    df_random = build_responses(RANDOM_SAMPLE_DELTA, "random")
    df_all = pd.concat([df_pairs, df_random], ignore_index=True)
    out_path = REPO / "subjects" / "history" / "samples" / "student_responses.LLMSIM.csv"
    df_all.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Đã sinh {len(df_all)} lượt trả lời mô phỏng "
         f"({len(DELTA)} câu cặp đối chứng + {len(RANDOM_SAMPLE_DELTA)} câu mẫu ngẫu nhiên) "
         f"x {len(PERSONAS)} persona x {N_REPEATS} lần lặp")
    print(f"  -> {out_path}\n")

    p_sim_pairs = df_pairs.groupby("item_id")["correct"].mean()
    p_sim_random = df_random.groupby("item_id")["correct"].mean()
    p_sim_all = pd.concat([p_sim_pairs, p_sim_random])

    print("=== [1] Gap trong 20 cặp đối chứng (mẫu CÓ CHỦ ĐÍCH) ===")
    print(f"{'#':<3}{'nhóm/nhãn LLM':<20}{'p_sim A':>9}{'p_sim B':>9}{'gap':>7}")
    gaps = []
    for i, p in enumerate(tf["control_pairs"]):
        a, b = p["core_or_edge_a"], p["core_or_edge_b"]
        pa, pb = p_sim_pairs.get(a, float("nan")), p_sim_pairs.get(b, float("nan"))
        gap = abs(pa - pb)
        gaps.append(gap)
        print(f"{i+1:<3}{p['group']:<20}{pa:>9.2f}{pb:>9.2f}{gap:>7.2f}")
    gaps = np.array(gaps)
    print(f"\nGap trung bình: {gaps.mean():.3f} | cặp gap>=0.3: {(gaps>=0.3).sum()}/{len(gaps)} "
         f"| cặp gap<=0.05: {(gaps<=0.05).sum()}/{len(gaps)}")

    print("\n=== [2] corr(nhãn LLM, p_sim) — SO SÁNH mẫu có chủ đích vs mẫu NGẪU NHIÊN ===")
    c_pairs = label_corr(p_sim_pairs, list(DELTA.keys()), all_q)
    c_random = label_corr(p_sim_random, list(RANDOM_SAMPLE_DELTA.keys()), all_q)
    c_all = label_corr(p_sim_all, list(DELTA.keys()) + list(RANDOM_SAMPLE_DELTA.keys()), all_q)
    print(f"  20 cặp đối chứng (n={c_pairs['n']}, CÓ CHỦ ĐÍCH — không đại diện tổng thể): "
         f"Pearson={c_pairs['pearson']:+.3f}  Spearman={c_pairs['spearman']:+.3f}")
    print(f"  30 câu MẪU NGẪU NHIÊN (n={c_random['n']}, phân tầng Easy/Medium/Hard, "
         f"KHÔNG chọn có chủ đích — đây là ước lượng ít thiên lệch nhất):")
    print(f"    Pearson={c_random['pearson']:+.3f}  Spearman={c_random['spearman']:+.3f}")
    print(f"  Gộp cả 70 câu (n={c_all['n']}): "
         f"Pearson={c_all['pearson']:+.3f}  Spearman={c_all['spearman']:+.3f}")

    print("\n⚠ Đây là pilot ĐỊNH TÍNH bằng mô phỏng hành vi LLM (không phải học sinh "
         "thật) — dùng để MINH HOẠ cơ chế phân tích, không phải bằng chứng khoa học "
         "cuối cùng. Kết luận chính thức PHẢI chờ p-value thật từ T4. Mẫu ngẫu nhiên "
         "(mục [2] dòng 2) là con số ÍT THIÊN LỆCH NHẤT trong pilot này — nên trích dẫn "
         "con số đó, KHÔNG trích corr trên riêng 20 cặp đối chứng làm 'tương quan chung'.")


if __name__ == "__main__":
    main()
