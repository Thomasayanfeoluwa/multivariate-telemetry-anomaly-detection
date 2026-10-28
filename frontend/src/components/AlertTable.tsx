import type { ScorePoint } from "./ScoreChart";

export interface AlertTableProps {
  points: ScorePoint[];
  threshold: number;
  maxRows?: number;
}

export function AlertTable({
  points,
  threshold,
  maxRows = 5,
}: AlertTableProps) {
  const alerts = points
    .filter((p) => p.alert)
    .slice(-maxRows)
    .reverse();

  return (
    <section className="alert-table" aria-label="Anomaly alert history">
      <header className="alert-table-header">
        <h2>Anomaly alert history</h2>
        {alerts.length > 0 && (
          <span className="alert-table-count">
            Showing last {alerts.length} of {maxRows}
          </span>
        )}
      </header>

      {alerts.length === 0 ? (
        <p className="hint">No threshold crossings in this session yet.</p>
      ) : (
        <table>
          <caption className="sr-only">
            Most recent {alerts.length} threshold crossings, newest first.
          </caption>
          <thead>
            <tr>
              <th scope="col">Timestamp</th>
              <th scope="col">Score</th>
              <th scope="col">Threshold</th>
              <th scope="col">Excess</th>
            </tr>
          </thead>
          <tbody>
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
                  <td className="num muted">
                    {threshold.toExponential(4)}
                  </td>
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
          </tbody>
        </table>
      )}

      {alerts.length > 0 && (
        <p className="alert-table-footer">
          Live · newest alert at the top · updates as replay advances
        </p>
      )}
    </section>
  );
}