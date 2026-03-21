# RepoPromo / 项目成片器

RepoPromo 想做的事情很直接：

`GitHub 项目链接 -> 项目提炼 -> PPT 页面 -> 配音字幕 -> 竖版宣传视频`

它不是单纯的“一键渲染器”，而是一套把仓库内容转成宣传视频的生产流程。

## 两种模式

### 1. 一键成片

适合公开仓库和快速传播场景。

流程是：

1. 读取仓库信息、README 和关键文档
2. 生成项目 brief
3. 生成脚本和分镜
4. 生成主页面与补充镜头页
5. 生成配音、字幕、封面和最终视频

### 2. 审稿模式

适合重要项目，先看中间产物，再决定是否继续出片。

流程是：

1. 读取仓库内容
2. 生成项目 brief
3. 生成脚本和分镜
4. 输出可审的静帧页面
5. 等待确认
6. 再继续生成配音、字幕和视频

## 当前范围

当前已经具备的基础能力：

- GitHub 链接解析
- README 原始地址候选生成
- 常见 docs 原始地址候选生成
- 从 markdown 中提炼项目 brief
- 生成脚本段落
- 生成主页面规划
- 输出 HTML 审稿页
- 输出 PNG 审稿图
- 用 Xiaoxiao 生成最小样片

## 常用命令

```bash
repopromo plan https://github.com/davidliuzhibo/clawmingguang --mode review
repopromo brief https://github.com/davidliuzhibo/clawmingguang --mode review
repopromo render-review https://github.com/davidliuzhibo/clawmingguang --output-dir ./review_html
repopromo render-review-png https://github.com/davidliuzhibo/clawmingguang --output-dir ./review_assets
repopromo render-sample-video https://github.com/davidliuzhibo/clawmingguang --output-dir ./sample_video
```

## 核心原则

1. 先做静帧，再做视频
2. 中文高密度页面优先用 HTML/CSS 排版
3. 主页面负责结构，补充镜头页只负责强调
4. 旁白必须和当前页面严格对应
5. 所有评审资产都要版本化，不能覆盖旧版本

## 状态

仓库现在已经打通了 `repo -> brief -> script -> slides -> png -> sample video` 的最小闭环。

下一步会继续补强：

- 中文脚本质量
- 页面视觉风格
- 更完整的一键成片能力
