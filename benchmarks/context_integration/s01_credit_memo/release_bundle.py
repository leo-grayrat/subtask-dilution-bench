from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import zipfile
from pathlib import Path

OPAQUE_RE = re.compile(r"^job-[0-9a-f]{12}$")


def _zip_dir(source: Path, dest: Path) -> None:
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            zf.write(path, path.relative_to(source).as_posix())


def build_release_bundle(public_root: str | Path, release_dir: str | Path) -> list[Path]:
    public = Path(public_root).resolve()
    release = Path(release_dir).resolve()
    if not public.is_dir():
        raise FileNotFoundError(public)

    entries = sorted(public.iterdir())
    if not entries:
        raise ValueError("public_root contains no packages")
    for entry in entries:
        if not entry.is_dir():
            raise ValueError(f"public_root must contain package directories only: {entry.name}")
        if not OPAQUE_RE.fullmatch(entry.name):
            raise ValueError(f"non-opaque package name: {entry.name}")

    if release.exists():
        shutil.rmtree(release)
    release.mkdir(parents=True)

    assets: list[Path] = []
    checksums: list[str] = []
    for entry in entries:
        archive = release / f"{entry.name}.zip"
        _zip_dir(entry, archive)
        assets.append(archive)
        checksums.append(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}")

    (release / "SHA256SUMS.txt").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    return assets


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build release-ready anonymous task ZIP files")
    parser.add_argument("public_root", help="Directory containing job-<opaque id> packages")
    parser.add_argument("release_dir", help="Output directory containing ZIP assets only")
    args = parser.parse_args()
    for asset in build_release_bundle(args.public_root, args.release_dir):
        print(asset)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
