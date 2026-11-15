# 两套自媒体 Skill 使用说明

这份说明适合做口播短视频的创作者。先把原片剪辑包装成成片，再用同一份定稿脚本做封面和三平台发布文案。只做其中一步时，单独调用对应的 Skill 即可。

## 先安装 Skill

从网盘下载所需 ZIP。剪视频选 `liya-talking-head-packaging.zip`，做封面和发布文案选 `liya-ai-cover.zip`。两个可以只装一个，也可以分别安装。

**Codex**

> Codex，帮我安装这份 Skill ZIP。我会把文件发给你，或告诉你它的位置。请解压并保留整个 Skill 文件夹，放进当前项目的 Skills 目录。装好后告诉我安装位置、Skill 名称和怎么调用，先不用开始剪片或做封面。

在项目里使用时，可以放到 `.agents/skills/<Skill名>/`，确认里面能直接看到 `SKILL.md`。安装后新开一个对话，按名称调用。

**WorkBuddy**

> WorkBuddy，我要安装这份本地 Skill ZIP。请告诉我怎么通过「上传技能」导入。导入后帮我确认能不能按 Skill 名称调用。

在桌面端进入「专家·技能·连接器 → 技能 → 添加技能 → 上传技能」，选择下载的 ZIP。对话安装主要针对技能市场，网盘 ZIP 走本地上传。上传后到「已安装」确认已启用。 [WorkBuddy 官方安装说明](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)

**Claude**

> Claude，帮我把这个 Skill 安装到我现在用的 Claude。我要装的是这份 ZIP。请告诉我该用上传入口还是项目目录，完成后给我一句调用示例。

- **Claude 网页或桌面聊天**。启用代码执行后，进入「自定义（Customize）→ Skills」，选择上传自定义 Skill，再逐个上传 ZIP。 [Claude 官方上传说明](https://support.claude.com/en/articles/12512180-use-skills-in-claude)
- **Claude Code 项目**。请 Claude Code 解压 ZIP，把完整 Skill 文件夹放进 `.claude/skills/<Skill名>/`。用 `/liya-talking-head-packaging` 或 `/liya-ai-cover` 调用。 [Claude Code Skill 说明](https://support.claude.com/en/articles/14554922-claude-code-user-faq)

装完先问一句「请确认已加载这个 Skill，告诉我第一步要提供什么」。剪辑仍需当前环境能读取素材并运行转写和渲染。封面仍需可用的图像生成或排版工具。剪映工程还取决于编辑器的连接情况。

## GitHub 源码和说明

- [黎雅自媒体制作 Skills 仓库](https://github.com/liya1998124-glitch/liya-video-editing)
- [一键剪辑包装 Skill](https://github.com/liya1998124-glitch/liya-video-editing/blob/main/SKILL.md)，入口在仓库根目录。
- [一键封面和三平台发布文案 Skill](https://github.com/liya1998124-glitch/liya-video-editing/tree/main/skills/liya-ai-cover)，单独取 `skills/liya-ai-cover` 文件夹。
- [两套 Skill 在线使用说明](https://github.com/liya1998124-glitch/liya-video-editing/blob/main/%E4%B8%A4%E5%A5%97Skill%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E.md)

直接从 GitHub 取源码时，按上面两个位置选取 Skill。上传平台时用对应的单独 ZIP，每个 ZIP 内的第一层是该 Skill 文件夹。

## 第一步 交给一键剪辑包装 Skill

- **要给的东西**。口播视频、最终脚本，有录屏和往期作品时放在同一个素材目录。没有脚本先转写原片。数据要配对应的原始截图。
- **要说清的事**。是否保留原剪口、色调与比例、重点句、片尾关键词的准确拼法、成片保存在什么位置。视频里不能出现的平台名或字词，也写在这里。
- **怎么给指令**。用 `liya-talking-head-packaging` 给这条口播做包装。这是视频、脚本和素材目录。请从里面挑画面，按口播做独立动效、字幕、词条和音效，前五秒优先。保留原声。做完给我成片、SRT、时间轴和动效素材。
- **怎么验收**。先看开头是否吸引人、动作和台词对不对、数据是否标对案例，再看字幕、音效和结尾。要剪映等可编辑工程，任务开始就说明你用的编辑器。

## 第二步 交给一键封面与发布文案 Skill

- **要给的东西**。本条脚本、字幕或摘要。真人封面附本人清晰正脸照，可多给一张手势照。要展示作品和数据就补可使用的原截图。
- **要说清的事**。有封面标题就指定原文。没给标题时，让它根据脚本拟写。可指定画幅 3:4、9:16 或两种，以及风格、主色、标题位置和必须出现的对象。
- **怎么给指令**。用 `liya-ai-cover` 根据脚本和照片做真人封面，没定标题请你拟。请做 3:4 和 9:16 两张，再给我抖音、小红书、视频号的标题、正文和话题。
- **怎么验收**。手机缩略图上检查大字、脸、手势和数字。发布文案检查抖音 5 个话题、小红书 10 个并自然融入长尾搜索词、视频号 5 个。发布稿里可以写平台全名，视频内按原先指定的称呼处理。

## 分享材料

转发两套 Skill ZIP 和这份说明即可。拍摄照片、对标原图、历史截图等在每次制作时按需提供，留在自己的项目里。
