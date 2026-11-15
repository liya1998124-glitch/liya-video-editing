"""Render a moving filmstrip from local videos. Requires Pillow and FFmpeg."""
import argparse
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw


def previews(path, width, height, fps, seconds):
    vf = (f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease,"
          f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x182c35")
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-threads", "2", "-i", str(path), "-an",
        "-t", str(seconds), "-filter_threads", "2", "-vf", vf,
        "-pix_fmt", "rgb24", "-f", "rawvideo", "-",
    ])
    stride = width * height * 3
    frames = [Image.frombytes("RGB", (width, height), raw[i:i+stride])
              for i in range(0, len(raw), stride)]
    if len(frames) < 2:
        raise ValueError(f"Expected a playable video clip: {path}")
    return frames


def render(paths, output, size, fps, seconds):
    width, height = size
    tile_w = round(width * .32)
    tile_h = round(tile_w * 9 / 16)
    clips = [previews(path, tile_w, tile_h, fps, seconds) for path in paths]
    pitch = tile_h + max(20, width // 30)
    cols = (clips[::2], clips[1::2] or clips[::2])
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
        "-video_size", f"{width}x{height}", "-framerate", str(fps), "-i", "-",
        "-an", "-c:v", "libx264", "-threads", "3", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", str(output),
    ]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as proc:
        for n in range(math.ceil(seconds * fps)):
            frame = Image.new("RGB", size, "#e9f7f4")
            pen = ImageDraw.Draw(frame)
            for j, lane in enumerate(cols):
                x = round(width * (.12 + .44*j))
                edge = width // 45
                pen.rectangle((x-edge, 0, x+tile_w+edge, height), fill="#173e48")
                shift = round(n * pitch / (fps * 1.55)) * (-1 if j == 0 else 1)
                for i in range(-2, math.ceil(height/pitch) + 2):
                    y = i*pitch + shift % pitch
                    clip = lane[(i-shift//pitch) % len(lane)]
                    frame.paste(clip[n % len(clip)], (x, y))
                for y in range(0, height, max(12, width//34)):
                    for pin in (x-edge+3, x+tile_w+3):
                        pen.rectangle((pin, y, pin+max(2, edge//3), y+7), fill="#a1f3e4")
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        if proc.wait():
            raise RuntimeError("Filmstrip render failed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clips", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--size", choices=("960x540", "540x960", "720x960", "720x720"), default="960x540")
    parser.add_argument("--seconds", type=float, default=5)
    args = parser.parse_args()
    if not .5 <= args.seconds <= 12 or len(args.clips) > 12:
        parser.error("Use 1–12 clips and a duration of 0.5–12 seconds.")
    if args.out.suffix.lower() != ".mp4" or any(args.out.resolve() == clip.resolve() or
        (args.out.exists() and clip.exists() and args.out.samefile(clip)) for clip in args.clips):
        parser.error("Provide a separate MP4 output path.")
    render(args.clips, args.out, tuple(map(int, args.size.split("x"))), 30, args.seconds)


if __name__ == "__main__":
    main()
