# -*- coding: utf-8 -*-
"""Đổi mô hình nền thì 56 con số của đề tài đổi những gì.

Đọc hai bảng mốc đã đóng băng — `docs/results_frozen.json` (XGBoost trên 15 cột
viết tay) và `docs/results_frozen_pb.json` (PhoBERT đóng băng + 15 cột đó) — rồi
in ra bảng chênh lệch, sắp theo độ lớn. Bảng này là bằng chứng cho mục "đánh đổi"
trong docs/MODEL_UPGRADE.md: không con số nào được chọn sau khi nhìn kết quả,
vì cả 56 con số đều nằm trong danh sách trích dẫn có sẵn của reproduce_all.

Chạy:  python tools/backend_diff.py            # bảng đầy đủ
       python tools/backend_diff.py --md       # dán thẳng vào tài liệu
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
OLD = REPO / "docs" / "results_frozen.json"
NEW = REPO / "docs" / "results_frozen_pb.json"
EPS = 1e-9


def load(p: Path) -> dict:
    if not p.exists():
        sys.exit(f"chưa có {p.relative_to(REPO)} — chạy reproduce_all --freeze trước")
    return json.loads(p.read_text(encoding="utf-8"))


def rows():
    a, b = load(OLD), load(NEW)
    va, vb = a["values"], b["values"]
    out = []
    for k, x in va.items():
        y = vb.get(k)
        d = None
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            d = y - x
            if abs(d) < EPS:
                d = 0.0
        out.append((k, x, y, d))
    return out, a.get("frozen_at"), b.get("frozen_at")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="in ở dạng bảng markdown")
    ap.add_argument("--all", action="store_true", help="in cả những số không đổi")
    args = ap.parse_args()

    rs, ta, tb = rows()
    moved = [r for r in rs if r[3] is None or abs(r[3]) > EPS]
    same = len(rs) - len(moved)
    moved.sort(key=lambda r: -abs(r[3] or 0))
    show = rs if args.all else moved

    if args.md:
        print(f"<!-- sinh bởi tools/backend_diff.py · cũ {ta} · mới {tb} -->\n")
        print("| con số | 15 cột viết tay | PhoBERT + 15 cột | lệch |")
        print("|---|---:|---:|---:|")
        for k, x, y, d in show:
            f = lambda v: f"{v:.4f}" if isinstance(v, float) else str(v)
            print(f"| {k} | {f(x)} | {f(y)} | {d:+.4f} |" if d is not None
                  else f"| {k} | {f(x)} | {f(y)} | — |")
    else:
        print(f"cũ  {OLD.name}  đóng băng {ta}")
        print(f"mới {NEW.name}  đóng băng {tb}\n")
        for k, x, y, d in show:
            if isinstance(x, float) and isinstance(y, float):
                print(f"  {k[:58]:58s} {x:10.4f} → {y:10.4f}  {d:+.4f}")
            else:
                print(f"  {k[:58]:58s} {x} → {y}")
    print(f"\ngiữ nguyên {same}/{len(rs)} · đổi {len(moved)}/{len(rs)}")


if __name__ == "__main__":
    main()
