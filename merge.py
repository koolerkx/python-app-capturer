# merge.py  (or merge_to_pdf.py)
# Merge images into chapter PDFs and final PDFs, with optional global crop.
# INPUT images: CONFIG["image_dir"]
# OUTPUT PDFs:  CONFIG["pdf_output_dir"]
# Requires: pip install img2pdf pypdf pillow tqdm

import os
import re
import tempfile
import shutil
from typing import List, Tuple, Optional, Dict
import img2pdf
from pypdf import PdfWriter, PdfReader
from PIL import Image, ImageOps

# Optional progress bars
try:
    from tqdm import tqdm as _tqdm
    def tqdm(iterable, **kwargs):
        return _tqdm(iterable, **kwargs)
except Exception:
    # Fallback: no-op if tqdm is not available
    def tqdm(iterable, **kwargs):
        return iterable

IMAGE_EXTS = {".png", ".jpg", ".jpeg"}

CONFIG = {
    # ---- paths ----
    "image_dir": "outputs",        # where capture.py saved the page images
    "pdf_output_dir": "pdf_out",   # where to write all PDFs

    # ---- ranges & filenames ----
    # Inclusive ranges, 1-based after natural sort
    "chapter_ranges": [
        (9, 14), 
        (15, 56),
        (57, 82),
        (83, 102),
        (103, 130),
        (131, 146),
        (147, 170),
        (171, 192),
        (193, 212),
        (213, 232),
        (233, 260),
        (261, 292),
        (293, 310),
        (311, 330),
        (331, 360),
        (361, 390),
        (391, 415),
        (416, 423),
        (424, 430),
        (431, 436),
        (437, 444),
        (445, 446),
        (447, 454),
        (454, 463),
    ],
    "chapters_name": "chapter",
    "final_all": "book_all_images.pdf",
    "final_from_chapters": "book_from_chapters.pdf",

    # ---- global crop (applied to every image before PDF) ----
    # pixels from image top-left; w/h can be None (to right/bottom edge)
    "crop": {
        "enabled": True,
        "x": 495,
        "y": 311,
        "w": 1006,
        "h": 1421,
        "temp_format": "PNG",       # "PNG" (lossless) or "JPEG"
        "debug_preview_count": 0
    },

    # ---- progress toggles ----
    "progress": {
        "crop": True,          # progress bar over images during cropping
        "chapters": True,      # progress bar over chapter ranges
        "merge_chapters": True # progress bar over chapter PDFs during merge
    },

    # ---- safety/debug ----
    "dry_run": False,          # True = log only; no files written
}

# -----------------------------
# Helpers
# -----------------------------
def ensure_dir(path: str) -> None:
    if path:
        os.makedirs(path, exist_ok=True)

def natural_key(s: str):
    # "page_2.png" < "page_10.png"
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def list_images_sorted(image_dir: str) -> List[str]:
    if not os.path.isdir(image_dir):
        raise FileNotFoundError(f"Image dir not found: {image_dir}")
    files = []
    for name in os.listdir(image_dir):
        _, ext = os.path.splitext(name)
        if ext.lower() in IMAGE_EXTS:
            files.append(name)
    files.sort(key=natural_key)
    paths = [os.path.join(image_dir, f) for f in files]
    if not paths:
        raise FileNotFoundError(f"No images found in {image_dir} (accepted: {', '.join(IMAGE_EXTS)})")
    return paths

def select_pages(images: List[str], start: int, end: int) -> List[str]:
    if start <= 0 or end <= 0 or start > end:
        raise ValueError(f"Invalid range ({start}, {end}). Pages are 1-based and require start<=end.")
    if start > len(images):
        return []
    end = min(end, len(images))
    return images[start - 1:end]

def clamp(val: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, val))

def _to_int_or_none(v):
    if v is None:
        return None
    if isinstance(v, bool):
        raise ValueError("crop w/h cannot be boolean")
    return int(v)

