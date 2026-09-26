# -*- coding: utf-8 -*-
"""Biểu diễn độ khó bằng HAI TRỤC — có khả thi với asset đang có không?

Lí thuyết hai trục của đề tài:

    độ khó  =  TRỤC TRI THỨC (câu hỏi nằm ở đâu trong đồ thị tri thức)
             × TRỤC THAO TÁC (câu hỏi đòi thao tác nhận thức gì — NB/TH/VD/VDC)

Chẩn đoán trước khi đo: **chỉ trục thứ nhất đang có dụng cụ đo.** Mọi cột KG
hiện tại (`kad_path_distance_mean`, `jaccard_*`, `rsi_dc`, `kg_prereq_*`) đều đo
quan hệ ĐÁP ÁN ↔ NHIỄU — tức độ gây nhiễu của phương án, giả thuyết Vinu. Không
có cột nào đo CÂU DẪN → ĐÁP ÁN, tức bao nhiêu bước suy luận. Còn cái đang đóng
vai "trục thao tác" thì thực chất chỉ là **độ dài văn bản**, và độ dài đã bị
chứng minh là đặc tính của người gán nhãn LLM chứ không của độ khó
(`tools/label_source_axes.py`).

Nên phép này thêm hai bộ dụng cụ mới cho TRỤC THAO TÁC rồi đo xem có tín hiệu:

  A. DẤU HIỆU NGÔN NGỮ — động từ/khuôn hỏi tiếng Việt phân tầng Bloom:
     "là gì / năm nào"        → nhớ lại
     "vì sao / nguyên nhân"   → hiểu
     "so sánh / nhận xét"     → vận dụng
     "bài học / đánh giá"     → vận dụng cao
     cùng các dấu hiệu phụ: so sánh nhất ("chủ yếu nhất"), phủ định
     ("không phải", "ngoại trừ"), giả định ("nếu", "giả sử").

  B. CHIỀU SÂU SUY LUẬN TRÊN ĐỒ THỊ — số bước từ thực thể trong CÂU DẪN tới
     thực thể trong ĐÁP ÁN. Đây mới là thứ đáng gọi là "trục thao tác trên KG",
     và đề tài chưa từng tính nó.

Bảy bộ đặc trưng, đo trên CẢ HAI nguồn nhãn. Thước đo gồm cả AUC tầng cao —
bất biến với tỉ lệ lớp, nên không đổ lỗi được cho phân bố nhãn lệch.

Chạy:  python tools/two_axis_feasibility.py [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score, f1_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

NAME = ["NB", "TH", "VD", "VDC"]
MK = dict(n_estimators=200, max_depth=4, learning_rate=0.1, subsample=0.8,
          colsample_bytree=0.8, eval_metric="mlogloss", verbosity=0)

# ---------------------------------------------------------------- trục thao tác A
CUES = {
    "op_recall": ["là gì", "nào sau đây", "nào dưới đây", "năm nào", "ở đâu",
                  "khi nào", "ai là", "kể tên", "được gọi là", "gồm những",
                  "vào thời gian", "diễn ra ở", "tên gọi"],
    "op_explain": ["vì sao", "tại sao", "nguyên nhân", "lí do", "lý do",
                   "giải thích", "nhằm", "mục đích", "thể hiện", "phản ánh",
                   "chứng tỏ", "có nghĩa"],
    "op_apply": ["nhận xét", "so sánh", "điểm khác", "điểm giống", "khác nhau",
                 "giống nhau", "rút ra", "liên hệ", "vận dụng", "điểm tương đồng"],
    "op_evaluate": ["bài học", "đánh giá", "bản chất", "tác động", "ảnh hưởng",
                    "ý nghĩa", "hệ quả", "vai trò"],
}
SUPERLATIVE = re.compile(r"\bnhất\b")
NEGATION = re.compile(r"không phải|không đúng|ngoại trừ|không thuộc|không nằm")
CONDITIONAL = re.compile(r"\bnếu\b|giả sử|trong trường hợp")


def norm(t: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", (t or "").lower()))


def op_features(stem: str) -> dict:
    s = norm(stem)
    f = {k: float(sum(s.count(c) for c in v)) for k, v in CUES.items()}
    f["op_superlative"] = float(len(SUPERLATIVE.findall(s)))
    f["op_negation"] = float(bool(NEGATION.search(s)))
    f["op_conditional"] = float(bool(CONDITIONAL.search(s)))
    f["op_n_clauses"] = float(s.count(",") + s.count(";"))
    f["op_n_words"] = float(len(s.split()))
    return f


OP_COLS = list(CUES) + ["op_superlative", "op_negation", "op_conditional",
                        "op_n_clauses", "op_n_words"]


# ---------------------------------------------------------------- trục thao tác B
def depth_features(stem_uris: set, ans_uris: set, hops: dict) -> dict:
    """Số bước CÂU DẪN → ĐÁP ÁN. Đề tài chưa từng tính đại lượng này."""
    ds = [hops.get(s, {}).get(a) for s in stem_uris for a in ans_uris]
    ds = [float(d) for d in ds if d is not None]
    new = ans_uris - stem_uris
    return {
        "depth_min": min(ds) if ds else np.nan,
        "depth_mean": float(np.mean(ds)) if ds else np.nan,
        "depth_max": max(ds) if ds else np.nan,
        "depth_n_stem_ent": float(len(stem_uris)),
        "depth_n_ans_ent": float(len(ans_uris)),
        "depth_n_new_ent": float(len(new)),
        "depth_frac_new": len(new) / max(1.0, float(len(ans_uris))),
        "depth_disconnected": float(not ds),
    }


DEPTH_COLS = ["depth_min", "depth_mean", "depth_max", "depth_n_stem_ent",
              "depth_n_ans_ent", "depth_n_new_ent", "depth_frac_new",
              "depth_disconnected"]

# trục tri thức: VỊ TRÍ trong đồ thị, không phải quan hệ đáp án↔nhiễu
KNOW_COLS = ["kg_centrality_mean", "kg_prereq_correct", "kg_prereq_distractor",
             "kg_entity_match_coverage", "kg_num_correct"]
# khối Vinu: quan hệ đáp án↔nhiễu (để đối chiếu)
VINU_COLS = ["kad_path_distance_mean", "jaccard_kg_max", "jaccard_kg_mean",
             "rsi_dc"]


def oof(X, y, seed):
    pred = np.zeros(len(y), dtype=int)
    prob_hi = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y):
        m = XGBClassifier(**MK, random_state=seed).fit(X.iloc[tr], y[tr])
        pred[te] = m.predict(X.iloc[te])
        pr, cls = m.predict_proba(X.iloc[te]), list(m.classes_)
        prob_hi[te] = sum(pr[:, cls.index(k)] for k in (2, 3) if k in cls)
    return pred, prob_hi


def build(subject, fz, hops):
    cfg = cv.SUBJECTS[subject]
    items = cv.load_items(subject)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    rows = []
    for q in items:
        base = fz(q["stem"], q["correct"], q["distractors"])
        su = {e.uri for e in fz.entities(q["stem"])}
        au = {e.uri for e in fz.entities(q["correct"])}
        rows.append({**base, **op_features(q["stem"]),
                     **depth_features(su, au, hops)})
    return items, y, pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out",
                    default="subjects/history/samples/two_axis_feasibility.json")
    args = ap.parse_args()

    eng = OntologyEngine.for_subject("history")
    fz = cv.Featurizer(eng, "verbosity")
    hops = cv.all_pairs_hops(eng)
    surf = cv.SURFACE_COLS["verbosity"]

    SETS = [
        ("bề mặt (hành văn)", surf),
        ("thao tác · ngôn ngữ", OP_COLS),
        ("thao tác · chiều sâu KG", DEPTH_COLS),
        ("TRỤC THAO TÁC (A+B)", OP_COLS + DEPTH_COLS),
        ("TRỤC TRI THỨC (vị trí)", KNOW_COLS),
        ("khối Vinu (đáp án↔nhiễu)", VINU_COLS),
        ("HAI TRỤC", OP_COLS + DEPTH_COLS + KNOW_COLS),
        ("HAI TRỤC + bề mặt", OP_COLS + DEPTH_COLS + KNOW_COLS + surf),
    ]

    print(f"ontology Sử {len(eng)} thực thể / {eng.nx_graph.number_of_edges()} cạnh")
    print(f"dụng cụ MỚI: {len(OP_COLS)} cột ngôn ngữ + {len(DEPTH_COLS)} cột "
          f"chiều sâu câu dẫn→đáp án\n")

    out = {}
    for sub in ("history_gv", "history"):
        cfg = cv.SUBJECTS[sub]
        items, y, X = build(sub, fz, hops)
        hi = (y >= 2).astype(int)
        print("=" * 86)
        print(f"{sub}  n={len(items)}  nhãn: {cfg['label_by']}")
        print(f"phân bố " + " ".join(f"{NAME[k]} {int((y == k).sum())}"
                                     for k in range(4)) +
              f"  · tầng cao {hi.sum()} ({hi.mean():.1%})")
        print("=" * 86)
        print(f"{'bộ đặc trưng':28s} {'#cột':>4s} {'QWK':>7s} {'mF1':>6s} "
              f"{'AUC cao':>8s} {'rec VD':>7s} {'rec VDC':>8s}")
        res = {}
        for nm, c in SETS:
            c = [x for x in c if x in X.columns]
            pred, ph = oof(X[c], y, args.seed)
            rec = recall_score(y, pred, average=None, labels=range(4),
                               zero_division=0)
            auc = roc_auc_score(hi, ph) if hi.sum() > 1 else np.nan
            q = cohen_kappa_score(y, pred, weights="quadratic")
            print(f"{nm:28s} {len(c):4d} {q:7.3f} "
                  f"{f1_score(y, pred, average='macro'):6.3f} {auc:8.3f} "
                  f"{rec[2]:7.1%} {rec[3]:8.1%}")
            res[nm] = {"n_cols": len(c), "qwk": float(q),
                       "macro_f1": float(f1_score(y, pred, average="macro")),
                       "auc_high": float(auc), "recall_vd": float(rec[2]),
                       "recall_vdc": float(rec[3])}
        out[sub] = res

        # hai trục có ĐỘC LẬP không? (lí thuyết đòi chúng trực giao)
        pk, _ = oof(X[[c for c in KNOW_COLS if c in X.columns]], y, args.seed)
        po, _ = oof(X[[c for c in OP_COLS + DEPTH_COLS if c in X.columns]], y,
                    args.seed)
        rho = spearmanr(pk, po)[0]
        print(f"\ntương quan giữa dự đoán TRỤC TRI THỨC và TRỤC THAO TÁC: "
              f"ρ = {rho:+.3f}")
        print("  (ρ thấp = hai trục thật sự đo hai thứ khác nhau ⇒ cộng vào có lợi)")
        out[sub]["axis_orthogonality"] = float(rho)

        # cột nào của dụng cụ MỚI thực sự mang tín hiệu
        print(f"\ncột MỚI mạnh nhất (Spearman với nhãn):")
        rr = []
        for c in OP_COLS + DEPTH_COLS:
            v = X[c].values.astype(float)
            m = ~np.isnan(v)
            if m.sum() < 50 or np.nanstd(v[m]) == 0:
                continue
            rr.append((abs(spearmanr(v[m], y[m])[0]), c,
                       spearmanr(v[m], y[m])[0]))
        for _, c, r in sorted(rr, reverse=True)[:8]:
            print(f"   {c:22s} ρ {r:+.3f}")
        out[sub]["top_new_cols"] = {c: float(r) for _, c, r in
                                    sorted(rr, reverse=True)[:8]}
        print()

    Path(args.out).write_text(json.dumps({"seed": args.seed, "results": out},
                                         ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(f"→ {args.out}")


if __name__ == "__main__":
    main()
