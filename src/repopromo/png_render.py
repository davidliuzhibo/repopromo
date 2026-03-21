from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PIL import Image


TARGET_SIZE = (1080, 1920)


def resolve_edge_binary() -> str:
    known_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in known_paths:
        if Path(candidate).exists():
            return candidate
    edge = shutil.which("msedge") or shutil.which("microsoft-edge")
    if edge:
        return edge
    raise FileNotFoundError("Microsoft Edge binary not found.")


def _is_white(pixel: tuple[int, ...]) -> bool:
    rgb = pixel[:3]
    return all(channel >= 250 for channel in rgb)


def trim_white_edges(path: Path) -> None:
    image = Image.open(path).convert("RGBA")
    width, height = image.size
    right = width
    bottom = height

    while right > 1:
        x = right - 1
        if any(not _is_white(image.getpixel((x, y))) for y in range(height)):
            break
        right -= 1

    while bottom > 1:
        y = bottom - 1
        if any(not _is_white(image.getpixel((x, y))) for x in range(width)):
            break
        bottom -= 1

    cropped = image.crop((0, 0, right, bottom))
    resized = cropped.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    resized.save(path)


def render_html_to_png(html_path: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    edge = resolve_edge_binary()
    resolved_output = output_path.resolve()
    command = [
        edge,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=3000",
        "--force-device-scale-factor=1",
        "--window-size=1080,1920",
        f"--screenshot={resolved_output}",
        html_path.resolve().as_uri(),
    ]
    subprocess.run(command, check=True)
    if not resolved_output.exists():
        raise RuntimeError(f"Screenshot was not created for {html_path}")
    trim_white_edges(resolved_output)
    return resolved_output


def render_html_directory_to_pngs(html_dir: str | Path, output_dir: str | Path) -> list[Path]:
    html_dir = Path(html_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for html_path in sorted(html_dir.glob("[0-9][0-9]_*.html")):
        output_path = output_dir / f"{html_path.stem}.png"
        written.append(render_html_to_png(html_path, output_path))
    return written
