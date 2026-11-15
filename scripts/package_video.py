"""Build and render an editable local talking-head packaging plan."""
import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import wave
from array import array


THEMES = {
    "light": ("FFFFFF", "28140D", "E34691"),
    "dark": ("28140D", "FFFFFF", "D1E784"),
}
SRT_TIME = re.compile(r"(\d+):(\d\d):(\d\d)[,.](\d{3})")


from motion_clips import prepare_clips, video_graph

def ffprobe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ]))


def timecode(seconds, ass=False):
    rate = 100 if ass else 1000
    total = round(max(0, seconds) * rate)
    minutes, remainder = divmod(total, 60 * rate)
    hours, minutes = divmod(minutes, 60)
    sec, fraction = divmod(remainder, rate)
    if ass:
        return f"{hours}:{minutes:02d}:{sec:02d}.{fraction:02d}"
    return f"{hours:02d}:{minutes:02d}:{sec:02d},{fraction:03d}"


def parse_srt(path):
    cues = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        timing = next((i for i, line in enumerate(lines) if "-->" in line), -1)
        if timing < 0:
            continue
        matches = SRT_TIME.findall(lines[timing])
        if len(matches) != 2:
            continue
        start, end = [int(h)*3600+int(m)*60+int(s)+int(ms)/1000 for h,m,s,ms in matches]
        content = " ".join(lines[timing+1:])
        if content and end > start:
            cues.append({"start": start, "end": end, "text": content})
    return cues


def transcribe(source, model, language):
    if not model:
        raise SystemExit("Pure video input needs --model pointing to a local Whisper model, or --srt.")
    if not model.is_dir():
        raise SystemExit(f"Local model directory is unavailable: {model}")
    try:
        import numpy as np
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit("Install faster-whisper or provide a transcript with --srt.") from exc
    engine = WhisperModel(str(model), device="cpu", compute_type="int8", local_files_only=True)
    pcm = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(source), "-map", "0:a:0",
        "-ac", "1", "-ar", "16000", "-f", "f32le", "-"
    ])
    samples = np.frombuffer(pcm, dtype="<f4").copy()
    segments, _ = engine.transcribe(samples, language=language, vad_filter=True, word_timestamps=True)
    cues = []
    for segment in segments:
        words = segment.words or []
        limit = 32 if re.search(r"[\u3400-\u9fff]", segment.text) else 62
        start, end, text = segment.start, segment.start, ""
        for word in words:
            if text and (len((text+word.word).strip()) > limit or word.end-start > 4.4):
                cues.append({"start": start, "end": end, "text": text.strip()})
                text = ""
            if not text:
                start = word.start
            text += word.word
            end = word.end
        if text.strip():
            cues.append({"start": start, "end": end, "text": text.strip()})
        elif not words and segment.text.strip():
            cues.append({"start": segment.start, "end": segment.end, "text": segment.text.strip()})
    return cues


def auto_theme(source):
    pixels = subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(source), "-vf", "fps=1/2,scale=12:8,format=gray",
        "-frames:v", "4", "-f", "rawvideo", "-"
    ])
    if not pixels:
        return "light"
    edges = [value for i, value in enumerate(pixels) if i % 12 in {0, 1, 10, 11}]
    return "light" if sum(edges)/len(edges) >= 105 else "dark"


def phrase(text, limit):
    clean = text.strip(" ，。！？、,.!?")
    if len(clean) <= limit:
        return clean
    return clean[:limit-1].rstrip() + "…"


def plan_events(cues, duration):
    first = cues[0]
    title = phrase(re.split(r"[。！？!?]", first["text"])[0], 28)
    events = [{"kind": "title", "start": first["start"], "end": min(duration, first["start"]+3.8),
               "text": title, "sfx": False, "position": "upper-left"}]
    last = first["start"]
    for cue in cues[1:]:
        if cue["start"] < last+9 or cue["start"]+1 > duration:
            continue
        candidate = re.match(r"^\s*(首先|接下来|然后|最后|第一[步点个]?|第二[步点个]?|第三[步点个]?|例如|比如)\s*[、：:，,]?\s*(.+)", cue["text"])
        if candidate:
            name, details = candidate.groups()
            event = {"kind": "chapter", "start": cue["start"], "end": min(duration, cue["start"]+3.2),
                     "text": f"{name} · {phrase(details, 22)}", "sfx": True, "position": "upper-left"}
        elif cue["start"] >= last+21:
            event = {"kind": "type", "start": cue["start"], "end": min(duration, cue["start"]+3.1),
                     "text": phrase(cue["text"], 22), "sfx": False, "position": "upper-left"}
        else:
            continue
        events.append(event)
        last = cue["start"]
    return events


