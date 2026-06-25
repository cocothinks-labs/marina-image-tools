import sys
import os
from pathlib import Path

EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}


def ensure_deps():
    try:
        from rembg import remove
        from PIL import Image
        return remove, Image
    except ImportError:
        print("\n  ERROR: rembg no está instalado.")
        print("  Ejecuta en una terminal:")
        print("    pip install rembg onnxruntime pillow\n")
        input("  Presiona Enter para salir...")
        sys.exit(1)


def process(path, remove_fn, Image):
    p = Path(path)
    if p.is_file():
        files = [p] if p.suffix.lower() in EXTS else []
    elif p.is_dir():
        files = [f for f in p.iterdir() if f.suffix.lower() in EXTS]
    else:
        print(f"  No encontrado: {path}")
        return

    if not files:
        print("  No se encontraron imágenes compatibles.")
        return

    out_dir = (p if p.is_dir() else p.parent) / "sin_fondo"
    out_dir.mkdir(exist_ok=True)
    print(f"  {len(files)} imagen(es) → {out_dir.name}/\n")

    for f in files:
        print(f"  [{f.name}]", end=" ", flush=True)
        try:
            img = Image.open(f).convert("RGBA")
            result = remove_fn(img)
            out = out_dir / (f.stem + "_nobg.png")
            result.save(out, "PNG")
            print(f"✓  ({result.size[0]}x{result.size[1]}px)")
        except Exception as e:
            print(f"✗  Error: {e}")

    print(f"\n  Listo. Carpeta: {out_dir}")


def main():
    if len(sys.argv) < 2:
        print("\n  REMOVE BG — Eliminador de fondos local (sin API)\n")
        print("  Arrastra una imagen o carpeta sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    remove_fn, Image = ensure_deps()
    for arg in sys.argv[1:]:
        process(arg.strip('"'), remove_fn, Image)

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
