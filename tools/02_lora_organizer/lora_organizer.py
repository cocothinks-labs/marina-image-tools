import sys
from pathlib import Path

try:
    from PIL import Image
    import imagehash
except ImportError:
    sys.exit("ERROR: Pillow o imagehash no instalados. Ejecuta install.bat primero.")

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def ask(prompt: str, default: str) -> str:
    val = input(f"  {prompt} [{default}]: ").strip()
    return val if val else default


def remove_duplicates(files: list[Path], threshold: int = 8) -> list[Path]:
    print(f"  Detectando duplicados (threshold={threshold})...")
    hashes: dict[Path, imagehash.ImageHash] = {}
    for f in files:
        try:
            hashes[f] = imagehash.phash(Image.open(f))
        except Exception:
            pass

    file_list = list(hashes.keys())
    keep: list[Path] = []
    visited: set[Path] = set()

    for i, f1 in enumerate(file_list):
        if f1 in visited:
            continue
        group = [f1]
        for f2 in file_list[i + 1:]:
            if f2 not in visited and (hashes[f1] - hashes[f2]) <= threshold:
                group.append(f2)
                visited.add(f2)
        visited.add(f1)
        group.sort(key=lambda f: f.stat().st_size, reverse=True)
        keep.append(group[0])
        if len(group) > 1:
            dupes = [g.name for g in group[1:]]
            print(f"    [DUP] conserva {group[0].name}, descarta {dupes}")

    print(f"  {len(files) - len(keep)} duplicados eliminados, {len(keep)} únicas")
    return keep


def process(folder_path: str) -> None:
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"  Error: '{folder_path}' no es una carpeta.")
        return

    files = [f for f in folder.iterdir() if f.suffix.lower() in EXTS]
    if not files:
        print("  No se encontraron imágenes.")
        return

    print(f"\n  Carpeta: {folder.name} — {len(files)} imágenes\n")

    trigger = ask("Palabra trigger para el LoRA", folder.name.lower().replace(" ", "_"))
    size_str = ask("Tamaño de salida (512 / 768 / 1024)", "768")
    prefix = ask("Repeticiones (ej: 10, 15, 20)", "10")

    try:
        size = int(size_str)
    except ValueError:
        size = 768

    unique = remove_duplicates(files)

    out_dir = folder / f"dataset_{trigger}"
    out_dir.mkdir(exist_ok=True)
    print(f"\n  Generando dataset en: {out_dir.name}/")

    for i, f in enumerate(unique, 1):
        try:
            img = Image.open(f).convert("RGB")
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            img = img.resize((size, size), Image.LANCZOS)

            stem = f"{prefix}_{trigger}_{i:03d}"
            img_out = out_dir / f"{stem}.png"
            txt_out = out_dir / f"{stem}.txt"

            img.save(img_out, "PNG")
            txt_out.write_text(trigger, encoding="utf-8")
            print(f"  [{i:03d}] {stem}.png + .txt")
        except Exception as e:
            print(f"  [ERROR] {f.name}: {e}")

    print(f"\n  Dataset listo: {len(unique)} imágenes + captions en {out_dir}")


def main() -> None:
    if len(sys.argv) < 2:
        print("\n  LORA ORGANIZER — Prepara datasets para entrenar LoRAs\n")
        print("  Arrastra una carpeta de imágenes sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'))

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
