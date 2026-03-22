from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Iterable


def _iter_files(paths: Iterable[Path]) -> Iterable[Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        for item in path.rglob("*"):
            if item.is_file():
                yield item


def create_assets_zip(base_dir: str | Path, zip_name: str, include: Iterable[str | Path]) -> Path:
    base_dir = Path(base_dir)
    zip_path = base_dir / zip_name
    include_paths = [Path(path) for path in include]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for file_path in _iter_files(include_paths):
            if file_path.resolve() == zip_path.resolve():
                continue
            arcname = file_path.relative_to(base_dir).as_posix()
            zf.write(file_path, arcname)
    return zip_path
