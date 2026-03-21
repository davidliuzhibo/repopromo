from __future__ import annotations

from .models import PromoMode, WorkflowStage


def build_workflow(mode: PromoMode) -> list[WorkflowStage]:
    stages = [
        WorkflowStage("ingest", "Read Repo", "readme_and_docs"),
        WorkflowStage("brief", "Build Brief", "project_brief"),
        WorkflowStage("script", "Draft Script", "video_script"),
        WorkflowStage("slides", "Build Slides", "review_slides"),
    ]
    if mode == PromoMode.REVIEW:
        stages.append(WorkflowStage("review", "Review Gate", "approved_slides"))
    stages.extend(
        [
            WorkflowStage("voice", "Generate Narration", "audio_and_subtitles"),
            WorkflowStage("video", "Assemble Video", "final_video"),
        ]
    )
    return stages
