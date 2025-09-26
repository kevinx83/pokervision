import React, { useState } from "react";

function App() {
  const [result, setResult] = useState<string>("");

  const callAPI = async () => {
    const response = await fetch("http://127.0.0.1:8000/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cards: [0, 12] }) // Ace♠, King♥
    });
    const data = await response.json();
    setResult(JSON.stringify(data));
  };

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h1>PokerVision Frontend</h1>
      <button onClick={callAPI}>Simulate Hand</button>
      <p>Result: {result}</p>
    </div>
  );
}

export default App;
