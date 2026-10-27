import { useEffect, useRef, useState } from "react";
import { api, ApiError } from "../api/apiClient";
import type {
  Partition,
  ReplayAdvanceResponse,
  ReplayResetResponse,
  ReplayStatus,
} from "../types/api";

const PARTITIONS: Partition[] = ["threshold", "validation", "attack"];

const SPEEDS = [
  { label: "1×", value: 1 },
  { label: "5×", value: 5 },
  { label: "20×", value: 20 },
  { label: "50×", value: 50 },
] as const;

function formatError(e: unknown): string {
  if (e instanceof ApiError) return `${e.status}: ${e.detail}`;
  if (e instanceof Error) return e.message;
  return String(e);
}

export interface ReplayControlsProps {
  onStart?: (res: ReplayResetResponse) => void;
  onAdvance?: (res: ReplayAdvanceResponse) => void;
  onReset?: (res: ReplayResetResponse) => void;
  onInitialStatus?: (status: ReplayStatus | null) => void;
  soundEnabled?: boolean;
  onToggleSound?: () => void;
}

export function ReplayControls({
  onStart,
  onAdvance,
  onReset,
  onInitialStatus,
  soundEnabled,
  onToggleSound,
}: ReplayControlsProps = {}) {
  const [partition, setPartition] = useState<Partition>("threshold");
  const [status, setStatus] = useState<ReplayStatus | null>(null);
  const [last, setLast] = useState<ReplayAdvanceResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [active, setActive] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState<number>(10);

  const playRef = useRef(false);
  const onAdvanceRef = useRef(onAdvance);

  useEffect(() => {
    playRef.current = playing;
  }, [playing]);

  useEffect(() => {
    onAdvanceRef.current = onAdvance;
  }, [onAdvance]);

  // Mount probe: resume from any existing backend replay.
  useEffect(() => {
    let cancelled = false;
    api.replayStatus().then(
      (s) => {
        if (!cancelled) {
          setStatus(s);
          setActive(true);
          // Sync dropdown to backend's actual partition so a page refresh
          // does not leave the select showing a stale value.
          if (s.partition) {
            setPartition(s.partition as Partition);
          }
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-play loop.
  useEffect(() => {
    if (!playing) return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const tick = async () => {
      if (cancelled || !playRef.current) return;
      try {
        const res = await api.replayAdvance();
        if (cancelled) return;
        setStatus(res.status);
        setLast(res);
        onAdvanceRef.current?.(res);
        if (res.finished) {
          setPlaying(false);
          return;
        }
      } catch (e) {
        setError(formatError(e));
        setPlaying(false);
        return;
      }
      if (!cancelled) {
        timer = setTimeout(tick, Math.max(1, 1000 / speed));
      }
    };

    tick();

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [playing, speed]);

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
      setPlaying(false);
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
      setPlaying(false);
      const res = await api.replayReset();
      setStatus(res.status);
      setLast(null);
      onReset?.(res);
    });

  const handlePlayToggle = () => setPlaying((p) => !p);

  const finished = status?.finished ?? false;
  const canPlay = active && !finished && !busy;

  return (
    <section className="replay-controls" aria-label="Historical replay controls">
      <div className="controls">
        <label>
          Partition{" "}
          <select
            value={partition}
            onChange={(e) => setPartition(e.target.value as Partition)}
            disabled={busy || playing}
          >
            {PARTITIONS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <button type="button" onClick={handleStart} disabled={busy || playing}>
          Start
        </button>
        <button
          type="button"
          onClick={handleAdvance}
          disabled={busy || !active || finished || playing}
        >
          Advance
        </button>
        <button
          type="button"
          onClick={handlePlayToggle}
          disabled={!canPlay}
          className={playing ? "playing" : undefined}
        >
          {playing ? "Pause" : "Play"}
        </button>
        <label>
          Speed{" "}
          <select
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            disabled={busy}
          >
            {SPEEDS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={handleReset}
          disabled={busy || !active}
        >
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
              : `no (${status.warmup_remaining} to go)`}
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