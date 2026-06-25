# Marina Image Tools

11 herramientas de procesamiento de imagen y vídeo para escritorio Windows. Funcionan arrastrando archivos o carpetas sobre el icono de cada herramienta — sin configuración, sin interfaz extra.

**Licencia:** [CC BY-NC-SA 4.0](LICENSE) — uso libre, no comercial, derivadas con misma licencia.

---

## Herramientas incluidas

| # | Herramienta | Qué hace |
|---|---|---|
| — | **Split Poses** | Divide una imagen de poses múltiples en PNGs individuales |
| 1 | **Remove BG** | Elimina el fondo con IA local (sin API externa) |
| 2 | **LoRA Organizer** | Prepara datasets de imágenes para entrenar LoRAs |
| 3 | **Social Resize** | Exporta a los 6 formatos estándar de redes sociales |
| 4 | **Dup Finder** | Detecta y mueve imágenes duplicadas visualmente |
| 5 | **Folder Watcher** | Organiza archivos en subcarpetas por fecha |
| 6 | **Seq to MP4** | Convierte secuencias de imágenes a vídeo H.264 |
| 7 | **Meta Viewer** | Muestra metadatos de PNGs generados por ComfyUI |
| 8 | **Grid Maker** | Combina imágenes en una hoja de referencia |
| 9 | **Frame Extractor** | Extrae fotogramas de un vídeo |
| 10 | **EXR to PNG** | Convierte EXR 32-bit a PNG con tone mapping |
| 11 | **Video Social Resize** | Exporta vídeos a los 6 formatos de redes sociales |

Ver [TOOLS.md](TOOLS.md) para descripción detallada de cada una.

---

## Requisitos del sistema

| Requisito | Detalle |
|---|---|
| Windows | 10 / 11 |
| Python | 3.10 o superior — [descargar](https://www.python.org/downloads/) |
| ffmpeg | Solo para herramientas 6, 9 y 10 — [descargar](https://ffmpeg.org/download.html) |

> Al instalar Python, marca **"Add Python to PATH"**.
>
> Para ffmpeg, extrae en `C:\ffmpeg\` — las herramientas lo detectan automáticamente en `C:\ffmpeg\bin\ffmpeg.exe`.

---

## Instalación

```
1. Descarga o clona este repositorio
2. Ejecuta install.bat  (instala las dependencias Python)
3. Ejecuta create_shortcuts.ps1 en PowerShell  (crea los iconos en el escritorio)
```

Para el paso 3 desde PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File .\create_shortcuts.ps1
```

---

## Uso

Arrastra un archivo o carpeta sobre el icono del escritorio correspondiente.

El resultado se guarda siempre junto al archivo original (en la misma carpeta o en una subcarpeta al lado).

---

## Licencia

[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](LICENSE)

- Puedes usar y compartir libremente estas herramientas
- No puedes venderlas ni usarlas con fines comerciales
- Si las modificas o derivas, debes usar la misma licencia
