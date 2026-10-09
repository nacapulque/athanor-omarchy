from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ATHANOR = ROOT / "vendor/athanor"
PLATES_DIR = ATHANOR / "src/athanor/plates"
ASSETS = ROOT / "assets"
# Omarchy's own art, recolored per theme: the Plymouth unlock wordmark and the logo wallpaper.
OMARCHY_UNLOCK = ASSETS / "omarchy/unlock.png"
OMARCHY_WALLPAPER = ASSETS / "omarchy/omarchy-wallpaper.png"
