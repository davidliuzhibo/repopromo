from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .archive import create_assets_zip
from .models import PromoMode
from .pipeline import build_brief_bundle_from_repo_url, plan_from_repo_url
from .png_render import render_html_directory_to_pngs
from .review_render import write_review_slides
from .video_assembly import (
    concat_segments,
    generate_edge_tts_audio,
    probe_duration_seconds,
    render_video_segment,
    write_simple_srt,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="repopromo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Build a workflow plan from a GitHub repository URL.")
    plan_parser.add_argument("repo_url", help="Public GitHub repository URL.")
    plan_parser.add_argument(
        "--mode",
        choices=[mode.value for mode in PromoMode],
        default=PromoMode.ONE_CLICK.value,
        help="Workflow mode to build.",
    )

    brief_parser = subparsers.add_parser("brief", help="Fetch repository content and build a project brief.")
    brief_parser.add_argument("repo_url", help="Public GitHub repository URL.")
    brief_parser.add_argument(
        "--mode",
        choices=[mode.value for mode in PromoMode],
        default=PromoMode.REVIEW.value,
        help="Workflow mode to build.",
    )
    brief_parser.add_argument("--doc-limit", type=int, default=4, help="Maximum number of docs to attach.")

    render_parser = subparsers.add_parser("render-review", help="Render HTML review slides from a GitHub repository URL.")
    render_parser.add_argument("repo_url", help="Public GitHub repository URL.")
    render_parser.add_argument("--output-dir", required=True, help="Directory to write HTML review slides into.")
    render_parser.add_argument("--doc-limit", type=int, default=4, help="Maximum number of docs to attach.")

    png_parser = subparsers.add_parser("render-review-png", help="Render review slides to HTML and PNG.")
    png_parser.add_argument("repo_url", help="Public GitHub repository URL.")
    png_parser.add_argument("--output-dir", required=True, help="Directory to write rendered assets into.")
    png_parser.add_argument("--doc-limit", type=int, default=4, help="Maximum number of docs to attach.")

    sample_parser = subparsers.add_parser("render-sample-video", help="Render a minimal sample promo video.")
    sample_parser.add_argument("repo_url", help="Public GitHub repository URL.")
    sample_parser.add_argument("--output-dir", required=True, help="Directory to write the sample video assets into.")
    sample_parser.add_argument("--doc-limit", type=int, default=4, help="Maximum number of docs to attach.")
    sample_parser.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="Edge TTS voice name.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "plan":
        plan = plan_from_repo_url(args.repo_url, PromoMode(args.mode))
        payload = {
            "target": {
                "owner": plan.target.owner,
                "repo": plan.target.repo,
                "url": plan.target.url,
                "branch": plan.target.branch,
                "slug": plan.target.slug,
            },
            "readme_candidates": plan.readme_candidates,
            "stages": [
                {"key": stage.key, "title": stage.title, "output": stage.output}
                for stage in plan.stages
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "brief":
        bundle = build_brief_bundle_from_repo_url(
            args.repo_url,
            mode=PromoMode(args.mode),
            doc_limit=args.doc_limit,
        )
        payload = {
            "target": {
                "owner": bundle.plan.target.owner,
                "repo": bundle.plan.target.repo,
                "url": bundle.plan.target.url,
                "slug": bundle.plan.target.slug,
            },
            "readme": {"url": bundle.snapshot.readme.url, "label": bundle.snapshot.readme.label},
            "docs": [{"url": doc.url, "label": doc.label} for doc in bundle.snapshot.docs],
            "brief": {
                "project_name": bundle.brief.project_name,
                "why": bundle.brief.why,
                "mechanism": bundle.brief.mechanism,
                "features": bundle.brief.features,
                "advantages": bundle.brief.advantages,
                "cta": bundle.brief.cta,
            },
            "script_sections": [
                {
                    "key": section.key,
                    "title": section.title,
                    "visual_focus": section.visual_focus,
                    "narration": section.narration,
                }
                for section in bundle.script_sections
            ],
            "script_sections_zh": [
                {
                    "key": section.key,
                    "title": section.title,
                    "visual_focus": section.visual_focus,
                    "narration": section.narration,
                }
                for section in bundle.script_sections_zh
            ],
            "main_slides": [
                {
                    "key": slide.key,
                    "title": slide.title,
                    "subtitle": slide.subtitle,
                    "bullets": slide.bullets,
                }
                for slide in bundle.main_slides
            ],
            "stages": [
                {"key": stage.key, "title": stage.title, "output": stage.output}
                for stage in bundle.plan.stages
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "render-review":
        bundle = build_brief_bundle_from_repo_url(
            args.repo_url,
            mode=PromoMode.REVIEW,
            doc_limit=args.doc_limit,
        )
        written = write_review_slides(
            Path(args.output_dir),
            repo_name=bundle.plan.target.slug,
            slides=bundle.main_slides,
        )
        payload = {
            "target": bundle.plan.target.slug,
            "output_dir": str(Path(args.output_dir).resolve()),
            "files": [str(path) for path in written],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "render-review-png":
        bundle = build_brief_bundle_from_repo_url(
            args.repo_url,
            mode=PromoMode.REVIEW,
            doc_limit=args.doc_limit,
        )
        base_dir = Path(args.output_dir)
        html_dir = base_dir / "html"
        png_dir = base_dir / "png"
        html_files = write_review_slides(
            html_dir,
            repo_name=bundle.plan.target.slug,
            slides=bundle.main_slides,
        )
        png_files = render_html_directory_to_pngs(html_dir, png_dir)
        payload = {
            "target": bundle.plan.target.slug,
            "output_dir": str(base_dir.resolve()),
            "html_files": [str(path) for path in html_files],
            "png_files": [str(path) for path in png_files],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if args.command == "render-sample-video":
        bundle = build_brief_bundle_from_repo_url(
            args.repo_url,
            mode=PromoMode.REVIEW,
            doc_limit=args.doc_limit,
        )
        base_dir = Path(args.output_dir)
        html_dir = base_dir / "html"
        png_dir = base_dir / "png"
        narration_dir = base_dir / "narration"
        audio_dir = base_dir / "audio"
        segments_dir = base_dir / "segments"
        for directory in (html_dir, png_dir, narration_dir, audio_dir, segments_dir):
            directory.mkdir(parents=True, exist_ok=True)

        html_files = write_review_slides(
            html_dir,
            repo_name=bundle.plan.target.slug,
            slides=bundle.main_slides,
        )
        png_files = render_html_directory_to_pngs(html_dir, png_dir)

        durations: list[float] = []
        segment_paths: list[Path] = []
        for index, (section, png_path) in enumerate(zip(bundle.script_sections_zh, png_files, strict=True), start=1):
            text_path = narration_dir / f"{index:02d}_{section.key}.txt"
            text_path.write_text(section.narration, encoding="utf-8")
            audio_path = audio_dir / f"{index:02d}_{section.key}.mp3"
            generate_edge_tts_audio(text_path, audio_path, voice=args.voice)
            segment_path = segments_dir / f"{index:02d}_{section.key}.mp4"
            render_video_segment(png_path, audio_path, segment_path)
            segment_paths.append(segment_path)
            durations.append(probe_duration_seconds(segment_path))

        video_path = base_dir / "sample_video.mp4"
        concat_segments(segment_paths, video_path)

        srt_path = base_dir / "sample_video.srt"
        write_simple_srt(srt_path, bundle.script_sections_zh, durations)

        cover_path = base_dir / "sample_cover.png"
        shutil.copyfile(png_files[-1], cover_path)
        zip_path = create_assets_zip(
            base_dir,
            "sample_assets.zip",
            [video_path, cover_path, srt_path, html_dir, png_dir, narration_dir],
        )

        payload = {
            "target": bundle.plan.target.slug,
            "output_dir": str(base_dir.resolve()),
            "video": str(video_path),
            "cover": str(cover_path),
            "srt": str(srt_path),
            "zip": str(zip_path),
            "png_files": [str(path) for path in png_files],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    parser.error("Unsupported command.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
