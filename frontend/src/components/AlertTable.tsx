import type { ScorePoint } from "./ScoreChart";

export interface AlertTableProps {
  points: ScorePoint[];
  threshold: number;
  maxRows?: number;
}

export function AlertTable({
  points,
  threshold,
  maxRows = 50,
}: AlertTableProps) {
  const alerts = points
    .filter((p) => p.alert)
    .slice(-maxRows)
    .reverse();

  return (
    <section className="alert-table" aria-label="Anomaly alert history">
      <h2>Anomaly alert history</h2>

      {alerts.length === 0 ? (
        <p className="hint">No threshold crossings in this session yet.</p>
      ) : (
        <table>
          <caption className="sr-only">
            Threshold crossings in the current replay session.
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
            {alerts.map((p, i) => (
              <tr key={`${p.timestamp}-${i}`}>
                <td>
                  <time dateTime={p.timestamp}>{p.timestamp}</time>
                </td>
                <td className="num">{p.score.toExponential(4)}</td>
                <td className="num">{threshold.toExponential(4)}</td>
                <td className="num">
                  {(p.score - threshold).toExponential(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}