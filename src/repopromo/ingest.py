from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .models import RepoTarget, SourceDocument

DEFAULT_TIMEOUT_SECONDS = 12
COMMON_DOC_PATHS = (
    "docs/README.md",
    "docs/README.mdx",
    "docs/index.md",
    "docs/index.mdx",
    "docs/overview.md",
    "docs/architecture.md",
    "docs/workflow.md",
    "docs/getting-started.md",
    "docs/quickstart.md",
    "docs/introduction.md",
    "guide/README.md",
    "guide/index.md",
    "website/README.md",
    "website/docs/index.md",
    "website/docs/index.mdx",
    "website/docs/README.md",
    "website/docs/README.mdx",
    "docs/src/index.md",
    "docs/src/README.md",
    "documentation/README.md",
)
DISCOVERY_DIRS = (
    "docs",
    "guide",
    "documentation",
    "website/docs",
    "docs/src",
)
PREFERRED_DOC_NAMES = (
    "readme.md",
    "readme.mdx",
    "index.md",
    "index.mdx",
    "overview.md",
    "architecture.md",
    "workflow.md",
    "quickstart.md",
    "getting-started.md",
    "introduction.md",
)
PREFERRED_DOC_ORDER = {name: index for index, name in enumerate(PREFERRED_DOC_NAMES)}
DOC_PATH_HINTS = (
    "docs/",
    "guide/",
    "documentation/",
    "website/docs/",
    "docs/src/",
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


def fetch_url_json(url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> Any:
    request = Request(
        url,
        headers={
            "User-Agent": "RepoPromo/0.1 (+https://github.com)",
            "Accept": "application/vnd.github+json",
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return json.loads(response.read().decode(charset, errors="replace"))


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


def discover_doc_candidates(
    target: RepoTarget,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    limit: int = 12,
) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    seen: set[str] = set()
    for branch in ("main", "master"):
        for doc_dir in DISCOVERY_DIRS:
            api_url = f"https://api.github.com/repos/{target.owner}/{target.repo}/contents/{doc_dir}?ref={branch}"
            try:
                items = fetch_url_json(api_url, timeout_seconds=timeout_seconds)
            except Exception:
                continue
            if not isinstance(items, list):
                continue
            preferred = []
            fallback = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "file":
                    continue
                path = str(item.get("path", "") or "").strip()
                download_url = str(item.get("download_url", "") or "").strip()
                if not path or not download_url:
                    continue
                lower_name = path.rsplit("/", 1)[-1].lower()
                if not (lower_name.endswith(".md") or lower_name.endswith(".mdx")):
                    continue
                pair = (path, download_url)
                if lower_name in PREFERRED_DOC_NAMES:
                    preferred.append(pair)
                else:
                    fallback.append(pair)
            preferred.sort(key=lambda pair: PREFERRED_DOC_ORDER.get(pair[0].rsplit("/", 1)[-1].lower(), 999))
            fallback.sort(key=lambda pair: pair[0].lower())
            for pair in [*preferred, *fallback]:
                if pair[0] in seen:
                    continue
                candidates.append(pair)
                seen.add(pair[0])
                if len(candidates) >= limit:
                    return candidates
    return candidates


def discover_doc_candidates_recursive(
    target: RepoTarget,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    limit: int = 20,
) -> list[tuple[str, str]]:
    candidates: list[tuple[str, str]] = []
    seen: set[str] = set()
    for branch in ("main", "master"):
        api_url = f"https://api.github.com/repos/{target.owner}/{target.repo}/git/trees/{branch}?recursive=1"
        try:
            payload = fetch_url_json(api_url, timeout_seconds=timeout_seconds)
        except Exception:
            continue
        tree = payload.get("tree", []) if isinstance(payload, dict) else []
        if not isinstance(tree, list):
            continue
        ranked: list[tuple[tuple[int, int, str], tuple[str, str]]] = []
        for item in tree:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "blob":
                continue
            path = str(item.get("path", "") or "").strip()
            if not path:
                continue
            lower = path.lower()
            if not (lower.endswith(".md") or lower.endswith(".mdx")):
                continue
            if not any(hint in lower for hint in DOC_PATH_HINTS):
                continue
            if lower in seen:
                continue
            file_name = lower.rsplit("/", 1)[-1]
            priority = PREFERRED_DOC_ORDER.get(file_name, 999)
            depth = lower.count("/")
            download_url = f"https://raw.githubusercontent.com/{target.owner}/{target.repo}/{branch}/{path}"
            ranked.append(((priority, depth, lower), (path, download_url)))
        ranked.sort(key=lambda item: item[0])
        for _, pair in ranked:
            if pair[0].lower() in seen:
                continue
            candidates.append(pair)
            seen.add(pair[0].lower())
            if len(candidates) >= limit:
                return candidates
    return candidates


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
    doc_candidates = [
        *raw_doc_candidates(target),
        *discover_doc_candidates(target, timeout_seconds=timeout_seconds, limit=max(doc_limit * 2, 8)),
        *discover_doc_candidates_recursive(target, timeout_seconds=timeout_seconds, limit=max(doc_limit * 4, 16)),
    ]
    docs = fetch_optional_documents(
        doc_candidates,
        timeout_seconds=timeout_seconds,
        limit=doc_limit,
    )
    return RepositorySnapshot(
        target=target,
        readme=SourceDocument(label="README", url=readme_url, text=readme_text),
        docs=docs,
    )
