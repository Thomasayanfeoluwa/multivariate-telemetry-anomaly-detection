import { useEffect, useState } from "react";
import { api, ApiError } from "../api/apiClient";
import type { EvaluationSummaryResponse } from "../types/api";

function formatError(e: unknown): string {
  if (e instanceof ApiError) return `${e.status}: ${e.detail}`;
  if (e instanceof Error) return e.message;
  return String(e);
}

export function EvaluationSummary() {
  const [data, setData] = useState<EvaluationSummaryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    api
      .evaluationSummary()
      .then(
        (d) => {
          if (!cancelled) {
            setData(d);
            setLoading(false);
          }
        },
        (e) => {
          if (!cancelled) {
            setError(formatError(e));
            setLoading(false);
          }
        },
      );
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <section className="evaluation-summary" aria-label="Retrospective evaluation">
        <h2>Retrospective benchmark evaluation</h2>
        <p className="hint">Loading evaluation artifacts…</p>
      </section>
    );
  }

  if (error || data === null) {
    return (
      <section className="evaluation-summary" aria-label="Retrospective evaluation">
        <h2>Retrospective benchmark evaluation</h2>
        <p className="error" role="alert">
          Could not load evaluation summary: {error ?? "unknown error"}
        </p>
      </section>
    );
  }

  return (
    <section
      className="evaluation-summary retrospective"
      aria-label="Retrospective benchmark evaluation"
    >
      <header className="retro-header">
        <h2>Retrospective benchmark evaluation</h2>
        <p className="badge">Not live inference — offline evaluation</p>
      </header>

      <p className="disclaimer">{data.disclaimer}</p>

      <p className="meta">
        <strong>Decision:</strong> {data.decision} &nbsp;|&nbsp;
        <strong>Method:</strong> {data.method} &nbsp;|&nbsp;
        <strong>Window:</strong> {data.window_size} &nbsp;|&nbsp;
        <strong>Threshold:</strong> {data.threshold.toExponential(4)}
      </p>

      <div className="eval-grid">
        <div className="eval-block">
          <h3>Score parity vs frozen NB08 scores</h3>
          <dl>
            <dt>Sequences rescored</dt>
            <dd>{data.parity.n_sequences.toLocaleString()}</dd>
            <dt>Max |score diff|</dt>
            <dd>{data.parity.max_abs_diff_score.toExponential(3)}</dd>
            <dt>Flag disagreements</dt>
            <dd>{data.parity.flag_disagreements}</dd>
          </dl>
        </div>

        <div className="eval-block">
          <h3>Point-level outcomes</h3>
          <dl>
            <dt>Validation alerts (FP)</dt>
            <dd>{data.point_level.validation_fp_count.toLocaleString()}</dd>
            <dt>Attack alerts (TP)</dt>
            <dd>{data.point_level.attack_tp_count.toLocaleString()}</dd>
          </dl>
        </div>

        <div className="eval-block">
          <h3>Event-level outcomes</h3>
          <dl>
            <dt>Scenarios detected</dt>
            <dd>
              {data.event_level.scenarios_detected} / {data.event_level.scenarios_total}
            </dd>
            <dt>Scenarios missed</dt>
            <dd>{data.event_level.scenarios_missed}</dd>
            <dt>Median detection delay</dt>
            <dd>{data.event_level.median_delay_s.toFixed(2)} s</dd>
            <dt>p90 delay</dt>
            <dd>{data.event_level.p90_delay_s.toFixed(2)} s</dd>
            <dt>Max delay</dt>
            <dd>{data.event_level.max_delay_s.toFixed(2)} s</dd>
            <dt>Validation FP periods</dt>
            <dd>
              {data.event_level.validation_fp_periods} (grouped at ≤{" "}
              {data.event_level.period_gap_limit_s} s gaps)
            </dd>
          </dl>
          <p className="interpretation-note">
            A median delay of ~0 s means the first alert coincides with the
            first scored observation of a detected scenario. It does{" "}
            <strong>not</strong> mean the model predicts attacks before they
            occur. Validation FP periods count <em>clusters</em> of
            consecutive alerts, not individual flagged observations.
          </p>
        </div>

        <div className="eval-block">
          <h3>Inference performance (CPU, NB13 Cell 7)</h3>
          <dl>
            <dt>Batch=1 median latency</dt>
            <dd>{data.performance.batch1_median_ms.toFixed(2)} ms</dd>
            <dt>Batch=1 utilization at 1 Hz</dt>
            <dd>{data.performance.batch1_utilization_pct_1hz.toFixed(3)}%</dd>
            <dt>Batch=1 throughput</dt>
            <dd>
              {data.performance.batch1_throughput_seqs_per_s.toFixed(1)} seq/s
            </dd>
            <dt>Batch=512 median latency</dt>
            <dd>{data.performance.batch512_median_ms.toFixed(2)} ms</dd>
            <dt>Batch=512 throughput</dt>
            <dd>
              {data.performance.batch512_throughput_seqs_per_s.toFixed(1)} seq/s
            </dd>
          </dl>
        </div>
      </div>

      <p className="source-note">
        Source artifacts: <code>{data.source_artifact}</code>. These numbers
        were computed by Notebook 13's offline evaluation; they are independent
        of any live replay in progress above.
      </p>
    </section>
  );
}