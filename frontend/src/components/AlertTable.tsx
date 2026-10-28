import type { ScorePoint } from "./ScoreChart";

export interface LiveState {
  timestamp: string | null;
  score: number | null;
  alert: boolean | null;
}

export interface AlertTableProps {
  points: ScorePoint[];
  threshold: number;
  liveState?: LiveState | null;
  maxRows?: number;
}

export function AlertTable({
  points,
  threshold,
  liveState = null,
  maxRows = 5,
}: AlertTableProps) {
  const liveTs = liveState?.timestamp ?? null;
  const totalAlerts = points.filter((p) => p.alert).length;
  // Exclude the current live timestamp from the alert history to avoid
  // showing the same observation twice (once as LIVE, once as history).
  const alerts = points
    .filter((p) => p.alert && p.timestamp !== liveTs)
    .slice(-maxRows)
    .reverse();

  const showLive = liveState !== null && liveState.timestamp !== null;
  const liveIsWarmup = showLive && liveState!.score === null;
  const liveIsAlert = showLive && liveState!.alert === true;

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
        {totalAlerts > 0 && (
          <span className="alert-table-count">
            {totalAlerts.toLocaleString()} total alert
            {totalAlerts === 1 ? "" : "s"}
          </span>
        )}
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
              <td className="num live-status">{liveStatusText}</td>
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

      {showLive && totalAlerts === 0 && (
        <p className="alert-table-footer">
          No threshold crossings yet in this session.
        </p>
      )}
    </section>
  );
}