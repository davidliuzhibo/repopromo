# RepoPromo

RepoPromo turns a GitHub repository into a promo-video production workflow.

The goal is simple:

`GitHub URL -> project brief -> slides -> narration -> subtitles -> vertical video`

This project exists because most "AI video" tools only help with the final step. The hard part is upstream:

- understand what the project is really about
- decide what belongs in the story
- build readable slides for Chinese-heavy content
- keep narration aligned with the visual page
- keep review assets versioned instead of overwritten

RepoPromo packages the method we validated on:

- [ClawDayDayUp](https://github.com/davidliuzhibo/clawdaydayup)
- [ClawMingGuang](https://github.com/davidliuzhibo/clawmingguang)

## Two modes

### 1. One-click final video

Use this mode when you want the fastest path from a public GitHub repository to a shareable promo video.

The workflow is:

1. read repository metadata, README, and selected docs
2. build a project brief
3. draft the script and scene plan
4. render review slides and supporting shot pages
5. generate narration, subtitles, cover, and final video

### 2. Review mode

Use this mode when the project matters enough that we want to inspect the intermediate assets before final rendering.

The workflow is:

1. ingest repository content
2. generate the project brief
3. generate script and scene plan
4. render review slides
5. pause for approval
6. continue with narration, subtitles, and final video

## Current scope

RepoPromo currently includes:

- repository URL parsing
- raw README candidate discovery
- common docs candidate discovery
- project brief generation from markdown sections
- workflow planning for both modes
- script-section generation
- main-slide planning
- HTML review slide rendering
- PNG review slide rendering
- a minimal sample-video pipeline with Xiaoxiao narration
- a skill skeleton for a future agent workflow

## Demos

The workflow was validated on real public projects:

- [ClawDayDayUp](https://github.com/davidliuzhibo/clawdaydayup)
- [ClawMingGuang](https://github.com/davidliuzhibo/clawmingguang)

The current baseline can already produce:

- a project brief
- review HTML pages
- review PNG slides
- a Xiaoxiao-narrated sample video

## CLI examples

```bash
repopromo plan https://github.com/davidliuzhibo/clawmingguang --mode review
repopromo brief https://github.com/davidliuzhibo/clawmingguang --mode review
repopromo render-review https://github.com/davidliuzhibo/clawmingguang --output-dir ./review_html
repopromo render-review-png https://github.com/davidliuzhibo/clawmingguang --output-dir ./review_assets
repopromo render-sample-video https://github.com/davidliuzhibo/clawmingguang --output-dir ./sample_video
```

## Principles

1. Static-first, video-second
2. HTML/CSS for dense slide layouts, not raw SVG text blocks
3. Main slides carry the structure
4. Supporting shots only reinforce the spoken section they belong to
5. Never overwrite review assets; version them and archive older outputs

## Status

The repository now has a working ingest-to-review-assets baseline and a minimal sample-video output. The next layer is stronger markdown understanding, better Chinese-first narration templates, and a cleaner one-click publishing path.
