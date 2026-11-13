# 本地运行与素材交付

Python 3.10+、FFmpeg 和 FFprobe。FFmpeg 需带 libass 与 libx264。视频已有字幕时可指定 SRT，纯视频输入需要可用的转写能力。脚本使用可选依赖 `faster-whisper`，用已经下载的模型目录执行本地转写。也可以用当前 Agent 的已连接转写能力产出 SRT，再交脚本渲染。

```shell
python scripts/package_video.py input.mp4 --out output --theme auto --model /path/to/whisper-model
python scripts/package_video.py input.mp4 --out output --theme dark --srt captions.srt --font "Microsoft YaHei"
```

在本机选择覆盖口播语言的字体，例如 Microsoft YaHei 或 Noto Sans CJK SC。使用 `--theme light` 或 `--theme dark` 固定配色，`--captions off` 适用于原画面已有可用字幕，`--silent-effects` 保留原音轨。使用 `--plan-only` 生成 `timeline.json`，再改文案、时间、位置或动效后重跑。传 `--plan file.json` 可指定另一份时间轴。时间轴事件支持 `title`、`chapter`、`type` 和 `label`，每项可用 `position` 选择 `upper-left`、`upper-right` 或 `lower-left`，用 `sfx` 指定是否加提示音。字幕和时间轴的时间单位为秒。

章节标记自带入场进度线，`input` 事件可用于片尾打字输入提示。脚本负责自动基础包装。Agent 根据原画面修订时间轴，必要时另渲染原录屏画中画、透明角色动作和图解镜头，和基础包装统一导出。保留片段素材、参数和可编辑工程引用。没有真实操作素材的教程可以使用标清楚的原创示意。模型或编解码器缺失时，根据现有能力完成可验证的部分，并说明剩余依赖。
