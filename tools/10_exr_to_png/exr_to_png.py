"""
EXR → PNG Batch Converter
Convierte archivos EXR de 32-bit a PNG 8-bit usando ffmpeg.
Tone mapping configurable: linear, reinhard, filmic.
"""
import sys
import subprocess
from pathlib import Path

EXR_EXTS = {'.exr'}


def find_ffmpeg():
    for cmd in ["ffmpeg", r"C:\ffmpeg\bin\ffmpeg.exe"]:
        try:
            subprocess.run([cmd, "-version"], capture_output=True, check=True)
            return cmd
        except Exception:
            pass
    return None


TONE_MAPS = {
    "1": ("linear",   "zscale=transfer=linear,format=gbrpf32le,zscale=transfer=bt709,format=rgb24"),
    "2": ("reinhard", "tonemap=tonemap=reinhard:desat=0"),
    "3": ("filmic",   "tonemap=tonemap=hable:desat=0.5"),
    "4": ("clip",     "exposure=0,format=rgb24"),
}


def process(path_str):
    p = Path(path_str)
    if p.is_file() and p.suffix.lower() in EXR_EXTS:
        files = [p]
    elif p.is_dir():
        files = list(p.rglob("*.exr")) + list(p.rglob("*.EXR"))
    else:
        print(f"  No se encontraron EXRs en: {path_str}")
        return

    if not files:
        print("  No se encontraron archivos EXR.")
        return

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("  ERROR: ffmpeg no encontrado.")
        return

    print(f"\n  {len(files)} archivo(s) EXR encontrado(s)")
    print("\n  Tone mapping:")
    for k, (name, _) in TONE_MAPS.items():
        print(f"  [{k}] {name}")
    mode = input("  Selección [1-4, default=3]: ").strip() or "3"
    if mode not in TONE_MAPS:
        mode = "3"

    tm_name, vf_filter = TONE_MAPS[mode]
    print(f"\n  Aplicando tone mapping: {tm_name}\n")

    for f in files:
        out = f.with_suffix(".png")
        cmd = [
            ffmpeg, "-y",
            "-i", str(f),
            "-vf", vf_filter,
            "-compression_level", "6",
            str(out)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            size_kb = out.stat().st_size // 1024
            print(f"  ✓ {f.name} → {out.name} ({size_kb} KB)")
        else:
            # Fallback: simple conversion
            cmd2 = [ffmpeg, "-y", "-i", str(f), "-compression_level", "6", str(out)]
            r2 = subprocess.run(cmd2, capture_output=True, text=True)
            if r2.returncode == 0:
                print(f"  ✓ {f.name} → {out.name} (conversión directa)")
            else:
                print(f"  ✗ {f.name}: {r2.stderr[-200:]}")

    print(f"\n  Conversión completa.")


def main():
    if len(sys.argv) < 2:
        print("\n  EXR → PNG — Conversor de EXR 32-bit a PNG\n")
        print("  Arrastra un archivo EXR o carpeta sobre el icono del escritorio.\n")
        input("  Presiona Enter para salir...")
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'))

    print()
    input("  Presiona Enter para cerrar...")


if __name__ == "__main__":
    main()
