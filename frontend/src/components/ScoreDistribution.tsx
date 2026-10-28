import { useMemo } from "react";
import type { ScorePoint } from "./ScoreChart";

export interface ScoreDistributionProps {
    points: ScorePoint[];
    threshold: number;
    width?: number;
    height?: number;
    bins?: number;
}

const PAD = { top: 20, right: 16, bottom: 40, left: 56 };

export function ScoreDistribution({
    points,
    threshold,
    width = 720,
    height = 260,
    bins = 30,
}: ScoreDistributionProps) {
    const peak = useMemo(
        () => points.reduce((m, p) => (p.score > m ? p.score : m), 0),
        [points],
    );

    if (points.length < 20) {
        return (
            <section
                className="score-distribution"
                aria-label="Score distribution"
            >
                <h2>Score distribution</h2>
                <p className="hint">
                    Available after 20 scored observations. Replay to accumulate scores.
                </p>
            </section>
        );
    }

    const scoreMax = Math.max(threshold * 1.5, peak * 1.05, 1e-6);
    const binWidth = scoreMax / bins;
    const counts = new Array<number>(bins).fill(0);
    for (const p of points) {
        const b = Math.min(bins - 1, Math.floor(p.score / binWidth));
        if (b >= 0) counts[b] += 1;
    }

    const maxCount = counts.reduce((m, c) => (c > m ? c : m), 1);
    const innerW = width - PAD.left - PAD.right;
    const innerH = height - PAD.top - PAD.bottom;
    const barW = innerW / bins;
    const thresholdBin = Math.min(
        bins - 1,
        Math.max(0, threshold / binWidth),
    );

    const xForBin = (b: number) => PAD.left + b * barW;
    const yForCount = (c: number) =>
        PAD.top + innerH - (c / maxCount) * innerH;

    return (
        <section className="score-distribution" aria-label="Score distribution">
            <h2>Score distribution</h2>
            <svg
                viewBox={`0 0 ${width} ${height}`}
                width="100%"
                role="img"
                aria-label={`Histogram of ${points.length} anomaly scores, ${counts.filter((_, i) => i >= thresholdBin).reduce((a, b) => a + b, 0)} above threshold`}
            >
                {/* Threshold marker (behind bars) */}
                <line
                    x1={PAD.left + thresholdBin * barW}
                    x2={PAD.left + thresholdBin * barW}
                    y1={PAD.top}
                    y2={PAD.top + innerH}
                    stroke="#f59e0b"
                    strokeWidth={1.5}
                    strokeDasharray="4 3"
                />
                <text
                    x={PAD.left + thresholdBin * barW + 4}
                    y={PAD.top + 12}
                    fontSize={10}
                    fill="#f59e0b"
                >
                    threshold
                </text>

                {/* Bars */}
                {counts.map((c, i) => {
                    if (c === 0) return null;
                    const x = xForBin(i);
                    const y = yForCount(c);
                    const h = PAD.top + innerH - y;
                    const aboveThreshold = i >= thresholdBin;
                    return (
                        <rect
                            key={i}
                            x={x + 1}
                            y={y}
                            width={Math.max(1, barW - 2)}
                            height={h}
                            fill={aboveThreshold ? "#ef4444" : "#14b8a6"}
                            opacity={aboveThreshold ? 0.85 : 0.7}
                        />
                    );
                })}

                {/* Baseline */}
                <line
                    x1={PAD.left}
                    x2={width - PAD.right}
                    y1={PAD.top + innerH}
                    y2={PAD.top + innerH}
                    stroke="#3b5875"
                    strokeWidth={1}
                />

                {/* X-axis labels */}
                <text
                    x={PAD.left}
                    y={height - 20}
                    fontSize={10}
                    fill="#8ba3ba"
                    textAnchor="middle"
                >
                    0
                </text>
                <text
                    x={width - PAD.right}
                    y={height - 20}
                    fontSize={10}
                    fill="#8ba3ba"
                    textAnchor="end"
                >
                    {scoreMax.toExponential(2)}
                </text>
                <text
                    x={(PAD.left + width - PAD.right) / 2}
                    y={height - 6}
                    fontSize={10}
                    fill="#8ba3ba"
                    textAnchor="middle"
                >
                    anomaly score
                </text>

                {/* Y-axis max label */}
                <text
                    x={PAD.left - 6}
                    y={PAD.top + 6}
                    fontSize={10}
                    fill="#8ba3ba"
                    textAnchor="end"
                >
                    {maxCount.toLocaleString()}
                </text>
            </svg>
            <p className="chart-caption">
                Score distribution across {points.length.toLocaleString()} observations
                · amber line: threshold · red bars: above threshold
            </p>
        </section>
    );
}