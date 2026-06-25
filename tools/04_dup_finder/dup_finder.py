import sys
import shutil
from pathlib import Path

try:
    from PIL import Image
    import imagehash
except ImportError:
    sys.exit("ERROR: Pillow o imagehash no instalados. Ejecuta install.bat primero.")

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def find_duplicates(files: list[Path], threshold: int = 8) -> list[list[Path]]:
    print("  Calculando hashes perceptuales...")
    hashes: dict[Path, imagehash.ImageHash] = {}
    for f in files:
        try:
            hashes[f] = imagehash.phash(Image.open(f))
        except Exception as e:
            print(f"  [SKIP] {f.name}: {e}")

    file_list = list(hashes.keys())
    groups: list[list[Path]] = []
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
        if len(group) > 1:
            groups.append(group)

    return groups


def process(folder_path: str, threshold: int = 8) -> None:
    folder = Path(folder_path)
    if not folder.is_dir():
        print(f"  Error: '{folder_path}' no es una carpeta.")
        return

    files = [f for f in folder.rglob("*")
             if f.suffix.lower() in EXTS and "duplicados" not in f.parts]

    if not files:
        print("  No se encontraron imágenes.")
        return

    print(f"\n  Carpeta: {folder.name} — {len(files)} imágenes")

    groups = find_duplicates(files, threshold)

    if not groups:
        print("\n  No se encontraron duplicados. La carpeta está limpia.")
        return

    dup_dir = folder / "duplicados"
    dup_dir.mkdir(exist_ok=True)

    total_moved = 0
    for group in groups:
        group.sort(key=lambda f: f.stat().st_size, reverse=True)
        keeper = group[0]
        print(f"\n  GRUPO: conserva → {keeper.name}")
        for d in group[1:]:
            dest = dup_dir / d.name
            if dest.exists():
                dest = dup_dir / (d.stem + "_2" + d.suffix)
            shutil.move(str(d), str(dest))
            print(f"    movido → duplicados/{dest.name}")
            total_moved += 1

    print(f"\n  {total_moved} duplicados movidos a: duplicados/")
    print("  Revísalos antes de borrar definitivamente.")


def main() -> None:
    if len(sys.argv) < 2:
        print("\n  DUP FINDER — Detector de imágenes duplicadas\n")
        print("  Arrastra una carpeta sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'))

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
