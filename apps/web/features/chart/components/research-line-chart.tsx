import type { ChartGuide, PricePoint } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type ResearchLineChartProps = {
  points: PricePoint[];
  guides?: ChartGuide[];
  accent?: "primary" | "positive" | "negative";
  className?: string;
};

const accentMap = {
  primary: "var(--primary)",
  positive: "var(--positive)",
  negative: "var(--negative)",
} as const;

const guideToneMap = {
  positive: "var(--positive)",
  negative: "var(--negative)",
  neutral: "var(--neutral)",
} as const;

export function ResearchLineChart({
  points,
  guides = [],
  accent = "primary",
  className,
}: ResearchLineChartProps) {
  const width = 680;
  const height = 320;
  const paddingX = 18;
  const chartTop = 20;
  const chartHeight = 192;
  const volumeTop = 236;
  const volumeHeight = 48;
  const values = points.map((point) => point.close);
  const volumes = points.map((point) => point.volume);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);
  const valueRange = maxValue - minValue || 1;
  const maxVolume = Math.max(...volumes);
  const step = points.length > 1 ? (width - paddingX * 2) / (points.length - 1) : 0;

  const linePoints = points.map((point, index) => {
    const x = paddingX + step * index;
    const y =
      chartTop +
      chartHeight -
      ((point.close - minValue) / valueRange) * chartHeight;

    return { ...point, x, y };
  });

  const linePath = linePoints
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");

  const areaPath = `${linePath} L ${linePoints.at(-1)?.x ?? 0} ${
    chartTop + chartHeight
  } L ${linePoints[0]?.x ?? 0} ${chartTop + chartHeight} Z`;

  return (
    <div className={cn("space-y-3", className)}>
      <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <Metric label="고가" value={maxValue.toFixed(2)} />
        <Metric label="저가" value={minValue.toFixed(2)} />
        <Metric
          label="거래량 피크"
          value={`${maxVolume.toFixed(0)}x`}
        />
        <Metric
          label="현재가"
          value={linePoints.at(-1)?.close.toFixed(2) ?? "-"}
        />
      </div>

      <div className="rounded-[calc(var(--radius)*1.2)] border border-border/55 bg-background/30 p-3">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full">
          {[0, 1, 2, 3].map((index) => {
            const y = chartTop + (chartHeight / 3) * index;

            return (
              <line
                key={index}
                x1={paddingX}
                x2={width - paddingX}
                y1={y}
                y2={y}
                stroke="color-mix(in oklch, var(--border) 80%, transparent)"
                strokeDasharray="4 6"
              />
            );
          })}

          {guides.map((guide) => {
            const y =
              chartTop +
              chartHeight -
              ((guide.value - minValue) / valueRange) * chartHeight;

            return (
              <g key={guide.label}>
                <line
                  x1={paddingX}
                  x2={width - paddingX}
                  y1={y}
                  y2={y}
                  stroke={guideToneMap[guide.tone]}
                  strokeDasharray="6 6"
                  opacity="0.8"
                />
                <text
                  x={width - paddingX}
                  y={y - 6}
                  textAnchor="end"
                  fill={guideToneMap[guide.tone]}
                  fontSize="11"
                  fontWeight="600"
                >
                  {guide.label}
                </text>
              </g>
            );
          })}

          <path d={areaPath} fill={accentMap[accent]} fillOpacity="0.12" />
          <path
            d={linePath}
            fill="none"
            stroke={accentMap[accent]}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {linePoints.map((point, index) => (
            <circle
              key={`${point.label}-${index}`}
              cx={point.x}
              cy={point.y}
              r={index === linePoints.length - 1 ? 4.5 : 3}
              fill={accentMap[accent]}
              stroke="var(--background)"
              strokeWidth="2"
            />
          ))}

          {linePoints.map((point, index) => {
            const barWidth = Math.max(step * 0.56, 14);
            const barHeight = (point.volume / maxVolume) * volumeHeight;
            const barX = point.x - barWidth / 2;
            const barY = volumeTop + volumeHeight - barHeight;

            return (
              <rect
                key={`volume-${point.label}-${index}`}
                x={barX}
                y={barY}
                width={barWidth}
                height={barHeight}
                rx="4"
                fill={accentMap[accent]}
                fillOpacity="0.24"
              />
            );
          })}
        </svg>

        <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
          <span>{points[0]?.label}</span>
          <span>{points.at(-1)?.label}</span>
        </div>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border/50 bg-background/30 px-3 py-2">
      <p className="text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
        {label}
      </p>
      <p className="numeric mt-1 text-sm font-semibold">{value}</p>
    </div>
  );
}
