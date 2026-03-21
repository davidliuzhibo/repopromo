from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .models import RepoTarget, SourceDocument

DEFAULT_TIMEOUT_SECONDS = 12
COMMON_DOC_PATHS = (
    "docs/README.md",
    "docs/index.md",
    "docs/overview.md",
    "docs/architecture.md",
    "docs/workflow.md",
    "docs/getting-started.md",
    "docs/quickstart.md",
)


@dataclass(slots=True)
class RepositorySnapshot:
    target: RepoTarget
    readme: SourceDocument
    docs: list[SourceDocument]


def parse_github_repo_url(url: str) -> RepoTarget:
    parsed = urlparse(url.strip())
    if parsed.netloc.lower() != "github.com":
        raise ValueError("Only github.com repository URLs are supported.")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("Repository URL must include owner and repo.")

    owner, repo = parts[0], parts[1]
    repo = repo.removesuffix(".git")
    return RepoTarget(owner=owner, repo=repo, url=f"https://github.com/{owner}/{repo}")


def raw_readme_candidates(target: RepoTarget) -> list[str]:
    return [
        f"https://raw.githubusercontent.com/{target.owner}/{target.repo}/main/README.md",
        f"https://raw.githubusercontent.com/{target.owner}/{target.repo}/master/README.md",
        f"https://raw.githubusercontent.com/{target.owner}/{target.repo}/main/README.zh-CN.md",
        f"https://raw.githubusercontent.com/{target.owner}/{target.repo}/master/README.zh-CN.md",
    ]


def raw_doc_candidates(target: RepoTarget) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    for branch in ("main", "master"):
        for path in COMMON_DOC_PATHS:
            candidates.append(
                (
                    path,
                    f"https://raw.githubusercontent.com/{target.owner}/{target.repo}/{branch}/{path}",
                )
            )
    return candidates


def fetch_url_text(url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    request = Request(url, headers={"User-Agent": "RepoPromo/0.1 (+https://github.com)"})
    with urlopen(request, timeout=timeout_seconds) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def fetch_first_available(
    urls: list[str],
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[str, str]:
    last_error: Exception | None = None
    for url in urls:
        try:
            return url, fetch_url_text(url, timeout_seconds=timeout_seconds)
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc
    raise RuntimeError(f"Unable to fetch any candidate URL. Last error: {last_error}")


def fetch_optional_documents(
    candidates: list[tuple[str, str]],
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    limit: int = 4,
) -> list[SourceDocument]:
    docs: list[SourceDocument] = []
    seen_labels: set[str] = set()
    for label, url in candidates:
        if label in seen_labels:
            continue
        try:
            text = fetch_url_text(url, timeout_seconds=timeout_seconds)
        except Exception:
            continue
        docs.append(SourceDocument(label=label, url=url, text=text))
        seen_labels.add(label)
        if len(docs) >= limit:
            break
    return docs


def fetch_repository_snapshot(
    target: RepoTarget,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    doc_limit: int = 4,
) -> RepositorySnapshot:
    readme_url, readme_text = fetch_first_available(
        raw_readme_candidates(target),
        timeout_seconds=timeout_seconds,
    )
    docs = fetch_optional_documents(
        raw_doc_candidates(target),
        timeout_seconds=timeout_seconds,
        limit=doc_limit,
    )
    return RepositorySnapshot(
        target=target,
        readme=SourceDocument(label="README", url=readme_url, text=readme_text),
        docs=docs,
    )
