import type { ScorePoint } from "./ScoreChart";

export interface LiveState {
  timestamp: string | null;
  score: number | null;
  alert: boolean | null;
  alertStartTime?: string | null;
}

export interface AlertTableProps {
  points: ScorePoint[];
  threshold: number;
  liveState?: LiveState | null;
  backendAlerts?: number; // NEW: To show the total processed by the backend
  maxRows?: number;
}

function formatDuration(startTs?: string | null, endTs?: string | null) {
  if (!startTs || !endTs) return "";
  const start = new Date(startTs.replace(" ", "T")).getTime();
  const end = new Date(endTs.replace(" ", "T")).getTime();
  const sec = Math.floor((end - start) / 1000);
  if (sec < 60) return `${sec}s`;
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}m ${s}s`;
}

export function AlertTable({
  points,
  threshold,
  liveState = null,
  backendAlerts = 0,
  maxRows = 5,
}: AlertTableProps) {
  const liveTs = liveState?.timestamp ?? null;
  const totalSessionAlerts = points.filter((p) => p.alert).length;
  
  // Exclude the current live timestamp from the alert history to avoid
  // showing the same observation twice (once as LIVE, once as history).
  const alerts = points
    .filter((p) => p.alert && p.timestamp !== liveTs)
    .slice(-maxRows)
    .reverse();

  const showLive = liveState !== null && liveState.timestamp !== null;
  const liveIsWarmup = showLive && liveState!.score === null;
  const liveIsAlert = showLive && liveState!.alert === true;
  
  const liveDuration = liveIsAlert 
    ? formatDuration(liveState!.alertStartTime, liveState!.timestamp)
    : null;

  const liveRowClass = liveIsWarmup
    ? "alert-live-row alert-live-warmup"
    : liveIsAlert
      ? "alert-live-row alert-live-alert"
      : "alert-live-row alert-live-normal";

  const liveStatusText = !showLive
    ? ""
    : liveIsWarmup
      ? "warming up"
      : liveIsAlert
        ? `+${(((liveState!.score! - threshold) / threshold) * 100).toFixed(0)}% above`
        : "below threshold";

  return (
    <section className="alert-table" aria-label="Anomaly alert history">
      <header className="alert-table-header">
        <h2>Anomaly alert history</h2>
        <div className="alert-table-counts">
          <span className="alert-table-count" title="Alerts visible in this browser session">
            Session: {totalSessionAlerts.toLocaleString()}
          </span>
          {backendAlerts > totalSessionAlerts && (
            <span className="alert-table-count" title="Total alerts processed by the backend since Start">
              Backend total: {backendAlerts.toLocaleString()}
            </span>
          )}
        </div>
      </header>

      <table>
        <caption className="sr-only">
          Current state above; most recent threshold crossings below, newest
          first.
        </caption>
        <thead>
          <tr>
            <th scope="col">Timestamp</th>
            <th scope="col">Score</th>
            <th scope="col">Threshold</th>
            <th scope="col">Detail</th>
          </tr>
        </thead>
        <tbody>
          {showLive && (
            <tr className={liveRowClass}>
              <td>
                <span className="alert-live-badge">
                  <span className="alert-live-dot" aria-hidden="true" />
                  LIVE
                </span>
                <time dateTime={liveState!.timestamp!}>
                  {liveState!.timestamp}
                </time>
              </td>
              <td className="num">
                {liveIsWarmup
                  ? "— (warm-up)"
                  : liveState!.score!.toExponential(4)}
              </td>
              <td className="num muted">{threshold.toExponential(4)}</td>
              <td className="num live-status">
                {liveStatusText}
                {liveDuration && <span className="live-duration"> ({liveDuration})</span>}
              </td>
            </tr>
          )}

          {alerts.map((p, i) => {
            const freshness =
              i === 0 ? "newest" : i === 1 ? "recent" : "older";
            const excessPct = ((p.score - threshold) / threshold) * 100;
            return (
              <tr
                key={`${p.timestamp}-${i}`}
                className={`alert-row alert-row-${freshness}`}
              >
                <td>
                  <span
                    className={`alert-dot alert-dot-${freshness}`}
                    aria-hidden="true"
                  />
                  <time dateTime={p.timestamp}>{p.timestamp}</time>
                </td>
                <td className="num">{p.score.toExponential(4)}</td>
                <td className="num muted">{threshold.toExponential(4)}</td>
                <td className="num excess">
                  <span className="excess-value">
                    +{(p.score - threshold).toExponential(2)}
                  </span>
                  <span className="excess-pct">
                    +{excessPct.toFixed(0)}%
                  </span>
                </td>
              </tr>
            );
          })}

          {!showLive && (
            <tr>
              <td colSpan={4} className="hint-cell">
                No observations yet. Start a replay and advance to see the
                current state here.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {showLive && totalSessionAlerts === 0 && (
        <p className="alert-table-footer">
          No threshold crossings yet in this session.
        </p>
      )}
    </section>
  );
}