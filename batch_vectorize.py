#!/usr/bin/env python3
"""
Batch vectorize all images in a folder.

Example:
    python batch_vectorize.py ./input_images ./vector_output --preset portrait_clean --formats svg pdf
"""
from __future__ import annotations

import argparse
from pathlib import Path

from vector_photo_tracer.cli import run_vectorize_from_args, build_parser


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch vectorize a folder of images.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--preset", default="portrait_clean")
    parser.add_argument("--formats", nargs="+", default=["svg"], choices=["svg", "pdf", "eps", "ps"])
    parser.add_argument("--colors", type=int, default=None)
    parser.add_argument("--max-size", type=int, default=None)
    parser.add_argument("--epsilon", type=float, default=None)
    parser.add_argument("--min-area", type=float, default=None)
    parser.add_argument("--background", default=None, choices=["auto", "none", "keep"])
    parser.add_argument("--seam-stroke", type=float, default=None)

    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    paths = args.input_dir.rglob("*") if args.recursive else args.input_dir.glob("*")
    images = [p for p in paths if p.suffix.lower() in IMAGE_EXTS]

    if not images:
        raise SystemExit(f"No images found in: {args.input_dir}")

    vector_parser = build_parser()

    for image_path in images:
        out_svg = args.output_dir / f"{image_path.stem}.svg"
        cli_parts = [
            str(image_path),
            str(out_svg),
            "--preset", args.preset,
            "--formats", *args.formats,
        ]
        if args.colors is not None:
            cli_parts += ["--colors", str(args.colors)]
        if args.max_size is not None:
            cli_parts += ["--max-size", str(args.max_size)]
        if args.epsilon is not None:
            cli_parts += ["--epsilon", str(args.epsilon)]
        if args.min_area is not None:
            cli_parts += ["--min-area", str(args.min_area)]
        if args.background is not None:
            cli_parts += ["--background", args.background]
        if args.seam_stroke is not None:
            cli_parts += ["--seam-stroke", str(args.seam_stroke)]

        print(f"\n==> Vectorizing {image_path.name}")
        vector_args = vector_parser.parse_args(cli_parts)
        run_vectorize_from_args(vector_args)


if __name__ == "__main__":
    main()
