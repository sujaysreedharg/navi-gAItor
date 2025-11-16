import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import type { FlightEvent, SeriesPoint } from '../types';

interface FlightChartProps {
  data: SeriesPoint[];
  events: FlightEvent[];
}

const formatter = (tick: number) => {
  const minutes = Math.floor(tick / 60);
  const seconds = tick % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
};

export function FlightChart({ data, events }: FlightChartProps) {
  if (!data.length) {
    return null;
  }

  const criticalMarkers = events.filter((event) => event.severity === 'critical');

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Profile</p>
          <h2>Altitude & Airspeed Timeline</h2>
        </div>
      </div>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height={360}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
            <XAxis dataKey="time_seconds" tickFormatter={formatter} stroke="rgba(255,255,255,0.4)" />
            <YAxis yAxisId="left" stroke="rgba(33,150,243,0.7)" tickFormatter={(v) => `${v} ft`} />
            <YAxis yAxisId="right" orientation="right" stroke="rgba(76,175,80,0.7)" tickFormatter={(v) => `${v} kt`} />
            <Tooltip
              contentStyle={{ background: '#0b0d10', border: '1px solid rgba(255,255,255,0.08)' }}
              labelFormatter={(value) => `T+ ${formatter(Number(value))}`}
            />
            <Legend />
            {data[0].alt_msl_ft !== undefined && (
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="alt_msl_ft"
                stroke="#5cc8ff"
                dot={false}
                name="Altitude"
                strokeWidth={2}
              />
            )}
            {data[0].airspeed_indicated_kt !== undefined && (
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="airspeed_indicated_kt"
                stroke="#80ff8f"
                dot={false}
                name="Airspeed"
                strokeWidth={2}
              />
            )}
            {criticalMarkers.map((event) => (
              <ReferenceLine
                key={`${event.type}-${event.time_seconds}`}
                x={event.time_seconds}
                stroke="#ff6b6b"
                strokeDasharray="3 3"
                label={{ value: event.type.replace('_', ' '), position: 'top', fill: '#ff6b6b' }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
