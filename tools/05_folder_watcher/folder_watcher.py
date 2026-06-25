"""
FolderWatcher — Organiza automáticamente archivos nuevos por fecha.
Uso:
  - Arrastrar una carpeta para vigilarla una vez (modo one-shot)
  - Ejecutar sin argumentos para iniciar el watcher continuo
  - El config.txt guarda la carpeta vigilada entre sesiones
"""
import sys
import os
import time
import shutil
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path(__file__).parent / "config.txt"
EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff',
        '.mp4', '.mov', '.avi', '.gif'}
CHECK_INTERVAL = 30  # segundos


def load_config():
    if CONFIG_FILE.exists():
        return Path(CONFIG_FILE.read_text(encoding="utf-8").strip())
    return None


def save_config(folder: Path):
    CONFIG_FILE.write_text(str(folder), encoding="utf-8")


def organize_folder(folder: Path, verbose=True):
    moved = 0
    for f in folder.iterdir():
        if not f.is_file():
            continue
        if f.suffix.lower() not in EXTS:
            continue
        date_str = datetime.fromtimestamp(f.stat().st_ctime).strftime("%Y-%m-%d")
        dest_dir = folder / date_str
        dest_dir.mkdir(exist_ok=True)
        dest = dest_dir / f.name
        if dest.exists():
            dest = dest_dir / (f.stem + f"_{int(time.time())}" + f.suffix)
        shutil.move(str(f), str(dest))
        if verbose:
            print(f"  {f.name} → {date_str}/")
        moved += 1
    return moved


def watch_loop(folder: Path):
    print(f"\n  Vigilando: {folder}")
    print("  Los archivos nuevos se organizarán por fecha automáticamente.")
    print("  Cierra esta ventana para detener.\n")
    while True:
        try:
            moved = organize_folder(folder, verbose=True)
            if moved:
                print(f"  [{datetime.now().strftime('%H:%M:%S')}] {moved} archivos organizados\n")
        except Exception as e:
            print(f"  [ERROR] {e}")
        time.sleep(CHECK_INTERVAL)


def main():
    if len(sys.argv) >= 2:
        folder = Path(sys.argv[1].strip('"'))
        if not folder.is_dir():
            print(f"  Error: '{folder}' no es una carpeta válida.")
            input("  Presiona Enter para salir...")
            return

        save_config(folder)
        print(f"\n  Organizando: {folder.name}...")
        moved = organize_folder(folder, verbose=True)
        print(f"\n  {moved} archivos organizados.")
        print(f"  Carpeta guardada como destino de vigilancia.")
        choice = input("\n  ¿Iniciar vigilancia continua? (s/n): ").strip().lower()
        if choice == 's':
            watch_loop(folder)
        else:
            input("  Presiona Enter para cerrar...")
        return

    # No argument — use saved config or ask
    folder = load_config()
    if not folder or not folder.is_dir():
        print("\n  FOLDER WATCHER — Organizador automático por fecha\n")
        folder_str = input("  Pega la ruta de la carpeta a vigilar: ").strip().strip('"')
        folder = Path(folder_str)
        if not folder.is_dir():
            print("  Ruta no válida.")
            input("  Presiona Enter para salir...")
            return
        save_config(folder)

    watch_loop(folder)


if __name__ == "__main__":
    main()
