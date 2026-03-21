# Architecture

RepoPromo is organized around four layers.

## 1. Brief Extraction

Input:

- README
- selected docs
- optional architecture notes

Output:

- why the project matters
- mechanism
- features
- advantages
- CTA

This layer should stay deterministic and reviewable.

## 2. Story Planning

The story planner converts a project brief into:

- short script
- scene manifest
- main slide list
- optional supporting shot list

The planner must preserve one rule:

> supporting shots reinforce the same spoken section, they do not start a new story thread.

## 3. Slide Production

Slides are built as 1080x1920 HTML/CSS pages first.

## 4. Media Assembly

After slides pass review:

- generate narration
- generate subtitles
- assign scene durations
- assemble the vertical video
- export cover
