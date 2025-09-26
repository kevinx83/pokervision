import cv2 as cv
import time
from pathlib import Path

FRAMES_DIR = Path(__file__).resolve().parents[1] / "data" / "frames"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

def main():
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open camera.")

    print("[i] Press 's' to save a frame, 'q' to quit.")
    while True:
        ok, frame = cap.read()
        if not ok:
            print("[!] Failed to read frame")
            break

        cv.putText(frame, "s: save  |  q: quit", (12, 28),
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv.imshow("camera", frame)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('s'):
            ts = int(time.time() * 1000)
            out = FRAMES_DIR / f"frame_{ts}.jpg"
            cv.imwrite(str(out), frame)
            print(f"[+] saved {out}")

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()