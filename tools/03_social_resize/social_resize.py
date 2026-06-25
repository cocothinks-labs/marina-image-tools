"""
Social Resize — Exporta imágenes a todos los formatos de red social.

Uso: arrastra una imagen o carpeta sobre el icono del escritorio.
Resultado: carpeta social/<nombre>/ junto al archivo original con los 6 JPGs.

Licencia: CC BY-NC-SA 4.0 — https://creativecommons.org/licenses/by-nc-sa/4.0/
Auto-framing con MediaPipe Face Detection (Apache 2.0) — © Google LLC
"""
import sys
from pathlib import Path

try:
    from PIL import Image, ImageFilter
except ImportError:
    sys.exit("ERROR: Pillow no instalado. Ejecuta install.bat primero.")

FORMATS = {
    "reels_9x16":   (1080, 1920),
    "feed_4x5":     (1080, 1350),
    "square_1x1":   (1080, 1080),
    "youtube_16x9": (1920, 1080),
    "twitter_16x9": (1200,  675),
    "linkedin_1x1": (1200, 1200),
}

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def detect_subject_center(img_rgb) -> tuple[float, float]:
    """
    Detecta el centro del sujeto principal (cara) con MediaPipe.
    Retorna (cx, cy) normalizados 0.0–1.0.
    Fallback silencioso a (0.5, 0.5) si MediaPipe no está disponible.

    MediaPipe Face Detection — Apache 2.0 — © Google LLC
    https://github.com/google-ai-edge/mediapipe
    """
    try:
        import mediapipe as mp
    except ImportError:
        return 0.5, 0.5

    try:
        with mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.4
        ) as detector:
            results = detector.process(img_rgb)
        if results.detections:
            best = max(
                results.detections,
                key=lambda d: (
                    d.location_data.relative_bounding_box.width
                    * d.location_data.relative_bounding_box.height
                ),
            )
            bb = best.location_data.relative_bounding_box
            return (
                max(0.0, min(1.0, bb.xmin + bb.width / 2)),
                max(0.0, min(1.0, bb.ymin + bb.height / 2)),
            )
    except Exception as e:
        print(f"  [Auto-encuadre] advertencia: {e}")

    return 0.5, 0.5


def smart_fit(
    img: Image.Image,
    tw: int,
    th: int,
    cx: float = 0.5,
    cy: float = 0.5,
    blur_radius: int = 40,
) -> Image.Image:
    """
    Redimensiona img al tamaño (tw, th) manteniendo el sujeto en cuadro.

    - Mismo ratio  → escala directa.
    - Más ancho    → escala a altura, recorta ancla en cx (posición del sujeto).
    - Más alto     → escala a ancho, rellena con fondo desenfocado (blur-pad).
    """
    sw, sh = img.size
    sr = sw / sh
    tr = tw / th

    if abs(sr - tr) < 0.02:
        return img.resize((tw, th), Image.LANCZOS)

    if sr > tr:
        nh = th
        nw = int(sw * th / sh)
        scaled = img.resize((nw, nh), Image.LANCZOS)
        cx_px = int(cx * nw)
        x = max(0, min(nw - tw, cx_px - tw // 2))
        return scaled.crop((x, 0, x + tw, th))

    nw = tw
    nh = int(sh * tw / sw)
    scaled = img.resize((nw, nh), Image.LANCZOS)
    bg = img.resize((tw, th), Image.LANCZOS).filter(
        ImageFilter.GaussianBlur(radius=blur_radius)
    )
    y = (th - nh) // 2
    bg.paste(scaled, (0, y))
    return bg


def process(path: str) -> None:
    p = Path(path)
    files = [p] if p.is_file() and p.suffix.lower() in EXTS else []
    if p.is_dir():
        files = [f for f in p.iterdir() if f.suffix.lower() in EXTS]

    for f in files:
        print(f"\n  {f.name}")

        img = Image.open(f).convert("RGB")

        try:
            import numpy as np
            img_rgb = np.array(img)
            cx, cy = detect_subject_center(img_rgb)
            label = f"cx={cx:.2f}" if cx != 0.5 or cy != 0.5 else "centro"
        except ImportError:
            cx, cy = 0.5, 0.5
            label = "centro"

        print(f"  Auto-encuadre: {label}")

        out_dir = f.parent / "social" / f.stem
        out_dir.mkdir(parents=True, exist_ok=True)

        for name, (tw, th) in FORMATS.items():
            result = smart_fit(img, tw, th, cx=cx, cy=cy)
            out = out_dir / f"{f.stem}_{name}.jpg"
            result.save(out, "JPEG", quality=95, optimize=True)
            print(f"    {name:20s} {tw}x{th}")

    print(f"\n  Versiones guardadas en: social/")


def main() -> None:
    if len(sys.argv) < 2:
        print("\n  SOCIAL RESIZE — Exporta a todos los formatos de red social\n")
        print("  Auto-encuadre con MediaPipe (Google) si está instalado.\n")
        print("  Arrastra una imagen o carpeta sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'))

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
