from __future__ import annotations

from dataclasses import dataclass

from .brief import build_project_brief
from .ingest import (
    RepositorySnapshot,
    fetch_repository_snapshot,
    parse_github_repo_url,
    raw_readme_candidates,
)
from .models import ProjectBrief, PromoMode, RepoTarget, SlideSpec, VideoSection, WorkflowStage
from .script import build_video_sections, build_video_sections_zh
from .slides import build_main_slide_specs
from .workflow import build_workflow


@dataclass(slots=True)
class WorkflowPlan:
    target: RepoTarget
    readme_candidates: list[str]
    stages: list[WorkflowStage]


@dataclass(slots=True)
class BriefBundle:
    snapshot: RepositorySnapshot
    brief: ProjectBrief
    plan: WorkflowPlan
    script_sections: list[VideoSection]
    script_sections_zh: list[VideoSection]
    main_slides: list[SlideSpec]


def plan_from_repo_url(url: str, mode: PromoMode = PromoMode.ONE_CLICK) -> WorkflowPlan:
    target = parse_github_repo_url(url)
    return WorkflowPlan(
        target=target,
        readme_candidates=raw_readme_candidates(target),
        stages=build_workflow(mode),
    )


def build_brief_bundle_from_repo_url(
    url: str,
    mode: PromoMode = PromoMode.REVIEW,
    *,
    timeout_seconds: int = 12,
    doc_limit: int = 4,
) -> BriefBundle:
    target = parse_github_repo_url(url)
    snapshot = fetch_repository_snapshot(
        target,
        timeout_seconds=timeout_seconds,
        doc_limit=doc_limit,
    )
    brief = build_project_brief(
        project_name=target.repo,
        readme_text=snapshot.readme.text,
        extra_docs=[doc.text for doc in snapshot.docs],
    )
    plan = WorkflowPlan(
        target=target,
        readme_candidates=raw_readme_candidates(target),
        stages=build_workflow(mode),
    )
    script_sections = build_video_sections(brief)
    script_sections_zh = build_video_sections_zh(brief)
    main_slides = build_main_slide_specs(brief, script_sections)
    return BriefBundle(
        snapshot=snapshot,
        brief=brief,
        plan=plan,
        script_sections=script_sections,
        script_sections_zh=script_sections_zh,
        main_slides=main_slides,
    )
