from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .models import VideoSection


def _resolve_binary(name: str) -> str:
    resolved = shutil.which(name)
    if not resolved:
        raise FileNotFoundError(f"{name} was not found in PATH.")
    return resolved


def probe_duration_seconds(media_path: str | Path) -> float:
    ffprobe = _resolve_binary("ffprobe")
    command = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(media_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def seconds_to_srt(ts: float) -> str:
    millis = int(round(ts * 1000))
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def write_simple_srt(output_path: str | Path, sections: list[VideoSection], durations: list[float]) -> Path:
    output_path = Path(output_path)
    lines: list[str] = []
    cursor = 0.0
    for index, (section, duration) in enumerate(zip(sections, durations, strict=True), start=1):
        start = cursor
        end = cursor + duration
        lines.extend(
            [
                str(index),
                f"{seconds_to_srt(start)} --> {seconds_to_srt(end)}",
                section.narration,
                "",
            ]
        )
        cursor = end
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def generate_edge_tts_audio(
    text_path: str | Path,
    audio_path: str | Path,
    *,
    voice: str = "zh-CN-XiaoxiaoNeural",
) -> Path:
    command = [
        _resolve_binary("python"),
        "-m",
        "edge_tts",
        "--file",
        str(text_path),
        "--voice",
        voice,
        "--write-media",
        str(audio_path),
    ]
    subprocess.run(command, check=True)
    return Path(audio_path)


def render_video_segment(
    image_path: str | Path,
    audio_path: str | Path,
    output_path: str | Path,
    *,
    min_duration: float = 5.0,
) -> Path:
    ffmpeg = _resolve_binary("ffmpeg")
    audio_duration = probe_duration_seconds(audio_path)
    target_duration = max(audio_duration, min_duration)
    command = [
        ffmpeg,
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-i",
        str(audio_path),
        "-vf",
        "scale=1080:1920,format=yuv420p",
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-af",
        f"apad=whole_dur={target_duration:.3f}",
        "-t",
        f"{target_duration:.3f}",
        "-r",
        "30",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    subprocess.run(command, check=True)
    return Path(output_path)


def concat_segments(segment_paths: list[Path], output_path: str | Path) -> Path:
    ffmpeg = _resolve_binary("ffmpeg")
    output_path = Path(output_path)
    list_path = output_path.with_suffix(".txt")
    list_path.write_text(
        "\n".join(f"file '{path.as_posix()}'" for path in segment_paths),
        encoding="utf-8",
    )
    command = [
        ffmpeg,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_path),
        "-c",
        "copy",
        str(output_path),
    ]
    subprocess.run(command, check=True)
    return output_path
