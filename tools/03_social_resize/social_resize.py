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


def smart_fit(img: Image.Image, tw: int, th: int, blur_radius: int = 40) -> Image.Image:
    sw, sh = img.size
    sr = sw / sh
    tr = tw / th

    if abs(sr - tr) < 0.02:
        return img.resize((tw, th), Image.LANCZOS)

    if sr > tr:
        nh = th
        nw = int(sw * th / sh)
        r = img.resize((nw, nh), Image.LANCZOS)
        x = (nw - tw) // 2
        return r.crop((x, 0, x + tw, th))
    else:
        nw = tw
        nh = int(sh * tw / sw)
        r = img.resize((nw, nh), Image.LANCZOS)
        bg = img.resize((tw, th), Image.LANCZOS).filter(
            ImageFilter.GaussianBlur(radius=blur_radius)
        )
        y = (th - nh) // 2
        bg.paste(r, (0, y))
        return bg


def process(path: str) -> None:
    p = Path(path)
    files = [p] if p.is_file() and p.suffix.lower() in EXTS else []
    if p.is_dir():
        files = [f for f in p.iterdir() if f.suffix.lower() in EXTS]

    for f in files:
        print(f"\n  {f.name}")
        out_dir = f.parent / "social" / f.stem
        out_dir.mkdir(parents=True, exist_ok=True)

        img = Image.open(f).convert("RGB")
        for name, (tw, th) in FORMATS.items():
            result = smart_fit(img, tw, th)
            out = out_dir / f"{f.stem}_{name}.jpg"
            result.save(out, "JPEG", quality=95, optimize=True)
            print(f"    {name:20s} {tw}x{th}")

    print(f"\n  Versiones guardadas en: social/")


def main() -> None:
    if len(sys.argv) < 2:
        print("\n  SOCIAL RESIZE — Exporta a todos los formatos de red social\n")
        print("  Arrastra una imagen o carpeta sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'))

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
