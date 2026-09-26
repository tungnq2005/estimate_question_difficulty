# -*- coding: utf-8 -*-
"""Giả thuyết ĐỘ PHÂN GIẢI: ontology không sai, chỉ thô hơn chính câu hỏi.

`docs/COUNTERFACTUAL_VALIDITY.md` §3.2 đo được: nhiễu THẬT do giáo viên viết đã
nằm ở 0,33 hop so với đáp án đúng — bốn phương án của một câu **sụp về cùng một
nút**. Giả thuyết rút ra: khoảng cách trên đồ thị không lay chuyển được dự đoán
KHÔNG phải vì ý tưởng sai, mà vì ontology **không đủ mịn để phân biệt các
phương án với nhau**.

Không thể làm ontology mịn hơn trong một buổi, nhưng CÓ THỂ làm nó **thô đi**
một cách có kiểm soát và đo **đường liều–đáp ứng**. Nếu độ phân giải đúng là
nút thắt thì:

    càng thô  ->  mô hình càng ít phản ứng với can thiệp khoảng cách

và ngoại suy ngược cho biết mịn hơn thì được gì. Thêm một **đầu mút phân giải
tối đa** (cosine PhoBERT giữa các phương án — phân biệt được MỌI phương án) để
có đầu trên của thang.

Thang phân giải:
    k=0   ontology hiện tại (319 nút)
    k=1   gộp mỗi nút với hàng xóm bán kính 1 thành siêu nút
    k=2   bán kính 2
    k=3   bán kính 3
    emb   cosine PhoBERT — phân giải tối đa, mọi phương án là một điểm riêng

Can thiệp được ĐỊNH NGHĨA CỐ ĐỊNH trên đồ thị mịn nhất (k=0) ở mọi mức, nên
"liều" không đổi; chỉ **độ phân giải của đặc trưng mô hình** thay đổi.

Chạy:  python tools/ontology_resolution.py [--subject physics] [--seed 42]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import t as tdist
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402

# Khối KG dùng cho THANG PHÂN GIẢI: chỉ giữ các đại lượng làm thô được trung
# thực trên đồ thị đã co (kể cả kad_path_distance_mean — đại lượng của giả
# thuyết gốc). jaccard_kg_*/rsi_dc dựa trên tập láng giềng thực thể, muốn làm
# thô đúng phải viết lại chúng — để ngoài, ghi rõ ở docs.
KG_COLS = ["kg_entity_match_coverage", "kg_num_correct", "kg_num_distractor",
           "kg_prereq_correct", "kg_prereq_distractor", "kg_centrality_mean",
           "kad_path_distance_mean"]
EMB_COLS = ["emb_sim_max", "emb_sim_mean", "emb_sim_spread", "emb_sim_stem"]
# chỉ giữ những nhánh cần cho thí nghiệm này + 1 mốc so sánh trục thao tác
ARMS: list = []   # điền trong main() theo trục bề mặt của môn
KG_ARMS = ["kg_near", "kg_far", "placebo_ent"]


# ----------------------------------------------------------------------
# Làm thô ontology: phủ bi bán kính k, tất định
# ----------------------------------------------------------------------
def coarsen(engine: OntologyEngine, k: int):
    und = engine.nx_graph.to_undirected(as_view=True)
    if k <= 0:
        node_of = {n: n for n in und.nodes()}
        return node_of, nx.Graph(und)

    order = sorted(und.nodes(), key=lambda n: (-und.degree(n), n))
    node_of: dict[str, str] = {}
    for centre in order:
        if centre in node_of:
            continue
        ball = nx.single_source_shortest_path_length(und, centre, cutoff=k)
        for m in ball:
            node_of.setdefault(m, centre)

    G = nx.Graph()
    G.add_nodes_from(set(node_of.values()))
    for u, v in und.edges():
        a, b = node_of[u], node_of[v]
        if a != b:
            G.add_edge(a, b)
    return node_of, G


def super_depth(engine: OntologyEngine, node_of: dict) -> dict:
    """Độ sâu tiên quyết của siêu nút = độ sâu NHỎ NHẤT trong các nút thành viên."""
    out: dict[str, int] = {}
    for uri, sup in node_of.items():
        d = engine.prerequisite_depth(uri)
        if sup not in out or d < out[sup]:
            out[sup] = d
    return out


# ----------------------------------------------------------------------
# Đặc trưng KG ở một mức phân giải, tính từ danh sách thực thể ĐÃ cache
# ----------------------------------------------------------------------
def graph_metrics(G: nx.Graph):
    """all-pairs hop + đường kính + degree-centrality TRÊN ĐỒ THỊ ĐÃ CO."""
    dist = {n: dict(nx.single_source_shortest_path_length(G, n)) for n in G}
    finite = [d for src in dist.values() for d in src.values() if d > 0]
    diam = max(finite) if finite else 1
    n = max(1, G.number_of_nodes() - 1)
    cent = {v: G.degree(v) / n for v in G}
    return dist, float(diam), cent


def kg_features(ents_per_option: list[tuple], node_of: dict, depth_of: dict,
                dist: dict, diam: float, cent: dict) -> dict:
    sup = [{node_of[e.uri] for e in group if e.uri in node_of}
           for group in ents_per_option]
    d_correct = [depth_of[s] for s in sup[0]]
    d_dist = [depth_of[s] for group in sup[1:] for s in group]
    n_dist = max(1, len(sup) - 1)
    allc = [cent.get(s, 0.0) for g in sup for s in g]
    # kad_path_distance_mean, chuẩn hoá theo đường kính — như engine.path_distance
    pd_ = [dist.get(a, {}).get(b, diam) / diam
           for a in sup[0] for g in sup[1:] for b in g]
    return {
        "kg_entity_match_coverage": sum(1 for s in sup if s) / len(sup),
        "kg_num_correct": len(sup[0]),
        "kg_num_distractor": sum(len(s) for s in sup[1:]) / n_dist,
        "kg_prereq_correct": (sum(d_correct) / len(d_correct)) if d_correct else 0.0,
        "kg_prereq_distractor": (sum(d_dist) / len(d_dist)) if d_dist else 0.0,
        "kg_centrality_mean": float(np.mean(allc)) if allc else 0.0,
        "kad_path_distance_mean": float(np.mean(pd_)) if pd_ else np.nan,
    }


def emb_features(embed, stem: str, opts: list[str]) -> dict:
    """Đầu mút phân giải tối đa: mỗi phương án là một điểm riêng trong không gian."""
    vs = [embed(o) for o in opts]
    sv = embed(stem)

    def cos(a, b):
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        return float(a @ b / (na * nb)) if na and nb else 0.0

    sims = [cos(vs[0], v) for v in vs[1:]]
    return {
        "emb_sim_max": max(sims) if sims else 0.0,
        "emb_sim_mean": float(np.mean(sims)) if sims else 0.0,
        "emb_sim_spread": float(np.std(sims)) if sims else 0.0,
        "emb_sim_stem": cos(sv, vs[0]),
    }


# ----------------------------------------------------------------------
# Dự đoán theo lô, dùng đúng mô hình out-of-fold của từng câu
# ----------------------------------------------------------------------
def predict_expected(model_of: dict, rows: list[dict], items_idx: list[int], cols):
    df = pd.DataFrame(rows)[cols]
    out = np.zeros(len(rows))
    by_model: dict[int, list[int]] = {}
    for r, i in enumerate(items_idx):
        by_model.setdefault(id(model_of[i]), []).append(r)
    for _, rs in by_model.items():
        m = model_of[items_idx[rs[0]]]
        proba = m.predict_proba(df.iloc[rs])
        out[rs] = proba @ np.arange(proba.shape[1])
    return out


def ols(X: np.ndarray, y: np.ndarray):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    s2 = resid @ resid / dof
    se = np.sqrt(np.diag(s2 * np.linalg.pinv(X.T @ X)))
    tv = np.divide(beta, se, out=np.zeros_like(beta), where=se > 0)
    p = 2 * (1 - tdist.cdf(np.abs(tv), dof))
    return beta, se, tv, p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="physics")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--no-emb", action="store_true",
                    help="bỏ đầu mút PhoBERT (chạy nhanh, chỉ thang đồ thị)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    eng = OntologyEngine.for_subject(cv.ontology_of(args.subject))
    cfg = cv.SUBJECTS[args.subject]
    global ARMS, SURFACE_COLS, SURF_ARM
    SURFACE_COLS = cv.SURFACE_COLS[cfg["surface"]]
    SURF_ARM = cv.arms_for(cfg["surface"])[0][0]      # nhánh bề mặt "down"
    ARMS = [("kg_near", +1), ("kg_far", -1), ("placebo_ent", 0), (SURF_ARM, -1)]
    fz = cv.Featurizer(eng, cfg["surface"])     # dùng làm cache trích thực thể
    items = cv.load_items(args.subject)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    print(f"Ontology {args.subject}: {len(eng)} thực thể, "
          f"{eng.nx_graph.number_of_edges()} cạnh | {len(items)} câu\n")

    # ---------- 1) dựng TOÀN BỘ biến thể (gốc + phản thực), một lần ----------
    hops = cv.all_pairs_hops(eng)
    pool = cv.DonorPool(items, fz)
    correct_uris = [{e.uri for e in fz.entities(q["correct"])} for q in items]

    variants = []   # {arm,item,stem,correct,distractors,hop_new}
    for i, q in enumerate(items):
        variants.append({"arm": "base", "item": i, "stem": q["stem"],
                         "correct": q["correct"], "distractors": q["distractors"],
                         "hop_new": np.nan})
    for arm, _ in ARMS:
        for i, q in enumerate(items):
            cf = cv.make_counterfactual(arm, q, i, pool, hops, correct_uris[i], rng)
            if cf is None:
                continue
            new_d, slot, donor = cf
            variants.append({
                "arm": arm, "item": i, "stem": q["stem"], "correct": q["correct"],
                "distractors": new_d,
                "hop_new": cv.min_hop(correct_uris[i],
                                      {e.uri for e in fz.entities(donor)}, hops),
            })
    print(f"{len(variants)} biến thể (1 gốc + {len(variants)-len(items)} phản thực)")

    # ---------- 2) phần KHÔNG phụ thuộc độ phân giải: numeric + thực thể ----------
    num_cache: dict[tuple, dict] = {}
    for v in variants:
        key = (v["stem"], v["correct"], tuple(v["distractors"]))
        if key not in num_cache:
            num_cache[key] = fz.surface_features(
                v["stem"], v["correct"], list(v["distractors"]),
                list(fz.entities(v["stem"])))
        v["_key"] = key
        v["_ents"] = [fz.entities(o) for o in
                      [v["correct"]] + list(v["distractors"])]
    print(f"{len(num_cache)} tổ hợp phương án khác nhau, "
          f"{len(fz._ent_cache)} văn bản đã trích thực thể")

    # ---------- 3) chạy từng mức phân giải ----------
    levels = [("k=0", 0), ("k=1", 1), ("k=2", 2), ("k=3", 3)]
    results = {}
    rows_out = []

    for name, k in levels:
        node_of, G = coarsen(eng, k)
        depth_of = super_depth(eng, node_of)
        dist, diam, cent = graph_metrics(G)
        n_super = len(set(node_of.values()))

        # độ phân giải TRONG CÂU: bốn phương án có tách nhau ra không
        sep, distinct = [], []
        for i, q in enumerate(items):
            sup = [{node_of[e.uri] for e in g if e.uri in node_of}
                   for g in variants[i]["_ents"]]
            distinct.append(len(set().union(*sup)) if any(sup) else 0)
            sep.append(bool(sup[0]) and any(s and not (s & sup[0]) for s in sup[1:]))
        res_sep, res_distinct = float(np.mean(sep)), float(np.mean(distinct))

        feats = [dict(num_cache[v["_key"]],
                      **kg_features(v["_ents"], node_of, depth_of,
                                    dist, diam, cent))
                 for v in variants]
        cols = SURFACE_COLS + KG_COLS
        results[name] = run_level(name, feats, variants, cols, y, args.seed,
                                  n_super, res_sep, res_distinct, rows_out)
        if k == 0:
            separable_at_k0 = list(sep)

    # ---------- 4) đầu mút phân giải tối đa: PhoBERT ----------
    if not args.no_emb:
        # Chú ý: KHÔNG dùng EntityEmbeddingCache.save/load — chúng chỉ lưu
        # `entity_embeddings` (do precompute_all sinh), còn embed_text chạy qua
        # lru_cache(maxsize=1000) nên vừa không ra đĩa được vừa bị đẩy khỏi cache
        # khi số văn bản > 1000. Ở đây tự giữ một dict tường minh và tự lưu.
        texts = sorted({t for v in variants
                        for t in [v["stem"], v["correct"], *v["distractors"]]})
        cpath = Path(f".cache/{args.subject}_mcq_option_emb.npz")
        cpath.parent.mkdir(exist_ok=True)
        vecs: dict[str, np.ndarray] = {}
        if cpath.exists():
            z = np.load(cpath, allow_pickle=False)
            keys, mat = list(z["keys"]), z["vecs"]
            vecs = {k: mat[r] for r, k in enumerate(keys)}
            print(f"\n[emb] nạp lại {len(vecs)} vector từ {cpath}")
        todo = [t for t in texts if t not in vecs]
        if todo:
            from shared.mcq.embedding_cache import EntityEmbeddingCache
            cache = EntityEmbeddingCache()
            print(f"[emb] nhúng {len(todo)} văn bản mới bằng PhoBERT…")
            for t in todo:
                vecs[t] = cache.embed_text(t)
            keys = sorted(vecs)
            np.savez_compressed(cpath, keys=np.array(keys, dtype=object).astype(str),
                                vecs=np.stack([vecs[k] for k in keys]))
            print(f"[emb] đã lưu {len(vecs)} vector → {cpath}")
        feats = [dict(num_cache[v["_key"]],
                      **emb_features(vecs.__getitem__, v["stem"],
                                     [v["correct"]] + list(v["distractors"])))
                 for v in variants]
        cols = SURFACE_COLS + EMB_COLS
        results["emb"] = run_level("emb", feats, variants, cols, y, args.seed,
                                   None, 1.0, 4.0, rows_out)

    # ---------- 5) bảng thang phân giải ----------
    print("\n" + "=" * 84)
    print("THANG ĐỘ PHÂN GIẢI — mô hình phản ứng với can thiệp khoảng cách mạnh cỡ nào")
    print("=" * 84)
    print(f"{'mức':6s} {'#nút':>6s} {'tách được':>10s} {'#nút/câu':>9s} "
          f"{'hệ số hop':>10s} {'p':>9s} {'|Δ| nhánh KG':>13s} {'|Δ| bề mặt':>13s}")
    for name in results:
        r = results[name]
        ns = "—" if r["n_nodes"] is None else str(r["n_nodes"])
        print(f"{name:6s} {ns:>6s} {r['res_separable']:9.1%} "
              f"{r['res_distinct']:9.2f} {r['hop_coef']:10.5f} {r['hop_p']:9.3g} "
              f"{r['kg_arm_abs_delta']:13.4f} {r['surf_arm_abs_delta']:13.4f}")
    print("\n'tách được' = tỉ lệ câu mà đáp án đúng và ít nhất 1 nhiễu rơi vào "
          "HAI nút khác nhau.\n'hệ số hop' = Δ E[y] mỗi hop, cùng một can thiệp "
          "ở mọi mức (liều không đổi).")

    # ---------- 6) phân tầng: ontology ĐÃ tách được phương án thì sao? ----------
    # Đây là phiên bản trực tiếp nhất của giả thuyết, đo ngay trên dữ liệu thật
    # thay vì ngoại suy từ đường làm-thô.
    print("\n" + "=" * 84)
    print("PHÂN TẦNG THEO ĐỘ PHÂN GIẢI SẴN CÓ (mức k=0)")
    print("=" * 84)
    strat = {}
    all_rows = pd.concat(rows_out, ignore_index=True)
    kg0 = all_rows[(all_rows.level == "k=0") & all_rows.arm.isin(KG_ARMS)].copy()
    kg0["hop_eff"] = kg0.hop.fillna(8.0)
    kg0["separable"] = kg0.item.map(lambda i: separable_at_k0[i])
    print(f"{'nhóm câu':34s} {'n':>6s} {'hệ số hop':>10s} {'SE':>8s} {'p':>10s}")
    for flag, lab in ((True, "ontology TÁCH được phương án"),
                      (False, "bốn phương án SỤP về một nút")):
        s = kg0[kg0.separable == flag]
        if len(s) < 30:
            continue
        Xr = np.column_stack([np.ones(len(s)), s.hop_eff.values])
        b, se, tv, p = ols(Xr, s.delta.values)
        print(f"{lab:34s} {len(s):6d} {b[1]:10.5f} {se[1]:8.5f} {p[1]:10.3g}")
        strat["separable" if flag else "collapsed"] = {
            "n": int(len(s)), "hop_coef": float(b[1]),
            "hop_se": float(se[1]), "hop_p": float(p[1])}
    if len(strat) == 2:
        d = strat["separable"]["hop_coef"] - strat["collapsed"]["hop_coef"]
        sed = float(np.hypot(strat["separable"]["hop_se"],
                             strat["collapsed"]["hop_se"]))
        z = d / sed if sed else 0.0
        print(f"\nchênh hai nhóm = {d:+.5f} (SE {sed:.5f}, z = {z:+.2f})")
        print("Giả thuyết độ phân giải dự đoán chênh này ÂM RÕ "
              "(nhóm tách được nhạy hơn).")
        strat["difference"] = {"diff": float(d), "se": sed, "z": float(z)}

    out = args.out or cv.out_path(args.subject, "ontology_resolution")
    Path(out).write_text(json.dumps(
        {"subject": args.subject, "seed": args.seed, "levels": results,
         "stratified_k0": strat},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {out}")


def run_level(name, feats, variants, cols, y, seed, n_nodes,
              res_sep, res_distinct, rows_out):
    """Huấn luyện out-of-fold ở một mức phân giải rồi đo phản ứng phản thực."""
    base_idx = [r for r, v in enumerate(variants) if v["arm"] == "base"]
    X = pd.DataFrame([feats[r] for r in base_idx])[cols]

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    model_of = {}
    for tr, te in skf.split(X, y):
        m = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                          subsample=0.8, colsample_bytree=0.8, random_state=seed,
                          eval_metric="mlogloss", verbosity=0)
        m.fit(X.iloc[tr], y[tr])
        for i in te:
            model_of[int(i)] = m

    base_pred = predict_expected(model_of, [feats[r] for r in base_idx],
                                 list(range(len(base_idx))), cols)

    recs = []
    for arm, promise in ARMS:
        idx = [r for r, v in enumerate(variants) if v["arm"] == arm]
        if not idx:
            continue
        its = [variants[r]["item"] for r in idx]
        pred = predict_expected(model_of, [feats[r] for r in idx], its, cols)
        for r, i, p in zip(idx, its, pred):
            recs.append({"arm": arm, "item": i, "promise": promise,
                         "delta": p - base_pred[i],
                         "hop": variants[r]["hop_new"]})
    df = pd.DataFrame(recs)
    rows_out.append(df.assign(level=name))

    kg = df[df.arm.isin(KG_ARMS)].copy()
    kg["hop_eff"] = kg.hop.fillna(8.0)
    Xr = np.column_stack([np.ones(len(kg)), kg.hop_eff.values])
    beta, se, tv, p = ols(Xr, kg.delta.values)

    return {
        "n_nodes": n_nodes,
        "res_separable": res_sep,
        "res_distinct": res_distinct,
        "hop_coef": float(beta[1]), "hop_se": float(se[1]), "hop_p": float(p[1]),
        "kg_arm_abs_delta": float(kg.delta.abs().mean()),
        "surf_arm": SURF_ARM,
        "surf_arm_abs_delta": float(df[df.arm == SURF_ARM].delta.abs().mean()),
        "n_kg_cf": int(len(kg)),
    }


if __name__ == "__main__":
    main()
