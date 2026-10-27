import { useEffect, useState } from "react";
import { api, ApiError } from "../api/apiClient";
import type {
  Partition,
  ReplayAdvanceResponse,
  ReplayResetResponse,
  ReplayStatus,
} from "../types/api";

const PARTITIONS: Partition[] = ["threshold", "validation", "attack"];

function formatError(e: unknown): string {
  if (e instanceof ApiError) return `${e.status}: ${e.detail}`;
  if (e instanceof Error) return e.message;
  return String(e);
}

export interface ReplayControlsProps {
  onStart?: (res: ReplayResetResponse) => void;
  onAdvance?: (res: ReplayAdvanceResponse) => void;
  onReset?: (res: ReplayResetResponse) => void;
  /** Called once on mount with the current backend status (or null if no active replay). */
  onInitialStatus?: (status: ReplayStatus | null) => void;
}

export function ReplayControls({
  onStart,
  onAdvance,
  onReset,
  onInitialStatus,
}: ReplayControlsProps = {}) {
  const [partition, setPartition] = useState<Partition>("threshold");
  const [status, setStatus] = useState<ReplayStatus | null>(null);
  const [last, setLast] = useState<ReplayAdvanceResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    let cancelled = false;
    api.replayStatus().then(
      (s) => {
        if (!cancelled) {
          setStatus(s);
          setActive(true);
          onInitialStatus?.(s);
        }
      },
      (e) => {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 404) {
          onInitialStatus?.(null);
          return;
        }
        setError(formatError(e));
        onInitialStatus?.(null);
      },
    );
    return () => {
      cancelled = true;
    };
  }, []);

  const withBusy = async (fn: () => Promise<void>) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
    } catch (e) {
      setError(formatError(e));
    } finally {
      setBusy(false);
    }
  };

  const handleStart = () =>
    withBusy(async () => {
      const res = await api.replayStart(partition);
      setStatus(res.status);
      setLast(null);
      setActive(true);
      onStart?.(res);
    });

  const handleAdvance = () =>
    withBusy(async () => {
      const res = await api.replayAdvance();
      setStatus(res.status);
      setLast(res);
      onAdvance?.(res);
    });

  const handleReset = () =>
    withBusy(async () => {
      const res = await api.replayReset();
      setStatus(res.status);
      setLast(null);
      onReset?.(res);
    });

  const finished = status?.finished ?? false;

  return (
    <section className="replay-controls" aria-label="Historical replay controls">
      <div className="controls">
        <label>
          Partition{" "}
          <select
            value={partition}
            onChange={(e) => setPartition(e.target.value as Partition)}
            disabled={busy}
          >
            {PARTITIONS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <button type="button" onClick={handleStart} disabled={busy}>
          Start
        </button>
        <button
          type="button"
          onClick={handleAdvance}
          disabled={busy || !active || finished}
        >
          Advance
        </button>
        <button type="button" onClick={handleReset} disabled={busy || !active}>
          Reset
        </button>
      </div>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {!active && !error && (
        <p className="hint">
          No active replay. Choose a partition and press Start.
        </p>
      )}

      {status && (
        <dl className="status">
          <dt>partition</dt>
          <dd>{status.partition ?? "—"}</dd>
          <dt>position</dt>
          <dd>
            {status.position} / {status.total_rows}
          </dd>
          <dt>window filled</dt>
          <dd>
            {status.window_filled
              ? "yes"
              : `no (${status.warmup_remaining} observations to go)`}
          </dd>
          <dt>last timestamp</dt>
          <dd>{status.last_timestamp ?? "—"}</dd>
          <dt>last score</dt>
          <dd>
            {status.last_score === null
              ? "— (warm-up)"
              : status.last_score.toExponential(4)}
          </dd>
          <dt>threshold</dt>
          <dd>{status.threshold.toExponential(4)}</dd>
          <dt>alerts emitted</dt>
          <dd>{status.alerts_emitted}</dd>
          <dt>finished</dt>
          <dd>{status.finished ? "yes" : "no"}</dd>
        </dl>
      )}

      {last && last.warmup_remaining > 0 && (
        <p className="warmup">
          Warm-up: {last.warmup_remaining} more observations until scoring
          begins.
        </p>
      )}

      {last?.alert === true && (
        <p className="alert-note" role="status">
          Score exceeded threshold at {last.timestamp}
        </p>
      )}
    </section>
  );
}