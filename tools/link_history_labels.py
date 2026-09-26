# -*- coding: utf-8 -*-
"""Ghép bộ Sử nhãn GIÁO VIÊN (kenhgiaovien) với bộ vietjack đã có.

Nguồn mới: `tools/crawl/crawl_kenhgiaovien.py --subject history` → 1.339 câu Sử
có nhãn NB/TH/VD/VDC **do giáo viên soạn theo ma trận đề** — nguồn nhãn PHI-LLM
đầu tiên có quy mô cho môn Sử (trước đó chỉ có 90 câu từ form của 1 giáo viên).

Trang nguồn KHÔNG có đáp án đúng (giống Lý). Công cụ này:
  1. khử trùng nội bộ theo câu dẫn chuẩn hoá  → dup_group / is_canonical
  2. ghép ĐÁP ÁN + nhãn `llm_vote3` từ `mcq_crawled.json` theo câu dẫn trùng
  3. báo cáo ghép cặp: nhãn GIÁO VIÊN vs nhãn LLM trên các câu chung

Idempotent: chạy lại nhiều lần cho cùng kết quả.

Chạy:  python tools/link_history_labels.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import cohen_kappa_score

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm_answer_key as ak  # noqa: E402  — dùng chung phép soi phương án

KGV = Path("subjects/history/samples/mcq_kenhgiaovien.json")
VJ = Path("subjects/history/samples/mcq_crawled.json")
LV = {"Nhận biết": 0, "Thông hiểu": 1, "Vận dụng": 2, "Vận dụng cao": 3}
NAME = ["NB", "TH", "VD", "VDC"]


def norm(t: str) -> str:
    t = unicodedata.normalize("NFC", (t or "").lower())
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t)).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="subjects/history/samples/kgv_link_report.json")
    args = ap.parse_args()

    new = json.loads(KGV.read_text(encoding="utf-8"))
    old = json.loads(VJ.read_text(encoding="utf-8"))
    print(f"kenhgiaovien (nhãn GIÁO VIÊN): {len(new)} câu")
    print(f"vietjack     (nhãn LLM)      : {len(old)} câu")

    # 1) khử trùng nội bộ — tất định theo câu dẫn đã chuẩn hoá
    groups = defaultdict(list)
    for q in new:
        groups[norm(q["stem"])].append(q)
    for gi, key in enumerate(sorted(groups)):
        for j, q in enumerate(groups[key]):
            q["dup_group"] = gi
            q["is_canonical"] = (j == 0)
    n_canon = sum(1 for q in new if q["is_canonical"])
    print(f"\n[1] khử trùng: {len(new)} → {len(groups)} nội dung khác nhau "
          f"({(len(new) - len(groups)) / len(new):.1%} trùng), canonical {n_canon}")

    # 2) ghép đáp án + nhãn LLM từ vietjack
    by_stem = {norm(q["stem"]): q for q in old}
    n_ans = n_skip = n_keep = 0
    for q in new:
        o = by_stem.get(norm(q["stem"]))
        q.setdefault("answer_from", None)
        q["llm_vote3_label"] = o.get("difficulty_vn") if o else None
        if not (o and o.get("correct")):
            continue
        if q.get("correct"):                      # đã có đáp án (kể cả LLM sinh)
            n_keep += 1
            continue
        # Câu dẫn trùng KHÔNG bảo đảm bộ phương án trùng: phải soi đáp án của
        # vietjack vào ĐÚNG bộ 4 phương án của kenhgiaovien — đó mới là đề mà
        # giáo viên đã gán nhãn. Không soi được thì bỏ, để LLM sinh sau.
        idx = ak.match_option(o["correct"], q["options"])
        if idx is None:
            n_skip += 1
            continue
        q["correct"] = q["options"][idx]
        q["distractors"] = [x for i, x in enumerate(q["options"]) if i != idx]
        q["answer_letter"] = "ABCD"[idx]
        q["answer_source"] = "vietjack"
        q["answer_from"] = o["id"]
        n_ans += 1
    tot = sum(1 for q in new if q.get("correct"))
    print(f"[2] ghép đáp án từ vietjack: +{n_ans} câu mới · giữ nguyên {n_keep} câu "
          f"đã có · bỏ {n_skip} câu phương án lệch")
    print(f"    tổng {tot}/{len(new)} câu có đáp án "
          f"({tot / len(new):.1%}) · còn {len(new) - tot} câu CHƯA CÓ ĐÁP ÁN")
    KGV.write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")

    # 3) ghép cặp nhãn
    pair = [q for q in new
            if q["is_canonical"] and q.get("llm_vote3_label") in LV
            and q["difficulty_vn"] in LV]
    yh = np.array([LV[q["difficulty_vn"]] for q in pair])
    yl = np.array([LV[q["llm_vote3_label"]] for q in pair])
    kap = cohen_kappa_score(yh, yl)
    qwk = cohen_kappa_score(yh, yl, weights="quadratic")
    print(f"\n[3] GHÉP CẶP nhãn GIÁO VIÊN vs nhãn LLM — n = {len(pair)}")
    print(f"    đồng thuận {np.mean(yh == yl):.1%} | κ {kap:+.3f} | QWK {qwk:+.3f}")
    M = np.zeros((4, 4), int)
    for a, b in zip(yh, yl):
        M[a, b] += 1
    print("    ma trận (hàng GIÁO VIÊN, cột LLM):   " +
          "  ".join(f"{n:>4s}" for n in NAME))
    for r, n in zip(M, NAME):
        print(f"      GV {n:4s}                        " +
              "  ".join(f"{v:4d}" for v in r))
    hi = M[2:].sum()
    hi_ok = M[2:, 2:].sum()
    print(f"\n    ⚠️ Câu giáo viên gán VD/VDC: {hi} · LLM cũng gán VD/VDC: "
          f"{hi_ok} ({hi_ok / max(1, hi):.1%})")
    print(f"       trong đó bị LLM hạ xuống NB: {M[2:, 0].sum()}")
    print("       ⇒ κ vừa phải nhưng QWK ≈ 0 vì bất đồng dồn vào tầng CAO.")

    dist_h = Counter(q["difficulty_vn"] for q in new if q["is_canonical"])
    print(f"\nphân bố nhãn GIÁO VIÊN (canonical): " +
          " ".join(f"{k} {v}" for k, v in dist_h.items()))

    Path(args.out).write_text(json.dumps({
        "n_kgv": len(new), "n_unique": len(groups), "n_canonical": n_canon,
        "n_with_answer": tot, "n_paired": len(pair),
        "agreement": {"absolute": float(np.mean(yh == yl)), "kappa": float(kap),
                      "qwk": float(qwk), "confusion_teacher_rows": M.tolist()},
        "high_tier": {"teacher_vd_vdc": int(hi), "llm_agrees": int(hi_ok),
                      "llm_calls_nb": int(M[2:, 0].sum())},
        "teacher_label_dist": dict(dist_h),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {args.out}")
    if len(new) - tot:
        print("")
        print(f"⚠️ {len(new) - tot} câu chưa có đáp án. Sinh bằng:")
        print("   python tools/llm_answer_key.py --subject history --validate "
              "--api-key sk-...   # đo trước")
        print("   python tools/llm_answer_key.py --subject history "
              "--api-key sk-...              # rồi sinh")


if __name__ == "__main__":
    main()
