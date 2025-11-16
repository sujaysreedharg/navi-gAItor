import { motion } from 'framer-motion';
import clsx from 'clsx';
import type { FlightEvent } from '../types';

const severityToHue: Record<FlightEvent['severity'], string> = {
  critical: '#ff6b6b',
  warning: '#ffc857',
  info: '#5cc8ff',
};

interface EventsTimelineProps {
  events: FlightEvent[];
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export function EventsTimeline({ events }: EventsTimelineProps) {
  return (
    <div className="panel grow">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Events</p>
          <h2>Timeline</h2>
        </div>
      </div>
      <div className="timeline">
        {events.length === 0 && <p className="muted">No events detected—smooth flight!</p>}
        {events.map((event, index) => (
          <motion.div
            key={`${event.type}-${event.time_seconds}-${index}`}
            className={clsx('timeline-item', `severity-${event.severity}`)}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.03, duration: 0.3 }}
          >
            <span className="timeline-dot" style={{ background: severityToHue[event.severity] }} />
            <div className="timeline-content">
              <div className="timeline-meta">
                <p>{event.type.replace(/_/g, ' ')}</p>
                <span>{formatTime(event.time_seconds)}</span>
              </div>
              <p>{event.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
