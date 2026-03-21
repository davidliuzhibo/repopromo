# RepoPromo / 项目成片器

RepoPromo 想做的事情很直接：

`GitHub 项目链接 -> 项目提炼 -> PPT 页面 -> 配音字幕 -> 竖版宣传视频`

它不是单纯的“一键渲染器”，而是一套把仓库内容转成宣传视频的生产流程。

## 这个项目为什么有价值

很多“AI 视频”工具只解决了最后一步：把已有内容剪成视频。

真正难的是前面这些：

- 读懂项目到底在解决什么问题
- 判断哪些信息值得讲，哪些应该删掉
- 把 README 和 docs 压成适合传播的故事线
- 做出中文可读、信息密度高的页面
- 让旁白和当前页面严格对齐
- 让审稿资产版本化，而不是一遍遍覆盖旧文件

RepoPromo 就是在解决这部分。

## 两种模式

### 1. 一键成片

适合公开仓库和快速传播场景。

流程是：

1. 读取仓库信息、README 和关键 docs
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
4. 输出可审的页面和摘要
5. 等待确认
6. 再继续生成配音、字幕和视频

## 当前能力

当前已经打通的能力包括：

- GitHub 链接解析
- README 原始地址候选发现
- 常见 docs 原始地址候选发现
- 从 markdown 中提炼项目 brief
- 生成中英文脚本段落
- 生成主页面规划
- 输出 HTML 审稿页
- 输出 PNG 审稿图
- 基于 Xiaoxiao 生成最小样片

## Demo

RepoPromo 的方法已经在这些真实项目上验证过：

- [ClawDayDayUp](https://github.com/davidliuzhibo/clawdaydayup)
- [ClawMingGuang](https://github.com/davidliuzhibo/clawmingguang)

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
3. 主页面负责结构，补充镜头页只负责强化
4. 旁白必须和当前页面严格对齐
5. 所有审稿资产都要版本化，不能覆盖旧版本

## 当前状态

RepoPromo 现在已经打通了：

`repo -> brief -> script -> slides -> png -> sample video`

下一步会继续补强：

- 更强的 markdown 理解
- 更成熟的中文宣传片口径
- 更稳定的一键成片与飞书回推链路
