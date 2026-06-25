import sys
import json
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("ERROR: Pillow no instalado. Ejecuta install.bat primero.")


def extract_comfy_meta(img_path: Path):
    img = Image.open(img_path)
    meta = img.info  # PNG tEXt chunks

    result = {}
    for key, value in meta.items():
        if key in ("prompt", "workflow", "parameters", "Comment", "comment"):
            try:
                result[key] = json.loads(value)
            except Exception:
                result[key] = value

    if not result:
        result["raw_meta"] = dict(meta) if meta else {"(vacío)": "Este PNG no tiene metadatos embebidos."}

    return result


def format_meta(meta: dict) -> str:
    lines = []
    for key, val in meta.items():
        lines.append(f"{'='*60}")
        lines.append(f"  {key.upper()}")
        lines.append(f"{'='*60}")
        if isinstance(val, dict):
            lines.append(json.dumps(val, indent=2, ensure_ascii=False))
        elif isinstance(val, list):
            lines.append(json.dumps(val, indent=2, ensure_ascii=False))
        else:
            lines.append(str(val))
        lines.append("")
    return "\n".join(lines)


def extract_summary(meta: dict) -> str:
    """Try to pull key info from ComfyUI prompt structure."""
    prompt = meta.get("prompt", {})
    if not isinstance(prompt, dict):
        return ""

    models, loras, samplers, seeds, texts = [], [], [], [], []

    for node in prompt.values():
        if not isinstance(node, dict):
            continue
        cls  = node.get("class_type", "")
        inp  = node.get("inputs", {})

        if "CheckpointLoader" in cls or "UNETLoader" in cls:
            models.append(inp.get("ckpt_name") or inp.get("unet_name", ""))
        if "LoraLoader" in cls:
            loras.append(f"{inp.get('lora_name','')} (str={inp.get('strength_model',1):.2f})")
        if "KSampler" in cls:
            samplers.append(f"steps={inp.get('steps')} cfg={inp.get('cfg')} "
                            f"sampler={inp.get('sampler_name')} scheduler={inp.get('scheduler')}")
            seeds.append(str(inp.get("seed", inp.get("noise_seed", "?"))))
        if cls in ("CLIPTextEncode",) and "text" in inp:
            text = str(inp["text"])[:120]
            if text not in texts:
                texts.append(text)

    lines = []
    if models:  lines.append(f"Modelo:    {', '.join(filter(None, models))}")
    if loras:   lines.append(f"LoRAs:     {'; '.join(filter(None, loras))}")
    if samplers: lines.append(f"Sampler:   {samplers[0]}")
    if seeds:   lines.append(f"Seeds:     {', '.join(seeds)}")
    if texts:
        lines.append("Prompts:")
        for t in texts:
            lines.append(f"  · {t}")
    return "\n".join(lines)


def show_gui(img_path: Path, meta: dict):
    root = tk.Tk()
    root.title(f"MetaViewer — {img_path.name}")
    root.geometry("900x700")
    root.configure(bg="#1e1e2e")

    # Summary bar
    summary = extract_summary(meta)
    if summary:
        lbl = tk.Label(root, text=summary, bg="#313244", fg="#cdd6f4",
                       font=("Consolas", 10), justify="left", anchor="w",
                       padx=10, pady=8, wraplength=870)
        lbl.pack(fill="x", padx=10, pady=(10, 0))

    # Raw text area
    txt = scrolledtext.ScrolledText(root, bg="#181825", fg="#cdd6f4",
                                    font=("Consolas", 10), wrap="word",
                                    insertbackground="white")
    txt.pack(fill="both", expand=True, padx=10, pady=10)
    txt.insert("1.0", format_meta(meta))
    txt.config(state="disabled")

    # Buttons
    btn_frame = tk.Frame(root, bg="#1e1e2e")
    btn_frame.pack(fill="x", padx=10, pady=(0, 10))

    def save_txt():
        out = img_path.with_suffix(".meta.txt")
        out.write_text(format_meta(meta), encoding="utf-8")
        messagebox.showinfo("Guardado", f"Metadatos guardados en:\n{out}")

    tk.Button(btn_frame, text="Guardar como TXT", command=save_txt,
              bg="#313244", fg="#cdd6f4", font=("Segoe UI", 10),
              relief="flat", padx=12, pady=4).pack(side="left", padx=4)
    tk.Button(btn_frame, text="Cerrar", command=root.destroy,
              bg="#45475a", fg="#cdd6f4", font=("Segoe UI", 10),
              relief="flat", padx=12, pady=4).pack(side="left", padx=4)

    root.mainloop()


def process(path_str):
    p = Path(path_str)
    if p.is_dir():
        files = list(p.glob("*.png"))
        if not files:
            print("  No hay PNGs en la carpeta.")
            return
        p = files[0]
        print(f"  Mostrando primer PNG: {p.name}")

    if p.suffix.lower() != ".png":
        print(f"  Solo se soportan archivos PNG (ComfyUI).")
        return

    meta = extract_comfy_meta(p)
    show_gui(p, meta)


def main():
    if len(sys.argv) < 2:
        # Open file dialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(
            title="Selecciona un PNG de ComfyUI",
            filetypes=[("PNG files", "*.png")]
        )
        root.destroy()
        if path:
            process(path)
        return

    for arg in sys.argv[1:]:
        process(arg.strip('"'))


if __name__ == "__main__":
    main()
