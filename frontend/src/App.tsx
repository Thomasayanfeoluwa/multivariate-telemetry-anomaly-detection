import { useEffect, useState } from "react";
import { api } from "./api/apiClient";
import { ReplayControls } from "./components/ReplayControls";
import { ScoreChart, type ScorePoint } from "./components/ScoreChart";
import "./App.css";

function App() {
  const [history, setHistory] = useState<ScorePoint[]>([]);
  const [threshold, setThreshold] = useState<number | null>(null);

  // Read the threshold from the frozen bundle via /model-info.
  // Never hardcode it — the backend is the source of truth.
  useEffect(() => {
    api
      .modelInfo()
      .then((mi) => setThreshold(mi.threshold))
      .catch(() => setThreshold(null));
  }, []);

  return (
    <main className="app">
      <header>
        <h1>SWaT Process Anomaly Monitoring Prototype</h1>
        <p className="subtitle">
          Historical replay of recorded SWaT measurements through the frozen
          TCN Autoencoder. Alerts indicate the model&apos;s anomaly score
          exceeded a frozen threshold; they are not confirmed attacks,
          equipment failures, or safety events. Human review is required.
        </p>
      </header>

      <ReplayControls
        onStart={() => setHistory([])}
        onReset={() => setHistory([])}
        onAdvance={(res) => {
          if (res.score !== null && res.timestamp !== null && res.alert !== null) {
            setHistory((h) => [
              ...h,
              {
                timestamp: res.timestamp as string,
                score: res.score as number,
                alert: res.alert as boolean,
              },
            ]);
          }
        }}
      />

      {threshold !== null && (
        <>
          <ScoreChart points={history} threshold={threshold} />
          <AlertTable points={history} threshold={threshold} />
        </>
      )}
    </main>
  );
}

export default App;