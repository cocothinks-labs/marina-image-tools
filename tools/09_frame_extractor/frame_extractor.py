import sys
import subprocess
from pathlib import Path

VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.mxf', '.m4v'}


def find_ffmpeg():
    for cmd in ["ffmpeg", r"C:\ffmpeg\bin\ffmpeg.exe"]:
        try:
            subprocess.run([cmd, "-version"], capture_output=True, check=True)
            return cmd
        except Exception:
            pass
    return None


def get_duration(ffmpeg, video):
    r = subprocess.run(
        [ffmpeg, "-i", str(video)],
        capture_output=True, text=True
    )
    for line in r.stderr.splitlines():
        if "Duration" in line:
            parts = line.strip().split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return None


def process(video_path):
    p = Path(video_path)
    if p.is_dir():
        files = [f for f in p.iterdir() if f.suffix.lower() in VIDEO_EXTS]
    elif p.is_file() and p.suffix.lower() in VIDEO_EXTS:
        files = [p]
    else:
        print(f"  No es un vídeo compatible: {video_path}")
        return

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("  ERROR: ffmpeg no encontrado.")
        return

    for video in files:
        print(f"\n  Vídeo: {video.name}")
        duration = get_duration(ffmpeg, video)
        if duration:
            print(f"  Duración: {duration:.1f}s")

        print("\n  Modo de extracción:")
        print("  [1] Cada N segundos")
        print("  [2] N frames en total (distribuidos uniformemente)")
        print("  [3] Puntos clave: 0%, 25%, 50%, 75%, 100%")
        mode = input("  Modo [1/2/3]: ").strip() or "1"

        out_dir = video.parent / (video.stem + "_frames")
        out_dir.mkdir(exist_ok=True)

        if mode == "1":
            n = input("  Cada cuántos segundos [5]: ").strip() or "5"
            cmd = [ffmpeg, "-y", "-i", str(video),
                   "-vf", f"fps=1/{n}",
                   str(out_dir / "frame_%04d.png")]
        elif mode == "2":
            n = input("  Número de frames [10]: ").strip() or "10"
            if duration:
                interval = duration / int(n)
                cmd = [ffmpeg, "-y", "-i", str(video),
                       "-vf", f"fps=1/{interval:.3f}",
                       str(out_dir / "frame_%04d.png")]
            else:
                cmd = [ffmpeg, "-y", "-i", str(video),
                       "-vf", f"select='not(mod(n,{max(1, 100//int(n))}))'",
                       "-vsync", "vfr",
                       str(out_dir / "frame_%04d.png")]
        else:  # mode 3
            if duration:
                timestamps = [0, duration*0.25, duration*0.5, duration*0.75, duration*0.99]
                for i, ts in enumerate(timestamps):
                    cmd = [ffmpeg, "-y", "-ss", f"{ts:.2f}",
                           "-i", str(video), "-frames:v", "1",
                           str(out_dir / f"frame_{i+1:02d}_pct{int(i*25)}.png")]
                    subprocess.run(cmd, capture_output=True)
                print(f"  ✓ 5 frames extraídos en: {out_dir.name}/")
                continue
            else:
                cmd = [ffmpeg, "-y", "-i", str(video),
                       "-vf", "select='eq(n,0)+eq(n,25)+eq(n,50)+eq(n,75)+eq(n,99)'",
                       "-vsync", "vfr", str(out_dir / "frame_%04d.png")]

        result = subprocess.run(cmd, capture_output=True, text=True)
        frames = list(out_dir.glob("*.png"))
        if result.returncode == 0 or frames:
            print(f"  ✓ {len(frames)} frames extraídos en: {out_dir.name}/")
        else:
            print(f"  ✗ Error: {result.stderr[-300:]}")


def main():
    if len(sys.argv) < 2:
        print("\n  FRAME EXTRACTOR — Extrae frames de vídeo\n")
        print("  Arrastra un vídeo o carpeta sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'))

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
