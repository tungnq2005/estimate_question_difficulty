"""Build every subject ontology (.ttl + .owl) from its data/.

Usage:
    python tools/build_all.py
"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = ["physics", "math", "chemistry", "english",
            "geography", "literature", "history"]


def main():
    failures = []
    for s in SUBJECTS:
        build = REPO_ROOT / "subjects" / s / "build.py"
        print(f"\n{'=' * 55}\n=== Building {s} ===\n{'=' * 55}")
        result = subprocess.run([sys.executable, str(build)], cwd=str(REPO_ROOT))
        if result.returncode != 0:
            failures.append(s)

    print("\n" + "=" * 55)
    if failures:
        print(f"[FAILED] {', '.join(failures)}")
        sys.exit(1)
    print(f"[OK] Built {len(SUBJECTS)} subject ontologies.")


if __name__ == "__main__":
    main()
