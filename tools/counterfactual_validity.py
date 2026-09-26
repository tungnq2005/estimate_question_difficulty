# -*- coding: utf-8 -*-
"""Hiệu lực phản thực (counterfactual validity) của lời giải thích độ khó.

Câu hỏi: khi lời giải thích nói "câu này khó vì trục BỀ MẶT" hoặc "vì trục TRI
THỨC", ta can thiệp tối thiểu đúng trục đó thì dự đoán có dịch chuyển đúng
hướng không? Đây là cách kiểm lời giải thích KHÔNG cần người thật — thay cho
user study với giáo viên (nguồn lực đang bị chặn).

Chạy được cho HAI môn, cùng một thang nhãn 4 mức NB/TH/VD/VDC:
  physics  (tự nhiên) — 1.539 câu, nhãn giáo viên
  history  (xã hội)   — 2.137 câu canonical, nhãn llm_vote3

Thiết kế: mỗi can thiệp thay ĐÚNG MỘT phương án nhiễu bằng một nhiễu THẬT lấy
từ câu khác (donor), nên văn bản không rơi ra ngoài phân phối.

  <surf>_down / <surf>_up   can thiệp trục BỀ MẶT của môn đó
        physics: bỏ/thêm một nhiễu CÓ SỐ      (numeric_option_count, rho +0,47)
        history: rút ngắn/kéo dài một nhiễu   (len_dist_mean,        rho +0,54)
  kg_near     nhiễu mới cách đáp án đúng 1 hop      (hứa: khó lên — dễ nhầm)
  kg_far      nhiễu mới cách >=3 hop / rời mạch     (hứa: dễ đi  — dễ loại)
  placebo     nhiễu bất kỳ, khớp bề mặt             (hứa: ~0)
  placebo_ent như placebo nhưng donor buộc có thực thể — đối chứng KHỚP cho
              hai nhánh KG (placebo thường để lọt donor không thực thể nào,
              tự nó đã là một can thiệp KG)

Nhánh bề mặt là ĐỐI CHỨNG DƯƠNG: đã biết tương quan mạnh với nhãn. Nếu phép đo
không bắt được cả nhánh này thì phép đo hỏng, không phải KG hỏng.

Khối đặc trưng KG ở đây CÓ các đại lượng của giả thuyết gốc (Vinu 2015: "độ khó
= độ tương tự giữa đáp án đúng và nhiễu") — `kad_path_distance_mean`,
`jaccard_kg_*`, `rsi_dc`. Bản trước (theo tools/ablate_physics.py) thiếu cả ba,
nên kết luận cũ chưa kiểm đúng giả thuyết mình định bác.

Chạy:  python tools/counterfactual_validity.py --subject physics|history|history_gv
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.stats import spearmanr, t as tdist, wilcoxon
from sklearn.model_selection import StratifiedKFold
from xgboost import XGBClassifier

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from shared.mcq.jaccard import compute_jaccard_features  # noqa: E402
from shared.mcq.numeric_features import compute_numeric_features  # noqa: E402
from shared.mcq.ontology_bridge import OntologyEngine  # noqa: E402
from shared.mcq.rsi import compute_rsi_features  # noqa: E402

NUM_RE = re.compile(r"\d")
YEAR_RE = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")

# ----------------------------------------------------------------------
# Backend của HỆ THỐNG ĐƯỢC GIẢI THÍCH
# ----------------------------------------------------------------------
# "xgb15" (mặc định) — XGBoost trên 15 cột luật tay. Đây là mô hình sinh ra
#          toàn bộ bảng 56 số đang đóng băng; KHÔNG được đổi mặc định, nếu
#          không mọi con số đã trích dẫn sẽ không tái lập được.
# "text"  — PhoBERT đóng băng + đúng 15 cột đó (xem tools/text_backend.py).
# "tfidf" — TF-IDF từ + ký tự + đúng 15 cột đó.
# "emb"   — PhoBERT đóng băng, KHÔNG cột luật tay nào.
#          Bật bằng biến môi trường QDE_BACKEND=...; mỗi mô hình nền ghi ra một
#          hậu tố file riêng nên bốn bộ kết quả sống song song, không đè nhau.
# Bốn mô hình này xếp theo TỈ TRỌNG QUYẾT ĐỊNH NẰM NGOÀI CỘT ĐẶT TÊN ĐƯỢC
# (~0 % ở xgb15 → ~100 % ở emb). Chạy cùng một bộ tiêu chí trên cả bốn là cách
# kiểm xem kết luận của lớp giải thích là về PIPELINE hay chỉ về một mô hình.
# Các nghiên cứu mức ĐẶC TRƯNG (axis_evidence, operation_axis,
# label_source_axes, incremental_value) cố ý KHÔNG đổi theo công tắc này: chúng
# so các khối đặc trưng với nhau bằng một bộ phân loại chuẩn, không phải đo
# phản ứng của hệ thống được giải thích.
BACKENDS = {"xgb15": "", "text": "_pb", "tfidf": "_tf", "emb": "_eo"}
BACKEND = os.environ.get("QDE_BACKEND", "xgb15")
if BACKEND not in BACKENDS:
    sys.exit(f"QDE_BACKEND lạ: {BACKEND!r} (nhận: {', '.join(BACKENDS)})")
BACKEND_SUFFIX = BACKENDS[BACKEND]
# Mọi mô hình nền khác xgb15 đều là mô hình TUYẾN TÍNH trên biểu diễn văn bản,
# dùng chung text_backend.py và chung đường quy kết.
IS_TEXT = BACKEND != "xgb15"

SUBJECTS = {
    "physics": {
        "path": "subjects/physics/samples/mcq_kenhgiaovien.json",
        "label_field": "difficulty",
        "label_map": {"NB": 0, "TH": 1, "VD": 2, "VDC": 3},
        "surface": "numeric",
        "canonical_only": False,
        "label_by": "GIÁO VIÊN (ma trận đề kenhgiaovien)",
    },
    "history": {
        "path": "subjects/history/samples/mcq_crawled.json",
        "label_field": "difficulty_vn",
        "label_map": {"Nhận biết": 0, "Thông hiểu": 1,
                      "Vận dụng": 2, "Vận dụng cao": 3},
        "surface": "verbosity",
        "canonical_only": True,     # bắt buộc: 54,7% bộ crawl là bản sao
        "label_by": "LLM (llm_vote3)",
    },
    # CÙNG môn, CÙNG ontology, CÙNG pipeline — chỉ đổi NGUỒN NHÃN.
    # Đây là cặp đối chứng để tách "thuộc tính của độ khó" khỏi "thuộc tính của
    # cách gán nhãn": mọi chênh lệch giữa `history` và `history_gv` chỉ có thể
    # đến từ nhãn, vì không còn biến nào khác thay đổi.
    "history_gv": {
        "path": "subjects/history/samples/mcq_kenhgiaovien.json",
        "label_field": "difficulty_vn",
        "label_map": {"Nhận biết": 0, "Thông hiểu": 1,
                      "Vận dụng": 2, "Vận dụng cao": 3},
        "surface": "verbosity",
        "canonical_only": True,
        "require_answer": True,     # bỏ câu chưa/không có đáp án hợp lệ
        "ontology": "history",
        "out_dir": "subjects/history/samples",
        "out_suffix": "_gv",
        "label_by": "GIÁO VIÊN (ma trận đề kenhgiaovien)",
    },
}


def ontology_of(subject: str) -> str:
    """Tên ontology dùng cho môn — bộ nhãn GV dùng chung ontology với môn Sử."""
    return SUBJECTS[subject].get("ontology", subject)


def out_path(subject: str, name: str) -> str:
    cfg = SUBJECTS[subject]
    d = cfg.get("out_dir", f"subjects/{subject}/samples")
    return f"{d}/{name}{cfg.get('out_suffix', '')}{BACKEND_SUFFIX}.json"


LEVEL_NAME = ["NB", "TH", "VD", "VDC"]

SURFACE_COLS = {
    "numeric": ["num_answer_present", "num_mag_ratio", "num_recip_swap",
                "num_formula_family", "num_option_count"],
    "verbosity": ["len_correct", "len_stem", "len_dist_mean", "len_ratio",
                  "n_year_options"],
}
# Khối KG — CÓ đủ ba đại lượng của giả thuyết gốc (path distance, jaccard, rsi_dc)
KG_COLS = ["kg_entity_match_coverage", "kg_num_correct", "kg_num_distractor",
           "kg_prereq_correct", "kg_prereq_distractor", "kg_centrality_mean",
           "kad_path_distance_mean", "jaccard_kg_max", "jaccard_kg_mean",
           "rsi_dc"]


def model_cols(surface: str) -> list:
    """Cột đầu vào của hệ thống được giải thích, theo backend đang bật.

    Backend văn bản dùng ĐÚNG 15 cột này cộng thêm một cột số hiệu văn bản, nên
    định nghĩa trục BỀ MẶT / TRI THỨC và máy quy trách nhiệm theo cột không đổi.
    """
    cols = SURFACE_COLS[surface] + KG_COLS
    if IS_TEXT:
        import text_backend as tb
        cols = cols + [tb.TID_COL]
    return cols


def load_items(subject: str) -> list[dict]:
    cfg = SUBJECTS[subject]
    rows = json.loads(Path(cfg["path"]).read_text(encoding="utf-8"))
    if cfg["canonical_only"]:
        rows = [q for q in rows if q.get("is_canonical")]
    if cfg.get("require_answer"):
        # câu thiếu đáp án, hoặc trang nguồn in trùng phương án (không tồn tại
        # đáp án duy nhất) → loại, đừng để lọt vào đặc trưng nhiễu loạn
        rows = [q for q in rows
                if q.get("correct") and len(q.get("distractors") or []) == 3
                and not q.get("option_defect")]
    return rows


# ----------------------------------------------------------------------
# Đặc trưng
# ----------------------------------------------------------------------
class Featurizer:
    """Trích đặc trưng, cache theo văn bản (mỗi can thiệp chỉ đổi 1 phương án)."""

    def __init__(self, engine: OntologyEngine, surface: str = "numeric"):
        self.eng = engine
        self.surface = surface
        self._ent_cache: dict[str, tuple] = {}

    def entities(self, text: str) -> tuple:
        hit = self._ent_cache.get(text)
        if hit is None:
            hit = tuple(self.eng.extract_entities_from_text(text))
            self._ent_cache[text] = hit
        return hit

    def surface_features(self, stem, correct, distractors, stem_ents) -> dict:
        if self.surface == "numeric":
            nf = compute_numeric_features(stem, correct, list(distractors),
                                          stem_ents, self.eng)
            opts = [correct] + list(distractors)
            return {
                "num_answer_present": nf["numeric_answer_present"],
                "num_mag_ratio": nf["numeric_magnitude_ratio_to_correct"],
                "num_recip_swap": nf["numeric_reciprocal_swap_match"],
                "num_formula_family": nf["numeric_same_formula_family"],
                "num_option_count": sum(1 for o in opts if NUM_RE.search(o)),
            }
        dl = [len(d) for d in distractors] or [1]
        return {
            "len_correct": float(len(correct)),
            "len_stem": float(len(stem)),
            "len_dist_mean": float(np.mean(dl)),
            "len_ratio": len(correct) / max(1.0, float(np.mean(dl))),
            "n_year_options": sum(1 for o in [correct] + list(distractors)
                                  if YEAR_RE.search(o)),
        }

    def kg_features(self, stem, correct, distractors, stem_ents, ents) -> dict:
        eng = self.eng
        depth_c = [eng.prerequisite_depth(e.uri) for e in ents[0]]
        depth_d = [eng.prerequisite_depth(e.uri) for g in ents[1:] for e in g]
        cent = [eng.centrality(e.uri) for g in ents for e in g]
        pdist = [eng.path_distance(a.uri, b.uri)
                 for a in ents[0] for g in ents[1:] for b in g]
        jac = compute_jaccard_features(stem_ents, list(ents[0]),
                                       [list(g) for g in ents[1:]], eng)
        rsi = compute_rsi_features(stem, stem_ents, correct, list(ents[0]),
                                   list(distractors),
                                   [list(g) for g in ents[1:]], eng)
        return {
            "kg_entity_match_coverage": sum(1 for e in ents if e) / len(ents),
            "kg_num_correct": float(len(ents[0])),
            "kg_num_distractor": sum(len(g) for g in ents[1:]) / max(1, len(ents) - 1),
            "kg_prereq_correct": float(np.mean(depth_c)) if depth_c else 0.0,
            "kg_prereq_distractor": float(np.mean(depth_d)) if depth_d else 0.0,
            "kg_centrality_mean": float(np.mean(cent)) if cent else 0.0,
            "kad_path_distance_mean": float(np.mean(pdist)) if pdist else np.nan,
            "jaccard_kg_max": jac.get("jaccard_kg_max", np.nan),
            "jaccard_kg_mean": jac.get("jaccard_kg_mean", np.nan),
            "rsi_dc": rsi.get("rsi_dc", np.nan),
        }

    def __call__(self, stem: str, correct: str, distractors: list[str]) -> dict:
        stem_ents = list(self.entities(stem))
        ents = [self.entities(o) for o in [correct] + list(distractors)]
        row = dict(
            self.surface_features(stem, correct, distractors, stem_ents),
            **self.kg_features(stem, correct, distractors, stem_ents, ents),
        )
        if IS_TEXT:
            # Đăng ký văn bản của (câu dẫn + 4 phương án) và gắn số hiệu vào
            # hàng đặc trưng. Mọi can thiệp đều đi qua đây, nên văn bản phản
            # thực tự động được đăng ký theo.
            import text_backend as tb
            row[tb.TID_COL] = tb.register(tb.text_of(stem, correct, distractors))
        return row


# ----------------------------------------------------------------------
# Đồ thị
# ----------------------------------------------------------------------
def all_pairs_hops(engine: OntologyEngine) -> dict[str, dict[str, int]]:
    und = engine.nx_graph.to_undirected(as_view=True)
    return {n: dict(nx.single_source_shortest_path_length(und, n)) for n in und}


def min_hop(correct_uris: set, other_uris: set, hops) -> float:
    best = None
    for cu in correct_uris:
        src = hops.get(cu, {})
        for ou in other_uris:
            h = src.get(ou)
            if h is not None and (best is None or h < best):
                best = h
    return float(best) if best is not None else float("nan")


# ----------------------------------------------------------------------
# Mô hình out-of-fold
# ----------------------------------------------------------------------
def fit_out_of_fold(X: pd.DataFrame, y: np.ndarray, seed: int, cols=None,
                    backend: str | None = None):
    # `backend` ép một backend cụ thể bất kể công tắc — dùng cho các đại lượng
    # chẩn đoán về CỘT (ví dụ mô hình chỉ-KG), vốn phải giữ nguyên bộ phân loại
    # cũ thì mới so được với số đã công bố.
    if (backend or BACKEND) != "xgb15":
        import text_backend as tb
        return tb.fit_out_of_fold(X, y, seed, cols)
    cols = list(cols) if cols else list(X.columns)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    model_of = {}
    for tr, te in skf.split(X, y):
        m = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1,
                          subsample=0.8, colsample_bytree=0.8, random_state=seed,
                          eval_metric="mlogloss", verbosity=0)
        m.fit(X.iloc[tr][cols], y[tr])
        for i in te:
            model_of[int(i)] = m
    return model_of


def predict_expected(model_of, rows: list[dict], items_idx: list[int], cols):
    df = pd.DataFrame(rows)[list(cols)]
    out = np.zeros(len(rows))
    groups: dict[int, list[int]] = {}
    for r, i in enumerate(items_idx):
        groups.setdefault(id(model_of[i]), []).append(r)
    for _, rs in groups.items():
        proba = model_of[items_idx[rs[0]]].predict_proba(df.iloc[rs])
        out[rs] = proba @ np.arange(proba.shape[1])
    return out


def expected_level(model, feat_row: dict, cols) -> float:
    proba = model.predict_proba(pd.DataFrame([feat_row])[list(cols)])[0]
    return float(np.dot(proba, np.arange(len(proba))))


# ----------------------------------------------------------------------
# Kho donor
# ----------------------------------------------------------------------
class DonorPool:
    def __init__(self, items, fz: Featurizer):
        seen = set()
        self.donors = []
        for qi, q in enumerate(items):
            for d in q["distractors"]:
                key = d.strip()
                if not key or key in seen:
                    continue
                seen.add(key)
                self.donors.append({
                    "text": d, "owner": qi,
                    "has_num": bool(NUM_RE.search(d)), "len": len(d),
                    "uris": {e.uri for e in fz.entities(d)},
                })
        self.by_uri = defaultdict(list)
        for j, dn in enumerate(self.donors):
            for u in dn["uris"]:
                self.by_uri[u].append(j)

    def candidates(self, *, has_num=None, length=None, tol=None,
                   len_range=None, exclude_owner=None, uris=None):
        pool = (range(len(self.donors)) if uris is None
                else sorted({j for u in uris for j in self.by_uri.get(u, [])}))
        if len_range is not None:
            lo, hi = len_range
        else:
            lo, hi = length * (1 - tol), length * (1 + tol)
        out = []
        for j in pool:
            dn = self.donors[j]
            if dn["owner"] == exclude_owner:
                continue
            if has_num is not None and dn["has_num"] != has_num:
                continue
            if not (lo <= dn["len"] <= hi):
                continue
            out.append(j)
        return out


LEN_TOL = 0.45          # ±45% độ dài cho các nhánh KG/placebo
LEN_FACTOR = 1.6        # nhánh bề mặt của Sử: dài gấp >=1,6 lần / ngắn <=1/1,6


def arms_for(surface: str):
    surf = ([("num_down", -1, "bỏ 1 nhiễu có số → trục thao tác nhẹ đi"),
             ("num_up", +1, "thêm 1 nhiễu có số → trục thao tác nặng lên")]
            if surface == "numeric" else
            [("len_down", -1, "rút ngắn 1 nhiễu → trục hành văn nhẹ đi"),
             ("len_up", +1, "kéo dài 1 nhiễu → trục hành văn nặng lên")])
    return surf + [
        ("kg_near", +1, "nhiễu cách đáp án 1 hop → dễ nhầm hơn"),
        ("kg_far", -1, "nhiễu cách đáp án ≥3 hop → dễ loại hơn"),
        ("placebo", 0, "thay nhiễu bất kỳ, khớp bề mặt → không hứa gì"),
        ("placebo_ent", 0, "như placebo nhưng donor buộc có thực thể"),
    ]


def make_counterfactual(arm, q, qi, pool, hops, correct_uris, rng):
    """(distractors_mới, slot bị thay, text donor) hoặc None nếu không dựng được."""
    dists = q["distractors"]
    if not dists:
        return None
    num_idx = [i for i, d in enumerate(dists) if NUM_RE.search(d)]
    plain_idx = [i for i, d in enumerate(dists) if not NUM_RE.search(d)]

    if arm == "num_down":
        if not num_idx:
            return None
        slot = num_idx[0]
        cands = pool.candidates(has_num=False, length=len(dists[slot]),
                                tol=LEN_TOL, exclude_owner=qi)
    elif arm == "num_up":
        if not plain_idx:
            return None
        slot = plain_idx[0]
        cands = pool.candidates(has_num=True, length=len(dists[slot]),
                                tol=LEN_TOL, exclude_owner=qi)
    elif arm == "len_up":
        slot = int(np.argmin([len(d) for d in dists]))
        L = len(dists[slot])
        cands = pool.candidates(has_num=bool(NUM_RE.search(dists[slot])),
                                len_range=(L * LEN_FACTOR, 10_000),
                                exclude_owner=qi)
    elif arm == "len_down":
        slot = int(np.argmax([len(d) for d in dists]))
        L = len(dists[slot])
        cands = pool.candidates(has_num=bool(NUM_RE.search(dists[slot])),
                                len_range=(0, L / LEN_FACTOR), exclude_owner=qi)
    elif arm in ("kg_near", "kg_far"):
        if not correct_uris:
            return None
        want_near = arm == "kg_near"
        target = set()
        for cu in correct_uris:
            src = hops.get(cu, {})
            for uri in pool.by_uri:
                h = src.get(uri)
                if want_near:
                    if h == 1:
                        target.add(uri)
                elif h is None or h >= 3:
                    target.add(uri)
        if not target:
            return None
        slot = 0
        cands = pool.candidates(has_num=bool(NUM_RE.search(dists[slot])),
                                length=len(dists[slot]), tol=LEN_TOL,
                                exclude_owner=qi, uris=target)
    elif arm == "placebo":
        slot = 0
        cands = pool.candidates(has_num=bool(NUM_RE.search(dists[slot])),
                                length=len(dists[slot]), tol=LEN_TOL,
                                exclude_owner=qi)
    elif arm == "placebo_ent":
        slot = 0
        cands = pool.candidates(has_num=bool(NUM_RE.search(dists[slot])),
                                length=len(dists[slot]), tol=LEN_TOL,
                                exclude_owner=qi, uris=set(pool.by_uri))
    else:
        raise ValueError(arm)

    if not cands:
        return None
    j = rng.choice(cands)
    new_d = list(dists)
    new_d[slot] = pool.donors[j]["text"]
    return new_d, slot, pool.donors[j]["text"]


def group_attribution(model_of, X: pd.DataFrame, cols, surf_cols):
    """|SHAP| trung bình trên các lớp, gộp theo nhóm bề mặt / KG, từng câu."""
    by_model = defaultdict(list)
    for i, m in model_of.items():
        by_model[id(m)].append(i)
    cols = list(cols)
    rows = {}
    if IS_TEXT:
        # Mô hình tuyến tính: quy kết tính thẳng từ hệ số, không cần TreeSHAP.
        for _, idxs in by_model.items():
            g = model_of[idxs[0]].contrib_rows(
                X.iloc[idxs], {"surface": surf_cols, "kg": KG_COLS})
            for r, i in enumerate(idxs):
                rows[i] = {"attr_surface": float(g["surface"][r]),
                           "attr_kg": float(g["kg"][r]),
                           "attr_text": float(g["__text__"][r])}
        out = pd.DataFrame.from_dict(rows, orient="index").sort_index()
        out["attr_kg_share"] = out.attr_kg / (out.attr_kg + out.attr_surface + 1e-12)
        return out
    i_surf = [cols.index(c) for c in surf_cols]
    i_kg = [cols.index(c) for c in KG_COLS]
    for _, idxs in by_model.items():
        m = model_of[idxs[0]]
        contrib = m.get_booster().predict(
            xgb.DMatrix(X.iloc[idxs][cols]), pred_contribs=True)
        if contrib.ndim == 2:
            contrib = contrib[:, None, :]
        for r, i in enumerate(idxs):
            c = contrib[r]
            rows[i] = {"attr_surface": float(np.abs(c[:, i_surf].sum(axis=1)).mean()),
                       "attr_kg": float(np.abs(c[:, i_kg].sum(axis=1)).mean())}
    out = pd.DataFrame.from_dict(rows, orient="index").sort_index()
    out["attr_kg_share"] = out.attr_kg / (out.attr_kg + out.attr_surface + 1e-12)
    return out


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = len(y) - X.shape[1]
    s2 = resid @ resid / dof
    se = np.sqrt(np.diag(s2 * np.linalg.pinv(X.T @ X)))
    tv = np.divide(beta, se, out=np.zeros_like(beta), where=se > 0)
    return beta, se, tv, 2 * (1 - tdist.cdf(np.abs(tv), dof))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", default="physics", choices=sorted(SUBJECTS))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=None)
    ap.add_argument("--permute-labels", action="store_true",
                    help="KIỂM TRA TỈNH TÁO: xáo nhãn trước khi huấn luyện")
    args = ap.parse_args()

    cfg = SUBJECTS[args.subject]
    surf_cols = SURFACE_COLS[cfg["surface"]]
    cols = model_cols(cfg["surface"])
    # Seed bốc DONOR tách khỏi seed mô hình. Mặc định trùng nhau (hành vi cũ).
    # Kiểm tra tỉnh táo của backend văn bản đặt QDE_DONOR_SEED=42 để 84 lần
    # chạy dùng CHUNG một bộ phản thực: mỗi bộ donor mới là ~5.000 văn bản phải
    # nhúng lại (~7 phút), 84 lần là hơn 10 giờ. Hệ quả phải khai khi viết: cả
    # phân bố rỗng lẫn các lần chạy thật đều bớt một nguồn nhiễu (donor), nên
    # phép so vẫn cùng điều kiện và phân bố rỗng HẸP hơn — tức phép thử nghiêm
    # hơn, không dễ hơn.
    donor_seed = int(os.environ.get("QDE_DONOR_SEED", args.seed))
    rng = random.Random(donor_seed)
    eng = OntologyEngine.for_subject(ontology_of(args.subject))
    fz = Featurizer(eng, cfg["surface"])
    items = load_items(args.subject)
    y = np.array([cfg["label_map"][q[cfg["label_field"]]] for q in items])
    if args.permute_labels:
        # Kiểm tra tỉnh táo (Adebayo et al. 2018, data randomization test): mô
        # hình học trên nhãn đã xáo thì không học được gì thật, nên cổng chứng
        # chỉ trục của lớp giải thích PHẢI trượt trên kết quả của lần chạy này.
        y = np.random.default_rng(args.seed).permutation(y)
        cfg = dict(cfg, label_by=f"{cfg.get('label_by', '?')} — NHÃN ĐÃ XÁO "
                                 f"(seed {args.seed}, kiểm tra tỉnh táo)")
    arms = arms_for(cfg["surface"])

    print(f"Môn {args.subject} | nhãn: {cfg.get('label_by', '?')}")
    desc = {"xgb15": "XGBoost trên 15 cột luật tay",
            "text": "PhoBERT đóng băng + 15 cột luật tay",
            "tfidf": "TF-IDF từ + ký tự + 15 cột luật tay",
            "emb": "PhoBERT đóng băng, KHÔNG cột luật tay"}[BACKEND]
    print(f"backend: {BACKEND} — {desc}"
          + (f", ghi ra *{BACKEND_SUFFIX}.json" if BACKEND_SUFFIX else ""))
    print(f"ontology {len(eng)} thực thể, {eng.nx_graph.number_of_edges()} cạnh")
    print(f"{len(items)} câu | phân bố " +
          ", ".join(f"{LEVEL_NAME[k]} {int((y == k).sum())}" for k in range(4)))
    print(f"trục bề mặt: {cfg['surface']} ({len(surf_cols)} cột) + KG "
          f"({len(KG_COLS)} cột, CÓ path distance / jaccard / rsi_dc)\n")

    base_feats = [fz(q["stem"], q["correct"], q["distractors"]) for q in items]
    X = pd.DataFrame(base_feats)[cols]
    model_of = fit_out_of_fold(X, y, args.seed, cols)
    base_pred = predict_expected(model_of, base_feats, list(range(len(items))), cols)
    model_kg = fit_out_of_fold(X, y, args.seed, KG_COLS, backend="xgb15")
    base_pred_kg = predict_expected(model_kg, base_feats,
                                    list(range(len(items))), KG_COLS)
    print(f"E[y] gốc: {base_pred.mean():.3f} (nhãn thật {y.mean():.3f})")

    hops = all_pairs_hops(eng)
    pool = DonorPool(items, fz)
    correct_uris = [{e.uri for e in fz.entities(q["correct"])} for q in items]
    print(f"Kho donor: {len(pool.donors)} nhiễu thật, "
          f"{len(pool.by_uri)} thực thể được nhắc tới\n")

    # Hai lượt: dựng hết phản thực rồi mới dự đoán MỘT LƯỢT. Thứ tự bốc donor
    # không đổi (vẫn cùng một `rng`, cùng thứ tự duyệt), nên kết quả y hệt cách
    # dự đoán từng câu — nhưng backend văn bản nhúng được theo lô thay vì từng
    # văn bản một, nhanh hơn hàng chục lần.
    pend = []
    for arm, promise, desc in arms:
        for i, q in enumerate(items):
            cf = make_counterfactual(arm, q, i, pool, hops, correct_uris[i], rng)
            if cf is None:
                continue
            new_d, slot, donor = cf
            pend.append((arm, promise, i, q, fz(q["stem"], q["correct"], new_d),
                         slot, donor))
    ey_cf = predict_expected(model_of, [p[4] for p in pend],
                             [p[2] for p in pend], cols)
    ey_cf_kg = predict_expected(model_kg, [p[4] for p in pend],
                                [p[2] for p in pend], KG_COLS)

    records = []
    for r_, (arm, promise, i, q, f_cf, slot, donor) in enumerate(pend):
        rec = {"arm": arm, "promise": promise, "item": i, "id": q["id"],
               "base": base_pred[i],
               "delta": float(ey_cf[r_]) - base_pred[i],
               "delta_kgonly": float(ey_cf_kg[r_]) - base_pred_kg[i],
               "hop_old": min_hop(correct_uris[i],
                                  {e.uri for e in fz.entities(q["distractors"][slot])},
                                  hops),
               "hop_new": min_hop(correct_uris[i],
                                  {e.uri for e in fz.entities(donor)}, hops)}
        for c in cols:
            if c.startswith("__"):
                continue
            rec["d_" + c] = f_cf[c] - base_feats[i][c]
        records.append(rec)
    df = pd.DataFrame(records)

    # ---------------- báo cáo ----------------
    print("=" * 80)
    print("HIỆU LỰC PHẢN THỰC — Δ E[y] (0=NB … 3=VDC)")
    print("=" * 80)
    print(f"{'nhánh':12s} {'n':>5s} {'hứa':>4s} {'Δ TB':>9s} {'Δ trung vị':>11s} "
          f"{'đúng hướng':>11s}")
    summary = {}
    for arm, promise, desc in arms:
        sub = df[df.arm == arm]
        if sub.empty:
            print(f"{arm:12s}     0  (không dựng được phản thực nào)")
            continue
        agree = ((np.sign(sub.delta) == promise).mean() if promise
                 else (sub.delta.abs() < 0.05).mean())
        print(f"{arm:12s} {len(sub):5d} {promise:+4d} {sub.delta.mean():9.4f} "
              f"{sub.delta.median():11.4f} {agree:10.1%}")
        summary[arm] = {"n": int(len(sub)), "promise": promise, "desc": desc,
                        "delta_mean": float(sub.delta.mean()),
                        "delta_median": float(sub.delta.median()),
                        "direction_agreement": float(agree),
                        "delta_kgonly_mean": float(sub.delta_kgonly.mean())}
    print("\n(placebo: 'đúng hướng' = tỉ lệ |Δ| < 0,05, tức ĐỨNG YÊN như hứa)")

    print("\n" + "=" * 80)
    print("SO VỚI ĐỐI CHỨNG KHỚP (Wilcoxon ghép cặp)")
    print("=" * 80)
    surf_arms = [a for a, _, _ in arms[:2]]
    ctrl_of = {surf_arms[0]: "placebo", surf_arms[1]: "placebo",
               "kg_near": "placebo_ent", "kg_far": "placebo_ent"}
    for arm, ctrl in ctrl_of.items():
        a_ = df[df.arm == arm].set_index("item").delta
        b_ = df[df.arm == ctrl].set_index("item").delta
        com = a_.index.intersection(b_.index)
        if len(com) < 10:
            continue
        _, p = wilcoxon(a_.loc[com], b_.loc[com])
        print(f"{arm:12s} n={len(com):5d} đc={ctrl:12s} Δ={a_.loc[com].mean():+.4f} "
              f"Δđc={b_.loc[com].mean():+.4f} chênh={(a_.loc[com]-b_.loc[com]).mean():+.4f} "
              f"p={p:.3g}")
        summary[arm].update(control_arm=ctrl,
                            vs_control_diff=float((a_.loc[com] - b_.loc[com]).mean()),
                            vs_control_p=float(p))

    print("\n" + "=" * 80)
    print("CAN THIỆP KG CÓ ĐÁP ĐÚNG ĐÍCH KHÔNG (hop đáp án ↔ nhiễu)")
    print("=" * 80)
    print(f"{'nhánh':12s} {'hop cũ':>8s} {'hop mới':>9s} {'rời mạch':>10s}")
    for arm, _, _ in arms:
        sub = df[df.arm == arm]
        if sub.empty:
            continue
        hn = sub.hop_new.dropna()
        print(f"{arm:12s} {sub.hop_old.mean():8.2f} "
              f"{(hn.mean() if len(hn) else float('nan')):9.2f} "
              f"{sub.hop_new.isna().mean():9.1%}")
        if arm in summary:
            summary[arm].update(
                hop_old_mean=float(sub.hop_old.mean()),
                hop_new_mean_measured=(float(hn.mean()) if len(hn) else None),
                frac_disconnected=float(sub.hop_new.isna().mean()))

    # ---- phép chính: khoảng cách có tác dụng riêng không ----
    print("\n" + "=" * 80)
    print("PHÉP CHÍNH — hồi quy Δ theo KHOẢNG CÁCH, kiểm soát MỌI đặc trưng khác")
    print("=" * 80)
    kg = df[df.arm.isin(["kg_near", "kg_far", "placebo_ent"])].copy()
    kg["hop_eff"] = kg.hop_new.fillna(8.0)
    ctrl_cols = ["d_" + c for c in cols
                 if c != "kad_path_distance_mean" and not c.startswith("__")]
    M = kg[ctrl_cols].fillna(0.0).values
    Xr = np.column_stack([np.ones(len(kg)), kg.hop_eff.values, M])
    beta, se, tv, p = ols(Xr, kg.delta.values)
    print(f"n = {len(kg)} phản thực; kiểm soát {len(ctrl_cols)} biến Δ đặc trưng")
    print(f"\n  hop (khoảng cách):  hệ số {beta[1]:+.5f}  SE {se[1]:.5f}  "
          f"t {tv[1]:+.2f}  p {p[1]:.3g}")
    print(f"  KTC 95%: {beta[1]-1.96*se[1]:+.5f} … {beta[1]+1.96*se[1]:+.5f}")
    summary["regression_hop_controlled"] = {
        "coef": float(beta[1]), "se": float(se[1]), "p": float(p[1]),
        "n": int(len(kg)), "n_controls": len(ctrl_cols)}
    sd = summary[surf_arms[0]]["delta_mean"]
    print(f"\n  Để so: nhánh {surf_arms[0]} làm E[y] đổi {sd:+.4f} mức.")

    # ---- quy kết vs can thiệp ----
    print("\n" + "=" * 80)
    print("QUY KẾT (SHAP) so với CAN THIỆP")
    print("=" * 80)
    attr = group_attribution(model_of, X, cols, surf_cols)
    print(f"|SHAP| nhóm bề mặt {attr.attr_surface.mean():.4f} | "
          f"nhóm KG {attr.attr_kg.mean():.4f} | "
          f"tỉ trọng KG {attr.attr_kg_share.mean():.1%}")
    pb_abs = df[df.arm == "placebo"].set_index("item").delta.abs()
    faith = {}
    for arm, group in ((surf_arms[0], "attr_surface"), ("kg_near", "attr_kg"),
                       ("kg_far", "attr_kg")):
        s = df[df.arm == arm].set_index("item").delta
        com = s.index.intersection(pb_abs.index)
        if len(com) < 30:
            continue
        resp = (s.loc[com].abs() - pb_abs.loc[com]).values
        a = attr.loc[com, group].values
        # Mô hình nền `emb` không nhận cột luật tay nào, nên quy kết cho mọi
        # khối đặt tên được đều bằng 0. "Quy kết có dự báo được can thiệp
        # không" khi ấy là câu hỏi KHÔNG ĐỊNH NGHĨA ĐƯỢC, chứ không phải bằng 0
        # — ghi ra đúng như vậy thay vì để NaN lọt vào file kết quả.
        if np.allclose(a, a[0]):
            print(f"{arm:12s} quy kết hằng số ({group} ≡ {a[0]:.3g}) — "
                  f"không định nghĩa được tương quan  n={len(com)}")
            faith[arm] = {"group": group, "spearman": None, "p": None,
                          "spearman_placebo_control": None, "n": int(len(com)),
                          "undefined": "quy kết hằng số: mô hình nền không dùng "
                                       "cột luật tay nào"}
            continue
        rho, pv = spearmanr(a, resp)
        rho_pb, _ = spearmanr(a, pb_abs.loc[com].values)
        print(f"{arm:12s} ρ(|SHAP|, phản ứng ròng) = {rho:+.3f} (p={pv:.2g})"
              f"   [đối chứng bão hoà {rho_pb:+.3f}]  n={len(com)}")
        faith[arm] = {"group": group, "spearman": float(rho), "p": float(pv),
                      "spearman_placebo_control": float(rho_pb), "n": int(len(com))}
    summary["attribution"] = {"surface": float(attr.attr_surface.mean()),
                              "kg": float(attr.attr_kg.mean()),
                              "kg_share": float(attr.attr_kg_share.mean())}
    if "attr_text" in attr:
        summary["attribution"]["text"] = float(attr.attr_text.mean())
    summary["faithfulness"] = faith

    out = args.out or out_path(args.subject, "counterfactual_validity")
    Path(out).write_text(json.dumps({
        "subject": args.subject, "label_by": cfg.get("label_by"),
        "backend": BACKEND, "seed": args.seed, "donor_seed": donor_seed,
        "n_items": len(items),
        "surface_kind": cfg["surface"], "surface_cols": surf_cols,
        "kg_cols": KG_COLS, "n_donors": len(pool.donors),
        "base_expected_level_mean": float(base_pred.mean()),
        "arms": summary,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {out}")


if __name__ == "__main__":
    main()
