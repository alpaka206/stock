import type { ChartGuide, ChartMarker, PricePoint } from "@/lib/research/types";
import { cn } from "@/lib/utils";

type ResearchLineChartProps = {
  points: PricePoint[];
  guides?: ChartGuide[];
  markers?: ChartMarker[];
  accent?: "primary" | "positive" | "negative";
  activePointKey?: string;
  highlightRange?: {
    startKey?: string;
    endKey?: string;
  };
  className?: string;
  onPointSelect?: (pointKey: string) => void;
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
  markers = [],
  accent = "primary",
  activePointKey,
  highlightRange,
  className,
  onPointSelect,
}: ResearchLineChartProps) {
  if (points.length === 0) {
    return (
      <div
        className={cn(
          "flex min-h-[240px] items-center justify-center rounded-[calc(var(--radius)*1.2)] border border-dashed border-border/70 bg-background/25 text-sm text-muted-foreground",
          className
        )}
      >
        차트 데이터가 없습니다.
      </div>
    );
  }

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
  const maxVolume = Math.max(...volumes) || 1;
  const step = points.length > 1 ? (width - paddingX * 2) / (points.length - 1) : 0;

  const linePoints = points.map((point, index) => {
    const x = paddingX + step * index;
    const y =
      chartTop +
      chartHeight -
      ((point.close - minValue) / valueRange) * chartHeight;

    return {
      ...point,
      x,
      y,
      key: getPointKey(point),
    };
  });

  const activePoint =
    linePoints.find((point) => point.key === activePointKey) ?? linePoints.at(-1);
  const linePath = linePoints
    .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
    .join(" ");

  const areaPath = `${linePath} L ${linePoints.at(-1)?.x ?? 0} ${
    chartTop + chartHeight
  } L ${linePoints[0]?.x ?? 0} ${chartTop + chartHeight} Z`;

  const markerPoints = markers
    .map((marker) => ({
      ...marker,
      point: linePoints.find((point) => point.key === getMarkerKey(marker)),
    }))
    .filter(
      (marker): marker is typeof marker & { point: (typeof linePoints)[number] } =>
        Boolean(marker.point)
    );

  const rangeStartPoint = linePoints.find(
    (point) => point.key === highlightRange?.startKey
  );
  const rangeEndPoint = linePoints.find(
    (point) => point.key === highlightRange?.endKey
  );

  return (
    <div className={cn("space-y-3", className)}>
      <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <Metric label="고가" value={maxValue.toFixed(2)} />
        <Metric label="저가" value={minValue.toFixed(2)} />
        <Metric label="거래량 피크" value={`${maxVolume.toFixed(0)}x`} />
        <Metric
          label={activePoint ? `${activePoint.label} 종가` : "현재가"}
          value={activePoint?.close.toFixed(2) ?? "-"}
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

          {rangeStartPoint && rangeEndPoint ? (
            <rect
              x={Math.min(rangeStartPoint.x, rangeEndPoint.x)}
              y={chartTop}
              width={Math.abs(rangeEndPoint.x - rangeStartPoint.x)}
              height={chartHeight + volumeHeight + 24}
              fill={accentMap[accent]}
              fillOpacity="0.08"
              rx="10"
            />
          ) : null}

          {guides
            .filter((guide) => guide.enabled !== false)
            .map((guide) => {
              const y =
                chartTop +
                chartHeight -
                ((guide.value - minValue) / valueRange) * chartHeight;

              return (
                <g key={guide.id}>
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

          {markerPoints.map((marker) => (
            <g key={marker.id}>
              <line
                x1={marker.point.x}
                x2={marker.point.x}
                y1={chartTop}
                y2={chartTop + chartHeight}
                stroke={guideToneMap[marker.tone]}
                strokeDasharray="4 6"
                opacity="0.55"
              />
              <circle
                cx={marker.point.x}
                cy={marker.point.y}
                r={5}
                fill={guideToneMap[marker.tone]}
                stroke="var(--background)"
                strokeWidth="2"
              />
              <text
                x={marker.point.x}
                y={chartTop - 2}
                textAnchor="middle"
                fill={guideToneMap[marker.tone]}
                fontSize="10"
                fontWeight="700"
              >
                {marker.label}
              </text>
            </g>
          ))}

          <path d={areaPath} fill={accentMap[accent]} fillOpacity="0.12" />
          <path
            d={linePath}
            fill="none"
            stroke={accentMap[accent]}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {linePoints.map((point, index) => {
            const isActive = point.key === activePoint?.key;

            return (
              <g key={`${point.key}-${index}`}>
                {isActive ? (
                  <line
                    x1={point.x}
                    x2={point.x}
                    y1={chartTop}
                    y2={chartTop + chartHeight}
                    stroke={accentMap[accent]}
                    strokeDasharray="4 4"
                    opacity="0.32"
                  />
                ) : null}
                <circle
                  cx={point.x}
                  cy={point.y}
                  r={isActive ? 5.5 : index === linePoints.length - 1 ? 4.5 : 3}
                  fill={accentMap[accent]}
                  stroke="var(--background)"
                  strokeWidth="2"
                  className={cn(onPointSelect ? "cursor-pointer" : undefined)}
                  onClick={() => onPointSelect?.(point.key)}
                />
              </g>
            );
          })}

          {linePoints.map((point, index) => {
            const barWidth = Math.max(step * 0.56, 14);
            const barHeight = (point.volume / maxVolume) * volumeHeight;
            const barX = point.x - barWidth / 2;
            const barY = volumeTop + volumeHeight - barHeight;
            const isActive = point.key === activePoint?.key;

            return (
              <rect
                key={`volume-${point.key}-${index}`}
                x={barX}
                y={barY}
                width={barWidth}
                height={barHeight}
                rx="4"
                fill={accentMap[accent]}
                fillOpacity={isActive ? "0.42" : "0.24"}
                className={cn(onPointSelect ? "cursor-pointer" : undefined)}
                onClick={() => onPointSelect?.(point.key)}
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

function getPointKey(point: PricePoint) {
  return point.date ?? point.label;
}

function getMarkerKey(marker: ChartMarker) {
  return marker.date ?? marker.pointLabel ?? marker.id;
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
