import { useEffect, useState } from "react";
import { api } from "../api/apiClient";
import { ReplayControls } from "../components/ReplayControls";
import { ScoreChart, type ScorePoint } from "../components/ScoreChart";
import { AlertTable } from "../components/AlertTable";
import { ScoreDistribution } from "../components/ScoreDistribution";
import { SensorChart, type SensorObservation } from "../components/SensorChart";
import { EvaluationSummary } from "../components/EvaluationSummary";
import { SessionSummary } from "../components/SessionSummary";
import type {
  GroundTruthWindow,
  ModelInfoResponse,
  ReplayStatus,
} from "../types/api";

export interface DashboardProps {
  onExit?: () => void;
}

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

  useEffect(() => {
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
  }, []);

  useEffect(() => {
    api
      .groundTruthWindows()
      .then((r) => setGroundTruthWindows(r.windows))
      .catch(() => setGroundTruthWindows([]));
  }, []);

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

      <ReplayControls
        onInitialStatus={(s) => {
          setPriorBackendState(s);
          setCurrentPartition(s?.partition ?? null);
        }}
        onStart={(res) => {
          setHistory([]);
          setSensorHistory([]);
          setPriorBackendState(null);
          setCurrentPartition(res.status.partition);
        }}
        onReset={(res) => {
          setHistory([]);
          setSensorHistory([]);
          setPriorBackendState(null);
          setCurrentPartition(res.status.partition);
        }}
        onAdvance={(res) => {
          setPriorBackendState(null);
          setCurrentPartition(res.status.partition);
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
            . Click <strong>Reset</strong> to align with the backend count, or{" "}
            <strong>Advance</strong> to continue and accumulate fresh history.
          </p>
        )}

      {threshold !== null && (
        <>
          <ScoreChart
            points={history}
            threshold={threshold}
            retrospectiveWindows={
              currentPartition === "attack" ? groundTruthWindows : []
            }
          />
          <AlertTable points={history} threshold={threshold} />
          {featureNames.length > 0 && (
            <SensorChart
              observations={sensorHistory}
              featureNames={featureNames}
            />
          )}
        </>
      )}

      <EvaluationSummary />
    </main>
  );
}