# -*- coding: utf-8 -*-
"""ĐÓNG GÓI TÁI LẬP — chạy lại toàn bộ thí nghiệm và kiểm tra số có trôi không.

Vì sao cần: mọi con số trong báo cáo đều nằm rải trong các file JSON do nhiều
công cụ khác nhau sinh ra, ở nhiều thời điểm khác nhau. Không có gì bảo đảm
rằng chạy lại hôm nay vẫn ra đúng số đã viết. Công cụ này biến bảng kết quả
của báo cáo thành một BÀI KIỂM TRA HỒI QUY.

Hai loại bước, tách bạch:

  offline  tất định, chạy lại được miễn phí (seed cố định). Đây là phần hội
           đồng kiểm chứng được.
  llm      cần gọi mô hình ngôn ngữ, TỐN TIỀN và không tái lập bit-by-bit.
           KHÔNG chạy lại. Kết quả đóng băng thành dữ liệu đầu vào, và công
           cụ chỉ kiểm tra file còn đó, đúng số dòng.

Chạy:
    python tools/reproduce_all.py --list             # xem kế hoạch
    python tools/reproduce_all.py --check            # đối chiếu số hiện có với bảng đóng băng
    python tools/reproduce_all.py --run              # chạy lại toàn bộ bước offline
    python tools/reproduce_all.py --run --only axis_evidence
    python tools/reproduce_all.py --freeze           # ghi số hiện tại làm mốc
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent

# --backend <tên>: đối chiếu bộ số của LỚP GIẢI THÍCH chạy trên mô hình nền đó
# (xem tools/text_backend.py). Dùng ĐÚNG danh sách con số ở dưới, chỉ đổi file
# nguồn sang bản có hậu tố khi bản đó tồn tại. Các con số KHÔNG phụ thuộc mô
# hình (trục thao tác, bằng chứng trục, nguồn nhãn, người–người, hồ sơ đo đạc
# bốn mô hình) không có bản hậu tố nên tự động đọc lại file gốc — cố ý, để các
# bảng so được với nhau theo từng dòng.
BACKEND = "xgb15"
SUFFIX = {"xgb15": "", "text": "_pb", "tfidf": "_tf", "emb": "_eo"}
BACKEND_DESC = {
    "xgb15": "XGBoost trên 15 cột luật tay",
    "text": "PhoBERT đóng băng + 15 cột luật tay",
    "tfidf": "TF-IDF từ + ký tự + 15 cột luật tay",
    "emb": "PhoBERT đóng băng, KHÔNG cột luật tay",
}


def frozen_file():
    return REPO / "docs" / f"results_frozen{SUFFIX[BACKEND]}.json"


def resolve(f: str) -> Path:
    """Đường dẫn file nguồn cho backend đang chọn (rơi về bản gốc nếu chưa có)."""
    p = REPO / f
    suf = SUFFIX[BACKEND]
    if suf:
        alt = REPO / (f[:-5] + suf + ".json")
        if alt.exists():
            return alt
    return p


PY = sys.executable

# ----------------------------------------------------------------------
# Các bước. Thứ tự là thứ tự phụ thuộc: bước sau đọc đầu ra của bước trước.
# ----------------------------------------------------------------------
STEPS = [
    # --- ĐÓNG BĂNG: cần LLM, không chạy lại ---
    dict(id="answer_key", kind="llm", mins=None,
         desc="sinh đáp án + kiểm mù cho bộ Sử (kenhgiaovien)",
         cmd=["tools/llm_answer_key.py", "--subject", "history"],
         outputs=["subjects/history/samples/mcq_kenhgiaovien.json",
                  "subjects/history/samples/answer_key_report.json"]),
    dict(id="solution_trace", kind="llm", mins=None,
         desc="vết giải LLM cho môn Lý (đặc trưng, KHÔNG phải nhãn)",
         cmd=["tools/llm_solution_trace.py", "--subject", "physics"],
         outputs=["subjects/physics/samples/solution_traces.json"]),
    dict(id="llm_judge", kind="llm", mins=None,
         desc="LLM chấm mức NB/TH/VD/VDC (dùng làm nguồn nhãn đối chứng)",
         cmd=["tools/llm_judge_labels.py", "--subject", "physics"],
         outputs=["subjects/physics/samples/mcq_kenhgiaovien_llmjudge.json"]),

    # --- OFFLINE: tất định, chạy lại được ---
    dict(id="counterfactual_physics", kind="offline", mins=6,
         desc="hiệu lực phản thực, môn Lý",
         cmd=["tools/counterfactual_validity.py", "--subject", "physics"],
         outputs=["subjects/physics/samples/counterfactual_validity.json"]),
    dict(id="counterfactual_history_gv", kind="offline", mins=5,
         desc="hiệu lực phản thực, mảng Sử nhãn giáo viên",
         cmd=["tools/counterfactual_validity.py", "--subject", "history_gv"],
         outputs=["subjects/history/samples/counterfactual_validity_gv.json"]),
    # Phải chạy TRƯỚC các bước XAI: cổng chứng chỉ đọc phân bố rỗng từ đây.
    # Lần chạy đã có file trong samples/sanity/ thì bỏ qua — xoá thư mục đó để
    # chạy lại từ đầu (bắt buộc nếu sửa counterfactual_validity.py).
    dict(id="xai_sanity", kind="offline", mins=20,
         desc="kiểm tra tỉnh táo cổng B1: 39 mô hình nhãn xáo + 3 seed, hai môn",
         cmd=["tools/xai_sanity.py"],
         outputs=["docs/xai_sanity.json"]),
    dict(id="natural_raters", kind="offline", mins=2,
         desc="người chấm tự nhiên: độ tin cậy nhãn GV trên câu trùng, máy vs người",
         cmd=["tools/natural_raters.py"],
         outputs=["docs/natural_raters.json"]),
    dict(id="operation_axis", kind="offline", mins=4,
         desc="trục thao tác: ontology tiên quyết + vết giải",
         cmd=["tools/operation_axis.py", "--subject", "both"],
         outputs=["subjects/physics/samples/operation_axis.json"]),
    dict(id="axis_evidence", kind="offline", mins=8,
         desc="ba cửa bác bỏ cho từng trục (hiệu ứng cố định · cặp · can thiệp)",
         cmd=["tools/axis_evidence.py", "--subject", "both"],
         outputs=["subjects/history/samples/axis_evidence.json"]),
    dict(id="ablation", kind="offline", mins=3,
         desc="ablation với khối KG đầy đủ",
         cmd=["tools/ablate_full.py", "--subject", "both"],
         outputs=["subjects/physics/samples/ablation_full.json",
                  "subjects/history/samples/ablation_full_gv.json"]),
    dict(id="incremental_value", kind="offline", mins=6,
         desc="giá trị biên: đặc trưng sạch vs nhãn LLM",
         cmd=["tools/incremental_value.py", "--subject", "both"],
         outputs=["subjects/history/samples/incremental_value.json"]),
    dict(id="label_source_axes", kind="offline", mins=5,
         desc="nguồn nhãn nào giữ được trục nào (bề mặt là tạo tác của người gán)",
         cmd=["tools/label_source_axes.py"],
         outputs=["subjects/history/samples/label_source_axes.json"]),
    dict(id="xai_validate_physics", kind="offline", mins=4,
         desc="XAI kiểm tra chéo nửa A/nửa B, môn Lý",
         cmd=["tools/xai_difficulty.py", "--validate", "--subject", "physics",
              "--n", "150", "--reps", "16", "--out",
              "subjects/physics/samples/xai_validate.json"],
         outputs=["subjects/physics/samples/xai_validate.json"]),
    dict(id="xai_coverage", kind="offline", mins=3,
         desc="độ phủ can thiệp: trục nào đo được ở bao nhiêu câu",
         cmd=["tools/_run_xai.py", "coverage"],
         outputs=["subjects/physics/samples/xai_coverage.json",
                  "subjects/history/samples/xai_coverage_gv.json"]),
    dict(id="xai_selective", kind="offline", mins=12,
         desc="khai thác: lời giải thích có dùng để TỪ CHỐI trả lời được không",
         cmd=["tools/_run_xai.py", "selective"],
         outputs=["subjects/physics/samples/xai_selective.json",
                  "subjects/history/samples/xai_selective_gv.json"]),
    dict(id="xai_recourse", kind="offline", mins=9,
         desc="khai thác: sửa tối thiểu gì thì hệ xếp lại mức",
         cmd=["tools/_run_xai.py", "recourse"],
         outputs=["subjects/physics/samples/xai_recourse.json",
                  "subjects/history/samples/xai_recourse_gv.json"]),
    dict(id="xai_validate_history", kind="offline", mins=4,
         desc="XAI kiểm tra chéo nửa A/nửa B, mảng Sử",
         cmd=["tools/xai_difficulty.py", "--validate", "--subject",
              "history_gv", "--n", "150", "--reps", "16", "--out",
              "subjects/history/samples/xai_validate_gv.json"],
         outputs=["subjects/history/samples/xai_validate_gv.json"]),
    dict(id="text_vs_rules", kind="offline", mins=75,
         desc="đặc trưng viết tay hay biểu diễn học được: cái nào là chỗ nghẽn",
         cmd=["tools/text_vs_rules.py", "--subject", "both"],
         outputs=["docs/text_vs_rules.json"]),
]

# ----------------------------------------------------------------------
# Các con số ĐƯỢC TRÍCH DẪN trong báo cáo / README. Mỗi dòng: nhãn, file,
# đường dẫn khoá (ngăn bằng "/"), dung sai, và chỗ nó được dẫn.
# Dung sai tuyệt đối — đặt theo mức mà kết luận vẫn giữ nguyên nếu số trôi
# trong khoảng đó.
# ----------------------------------------------------------------------
H = "subjects/history/samples"
P = "subjects/physics/samples"
CLAIMS = [
    # ---- mảng Vật lí ----
    ("Lý · trục thao tác, t trong cùng bài", f"{H}/axis_evidence.json",
     "results/physics/THAO TÁC/fixed_effects/tr_steps/within/t", 0.5, "BC 1.1 KQ1"),
    ("Lý · trục thao tác, tỉ lệ cặp thắng", f"{H}/axis_evidence.json",
     "results/physics/THAO TÁC/pair_test/tr_steps/rate", 0.01, "BC 1.1 KQ1"),
    ("Lý · can thiệp khối thao tác, tỉ trọng", f"{H}/axis_evidence.json",
     "results/physics/THAO TÁC/intervention/khối thao tác/share", 0.02, "BC 1.1 KQ1"),
    ("Lý · đối chứng (kad_path_distance)", f"{H}/axis_evidence.json",
     "results/physics/THAO TÁC/intervention/kad_path_distance_mean ⟨đối chứng⟩/share",
     0.01, "BC 1.1 KQ1"),
    ("Lý · trục tri thức chạy NGƯỢC, t", f"{H}/axis_evidence.json",
     "results/physics/TRI THỨC/fixed_effects/kg_centrality_mean/within/t",
     0.5, "BC 1.1 KQ3"),
    ("Lý · AUC tầng cao, thao tác+vết giải", f"{P}/operation_axis.json",
     "results/physics/thao tác + vết giải/auc_high", 0.02, "BC 1.1 KQ2"),
    ("Lý · QWK, thao tác+vết giải", f"{P}/operation_axis.json",
     "results/physics/thao tác + vết giải/qwk", 0.03, "BC 1.1 KQ2"),
    ("Lý · nền bề mặt, QWK", f"{P}/operation_axis.json",
     "results/physics/bề mặt (hiện tại)/qwk", 0.03, "BC 1.1 KQ2"),
    ("Lý · số cạnh prerequisiteOf", f"{P}/operation_axis.json",
     "results/physics/n_prereq_edges", 0, "BC 1.1"),
    ("Lý · phản thực num_down vượt đối chứng", f"{P}/counterfactual_validity.json",
     "arms/num_down/vs_control_diff", 0.02, "XAI B1"),
    ("Lý · kg_near đi đúng hướng (dưới 50%)", f"{P}/counterfactual_validity.json",
     "arms/kg_near/direction_agreement", 0.03, "XAI B1"),
    ("Lý · XAI trần lặp lại (nửa A→B)", f"{P}/xai_validate.json",
     "rho_split_half", 0.06, "XAI kiểm tra chéo"),
    ("Lý · XAI, SHAP dự báo nửa B", f"{P}/xai_validate.json",
     "rho_shap_vs_intervention", 0.08, "XAI kiểm tra chéo"),

    # ---- mảng Lịch sử ----
    ("Sử · can thiệp khối tri thức, tỉ trọng", f"{H}/axis_evidence.json",
     "results/history_gv/TRI THỨC/intervention/khối tri thức/share",
     0.03, "BC 1.2"),
    ("Sử · đối chứng (kad_path_distance)", f"{H}/axis_evidence.json",
     "results/history_gv/TRI THỨC/intervention/kad_path_distance_mean ⟨đối chứng⟩/share",
     0.01, "BC 1.2"),
    ("Sử · trục tri thức, t trong cùng ô", f"{H}/axis_evidence.json",
     "results/history_gv/TRI THỨC/fixed_effects/kg_centrality_mean/within/t",
     0.4, "BC 1.2"),
    ("Sử · giữ trục bề mặt khi đổi nguồn nhãn", f"{H}/label_source_axes.json",
     "differential_retention/bề mặt/retention", 0.05, "BC 1.2"),
    ("Sử · giữ trục KG khi đổi nguồn nhãn", f"{H}/label_source_axes.json",
     "differential_retention/KG đầy đủ/retention", 0.08, "BC 1.2"),
    ("Sử · phản thực len_up vượt đối chứng", f"{H}/counterfactual_validity_gv.json",
     "arms/len_up/vs_control_diff", 0.02, "XAI B1"),
    ("Sử · XAI trần lặp lại (nửa A→B)", f"{H}/xai_validate_gv.json",
     "rho_split_half", 0.06, "XAI kiểm tra chéo"),
    ("Sử · XAI, SHAP dự báo nửa B", f"{H}/xai_validate_gv.json",
     "rho_shap_vs_intervention", 0.08, "XAI kiểm tra chéo"),

    # ---- độ phủ: mọi kết luận từng câu về trục KG chỉ có giá trị trên tập này
    ("Lý · độ phủ trục TRI THỨC", f"{P}/xai_coverage.json",
     "by_axis/TRI THỨC", 0.01, "XAI độ phủ"),
    ("Lý · độ phủ trục BỀ MẶT", f"{P}/xai_coverage.json",
     "by_axis/BỀ MẶT", 0.01, "XAI độ phủ"),
    ("Sử · độ phủ trục TRI THỨC", f"{H}/xai_coverage_gv.json",
     "by_axis/TRI THỨC", 0.01, "XAI độ phủ"),
    ("Sử · độ phủ trục BỀ MẶT", f"{H}/xai_coverage_gv.json",
     "by_axis/BỀ MẶT", 0.01, "XAI độ phủ"),
    # cổng THEO NHÁNH: trục BỀ MẶT chỉ nói được ở câu dựng được nhánh đạt chứng chỉ
    ("Lý · độ phủ nhánh num_down (cổng theo nhánh)", f"{P}/xai_coverage.json",
     "by_arm/num_down", 0.01, "XAI độ phủ"),
    ("Sử · độ phủ nhánh len_down (cổng theo nhánh)", f"{H}/xai_coverage_gv.json",
     "by_arm/len_down", 0.01, "XAI độ phủ"),

    # ---- khai thác: kết quả ÂM về từ chối có chọn lọc, và lời khuyên sửa đề
    # Buộc luôn cả đối chứng entropy: kết luận "sức giải thích thua entropy"
    # chỉ đứng được khi entropy THẬT SỰ đi lên. Nếu một ngày entropy cũng đi
    # xuống thì phép đo hỏng, không phải kết luận đúng.
    ("Lý · từ chối theo entropy @20% (đối chứng)", f"{P}/xai_selective.json",
     "curve/entropy (đối chứng)/4", 0.08, "XAI khai thác 8b.1"),
    ("Lý · từ chối theo sức giải thích @20%", f"{P}/xai_selective.json",
     "curve/sức giải thích/4", 0.08, "XAI khai thác 8b.1"),
    ("Sử · từ chối theo entropy @20% (đối chứng)", f"{H}/xai_selective_gv.json",
     "curve/entropy (đối chứng)/4", 0.08, "XAI khai thác 8b.1"),
    ("Sử · từ chối theo sức giải thích @20%", f"{H}/xai_selective_gv.json",
     "curve/sức giải thích/4", 0.08, "XAI khai thác 8b.1"),
    # Kết luận của mục 8b.2 dựa vào HAI số này, nên chúng phải bị buộc: ở Lý nó
    # gần 0 (kết quả rỗng), ở Sử nó dương rõ (sức giải thích đi sai hướng).
    ("Lý · rho(sức giải thích, |sai lệch|)", f"{P}/xai_selective.json",
     "mechanism/rho_strength_abserr", 0.08, "XAI khai thác 8b.2"),
    ("Sử · rho(sức giải thích, |sai lệch|)", f"{H}/xai_selective_gv.json",
     "mechanism/rho_strength_abserr", 0.08, "XAI khai thác 8b.2"),
    ("Lý · rho(sức giải thích, entropy)", f"{P}/xai_selective.json",
     "mechanism/rho_strength_entropy", 0.08, "XAI khai thác 8b.2"),
    ("Sử · rho(sức giải thích, entropy)", f"{H}/xai_selective_gv.json",
     "mechanism/rho_strength_entropy", 0.08, "XAI khai thác 8b.2"),
    ("Lý · sửa được xuống mức thấp hơn", f"{P}/xai_recourse.json",
     "editable_down", 0.06, "XAI khai thác 8b.3"),
    ("Sử · sửa được xuống mức thấp hơn", f"{H}/xai_recourse_gv.json",
     "editable_down", 0.06, "XAI khai thác 8b.3"),

    # ---- 09/2026 · độ tin cậy lời giải thích, trần đúng √ρ, SHAP công bằng nhất
    ("Lý · độ tin cậy lời giải thích (Spearman–Brown)", f"{P}/xai_validate.json",
     "reliability_full_spearman_brown", 0.05, "XAI kiểm tra chéo"),
    ("Lý · SHAP cây, tỉ lệ trần √ρ", f"{P}/xai_validate.json",
     "frac_ceiling_shap", 0.10, "XAI kiểm tra chéo"),
    ("Lý · Shapley khối trên E[y] dự báo nửa B", f"{P}/xai_validate.json",
     "rho_groupshap_vs_intervention", 0.08, "XAI kiểm tra chéo"),
    ("Sử · độ tin cậy lời giải thích (Spearman–Brown)", f"{H}/xai_validate_gv.json",
     "reliability_full_spearman_brown", 0.05, "XAI kiểm tra chéo"),
    ("Sử · Shapley khối trên E[y] dự báo nửa B", f"{H}/xai_validate_gv.json",
     "rho_groupshap_vs_intervention", 0.08, "XAI kiểm tra chéo"),

    # ---- người chấm tự nhiên: người–người không phụ thuộc mô hình → dung sai ~0
    ("Lý · người–người trên câu trùng (QWK)", "docs/natural_raters.json",
     "physics/qwk_human_human", 0.001, "Nhãn · người chấm tự nhiên"),
    ("Lý · máy–người trên CÙNG câu trùng (QWK)", "docs/natural_raters.json",
     "physics/qwk_machine_human", 0.05, "Nhãn · người chấm tự nhiên"),
    ("Sử · người–người trên câu trùng (QWK)", "docs/natural_raters.json",
     "history_gv/qwk_human_human", 0.001, "Nhãn · người chấm tự nhiên"),
    ("Sử · máy–người trên CÙNG câu trùng (QWK)", "docs/natural_raters.json",
     "history_gv/qwk_machine_human", 0.05, "Nhãn · người chấm tự nhiên"),

    # ---- kiểm tra tỉnh táo cổng B1 (K = 39). Buộc cả ba luật: kết luận "luật cũ
    # cấp nhầm gần hết mô hình nhãn xáo" và "nhánh BỚT vượt mọi mô hình nhãn
    # xáo, nhánh THÊM thì không chắc" phải đứng được trong các dung sai này.
    ("Lý · luật CŨ cấp nhầm cho mô hình nhãn xáo (/39)", "docs/xai_sanity.json",
     "physics/false_cert/legacy", 5, "XAI kiểm tra tỉnh táo"),
    ("Lý · luật CHẶT cấp nhầm (/39)", "docs/xai_sanity.json",
     "physics/false_cert/iut", 1, "XAI kiểm tra tỉnh táo"),
    ("Lý · theo nhánh, cấp nhầm ≥ 1 nhánh (/39)", "docs/xai_sanity.json",
     "physics/false_cert/any_arm_calibrated", 2, "XAI kiểm tra tỉnh táo"),
    ("Lý · p hoán vị num_down", "docs/xai_sanity.json",
     "physics/p_perm/num_down", 0.02, "XAI kiểm tra tỉnh táo"),
    ("Lý · p hoán vị num_up", "docs/xai_sanity.json",
     "physics/p_perm/num_up", 0.04, "XAI kiểm tra tỉnh táo"),
    ("Sử · luật CŨ cấp nhầm cho mô hình nhãn xáo (/39)", "docs/xai_sanity.json",
     "history_gv/false_cert/legacy", 5, "XAI kiểm tra tỉnh táo"),
    ("Sử · luật CHẶT cấp nhầm (/39)", "docs/xai_sanity.json",
     "history_gv/false_cert/iut", 1, "XAI kiểm tra tỉnh táo"),
    ("Sử · theo nhánh, cấp nhầm ≥ 1 nhánh (/39)", "docs/xai_sanity.json",
     "history_gv/false_cert/any_arm_calibrated", 2, "XAI kiểm tra tỉnh táo"),
    ("Sử · p hoán vị len_down", "docs/xai_sanity.json",
     "history_gv/p_perm/len_down", 0.02, "XAI kiểm tra tỉnh táo"),
    ("Sử · p hoán vị len_up", "docs/xai_sanity.json",
     "history_gv/p_perm/len_up", 0.02, "XAI kiểm tra tỉnh táo"),

    # ---- hồ sơ đo đạc biện minh cho việc đổi mô hình nền ----
    # docs/text_vs_rules.json so BỐN mô hình trên cùng lát cắt, nên nó KHÔNG có
    # bản _pb: một file chứa cả hai họ mô hình. Xem docs/MODEL_UPGRADE.md.
    ("Lý · bài chưa gặp, 15 cột viết tay (QWK)", "docs/text_vs_rules.json",
     "physics/main/bài mới/R15/qwk", 0.03, "MODEL_UPGRADE §3"),
    ("Lý · bài chưa gặp, PhoBERT + 15 cột (QWK)", "docs/text_vs_rules.json",
     "physics/main/bài mới/E+R15/qwk", 0.03, "MODEL_UPGRADE §3"),
    ("Lý · lát ngẫu nhiên, 15 cột viết tay (QWK)", "docs/text_vs_rules.json",
     "physics/main/ngẫu nhiên/R15/qwk", 0.03, "MODEL_UPGRADE §2"),
    ("Lý · lát ngẫu nhiên, TF-IDF (QWK)", "docs/text_vs_rules.json",
     "physics/main/ngẫu nhiên/T/qwk", 0.03, "MODEL_UPGRADE §2"),
    ("Sử · bài chưa gặp, 15 cột viết tay (QWK)", "docs/text_vs_rules.json",
     "history_gv/main/bài mới/R15/qwk", 0.04, "MODEL_UPGRADE §3"),
    ("Sử · bài chưa gặp, PhoBERT + 15 cột (QWK)", "docs/text_vs_rules.json",
     "history_gv/main/bài mới/E+R15/qwk", 0.05, "MODEL_UPGRADE §3"),
    ("Lý · đường cong 15 cột, 25% số bài", "docs/text_vs_rules.json",
     "physics/curve/R15/0.25/qwk", 0.03, "MODEL_UPGRADE §4"),
    ("Lý · đường cong PhoBERT+15, 25% số bài", "docs/text_vs_rules.json",
     "physics/curve/E+R15/0.25/qwk", 0.06, "MODEL_UPGRADE §4"),
    ("Sử · đường cong 15 cột, 25% số bài", "docs/text_vs_rules.json",
     "history_gv/curve/R15/0.25/qwk", 0.06, "MODEL_UPGRADE §4"),
    ("Sử · đường cong PhoBERT+15, 25% số bài", "docs/text_vs_rules.json",
     "history_gv/curve/E+R15/0.25/qwk", 0.04, "MODEL_UPGRADE §4"),
    ("Lý · câu trùng, người–người", "docs/text_vs_rules.json",
     "physics/dup_pairs/R15/hh", 0.01, "MODEL_UPGRADE §5"),
    ("Lý · câu trùng, máy–người (15 cột)", "docs/text_vs_rules.json",
     "physics/dup_pairs/R15/mh", 0.03, "MODEL_UPGRADE §5"),
    ("Lý · câu trùng, máy–người (PhoBERT+15)", "docs/text_vs_rules.json",
     "physics/dup_pairs/E+R15/mh", 0.03, "MODEL_UPGRADE §5"),
    ("Sử · câu trùng, người–người", "docs/text_vs_rules.json",
     "history_gv/dup_pairs/R15/hh", 0.01, "MODEL_UPGRADE §5"),
    ("Sử · câu trùng, máy–người (15 cột)", "docs/text_vs_rules.json",
     "history_gv/dup_pairs/R15/mh", 0.03, "MODEL_UPGRADE §5"),
    ("Sử · câu trùng, máy–người (PhoBERT+15)", "docs/text_vs_rules.json",
     "history_gv/dup_pairs/E+R15/mh", 0.04, "MODEL_UPGRADE §5"),
]


def dig(obj, path: str):
    cur = obj
    for k in path.split("/"):
        if isinstance(cur, list):
            cur = cur[int(k)]
        else:
            if k not in cur:
                raise KeyError(f"{path}  (kẹt ở '{k}')")
            cur = cur[k]
    return cur


def read_claims() -> dict:
    out = {}
    for label, f, path, tol, src in CLAIMS:
        p = resolve(f)
        if not p.exists():
            out[label] = {"value": None, "err": "thiếu file"}
            continue
        try:
            v = dig(json.loads(p.read_text(encoding="utf-8")), path)
        except Exception as e:                            # noqa: BLE001
            out[label] = {"value": None, "err": str(e)[:70]}
            continue
        # null CÓ CHỦ Ý ≠ đọc lỗi. Mô hình nền `emb` không dùng cột luật tay
        # nào, nên mọi đại lượng quy kết là KHÔNG ĐỊNH NGHĨA ĐƯỢC chứ không
        # phải bằng 0 — công cụ sinh ra chúng ghi null, và ở đây phải giữ
        # nguyên ý đó thay vì coi là hỏng.
        out[label] = ({"value": None, "undefined": True} if v is None
                      else {"value": float(v)})
    return out


def cmd_list():
    print("=" * 78)
    print("KẾ HOẠCH TÁI LẬP")
    print("=" * 78)
    for kind, title, note in (
            ("llm", "ĐÓNG BĂNG — cần LLM, KHÔNG chạy lại",
             "tốn tiền và không tái lập bit-by-bit; đầu ra là dữ liệu đầu vào"),
            ("offline", "OFFLINE — tất định, chạy lại được",
             "seed 42 cố định; đây là phần hội đồng kiểm chứng được")):
        rows = [s for s in STEPS if s["kind"] == kind]
        tot = sum(s["mins"] or 0 for s in rows)
        print(f"\n── {title}   ({len(rows)} bước"
              + (f", ~{tot} phút)" if tot else ")"))
        print(f"   {note}")
        for s in rows:
            miss = [o for o in s["outputs"] if not (REPO / o).exists()]
            mark = "✗ thiếu đầu ra" if miss else "✓"
            mins = f"~{s['mins']}′" if s["mins"] else "  —"
            print(f"   {mark:14s} {s['id']:26s} {mins:>5s}  {s['desc']}")
            for o in miss:
                print(f"                  thiếu: {o}")
    print(f"\n{len(CLAIMS)} con số được trích dẫn sẽ được đối chiếu ở --check.")


def cmd_run(only=None):
    rows = [s for s in STEPS if s["kind"] == "offline"
            and (only is None or s["id"] == only)]
    if not rows:
        sys.exit(f"không có bước offline nào tên '{only}'")
    print(f"Chạy {len(rows)} bước offline. Bước LLM bị bỏ qua có chủ đích.\n")
    for s in rows:
        print("─" * 78)
        print(f"▶ {s['id']} — {s['desc']}")
        t0 = time.time()
        r = subprocess.run([PY] + s["cmd"], cwd=REPO,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        dt = time.time() - t0
        if r.returncode != 0:
            print(f"  ✗ LỖI sau {dt:.0f}s (mã {r.returncode})")
            print("  " + (r.stderr or "")[-1200:].replace("\n", "\n  "))
            sys.exit(1)
        print(f"  ✓ xong sau {dt:.0f}s")
    print("\nXong. Chạy --check để đối chiếu số với bảng đóng băng.")


def cmd_freeze():
    cur = read_claims()
    bad = {k: v for k, v in cur.items()
           if v.get("value") is None and not v.get("undefined")}
    if bad:
        print("KHÔNG đóng băng được — còn số đọc lỗi:")
        for k, v in bad.items():
            print(f"  {k}: {v.get('err')}")
        sys.exit(1)
    payload = {
        "frozen_at": time.strftime("%Y-%m-%d"),
        "note": "Mốc để --check đối chiếu. Chỉ cập nhật khi CÓ CHỦ Ý đổi "
                "phương pháp, và phải ghi lý do trong docs/RESULTS_FROZEN.md.",
        "values": {k: v["value"] for k, v in cur.items()},
    }
    frozen_file().write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                             encoding="utf-8")
    print(f"Đã đóng băng {len(cur)} số vào "
          f"{frozen_file().relative_to(REPO)}  [backend {BACKEND}]")


def cmd_check():
    if not frozen_file().exists():
        sys.exit(f"chưa có {frozen_file().relative_to(REPO)} — chạy --freeze trước")
    frozen = json.loads(frozen_file().read_text(encoding="utf-8"))
    ref, cur = frozen["values"], read_claims()
    tol = {c[0]: c[3] for c in CLAIMS}
    src = {c[0]: c[4] for c in CLAIMS}
    print("=" * 78)
    print(f"ĐỐI CHIẾU với mốc đóng băng ngày {frozen['frozen_at']}")
    print("=" * 78)
    print(f"{'con số':44s}{'mốc':>10s}{'hiện tại':>11s}{'lệch':>9s}  kết")
    npass = nfail = nmiss = 0
    for label, _f, _p, t, _s in CLAIMS:
        c = cur[label]
        if label not in ref:
            print(f"{label:44s}{'—':>10s}{'—':>11s}{'—':>9s}  MỚI (chưa có mốc)")
            nmiss += 1
            continue
        if c.get("value") is None and c.get("undefined"):
            ok = ref[label] is None
            npass += ok
            nfail += (not ok)
            print(f"{label:44s}{'—' if ref[label] is None else ref[label]:>10}"
                  f"{'—':>11s}{'—':>9s}  "
                  + ("khớp (không định nghĩa được)" if ok
                     else "LỆCH: mốc có số, hiện tại không định nghĩa được"))
            continue
        if c.get("value") is None:
            print(f"{label:44s}{ref[label]:10.4f}{'—':>11s}{'—':>9s}  "
                  f"KHÔNG ĐỌC ĐƯỢC: {c.get('err')}")
            nfail += 1
            continue
        if ref[label] is None:
            print(f"{label:44s}{'—':>10s}{c['value']:11.4f}{'—':>9s}  "
                  f"LỆCH: mốc không định nghĩa được, hiện tại có số")
            nfail += 1
            continue
        d = c["value"] - ref[label]
        ok = abs(d) <= t
        npass += ok
        nfail += (not ok)
        print(f"{label:44s}{ref[label]:10.4f}{c['value']:11.4f}{d:+9.4f}  "
              f"{'khớp' if ok else f'LỆCH (dung sai {t})'}")
    print()
    print(f"khớp {npass} · lệch {nfail} · chưa có mốc {nmiss}")
    if nfail:
        print("\nMột số LỆCH nghĩa là con số trong báo cáo không còn đúng với")
        print("mã hiện tại. Trước khi --freeze lại, phải biết vì sao nó đổi.")
    else:
        print("\nMọi con số được trích dẫn vẫn tái lập được.")
    print("\nNguồn trích dẫn:")
    for k in sorted({v for v in src.values()}):
        print(f"  {k}: " + ", ".join(l for l, s in src.items() if s == k)[:200])
    return nfail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--backend", default="xgb15", choices=list(SUFFIX),
                    help="mô hình nền của LỚP GIẢI THÍCH; mỗi cái đọc file có "
                         "hậu tố riêng và đóng băng ra bảng mốc riêng "
                         "(xgb15='' · text=_pb · tfidf=_tf · emb=_eo)")
    a = ap.parse_args()
    global BACKEND
    BACKEND = a.backend
    if BACKEND != "xgb15":
        os.environ["QDE_BACKEND"] = BACKEND
    if not any([a.list, a.run, a.check, a.freeze]):
        cmd_list()
        return
    if a.list:
        cmd_list()
    if a.run:
        cmd_run(a.only)
    if a.freeze:
        cmd_freeze()
    if a.check:
        sys.exit(1 if cmd_check() else 0)


if __name__ == "__main__":
    main()
