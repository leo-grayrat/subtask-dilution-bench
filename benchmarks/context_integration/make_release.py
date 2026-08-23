from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Callable

from .s01_credit_memo.blind_export import export_one
from .s01_credit_memo.release_bundle import build_release_bundle
from .s02_manager_approval.run import prepare_variants as prepare_s02
from .s04_contact_history.run import prepare_variants as prepare_s04
from .s07_beneficiary_survival.run import prepare_variants as prepare_s07
from .s08_expired_agreement.run import prepare_variants as prepare_s08
from .s09_reversed_deal.run import prepare_variants as prepare_s09
from .s10_store_order.run import prepare_variants as prepare_s10


Builder = Callable[[str | Path, str | Path], dict[str, Path]]

SAMPLE_BUILDERS: dict[str, Builder] = {
    "approval_identity": prepare_s02,
    "contact_history": prepare_s04,
    "beneficiary_survival": prepare_s07,
    "expired_agreement": prepare_s08,
    "reversed_deal": prepare_s09,
    "store_order": prepare_s10,
}


def _is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False


def build_release(
    handbook_dir: str | Path,
    release_dir: str | Path,
    private_manifest: str | Path,
) -> list[Path]:
    handbook = Path(handbook_dir).resolve()
    release = Path(release_dir).resolve()
    manifest = Path(private_manifest).resolve()
    if _is_relative_to(manifest, release):
        raise ValueError("private manifest must be outside the release directory")

    records: dict[str, dict[str, str]] = {}
    with tempfile.TemporaryDirectory(prefix="context-release-build-") as td:
        scratch = Path(td)
        generated = scratch / "generated"
        public = scratch / "public"
        for sample, builder in SAMPLE_BUILDERS.items():
            variants = builder(handbook, generated / sample)
            if set(variants) != {"local_A", "local_B", "full_A", "full_B"}:
                raise RuntimeError(f"{sample} did not produce the four required conditions")
            for condition, task_dir in variants.items():
                package = export_one(task_dir, public)
                records[f"{package.name}.zip"] = {
                    "sample": sample,
                    "condition": condition,
                }
        assets = build_release_bundle(public, release)

    if set(records) != {asset.name for asset in assets}:
        raise RuntimeError("private mapping does not match generated release files")
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps({"release_files": records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return assets


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build anonymous ZIP files for the six next-sample tasks")
    parser.add_argument("--handbook", required=True)
    parser.add_argument("--release-output", required=True)
    parser.add_argument("--private-manifest", required=True)
    args = parser.parse_args()
    assets = build_release(args.handbook, args.release_output, args.private_manifest)
    for asset in assets:
        print(asset)
    print(Path(args.release_output).resolve() / "SHA256SUMS.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
