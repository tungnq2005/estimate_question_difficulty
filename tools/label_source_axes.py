# -*- coding: utf-8 -*-
"""Các trục pipeline học được là thuộc tính của ĐỘ KHÓ, hay của CÁCH GÁN NHÃN?

Đây là câu hỏi nền của đề tài, và đến giờ mới trả lời được: bộ Sử kenhgiaovien
mang **hai nhãn trên cùng một câu** — `difficulty_vn` (giáo viên soạn theo ma
trận đề) và `llm_vote3_label` (LLM chấm). Cùng câu dẫn, cùng bộ phương án, cùng
ontology, cùng đặc trưng, cùng fold. **Chỉ mỗi y đổi.** Không còn biến nào khác
để đổ lỗi.

Năm phép, mỗi phép trả lời một phản biện:

1. SUY GIẢM VI SAI (hai bộ đầy đủ, không ghép cặp)
   Phản biện: *"nhãn giáo viên chỉ nhiễu hơn, nên cái gì cũng tệ đi."*
   Nếu đúng vậy, MỌI trục phải rơi cùng tỉ lệ. Đo tỉ lệ giữ lại của từng trục
   kèm khoảng tin cậy bootstrap, rồi kiểm chênh lệch giữa các tỉ lệ đó.

2. GHÉP CẶP HOÀN TOÀN (cùng câu, cùng đặc trưng, chỉ đổi y)
   Phản biện: *"hai bộ khác câu, khác phân bố nhãn."* Phép này loại sạch.
   Bootstrap ghép cặp trên chênh lệch QWK.

3. TỪNG CỘT — cột nào đổi độ lớn khi đổi nguồn nhãn, trên cùng tập ghép cặp.

4. TẦNG CAO — mô hình có tìm được VD/VDC của giáo viên không? Đây là chỗ LLM
   sụp hoàn toàn (đồng thuận 7,1%), nên là phép thử khắc nghiệt nhất.

5. NULL HOÁN VỊ — QWK bằng bao nhiêu khi nhãn bị xáo? Cho biết "0" nghĩa là gì
   và một con số nhỏ có khác 0 thật không.

Bootstrap dùng dự đoán out-of-fold CỐ ĐỊNH rồi lấy mẫu lại theo câu (không khớp
lại mô hình mỗi vòng) — chuẩn cho khoảng tin cậy của thước đo, và rẻ.

Chạy:  python tools/label_source_axes.py [--seed 42] [--boot 2000]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import (cohen_kappa_score, f1_score, recall_score,
                             roc_auc_score)
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

LV = {"Nhận biết": 0, "Thông hiểu": 1, "Vận dụng": 2, "Vận dụng cao": 3}
NAME = ["NB", "TH", "VD", "VDC"]
MK = dict(n_estimators=200, max_depth=4, learning_rate=0.1, subsample=0.8,
          colsample_bytree=0.8, eval_metric="mlogloss", verbosity=0)


def oof(X: pd.DataFrame, y: np.ndarray, seed: int) -> np.ndarray:
    """Dự đoán out-of-fold, 5 fold phân tầng — cùng seed ⇒ cùng fold."""
    pred = np.zeros(len(y), dtype=int)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y):
        m = XGBClassifier(**MK, random_state=seed).fit(X.iloc[tr], y[tr])
        pred[te] = m.predict(X.iloc[te])
    return pred


def qwk(y, p):
    return float(cohen_kappa_score(y, p, weights="quadratic"))


def boot_idx(n: int, rng, reps: int):
    for _ in range(reps):
        yield rng.integers(0, n, n)


def ci(v, lo=2.5, hi=97.5):
    v = np.asarray([x for x in v if np.isfinite(x)])
    return (float(np.percentile(v, lo)), float(np.percentile(v, hi))) if len(v) else (np.nan, np.nan)


# ----------------------------------------------------------------------
def featurize(items, fz, cols):
    return pd.DataFrame([fz(q["stem"], q["correct"], q["distractors"])
                         for q in items])[cols]


def part1(fz, cols, sets, seed, reps, rng) -> dict:
    print("\n" + "=" * 78)
    print("1) SUY GIẢM VI SAI — hai bộ đầy đủ, cùng pipeline, khác nguồn nhãn")
    print("=" * 78)
    print('Phản biện cần loại: "nhãn giáo viên chỉ nhiễu hơn nên cái gì cũng tệ".')
    print("Nếu đúng vậy, mọi trục phải giữ lại CÙNG một tỉ lệ.\n")

    store = {}
    for sub in ("history", "history_gv"):
        items = cv.load_items(sub)
        cfg = cv.SUBJECTS[sub]
        y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
        X = featurize(items, fz, cols)
        store[sub] = {"y": y, "X": X, "n": len(items),
                      "pred": {nm: oof(X[c], y, seed) for nm, c in sets}}
        print(f"{sub:11s} n={len(items):5d} | nhãn: {cfg['label_by']} | phân bố " +
              " ".join(f"{NAME[k]} {int((y == k).sum())}" for k in range(4)))

    print(f"\n{'bộ đặc trưng':22s} {'QWK LLM':>18s} {'QWK GV':>18s} {'giữ lại':>16s}")
    res, keep_draws = {}, {}
    for nm, _ in sets:
        row = {}
        for sub, tag in (("history", "llm"), ("history_gv", "gv")):
            d = store[sub]
            row[tag] = qwk(d["y"], d["pred"][nm])
            bs = [qwk(d["y"][i], d["pred"][nm][i]) for i in boot_idx(d["n"], rng, reps)]
            row[tag + "_ci"] = ci(bs)
            row[tag + "_boot"] = np.array(bs)
        # tỉ lệ giữ lại: bootstrap ĐỘC LẬP hai bộ (chúng là hai mẫu khác nhau)
        k = row["gv_boot"] / np.where(np.abs(row["llm_boot"]) < 1e-9,
                                      np.nan, row["llm_boot"])
        keep_draws[nm] = k
        keep = row["gv"] / row["llm"] if abs(row["llm"]) > 1e-9 else np.nan
        klo, khi = ci(k)
        print(f"{nm:22s} {row['llm']:7.3f} [{row['llm_ci'][0]:+.2f},{row['llm_ci'][1]:+.2f}]"
              f" {row['gv']:7.3f} [{row['gv_ci'][0]:+.2f},{row['gv_ci'][1]:+.2f}]"
              f" {keep:7.0%} [{klo:.0%},{khi:.0%}]")
        res[nm] = {"qwk_llm": row["llm"], "ci_llm": row["llm_ci"],
                   "qwk_gv": row["gv"], "ci_gv": row["gv_ci"],
                   "retention": float(keep), "retention_ci": [klo, khi]}

    a, b = "bề mặt", "KG đầy đủ"
    d = keep_draws[a] - keep_draws[b]
    d = d[np.isfinite(d)]
    p = 2 * min((d <= 0).mean(), (d >= 0).mean())
    print(f"\nchênh tỉ lệ giữ lại ({a} − {b}) = "
          f"{res[a]['retention'] - res[b]['retention']:+.0%} "
          f"[{ci(d)[0]:+.0%},{ci(d)[1]:+.0%}] · p = {p:.3f}")
    print("⇒ p nhỏ = hai trục KHÔNG rơi cùng nhau ⇒ phản biện 'chỉ là nhiễu' bị loại.")
    res["retention_diff"] = {"pair": [a, b],
                             "diff": float(res[a]["retention"] - res[b]["retention"]),
                             "ci": list(ci(d)), "p": float(p)}
    return res


def part2(pairs, fz, cols, sets, seed, reps, rng) -> dict:
    print("\n" + "=" * 78)
    print(f"2) GHÉP CẶP HOÀN TOÀN — cùng {len(pairs)} câu, cùng đặc trưng, "
          "cùng fold, CHỈ ĐỔI y")
    print("=" * 78)
    X = featurize(pairs, fz, cols)
    y_gv = np.array([LV[q["difficulty_vn"]] for q in pairs])
    y_llm = np.array([LV[q["llm_vote3_label"]] for q in pairs])
    print("nhãn GV : " + " ".join(f"{NAME[k]} {int((y_gv == k).sum())}" for k in range(4)))
    print("nhãn LLM: " + " ".join(f"{NAME[k]} {int((y_llm == k).sum())}" for k in range(4)))
    print(f"đồng thuận hai nhãn: κ {cohen_kappa_score(y_gv, y_llm):+.3f} · "
          f"QWK {qwk(y_gv, y_llm):+.3f}\n")

    print(f"{'bộ đặc trưng':22s} {'QWK vs LLM':>11s} {'QWK vs GV':>10s} "
          f"{'chênh':>8s} {'KTC 95% chênh':>18s} {'p':>7s}")
    res = {}
    for nm, c in sets:
        p_llm, p_gv = oof(X[c], y_llm, seed), oof(X[c], y_gv, seed)
        q_llm, q_gv = qwk(y_llm, p_llm), qwk(y_gv, p_gv)
        # ghép cặp: MỖI vòng lấy CÙNG bộ chỉ số cho cả hai nhãn
        bs = np.array([qwk(y_gv[i], p_gv[i]) - qwk(y_llm[i], p_llm[i])
                       for i in boot_idx(len(pairs), rng, reps)])
        bs = bs[np.isfinite(bs)]
        pv = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        lo, hi = ci(bs)
        print(f"{nm:22s} {q_llm:11.3f} {q_gv:10.3f} {q_gv - q_llm:+8.3f} "
              f"[{lo:+.3f},{hi:+.3f}] {pv:7.3f}")
        res[nm] = {"qwk_vs_llm": q_llm, "qwk_vs_gv": q_gv,
                   "diff": q_gv - q_llm, "ci": [lo, hi], "p": float(pv)}
    print("\n⇒ chênh âm = cùng đặc trưng đó đoán nhãn MÁY tốt hơn đoán nhãn NGƯỜI.")
    return res


def oof_high(X: pd.DataFrame, y: np.ndarray, seed: int) -> np.ndarray:
    """Xác suất out-of-fold cho TẦNG CAO (VD+VDC)."""
    p = np.zeros(len(y))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y):
        m = XGBClassifier(**MK, random_state=seed).fit(X.iloc[tr], y[tr])
        pr = m.predict_proba(X.iloc[te])
        cls = list(m.classes_)
        p[te] = sum(pr[:, cls.index(k)] for k in (2, 3) if k in cls)
    return p


def part2b(pairs, fz, cols, sets, seed, reps, rng) -> dict:
    """Phản biện: 'QWK thấp chỉ vì nhãn GV dồn 62% vào TH.'

    QWK nhạy với phân bố biên. AUC thì KHÔNG — nó bất biến với tỉ lệ lớp. Nếu
    hình mẫu vẫn giữ nguyên trên AUC, phản biện phân bố bị loại.
    """
    print("\n" + "=" * 78)
    print("2b) ĐỐI CHỨNG PHÂN BỐ — AUC tầng cao, bất biến với tỉ lệ lớp")
    print("=" * 78)
    print('Phản biện cần loại: "QWK thấp chỉ vì nhãn GV dồn 62% vào TH."')
    X = featurize(pairs, fz, cols)
    y_gv = np.array([LV[q["difficulty_vn"]] for q in pairs])
    y_llm = np.array([LV[q["llm_vote3_label"]] for q in pairs])
    h_gv, h_llm = (y_gv >= 2).astype(int), (y_llm >= 2).astype(int)
    print(f"tầng cao theo GV: {h_gv.sum()}/{len(h_gv)} ({h_gv.mean():.1%}) · "
          f"theo LLM: {h_llm.sum()}/{len(h_llm)} ({h_llm.mean():.1%})\n")
    print(f"{'bộ đặc trưng':22s} {'AUC vs LLM':>11s} {'AUC vs GV':>10s} "
          f"{'chênh':>8s} {'KTC 95% chênh':>18s} {'p':>7s}")
    res = {}
    for nm, c in sets:
        s_llm, s_gv = oof_high(X[c], y_llm, seed), oof_high(X[c], y_gv, seed)
        a_llm, a_gv = roc_auc_score(h_llm, s_llm), roc_auc_score(h_gv, s_gv)
        bs = []
        for i in boot_idx(len(pairs), rng, reps):
            if len(set(h_gv[i])) < 2 or len(set(h_llm[i])) < 2:
                continue
            bs.append(roc_auc_score(h_gv[i], s_gv[i]) -
                      roc_auc_score(h_llm[i], s_llm[i]))
        bs = np.asarray(bs)
        pv = 2 * min((bs <= 0).mean(), (bs >= 0).mean()) if len(bs) else np.nan
        lo, hi = ci(bs)
        print(f"{nm:22s} {a_llm:11.3f} {a_gv:10.3f} {a_gv - a_llm:+8.3f} "
              f"[{lo:+.3f},{hi:+.3f}] {pv:7.3f}")
        res[nm] = {"auc_vs_llm": float(a_llm), "auc_vs_gv": float(a_gv),
                   "diff": float(a_gv - a_llm), "ci": [lo, hi], "p": float(pv)}
    print("\n(AUC 0,50 = vô dụng. Thước này KHÔNG đổi theo tỉ lệ lớp,")
    print(" nên chênh lệch ở đây không thể đổ cho phân bố nhãn.)")
    return res


def part3(pairs, fz, cols, reps, rng) -> dict:
    print("\n" + "=" * 78)
    print("3) TỪNG CỘT — cùng câu, cùng cột, hai nguồn nhãn")
    print("=" * 78)
    F = [fz(q["stem"], q["correct"], q["distractors"]) for q in pairs]
    y_gv = np.array([LV[q["difficulty_vn"]] for q in pairs])
    y_llm = np.array([LV[q["llm_vote3_label"]] for q in pairs])
    print(f"{'cột':26s} {'ρ vs GV':>9s} {'ρ vs LLM':>9s} {'chênh':>8s} {'p':>7s}")
    out = {}
    rows = []
    for c in cols:
        v = np.array([f[c] for f in F], float)
        m = ~np.isnan(v)
        if m.sum() < 30 or np.nanstd(v[m]) == 0:
            continue
        r_g, r_l = spearmanr(v[m], y_gv[m])[0], spearmanr(v[m], y_llm[m])[0]
        bs = []
        for i in boot_idx(int(m.sum()), rng, reps):
            vv, gg, ll = v[m][i], y_gv[m][i], y_llm[m][i]
            if np.std(vv) == 0 or len(set(gg)) < 2 or len(set(ll)) < 2:
                continue
            bs.append(spearmanr(vv, ll)[0] - spearmanr(vv, gg)[0])
        bs = np.asarray(bs)
        pv = 2 * min((bs <= 0).mean(), (bs >= 0).mean()) if len(bs) else np.nan
        rows.append((abs(r_l - r_g), c, r_g, r_l, pv))
        out[c] = {"rho_gv": float(r_g), "rho_llm": float(r_l),
                  "diff": float(r_l - r_g), "p": float(pv)}
    for _, c, r_g, r_l, pv in sorted(rows, reverse=True):
        star = " ***" if pv < 0.05 / max(1, len(rows)) else (" *" if pv < 0.05 else "")
        print(f"{c:26s} {r_g:+9.3f} {r_l:+9.3f} {r_l - r_g:+8.3f} {pv:7.3f}{star}")
    print(f"\n*** = qua ngưỡng Bonferroni p < {0.05 / max(1, len(rows)):.4f} "
          f"({len(rows)} phép so sánh)")
    return out


def part4(fz, cols, sets, seed) -> dict:
    print("\n" + "=" * 78)
    print("4) TẦNG CAO — mô hình có tìm được VD/VDC của GIÁO VIÊN không?")
    print("=" * 78)
    print("Đây là chỗ LLM sụp hoàn toàn (đồng thuận với GV chỉ 7,1% ở tầng này),")
    print("nên là phép thử khắc nghiệt nhất — và là thứ quan trọng nhất khi ra đề.\n")
    out = {}
    for sub in ("history", "history_gv"):
        cfg = cv.SUBJECTS[sub]
        items = cv.load_items(sub)
        y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
        X = featurize(items, fz, cols)
        nm, c = sets[-1]                      # bộ đầy đủ nhất
        pred = oof(X[c], y, seed)
        rec = recall_score(y, pred, average=None, labels=range(4), zero_division=0)
        print(f"{sub:11s} ({cfg['label_by']})")
        print("   recall theo lớp: " +
              " · ".join(f"{NAME[k]} {rec[k]:.1%} (n={int((y == k).sum())})"
                         for k in range(4)))
        print(f"   macro-F1 {f1_score(y, pred, average='macro'):.3f} · "
              f"QWK {qwk(y, pred):.3f} · dự đoán VD/VDC: "
              f"{int(((pred == 2) | (pred == 3)).sum())} câu "
              f"(thật {int(((y == 2) | (y == 3)).sum())})\n")
        out[sub] = {"recall": rec.tolist(), "n_per_class": [int((y == k).sum())
                                                            for k in range(4)],
                    "macro_f1": float(f1_score(y, pred, average="macro")),
                    "qwk": qwk(y, pred),
                    "n_pred_high": int(((pred == 2) | (pred == 3)).sum()),
                    "n_true_high": int(((y == 2) | (y == 3)).sum())}
    return out


def part5(fz, cols, sets, seed, rng) -> dict:
    print("=" * 78)
    print("5) NULL HOÁN VỊ — 'QWK = 0,15' thì có khác 0 thật không?")
    print("=" * 78)
    out = {}
    for sub in ("history", "history_gv"):
        cfg = cv.SUBJECTS[sub]
        items = cv.load_items(sub)
        y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
        X = featurize(items, fz, cols)
        nulls = []
        for _ in range(20):
            ys = rng.permutation(y)
            nulls.append(qwk(ys, oof(X[cols], ys, seed)))
        nulls = np.array(nulls)
        real = qwk(y, oof(X[cols], y, seed))
        print(f"{sub:11s} QWK thật {real:+.3f} | null xáo nhãn "
              f"{nulls.mean():+.3f} ± {nulls.std():.3f} "
              f"(khoảng [{nulls.min():+.3f},{nulls.max():+.3f}], 20 lần)")
        out[sub] = {"real": real, "null_mean": float(nulls.mean()),
                    "null_sd": float(nulls.std()), "n_perm": 20}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--out", default="subjects/history/samples/label_source_axes.json")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    surf = cv.SURFACE_COLS["verbosity"]
    cols = surf + cv.KG_COLS
    sets = [("bề mặt", surf), ("KG lõi giả thuyết", ["kad_path_distance_mean",
                                                     "jaccard_kg_max",
                                                     "jaccard_kg_mean", "rsi_dc"]),
            ("KG đầy đủ", cv.KG_COLS), ("bề mặt + KG", cols)]
    eng = OntologyEngine.for_subject("history")
    fz = cv.Featurizer(eng, "verbosity")
    print(f"ontology Sử: {len(eng)} thực thể, {eng.nx_graph.number_of_edges()} cạnh "
          f"| {len(surf)} cột bề mặt + {len(cv.KG_COLS)} cột KG | "
          f"bootstrap {args.boot}")

    kgv = cv.load_items("history_gv")
    pairs = [q for q in kgv
             if q.get("llm_vote3_label") in LV and q["difficulty_vn"] in LV]

    r1 = part1(fz, cols, sets, args.seed, args.boot, rng)
    r2 = part2(pairs, fz, cols, sets, args.seed, args.boot, rng)
    r2b = part2b(pairs, fz, cols, sets, args.seed, args.boot, rng)
    r3 = part3(pairs, fz, cols, args.boot, rng)
    r4 = part4(fz, cols, sets, args.seed)
    r5 = part5(fz, cols, sets, args.seed, rng)

    Path(args.out).write_text(json.dumps(
        {"seed": args.seed, "n_boot": args.boot, "n_paired": len(pairs),
         "differential_retention": r1, "paired_same_items": r2, "paired_auc_control": r2b,
         "per_column": r3, "high_tier": r4, "permutation_null": r5},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {args.out}")


if __name__ == "__main__":
    main()
