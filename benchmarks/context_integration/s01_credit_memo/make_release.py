from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

if __package__:
    from .blind_export import export_variants
    from .release_bundle import build_release_bundle
    from .run import prepare_variants
else:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from benchmarks.context_integration.s01_credit_memo.blind_export import export_variants
    from benchmarks.context_integration.s01_credit_memo.release_bundle import build_release_bundle
    from benchmarks.context_integration.s01_credit_memo.run import prepare_variants


def _is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False


def build_release(handbook_dir: str | Path, release_dir: str | Path, private_manifest: str | Path) -> list[Path]:
    handbook = Path(handbook_dir).resolve()
    release = Path(release_dir).resolve()
    manifest = Path(private_manifest).resolve()

    if _is_relative_to(manifest, release):
        raise ValueError("private manifest must be outside the release directory")

    with tempfile.TemporaryDirectory(prefix="s01-release-build-") as td:
        scratch = Path(td)
        generated = scratch / "generated"
        public = scratch / "public"
        temp_manifest = scratch / "mapping.json"

        prepare_variants(handbook, generated)
        export_variants(generated, public, temp_manifest)
        assets = build_release_bundle(public, release)

        raw = json.loads(temp_manifest.read_text(encoding="utf-8"))
        release_files = {
            f"{job_name}.zip": record["condition"]
            for job_name, record in raw["runs"].items()
        }

    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps({"release_files": release_files}, indent=2) + "\n",
        encoding="utf-8",
    )
    return assets


def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Build four anonymous S01 ZIP files ready to upload to a GitHub Release"
    )
    parser.add_argument("--handbook", required=True, help="Path to a local surge-ai/handbook checkout")
    parser.add_argument("--release-output", required=True, help="Output directory for public ZIP assets")
    parser.add_argument(
        "--private-manifest",
        required=True,
        help="Private ZIP-to-condition mapping; keep outside the release directory",
    )
    args = parser.parse_args()

    assets = build_release(args.handbook, args.release_output, args.private_manifest)
    for asset in assets:
        print(asset)
    print(Path(args.release_output).resolve() / "SHA256SUMS.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
