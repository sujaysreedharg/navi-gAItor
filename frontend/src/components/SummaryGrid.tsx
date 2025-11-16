import { motion } from 'framer-motion';
import type { FlightSummary } from '../types';

const cards = [
  { key: 'total_duration_minutes', label: 'Duration', formatter: (v?: number) => (v ? `${v.toFixed(1)} min` : '—') },
  { key: 'max_altitude_ft', label: 'Max Altitude', formatter: (v?: number) => formatNumber(v, 'ft') },
  { key: 'max_airspeed_kt', label: 'Max Airspeed', formatter: (v?: number) => formatNumber(v, 'kt') },
  { key: 'max_bank_angle_deg', label: 'Max Bank', formatter: (v?: number) => formatNumber(v, '°') },
  { key: 'max_positive_g', label: 'Max +G', formatter: (v?: number) => (v ? `${v.toFixed(2)} G` : '—') },
  { key: 'fuel_consumed_gal', label: 'Fuel Used', formatter: (v?: number) => formatNumber(v, 'gal') },
] as const;

function formatNumber(value?: number, unit?: string) {
  if (value === undefined || Number.isNaN(value)) return '—';
  return `${Math.round(value).toLocaleString()} ${unit ?? ''}`.trim();
}

interface SummaryGridProps {
  summary: FlightSummary;
}

export function SummaryGrid({ summary }: SummaryGridProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Snapshot</p>
          <h2>Flight Metrics</h2>
        </div>
      </div>
      <div className="summary-grid">
        {cards.map((card, index) => (
          <motion.div
            key={card.key}
            className="summary-card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05, duration: 0.4 }}
          >
            <p>{card.label}</p>
            <h3>{card.formatter(summary[card.key])}</h3>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
