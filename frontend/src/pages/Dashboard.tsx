import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "../api/apiClient";
import { useAlertSound } from "../hooks/useAlertSound";
import { ReplayControls } from "../components/ReplayControls";
import { ScoreChart, type ScorePoint } from "../components/ScoreChart";
import { AlertTable } from "../components/AlertTable";
import { SensorChart, type SensorObservation } from "../components/SensorChart";
import { EvaluationSummary } from "../components/EvaluationSummary";
import { SessionSummary } from "../components/SessionSummary";
import { ScoreDistribution } from "../components/ScoreDistribution";
import { FeatureAttribution } from "../components/FeatureAttribution";
import { AlertRateChart } from "../components/AlertRateChart";
import type {
  GroundTruthWindow,
  ModelInfoResponse,
  ReplayStatus,
} from "../types/api";

export interface DashboardProps {
  onExit?: () => void;
}

type BackendStatus = "checking" | "ok" | "unreachable" | "not_ready";

export function Dashboard({ onExit }: DashboardProps) {
  const [history, setHistory] = useState<ScorePoint[]>([]);
  const [sensorHistory, setSensorHistory] = useState<SensorObservation[]>([]);
  const [threshold, setThreshold] = useState<number | null>(null);
  const [featureNames, setFeatureNames] = useState<string[]>([]);
  const [priorBackendState, setPriorBackendState] =
    useState<ReplayStatus | null>(null);
  const [currentPartition, setCurrentPartition] = useState<string | null>(null);
  const [groundTruthWindows, setGroundTruthWindows] = useState<
    GroundTruthWindow[]
  >([]);
  const [lastAlertResiduals, setLastAlertResiduals] = useState<{
    residuals: Record<string, number>;
    score: number;
    timestamp: string;
  } | null>(null);

  const [backendStatus, setBackendStatus] =
    useState<BackendStatus>("checking");
  const [backendMessage, setBackendMessage] = useState<string>("");
  const [healthRetry, setHealthRetry] = useState(0);

  const { enabled: soundEnabled, toggle: toggleSound, play: playAlert } =
    useAlertSound();
  const lastAlertRef = useRef<boolean>(false);

  // Health check gate — decides whether the rest of the page can render.
  useEffect(() => {
    let cancelled = false;
    setBackendStatus("checking");
    api.health().then(
      (h) => {
        if (cancelled) return;
        if (h.model_ready) {
          setBackendStatus("ok");
          setBackendMessage("");
        } else {
          setBackendStatus("not_ready");
          setBackendMessage(h.message);
        }
      },
      (e) => {
        if (cancelled) return;
        setBackendStatus("unreachable");
        setBackendMessage(
          e instanceof ApiError ? e.detail : String(e),
        );
      },
    );
    return () => {
      cancelled = true;
    };
  }, [healthRetry]);

  // Fetch model info only when backend is confirmed OK.
  useEffect(() => {
    if (backendStatus !== "ok") return;
    api
      .modelInfo()
      .then((mi: ModelInfoResponse) => {
        setThreshold(mi.threshold);
        setFeatureNames(mi.feature_names);
      })
      .catch(() => {
        setThreshold(null);
        setFeatureNames([]);
      });
  }, [backendStatus]);

  useEffect(() => {
    if (backendStatus !== "ok") return;
    api
      .groundTruthWindows()
      .then((r) => setGroundTruthWindows(r.windows))
      .catch(() => setGroundTruthWindows([]));
  }, [backendStatus]);

  return (
    <main className="app">
      <header className="dashboard-header">
        {onExit && (
          <button
            type="button"
            className="back-home"
            onClick={onExit}
            aria-label="Back to home page"
          >
            ← Home
          </button>
        )}
        <h1>SWaT Process Anomaly Monitor</h1>
      </header>

      {backendStatus === "checking" && (
        <p className="hint">Connecting to the API…</p>
      )}

      {backendStatus === "unreachable" && (
        <div className="backend-banner backend-error" role="alert">
          <div className="backend-banner-text">
            <strong>Cannot reach the API.</strong>{" "}
            {backendMessage || "The backend is not responding."} Check that
            the FastAPI server is running, then retry.
          </div>
          <button
            type="button"
            onClick={() => setHealthRetry((n) => n + 1)}
          >
            Retry
          </button>
        </div>
      )}

      {backendStatus === "not_ready" && (
        <div className="backend-banner backend-error" role="alert">
          <div className="backend-banner-text">
            <strong>Model not ready.</strong>{" "}
            {backendMessage || "The model bundle failed to load on the backend."}
          </div>
          <button
            type="button"
            onClick={() => setHealthRetry((n) => n + 1)}
          >
            Retry
          </button>
        </div>
      )}

      {backendStatus === "ok" && (
        <>
          <ReplayControls
            soundEnabled={soundEnabled}
            onToggleSound={toggleSound}
            onInitialStatus={(s) => {
              setPriorBackendState(s);
              setCurrentPartition(s?.partition ?? null);
            }}
            onStart={(res) => {
              setHistory([]);
              setSensorHistory([]);
              setLastAlertResiduals(null);
              setPriorBackendState(null);
              setCurrentPartition(res.status.partition);
              lastAlertRef.current = false;
            }}
            onReset={(res) => {
              setHistory([]);
              setSensorHistory([]);
              setLastAlertResiduals(null);
              setPriorBackendState(null);
              setCurrentPartition(res.status.partition);
              lastAlertRef.current = false;
            }}
            onAdvance={(res) => {
              setPriorBackendState(null);
              setCurrentPartition(res.status.partition);
              const isAlert = res.alert === true;
              if (isAlert && !lastAlertRef.current) {
                playAlert();
              }
              lastAlertRef.current = isAlert;
              if (res.timestamp !== null && res.observation !== null) {
                setSensorHistory((s) => [
                  ...s,
                  {
                    timestamp: res.timestamp as string,
                    values: res.observation as Record<string, number>,
                  },
                ]);
              }
              if (
                res.score !== null &&
                res.timestamp !== null &&
                res.alert !== null
              ) {
                setHistory((h) => [
                  ...h,
                  {
                    timestamp: res.timestamp as string,
                    score: res.score as number,
                    alert: res.alert as boolean,
                  },
                ]);
              }
              if (
                res.alert === true &&
                res.feature_residuals !== null &&
                res.score !== null &&
                res.timestamp !== null
              ) {
                setLastAlertResiduals({
                  residuals: res.feature_residuals,
                  score: res.score,
                  timestamp: res.timestamp,
                });
              }
            }}
            onBatch={(batch) => {
              setPriorBackendState(null);
              if (batch.results.length > 0) {
                setCurrentPartition(
                  batch.results[batch.results.length - 1].status.partition,
                );
              }
              const newPoints: ScorePoint[] = [];
              const newSensors: SensorObservation[] = [];
              for (const r of batch.results) {
                const isAlert = r.alert === true;
                if (isAlert && !lastAlertRef.current) {
                  playAlert();
                }
                lastAlertRef.current = isAlert;
                if (r.timestamp !== null && r.observation !== null) {
                  newSensors.push({
                    timestamp: r.timestamp as string,
                    values: r.observation as Record<string, number>,
                  });
                }
                if (
                  r.score !== null &&
                  r.timestamp !== null &&
                  r.alert !== null
                ) {
                  newPoints.push({
                    timestamp: r.timestamp as string,
                    score: r.score as number,
                    alert: r.alert as boolean,
                  });
                }
              }
              if (newSensors.length > 0) {
                setSensorHistory((s) => [...s, ...newSensors]);
              }
              if (newPoints.length > 0) {
                setHistory((h) => [...h, ...newPoints]);
              }
              // Capture the residuals of the last alert in this batch (if any)
              for (const r of batch.results) {
                if (
                  r.alert === true &&
                  r.feature_residuals !== null &&
                  r.score !== null &&
                  r.timestamp !== null
                ) {
                  setLastAlertResiduals({
                    residuals: r.feature_residuals,
                    score: r.score,
                    timestamp: r.timestamp,
                  });
                }
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
                    {" "}with{" "}
                    <strong>{priorBackendState.alerts_emitted}</strong>{" "}
                    alert{priorBackendState.alerts_emitted === 1 ? "" : "s"}{" "}
                    emitted
                  </>
                )}
                . Click <strong>Reset</strong> to align with the backend
                count, or <strong>Advance</strong> to continue and accumulate
                fresh history.
              </p>
            )}

          {threshold !== null && (
            <>
              <div className="dashboard-charts">
                <ScoreChart
                  points={history}
                  threshold={threshold}
                  retrospectiveWindows={
                    currentPartition === "attack" ? groundTruthWindows : []
                  }
                />
                {featureNames.length > 0 && (
                  <SensorChart
                    observations={sensorHistory}
                    featureNames={featureNames}
                  />
                )}
              </div>
              <AlertTable points={history} threshold={threshold} />
              <div className="dashboard-analysis-grid">
                <FeatureAttribution
                  residuals={lastAlertResiduals?.residuals ?? null}
                  score={lastAlertResiduals?.score ?? null}
                  threshold={threshold}
                  timestamp={lastAlertResiduals?.timestamp ?? null}
                />
                <AlertRateChart points={history} />
              </div>
              <ScoreDistribution points={history} threshold={threshold} />
              <SessionSummary points={history} threshold={threshold} />
            </>
          )}

          <EvaluationSummary />
        </>
      )}
    </main>
  );
}