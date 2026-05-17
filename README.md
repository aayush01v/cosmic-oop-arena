# Vector Photo Tracer

A small cross-platform Python toolkit for converting **vector-like raster images** such as posterized portraits, AI vector-style PNGs, flat illustrations, and logo-like images into editable **SVG** paths, with optional **PDF/EPS/PS** export.

It is designed for Linux and Windows.

## What this does

```text
PNG/JPG/WEBP -> smoothing -> color quantization -> mask per color -> contour tracing -> editable SVG paths -> optional PDF/EPS export
```

## Important limitation

This is an **auto-trace** tool. It creates real vector paths, but it will not be as clean as a manually drawn Illustrator file.

For portraits:
- Use the already vector-like/posterized image as input, not the raw photo.
- Use more colors, usually 60-110.
- Use higher `--min-area` to remove noisy fragments.
- Avoid adding seam strokes unless you see white gaps.

## Install

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Optional PDF/EPS export: install **Inkscape** and add it to PATH. Alternative:

```bash
pip install -r requirements-exports-optional.txt
```

## Basic usage

```bash
python vectorize.py input.png output.svg --preset portrait_clean
```

Create SVG + PDF + EPS:

```bash
python vectorize.py input.png output.svg --preset portrait_clean --formats svg pdf eps
```

For vector portraits, start with:

```bash
python vectorize.py portrait.png portrait_clean.svg --preset portrait_clean --colors 80 --max-size 3600 --epsilon 1.0 --min-area 45 --formats svg pdf eps
```

## Presets

- `portrait_clean` - best first try for vector-like portraits.
- `portrait_detailed` - more detail, larger SVG, better likeness, more tiny paths.
- `poster_flat` - fewer shapes, flatter graphic poster look.
- `logo_flat` - very simplified trace.
- `accurate` - less smoothing, more exact contours; useful for debugging but can look noisy.

## Recommended portrait commands

Clean but still detailed:

```bash
python vectorize.py portrait.png portrait.svg --preset portrait_clean --colors 76 --epsilon 1.1 --min-area 35
```

More Illustrator-like flat poster:

```bash
python vectorize.py portrait.png portrait.svg --preset poster_flat --colors 42 --epsilon 2.0 --min-area 90
```

More detailed face and eyes:

```bash
python vectorize.py portrait.png portrait.svg --preset portrait_detailed --colors 100 --epsilon 0.8 --min-area 18
```

If the result has too many ugly fragments, increase `--min-area`, increase smoothing, or use fewer colors:

```bash
python vectorize.py portrait.png portrait.svg --preset portrait_clean --min-area 80
python vectorize.py portrait.png portrait.svg --preset portrait_clean --smooth combo --sigma-color 70 --sigma-space 70
python vectorize.py portrait.png portrait.svg --preset portrait_clean --colors 55
```

If the face loses likeness, use more colors, lower simplification, or lower minimum area:

```bash
python vectorize.py portrait.png portrait.svg --preset portrait_clean --colors 100
python vectorize.py portrait.png portrait.svg --preset portrait_clean --epsilon 0.7
python vectorize.py portrait.png portrait.svg --preset portrait_clean --min-area 20
```

If tiny white gaps appear between shapes, try a very small seam stroke:

```bash
python vectorize.py portrait.png portrait.svg --preset portrait_clean --seam-stroke 0.2
```

Do not use large strokes. Large strokes can make the trace look dirty.

## Batch usage

```bash
python batch_vectorize.py ./input_images ./output_vectors --preset portrait_clean --formats svg pdf
```

Recursive:

```bash
python batch_vectorize.py ./input_images ./output_vectors --recursive --preset poster_flat
```

## How to open in Illustrator

1. Open the `.svg` or `.pdf` in Adobe Illustrator.
2. Ungroup if needed.
3. Save as `.ai`.

The SVG contains actual editable paths, not an embedded image.

## How to export PDF/EPS

PDF/EPS export needs either Inkscape or CairoSVG.

Recommended: install Inkscape, then make sure this works:

```bash
inkscape --version
```

Then run:

```bash
python vectorize.py input.png output.svg --formats svg pdf eps
```

If export fails, the SVG is still the main vector file. Open it in Illustrator/Inkscape and export PDF/EPS manually.

## Practical advice

For clean vector portraits, the best workflow is:

1. Start from a clean vector-like PNG.
2. Trace with `portrait_clean`.
3. Compare result.
4. If noisy: increase `--min-area`, reduce `--colors`, increase smoothing.
5. If too flat: increase `--colors`, lower `--epsilon`, lower `--min-area`.
6. Do final cleanup manually in Illustrator/Inkscape.
