from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from .materialize import materialize
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from benchmarks.context_integration.s07_beneficiary_survival.materialize import materialize


SOURCE_TASK = "insurance_vanguard_shield_mutual_82da8d17"


def prepare_variants(handbook_dir: str | Path, output_root: str | Path) -> dict[str, Path]:
    source = Path(handbook_dir) / "tasks" / SOURCE_TASK
    output = Path(output_root)
    variants = {}
    for mode in ("local", "full"):
        for variant in ("A", "B"):
            name = f"{mode}_{variant}"
            destination = output / name
            materialize(source, destination, mode=mode, variant=variant)
            variants[name] = destination
    return variants


def _main() -> int:
    parser = argparse.ArgumentParser(description="Prepare the four S07 HANDBOOK task variants")
    parser.add_argument("--handbook", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    variants = prepare_variants(Path(args.handbook).resolve(), Path(args.output).resolve())
    for name, path in variants.items():
        print(f"prepared {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
