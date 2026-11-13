# Liya Talking Head Packaging

把已录制的口播视频交给能够读取本地文件、运行命令的 AI Agent。它会按口播安排字幕、标题、词条、过程图解和声音点缀，并导出视频供你检查。

> 请用 liya-talking-head-packaging 包装这条视频。字幕请自动生成，风格按画面选，保留我的原声。

## 使用

1. 把这个目录完整放进所用 Agent 的 Skills 目录，或在聊天中提供目录和视频的位置。
2. 任选亮色、深色或自动配色。亮色以白和紫为主，深色以深海军蓝和薄荷青为主。
3. 给 Agent 一条有清楚口播的视频。可以附录屏、原始字幕或已有视觉素材。涉及真实软件操作时，Agent 会根据实际素材安排演示。

本地脚本依赖 Python 3.10+、FFmpeg、FFprobe 和适合该语言的字体。视频直入的本地转写需要 `faster-whisper` 和可用的模型，也可以交给 Agent 已连接的转写工具。[运行命令、输出文件和时间轴参数](references/run.md)

脚本会生成可修改的时间轴、SRT、ASS、按需生成的音效轨和 MP4。更复杂的插画、录屏画中画和角色动作由 Agent 按[视觉设计指南](references/design.md)补做并检查。

## License

MIT，见 [LICENSE](LICENSE)。
