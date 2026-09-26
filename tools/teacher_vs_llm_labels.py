# -*- coding: utf-8 -*-
"""Nhãn NGƯỜI vs nhãn LLM trên CÙNG một bộ câu — trục nào là của độ khó thật?

Câu hỏi: các trục mà pipeline học được là thuộc tính của ĐỘ KHÓ, hay là thuộc
tính của CÁCH GÁN NHÃN? Chỉ trả lời được khi cùng một câu có **hai nguồn nhãn**.

Hai môn, hai thế đối xứng nhau:

  history  nhãn nền là LLM (`llm_vote3`, 2.137 câu); nhãn NGƯỜI chỉ có 90 câu
           do 1 giáo viên chấm  → mẫu nhỏ, thang 3 mức
  physics  nhãn nền là GIÁO VIÊN (1.539 câu, ma trận đề); nhãn LLM có đủ cho cả
           1.539 câu do `tools/llm_judge_physics.py` chấm mù → mẫu lớn, 4 mức

Ba phép:
  1. Đồng thuận hai nguồn nhãn (kappa / QWK / ma trận nhầm)
  2. Tương quan GHÉP CẶP từng đặc trưng với hai nguồn; chênh lệch kiểm bằng
     bootstrap (chênh trên CÙNG mẫu ⇒ không dùng Fisher z hai mẫu độc lập)
  3. Chuyển giao: huấn luyện trên nhãn LLM rồi đo lại trên CẢ HAI nguồn nhãn
     (history: loại 90 câu khỏi tập huấn luyện · physics: 5-fold out-of-fold)

Chạy:  python tools/teacher_vs_llm_labels.py --subject history|physics|both
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

TEACHER_FILE = "subjects/history/samples/su9_difficulty_teacher1_2026-08-17.json"
LLMJUDGE_FILE = "subjects/physics/samples/mcq_kenhgiaovien_llmjudge.json"
N_BOOT = 2000
LV4 = {"NB": 0, "TH": 1, "VD": 2, "VDC": 3}
NAME = {3: ["Dễ", "TB", "Khó"], 4: ["NB", "TH", "VD", "VDC"]}


def pairs_history():
    """90 câu: người = giáo viên (3 mức) · máy = llm_vote3 quy về 3 mức."""
    teacher = json.loads(Path(TEACHER_FILE).read_text(encoding="utf-8"))["responses"]
    rows = json.loads(Path(cv.SUBJECTS["history"]["path"]).read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in rows}
    tmap, lmap = {"easy": 0, "medium": 1, "hard": 2}, {"Easy": 0, "Medium": 1, "Hard": 2}
    ids = [i for i in teacher if i in by_id]
    return {
        "items": [by_id[i] for i in ids],
        "y_human": np.array([tmap[teacher[i]["verdict"]] for i in ids]),
        "y_llm": np.array([lmap[by_id[i]["difficulty"]] for i in ids]),
        "n_levels": 3, "human_src": "1 giáo viên (form web)", "llm_src": "llm_vote3",
        "train_pool": [q for q in rows
                       if q.get("is_canonical") and q["id"] not in set(ids)],
        "train_label": lambda q: lmap[q["difficulty"]],
    }


def pairs_physics():
    """1.539 câu: người = giáo viên (ma trận đề) · máy = LLM chấm mù."""
    rows = json.loads(Path(LLMJUDGE_FILE).read_text(encoding="utf-8"))
    rows = [q for q in rows if q.get("llm_level") in LV4]
    return {
        "items": rows,
        "y_human": np.array([LV4[q["difficulty"]] for q in rows]),
        "y_llm": np.array([LV4[q["llm_level"]] for q in rows]),
        "n_levels": 4, "human_src": "giáo viên (ma trận đề)",
        "llm_src": "deepseek-v4-pro chấm mù",
        "train_pool": None,       # dùng out-of-fold trên chính bộ này
        "train_label": lambda q: LV4[q["llm_level"]],
    }


BUILD = {"history": pairs_history, "physics": pairs_physics}


def run(subject: str, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    d = BUILD[subject]()
    items, y_h, y_l, K = d["items"], d["y_human"], d["y_llm"], d["n_levels"]
    names = NAME[K]

    print("\n" + "#" * 74)
    print(f"# {subject.upper()} — n = {len(items)} | người: {d['human_src']} "
          f"| máy: {d['llm_src']}")
    print("#" * 74)
    print("NGƯỜI: " + " ".join(f"{names[k]} {int((y_h == k).sum())}" for k in range(K)))
    print("MÁY  : " + " ".join(f"{names[k]} {int((y_l == k).sum())}" for k in range(K)))

    print("\n" + "=" * 74)
    print("1) ĐỒNG THUẬN HAI NGUỒN NHÃN")
    print("=" * 74)
    kap = cohen_kappa_score(y_h, y_l)
    qwk = cohen_kappa_score(y_h, y_l, weights="quadratic")
    rho, prho = spearmanr(y_h, y_l)
    print(f"đồng thuận tuyệt đối {np.mean(y_h == y_l):.1%} | Cohen κ {kap:+.3f} | "
          f"QWK {qwk:+.3f} | Spearman {rho:+.3f} (p={prho:.2g})")
    M = np.zeros((K, K), int)
    for a, b in zip(y_h, y_l):
        M[a, b] += 1
    print("ma trận (hàng NGƯỜI, cột MÁY): " + " ".join(f"{n:>5s}" for n in names))
    for r, n in zip(M, names):
        print(f"  {n:5s}                       " + " ".join(f"{v:5d}" for v in r))

    cfg = cv.SUBJECTS[subject]
    eng = OntologyEngine.for_subject(subject)
    fz = cv.Featurizer(eng, cfg["surface"])
    cols = cv.SURFACE_COLS[cfg["surface"]] + cv.KG_COLS
    F = [fz(q["stem"], q["correct"], q["distractors"]) for q in items]

    print("\n" + "=" * 74)
    print("2) TƯƠNG QUAN GHÉP CẶP — cùng câu, cùng đặc trưng, hai nguồn nhãn")
    print("=" * 74)
    print(f"{'đặc trưng':26s} {'ρ vs NGƯỜI':>11s} {'ρ vs MÁY':>10s} {'chênh':>8s} "
          f"{'p(boot)':>9s}")
    feats = {}
    for c in cols:
        v = np.array([f[c] for f in F], dtype=float)
        m = ~np.isnan(v)
        if m.sum() < 20 or np.nanstd(v[m]) == 0:
            continue
        r_h = spearmanr(v[m], y_h[m])[0]
        r_l = spearmanr(v[m], y_l[m])[0]
        idx = np.arange(int(m.sum()))
        bs = []
        for _ in range(N_BOOT):
            s = rng.choice(idx, len(idx), replace=True)
            if len(set(y_h[m][s])) < 2 or len(set(y_l[m][s])) < 2 or np.std(v[m][s]) == 0:
                continue
            bs.append(spearmanr(v[m][s], y_l[m][s])[0]
                      - spearmanr(v[m][s], y_h[m][s])[0])
        bs = np.array(bs)
        p = 2 * min((bs <= 0).mean(), (bs >= 0).mean()) if len(bs) else np.nan
        print(f"{c:26s} {r_h:+11.3f} {r_l:+10.3f} {r_l - r_h:+8.3f} {p:9.3f}")
        feats[c] = {"rho_human": float(r_h), "rho_llm": float(r_l),
                    "diff": float(r_l - r_h), "p_boot": float(p), "n": int(m.sum())}
    k = len(feats)
    print(f"\n⚠️ {k} phép so sánh — ngưỡng Bonferroni p < {0.05 / k:.4f}.")

    print("\n" + "=" * 74)
    print("3) CHUYỂN GIAO — mô hình huấn luyện trên NHÃN MÁY, đo trên cả hai nguồn")
    print("=" * 74)
    Xte = pd.DataFrame(F)[cols]
    mk = dict(n_estimators=200, max_depth=4, learning_rate=0.1, subsample=0.8,
              colsample_bytree=0.8, random_state=seed, eval_metric="mlogloss",
              verbosity=0)
    if d["train_pool"] is not None:
        tr = d["train_pool"]
        ytr = np.array([d["train_label"](q) for q in tr])
        Xtr = pd.DataFrame([fz(q["stem"], q["correct"], q["distractors"])
                            for q in tr])[cols]
        print(f"huấn luyện {len(tr)} câu (đã loại {len(items)} câu có nhãn người)")
        pred = XGBClassifier(**mk).fit(Xtr, ytr).predict(Xte)
    else:
        print(f"out-of-fold 5 lớp trên chính {len(items)} câu (nhãn máy)")
        pred = np.zeros(len(items), dtype=int)
        for tri, tei in StratifiedKFold(5, shuffle=True,
                                        random_state=seed).split(Xte, y_l):
            pred[tei] = XGBClassifier(**mk).fit(Xte.iloc[tri], y_l[tri]).predict(
                Xte.iloc[tei])
    transfer = {}
    for nm, yy in (("nhãn MÁY", y_l), ("nhãn NGƯỜI", y_h)):
        acc, kk = float(np.mean(pred == yy)), cohen_kappa_score(yy, pred)
        qq = cohen_kappa_score(yy, pred, weights="quadratic")
        rr = spearmanr(yy, pred)[0]
        print(f"  so với {nm:12s} acc {acc:.3f} | κ {kk:+.3f} | QWK {qq:+.3f} | "
              f"ρ {rr:+.3f}")
        transfer[nm] = {"acc": acc, "kappa": float(kk), "qwk": float(qq),
                        "spearman": float(rr)}
    base = float(max(np.bincount(y_h, minlength=K)) / len(y_h))
    print(f"  (baseline đoán lớp đông nhất của NGƯỜI: acc {base:.3f})")

    return {"n_items": len(items), "n_levels": K, "human_src": d["human_src"],
            "llm_src": d["llm_src"],
            "agreement": {"absolute": float(np.mean(y_h == y_l)),
                          "kappa": float(kap), "qwk": float(qwk),
                          "spearman": float(rho),
                          "confusion_human_rows": M.tolist()},
            "paired_correlations": feats, "bonferroni_threshold": 0.05 / k,
            "transfer": transfer, "human_majority_acc": base}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="both", choices=["history", "physics", "both"])
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    subs = ["history", "physics"] if args.subject == "both" else [args.subject]
    for s in subs:
        res = run(s, args.seed)
        out = f"subjects/{s}/samples/teacher_vs_llm.json"
        Path(out).write_text(json.dumps(dict(res, subject=s, seed=args.seed),
                                        ensure_ascii=False, indent=2),
                             encoding="utf-8")
        print(f"→ {out}")


if __name__ == "__main__":
    main()
