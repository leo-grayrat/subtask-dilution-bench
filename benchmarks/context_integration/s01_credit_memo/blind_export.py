from __future__ import annotations

import argparse
import json
import secrets
import shutil
from pathlib import Path

VARIANT_NAMES = ("local_A", "local_B", "full_A", "full_B")
TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".py"}
FORBIDDEN_MARKERS = (
    "benchmark",
    "context_integration",
    "context-integration",
    "s01_credit_memo",
    "s02_manager_approval",
    "s04_contact_history",
    "s07_beneficiary_survival",
    "s08_expired_agreement",
    "s09_reversed_deal",
    "s10_store_order",
    "pilot-samples",
    "quality-audit",
    "rubrics.json",
    "scorer.py",
    "result_scorer.py",
    "materialize.py",
    "variant_a",
    "variant_b",
    "local_a",
    "local_b",
    "full_a",
    "full_b",
)


class LeakageError(RuntimeError):
    pass


def _is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False


def _copy_model_visible(task_dir: Path, dest: Path) -> None:
    required = {
        "SYSTEM.md": task_dir / "system_prompt.md",
        "WORK_ORDER.md": task_dir / "instruction.md",
    }
    for out_name, src in required.items():
        if not src.is_file():
            raise FileNotFoundError(src)
        shutil.copy2(src, dest / out_name)

    dir_map = {
        "workspace": task_dir / "environment" / "initial_workspace",
        "services": task_dir / "environment" / "initial_external_services",
    }
    for out_name, src in dir_map.items():
        if not src.is_dir():
            raise FileNotFoundError(src)
        shutil.copytree(src, dest / out_name)


def scan_public_package(package_dir: str | Path) -> None:
    package = Path(package_dir)
    for path in package.rglob("*"):
        rel = str(path.relative_to(package)).replace("\\", "/").lower()
        for marker in FORBIDDEN_MARKERS:
            if marker in rel:
                raise LeakageError(f"forbidden marker in public path: {rel}")
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8").lower()
        except UnicodeDecodeError:
            continue
        for marker in FORBIDDEN_MARKERS:
            if marker in text:
                raise LeakageError(f"forbidden marker in public file {rel}: {marker}")


def export_one(task_dir: str | Path, public_root: str | Path, *, run_id: str | None = None) -> Path:
    source = Path(task_dir).resolve()
    root = Path(public_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    run_id = run_id or f"job-{secrets.token_hex(6)}"
    if any(part.lower() in {"local_a", "local_b", "full_a", "full_b"} for part in Path(run_id).parts):
        raise ValueError("public run_id must not reveal experimental condition")
    dest = root / run_id
    if dest.exists():
        raise FileExistsError(dest)
    dest.mkdir()
    try:
        _copy_model_visible(source, dest)
        scan_public_package(dest)
    except Exception:
        shutil.rmtree(dest, ignore_errors=True)
        raise
    return dest


def export_variants(generated_root: str | Path, public_root: str | Path, manifest_path: str | Path) -> dict[str, Path]:
    generated = Path(generated_root).resolve()
    public = Path(public_root).resolve()
    manifest = Path(manifest_path).resolve()
    if _is_relative_to(manifest, public):
        raise ValueError("private manifest must be outside the public package root")

    exported: dict[str, Path] = {}
    records: dict[str, dict[str, str]] = {}
    for condition in VARIANT_NAMES:
        source = generated / condition
        if not source.is_dir():
            raise FileNotFoundError(source)
        package = export_one(source, public)
        exported[condition] = package
        records[package.name] = {
            "condition": condition,
            "source": str(source),
        }

    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"runs": records}, indent=2) + "\n", encoding="utf-8")
    return exported


def _main() -> int:
    parser = argparse.ArgumentParser(description="Export opaque model-visible S01 task packages")
    parser.add_argument("generated_root", help="Directory containing local_A/local_B/full_A/full_B")
    parser.add_argument("public_root", help="Directory containing only model-visible packages")
    parser.add_argument("manifest", help="Private condition mapping; must be outside public_root")
    args = parser.parse_args()
    exported = export_variants(args.generated_root, args.public_root, args.manifest)
    for package in exported.values():
        print(package)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
