# -*- coding: utf-8 -*-
"""TRỤC THAO TÁC có đo được không — và vì sao môn tự nhiên khác môn xã hội.

`tools/two_axis_feasibility.py` cho thấy trên môn Sử, chiều sâu suy luận đo trên
đồ thị tri thức = AUC 0,495, tức đúng bằng tung đồng xu, kể cả khi chỉ xét phần
đồ thị nối được. Câu hỏi tiếp: **ý tưởng sai, hay đồ thị Sử không mang thông tin
đó?**

Đếm cạnh cho câu trả lời:

    Sử  (su9.ttl)   occursAt · occursDuring · hasContent · hasOrganization …
                    cạnh TIÊN QUYẾT: 0
    Lý  (phys9.ttl) prerequisiteOf: 216 · relatesQuantities: 32
                    kèm applicationSteps (28) · symbolicDensity (17) · bloomLevel (71)

Cạnh Sử mã hoá "cái gì liên quan cái gì" — khoảng cách trên đó là độ gần chủ đề
trong bách khoa, không phải số bước học sinh phải làm. Cạnh `prerequisiteOf` của
Lý mã hoá "phải biết Y trước mới tới được X" — ĐÚNG ngữ nghĩa cần cho trục thao
tác. Nên phép này dựng dụng cụ đo trục thao tác cho Lý và kiểm trên nhãn giáo
viên (1.539 câu, VD+VDC chiếm 38% — cân hơn hẳn Sử 13%).

Hai nhóm dụng cụ:

  A. TỪ ONTOLOGY — chỉ dùng cạnh `prerequisiteOf` (KHÔNG dùng cạnh chủ đề):
     khoảng cách câu dẫn → đáp án trên đồ thị tiên quyết, độ sâu tiên quyết,
     số tiên quyết mà đáp án đòi thêm ngoài câu dẫn, applicationSteps /
     symbolicDensity của công thức chạm tới, bloomLevel của thực thể.

  B. TỪ VĂN BẢN — dấu vết của phép tính: có mấy số, mấy đơn vị, có hỏi "tính /
     bao nhiêu / xác định" không, có kí hiệu công thức không.

So với: khối bề mặt hiện tại, khối KG hiện tại (đáp án↔nhiễu, tức Vinu).

Chạy:  python tools/operation_axis.py [--seed 42]
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import rdflib
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

NUM_RE = re.compile(r"\d+[.,]?\d*")
UNIT_RE = re.compile(r"\b(v|a|w|j|kw|kwh|ω|ohm|m|cm|mm|km|s|h|n|kg|g|hz|"
                     r"vôn|ampe|oát|jun|ôm|mét|giây|niutơn)\b")
COMPUTE_RE = re.compile(r"\btính\b|bao nhiêu|xác định|\bbằng\b.*\?|giá trị của")
SYMBOL_RE = re.compile(r"[=/×÷]|\b[UIRPQFmvts]\s*=|\b[UIRPQ]\d\b")


def norm(t):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", (t or "").lower()))


# ------------------------------------------------------------------ ontology
def load_ttl(subject):
    """Đọc thẳng .ttl để lấy các chú giải mà OntologyEngine chưa nạp."""
    f = glob.glob(f"subjects/{subject}/ontology/*.ttl")[0]
    g = rdflib.Graph()
    g.parse(f, format="turtle")
    ns = {"physics": "http://edu.vn/phys9/ontology#",
          "history": "http://edu.vn/su9/ontology#"}[subject]
    P = rdflib.Namespace(ns)

    def ints(prop):
        return {str(s): int(o) for s, o in g.subject_objects(P[prop])}

    pre = nx.DiGraph()
    for s, o in g.subject_objects(P.prerequisiteOf):
        pre.add_edge(str(s), str(o))          # s phải biết TRƯỚC o
    relq = collections.defaultdict(set)
    for s, o in g.subject_objects(P.relatesQuantities):
        relq[str(o)].add(str(s))              # quantity → các công thức dùng nó
    steps_by_code = {str(k).split("#")[-1]: v
                     for k, v in ints("applicationSteps").items()}
    return {"prereq": pre, "steps": ints("applicationSteps"),
            "steps_by_code": steps_by_code,
            "symd": ints("symbolicDensity"), "bloom": ints("bloomLevel"),
            "relq": relq, "n_prereq_edges": pre.number_of_edges()}


def op_ontology(stem_uris, ans_uris, O, undirected_pre, sp):
    """Trục thao tác từ ontology — CHỈ dùng cạnh tiên quyết, không dùng cạnh chủ đề."""
    pre = O["prereq"]
    # khoảng cách câu dẫn → đáp án TRÊN ĐỒ THỊ TIÊN QUYẾT
    d_dir, d_und = [], []
    for s in stem_uris:
        for a in ans_uris:
            if s in sp and a in sp[s]:
                d_dir.append(sp[s][a])
            if s in undirected_pre and a in undirected_pre[s]:
                d_und.append(undirected_pre[s][a])
    # công thức chạm tới, qua chính thực thể hoặc qua đại lượng nó liên hệ
    forms = set()
    for u in stem_uris | ans_uris:
        forms |= O["relq"].get(u, set())
        if u in O["steps"]:
            forms.add(u)
    steps = [O["steps"][f] for f in forms if f in O["steps"]]
    symd = [O["symd"][f] for f in forms if f in O["symd"]]
    bloom = [O["bloom"][u] for u in (stem_uris | ans_uris) if u in O["bloom"]]
    # tiên quyết mà ĐÁP ÁN đòi thêm, ngoài những gì câu dẫn đã cho
    need = set()
    for a in ans_uris:
        need |= set(pre.predecessors(a)) if a in pre else set()
    return {
        "op_pre_dist_dir": float(min(d_dir)) if d_dir else np.nan,
        "op_pre_dist_und": float(min(d_und)) if d_und else np.nan,
        "op_pre_reachable": float(bool(d_und)),
        "op_pre_depth_ans": float(max((len(nx.ancestors(pre, a)) for a in ans_uris
                                       if a in pre), default=0)),
        "op_pre_need_new": float(len(need - stem_uris)),
        "op_steps_max": float(max(steps)) if steps else np.nan,
        "op_steps_sum": float(sum(steps)) if steps else np.nan,
        "op_n_formula": float(len(forms)),
        "op_symd_max": float(max(symd)) if symd else np.nan,
        "op_bloom_max": float(max(bloom)) if bloom else np.nan,
        "op_bloom_mean": float(np.mean(bloom)) if bloom else np.nan,
    }


def op_text(stem, correct, distractors):
    s = norm(stem)
    opts = [correct] + list(distractors)
    return {
        "opt_n_numbers": float(len(NUM_RE.findall(s))),
        "opt_n_units": float(len(UNIT_RE.findall(s))),
        "opt_asks_compute": float(bool(COMPUTE_RE.search(s))),
        "opt_has_symbol": float(bool(SYMBOL_RE.search(stem))),
        "opt_num_in_options": float(sum(1 for o in opts if NUM_RE.search(o))),
        "opt_n_words": float(len(s.split())),
    }


OP_ONT = ["op_pre_dist_dir", "op_pre_dist_und", "op_pre_reachable",
          "op_pre_depth_ans", "op_pre_need_new", "op_steps_max", "op_steps_sum",
          "op_n_formula", "op_symd_max", "op_bloom_max", "op_bloom_mean"]
OP_TXT = ["opt_n_numbers", "opt_n_units", "opt_asks_compute", "opt_has_symbol",
          "opt_num_in_options", "opt_n_words"]


# ------------------------------------------------------- vết giải do LLM sinh
TRACE_PATH = {"physics": "subjects/physics/samples/solution_traces.json"}
TRACE_COLS = ["tr_steps", "tr_n_formula", "tr_given", "tr_unknowns",
              "tr_op_type", "tr_is_compute", "tr_ont_steps_sum",
              "tr_ont_steps_max"]
OP_TYPE = {"nho": 0.0, "hieu": 1.0, "tinh": 2.0, "phantich": 3.0}


def load_traces(subject):
    p = TRACE_PATH.get(cv.ontology_of(subject))
    if not p or not Path(p).exists():
        return {}
    return json.loads(Path(p).read_text(encoding="utf-8"))


def trace_features(qid, traces, ont_steps):
    """Đặc trưng từ tiến trình giải.

    `tr_ont_steps_*` là chỗ ontology thực sự trả công: LLM LIÊN KẾT được công
    thức (khớp chuỗi chỉ làm được 1/1539 câu), rồi `applicationSteps` do NGƯỜI
    soạn trong .ttl mới cấp con số. Không có bước liên kết thì cột này nằm chết.
    """
    t = traces.get(qid)
    if not t:
        return {c: np.nan for c in TRACE_COLS}
    st = [ont_steps[f] for f in t["formulas"] if f in ont_steps]
    return {
        "tr_steps": float(t["steps"]),
        "tr_n_formula": float(len(t["formulas"])),
        "tr_given": float(t["given"]),
        "tr_unknowns": float(t["unknowns"]),
        "tr_op_type": OP_TYPE.get(t["op_type"], np.nan),
        "tr_is_compute": float(t["op_type"] in ("tinh", "phantich")),
        "tr_ont_steps_sum": float(sum(st)) if st else 0.0,
        "tr_ont_steps_max": float(max(st)) if st else 0.0,
    }


def oof(X, y, seed):
    pred = np.zeros(len(y), int)
    ph = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y):
        m = XGBClassifier(**MK, random_state=seed).fit(X.iloc[tr], y[tr])
        pred[te] = m.predict(X.iloc[te])
        pr, cl = m.predict_proba(X.iloc[te]), list(m.classes_)
        ph[te] = sum(pr[:, cl.index(k)] for k in (2, 3) if k in cl)
    return pred, ph


def run(subject, seed):
    cfg = cv.SUBJECTS[subject]
    ont = cv.ontology_of(subject)
    O = load_ttl(ont)
    eng = OntologyEngine.for_subject(ont)
    fz = cv.Featurizer(eng, cfg["surface"])
    items = cv.load_items(subject)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    hi = (y >= 2).astype(int)

    pre = O["prereq"]
    und = pre.to_undirected()
    sp = dict(nx.all_pairs_shortest_path_length(pre))
    spu = dict(nx.all_pairs_shortest_path_length(und))

    traces = load_traces(subject)
    ont_steps = {f["code"]: f["steps"] for f in
                 [{"code": k, "steps": v} for k, v in O["steps_by_code"].items()]}
    rows = []
    for q in items:
        su = {e.uri for e in fz.entities(q["stem"])}
        au = {e.uri for e in fz.entities(q["correct"])}
        rows.append({**fz(q["stem"], q["correct"], q["distractors"]),
                     **op_ontology(su, au, O, spu, sp),
                     **op_text(q["stem"], q["correct"], q["distractors"]),
                     **trace_features(q["id"], traces, ont_steps)})
    X = pd.DataFrame(rows)

    print("=" * 88)
    print(f"{subject}  n={len(items)}  nhãn: {cfg.get('label_by')}")
    print(f"đồ thị TIÊN QUYẾT: {pre.number_of_nodes()} nút, "
          f"{O['n_prereq_edges']} cạnh · applicationSteps {len(O['steps'])} · "
          f"bloomLevel {len(O['bloom'])}")
    print("phân bố " + " ".join(f"{NAME[k]} {int((y == k).sum())}" for k in range(4))
          + f" · tầng cao {hi.sum()} ({hi.mean():.1%})")
    cov = float(np.mean(X.op_pre_reachable > 0))
    print(f"phủ: {cov:.1%} câu nối được câu dẫn→đáp án TRÊN ĐỒ THỊ TIÊN QUYẾT")
    print("=" * 88)

    surf = cv.SURFACE_COLS[cfg["surface"]]
    NOLEN = [c for c in OP_TXT if c != "opt_n_words"]
    SETS = [("bề mặt (hiện tại)", surf),
            ("KG hiện tại (đáp án↔nhiễu)", cv.KG_COLS),
            ("chỉ độ dài câu dẫn", ["opt_n_words"]),
            ("thao tác · ontology", OP_ONT),
            ("thao tác · văn bản", OP_TXT),
            ("VẾT GIẢI LLM", TRACE_COLS),
            ("vết giải + ontology (0 văn bản)", TRACE_COLS + OP_ONT),
            ("thao tác + vết giải", OP_ONT + OP_TXT + TRACE_COLS),
            ("vết giải + KG, BỎ độ dài", TRACE_COLS + cv.KG_COLS + OP_ONT + NOLEN),
            ("tất cả", surf + cv.KG_COLS + OP_ONT + OP_TXT + TRACE_COLS)]
    print(f"{'bộ đặc trưng':30s} {'#cột':>4s} {'QWK':>7s} {'mF1':>6s} "
          f"{'AUC cao':>8s} {'rec VD':>7s} {'rec VDC':>8s}")
    res = {}
    for nm, c in SETS:
        c = [x for x in c if x in X.columns]
        pred, ph = oof(X[c], y, seed)
        rec = recall_score(y, pred, average=None, labels=range(4), zero_division=0)
        q = cohen_kappa_score(y, pred, weights="quadratic")
        auc = roc_auc_score(hi, ph)
        print(f"{nm:30s} {len(c):4d} {q:7.3f} "
              f"{f1_score(y, pred, average='macro'):6.3f} {auc:8.3f} "
              f"{rec[2]:7.1%} {rec[3]:8.1%}")
        res[nm] = {"n_cols": len(c), "qwk": float(q), "auc_high": float(auc),
                   "macro_f1": float(f1_score(y, pred, average="macro")),
                   "recall_vd": float(rec[2]), "recall_vdc": float(rec[3])}

    print(f"\ncột thao tác mạnh nhất (Spearman với nhãn giáo viên):")
    rr = []
    for c in OP_ONT + OP_TXT + TRACE_COLS:
        v = X[c].values.astype(float)
        m = ~np.isnan(v)
        if m.sum() < 50 or np.nanstd(v[m]) == 0:
            continue
        r, p = spearmanr(v[m], y[m])
        rr.append((abs(r), c, r, p, int(m.sum())))
    for _, c, r, p, n in sorted(rr, reverse=True)[:10]:
        print(f"   {c:20s} ρ {r:+.3f} (p={p:.4f}, n={n})")
    res["top_cols"] = {c: {"rho": float(r), "p": float(p), "n": n}
                       for _, c, r, p, n in sorted(rr, reverse=True)[:10]}
    res["prereq_coverage"] = cov
    res["n_prereq_edges"] = O["n_prereq_edges"]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="both",
                    choices=["physics", "history_gv", "both"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="subjects/physics/samples/operation_axis.json")
    args = ap.parse_args()
    subs = ["physics", "history_gv"] if args.subject == "both" else [args.subject]
    out = {}
    for s in subs:
        out[s] = run(s, args.seed)
        print()
    Path(args.out).write_text(json.dumps({"seed": args.seed, "results": out},
                                         ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(f"→ {args.out}")


if __name__ == "__main__":
    main()
