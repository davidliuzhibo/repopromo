from __future__ import annotations

from .models import ProjectBrief, VideoSection


def _join_points(points: list[str], limit: int = 3, separator: str = "; ") -> str:
    selected = [point.strip().rstrip(".。；;") for point in points if point.strip()][:limit]
    return separator.join(selected)


def build_video_sections(brief: ProjectBrief) -> list[VideoSection]:
    sections: list[VideoSection] = []

    if brief.why:
        sections.append(
            VideoSection(
                key="why",
                title="Why It Matters",
                visual_focus="problem_and_value",
                narration=f"{brief.project_name} addresses this core problem: {_join_points(brief.why)}.",
            )
        )

    if brief.mechanism:
        sections.append(
            VideoSection(
                key="mechanism",
                title="How It Works",
                visual_focus="mechanism_and_flow",
                narration=f"Its core mechanism includes: {_join_points(brief.mechanism)}.",
            )
        )

    if brief.features:
        sections.append(
            VideoSection(
                key="features",
                title="What It Includes",
                visual_focus="feature_grid",
                narration=f"The most presentation-worthy capabilities are: {_join_points(brief.features)}.",
            )
        )

    if brief.advantages:
        sections.append(
            VideoSection(
                key="advantages",
                title="Why It Stands Out",
                visual_focus="advantages_and_differentiators",
                narration=f"Its main advantages are: {_join_points(brief.advantages)}.",
            )
        )

    cta_line = _join_points(brief.cta, limit=2) or f"search GitHub for {brief.project_name}"
    sections.append(
        VideoSection(
            key="cta",
            title="Call To Action",
            visual_focus="repo_name_and_search_hint",
            narration=f"To learn more, {cta_line}.",
        )
    )

    return sections


def build_video_sections_zh(brief: ProjectBrief) -> list[VideoSection]:
    sections: list[VideoSection] = []

    if brief.why:
        sections.append(
            VideoSection(
                key="why",
                title="为什么需要",
                visual_focus="problem_and_value",
                narration=(
                    f"{brief.project_name} 想解决的核心问题是："
                    f"{_join_points(brief.why, separator='；')}。"
                ),
            )
        )

    if brief.mechanism:
        sections.append(
            VideoSection(
                key="mechanism",
                title="实现机制",
                visual_focus="mechanism_and_flow",
                narration=(
                    f"它把这件事拆成一条可执行的生产链："
                    f"{_join_points(brief.mechanism, separator='；')}。"
                ),
            )
        )

    if brief.features:
        sections.append(
            VideoSection(
                key="features",
                title="关键能力",
                visual_focus="feature_grid",
                narration=(
                    f"当前最值得展示的能力有："
                    f"{_join_points(brief.features, separator='；')}。"
                ),
            )
        )

    if brief.advantages:
        sections.append(
            VideoSection(
                key="advantages",
                title="主要优势",
                visual_focus="advantages_and_differentiators",
                narration=(
                    f"它的优势不只是能出片，更在于："
                    f"{_join_points(brief.advantages, separator='；')}。"
                ),
            )
        )

    cta_line = _join_points(brief.cta, limit=2, separator="；")
    if not cta_line:
        cta_line = f"在 GitHub 搜索 {brief.project_name}"
    sections.append(
        VideoSection(
            key="cta",
            title="行动引导",
            visual_focus="repo_name_and_search_hint",
            narration=f"如果你想继续了解，可以{cta_line}。",
        )
    )

    return sections
