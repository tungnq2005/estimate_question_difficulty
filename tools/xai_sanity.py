# -*- coding: utf-8 -*-
"""Kiểm tra tỉnh táo cho CHỨNG CHỈ TRỤC (bước B1 của lớp giải thích).

Hai phép, đều không cần người. Mỗi phép chạy lại đúng công cụ phản thực
(`tools/counterfactual_validity.py`) rồi chấm bằng ĐÚNG hàm chứng chỉ mà lớp
giải thích dùng (`xai_difficulty.certificate`) — không có luật chấm thứ hai.

  (1) XÁO NHÃN — Adebayo et al. 2018 ("Sanity Checks for Saliency Maps",
      NeurIPS; data randomization test). Mô hình học trên nhãn đã xáo không
      học được gì thật về mức nhận thức. Cổng đáng tin thì PHẢI trượt.
  (2) ĐỔI SEED — đổi cùng lúc cách chia lát, khởi tạo mô hình và cách rút
      donor. Chứng chỉ thật phải giữ nguyên.

Ba luật được chấm song song:
  CŨ     một nhánh bất kỳ vượt đối chứng ở p < 0,05 (Wilcoxon) và đúng hướng
  CHẶT   MỌI nhánh của trục vượt đối chứng, đúng hướng, VÀ vượt mô hình nhãn
         xáo ở p hoán vị < 0,05 (định ra trước khi chạy K = 39)
  NHÁNH  từng nhánh riêng: nhánh nào vượt đối chứng, đúng hướng, và vượt mô
         hình nhãn xáo — không gộp thành trục

p hoán vị = (1 + #{mô hình xáo có hiệu ứng theo hướng hứa ≥ thật}) / (K + 1).
Tỉ lệ cấp nhầm của mỗi luật đo bằng cách đem chính các mô hình nhãn xáo ra
chấm, mỗi mô hình so với K − 1 mô hình xáo còn lại (bỏ-một-ra).

Chạy:
    python tools/xai_sanity.py               # lần nào thiếu thì chạy, rồi tổng hợp
    python tools/xai_sanity.py --summary     # chỉ tổng hợp từ file đã có
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
sys.path.insert(0, "tools")
import counterfactual_validity as cv  # noqa: E402
import xai_difficulty as xd  # noqa: E402

SUBJECTS = ["physics", "history_gv"]
PERM_SEEDS = list(range(1, 40))     # K = 39 → p hoán vị nhỏ nhất = 1/40
REAL_SEEDS = [43, 44, 45]
OUT = xd.SANITY_PATH


def run_path(subject: str, tag: str) -> Path:
    d = Path(cv.out_path(subject, "counterfactual_validity")).parent / "sanity"
    # hậu tố backend nằm trong TÊN FILE: hai backend dùng chung thư mục sanity,
    # không có hậu tố thì lần chạy của backend này đè lên backend kia.
    return d / f"cf_{subject}_{tag}{cv.BACKEND_SUFFIX}.json"


def job(subject: str, seed: int, permute: bool):
    tag = f"perm{seed}" if permute else f"seed{seed}"
    out = run_path(subject, tag)
    if out.exists():
        return subject, tag, "có sẵn", 0.0
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "tools/counterfactual_validity.py", "--subject",
           subject, "--seed", str(seed), "--out", str(out)]
    if permute:
        cmd.append("--permute-labels")
    # nhiều tiến trình chạy song song: giới hạn luồng XGBoost để khỏi tranh lõi
    env = dict(os.environ, OMP_NUM_THREADS="2", PYTHONIOENCODING="utf-8")
    t0 = time.time()
    r = subprocess.run(cmd, env=env, capture_output=True, text=True,
                       encoding="utf-8")
    dt = time.time() - t0
    if r.returncode != 0:
        return subject, tag, "LỖI: " + r.stderr[-400:], dt
    return subject, tag, "xong", dt


def run_all(workers: int):
    jobs = [(s, k, True) for s in SUBJECTS for k in PERM_SEEDS] + \
           [(s, k, False) for s in SUBJECTS for k in REAL_SEEDS]
    todo = [j for j in jobs
            if not run_path(j[0], f"{'perm' if j[2] else 'seed'}{j[1]}").exists()]
    print(f"{len(jobs)} lần chạy phản thực ({len(todo)} còn thiếu), "
          f"{workers} tiến trình song song", flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(job, *j) for j in todo]
        for f in as_completed(futs):
            s, tag, st, dt = f.result()
            print(f"  {s:11s} {tag:7s} {st}  ({dt:.0f}s)", flush=True)
    print(f"tổng thời gian {time.time() - t0:.0f}s\n")


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def arm_diffs(cf: dict) -> dict:
    return {a: v["vs_control_diff"] for a, v in cf["arms"].items()
            if isinstance(v, dict) and "promise" in v
            and v.get("vs_control_diff") is not None}


def arm_table(cert: dict) -> dict:
    return {r["arm"]: {"axis": ax, "promise": r["promise"],
                       "vs_control": r["vs_control"], "p": r["p"],
                       "p_perm": r["p_perm"], "ok": r["ok"]}
            for ax, v in cert["axes"].items() for r in v["arms"]}


def row(kind: str, seed: int, cert: dict) -> dict:
    ax = cert.get("axes", {})
    return {"labels": kind, "seed": seed,
            "legacy": [a for a, v in ax.items() if v["certified_legacy"]],
            "iut": [a for a, v in ax.items() if v["certified_iut"]],
            "arms_ok": [x for v in ax.values() for x in v["certified_arms"]],
            "arms": arm_table(cert)}


def fmt(xs) -> str:
    return ", ".join(xs) or "—"


def summarize() -> dict:
    res = {}
    for s in SUBJECTS:
        real_cf = [(42, xd.load_json(cv.out_path(s, "counterfactual_validity")))]
        real_cf += [(k, load(run_path(s, f"seed{k}"))) for k in REAL_SEEDS
                    if run_path(s, f"seed{k}").exists()]
        perm_cf = [(k, load(run_path(s, f"perm{k}"))) for k in PERM_SEEDS
                   if run_path(s, f"perm{k}").exists()]
        perm_d = [arm_diffs(cf) for _, cf in perm_cf]
        arms = list(arm_diffs(real_cf[0][1]))
        null = {a: [d[a] for d in perm_d if a in d] for a in arms}

        real = [row("thật", k, xd.certificate(s, cf, null)) for k, cf in real_cf]
        perm = []
        for j, (k, cf) in enumerate(perm_cf):
            loo = {a: [d[a] for jj, d in enumerate(perm_d) if jj != j and a in d]
                   for a in arms}
            perm.append(row("XÁO", k, xd.certificate(s, cf, loo)))
        K = len(perm)
        fc = {"legacy": sum(bool(r["legacy"]) for r in perm),
              "iut": sum(bool(r["iut"]) for r in perm),
              "any_arm_calibrated": sum(bool(r["arms_ok"]) for r in perm),
              "by_arm": {a: sum(a in r["arms_ok"] for r in perm) for a in arms}}
        p_by_seed = {a: [r["arms"][a]["p_perm"] for r in real] for a in arms}
        robust = [a for a in arms if all(a in r["arms_ok"] for r in real)]

        print("=" * 100)
        print(f"KIỂM TRA TỈNH TÁO — CHỨNG CHỈ TRỤC | môn {s} | K = {K} mô hình nhãn xáo")
        print("=" * 100)
        print(f"  {'':6s}{'seed':>5s}  {'luật CŨ':12s}{'luật CHẶT':12s}{'NHÁNH đạt':20s}"
              + "".join(f"{a:>16s}" for a in arms))
        for r in real + perm[:3]:
            cells = []
            for a in arms:
                t = r["arms"][a]
                if t["vs_control"] is None:
                    cells.append("—")
                    continue
                pp = t["p_perm"]
                star = "*" if t["p"] is not None and t["p"] < 0.05 else " "
                cells.append(f"{t['vs_control']:+.4f}{star}"
                             f"{'' if pp is None else f' p{pp:.3f}'}")
            print(f"  {r['labels']:6s}{r['seed']:5d}  {fmt(r['legacy']):12s}"
                  f"{fmt(r['iut']):12s}{fmt(r['arms_ok']):20s}"
                  + "".join(f"{c:>16s}" for c in cells))
        if K > 3:
            print(f"  … còn {K - 3} mô hình nhãn xáo, xem {OUT}")
        print("  (ô = chênh so với đối chứng khớp, mức E[y]; * = Wilcoxon p < 0,05;"
              " p… = p hoán vị)")
        print()
        print(f"  cấp chứng chỉ cho mô hình NHÃN XÁO "
              f"(mỗi mô hình so với {K - 1} mô hình còn lại):")
        print(f"    luật CŨ    : {fc['legacy']}/{K}")
        print(f"    luật CHẶT  : {fc['iut']}/{K}")
        print(f"    theo NHÁNH : {fc['any_arm_calibrated']}/{K} có ít nhất một nhánh đạt"
              f"  ({' · '.join(f'{a} {n}' for a, n in fc['by_arm'].items())})")
        print(f"  dữ liệu thật qua {len(real)} seed:")
        for r in real:
            print(f"    seed {r['seed']:3d}: CŨ {fmt(r['legacy']):9s} "
                  f"CHẶT {fmt(r['iut']):9s} NHÁNH đạt {fmt(r['arms_ok'])}")
        print("  p hoán vị theo seed (42, 43, 44, 45):")
        for a in arms:
            print(f"    {a:10s} " + "  ".join("  —  " if p is None else f"{p:.3f}"
                                           for p in p_by_seed[a]))
        print(f"  nhánh đạt ở MỌI seed: {fmt(robust)}")
        print()
        res[s] = {"n_perm": K, "null": null, "false_cert": fc,
                  "real": {k: real[0][k] for k in ("legacy", "iut", "arms_ok")},
                  "seeds": [{k: r[k] for k in ("seed", "legacy", "iut", "arms_ok")}
                            for r in real],
                  "robust_arms": robust,
                  "p_perm": {a: real[0]["arms"][a]["p_perm"] for a in arms},
                  "p_perm_by_seed": p_by_seed,
                  "runs": real + perm}
    Path(OUT).write_text(json.dumps(res, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"→ {OUT}")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()
    if not args.summary:
        run_all(args.workers)
    summarize()


if __name__ == "__main__":
    main()
