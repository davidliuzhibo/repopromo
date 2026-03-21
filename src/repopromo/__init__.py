"""RepoPromo package."""

from .brief import build_project_brief, extract_headings
from .ingest import (
    RepositorySnapshot,
    fetch_repository_snapshot,
    parse_github_repo_url,
    raw_doc_candidates,
    raw_readme_candidates,
)
from .models import (
    ProjectBrief,
    PromoMode,
    RepoTarget,
    SlideSpec,
    SourceDocument,
    VideoSection,
    WorkflowStage,
)
from .pipeline import BriefBundle, WorkflowPlan, build_brief_bundle_from_repo_url, plan_from_repo_url
from .png_render import render_html_directory_to_pngs, render_html_to_png
from .review_render import write_review_slides
from .script import build_video_sections, build_video_sections_zh
from .slides import build_main_slide_specs
from .video_assembly import seconds_to_srt, write_simple_srt
from .workflow import build_workflow

__all__ = [
    "BriefBundle",
    "ProjectBrief",
    "PromoMode",
    "RepoTarget",
    "RepositorySnapshot",
    "SlideSpec",
    "SourceDocument",
    "VideoSection",
    "WorkflowPlan",
    "WorkflowStage",
    "build_brief_bundle_from_repo_url",
    "build_main_slide_specs",
    "build_project_brief",
    "build_video_sections",
    "build_video_sections_zh",
    "build_workflow",
    "extract_headings",
    "fetch_repository_snapshot",
    "parse_github_repo_url",
    "plan_from_repo_url",
    "raw_doc_candidates",
    "raw_readme_candidates",
    "render_html_directory_to_pngs",
    "render_html_to_png",
    "seconds_to_srt",
    "write_review_slides",
    "write_simple_srt",
]