def clean_text(text):
    return str(text).replace("\\", "＼").replace("{", "｛").replace("}", "｝").replace("\n", " ")


def build_ass(width, height, theme, font, cues, events, captions, duration):
    paper, ink, accent = THEMES[theme]
    unit = min(width, height)
    size = max(16, round(unit*.049))
    margin = max(12, round(unit*.06))
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,{font},{size},&H00{ink},&H00{ink},&H00{paper},&H00000000,-1,0,0,0,100,100,0,0,1,{max(2,round(size*.11))},0,2,{margin},{margin},{round(height*.09)},1
Style: Graphic,{font},{size},&H00{ink},&H00{ink},&H10{paper},&H00000000,-1,0,0,0,100,100,0,0,3,9,0,7,{margin},{margin},{margin},1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []

    def add(layer, start, end, style, text):
        start, end = max(0,start), min(duration,end)
        if round(end*100) > round(start*100):
            lines.append(f"Dialogue: {layer},{timecode(start,True)},{timecode(end,True)},{style},,0,0,0,,{text}")

    if captions:
        for cue in cues:
            add(2,cue["start"],cue["end"],"Caption",clean_text(cue["text"]))
    for event in events:
        start, end = event["start"], event["end"]
        kind, text = event["kind"], clean_text(event["text"])
        position = event.get("position", "upper-left")
        align = 9 if position == "upper-right" else 7
        x = width-margin if align == 9 else margin
        y = round(height*(.66 if position == "lower-left" else .09))
        font_size = round(size*(1.24 if kind == "title" else .92))
        if kind in {"type", "input"}:
            if kind == "input":
                add(1,start,end,"Graphic",
                    f"{{\\an{align}\\pos({x},{y})\\fs{font_size}\\1c&H{accent}&}}›")
                x += font_size if align == 7 else 0
            step = min(.066, (end-start)*.55/max(1,len(text)))
            tags = f"{{\\an{align}\\pos({x},{y})\\fs{font_size}}}"
            for i in range(1,len(text)+1):
                tail = "" if i==len(text) else f"{{\\1c&H{accent}&}}▏"
                add(1,start+(i-1)*step,end if i==len(text) else start+i*step,"Graphic",tags+text[:i]+tail)
        else:
            tags = (f"{{\\an{align}\\move({x},{y+12},{x},{y},0,230)"
                    f"\\fs{font_size}\\fad(150,140)\\1c&H{accent if kind=='chapter' else ink}&}}")
            add(1,start,end,"Graphic",tags+text)
        if kind == "chapter":
            line_x = x if align == 7 else max(margin,x-round(unit*.30))
            line_y = y+round(font_size*1.56)
            distance = round(unit*.30)
            line = (f"{{\\an7\\pos({line_x},{line_y})\\p1\\bord0\\shad0\\1c&H{accent}&"
                    f"\\fscx5\\t(0,420,\\fscx100)}}m 0 0 l {distance} 0 {distance} 3 0 3")
            add(0,start,end,"Graphic",line)
    return header+"\n".join(lines)+"\n"


