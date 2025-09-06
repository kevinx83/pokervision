"""
Minimal stub for card detection.

Usage:
  python -m card_recognition.detect --image path/to.jpg
"""

import argparse
import cv2
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, required=True, help="Path to an image file")
    args = parser.parse_args()

    img_path = Path(args.image)
    if not img_path.exists():
        print(f"[error] Image not found: {img_path}")
        return

    img = cv2.imread(str(img_path))
    if img is None:
        print(f"[error] Could not read image (unsupported format?): {img_path}")
        return

    h, w = img.shape[:2]
    print(f"[ok] Loaded image: {img_path.name} ({w}x{h})")

    # Dummy detection: draw a green rectangle in the center
    cx, cy = w // 2, h // 2
    box_w, box_h = w // 4, h // 4
    pt1 = (cx - box_w // 2, cy - box_h // 2)
    pt2 = (cx + box_w // 2, cy + box_h // 2)
    cv2.rectangle(img, pt1, pt2, (0, 255, 0), 2)

    # Save to outputs
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True, parents=True)
    out_path = out_dir / f"detected_{img_path.name}"
    cv2.imwrite(str(out_path), img)
    print(f"[ok] Dummy detection saved to: {out_path}")

if __name__ == "__main__":
    main()
