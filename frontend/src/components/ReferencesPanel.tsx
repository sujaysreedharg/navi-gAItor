import type { ReferenceSnippet } from '../types';

interface ReferencesPanelProps {
  references: ReferenceSnippet[];
}

export function ReferencesPanel({ references }: ReferencesPanelProps) {
  if (!references.length) {
    return null;
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Regulations</p>
          <h2>You.com Citations</h2>
        </div>
      </div>
      <div className="references">
        {references.map((ref) => (
          <div key={`${ref.event_type}-${ref.url}`} className="reference-item">
            <p className="reference-tag">{ref.event_type.replace(/_/g, ' ')}</p>
            <a href={ref.url} target="_blank" rel="noreferrer">
              {ref.title}
            </a>
            <p>{ref.snippet}</p>
            <span>{ref.domain}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
