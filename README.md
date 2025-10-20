# Python Screen Capture Automation  
[ì˙ñ{åÍî≈ÇÕÇ±ÇøÇÁ Å® README_JP.md](./README_JP.md)

## Overview
This project provides a simple Python-based automation tool to **capture sequential screen content** from any desktop application that supports page switching with keyboard keys (e.g., arrow keys).  
Captured images can then be **merged into PDFs**, either as one complete file or split into chapters.

The tool consists of two main scripts:
- **capture.py** ? Automates screen capture page by page.
- **merge.py** ? Crops and merges captured images into organized PDF files.

---

## Features
- Automatically captures screen content using configurable hotkeys.
- Adjustable delay and crop margins for reliable and precise captures.
- Merges output images into chapter-based or full-length PDFs.
- Optional progress bars for cropping, merging, and PDF generation.
- Managed via the **uv** Python environment tool.

---

## Setup

### 1. Install [uv](https://github.com/astral-sh/uv)
`uv` is used to manage Python environments and dependencies for this project.

```bash
pip install uv
```

### 2. Install Dependencies
From the project directory:
```bash
uv sync
```
This will create a virtual environment and install all required packages listed in `pyproject.toml`, including:
```
img2pdf, pillow, pyautogui, pygetwindow, pypdf, tqdm
```

---

## Usage

### 1. Capture Images
Edit the configuration in **capture.py** to match your target window title and settings.

Run:
```bash
uv run capture.py
```

This will:
- Focus the specified window (if possible),
- Capture each page (using the arrow or page-down key),
- Save screenshots sequentially into the `outputs/` directory.

You can interrupt the process safely at any time (Ctrl + C).

---

### 2. Merge into PDFs
After all pages are captured, configure `merge.py` to define page ranges and crop settings.

Run:
```bash
uv run merge.py
```

This will:
- Crop images (if enabled),
- Generate chapter-based PDFs (optional),
- Produce a final merged PDF in the `pdf_out/` directory.

---

## Directory Structure
```
python-ebook-capturer/
Ñ†
Ñ•ÑüÑü capture.py           # Capture screen automation
Ñ•ÑüÑü merge.py             # Merge and crop into PDFs
Ñ•ÑüÑü pyproject.toml       # Project and dependency definitions
Ñ•ÑüÑü outputs/             # Captured image files (auto-created)
Ñ§ÑüÑü pdf_out/             # Generated PDF files (auto-created)
```

---

## Notes
- Works with any desktop application that allows page switching via keyboard.
- Use `delay_after_flip` in `capture.py` to ensure screen content finishes loading before capture.
- Temporary cropped images are deleted automatically after merging to save disk space.
