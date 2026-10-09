"""Compare a built theme against a published theme repo checkout.

Text files must match byte for byte. PNGs only need identical pixels:
ImageMagick stamps creation times into each file, so bytes differ between
otherwise identical builds.
"""

import subprocess
from pathlib import Path


def files(root):
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts}


def same_pixels(a, b):
    out = subprocess.run(["magick", "compare", "-metric", "AE", str(a), str(b), "null:"], capture_output=True, text=True)
    # AE prints the count of differing pixels on stderr; exit status 1 only means "different".
    return out.returncode in (0, 1) and out.stderr.split()[0] == "0"


def compare(built, published):
    """Return (added, removed, changed) relative paths, sorted."""
    built, published = Path(built), Path(published)
    new, old = files(built), files(published)
    changed = []
    for rel in sorted(new & old):
        a, b = built / rel, published / rel
        if a.read_bytes() == b.read_bytes():
            continue
        if rel.endswith(".png") and same_pixels(a, b):
            continue
        changed.append(rel)
    return sorted(new - old), sorted(old - new), changed
