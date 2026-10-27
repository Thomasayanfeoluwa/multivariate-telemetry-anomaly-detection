import { useEffect, useState } from "react";
import { api } from "./api/apiClient";
import { ReplayControls } from "./components/ReplayControls";
import { ScoreChart, type ScorePoint } from "./components/ScoreChart";
import { AlertTable } from "./components/AlertTable";
import { EvaluationSummary } from "./components/EvaluationSummary";
import type { ReplayStatus } from "./types/api";
import "./App.css";

function App() {
  const [history, setHistory] = useState<ScorePoint[]>([]);
  const [threshold, setThreshold] = useState<number | null>(null);
  const [priorBackendState, setPriorBackendState] =
    useState<ReplayStatus | null>(null);

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
        onInitialStatus={setPriorBackendState}
        onStart={() => {
          setHistory([]);
          setPriorBackendState(null);
        }}
        onReset={() => {
          setHistory([]);
          setPriorBackendState(null);
        }}
        onAdvance={(res) => {
          setPriorBackendState(null);
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

      {priorBackendState !== null &&
        priorBackendState.position > 0 &&
        history.length === 0 && (
          <p className="resume-banner" role="status">
            Backend replay is already active at position{" "}
            <strong>{priorBackendState.position}</strong> /{" "}
            {priorBackendState.total_rows}
            {priorBackendState.alerts_emitted > 0 && (
              <>
                {" "}with <strong>{priorBackendState.alerts_emitted}</strong>{" "}
                alert{priorBackendState.alerts_emitted === 1 ? "" : "s"}{" "}
                emitted
              </>
            )}
            . The chart and alert table below accumulate history from the
            moment this page loaded. Click <strong>Reset</strong> below to
            align with the backend count, or click <strong>Advance</strong>{" "}
            to continue and accumulate fresh history from here.
          </p>
        )}

      {threshold !== null && (
        <>
          <ScoreChart points={history} threshold={threshold} />
          <AlertTable points={history} threshold={threshold} />
        </>
      )}

      <EvaluationSummary />
    </main>
  );
}

export default App;