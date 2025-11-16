import clsx from 'clsx';
import type { RuleEvent } from '../types';

type RulePanelProps = {
  events: RuleEvent[];
  onJump: (time: number) => void;
};

const severityIcon: Record<RuleEvent['severity'], string> = {
  critical: '🔴',
  warning: '🟠',
  info: '🔵',
};

export function RulePanel({ events, onJump }: RulePanelProps) {
  return (
    <div className="panel rule-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Events</p>
          <h2>Rule Engine Output</h2>
        </div>
      </div>
      <div className="rule-list">
        {events.length === 0 && <p className="muted">No rules triggered.</p>}
        {events.map((event, index) => (
          <button
            key={`${event.rule}-${index}`}
            className={clsx('rule-row', `severity-${event.severity}`)}
            onClick={() => onJump(event.time_seconds)}
          >
            <div className="rule-left">
              <span>{severityIcon[event.severity]}</span>
              <div>
                <p className="rule-name">{event.rule}</p>
                <p className="rule-desc">{event.description}</p>
              </div>
            </div>
            <div className="rule-right">
              <p>{event.time_seconds.toFixed(1)}s</p>
              <div className="rule-values">
                {Object.entries(event.values || {}).map(([key, value]) => (
                  <span key={key}>
                    {key}: {value}
                  </span>
                ))}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
