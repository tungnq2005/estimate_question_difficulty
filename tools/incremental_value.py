# -*- coding: utf-8 -*-
"""Phản biện cuối: "vậy sao không hỏi thẳng LLM cho xong?"

Đây là câu hỏi mà bất kỳ người phản biện nào cũng hỏi trước tiên, và cho tới giờ
đề tài chưa trả lời được bằng số. Trả lời nó cần đúng một thứ: **nhãn LLM và
nhãn giáo viên trên CÙNG những câu**, ở cả hai môn — nay đã có
(`tools/llm_judge_labels.py`).

Ba phép, và cả ba đều lấy nhãn GIÁO VIÊN làm chân lý:

1. GIÁ TRỊ GIA TĂNG — mô hình lồng nhau.
   (a) chỉ nhãn LLM · (b) chỉ đặc trưng SẠCH của ta · (c) cả hai.
   Nếu (c) > (a) có ý nghĩa ⇒ đặc trưng của ta mang thông tin mà LLM KHÔNG có.
   Nếu (c) ≈ (a) ⇒ cả pipeline chỉ là cách đắt tiền để tái tạo phán đoán LLM.

2. DỰ ĐOÁN LỖI CỦA LLM — nhất là lỗi nguy hiểm: LLM nói tầng thấp mà giáo viên
   nói tầng cao. Nếu đặc trưng của ta báo trước được lỗi đó, ta có một sản phẩm
   dùng được ngay: *cờ "câu này LLM có thể chấm hụt, xem lại"*.

3. ĐIỂM VẬN HÀNH — thứ giáo viên thật sự dùng: đưa một danh sách ngắn các câu
   NGHI LÀ tầng cao. Đo precision@k, so với danh sách mà LLM đưa.

"SẠCH" nghĩa là: KHÔNG cột độ dài văn bản (đã chứng minh là đặc tính người gán
nhãn, `tools/label_source_axes.py`) và KHÔNG cột `tr_op_type` (đã đo: một mình
nó đạt QWK 0,492, tức là nhãn độ khó LLM trá hình).

Chạy:  python tools/incremental_value.py [--subject both] [--boot 2000]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
import operation_axis as oa  # noqa: E402
import two_axis_feasibility as tf  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

NAME = ["NB", "TH", "VD", "VDC"]
LV = {"NB": 0, "TH": 1, "VD": 2, "VDC": 3}
MK = dict(n_estimators=200, max_depth=4, learning_rate=0.1, subsample=0.8,
          colsample_bytree=0.8, eval_metric="mlogloss", verbosity=0)
TRACE_PROC = ["tr_steps", "tr_n_formula", "tr_given", "tr_unknowns",
              "tr_ont_steps_sum", "tr_ont_steps_max"]
LEN_COLS = {"opt_n_words", "op_n_words", "op_n_clauses", "len_correct",
            "len_stem", "len_dist_mean", "len_ratio"}


def oof(X, y, seed, binary=False):
    pred = np.zeros(len(y), int)
    score = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y):
        m = XGBClassifier(**MK, random_state=seed).fit(X.iloc[tr], y[tr])
        pred[te] = m.predict(X.iloc[te])
        pr, cl = m.predict_proba(X.iloc[te]), list(m.classes_)
        score[te] = (pr[:, cl.index(1)] if binary and 1 in cl
                     else sum(pr[:, cl.index(k)] for k in (2, 3) if k in cl))
    return pred, score


def featurize(subject):
    """Mọi khối đặc trưng đã dựng, gộp một chỗ."""
    cfg = cv.SUBJECTS[subject]
    ont = cv.ontology_of(subject)
    eng = OntologyEngine.for_subject(ont)
    fz = cv.Featurizer(eng, cfg["surface"])
    items = cv.load_items(subject)
    O = oa.load_ttl(ont)
    pre = O["prereq"]
    sp = dict(nx.all_pairs_shortest_path_length(pre))
    spu = dict(nx.all_pairs_shortest_path_length(pre.to_undirected()))
    hops = cv.all_pairs_hops(eng)
    traces = oa.load_traces(subject)
    rows = []
    for q in items:
        su = {e.uri for e in fz.entities(q["stem"])}
        au = {e.uri for e in fz.entities(q["correct"])}
        rows.append({**fz(q["stem"], q["correct"], q["distractors"]),
                     **oa.op_ontology(su, au, O, spu, sp),
                     **oa.op_text(q["stem"], q["correct"], q["distractors"]),
                     **oa.trace_features(q["id"], traces, O["steps_by_code"]),
                     **tf.op_features(q["stem"]),
                     **tf.depth_features(su, au, hops)})
    X = pd.DataFrame(rows)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    return items, X, y, cfg


def clean_cols(X, subject):
    """Đặc trưng SẠCH: bỏ cột độ dài và bỏ cột phán đoán độ khó của LLM."""
    drop = LEN_COLS | {"tr_op_type", "tr_is_compute"}
    cols = [c for c in X.columns if c not in drop]
    if not oa.load_traces(subject):        # môn không có vết giải
        cols = [c for c in cols if not c.startswith("tr_")]
    return [c for c in cols if X[c].notna().any() and X[c].std(skipna=True) > 0]


def llm_labels(subject, items):
    ont = cv.ontology_of(subject)
    p = Path(f"subjects/{ont}/samples/llm_judge_{subject}.json")
    if p.exists():
        m = json.loads(p.read_text(encoding="utf-8"))
    elif subject == "physics":
        m = {q["id"]: q["llm_level"] for q in json.loads(Path(
            "subjects/physics/samples/mcq_kenhgiaovien_llmjudge.json"
        ).read_text(encoding="utf-8")) if q.get("llm_level")}
    else:
        m = {}
    return np.array([LV.get(m.get(q["id"]), -1) for q in items])


def boot(rng, n, reps):
    for _ in range(reps):
        yield rng.integers(0, n, n)


def ci(v, a=2.5, b=97.5):
    v = np.asarray([x for x in v if np.isfinite(x)])
    return (float(np.percentile(v, a)), float(np.percentile(v, b))) if len(v) else (np.nan,) * 2


def run(subject, seed, reps, rng):
    items, X, y, cfg = featurize(subject)
    yl = llm_labels(subject, items)
    m = yl >= 0
    if m.sum() < 100:
        print(f"[{subject}] chưa đủ nhãn LLM ({int(m.sum())}) — bỏ qua")
        return None
    items = [q for q, k in zip(items, m) if k]
    X, y, yl = X[m].reset_index(drop=True), y[m], yl[m]
    hi = (y >= 2).astype(int)
    cols = clean_cols(X, subject)

    print("=" * 84)
    print(f"{subject}  n={len(y)}  nhãn thật: GIÁO VIÊN  ·  đối thủ: LLM chấm mù")
    print(f"đặc trưng SẠCH: {len(cols)} cột (đã bỏ mọi cột độ dài và tr_op_type)")
    print("GV : " + " ".join(f"{NAME[k]} {int((y == k).sum())}" for k in range(4))
          + f" · tầng cao {hi.sum()} ({hi.mean():.1%})")
    print("LLM: " + " ".join(f"{NAME[k]} {int((yl == k).sum())}" for k in range(4)))
    print("=" * 84)

    # ---------------------------------------------------------------- phép 1
    print("\n1) GIÁ TRỊ GIA TĂNG — mô hình lồng nhau, chân lý = nhãn giáo viên")
    Xl = pd.DataFrame({"llm_level": yl.astype(float)})
    SETS = [("(a) chỉ nhãn LLM", Xl),
            ("(b) chỉ đặc trưng SẠCH", X[cols]),
            ("(c) nhãn LLM + SẠCH", pd.concat([Xl, X[cols]], axis=1))]
    got = {}
    print(f"{'mô hình':26s} {'#':>3s} {'QWK':>7s} {'AUC cao':>8s} "
          f"{'recVD':>7s} {'recVDC':>7s}")
    for nm, XX in SETS:
        pred, sc = oof(XX, y, seed)
        rec = recall_score(y, pred, average=None, labels=range(4), zero_division=0)
        q = cohen_kappa_score(y, pred, weights="quadratic")
        a = roc_auc_score(hi, sc)
        got[nm] = {"pred": pred, "score": sc, "qwk": q, "auc": a}
        print(f"{nm:26s} {XX.shape[1]:3d} {q:7.3f} {a:8.3f} {rec[2]:7.1%} {rec[3]:7.1%}")

    res1 = {}
    for lo, hiK in (("(a) chỉ nhãn LLM", "(c) nhãn LLM + SẠCH"),
                    ("(b) chỉ đặc trưng SẠCH", "(c) nhãn LLM + SẠCH")):
        dq, da = [], []
        for i in boot(rng, len(y), reps):
            if len(set(hi[i])) < 2:
                continue
            dq.append(cohen_kappa_score(y[i], got[hiK]["pred"][i], weights="quadratic")
                      - cohen_kappa_score(y[i], got[lo]["pred"][i], weights="quadratic"))
            da.append(roc_auc_score(hi[i], got[hiK]["score"][i])
                      - roc_auc_score(hi[i], got[lo]["score"][i]))
        dq, da = np.array(dq), np.array(da)
        pq = 2 * min((dq <= 0).mean(), (dq >= 0).mean())
        pa = 2 * min((da <= 0).mean(), (da >= 0).mean())
        tag = "SẠCH thêm được gì cho LLM" if "(a)" in lo else "LLM thêm được gì cho SẠCH"
        print(f"  {tag:30s} ΔQWK {dq.mean():+.3f} [{ci(dq)[0]:+.3f},{ci(dq)[1]:+.3f}] "
              f"p={pq:.3f} · ΔAUC {da.mean():+.3f} "
              f"[{ci(da)[0]:+.3f},{ci(da)[1]:+.3f}] p={pa:.3f}")
        res1[tag] = {"d_qwk": float(dq.mean()), "ci_qwk": list(ci(dq)), "p_qwk": float(pq),
                     "d_auc": float(da.mean()), "ci_auc": list(ci(da)), "p_auc": float(pa)}

    # ---------------------------------------------------------------- phép 2
    print("\n2) DỰ ĐOÁN LỖI CỦA LLM — đặc trưng của ta có báo trước được không?")
    res2 = {}
    for nm, tgt in (("LLM sai (khác nhãn GV)", (yl != y).astype(int)),
                    ("LLM CHẤM HỤT (nói thấp, GV nói cao)",
                     ((yl < 2) & (y >= 2)).astype(int))):
        if tgt.sum() < 30:
            continue
        _, sc = oof(X[cols], tgt, seed, binary=True)
        auc = roc_auc_score(tgt, sc)
        bs = np.array([roc_auc_score(tgt[i], sc[i]) for i in boot(rng, len(y), reps)
                       if len(set(tgt[i])) > 1])
        print(f"  {nm:38s} n={int(tgt.sum()):4d} ({tgt.mean():5.1%})  "
              f"AUC {auc:.3f} [{ci(bs)[0]:.3f},{ci(bs)[1]:.3f}]")
        res2[nm] = {"n": int(tgt.sum()), "rate": float(tgt.mean()),
                    "auc": float(auc), "ci": list(ci(bs))}
    print("  (AUC > 0,60 = có thể gắn cờ 'câu này LLM dễ chấm hụt, xem lại')")

    # ---------------------------------------------------------------- phép 3
    print("\n3) ĐIỂM VẬN HÀNH — danh sách ngắn câu NGHI tầng cao, giáo viên rà tay")
    order_p = np.argsort(-got["(b) chỉ đặc trưng SẠCH"]["score"])
    order_c = np.argsort(-got["(c) nhãn LLM + SẠCH"]["score"])
    order_l = np.argsort(-(yl + rng.random(len(yl)) * 1e-6))   # phá hoà bằng ngẫu nhiên
    res3 = {}
    print(f"{'k':>5s} {'chỉ LLM':>10s} {'SẠCH':>10s} {'LLM+SẠCH':>10s}   "
          f"(precision — tỉ lệ đúng là VD/VDC)")
    for k in (25, 50, 100, int(hi.sum())):
        p_l = hi[order_l[:k]].mean()
        p_p = hi[order_p[:k]].mean()
        p_c = hi[order_c[:k]].mean()
        lbl = f"{k}" + ("*" if k == hi.sum() else "")
        print(f"{lbl:>5s} {p_l:10.1%} {p_p:10.1%} {p_c:10.1%}")
        res3[k] = {"llm": float(p_l), "clean": float(p_p), "both": float(p_c)}
    print(f"  (* k = số câu tầng cao thật = {int(hi.sum())} · "
          f"tỉ lệ nền {hi.mean():.1%})")
    return {"n": int(len(y)), "n_cols": len(cols), "models": {
        k: {"qwk": v["qwk"], "auc": v["auc"]} for k, v in got.items()},
        "increment": res1, "error_prediction": res2, "precision_at_k": res3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="both")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--out", default="subjects/history/samples/incremental_value.json")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    subs = (["physics", "history_gv"] if args.subject == "both" else [args.subject])
    out = {}
    for s in subs:
        r = run(s, args.seed, args.boot, rng)
        if r:
            out[s] = r
        print()
    Path(args.out).write_text(json.dumps({"seed": args.seed, "results": out},
                                         ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(f"→ {args.out}")


if __name__ == "__main__":
    main()
