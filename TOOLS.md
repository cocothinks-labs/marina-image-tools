# Descripción de cada herramienta

---

## Remove BG — Eliminador de fondos IA

**Qué hace:** Elimina el fondo de imágenes automáticamente usando IA local (sin API externa). Genera PNGs con fondo transparente.

**Acepta:** JPG, PNG, WEBP, BMP (archivo individual o carpeta)

**Resultado:** Carpeta `sin_fondo/` creada junto al archivo original, con los PNGs `_nobg.png`.

**Dependencias:** `rembg`, `onnxruntime`, `Pillow` (la primera vez descarga el modelo ONNX ~100MB)

---

## LoRA Organizer — Preparador de datasets para LoRA

**Qué hace:** Prepara una carpeta de imágenes como dataset para entrenar un LoRA en ComfyUI. Detecta y descarta duplicados visualmente similares, recorta las imágenes a cuadrado, las redimensiona al tamaño elegido y genera un archivo `.txt` de caption por imagen.

**Acepta:** Carpeta con imágenes JPG/PNG/WEBP

**Resultado:** Subcarpeta `dataset_<trigger>/` dentro de la carpeta original con las imágenes procesadas y los `.txt` de captions.

**Dependencias:** `Pillow`, `imagehash`

---

## Social Resize — Exportar a redes sociales

**Qué hace:** Exporta una imagen a los 6 formatos estándar de redes sociales en una sola operación. Centra y recorta o rellena con blur según la orientación.

**Formatos exportados:**
| Formato | Resolución |
|---|---|
| Instagram Reels (9:16) | 1080×1920 |
| Instagram Feed (4:5) | 1080×1350 |
| Square (1:1) | 1080×1080 |
| YouTube (16:9) | 1920×1080 |
| Twitter (16:9) | 1200×675 |
| LinkedIn (1:1) | 1200×1200 |

**Acepta:** JPG, PNG, WEBP, BMP (archivo individual o carpeta)

**Resultado:** Carpeta `social/<nombre_imagen>/` junto al original, con los 6 JPGs.

**Dependencias:** `Pillow`

---

## Dup Finder — Detector de duplicados

**Qué hace:** Analiza una carpeta en busca de imágenes visualmente similares o idénticas (aunque tengan diferente nombre o formato). Usa hash perceptual para detectar duplicados. Mantiene el archivo de mayor tamaño/calidad y mueve los demás a una carpeta de revisión.

**Acepta:** Carpeta con imágenes

**Resultado:** Carpeta `duplicados/` dentro de la carpeta analizada con los duplicados movidos (no borrados, para revisión manual).

**Dependencias:** `Pillow`, `imagehash`

---

## Folder Watcher — Organizador automático por fecha

**Qué hace:** Organiza los archivos de una carpeta en subcarpetas por fecha de creación (`YYYY-MM-DD/`). Se puede usar en modo one-shot (una pasada) o en modo watcher continuo que organiza archivos nuevos cada 30 segundos.

**Acepta:** Carpeta

**Resultado:** Subcarpetas de fecha (`2025-06-01/`, etc.) dentro de la misma carpeta.

**Dependencias:** Solo stdlib Python

---

## Seq to MP4 — Secuencia de imágenes a vídeo

**Qué hace:** Convierte una carpeta de frames (PNG, JPG, etc.) en un archivo MP4 con codec H.264. Pregunta el FPS antes de procesar.

**Acepta:** Carpeta con secuencia de imágenes (o un archivo dentro de ella)

**Resultado:** Archivo `<nombre_carpeta>.mp4` en la carpeta padre.

**Dependencias:** `ffmpeg` binario en `C:\ffmpeg\bin\`

---

## Meta Viewer — Visor de metadatos ComfyUI

**Qué hace:** Abre una ventana con los metadatos embebidos en PNGs generados por ComfyUI: modelo, LoRAs, sampler, seed, prompts. Permite guardar los metadatos como archivo `.txt`.

**Acepta:** PNG generado por ComfyUI (o carpeta, muestra el primero)

**Resultado:** Ventana gráfica con la información. Opción de guardar `<nombre>.meta.txt` junto al PNG.

**Dependencias:** `Pillow`, `tkinter` (stdlib)

---

## Grid Maker — Hoja de referencia de imágenes

**Qué hace:** Combina todas las imágenes de una carpeta en una sola imagen grid (hoja de referencia). Pregunta número de columnas, tamaño de celda y separación.

**Acepta:** Carpeta con imágenes

**Resultado:** Archivo `<nombre_carpeta>_grid.png` en la carpeta padre.

**Dependencias:** `Pillow`

---

## Frame Extractor — Extraer frames de vídeo

**Qué hace:** Extrae fotogramas de un vídeo. Tres modos: cada N segundos, N frames distribuidos uniformemente, o los 5 puntos clave (0%, 25%, 50%, 75%, 100%).

**Acepta:** MP4, MOV, AVI, MKV, WEBM, MXF (archivo o carpeta)

**Resultado:** Carpeta `<nombre_video>_frames/` junto al vídeo con los PNGs extraídos.

**Dependencias:** `ffmpeg` binario en `C:\ffmpeg\bin\`

---

## EXR to PNG — Conversor EXR 32-bit

**Qué hace:** Convierte archivos EXR de 32 bits a PNG de 8 bits con tone mapping configurable (linear, Reinhard, Filmic, clip). Procesado por lotes.

**Acepta:** Archivos `.exr` o carpeta con EXRs

**Resultado:** PNGs con el mismo nombre y ruta que los EXR originales.

**Dependencias:** `ffmpeg` binario en `C:\ffmpeg\bin\`

---

## Split Poses — Separador de poses de personaje

**Qué hace:** Detecta la cuadrícula de separación en una imagen de poses múltiples (hoja de referencia de personaje) y extrae cada pose como un PNG individual.

**Acepta:** PNG o JPG con múltiples poses en grid

**Resultado:** Carpeta `<nombre_imagen>/` junto al original con los PNGs `pose_01.png`, `pose_02.png`, etc.

**Dependencias:** `Pillow`, `numpy` (opcional, más rápido con él)

---

## Video Social Resize — Exportar vídeos a redes sociales

**Qué hace:** Exporta un vídeo a los 6 formatos estándar de redes sociales en una sola operación. Aplica la misma lógica que Social Resize para imágenes: recorte centrado si el vídeo es más ancho que el formato destino, o fondo desenfocado si es más alto. El audio se conserva en todos los formatos.

**Formatos exportados:**
| Formato | Resolución |
|---|---|
| Instagram Reels (9:16) | 1080×1920 |
| Instagram Feed (4:5) | 1080×1350 |
| Square (1:1) | 1080×1080 |
| YouTube (16:9) | 1920×1080 |
| Twitter (16:9) | 1200×675 |
| LinkedIn (1:1) | 1200×1200 |

**Acepta:** MP4, MOV, AVI, MKV, WEBM, M4V, MXF (archivo individual o carpeta)

**Resultado:** Carpeta `social/<nombre_video>/` junto al original con los 6 MP4.

**Dependencias:** `ffmpeg` binario en `C:\ffmpeg\bin\`
