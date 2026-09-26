# -*- coding: utf-8 -*-
"""Đặc trưng viết tay hay biểu diễn học được: cái nào là chỗ nghẽn?

Đây là hồ sơ đo đạc biện minh cho việc đổi mô hình nền của lớp giải thích
(tools/text_backend.py). Ba câu hỏi, ba phép đo:

1. LUẬT TAY CÓ PHẢI CHỖ NGHẼN KHÔNG — so 4 mô hình trên cùng lát cắt:
     R15    XGBoost trên 15 cột viết tay          (mô hình nền cũ)
     T      TF-IDF từ + ký tự, hồi quy logistic     (nền văn bản rẻ nhất)
     E      PhoBERT đóng băng, hồi quy logistic
     E+R15  PhoBERT + 15 cột đó                    (mô hình nền mới)

2. "THÍCH NGHI" ĐO TRÊN BÀI CHƯA GẶP — ngoài lát cắt ngẫu nhiên (thứ mọi con
   số cũ của đề tài dùng), còn chia lát THEO TRANG BÀI HỌC, nên tập kiểm toàn
   câu thuộc bài mô hình chưa từng thấy. Đây mới là phép đo khái quát hoá.

3. THÊM DỮ LIỆU CÓ ĐÁNG KHÔNG — đường cong học theo 25/50/100% số BÀI huấn
   luyện. Dốc còn lên thì crawl thêm là đáng; phẳng rồi thì tiền nằm ở nhãn.

Và một phép quyết định: trên các CẶP CÂU TRÙNG (xem tools/natural_raters.py),
máy khớp nhãn giáo viên bằng mức hai lần gán nhãn của người khớp nhau chưa?

Phương án được SẮP XẾP theo chữ cái trước khi đưa vào T/E, nên mô hình văn bản
không biết phương án nào đúng — dữ liệu crawl thêm không có đáp án vẫn dùng được.

Chạy:  python tools/text_vs_rules.py --subject both
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.metrics import cohen_kappa_score, roc_auc_score
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
import natural_raters as nr  # noqa: E402
import text_backend as tb  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

OUT = "docs/text_vs_rules.json"
SEEDS = [42, 43, 44]
FRACS = [0.25, 0.5, 1.0]
KINDS = ["R15", "T", "E", "E+R15"]


def load(subject):
    cfg = cv.SUBJECTS[subject]
    eng = OntologyEngine.for_subject(cv.ontology_of(subject))
    fz = cv.Featurizer(eng, cfg["surface"])
    items = cv.load_items(subject)
    cols = cv.SURFACE_COLS[cfg["surface"]] + cv.KG_COLS
    X = pd.DataFrame([fz(q["stem"], q["correct"], q["distractors"])
                      for q in items])[cols]
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    texts = [tb.text_of(q["stem"], q["correct"], q["distractors"]) for q in items]
    for t in texts:
        tb.register(t)
    tb.embed_pending()
    E = np.vstack([tb._vec[tb._index[t]] for t in texts])
    groups = np.array([q.get("source_url") or "?" for q in items])
    return items, X, y, texts, E, groups


def _proba4(m, Z):
    p = m.predict_proba(Z)
    full = np.zeros((p.shape[0], 4))
    for j, c in enumerate(m.classes_):
        full[:, int(c)] = p[:, j]
    return full


def fit_fold(kind, D, y, tr, te, seed):
    X, texts, E = D["X"], D["texts"], D["E"]
    if kind == "R15":
        m = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                          subsample=0.8, colsample_bytree=0.8, random_state=seed,
                          eval_metric="mlogloss", verbosity=0)
        m.fit(X.iloc[tr], y[tr])
        return _proba4(m, X.iloc[te])
    if kind == "T":
        a = [texts[i] for i in tr]
        b = [texts[i] for i in te]
        vw = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=2)
        vc = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=3,
                             sublinear_tf=True, max_features=40000)
        Ztr = hstack([vw.fit_transform(a), vc.fit_transform(a)]).tocsr()
        Zte = hstack([vw.transform(b), vc.transform(b)]).tocsr()
        m = LogisticRegressionCV(Cs=[1, 4, 16], cv=3, scoring="neg_log_loss",
                                 max_iter=2000).fit(Ztr, y[tr])
        return _proba4(m, Zte)
    M = E if kind == "E" else np.hstack([E, X.to_numpy(dtype=float)])
    imp = SimpleImputer(strategy="median").fit(M[tr])
    sc = StandardScaler().fit(imp.transform(M[tr]))
    m = LogisticRegression(C=tb.C_LR, max_iter=2000)
    m.fit(sc.transform(imp.transform(M[tr])), y[tr])
    return _proba4(m, sc.transform(imp.transform(M[te])))


def oof(kind, D, y, sp, seed):
    P = np.zeros((len(y), 4))
    for tr, te in sp:
        P[te] = fit_fold(kind, D, y, tr, te, seed)
    return P


def splits(y, groups, scheme, seed):
    if scheme == "ngẫu nhiên":
        return list(StratifiedKFold(5, shuffle=True, random_state=seed).split(y, y))
    try:
        gk = GroupKFold(5, shuffle=True, random_state=seed)
    except TypeError:
        gk = GroupKFold(5)
    return list(gk.split(y, y, groups))


def metr(y, P):
    lvl = P.argmax(1)
    return {"qwk": float(cohen_kappa_score(y, lvl, weights="quadratic")),
            "auc_high": float(roc_auc_score((y >= 2).astype(int), P[:, 2:].sum(1))),
            "acc": float((y == lvl).mean())}


def subsample(tr, groups, frac, seed):
    """Bớt BÀI HỌC khỏi tập huấn luyện (không bớt câu lẻ) — mô phỏng ít dữ liệu."""
    if frac >= 1.0:
        return tr
    rng = np.random.default_rng(seed)
    g = np.unique(groups[tr])
    keep = set(rng.choice(g, size=max(2, int(round(frac * len(g)))), replace=False))
    return np.array([i for i in tr if groups[i] in keep])


def dup_pairs(subject, D, y, items):
    """Máy so với người trên CÁC CẶP CÂU TRÙNG — dùng lại cách ghép của
    natural_raters (chia lát theo nhóm câu dẫn, bản sao luôn cùng lát)."""
    cfg = cv.SUBJECTS[subject]
    lf, lm = cfg["label_field"], cfg["label_map"]
    gstem = np.array([nr.norm(q["stem"]) for q in items])
    raw = [q for q in json.loads(Path(cfg["path"]).read_text(encoding="utf-8"))
           if q.get(lf) in lm]
    by = defaultdict(list)
    for q in raw:
        by[nr.norm(q["stem"])].append(q)
    out = {}
    for kind in ("R15", "E+R15"):
        sp = list(GroupKFold(n_splits=5).split(D["X"], y, gstem))
        pred = oof(kind, D, y, sp, 42).argmax(1)
        pred_of = {}
        for q, p in zip(items, pred):
            pred_of.setdefault(nr.key_of(q), int(p))
        pairs = []
        for g, qs in by.items():
            for a, b in itertools.combinations(qs, 2):
                if nr.key_of(a) != nr.key_of(b):
                    continue
                pairs.append({"g": g, "la": lm[a[lf]], "lb": lm[b[lf]],
                              "pred": pred_of.get(nr.key_of(a))})
        P = [p for p in pairs if p["pred"] is not None]
        fns = {"hh": lambda z: nr.human_human(z),
               "mh": lambda z: nr.machine_human(z),
               "diff": lambda z: nr.machine_human(z) - nr.human_human(z)}
        pt = {k: f(P) for k, f in fns.items()}
        ci = nr.boot(P, fns, np.random.default_rng(42))
        out[kind] = {"pairs": len(P), **pt, "ci": ci,
                     "qwk_all_items": float(nr.kappa(list(y), list(pred),
                                                     "quadratic"))}
        print(f"  cặp trùng · {kind:6s} người–người {pt['hh']:.3f} | "
              f"máy–người {pt['mh']:.3f} | chênh {pt['diff']:+.3f} "
              f"[{ci['diff'][0]:+.3f}; {ci['diff'][1]:+.3f}] | "
              f"QWK toàn bộ {out[kind]['qwk_all_items']:.3f}", flush=True)
    return out


def run(subject, res):
    print(f"\n===== {subject} =====", flush=True)
    items, X, y, texts, E, groups = load(subject)
    D = {"X": X, "texts": texts, "E": E}
    r = {"n": len(y), "n_lessons": int(len(set(groups))), "main": {}, "curve": {}}
    print(f"  {len(y)} câu · {r['n_lessons']} bài · {X.shape[1]} cột luật tay",
          flush=True)
    for scheme in ("ngẫu nhiên", "bài mới"):
        for kind in KINDS:
            ms = [metr(y, oof(kind, D, y, splits(y, groups, scheme, s), s))
                  for s in SEEDS]
            agg = {k: float(np.mean([m[k] for m in ms])) for k in ms[0]}
            agg["qwk_sd"] = float(np.std([m["qwk"] for m in ms]))
            r["main"].setdefault(scheme, {})[kind] = agg
            print(f"  [{scheme:10s}] {kind:6s} QWK {agg['qwk']:.3f} "
                  f"± {agg['qwk_sd']:.3f}  AUC cao {agg['auc_high']:.3f}  "
                  f"acc {agg['acc']:.3f}", flush=True)
    for kind in KINDS:
        for frac in FRACS:
            qs = []
            for s in SEEDS:
                sp = [(subsample(tr, groups, frac, s + k), te)
                      for k, (tr, te) in enumerate(splits(y, groups, "bài mới", s))]
                qs.append(metr(y, oof(kind, D, y, sp, s))["qwk"])
            r["curve"].setdefault(kind, {})[str(frac)] = {
                "qwk": float(np.mean(qs)), "sd": float(np.std(qs))}
            print(f"  đường cong {kind:6s} {int(frac * 100):3d}% số bài: "
                  f"QWK {np.mean(qs):.3f} ± {np.std(qs):.3f}", flush=True)
    r["dup_pairs"] = dup_pairs(subject, D, y, items)
    res[subject] = r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="both",
                    choices=["physics", "history_gv", "both"])
    a = ap.parse_args()
    subs = ["physics", "history_gv"] if a.subject == "both" else [a.subject]
    res = {"seeds": SEEDS, "C_lr": tb.C_LR, "encoder": tb.MODEL_NAME}
    for s in subs:
        run(s, res)
    Path(OUT).write_text(json.dumps(res, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"\n→ {OUT}")


if __name__ == "__main__":
    main()
