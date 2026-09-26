# -*- coding: utf-8 -*-
"""Chạy một chế độ của xai_difficulty cho CẢ HAI mảng — gói cho reproduce_all.py.

Dùng:  python tools/_run_xai.py <coverage|selective|recourse>
"""
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Mỗi mô hình nền ghi ra một hậu tố riêng để bốn bộ kết quả sống song song
# (xem tools/text_backend.py). Đọc thẳng biến môi trường cho nhẹ, khỏi import.
SUF = {"xgb15": "", "text": "_pb", "tfidf": "_tf", "emb": "_eo"}[
    os.environ.get("QDE_BACKEND", "xgb15")]
OUT = {
    "coverage": [("physics", "subjects/physics/samples/xai_coverage.json", []),
                 ("history_gv", "subjects/history/samples/xai_coverage_gv.json", [])],
    "selective": [("physics", "subjects/physics/samples/xai_selective.json",
                   ["--n", "300", "--reps", "16"]),
                  ("history_gv", "subjects/history/samples/xai_selective_gv.json",
                   ["--n", "300", "--reps", "16"])],
    "recourse": [("physics", "subjects/physics/samples/xai_recourse.json",
                  ["--n", "250", "--reps", "16"]),
                 ("history_gv", "subjects/history/samples/xai_recourse_gv.json",
                  ["--n", "250", "--reps", "16"])],
}

mode = sys.argv[1]
for subj, out, extra in OUT[mode]:
    out = out[:-5] + SUF + ".json"
    r = subprocess.run([sys.executable, "tools/xai_difficulty.py", "--" + mode,
                        "--subject", subj, "--out", out] + extra,
                       cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode:
        sys.stderr.write(r.stderr or "")
        sys.exit(r.returncode)
    print(f"{mode} {subj} -> {out}")
