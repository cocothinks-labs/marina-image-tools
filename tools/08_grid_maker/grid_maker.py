import sys
import math
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("ERROR: Pillow no instalado. Ejecuta install.bat primero.")

EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}


def make_grid(images, cols, cell_w, cell_h, gap=20, bg=(255, 255, 255)):
    rows   = math.ceil(len(images) / cols)
    total_w = cols * cell_w + (cols + 1) * gap
    total_h = rows * cell_h + (rows + 1) * gap

    canvas = Image.new("RGB", (total_w, total_h), bg)

    for i, img in enumerate(images):
        row = i // cols
        col = i %  cols
        x   = gap + col * (cell_w + gap)
        y   = gap + row * (cell_h + gap)

        # Fit inside cell preserving ratio
        img.thumbnail((cell_w, cell_h), Image.LANCZOS)
        tw, th = img.size
        ox = x + (cell_w - tw) // 2
        oy = y + (cell_h - th) // 2
        canvas.paste(img, (ox, oy))

    return canvas


def process(folder_path):
    folder = Path(folder_path)
    if folder.is_file():
        folder = folder.parent

    if not folder.is_dir():
        print(f"  Error: '{folder_path}' no es válido.")
        return

    files = sorted([f for f in folder.iterdir() if f.suffix.lower() in EXTS])
    if not files:
        print("  No se encontraron imágenes.")
        return

    print(f"\n  {len(files)} imágenes en {folder.name}")

    cols_str = input(f"  Columnas [{math.ceil(math.sqrt(len(files)))}]: ").strip()
    cols     = int(cols_str) if cols_str.isdigit() else math.ceil(math.sqrt(len(files)))

    size_str = input("  Tamaño de celda en px [512]: ").strip()
    cell     = int(size_str) if size_str.isdigit() else 512

    gap_str  = input("  Separación entre imágenes en px [20]: ").strip()
    gap      = int(gap_str) if gap_str.isdigit() else 20

    images = []
    for f in files:
        try:
            images.append(Image.open(f).convert("RGB"))
        except Exception as e:
            print(f"  [ERROR] {f.name}: {e}")

    grid    = make_grid(images, cols, cell, cell, gap)
    out     = folder.parent / (folder.name + "_grid.png")
    grid.save(out, "PNG")

    rows = math.ceil(len(images) / cols)
    print(f"\n  Grid {cols}×{rows} guardado: {out.name}")
    print(f"  Tamaño: {grid.size[0]}x{grid.size[1]}px")


def main():
    if len(sys.argv) < 2:
        print("\n  GRID MAKER — Combina imágenes en una hoja de referencia\n")
        print("  Arrastra una carpeta de imágenes sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'))

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
