import type { ScorePoint } from "./ScoreChart";

export interface AlertTableProps {
  points: ScorePoint[];
  threshold: number;
  interpretation?: string;
  maxRows?: number;
}

const DEFAULT_INTERPRETATION =
  "Alert indicates the model's anomaly score exceeded the frozen threshold. " +
  "It is not a confirmed attack, equipment failure, or safety event. " +
  "Human review is required.";

export function AlertTable({
  points,
  threshold,
  interpretation = DEFAULT_INTERPRETATION,
  maxRows = 50,
}: AlertTableProps) {
  const alerts = points
    .filter((p) => p.alert)
    .slice(-maxRows)
    .reverse(); // newest first

  return (
    <section className="alert-table" aria-label="Anomaly alert history">
      <h2>Anomaly alert history</h2>
      <p className="alert-table-caption">{interpretation}</p>

      {alerts.length === 0 ? (
        <p className="hint">
          No threshold-exceeding observations in this replay so far. This is
          not evidence of normal operation — the frozen threshold produces
          roughly 1% alerts on the calibration partition and ~3.2% on the
          validation partition (NB13 Cell 6).
        </p>
      ) : (
        <table>
          <caption className="sr-only">
            Alerts where the anomaly score exceeded the frozen threshold.
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