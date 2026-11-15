"""Build video filters for timed animation and B-roll clips."""
from pathlib import Path
import math


def prepare_clips(items, plan_folder, duration, width, height):
    clips = []
    for item in items:
        start, end = float(item["start"]), float(item["end"])
        seek = float(item.get("source_start", 0))
        if not all(math.isfinite(t) for t in (start, end, seek)) or not (
            0 <= start < end <= duration + .12 and seek >= 0
        ):
            raise ValueError("Invalid motion clip timing")
        path = (plan_folder / item["path"]).absolute()
        if not path.is_file():
            raise ValueError(f"Motion clip is unavailable: {path}")
        rect = item.get("rect", [0, 0, width, height])
        if len(rect) != 4 or any(type(n) is not int or n % 2 for n in rect):
            raise ValueError("Motion clip rect requires four even integers")
        x, y, w, h = rect
        if min(x, y) < 0 or min(w, h) < 2 or x+w > width or y+h > height:
            raise ValueError("Motion clip rect exceeds the canvas")
        clips.append((path, start, end, seek, x, y, w, h))
    return clips


def video_graph(picture_index, clips, first_input):
    filters = [f"[0:{picture_index}]pad=ceil(iw/2)*2:ceil(ih/2)*2,setsar=1[base0]"]
    for i, (_, start, end, seek, x, y, w, h) in enumerate(clips):
        filters.append(
            f"[{first_input+i}:v:0]trim=start={seek}:duration={end-start},"
            f"setpts=PTS-STARTPTS+{start}/TB,"
            f"scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1[clip{i}]"
        )
        filters.append(
            f"[base{i}][clip{i}]overlay={x}:{y}:eof_action=pass:repeatlast=0:"
            f"enable='gte(t,{start})*lt(t,{end})'[base{i+1}]"
        )
    return ";".join([*filters, f"[base{len(clips)}]ass=graphics.ass[v]"])
