# PokerVision (Monorepo)

Packages:
- packages/card-recognition — Python OpenCV starter
- packages/server — Node/Express API (health endpoint)
- packages/shared — placeholder for future shared code

## Quick Start

### Card recognition (Python)
cd packages/card-recognition
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Put an image anywhere and pass its path:
python -m card_recognition.detect --image sample.jpg

### Server (Node)
cd packages/server
npm install
npm run dev
# Open http://localhost:3001/health
