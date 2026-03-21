from __future__ import annotations

from html import escape
from pathlib import Path

from .models import SlideSpec


BASE_CSS = """
:root {
  --bg-1: #061520;
  --bg-2: #0c2431;
  --panel: rgba(9, 24, 35, 0.86);
  --panel-soft: rgba(17, 40, 56, 0.74);
  --border: rgba(129, 196, 255, 0.22);
  --text: #f4fbff;
  --muted: #99b7c8;
  --accent: #6ad1ff;
  --accent-2: #72f0c3;
}
* { box-sizing: border-box; }
html, body {
  margin: 0;
  width: 1080px;
  height: 1920px;
  overflow: hidden;
  font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
  color: var(--text);
  background:
    radial-gradient(circle at top left, rgba(106, 209, 255, 0.18), transparent 28%),
    radial-gradient(circle at bottom right, rgba(114, 240, 195, 0.16), transparent 22%),
    linear-gradient(180deg, var(--bg-1), var(--bg-2));
}
body { padding: 72px; }
.shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid var(--border);
  border-radius: 42px;
  background: linear-gradient(180deg, rgba(8, 19, 29, 0.88), rgba(7, 18, 28, 0.94));
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.35);
  overflow: hidden;
}
.hero {
  padding: 56px 56px 28px;
  border-bottom: 1px solid rgba(129, 196, 255, 0.12);
}
.eyebrow {
  display: inline-flex;
  padding: 10px 18px;
  border-radius: 999px;
  background: rgba(106, 209, 255, 0.1);
  color: var(--accent);
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.title {
  margin: 22px 0 14px;
  font-size: 82px;
  line-height: 1.05;
  font-weight: 800;
}
.subtitle {
  font-size: 34px;
  line-height: 1.45;
  color: var(--muted);
  max-width: 860px;
}
.content {
  flex: 1;
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 28px;
  padding: 30px 56px 56px;
}
.panel {
  border: 1px solid var(--border);
  border-radius: 30px;
  background: var(--panel);
  padding: 30px 32px;
}
.panel.soft { background: var(--panel-soft); }
.panel h3 {
  margin: 0 0 18px;
  font-size: 28px;
  line-height: 1.2;
  color: var(--accent-2);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.bullets {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.bullet {
  padding: 18px 20px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 31px;
  line-height: 1.42;
}
.meta {
  display: grid;
  gap: 18px;
}
.metric {
  padding: 18px 20px;
  border-radius: 22px;
  background: rgba(106, 209, 255, 0.08);
  border: 1px solid rgba(106, 209, 255, 0.18);
}
.metric .label {
  font-size: 22px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.metric .value {
  margin-top: 8px;
  font-size: 30px;
  line-height: 1.35;
}
.footer {
  padding: 0 56px 44px;
  font-size: 24px;
  color: var(--muted);
}
a { color: inherit; }
"""


def _render_bullets(bullets: list[str]) -> str:
    if not bullets:
        return '<div class="bullet">No bullets extracted yet.</div>'
    return "\n".join(f'<div class="bullet">{escape(bullet)}</div>' for bullet in bullets)


def render_slide_html(slide: SlideSpec, *, repo_name: str, index: int, total: int) -> str:
    title = escape(slide.title)
    subtitle = escape(slide.subtitle)
    repo_name = escape(repo_name)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=1080, initial-scale=1" />
  <title>{title}</title>
  <style>{BASE_CSS}</style>
</head>
<body>
  <div class="shell">
    <div class="hero">
      <div class="eyebrow">RepoPromo Review Mode</div>
      <div class="title">{title}</div>
      <div class="subtitle">{subtitle}</div>
    </div>
    <div class="content">
      <section class="panel">
        <h3>Slide Content</h3>
        <div class="bullets">
          {_render_bullets(slide.bullets)}
        </div>
      </section>
      <aside class="meta">
        <div class="panel soft">
          <h3>Context</h3>
          <div class="metric">
            <div class="label">Project</div>
            <div class="value">{repo_name}</div>
          </div>
          <div class="metric">
            <div class="label">Slide Key</div>
            <div class="value">{escape(slide.key)}</div>
          </div>
          <div class="metric">
            <div class="label">Position</div>
            <div class="value">{index} / {total}</div>
          </div>
        </div>
        <div class="panel soft">
          <h3>Review Goal</h3>
          <div class="metric">
            <div class="value">Check whether the story, hierarchy, and bullets are strong enough before narration and video assembly.</div>
          </div>
        </div>
      </aside>
    </div>
    <div class="footer">RepoPromo / 项目成片器 · review slide draft</div>
  </div>
</body>
</html>
"""


def render_index_html(repo_name: str, slides: list[SlideSpec]) -> str:
    items = "\n".join(
        f'<li><a href="{index:02d}_{slide.key}.html">{index:02d}. {escape(slide.title)}</a></li>'
        for index, slide in enumerate(slides, start=1)
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{escape(repo_name)} Review Slides</title>
  <style>
    body {{
      font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
      margin: 40px;
      background: #09141e;
      color: #f4fbff;
    }}
    a {{ color: #6ad1ff; text-decoration: none; }}
    li {{ margin: 10px 0; }}
  </style>
</head>
<body>
  <h1>{escape(repo_name)} · review slides</h1>
  <ol>{items}</ol>
</body>
</html>
"""


def write_review_slides(output_dir: str | Path, *, repo_name: str, slides: list[SlideSpec]) -> list[Path]:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    total = len(slides)
    for index, slide in enumerate(slides, start=1):
        path = target_dir / f"{index:02d}_{slide.key}.html"
        path.write_text(
            render_slide_html(slide, repo_name=repo_name, index=index, total=total),
            encoding="utf-8",
        )
        written.append(path)

    index_path = target_dir / "index.html"
    index_path.write_text(render_index_html(repo_name, slides), encoding="utf-8")
    written.append(index_path)
    return written
