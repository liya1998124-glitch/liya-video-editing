# 黎雅自媒体制作 Skills

- [一键剪辑包装](SKILL.md) 与 [剪辑使用说明](使用说明.md)
- [一键封面与三平台发布文案](skills/liya-ai-cover/SKILL.md) 与 [封面使用说明](skills/liya-ai-cover/使用说明.md)
- [两套 Skill 使用说明](两套Skill使用说明.md)

## 一键剪辑包装

给 Codex 或其他支持本地文件和命令的 AI 助手一条口播视频，就能自动转写、加字幕、做动效和轻音效，再导出 MP4。支持亮色和深色两套风格。

> 请用 liya-talking-head-packaging，把这条口播和我给你的素材目录一键剪辑包装成成片。自己挑素材、做动效和剪辑，配好字幕、词条与音效，保留我的原声。

## 使用

[零基础使用说明](使用说明.md)有可复制的调用指令。

1. 把这个目录完整放进所用 Agent 的 Skills 目录，或在聊天中提供目录和视频的位置。
2. 任选亮色、深色或自动配色。亮色以白和紫为主，深色以深海军蓝和薄荷青为主。
3. 给 Agent 一条有清楚口播的视频。可以附录屏、原始字幕或已有视觉素材。涉及真实软件操作时，Agent 会根据实际素材安排演示。

本地脚本依赖 Python 3.10+、FFmpeg、FFprobe 和适合该语言的字体。视频直入的本地转写需要 `faster-whisper` 和可用的模型，也可以交给 Agent 已连接的转写工具。[运行命令、输出文件和时间轴参数](references/run.md)

脚本会生成可修改的时间轴、SRT、ASS、按需生成的音效轨和 MP4。更复杂的插画、录屏画中画和角色动作由 Agent 按[视觉设计指南](references/design.md)补做并检查。

[一键剪辑包装流程](references/autonomous-edit.md)说明 Agent 如何主动完成素材盘点、独立动效、时间轴合成与成片验收。[胶片与分段动效](references/motion-workflow.md)提供可复用方法。

## License

MIT，见 [LICENSE](LICENSE)。
