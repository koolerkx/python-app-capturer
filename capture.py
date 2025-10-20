import os
import time
import sys
from typing import Optional, Tuple

import pyautogui
from PIL import Image
try:
    import pygetwindow as gw
except ImportError:
    gw = None

# -----------------------------
# 基本設定（可改成讀 JSON 檔）
# -----------------------------
CONFIG = {
    "window_title": "Kindle",   # 以關鍵字尋找視窗標題（大小寫不敏感）
    "output_dir": "outputs",
    "start_index": 1,
    "pages": 479,                # ← 測試時先小數量；實際請由使用者提供
    "delay_after_flip": 0.5,    # 翻頁後冷卻（秒）
    "hotkey_next": "right",     # 可改 "pagedown"
    # 視窗內裁切邊距（像素）：從視窗邊界往內縮
    "crop_margins": {"left": 8, "top": 80, "right": 8, "bottom": 20},
    # 首頁是否先截圖（True：一開始先存 page_001，再開始翻頁）
    "capture_first_page": True
}

# -----------------------------
# 工具函式
# -----------------------------
def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def find_window_bbox(title_keyword: str) -> Optional[Tuple[int, int, int, int]]:
    """
    以關鍵字尋找第一個匹配的視窗，回傳 bbox: (left, top, width, height)
    """
    if gw is None:
        print("pygetwindow 未安裝，無法自動尋找視窗。", file=sys.stderr)
        return None

    candidates = [w for w in gw.getAllTitles() if title_keyword.lower() in w.lower() and w.strip()]
    if not candidates:
        return None

    # 取得第一個真實視窗對象
    for t in candidates:
        try:
            win = gw.getWindowsWithTitle(t)[0]
            if win.isMinimized:
                win.restore()
                time.sleep(0.2)
            win.activate()
            time.sleep(0.2)
            return (win.left, win.top, win.width, win.height)
        except Exception:
            continue
    return None

def focus_window(title_keyword: str) -> bool:
    if gw is None:
        return False
    try:
        windows = gw.getWindowsWithTitle(title_keyword)
        if not windows:
            return False
        win = windows[0]
        if win.isMinimized:
            win.restore()
            time.sleep(0.2)
        win.activate()
        time.sleep(0.2)
        return True
    except Exception:
        return False

def crop_bbox(bbox: Tuple[int, int, int, int], margins: dict) -> Tuple[int, int, int, int]:
    left, top, width, height = bbox
    l = left + int(margins.get("left", 0))
    t = top + int(margins.get("top", 0))
    r = left + width - int(margins.get("right", 0))
    b = top + height - int(margins.get("bottom", 0))
    # 轉為 (left, top, width, height) for pyautogui.screenshot
    return (l, t, max(0, r - l), max(0, b - t))

def capture_region(region: Tuple[int, int, int, int], save_path: str) -> None:
    img = pyautogui.screenshot(region=region)  # region=(left, top, width, height)
    img.save(save_path)

def page_filename(output_dir: str, index: int) -> str:
    return os.path.join(output_dir, f"page_{index:03d}.png")

def flip_next_page(key: str) -> None:
    pyautogui.press(key)

# -----------------------------
# 主流程
# -----------------------------
def run_capture(
    window_title: str,
    output_dir: str,
    pages: int,
    start_index: int = 1,
    delay_after_flip: float = 0.3,
    hotkey_next: str = "right",
    crop_margins: Optional[dict] = None,
    capture_first_page: bool = True
):
    assert pages > 0, "pages 必須 > 0"
    ensure_output_dir(output_dir)

    print(f"[INFO] 尋找視窗: '{window_title}' ...")
    bbox = find_window_bbox(window_title)
    if bbox is None:
        print("[WARN] 找不到視窗，將改用『螢幕前景整個範圍』截圖。")
        screen_w, screen_h = pyautogui.size()
        bbox = (0, 0, screen_w, screen_h)

    if not focus_window(window_title):
        print("[WARN] 無法主動聚焦視窗，請手動把目標視窗切到最前景。")
        time.sleep(1.0)

    # 計算實際截圖範圍
    region = bbox
    if crop_margins:
        region = crop_bbox(bbox, crop_margins)

    print(f"[INFO] 截圖區域: left={region[0]}, top={region[1]}, width={region[2]}, height={region[3]}")
    print("[INFO] 3 秒後開始，自行將滑鼠移開避免遮擋...")
    for s in [3, 2, 1]:
        print(f"  {s} ...")
        time.sleep(1.0)

    page_idx = start_index
    try:
        if capture_first_page:
            out = page_filename(output_dir, page_idx)
            capture_region(region, out)
            print(f"[SAVE] {out}")
            page_idx += 1

        # 循環翻頁 + 擷取
        while page_idx < start_index + pages:
            flip_next_page(hotkey_next)
            time.sleep(delay_after_flip)

            out = page_filename(output_dir, page_idx)
            capture_region(region, out)
            print(f"[SAVE] {out}")
            page_idx += 1

        print("[DONE] 影像擷取完成。")
    except KeyboardInterrupt:
        print("\n[ABORT] 使用者中斷。已保存至目前進度。")
    except Exception as e:
        print(f"[ERROR] {e}")
        print("[HINT] 嘗試增大 delay_after_flip、確認視窗未被遮擋、調整 crop_margins。")

if __name__ == "__main__":
    # 你也可以改成從 argparse / JSON 讀入
    run_capture(
        window_title=CONFIG["window_title"],
        output_dir=CONFIG["output_dir"],
        pages=CONFIG["pages"],
        start_index=CONFIG["start_index"],
        delay_after_flip=CONFIG["delay_after_flip"],
        hotkey_next=CONFIG["hotkey_next"],
        crop_margins=CONFIG["crop_margins"],
        capture_first_page=CONFIG["capture_first_page"]
    )
