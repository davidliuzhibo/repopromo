from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class PromoMode(StrEnum):
    ONE_CLICK = "one_click"
    REVIEW = "review"


@dataclass(slots=True)
class RepoTarget:
    owner: str
    repo: str
    url: str
    branch: str = "main"

    @property
    def slug(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclass(slots=True)
class WorkflowStage:
    key: str
    title: str
    output: str


@dataclass(slots=True)
class ProjectBrief:
    project_name: str
    why: list[str] = field(default_factory=list)
    mechanism: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    advantages: list[str] = field(default_factory=list)
    cta: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SourceDocument:
    label: str
    url: str
    text: str


@dataclass(slots=True)
class VideoSection:
    key: str
    title: str
    visual_focus: str
    narration: str


@dataclass(slots=True)
class SlideSpec:
    key: str
    title: str
    subtitle: str
    bullets: list[str] = field(default_factory=list)
