"""
Video Social Resize — Exporta vídeos a todos los formatos de red social.

Uso: arrastra un vídeo o carpeta sobre el icono del escritorio.
Resultado: carpeta social/<nombre>/ junto al original con los 6 MOV (ProRes).

Licencia: CC BY-NC-SA 4.0 — https://creativecommons.org/licenses/by-nc-sa/4.0/
Auto-framing con MediaPipe Face Detection (Apache 2.0) — © Google LLC
"""
import sys
import statistics
import subprocess
from pathlib import Path

FORMATS = {
    "reels_9x16":   (1080, 1920),
    "feed_4x5":     (1080, 1350),
    "square_1x1":   (1080, 1080),
    "youtube_16x9": (1920, 1080),
    "twitter_16x9": (1200,  674),  # 675 es impar — los codecs de vídeo requieren dimensiones pares
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


def get_video_info(ffprobe: str, video: Path) -> tuple[int, int, str]:
    r = subprocess.run(
        [ffprobe, "-v", "quiet", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,pix_fmt",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True,
    )
    lines = r.stdout.strip().splitlines()
    return int(lines[0]), int(lines[1]), lines[2]


_HIGH_BIT_DEPTH = {"p010", "p016", "10le", "10be", "12le", "12be", "14le", "14be", "16le", "16be"}


def is_high_bit_depth(pix_fmt: str) -> bool:
    return any(tag in pix_fmt for tag in _HIGH_BIT_DEPTH)


def prores_params(high_bit: bool) -> list[str]:
    if high_bit:
        return ["-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuv444p10le", "-c:a", "pcm_s24le"]
    return ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le", "-c:a", "pcm_s16le"]


def sample_subject_cx(video: Path, n_samples: int = 20) -> float:
    """
    Muestrea N frames del vídeo, detecta la cara principal con MediaPipe
    y devuelve la mediana del centro X (0.0–1.0).
    Retorna 0.5 (centro) si MediaPipe no está disponible o no detecta caras.

    MediaPipe Face Detection — Apache 2.0 — © Google LLC
    https://github.com/google-ai-edge/mediapipe
    """
    try:
        import cv2
        import mediapipe as mp

        cap = cv2.VideoCapture(str(video))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            cap.release()
            return 0.5

        step = max(1, total // n_samples)
        cx_list: list[float] = []

        with mp.solutions.face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        ) as detector:
            for i in range(0, total, step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if not ret:
                    continue
                results = detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                if results.detections:
                    best = max(
                        results.detections,
                        key=lambda d: (
                            d.location_data.relative_bounding_box.width
                            * d.location_data.relative_bounding_box.height
                        ),
                    )
                    bb = best.location_data.relative_bounding_box
                    cx_list.append(
                        max(0.0, min(1.0, bb.xmin + bb.width / 2))
                    )

        cap.release()

        if cx_list:
            return statistics.median(cx_list)

    except Exception:
        pass

    return 0.5


def _even(n: int) -> int:
    return n if n % 2 == 0 else n - 1


def build_filter(
    src_w: int, src_h: int, tw: int, th: int, cx: float = 0.5
) -> tuple[str, str]:
    """
    Construye el filtro ffmpeg para redimensionar con auto-encuadre.
    Retorna (tipo, filtro) donde tipo es 'vf' o 'complex'.

    - Mismo ratio  → scale.
    - Más ancho    → scale a altura, crop ancla en cx (sujeto detectado).
    - Más alto     → blur-pad (fondo desenfocado + sujeto centrado).
    """
    tw, th = _even(tw), _even(th)
    sr = src_w / src_h
    tr = tw / th

    if abs(sr - tr) < 0.02:
        return "vf", f"scale={tw}:{th}"

    if sr > tr:
        scale_w = _even(int(src_w * th / src_h))
        crop_x = _even(max(0, min(scale_w - tw, int(cx * scale_w - tw // 2))))
        return "vf", f"scale={scale_w}:{th},crop={tw}:{th}:{crop_x}:0"

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
            src_w, src_h, pix_fmt = get_video_info(ffprobe, video)
        except Exception as e:
            print(f"  [ERROR] No se pudo leer la resolución: {e}")
            continue

        high_bit = is_high_bit_depth(pix_fmt)
        codec_label = "ProRes 4444" if high_bit else "ProRes 422 HQ"

        print(f"  Analizando sujeto en {20} frames muestreados...")
        cx = sample_subject_cx(video)
        label = f"cara detectada cx={cx:.2f}" if cx != 0.5 else "centro (sin cara detectada)"
        print(f"  Resolución: {src_w}x{src_h} [{pix_fmt}] — {codec_label} — Auto-encuadre: {label}")

        out_dir = video.parent / "social" / video.stem
        out_dir.mkdir(parents=True, exist_ok=True)

        for name, (tw, th) in FORMATS.items():
            out = out_dir / f"{video.stem}_{name}.mov"
            filter_type, filter_str = build_filter(src_w, src_h, tw, th, cx=cx)

            cmd = [ffmpeg, "-y", "-i", str(video)]
            if filter_type == "complex":
                cmd += ["-filter_complex", filter_str, "-map", "[v]", "-map", "0:a?"]
            else:
                cmd += ["-vf", filter_str, "-map", "0:v", "-map", "0:a?"]

            cmd += prores_params(high_bit) + [str(out)]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0 and out.exists():
                size_mb = out.stat().st_size / 1024 / 1024
                print(f"    {name:20s} {tw}x{th}  {size_mb:.1f} MB")
            else:
                print(f"    {name:20s} ERROR")
                lines = result.stderr.strip().splitlines()
                if lines:
                    print(f"      {lines[-1]}")

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
        print("  Auto-encuadre con MediaPipe (Google) si está instalado.\n")
        print("  Arrastra un vídeo o carpeta sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'), ffmpeg, ffprobe)

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
