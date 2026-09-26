# -*- coding: utf-8 -*-
"""Quy kết mất trung thực khi khối KHÔNG ĐẶT TÊN ĐƯỢC phình ra — bốn mô hình nền.

Cùng một bộ tiêu chí tiền đăng ký, cùng bộ phản thực, cùng hàm `certificate()`,
chạy trên bốn mô hình nền xếp theo **tỉ trọng quyết định nằm ngoài cột đặt tên
được**:

    xgb15   XGBoost, 15 cột luật tay                        ~0 %
    tfidf   TF-IDF từ + ký tự + 15 cột đó                   ~50 %
    text    PhoBERT đóng băng + 15 cột đó                   ~78 % / 88 %
    emb     PhoBERT đóng băng, KHÔNG cột luật tay           100 %  (ca giới hạn)

Hai điểm thì nối đường nào cũng được; bốn điểm thì mới nói được là có xu hướng.
`emb` là **ca giới hạn**: không còn cột đặt tên được nào nên quy kết bằng 0 ở
mọi câu, và câu hỏi "quy kết có dự báo được can thiệp không" thôi đặt ra được —
đó là None trong bảng, KHÔNG phải 0.

Chạy:  python tools/backend_curve.py          # bảng
       python tools/backend_curve.py --md     # dán thẳng vào tài liệu
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "docs" / "backend_curve.json"

BACKENDS = [("xgb15", "", "XGBoost · 15 cột luật tay"),
            ("tfidf", "_tf", "TF-IDF · + 15 cột"),
            ("text", "_pb", "PhoBERT · + 15 cột"),
            ("emb", "_eo", "PhoBERT · KHÔNG cột luật tay")]
SUBJECTS = [("physics", "Lý", "subjects/physics/samples",
             "counterfactual_validity", "xai_validate",
             "xai_selective", "xai_recourse"),
            ("history_gv", "Sử", "subjects/history/samples",
             "counterfactual_validity_gv", "xai_validate_gv",
             "xai_selective_gv", "xai_recourse_gv")]


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def opaque_share(cf) -> float | None:
    """Phần |quy kết| nằm ở khối văn bản — 0 khi mô hình không có khối đó."""
    at = (cf or {}).get("arms", {}).get("attribution")
    if not at:
        return None
    tot = at.get("surface", 0) + at.get("kg", 0) + at.get("text", 0)
    return (at.get("text", 0) / tot) if tot else None


def row(subject, dirname, cf_name, val_name, sel_name, rec_name,
        suffix) -> dict | None:
    cf = load(REPO / dirname / f"{cf_name}{suffix}.json")
    val = load(REPO / dirname / f"{val_name}{suffix}.json")
    if cf is None and val is None:
        return None
    r = {"opaque_share": opaque_share(cf)}
    for k in ("rho_split_half", "reliability_full_spearman_brown", "ceiling_sqrt",
              "rho_shap_vs_intervention", "frac_ceiling_shap",
              "rho_groupshap_vs_intervention", "frac_ceiling_groupshap"):
        r[k] = (val or {}).get(k)
    r["attribution_undefined"] = (val or {}).get("attribution_undefined", [])
    san = load(REPO / "docs" / f"xai_sanity{suffix}.json")
    if san and subject in san:
        s = san[subject]
        r["gate_iut"] = s["real"]["iut"]
        r["robust_arms"] = s["robust_arms"]
        r["false_cert_iut"] = s["false_cert"]["iut"]
    nat = load(REPO / "docs" / f"natural_raters{suffix}.json")
    if nat and subject in nat:
        n = nat[subject]
        r["dup_machine_human"] = n["qwk_machine_human"]
        r["dup_human_human"] = n["qwk_human_human"]
        r["grouped_qwk"] = n["model_grouped_qwk_all_items"]
    sel = load(REPO / dirname / f"{sel_name}{suffix}.json")
    if sel:
        cur = sel.get("curve", {})
        # @20 %: phần tử cuối của đường cong độ phủ ↔ độ chính xác
        for key, tag in (("entropy (đối chứng)", "sel20_entropy"),
                         ("sức giải thích", "sel20_strength")):
            v = cur.get(key)
            if v:
                r[tag] = v[-1]
        r["rho_strength_entropy"] = sel.get("mechanism", {}).get(
            "rho_strength_entropy")
    rec = load(REPO / dirname / f"{rec_name}{suffix}.json")
    if rec:
        r["recourse_down"] = rec.get("editable_down")
        r["recourse_up"] = rec.get("editable_up")
    return r


def collect() -> dict:
    res = {}
    for subject, _lbl, d, cfn, vn, sn, rn in SUBJECTS:
        for name, suf, _desc in BACKENDS:
            r = row(subject, d, cfn, vn, sn, rn, suf)
            if r is not None:
                res.setdefault(subject, {})[name] = r
    return res


def fmt(v, pct=False, signed=False):
    if v is None:
        return "—"
    if isinstance(v, list):
        return ", ".join(v) if v else "—"
    if pct:
        return f"{v:.1%}"
    return f"{v:+.3f}" if signed else f"{v:.3f}"


ROWS = [("khối không đặt tên được", "opaque_share", True, False),
        ("máy–người trên câu trùng", "dup_machine_human", False, False),
        ("QWK chia lát theo cụm", "grouped_qwk", False, False),
        ("can thiệp: nửa A → nửa B", "rho_split_half", False, True),
        ("QUY KẾT: SHAP → nửa B", "rho_shap_vs_intervention", False, True),
        ("QUY KẾT: % trần", "frac_ceiling_shap", True, False),
        ("QUY KẾT: Shapley khối → B", "rho_groupshap_vs_intervention", False, True),
        ("cổng B1: trục qua luật CHẶT", "gate_iut", False, False),
        ("cổng B1: nhánh vững mọi seed", "robust_arms", False, False),
        ("từ chối @20% · entropy", "sel20_entropy", True, False),
        ("từ chối @20% · sức giải thích", "sel20_strength", True, False),
        ("rho(sức giải thích, entropy)", "rho_strength_entropy", False, True),
        ("lời khuyên hạ mức", "recourse_down", True, False),
        ("lời khuyên nâng mức", "recourse_up", True, False)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true")
    a = ap.parse_args()
    res = collect()
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    for subject, lbl, *_ in SUBJECTS:
        got = res.get(subject, {})
        names = [n for n, _s, _d in BACKENDS if n in got]
        if not names:
            continue
        head = [d for n, _s, d in BACKENDS if n in names]
        print(f"\n===== {lbl} =====")
        if a.md:
            print("| | " + " | ".join(head) + " |")
            print("|---|" + "---:|" * len(names))
        else:
            print(f"{'':30s} " + " ".join(f"{n:>10s}" for n in names))
        for label, key, pct, signed in ROWS:
            cells = [fmt(got[n].get(key), pct, signed) for n in names]
            if a.md:
                print(f"| {label} | " + " | ".join(cells) + " |")
            else:
                print(f"{label:30s} " + " ".join(f"{c:>10s}" for c in cells))
        und = [n for n in names if got[n].get("attribution_undefined")]
        if und:
            print(f"  (quy kết không định nghĩa được ở: {', '.join(und)} — "
                  f"mô hình nền không dùng cột luật tay nào)")
    print(f"\n→ {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
