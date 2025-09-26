from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

class HandRequest(BaseModel):
    cards: list[int]

app = FastAPI()

# Allow React dev server to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "PokerVision API running"}

@app.post("/simulate")
def simulate_hand(req: HandRequest):
    win_rate = round(random.uniform(0, 1), 2)
    return {
        "hand": req.cards,
        "simulated_win_rate": win_rate
    }
