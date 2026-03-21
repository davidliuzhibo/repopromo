from __future__ import annotations

import re
from typing import Iterable

from .models import ProjectBrief


HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(?P<title>.+?)\s*$", re.MULTILINE)

WHY_KEYS = ("why", "problem", "motivation", "why this exists", "why it exists")
MECHANISM_KEYS = (
    "how",
    "architecture",
    "mechanism",
    "workflow",
    "evaluation",
    "model",
    "control points",
    "runtime guard",
    "adaptive daily install rule",
    "security model",
)
FEATURE_KEYS = ("features", "capabilities", "what it adds", "what it includes")
ADVANTAGE_KEYS = ("advantages", "benefits", "why it wins", "operator", "audit", "status")
CTA_KEYS = ("cta", "get started", "quick start", "quickstart", "github handoff", "release")


def extract_headings(markdown_text: str) -> list[str]:
    return [match.group("title").strip() for match in HEADING_RE.finditer(markdown_text)]


def _first_nonempty_paragraphs(text: str, limit: int = 2) -> list[str]:
    parts = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    return parts[:limit]


def _extract_bullets(text: str, limit: int = 5) -> list[str]:
    bullets: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
        if len(bullets) >= limit:
            break
    return bullets


def _pick_bucket(title: str) -> str | None:
    lowered = title.lower()
    for key in WHY_KEYS:
        if key in lowered:
            return "why"
    for key in MECHANISM_KEYS:
        if key in lowered:
            return "mechanism"
    for key in FEATURE_KEYS:
        if key in lowered:
            return "features"
    for key in ADVANTAGE_KEYS:
        if key in lowered:
            return "advantages"
    for key in CTA_KEYS:
        if key in lowered:
            return "cta"
    return None


def _append_unique(items: list[str], values: Iterable[str]) -> None:
    seen = set(items)
    for value in values:
        clean = value.strip()
        if clean and clean not in seen:
            items.append(clean)
            seen.add(clean)


def _section_points(bucket: str, section: str) -> list[str]:
    points: list[str] = []
    paragraphs = _first_nonempty_paragraphs(section, limit=2)
    bullets = _extract_bullets(section, limit=6)

    if bucket == "why":
        points.extend(paragraphs[:1])
        points.extend(bullets[:4])
    elif bucket in {"mechanism", "features", "advantages"}:
        points.extend(bullets[:5] or paragraphs[:2])
    elif bucket == "cta":
        points.extend(paragraphs[:1])
        points.extend(bullets[:3])
    else:
        points.extend(paragraphs[:2])

    return points


def build_project_brief(project_name: str, readme_text: str, extra_docs: Iterable[str] | None = None) -> ProjectBrief:
    brief = ProjectBrief(project_name=project_name)
    combined = [readme_text]
    if extra_docs:
        combined.extend(extra_docs)

    for doc in combined:
        headings = list(HEADING_RE.finditer(doc))
        if not headings:
            _append_unique(brief.why, _first_nonempty_paragraphs(doc, limit=1))
            continue

        for index, match in enumerate(headings):
            title = match.group("title").strip()
            bucket = _pick_bucket(title)
            start = match.end()
            end = headings[index + 1].start() if index + 1 < len(headings) else len(doc)
            section = doc[start:end].strip()
            points = _section_points(bucket, section) if bucket else []
            if not bucket or not points:
                continue
            _append_unique(getattr(brief, bucket), points)

    if not brief.why:
        _append_unique(brief.why, _first_nonempty_paragraphs(readme_text, limit=1))
    if not brief.cta:
        _append_unique(brief.cta, [f"Search GitHub for {project_name}."])

    return brief
