from pathlib import Path
import glob
import cv2 as cv
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FRAMES_DIR = ROOT / "data" / "frames"
CARDS_DIR = ROOT / "data" / "cards"
CARDS_DIR.mkdir(parents=True, exist_ok=True)

OUT_W, OUT_H = 200, 300
CANNY_LOW, CANNY_HIGH = 50, 200  # Increased for better edge detection
DILATE_ITERS = 2
MIN_AREA_FRAC = 0.0005  # Reduced from 0.002 - was too restrictive
APPROX_EPS_FRAC = 0.015
ASPECT_MIN, ASPECT_MAX = 0.55, 0.85  # Slightly wider range for different angles

def order_quad(pts):
    pts = np.array(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).reshape(-1)
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]
    return np.array([tl, tr, br, bl], dtype=np.float32)

def find_quads(image, debug=False):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5,5), 0)
    edges = cv.Canny(blur, CANNY_LOW, CANNY_HIGH)
    edges = cv.dilate(edges, np.ones((3,3), np.uint8), iterations=DILATE_ITERS)
    
    if debug:
        # Save intermediate processing steps
        cv.imwrite(str(CARDS_DIR / "debug_gray.jpg"), gray)
        cv.imwrite(str(CARDS_DIR / "debug_blur.jpg"), blur)
        cv.imwrite(str(CARDS_DIR / "debug_edges.jpg"), edges)
        print(f"[debug] Saved intermediate processing images to {CARDS_DIR}")
    
    cnts, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    h, w = gray.shape[:2]
    area_img = w * h
    min_area = MIN_AREA_FRAC * area_img
    
    if debug:
        print(f"[debug] Image dimensions: {w}x{h}, total area: {area_img}")
        print(f"[debug] Minimum contour area: {min_area:.0f}")
        print(f"[debug] Found {len(cnts)} total contours")
        print(f"[debug] Detection parameters:")
        print(f"  - Canny: {CANNY_LOW}-{CANNY_HIGH}")
        print(f"  - Min area fraction: {MIN_AREA_FRAC}")
        print(f"  - Aspect ratio range: {ASPECT_MIN}-{ASPECT_MAX}")
    
    quads = []
    filtered_stats = {"too_small": 0, "not_4_sided": 0, "not_convex": 0, "bad_aspect": 0}
    
    for i, c in enumerate(cnts):
        area = cv.contourArea(c)
        if area < min_area:
            filtered_stats["too_small"] += 1
            continue
            
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, APPROX_EPS_FRAC * peri, True)
        
        if len(approx) != 4:
            filtered_stats["not_4_sided"] += 1
            continue
            
        if not cv.isContourConvex(approx):
            filtered_stats["not_convex"] += 1
            continue
            
        rect = cv.minAreaRect(approx)
        (rw, rh) = rect[1]
        if rw == 0 or rh == 0:
            filtered_stats["bad_aspect"] += 1
            continue
            
        r = min(rw, rh) / max(rw, rh)
        if not (ASPECT_MIN <= r <= ASPECT_MAX):
            filtered_stats["bad_aspect"] += 1
            if debug and len(quads) < 5:  # Only show first few for readability
                print(f"[debug] Contour {i}: aspect ratio {r:.3f} outside range [{ASPECT_MIN}, {ASPECT_MAX}], area={area:.0f}")
            continue
            
        quads.append(approx.reshape(4, 2))
        if debug:
            print(f"[debug] Contour {i}: ACCEPTED - area={area:.0f}, aspect={r:.3f}")
    
    if debug:
        print(f"[debug] Filtering results: {filtered_stats}")
        
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
        print(f"[i] Processing {Path(f).name}...")
        quads = find_quads(img, debug=True)  # Enable debug for first analysis
        print(f"[i] Found {len(quads)} cards")
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
