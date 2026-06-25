import sys
import os
from pathlib import Path

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow no está instalado. Ejecuta: pip install pillow")
    sys.exit(1)


def find_separators(means, threshold=240, min_gap=15):
    """Find contiguous bands where mean pixel value >= threshold."""
    separators = []
    in_sep = False
    start = 0
    for i, v in enumerate(means):
        if v >= threshold:
            if not in_sep:
                in_sep = True
                start = i
        else:
            if in_sep:
                in_sep = False
                if i - start >= min_gap:
                    separators.append((start, i))
    if in_sep and len(means) - start >= min_gap:
        separators.append((start, len(means)))
    return separators


def sep_to_cuts(separators, total):
    """Convert separator bands to cut positions (midpoints), including 0 and total."""
    cuts = [0]
    for s, e in separators:
        cuts.append((s + e) // 2)
    cuts.append(total)
    return cuts


def compute_means(img_gray, threshold=240, min_gap=15):
    width, height = img_gray.size
    if HAS_NUMPY:
        arr = np.array(img_gray, dtype=float)
        col_means = arr.mean(axis=0).tolist()
        row_means = arr.mean(axis=1).tolist()
    else:
        pixels = list(img_gray.getdata())
        col_means = []
        for x in range(width):
            vals = [pixels[y * width + x] for y in range(height)]
            col_means.append(sum(vals) / height)
        row_means = []
        for y in range(height):
            row = pixels[y * width:(y + 1) * width]
            row_means.append(sum(row) / width)
    return col_means, row_means


def split_image(image_path, threshold=240, min_gap=15, padding=4, min_cell=200):
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"Error: no se encuentra '{image_path}'")
        return

    print(f"\nProcesando: {img_path.name}")
    img = Image.open(img_path).convert("RGB")
    width, height = img.size
    print(f"  Tamaño: {width} x {height} px")

    gray = img.convert("L")
    col_means, row_means = compute_means(gray, threshold, min_gap)

    col_seps = find_separators(col_means, threshold, min_gap)
    row_seps = find_separators(row_means, threshold, min_gap)

    x_cuts = sep_to_cuts(col_seps, width)
    y_cuts = sep_to_cuts(row_seps, height)

    cols = len(x_cuts) - 1
    rows = len(y_cuts) - 1
    print(f"  Cuadrícula detectada: {cols} col × {rows} fil = {cols * rows} celdas")

    output_dir = img_path.parent / img_path.stem
    output_dir.mkdir(exist_ok=True)

    count = 0
    for ri, (y1, y2) in enumerate(zip(y_cuts[:-1], y_cuts[1:])):
        for ci, (x1, x2) in enumerate(zip(x_cuts[:-1], x_cuts[1:])):
            cw = x2 - x1
            ch = y2 - y1
            if cw < min_cell or ch < min_cell:
                continue

            cx1 = max(0, x1 + padding)
            cy1 = max(0, y1 + padding)
            cx2 = min(width,  x2 - padding)
            cy2 = min(height, y2 - padding)

            crop = img.crop((cx1, cy1, cx2, cy2))
            count += 1
            out_file = output_dir / f"pose_{count:02d}.png"
            crop.save(out_file, "PNG")
            print(f"  [{count:02d}] pose_{count:02d}.png  ({cx2-cx1}x{cy2-cy1}px)")

    print(f"\n  {count} poses guardadas en:")
    print(f"  {output_dir}\n")
    return str(output_dir)


def main():
    if len(sys.argv) < 2:
        print("Uso: arrastra una imagen sobre el .bat o ejecuta:")
        print("  python split_poses.py <ruta_imagen>")
        input("\nPresiona Enter para salir...")
        sys.exit(0)

    for arg in sys.argv[1:]:
        split_image(arg.strip('"'))


if __name__ == "__main__":
    main()
