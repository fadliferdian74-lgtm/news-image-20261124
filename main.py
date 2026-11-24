#!/usr/bin/env python3
"""Entry point for the news-image-20261124 competition entry.

The repository ships the finished front-page image as entry.png (drawn by
render.py from the story data in stories.py). This program copies that
image to the output path the grader expects, byte for byte, so both
grading runs produce exactly the same file.
"""

import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(source, os.path.join(out_dir, "entry.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
