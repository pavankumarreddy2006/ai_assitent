# data/media_data.py
import os

# ---------- Folder paths (relative to project root) ----------
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_IMAGES_FOLDER = os.path.join(_BASE_DIR, "static", "media", "images")
_VIDEOS_FOLDER = os.path.join(_BASE_DIR, "static", "media", "videos")

# Allowed image extensions (case-insensitive)
_IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp")


def _natural_key(name: str):
    """
    Sort filenames naturally so 2.png comes before 10.png
    (instead of alphabetic 1, 10, 11, 2, 3, ...).
    """
    import re
    parts = re.split(r"(\d+)", name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def _scan_images():
    """Scan /static/media/images and return all valid image URL paths."""
    paths = []
    if os.path.isdir(_IMAGES_FOLDER):
        try:
            files = [
                f for f in os.listdir(_IMAGES_FOLDER)
                if f.lower().endswith(_IMAGE_EXTS)
                and not f.startswith(".")
                and os.path.isfile(os.path.join(_IMAGES_FOLDER, f))
                and f.lower() != "logo.png"   # skip the college logo
            ]
            files.sort(key=_natural_key)
            paths = [f"/static/media/images/{f}" for f in files]
        except Exception:
            paths = []

    # Fallback if folder missing or empty
    if not paths:
        paths = [
            "/static/media/images/1.png",
            "/static/media/images/2.png",
            "/static/media/images/3.png",
        ]
    return paths


def _pick_video():
    """Pick the first video file in /static/media/videos."""
    if os.path.isdir(_VIDEOS_FOLDER):
        try:
            for f in sorted(os.listdir(_VIDEOS_FOLDER), key=_natural_key):
                if f.lower().endswith((".mp4", ".webm", ".mov")):
                    return f"/static/media/videos/{f}"
        except Exception:
            pass
    return "/static/media/videos/college.mp4"


# ---------- Exposed constants (same names — backward compatible) ----------
IMAGE_PATHS = _scan_images()
VIDEO_PATH  = _pick_video()