def compute_crop_box(img_w: int, img_h: int, x: int, y: int,
                     w: Optional[int], h: Optional[int]) -> Optional[Tuple[int,int,int,int]]:
    left = clamp(int(x), 0, img_w)
    top  = clamp(int(y), 0, img_h)
    right = img_w if w is None else clamp(left + max(0, int(w)), 0, img_w)
    bottom = img_h if h is None else clamp(top + max(0, int(h)), 0, img_h)
    if right - left <= 0 or bottom - top <= 0:
        return None
    return (left, top, right, bottom)

def prepare_images_with_optional_crop(
    image_paths: List[str],
    crop_cfg: Dict,
    progress_cfg: Dict,
    dry_run: bool
) -> Tuple[List[str], Optional[str]]:
    """
    If cropping is enabled, create a temp dir with cropped images and return (paths, temp_dir).
    Else, return (original_paths, None).
    Caller is responsible for cleaning up temp_dir (if not None).
    """
    if not crop_cfg.get("enabled", False):
        return image_paths, None

    if dry_run:
        print("[CROP] (dry-run) Would crop all images with:", {
            "x": crop_cfg.get("x"), "y": crop_cfg.get("y"),
            "w": crop_cfg.get("w"), "h": crop_cfg.get("h"),
            "temp_format": crop_cfg.get("temp_format", "PNG")
        })
        return image_paths, None

    temp_dir = tempfile.mkdtemp(prefix="merge_crop_")
    prepared = []

    x = int(crop_cfg.get("x", 0))
    y = int(crop_cfg.get("y", 0))
    w = _to_int_or_none(crop_cfg.get("w", None))
    h = _to_int_or_none(crop_cfg.get("h", None))
    temp_format = str(crop_cfg.get("temp_format", "PNG")).upper()
    if temp_format not in ("PNG", "JPEG", "JPG"):
        temp_format = "PNG"
    debug_n = int(crop_cfg.get("debug_preview_count", 0))

    iterable = image_paths
    if progress_cfg.get("crop", True):
        iterable = tqdm(image_paths, desc="[CROP] cropping images", unit="img")

    for idx, src in enumerate(iterable, start=1):
        try:
            with Image.open(src) as im:
                # Fix orientation and normalize to RGB
                im = ImageOps.exif_transpose(im).convert("RGB")
                box = compute_crop_box(im.width, im.height, x, y, w, h)

                if idx <= debug_n:
                    print(f"[CROP][DBG] {os.path.basename(src)} "
                          f"img=({im.width}x{im.height}) cfg=(x={x},y={y},w={w},h={h}) "
                          f"-> box={box}")

                if box is None:
                    print(f"[CROP][WARN] Invalid crop for {os.path.basename(src)}; using full image.")
                    cropped = im
                else:
                    if box == (0, 0, im.width, im.height):
                        print(f"[CROP][WARN] Crop equals full image for {os.path.basename(src)} "
                              f"(box={box}). Adjust x/y/w/h if unintended.")
                    cropped = im.crop(box)

                if temp_format in ("JPEG", "JPG"):
                    out_name = f"crop_{idx:04d}.jpg"
                    out_path = os.path.join(temp_dir, out_name)
                    cropped.save(out_path, "JPEG", quality=95, optimize=True)
                else:
                    out_name = f"crop_{idx:04d}.png"
                    out_path = os.path.join(temp_dir, out_name)
                    cropped.save(out_path, "PNG", optimize=True)

                prepared.append(out_path)
        except Exception as e:
            print(f"[CROP][ERROR] {src}: {e} (using original)")
            prepared.append(src)

    return prepared, temp_dir

def cleanup_temp_dir(temp_dir: Optional[str]):
    if temp_dir and os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)

def save_images_to_pdf(images: List[str], pdf_path: str, dry_run: bool = False):
    if not images:
        raise ValueError("No images to write.")
    print(f"[WRITE] {pdf_path}  ({len(images)} images)")
    if dry_run:
        return
    ensure_dir(os.path.dirname(pdf_path) or ".")
    with open(pdf_path, "wb") as f:
        f.write(img2pdf.convert(images))

