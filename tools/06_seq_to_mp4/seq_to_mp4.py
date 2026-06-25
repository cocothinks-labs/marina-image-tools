import sys
import os
import subprocess
from pathlib import Path

EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}


def find_ffmpeg():
    for cmd in ["ffmpeg", r"C:\ffmpeg\bin\ffmpeg.exe", r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"]:
        try:
            subprocess.run([cmd, "-version"], capture_output=True, check=True)
            return cmd
        except Exception:
            pass
    return None


def detect_pattern(folder: Path):
    files = sorted([f for f in folder.iterdir() if f.suffix.lower() in EXTS])
    if not files:
        return None, None
    # ffmpeg glob pattern
    ext = files[0].suffix
    return files, ext


def process(folder_path, fps=24):
    folder = Path(folder_path)
    if folder.is_file():
        folder = folder.parent

    if not folder.is_dir():
        print(f"  Error: '{folder_path}' no es válido.")
        return

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("  ERROR: ffmpeg no encontrado.")
        print("  Descárgalo de https://ffmpeg.org/download.html")
        return

    files, ext = detect_pattern(folder)
    if not files:
        print("  No se encontraron imágenes.")
        return

    print(f"\n  Carpeta: {folder.name} — {len(files)} frames ({ext})")
    fps_str = input(f"  FPS [{fps}]: ").strip()
    fps = int(fps_str) if fps_str.isdigit() else fps

    out = folder.parent / (folder.name + ".mp4")
    pattern = str(folder / f"*{ext}")

    cmd = [
        ffmpeg, "-y",
        "-framerate", str(fps),
        "-pattern_type", "glob",
        "-i", pattern,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "slow",
        str(out)
    ]

    print(f"  Generando {out.name} a {fps} fps...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        size_mb = out.stat().st_size / 1024 / 1024
        print(f"  ✓ {out.name} ({size_mb:.1f} MB)")
    else:
        # ffmpeg glob doesn't work on Windows — fallback with concat
        print("  Probando método alternativo (concat)...")
        list_file = folder / "_ffmpeg_list.txt"
        with open(list_file, "w") as lf:
            for f in files:
                lf.write(f"file '{f}'\n")
        cmd2 = [
            ffmpeg, "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-framerate", str(fps),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
            str(out)
        ]
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        list_file.unlink(missing_ok=True)
        if result2.returncode == 0:
            size_mb = out.stat().st_size / 1024 / 1024
            print(f"  ✓ {out.name} ({size_mb:.1f} MB)")
        else:
            print(f"  ✗ Error ffmpeg:\n{result2.stderr[-500:]}")


def main():
    if len(sys.argv) < 2:
        print("\n  SEQ → MP4 — Convierte secuencia de imágenes a vídeo\n")
        print("  Arrastra una carpeta de PNGs/JPGs sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'))

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
