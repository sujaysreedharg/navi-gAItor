import type { ReferenceSnippet } from '../types';

interface ReferencesPanelProps {
  references: ReferenceSnippet[];
}

export function ReferencesPanel({ references }: ReferencesPanelProps) {
  if (!references.length) {
    return null;
  }

  return (
    <div className="panel references-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">FAA & Regulatory Context</p>
          <h2>You.com Citations</h2>
        </div>
        <p className="help-text">Referenced in debrief above using [1], [2], etc.</p>
      </div>
      <div className="references-grid">
        {references.map((ref, index) => (
          <div key={`${ref.event_type}-${ref.url}`} className="reference-card">
            <div className="reference-header">
              <span className="reference-number">[{index + 1}]</span>
              <span className="reference-tag">{ref.event_type.replace(/_/g, ' ')}</span>
            </div>
            <a href={ref.url} target="_blank" rel="noreferrer" className="reference-title">
              {ref.title}
            </a>
            <p className="reference-snippet">{ref.snippet.substring(0, 180)}...</p>
            <div className="reference-footer">
              <span className="reference-domain">📚 {ref.domain}</span>
              <a href={ref.url} target="_blank" rel="noreferrer" className="reference-link">
                View Source →
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
