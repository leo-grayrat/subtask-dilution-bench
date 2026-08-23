from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

if __package__:
    from .materialize import materialize
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from benchmarks.context_integration.s01_credit_memo.materialize import materialize

SOURCE_TASK = "finance_meridian_partners_158b9045"


def prepare_variants(handbook_dir: str | Path, output_root: str | Path) -> dict[str, Path]:
    handbook = Path(handbook_dir)
    source = handbook / "tasks" / SOURCE_TASK
    output = Path(output_root)
    variants: dict[str, Path] = {}
    for mode in ("local", "full"):
        for variant in ("A", "B"):
            name = f"{mode}_{variant}"
            dest = output / name
            materialize(source, dest, mode=mode, variant=variant)
            variants[name] = dest
    return variants


def harbor_command(handbook_dir: str | Path, task_dir: str | Path, *, model: str, env_file: str | Path) -> list[str]:
    handbook = Path(handbook_dir)
    return [
        str(handbook / ".venv" / "bin" / "harbor"),
        "run",
        "-p",
        str(Path(task_dir)),
        "--agent-import-path",
        "agent_harness.openhands_agent:OpenHandsAgent",
        "-m",
        model,
        "-n",
        "1",
        "--env-file",
        str(Path(env_file)),
    ]


def _main() -> int:
    parser = argparse.ArgumentParser(description="Prepare and run the four S01 HANDBOOK task variants")
    parser.add_argument("--handbook", required=True, help="Path to a local surge-ai/handbook checkout")
    parser.add_argument("--output", required=True, help="Directory for generated S01 tasks")
    parser.add_argument("--model", help="Model name passed to Harbor")
    parser.add_argument("--env-file", help="HANDBOOK .env file; defaults to <handbook>/.env")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()

    handbook = Path(args.handbook).resolve()
    variants = prepare_variants(handbook, Path(args.output).resolve())
    for name, path in variants.items():
        print(f"prepared {name}: {path}")

    if args.prepare_only:
        return 0
    if not args.model:
        parser.error("--model is required unless --prepare-only is used")

    env_file = Path(args.env_file).resolve() if args.env_file else handbook / ".env"
    harbor = handbook / ".venv" / "bin" / "harbor"
    if not harbor.exists():
        raise FileNotFoundError(f"Harbor executable not found: {harbor}")
    if not env_file.exists():
        raise FileNotFoundError(f"env file not found: {env_file}")

    for name, task in variants.items():
        print(f"running {name}")
        subprocess.run(
            harbor_command(handbook, task, model=args.model, env_file=env_file),
            cwd=handbook,
            check=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