def write_effects(path, starts, duration):
    rate = 24000
    cursor = 0
    sound = array("h", (round(380*math.sin(2*math.pi*760*i/rate)*
                             min(1,i/(rate*.008))*math.exp(-i/(rate*.03)))
                        for i in range(round(rate*.12))))
    with wave.open(str(path),"wb") as out:
        out.setparams((1,2,rate,0,"NONE","not compressed"))
        for start in sorted(set(starts)):
            offset = min(round(duration*rate), round(start*rate))
            if offset < cursor:
                continue
            while cursor < offset:
                length = min(rate*10,offset-cursor)
                out.writeframesraw(bytes(length*2))
                cursor += length
            piece = sound[:max(0,round(duration*rate)-cursor)]
            out.writeframesraw(piece.tobytes())
            cursor += len(piece)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--theme", choices=["auto","light","dark"], default="auto")
    parser.add_argument("--srt", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--language")
    parser.add_argument("--font", default="Noto Sans CJK SC")
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--captions", choices=["on","off"], default="on")
    parser.add_argument("--silent-effects", action="store_true")
    args = parser.parse_args()
    if not args.font.strip() or any(c in args.font for c in ",\r\n"):
        parser.error("Choose one font family without commas or line breaks.")
    source, out = args.video.absolute(), args.out.absolute()
    final, temp = out/"packaged.mp4", out/".rendering.mp4"
    if not source.is_file():
        parser.error(f"Video file is unavailable: {source}")
    if any(target == source or (target.exists() and target.samefile(source))
           for target in (final,temp)):
        parser.error("Use a separate output directory to protect the input.")
    metadata = ffprobe(source)
    picture = next((s for s in metadata["streams"] if s["codec_type"]=="video"
                    and not s.get("disposition",{}).get("attached_pic")),None)
    audio = next((s for s in metadata["streams"] if s["codec_type"]=="audio"),None)
    if not picture or not audio:
        parser.error("Provide a video with an audio stream.")
    duration = float(metadata["format"]["duration"])
    if not math.isfinite(duration) or duration <= 0:
        parser.error("The video duration must be finite and positive.")
    rotation = next((round(float(s["rotation"])) for s in picture.get("side_data_list",[]) if "rotation" in s),0)
    width, height = picture["width"],picture["height"]
    if rotation%180 == 90:
        width,height = height,width
    width,height = width+width%2,height+height%2
    if args.plan:
        plan = json.loads(args.plan.read_text(encoding="utf-8-sig"))
        cues, events = plan["captions"],plan["events"]
    else:
        cues = parse_srt(args.srt) if args.srt else transcribe(source,args.model,args.language)
        if not cues:
            parser.error("No speech cues found. Check the audio or provide synchronized subtitles.")
        events = plan_events(cues,duration)
    motion = plan.get("motion", []) if args.plan else []
    try:
        clips = prepare_clips(motion, args.plan.absolute().parent, duration, width, height) if motion else []
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.error(str(exc))
    for item in [*cues,*events]:
        start,end = item["start"],item["end"]
        if not (0 <= start < end <= duration+.12) or not str(item.get("text","")).strip():
            parser.error(f"Invalid cue or event: {item}")
    for event in events:
        if event["kind"] not in {"title","chapter","type","label","input"}:
            parser.error(f"Unsupported event: {event['kind']}")
    theme = auto_theme(source) if args.theme=="auto" else args.theme
    out.mkdir(parents=True,exist_ok=True)
    saved_motion = [{**item, "path": str(clip[0])} for item, clip in zip(motion, clips)]
    (out/"timeline.json").write_text(json.dumps({"theme":theme,"captions":cues,"events":events,"motion":saved_motion},
                                                ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"captions.srt").write_text("\n\n".join(
        f"{i}\n{timecode(c['start'])} --> {timecode(c['end'])}\n{c['text']}" for i,c in enumerate(cues,1)
    )+"\n",encoding="utf-8")
    (out/"graphics.ass").write_text(build_ass(width,height,theme,args.font,cues,events,
                                             args.captions=="on",duration),encoding="utf-8")
    if args.plan_only:
        return
    starts = [e["start"] for e in events if e.get("sfx") and not args.silent_effects]
    cmd = ["ffmpeg","-v","error","-y","-i",str(source)]
    graph = []
    if starts:
        write_effects(out/"effects.wav",starts,duration)
        cmd += ["-i","effects.wav"]
        graph.append("[0:a:0][1:a:0]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.98:level=0:latency=1[a]")
        audio_options = ["-map","[a]","-c:a","aac","-b:a","192k"]
    else:
        audio_options = ["-map","0:a:0","-c:a","copy" if audio["codec_name"] in {"aac","mp3","alac"} else "aac"]
    for path, *_ in clips:
        cmd += ["-i",str(path)]
    if clips:
        graph.append(video_graph(picture["index"], clips, 2 if starts else 1))
        video_options = ["-map","[v]"]
    else:
        video_options = ["-map",f"0:{picture['index']}","-vf",
                         "pad=ceil(iw/2)*2:ceil(ih/2)*2,ass=graphics.ass"]
    if graph:
        cmd += ["-filter_complex_threads","2","-filter_complex",";".join(graph)]
    cmd += audio_options + video_options + [
        "-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",
        "-movflags","+faststart",str(temp)]
    subprocess.run(cmd,cwd=out,check=True)
    subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(temp),"-f","null","-"],check=True)
    temp.replace(final)
    print(final)


if __name__=="__main__":
    main()
