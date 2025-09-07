from pathlib import Path
import glob
import cv2 as cv
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FRAMES_DIR = ROOT / "data" / "frames"
CARDS_DIR = ROOT / "data" / "cards"
CARDS_DIR.mkdir(parents=True, exist_ok=True)

OUT_W, OUT_H = 200, 300
CANNY_LOW, CANNY_HIGH = 30, 120
DILATE_ITERS = 2
MIN_AREA_FRAC = 0.002
APPROX_EPS_FRAC = 0.015
ASPECT_MIN, ASPECT_MAX = 0.60, 0.80

def order_quad(pts):
    pts = np.array(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).reshape(-1)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]
    return np.array([tl, tr, br, bl], dtype=np.float32)

def find_quads(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5,5), 0)
    edges = cv.Canny(blur, CANNY_LOW, CANNY_HIGH)
    edges = cv.dilate(edges, np.ones((3,3), np.uint8), iterations=DILATE_ITERS)
    cnts, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    h, w = gray.shape[:2]
    area_img = w * h
    quads = []
    for c in cnts:
        area = cv.contourArea(c)
        if area < MIN_AREA_FRAC * area_img:
            continue
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, APPROX_EPS_FRAC * peri, True)
        if len(approx) == 4 and cv.isContourConvex(approx):
            rect = cv.minAreaRect(approx)
            (rw, rh) = rect[1]
            if rw == 0 or rh == 0:
                continue
            r = min(rw, rh) / max(rw, rh)
            if not (ASPECT_MIN <= r <= ASPECT_MAX):
                continue
            quads.append(approx.reshape(4, 2))
    return quads

def warp_card(image, quad):
    src = order_quad(quad)
    dst = np.array([[0,0],[OUT_W-1,0],[OUT_W-1,OUT_H-1],[0,OUT_H-1]], dtype=np.float32)
    M = cv.getPerspectiveTransform(src, dst)
    return cv.warpPerspective(image, M, (OUT_W, OUT_H))

def main():
    files = sorted(glob.glob(str(FRAMES_DIR / "*.jpg")))
    if not files:
        print("[!] no frames in", FRAMES_DIR)
        return
    total = 0
    for f in files:
        img = cv.imread(f)
        if img is None:
            continue
        quads = find_quads(img)
        print(f"{Path(f).name}: {len(quads)} found")
        overlay = img.copy()
        for i, q in enumerate(quads):
            card = warp_card(img, q)
            out = CARDS_DIR / f"card_{Path(f).stem}_{i}.jpg"
            cv.imwrite(str(out), card)
            cv.polylines(overlay, [q.reshape(-1,1,2)], True, (0,255,0), 2)
        dbg = CARDS_DIR / f"debug_{Path(f).stem}.jpg"
        cv.imwrite(str(dbg), overlay)
        total += len(quads)
    print(f"saved {total} cards")

if __name__ == "__main__":
    main()
