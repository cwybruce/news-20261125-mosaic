#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261125 (news-20261125-mosaic).

Copies the pre-rendered entry.png (produced by draw_mosaic.py) into
$MAKEFUN_OUTPUT_DIR/entry.png, byte-for-byte.
"""
import hashlib
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1 * 1024 * 1024  # competition cap: entry image at most 1 MiB


def main():
    if not os.path.isfile(SRC):
        print(f"ERROR: {SRC} missing - run draw_mosaic.py first",
              file=sys.stderr)
        sys.exit(1)
    src_size = os.path.getsize(SRC)
    if src_size > MAX_BYTES:
        print(f"ERROR: entry.png is {src_size} bytes, over the "
              f"{MAX_BYTES} byte cap", file=sys.stderr)
        sys.exit(1)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    dst_size = os.path.getsize(dst)
    if dst_size != src_size:
        print(f"ERROR: incomplete copy ({dst_size} of {src_size} bytes)",
              file=sys.stderr)
        sys.exit(1)
    with open(dst, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print(f"wrote {dst} ({dst_size} bytes, sha256 {digest})")


if __name__ == "__main__":
    main()
