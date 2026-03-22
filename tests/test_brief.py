from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from repopromo.archive import create_assets_zip
from repopromo.brief import build_project_brief, extract_headings
from repopromo.cli import main
from repopromo.ingest import (
    RepositorySnapshot,
    branch_candidates,
    discover_doc_candidates,
    discover_doc_candidates_recursive,
    discover_root_readme_candidates,
    fetch_optional_documents,
    github_token,
    parse_github_repo_url,
    raw_doc_candidates,
    raw_readme_candidates,
)
from repopromo.models import PromoMode, SourceDocument
from repopromo.png_render import trim_white_edges
from repopromo.pipeline import build_brief_bundle_from_repo_url, plan_from_repo_url
from repopromo.review_render import write_review_slides
from repopromo.video_assembly import seconds_to_srt
from repopromo.workflow import build_workflow
from PIL import Image


SAMPLE = """
# Demo Project

This project turns repos into promo videos.

## Why

Teams can explain their work faster with a short video.

## Mechanism

It extracts a brief, builds slides, and assembles video assets.

## Features

Static slides, subtitles, narration, and covers.

## Advantages

Reviewable outputs and versioned assets.

## GitHub CTA

Search GitHub for RepoPromo.
"""


class BriefTests(unittest.TestCase):
    def test_extract_headings(self) -> None:
        self.assertEqual(
            extract_headings(SAMPLE),
            ["Demo Project", "Why", "Mechanism", "Features", "Advantages", "GitHub CTA"],
        )

    def test_build_project_brief(self) -> None:
        brief = build_project_brief("RepoPromo", SAMPLE)
        self.assertTrue(brief.why)
        self.assertTrue(brief.mechanism)
        self.assertTrue(brief.features)
        self.assertTrue(brief.advantages)
        self.assertTrue(brief.cta)
        self.assertIn("Search GitHub for RepoPromo.", brief.cta)

    def test_parse_github_repo_url(self) -> None:
        target = parse_github_repo_url("https://github.com/davidliuzhibo/clawmingguang")
        self.assertEqual(target.owner, "davidliuzhibo")
        self.assertEqual(target.repo, "clawmingguang")
        self.assertEqual(target.slug, "davidliuzhibo/clawmingguang")
        self.assertGreater(len(raw_readme_candidates(target)), 4)
        self.assertGreater(len(raw_doc_candidates(target)), 4)
        self.assertEqual(branch_candidates(target, "develop"), ["develop", "main", "master"])

    def test_build_workflow_modes(self) -> None:
        review = build_workflow(PromoMode.REVIEW)
        one_click = build_workflow(PromoMode.ONE_CLICK)
        self.assertTrue(any(stage.key == "review" for stage in review))
        self.assertFalse(any(stage.key == "review" for stage in one_click))
        self.assertEqual(review[-1].key, "video")
        self.assertEqual(one_click[-1].key, "video")

    def test_plan_from_repo_url(self) -> None:
        plan = plan_from_repo_url(
            "https://github.com/davidliuzhibo/clawdaydayup",
            mode=PromoMode.REVIEW,
        )
        self.assertEqual(plan.target.slug, "davidliuzhibo/clawdaydayup")
        self.assertEqual(plan.stages[0].key, "ingest")
        self.assertEqual(plan.stages[-1].key, "video")
        self.assertTrue(any(stage.key == "review" for stage in plan.stages))
        self.assertGreater(len(plan.readme_candidates), 4)

    def test_fetch_optional_documents_uses_successes_only(self) -> None:
        with mock.patch("repopromo.ingest.fetch_url_text") as fetch_url_text:
            fetch_url_text.side_effect = ["doc-a", RuntimeError("boom"), "doc-b"]
            docs = fetch_optional_documents(
                [
                    ("docs/a.md", "https://example.com/a"),
                    ("docs/b.md", "https://example.com/b"),
                    ("docs/c.md", "https://example.com/c"),
                ],
                limit=2,
            )
        self.assertEqual([doc.label for doc in docs], ["docs/a.md", "docs/c.md"])

    def test_discover_doc_candidates_prefers_common_doc_files(self) -> None:
        target = parse_github_repo_url("https://github.com/example/project")
        payload = [
            {"type": "file", "path": "docs/guide.md", "download_url": "https://example.com/guide.md"},
            {"type": "file", "path": "docs/index.mdx", "download_url": "https://example.com/index.mdx"},
            {"type": "file", "path": "docs/README.md", "download_url": "https://example.com/README.md"},
            {"type": "dir", "path": "docs/nested"},
        ]
        with mock.patch("repopromo.ingest.fetch_url_json", return_value=payload):
            candidates = discover_doc_candidates(target, limit=3)
        self.assertEqual(
            [label for label, _ in candidates],
            ["docs/README.md", "docs/index.mdx", "docs/guide.md"],
        )

    def test_discover_doc_candidates_recursive_finds_nested_docs(self) -> None:
        target = parse_github_repo_url("https://github.com/example/project")
        payload = {
            "tree": [
                {"type": "blob", "path": "docs/en/docs/index.md"},
                {"type": "blob", "path": "docs/en/docs/tutorial.md"},
                {"type": "blob", "path": "src/README.md"},
            ]
        }
        with mock.patch("repopromo.ingest.fetch_url_json", return_value=payload):
            candidates = discover_doc_candidates_recursive(target, limit=3)
        self.assertEqual(
            [label for label, _ in candidates],
            ["docs/en/docs/index.md", "docs/en/docs/tutorial.md"],
        )

    def test_discover_root_readme_candidates_supports_rst(self) -> None:
        target = parse_github_repo_url("https://github.com/example/project")
        payload = [
            {"type": "file", "path": "README.rst", "download_url": "https://example.com/README.rst"},
            {"type": "file", "path": "README.md", "download_url": "https://example.com/README.md"},
            {"type": "file", "path": "README.zh-CN.md", "download_url": "https://example.com/README.zh-CN.md"},
        ]
        with mock.patch("repopromo.ingest.fetch_url_json", return_value=payload):
            candidates = discover_root_readme_candidates(target, branches=["main"])
        self.assertEqual(
            candidates,
            [
                "https://example.com/README.md",
                "https://example.com/README.rst",
                "https://example.com/README.zh-CN.md",
            ],
        )

    def test_github_token_prefers_repopromo_key(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {
                "GITHUB_TOKEN": "generic-token",
                "REPOPROMO_GITHUB_TOKEN": "repo-token",
            },
            clear=False,
        ):
            with mock.patch("repopromo.ingest._GITHUB_TOKEN_CACHE", False):
                self.assertEqual(github_token(), "repo-token")

    def test_github_token_falls_back_to_gh_cli(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {
                "GITHUB_TOKEN": "",
                "REPOPROMO_GITHUB_TOKEN": "",
                "GH_TOKEN": "",
            },
            clear=False,
        ):
            completed = mock.Mock(returncode=0, stdout="gh-token\n")
            with mock.patch("repopromo.ingest._GITHUB_TOKEN_CACHE", False):
                with mock.patch("repopromo.ingest.subprocess.run", return_value=completed):
                    self.assertEqual(github_token(), "gh-token")

    def test_build_brief_bundle_from_repo_url(self) -> None:
        target = parse_github_repo_url("https://github.com/davidliuzhibo/clawmingguang")
        snapshot = RepositorySnapshot(
            target=target,
            readme=SourceDocument(label="README", url="https://example.com/readme", text=SAMPLE),
            docs=[SourceDocument(label="docs/architecture.md", url="https://example.com/arch", text="## Mechanism\n\nSecurity gates and runtime controls.")],
        )
        with mock.patch("repopromo.pipeline.fetch_repository_snapshot", return_value=snapshot):
            bundle = build_brief_bundle_from_repo_url(target.url, mode=PromoMode.REVIEW)
        self.assertEqual(bundle.plan.target.slug, target.slug)
        self.assertTrue(bundle.brief.why)
        self.assertTrue(bundle.brief.mechanism)
        self.assertTrue(bundle.script_sections)
        self.assertTrue(bundle.main_slides)
        self.assertEqual(bundle.script_sections[-1].key, "cta")
        self.assertEqual(bundle.main_slides[-1].key, "cta")
        self.assertTrue(any(stage.key == "review" for stage in bundle.plan.stages))

    def test_cli_plan(self) -> None:
        with mock.patch(
            "sys.argv",
            ["repopromo", "plan", "https://github.com/davidliuzhibo/clawmingguang", "--mode", "review"],
        ):
            result = main()
        self.assertEqual(result, 0)

    def test_write_review_slides(self) -> None:
        target = parse_github_repo_url("https://github.com/davidliuzhibo/clawmingguang")
        snapshot = RepositorySnapshot(
            target=target,
            readme=SourceDocument(label="README", url="https://example.com/readme", text=SAMPLE),
            docs=[],
        )
        with mock.patch("repopromo.pipeline.fetch_repository_snapshot", return_value=snapshot):
            bundle = build_brief_bundle_from_repo_url(target.url, mode=PromoMode.REVIEW)
        with TemporaryDirectory() as temp_dir:
            files = write_review_slides(temp_dir, repo_name=bundle.plan.target.slug, slides=bundle.main_slides)
            self.assertTrue(files)
            self.assertTrue((Path(temp_dir) / "index.html").exists())
            self.assertTrue(any(path.name.endswith("_why.html") for path in files))

    def test_trim_white_edges_keeps_target_size(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.png"
            image = Image.new("RGBA", (1100, 1940), (255, 255, 255, 255))
            for x in range(1050):
                for y in range(1880):
                    image.putpixel((x, y), (10, 30, 40, 255))
            image.save(path)
            trim_white_edges(path)
            with Image.open(path) as trimmed:
                self.assertEqual(trimmed.size, (1080, 1920))

    def test_seconds_to_srt(self) -> None:
        self.assertEqual(seconds_to_srt(65.432), "00:01:05,432")

    def test_create_assets_zip_only_keeps_whitelisted_files(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            keep_dir = base / "keep"
            skip_dir = base / "skip"
            keep_dir.mkdir()
            skip_dir.mkdir()
            (keep_dir / "a.txt").write_text("a", encoding="utf-8")
            (skip_dir / "b.txt").write_text("b", encoding="utf-8")
            zip_path = create_assets_zip(base, "assets.zip", [keep_dir])
            self.assertTrue(zip_path.exists())
            import zipfile

            with zipfile.ZipFile(zip_path, "r") as zf:
                names = zf.namelist()
            self.assertIn("keep/a.txt", names)
            self.assertNotIn("skip/b.txt", names)


if __name__ == "__main__":
    unittest.main()
