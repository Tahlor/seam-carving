#!/usr/bin/env python
import shlex
import argparse
from pathlib import Path

import numpy as np
import imageio
from seam_carving import resize  # assumes your enhanced resize lives here

"""
https://github.com/jonbarron/hist_thresh/blob/master/interactive_viewer.ipynb

"""

def parser(arg_str=None):
    """Parse arguments for the eval example."""
    p = argparse.ArgumentParser(
        description="Take one image from ROOT, match its seg, use first 2 channels as energy, resize 95%"
    )
    p.add_argument(
        "--root",
        type=Path,
        required=True,
        help="directory of source images",
    )
    p.add_argument(
        "--seg_dir",
        type=Path,
        required=True,
        help="directory of segmentation outputs",
    )
    p.add_argument(
        "--output",
        type=Path,
        required=True,
        help="where to save the resized image",
    )
    if arg_str:
        return p.parse_args(shlex.split(arg_str))
    return p.parse_args()


def main(args):
    imgs = sorted(args.root.glob("*.png")) + sorted(args.root.glob("*.jpg"))
    if not imgs:
        raise FileNotFoundError(f"No .png/.jpg in {args.root}")
    img_path = imgs[0]
    img = imageio.imread(str(img_path))

    stem = img_path.stem
    seg_paths = list(args.seg_dir.glob(f"{stem}.*"))
    if not seg_paths:
        raise FileNotFoundError(f"No matching seg for {stem} in {args.seg_dir}")
    seg = imageio.imread(str(seg_paths[0]))

    energy_map = seg[..., :2].astype(np.float32).mean(axis=2)

    h, w = img.shape[:2]
    new_size = (round(w * 0.95), round(h * 0.95))

    out = resize(
        img,
        size=new_size,
        energy_mode="backward",
        recompute_energy=False,
        energy_map=energy_map,
    )

    imageio.imwrite(str(args.output), out)
    print(f"Saved resized image to {args.output}")


if __name__ == "__main__":
    default_args = (
        "--root F:/labelbox/PA/pa_death_ems/5164/622/ "
        "--seg_dir F:/semantic_segmentation/pa_death_output-resized/ "
        "--output resized.png"
    )
    args = parser(default_args)
    main(args)