def merge_pdfs(pdf_paths: List[str], out_path: str, progress_cfg: Dict, dry_run: bool = False):
    writer = PdfWriter()
    total_pages = 0

    iterable = pdf_paths
    if progress_cfg.get("merge_chapters", True):
        iterable = tqdm(pdf_paths, desc="[MERGE] chapters", unit="pdf")

    for p in iterable:
        if not os.path.exists(p):
            print(f"[WARN] PDF not found, skip: {p}")
            continue
        reader = PdfReader(p)
        for page in reader.pages:
            writer.add_page(page)
            total_pages += 1

    if total_pages == 0:
        raise ValueError("No pages to write in merged PDF.")
    print(f"[MERGE] -> {out_path}  (chapters: {len(pdf_paths)}, pages: {total_pages})")
    if dry_run:
        return
    ensure_dir(os.path.dirname(out_path) or ".")
    with open(out_path, "wb") as f:
        writer.write(f)

def pretty_range_name(start: int, end: int) -> str:
    return f"p{start:03d}-p{end:03d}"

# -----------------------------
# Main
# -----------------------------
def run_merge(
    image_dir: str,
    pdf_output_dir: str,
    chapter_ranges: List[Tuple[int, int]],
    chapters_name: str,
    final_all_name: str,
    final_from_chapters_name: str,
    crop_cfg: Dict,
    progress_cfg: Dict,
    dry_run: bool = False
):
    images = list_images_sorted(image_dir)
    print(f"[INFO] Found {len(images)} image(s) in {image_dir}")
    ensure_dir(pdf_output_dir)

    prepared_all, temp_dir = prepare_images_with_optional_crop(images, crop_cfg, progress_cfg, dry_run=dry_run)

    try:
        # Chapters
        chapter_pdfs: List[str] = []
        ranges_iter = chapter_ranges
        if progress_cfg.get("chapters", True):
            ranges_iter = tqdm(chapter_ranges, desc="[PDF] chapters", unit="ch")

        for idx, rng in enumerate(ranges_iter, start=1):
            start_i, end_i = int(rng[0]), int(rng[1])
            selected = select_pages(prepared_all, start_i, end_i)
            if not selected:
                print(f"[WARN] Range {start_i}-{end_i} selects no images; skip.")
                continue
            chapter_pdf = os.path.join(
                pdf_output_dir,
                f"{chapters_name}_{idx:02d}_{pretty_range_name(start_i, end_i)}.pdf"
            )
            print(f"[CHAPTER] #{idx}: pages {start_i}-{end_i} -> {chapter_pdf} ({len(selected)} images)")
            save_images_to_pdf(selected, chapter_pdf, dry_run=dry_run)
            chapter_pdfs.append(chapter_pdf)

        if not chapter_pdfs:
            print("[WARN] No chapter PDFs created (ranges may have been empty/out of bounds).")

        # Final from ALL (cropped or not depending on config)
        final_all_path = os.path.join(pdf_output_dir, final_all_name)
        print(f"[FINAL] All images -> {final_all_path} ({len(prepared_all)} images)")
        save_images_to_pdf(prepared_all, final_all_path, dry_run=dry_run)

        # Final concatenated from chapters
        if chapter_pdfs:
            final_from_chapters_path = os.path.join(pdf_output_dir, final_from_chapters_name)
            print(f"[FINAL] Merge chapters (order same as ranges) -> {final_from_chapters_path}")
            merge_pdfs(chapter_pdfs, final_from_chapters_path, progress_cfg, dry_run=dry_run)

        print("[DONE] merge completed.")
    finally:
        if not dry_run:
            cleanup_temp_dir(temp_dir)

if __name__ == "__main__":
    run_merge(
        image_dir=CONFIG["image_dir"],
        pdf_output_dir=CONFIG["pdf_output_dir"],
        chapter_ranges=CONFIG["chapter_ranges"],
        chapters_name=CONFIG["chapters_name"],
        final_all_name=CONFIG["final_all"],
        final_from_chapters_name=CONFIG["final_from_chapters"],
        crop_cfg=CONFIG["crop"],
        progress_cfg=CONFIG["progress"],
        dry_run=CONFIG["dry_run"],
    )
