export interface ConfusionMatrixProps {
  tp: number;
  fn: number;
  fp: number;
  tn: number;
}

export function ConfusionMatrix({ tp, fn, fp, tn }: ConfusionMatrixProps) {
  return (
    <div
      className="confusion-matrix"
      role="figure"
      aria-label="Point-level confusion matrix"
    >
      <table>
        <thead>
          <tr>
            <th scope="col"></th>
            <th scope="col">Predicted alert</th>
            <th scope="col">Predicted normal</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">Actual attack</th>
            <td className="cm-cell cm-tp">
              <div className="cm-value">{tp.toLocaleString()}</div>
              <div className="cm-label">True positive</div>
            </td>
            <td className="cm-cell cm-fn">
              <div className="cm-value">{fn.toLocaleString()}</div>
              <div className="cm-label">False negative</div>
            </td>
          </tr>
          <tr>
            <th scope="row">Actual normal</th>
            <td className="cm-cell cm-fp">
              <div className="cm-value">{fp.toLocaleString()}</div>
              <div className="cm-label">False positive</div>
            </td>
            <td className="cm-cell cm-tn">
              <div className="cm-value">{tn.toLocaleString()}</div>
              <div className="cm-label">True negative</div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}