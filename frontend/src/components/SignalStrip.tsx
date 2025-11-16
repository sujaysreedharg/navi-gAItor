import { useMemo } from 'react';
import {
  ComposedChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
  Area,
  Legend,
} from 'recharts';
import type {
  SignalMatrixPoint,
  SignalMeta,
  RiskPoint,
  PresetWindow,
} from '../types';

const COLORS = ['#63c6ff', '#80ff8f', '#ffb347', '#d66bff', '#64d2f0', '#f77fbe'];

type SignalStripProps = {
  data: SignalMatrixPoint[];
  meta: SignalMeta[];
  risk: RiskPoint[];
  cursor: number;
  onCursorChange: (time: number) => void;
  window: [number, number];
  onWindowChange: (window: [number, number]) => void;
  presets: PresetWindow[];
};

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export function SignalStrip({
  data,
  meta,
  risk,
  cursor,
  onCursorChange,
  window,
  onWindowChange,
  presets,
}: SignalStripProps) {
  const riskLookup = useMemo(() => {
    const map = new Map<number, number>();
    risk.forEach((point) => map.set(Number(point.time_seconds.toFixed(1)), point.hf_index));
    return map;
  }, [risk]);

  const merged = useMemo(
    () =>
      data.map((point) => ({
        ...point,
        hf_index: riskLookup.get(Number(point.time_seconds.toFixed(1))) ?? 0,
      })),
    [data, riskLookup]
  );

  const filtered = merged.filter(
    (point) => point.time_seconds >= window[0] && point.time_seconds <= window[1]
  );

  const startIndex = Math.max(0, merged.findIndex((p) => p.time_seconds >= window[0]));
  const endIndex = Math.min(merged.length - 1, merged.findIndex((p) => p.time_seconds >= window[1]));

  const handleBrushChange = (range: { startIndex?: number; endIndex?: number }) => {
    if (range.startIndex === undefined || range.endIndex === undefined) return;
    const start = merged[Math.max(0, range.startIndex)]?.time_seconds ?? 0;
    const end = merged[Math.min(merged.length - 1, range.endIndex)]?.time_seconds ?? start;
    onWindowChange([start, end]);
  };

  const handleMouseMove = (state: any) => {
    if (!state || !state.activeLabel) return;
    onCursorChange(state.activeLabel as number);
  };

  return (
    <div className="panel signal-strip">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Profile</p>
          <h2>Signal Strip</h2>
        </div>
        <div className="preset-row">
          {presets.map((preset) => (
            <button
              key={preset.id}
              className="ghost-btn"
              onClick={() => onWindowChange(preset.window)}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      <div className="chart-wrapper large">
        <ResponsiveContainer width="100%" height={360}>
          <ComposedChart data={filtered} onMouseMove={handleMouseMove} syncId="signal-strip">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
            <XAxis
              dataKey="time_seconds"
              tickFormatter={formatTime}
              stroke="rgba(255,255,255,0.4)"
            />
            <YAxis yAxisId="left" stroke="#63c6ff" orientation="left" allowDataOverflow />
            <YAxis yAxisId="right" stroke="#80ff8f" orientation="right" allowDataOverflow />
            <YAxis yAxisId="risk" domain={[0, 100]} hide />
            <Tooltip
              contentStyle={{ background: '#0b0d10', border: '1px solid rgba(255,255,255,0.08)' }}
              labelFormatter={(value) => `T+ ${formatTime(Number(value))}`}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="hf_index"
              yAxisId="risk"
              fill="rgba(255, 99, 132, 0.2)"
              stroke="rgba(255, 99, 132, 0.6)"
              name="HF Index"
            />
            {meta.map((signal, index) => (
              <Line
                key={signal.key}
                type="monotone"
                dataKey={signal.key}
                yAxisId={signal.axis === 'right' ? 'right' : 'left'}
                stroke={COLORS[index % COLORS.length]}
                dot={false}
                name={`${signal.label} (${signal.unit})`}
                strokeWidth={2}
              />
            ))}
            <ReferenceLine x={cursor} stroke="#ffffff" strokeDasharray="4 2" />
            <Brush
              dataKey="time_seconds"
              height={24}
              stroke="#63c6ff"
              startIndex={startIndex}
              endIndex={endIndex > -1 ? endIndex : merged.length - 1}
              onChange={handleBrushChange}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="cursor-controls">
        <label>
          Cursor @ {formatTime(cursor)}
          <input
            type="range"
            min={window[0]}
            max={window[1]}
            step={0.5}
            value={cursor}
            onChange={(event) => onCursorChange(Number(event.target.value))}
          />
        </label>
      </div>
    </div>
  );
}
