# -*- coding: utf-8 -*-
"""Ba cửa bác bỏ, áp cho TỪNG TRỤC — dự báo thì LLM cũng làm được, cái này thì không.

Đề tài không hơn LLM ở con số dự báo (QWK 0,531 so với 0,540,
`docs/OPERATION_AXIS.md` §4.1). Chỗ đứng của nó là: **mọi phát biểu về độ khó
đều phải đi qua một phép bác bỏ**. Một LLM trả lời "VDC" thì không phép nào ở
đây áp được cho nó — không khử được nhiễu chủ đề khỏi lời nó nói, không có đối
chứng để giết lời nói sai, không can thiệp được vào "lí do" của nó để đo tỉ trọng.

Ba cửa, áp cho từng trục:

  1. KHỬ NHIỄU BẰNG THIẾT KẾ — hiệu ứng phải còn khi biến gây nhiễu bị giữ
     nguyên. Khử bằng cách CHỌN MẪU, không bằng cách thêm biến kiểm soát:
       · trục THAO TÁC → so trong cùng một BÀI (giữ nguyên trục tri thức)
       · trục TRI THỨC → so trong cùng một Ô "bài × số bước" (giữ nguyên CẢ
         chủ đề LẪN tải thao tác). Môn không có vết giải thì lùi về cùng bài.
     Báo cả hệ số TRONG nhóm lẫn GIỮA nhóm: giữa >> trong ⇒ nhiễu chủ đề.

  2. ĐỐI CHỨNG PHẢI TRƯỢT — thiết kế nào làm yếu tố nào cũng "đúng" thì vô dụng.
     Hai đối chứng chạy song song mọi lúc: `kad_path_distance_mean` (đại lượng
     lõi giả thuyết Vinu, đã bị bác bỏ) và một cột XÁO NGẪU NHIÊN.

  3. CAN THIỆP TRÊN MANIFOLD — không bịa giá trị: lấy hai câu THẬT cùng nhóm,
     ghép khối đặc trưng của câu này vào câu kia, so ΔE[y] của mô hình với chênh
     NHÃN THẬT của đúng hai câu đó. Kèm mốc trên (hoán đổi toàn bộ đặc trưng) để
     đọc được tỉ lệ như một PHÂN RÃ CÓ ĐƠN VỊ, không phải điểm số.

Ghi chú thiết kế: ICC theo bài của các cột tri thức chỉ 0,05–0,17, tức 83–95%
biến thiên nằm TRONG bài ⇒ thiết kế "cùng bài" dùng được cho cả trục tri thức.

Chạy:  python tools/axis_evidence.py [--subject both] [--gap 1.0]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, spearmanr
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import incremental_value as iv  # noqa: E402

NAME = ["NB", "TH", "VD", "VDC"]
MK = iv.MK
NEG = "kad_path_distance_mean"          # đại lượng Vinu — PHẢI trượt mọi cửa

AXES = {
    "THAO TÁC": {
        "probes": ["tr_steps", "tr_ont_steps_sum", "tr_n_formula", "tr_unknowns",
                   "tr_given"],
        "group": "lesson",
        "why": "cùng BÀI ⇒ giữ nguyên trục tri thức (chủ đề, chương, nội dung)",
    },
    "TRI THỨC": {
        "probes": ["kg_centrality_mean", "kg_entity_match_coverage",
                   "kg_num_correct", "kg_prereq_correct"],
        "group": "lesson_x_steps",
        "why": "cùng Ô bài×số bước ⇒ giữ nguyên CẢ chủ đề LẪN tải thao tác",
    },
}


def z(v):
    v = np.asarray(v, float)
    sd = np.nanstd(v)
    return (v - np.nanmean(v)) / sd if sd > 0 else v * np.nan


def make_groups(kind, items, X):
    les = np.array([q["source_url"] for q in items])
    if kind == "lesson" or "tr_steps" not in X.columns:
        return les, ("bài" if kind == "lesson" else "bài — môn này không có vết giải")
    st = X["tr_steps"].values.astype(float)
    strat = np.where(np.isnan(st), -1, np.clip(st, 0, 3)).astype(int)
    return np.array([f"{a}|{b}" for a, b in zip(les, strat)]), "bài × số bước"


def fe(y, x, g):
    """Hệ số TRONG nhóm (hiệu ứng cố định) và GIỮA nhóm."""
    df = pd.DataFrame({"y": y, "x": x, "g": g}).dropna()
    if df.empty or df.g.nunique() < 3:
        return {}
    gm = df.groupby("g").transform("mean")
    wy, wx = df.y - gm.y, df.x - gm.x
    out = {}
    if wx.std() > 0:
        b = float(np.polyfit(wx, wy, 1)[0])
        n, k = len(df), df.g.nunique()
        r = wy - b * wx
        se = float(np.sqrt((r ** 2).sum() / max(1, n - k - 1)
                           / max(1e-12, (wx ** 2).sum())))
        out["within"] = {"beta": b, "se": se, "t": b / max(1e-12, se),
                         "rho": float(spearmanr(wx, wy)[0]), "n": n,
                         "n_groups": int(k)}
    bm = df.groupby("g")[["y", "x"]].mean()
    if len(bm) > 3 and bm.x.std() > 0:
        out["between"] = {"beta": float(np.polyfit(bm.x, bm.y, 1)[0]),
                          "rho": float(spearmanr(bm.x, bm.y)[0])}
    return out


def pair_test(y, x, g, gap):
    by = collections.defaultdict(list)
    for yy, xx, gg in zip(y, x, g):
        if not np.isnan(xx):
            by[gg].append((yy, xx))
    win = tie = lose = 0
    for v in by.values():
        for i in range(len(v)):
            for j in range(i + 1, len(v)):
                if abs(v[i][1] - v[j][1]) < gap:
                    continue
                a, b = (v[i], v[j]) if v[i][1] > v[j][1] else (v[j], v[i])
                win, tie, lose = (win + (a[0] > b[0]), tie + (a[0] == b[0]),
                                  lose + (a[0] < b[0]))
    dec = win + lose
    return {"win": win, "lose": lose, "tie": tie,
            "rate": win / dec if dec else np.nan,
            "p": float(binomtest(win, dec, 0.5).pvalue) if dec else np.nan}


def swap_pairs(x, g, gap):
    """Cặp THẬT cùng nhóm, chênh ≥ gap: (chỉ số câu cao, chỉ số câu thấp)."""
    by = collections.defaultdict(list)
    for i, gg in enumerate(g):
        if not np.isnan(x[i]):
            by[gg].append(i)
    out = []
    for idxs in by.values():
        for a in idxs:
            for b in idxs:
                if x[a] - x[b] >= gap:
                    out.append((a, b))
    return out


def run_axis(axis, cfgA, items, X, y, cols, full, base, gap, rng):
    g, gname = make_groups(cfgA["group"], items, X)
    probes = [c for c in cfgA["probes"] if c in X.columns
              and X[c].notna().any() and X[c].std(skipna=True) > 0]
    if not probes:
        print(f"\n### TRỤC {axis}: không có cột nào dùng được ở môn này — bỏ qua")
        return None
    print(f"\n{'#' * 78}\n### TRỤC {axis}   ·   nhóm = {gname} "
          f"({len(set(g))} nhóm)\n### khử nhiễu: {cfgA['why']}\n{'#' * 78}")

    # ---- cửa 1
    print(f"\n[1] HIỆU ỨNG CỐ ĐỊNH  {'β trong':>10s} {'t':>7s} {'ρ trong':>8s} "
          f"{'β giữa':>9s} {'ρ giữa':>8s}")
    resA = {}
    for c in probes + [NEG]:
        if c not in X.columns:
            continue
        r = fe(y.astype(float), z(X[c].values), g)
        if "within" not in r:
            continue
        w, b = r["within"], r.get("between", {})
        tag = "  ← đối chứng" if c == NEG else ""
        print(f"    {c:26s} {w['beta']:+10.4f} {w['t']:+7.2f} {w['rho']:+8.3f} "
              f"{b.get('beta', float('nan')):+9.4f} "
              f"{b.get('rho', float('nan')):+8.3f}{tag}")
        resA[c] = r

    # ---- cửa 2
    print(f"\n[2] CẶP GHÉP (chênh ≥ {gap} độ lệch chuẩn)"
          f"      {'thắng':>7s} {'thua':>6s} {'tỉ lệ':>8s} {'p':>10s}")
    resB = {}
    rows = [(c, z(X[c].values)) for c in probes]
    rows.append((NEG + " ⟨đối chứng⟩", z(X[NEG].values)))
    rows.append(("XÁO ngẫu nhiên ⟨đối chứng⟩", rng.permutation(z(X[probes[0]].values))))
    for nm, v in rows:
        r = pair_test(y, v, g, gap)
        if not (r["win"] + r["lose"]):
            continue
        mark = "" if r["p"] > 0.05 else " ***"
        print(f"    {nm:34s} {r['win']:7d} {r['lose']:6d} {r['rate']:8.1%} "
              f"{r['p']:10.2e}{mark}")
        resB[nm] = r

    # ---- cửa 3
    pairs = swap_pairs(z(X[probes[0]].values), g, 1.0)
    resD = {}
    if len(pairs) >= 50:
        hi = np.array([a for a, _ in pairs])
        lo = np.array([b for _, b in pairs])
        dlab = float(np.mean(y[hi] - y[lo]))
        print(f"\n[3] CAN THIỆP TRÊN MANIFOLD — {len(pairs)} cặp thật cùng nhóm "
              f"(Δnhãn thật {-dlab:+.3f})")
        if abs(dlab) < 0.15:
            print("    ⚠️ Δnhãn thật quá nhỏ ⇒ mẫu số bé, mọi tỉ lệ dưới KHÔNG đọc được.")
            print("       Nghĩa là: khống chế xong thì trục này gần như không còn")
            print("       liên hệ với nhãn — ĐÓ mới là kết quả.")
        blocks = {"TOÀN BỘ đặc trưng ⟨mốc trên⟩": cols,
                  f"khối {axis.lower()}": probes,
                  NEG + " ⟨đối chứng⟩": [NEG] if NEG in cols else []}
        for nm, blk in blocks.items():
            blk = [c for c in blk if c in cols]
            if not blk:
                continue
            Xp = X[cols].iloc[hi].copy().reset_index(drop=True)
            src = X[cols].iloc[lo].reset_index(drop=True)
            for c in blk:
                Xp[c] = src[c].values
            pr, cl = full.predict_proba(Xp), list(full.classes_)
            dm = float(np.mean(sum(pr[:, a] * k for a, k in enumerate(cl))
                               - base[hi]))
            share = dm / -dlab if abs(dlab) > 1e-9 else np.nan
            print(f"    {nm:34s} ΔE[y] {dm:+8.4f}   phần giải thích {share:6.1%}")
            resD[nm] = {"delta_model": dm, "share": float(share),
                        "n_pairs": len(pairs)}
    else:
        print(f"\n[3] chỉ {len(pairs)} cặp — không đủ để can thiệp, bỏ qua")
    return {"group": gname, "n_groups": int(len(set(g))),
            "fixed_effects": resA, "pair_test": resB, "intervention": resD}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="both")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--gap", type=float, default=1.0)
    ap.add_argument("--out", default="subjects/history/samples/axis_evidence.json")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    subs = ["physics", "history_gv"] if args.subject == "both" else [args.subject]

    out = {}
    for sub in subs:
        items, X, y, cfg = iv.featurize(sub)
        cols = iv.clean_cols(X, sub)
        full = XGBClassifier(**MK, random_state=args.seed).fit(X[cols], y)
        pr, cl = full.predict_proba(X[cols]), list(full.classes_)
        base = sum(pr[:, a] * k for a, k in enumerate(cl))
        print("\n" + "=" * 78)
        print(f"{sub} · n={len(y)} · {len(cols)} cột sạch · nhãn GIÁO VIÊN")
        print("phân bố " + " ".join(f"{NAME[k]} {int((y == k).sum())}"
                                    for k in range(4)))
        print("=" * 78)
        out[sub] = {a: run_axis(a, c, items, X, y, cols, full, base, args.gap, rng)
                    for a, c in AXES.items()}
    Path(args.out).write_text(
        json.dumps({"seed": args.seed, "gap": args.gap, "results": out},
                   ensure_ascii=False, indent=2, default=float),
        encoding="utf-8")
    print(f"\n→ {args.out}")


if __name__ == "__main__":
    main()
