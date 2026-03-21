from __future__ import annotations

from .models import ProjectBrief, SlideSpec, VideoSection


def _pick_bullets(brief: ProjectBrief, key: str, limit: int = 4) -> list[str]:
    mapping = {
        "why": brief.why,
        "mechanism": brief.mechanism,
        "features": brief.features,
        "advantages": brief.advantages,
        "cta": brief.cta,
    }
    source = mapping.get(key, [])
    return [item for item in source[:limit] if item]


def build_main_slide_specs(brief: ProjectBrief, sections: list[VideoSection]) -> list[SlideSpec]:
    slides: list[SlideSpec] = []
    for section in sections:
        subtitle = section.visual_focus.replace("_", " ").title()
        slides.append(
            SlideSpec(
                key=section.key,
                title=section.title,
                subtitle=subtitle,
                bullets=_pick_bullets(brief, section.key),
            )
        )
    return slides
