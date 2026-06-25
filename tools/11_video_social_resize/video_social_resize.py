import sys
import subprocess
from pathlib import Path

FORMATS = {
    "reels_9x16":   (1080, 1920),
    "feed_4x5":     (1080, 1350),
    "square_1x1":   (1080, 1080),
    "youtube_16x9": (1920, 1080),
    "twitter_16x9": (1200,  675),
    "linkedin_1x1": (1200, 1200),
}

VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".mxf"}


def find_bin(names: list[str]) -> str | None:
    for cmd in names:
        try:
            subprocess.run([cmd, "-version"], capture_output=True, check=True)
            return cmd
        except Exception:
            pass
    return None


def get_video_size(ffprobe: str, video: Path) -> tuple[int, int]:
    r = subprocess.run(
        [ffprobe, "-v", "quiet", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=s=x:p=0", str(video)],
        capture_output=True, text=True,
    )
    w, h = r.stdout.strip().split("x")
    return int(w), int(h)


def build_filter(src_w: int, src_h: int, tw: int, th: int) -> tuple[str, str]:
    """
    Returns (filter_type, filter_string).
    filter_type is 'vf' for simple filters or 'complex' for filtergraph.

    Strategy (mirrors image social_resize):
      - Same ratio  → scale
      - Source wider → scale to fill height, crop center width
      - Source taller → blurred background + centered foreground
    """
    sr = src_w / src_h
    tr = tw / th

    if abs(sr - tr) < 0.02:
        return "vf", f"scale={tw}:{th}"

    if sr > tr:
        # Source is wider than target → crop
        return "vf", (
            f"scale=-2:{th}:force_original_aspect_ratio=increase,"
            f"crop={tw}:{th}"
        )

    # Source is taller than target → blur-pad
    # Background: scale to fill, blur. Foreground: scale to fit width.
    return "complex", (
        f"[0:v]scale={tw}:{th}:force_original_aspect_ratio=increase,"
        f"crop={tw}:{th},boxblur=40:40[bg];"
        f"[0:v]scale={tw}:-2[fg];"
        f"[bg][fg]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2[v]"
    )


def process(video_path: str, ffmpeg: str, ffprobe: str) -> None:
    p = Path(video_path)
    if p.is_dir():
        files = [f for f in p.iterdir() if f.suffix.lower() in VIDEO_EXTS]
    elif p.is_file() and p.suffix.lower() in VIDEO_EXTS:
        files = [p]
    else:
        print(f"  No es un vídeo compatible: {video_path}")
        return

    for video in files:
        print(f"\n  {video.name}")

        try:
            src_w, src_h = get_video_size(ffprobe, video)
            print(f"  Resolución: {src_w}x{src_h}")
        except Exception as e:
            print(f"  [ERROR] No se pudo leer la resolución: {e}")
            continue

        out_dir = video.parent / "social" / video.stem
        out_dir.mkdir(parents=True, exist_ok=True)

        for name, (tw, th) in FORMATS.items():
            out = out_dir / f"{video.stem}_{name}.mp4"
            filter_type, filter_str = build_filter(src_w, src_h, tw, th)

            cmd = [ffmpeg, "-y", "-i", str(video)]

            if filter_type == "complex":
                cmd += ["-filter_complex", filter_str, "-map", "[v]", "-map", "0:a?"]
            else:
                cmd += ["-vf", filter_str, "-map", "0:v", "-map", "0:a?"]

            cmd += [
                "-c:v", "libx264",
                "-crf", "20",
                "-preset", "fast",
                "-c:a", "aac",
                "-b:a", "192k",
                "-movflags", "+faststart",
                str(out),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and out.exists():
                size_mb = out.stat().st_size / 1024 / 1024
                print(f"    {name:20s} {tw}x{th}  {size_mb:.1f} MB")
            else:
                print(f"    {name:20s} ERROR")
                last = result.stderr.strip().splitlines()
                if last:
                    print(f"      {last[-1]}")

    print(f"\n  Versiones guardadas en: social/")


def main() -> None:
    ffmpeg = find_bin(["ffmpeg", r"C:\ffmpeg\bin\ffmpeg.exe"])
    ffprobe = find_bin(["ffprobe", r"C:\ffmpeg\bin\ffprobe.exe"])

    if not ffmpeg or not ffprobe:
        print("\n  ERROR: ffmpeg no encontrado.")
        print("  Descárgalo de https://ffmpeg.org y extrae en C:\\ffmpeg\\")
        input("\n  Presiona Enter para salir...")
        return

    if len(sys.argv) < 2:
        print("\n  VIDEO SOCIAL RESIZE — Exporta vídeos a todos los formatos de red social\n")
        print("  Formatos: Instagram Reels (9:16), Feed (4:5), Square (1:1),")
        print("            YouTube (16:9), Twitter (16:9), LinkedIn (1:1)\n")
        print("  Arrastra un vídeo o carpeta sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'), ffmpeg, ffprobe)

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
