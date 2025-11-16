import { type FormEvent, useState } from 'react';
import type { PresetWindow } from '../types';
import type { AiLogEntry } from '../hooks/useAiConsole';
import ReactMarkdown from 'react-markdown';

interface AiConsoleProps {
  logs: AiLogEntry[];
  onSubmit: (command: string, window?: { start: number; end: number }) => void;
  pending: boolean;
  window: [number, number];
  presets: PresetWindow[];
  initialDebrief?: string;
}

export function AiConsole({ logs, onSubmit, pending, window, presets, initialDebrief }: AiConsoleProps) {
  const [command, setCommand] = useState('');
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!command.trim()) return;
    const presetWindow = selectedPreset
      ? presets.find((preset) => preset.id === selectedPreset)?.window
      : window;
    onSubmit(command, { start: presetWindow?.[0] ?? window[0], end: presetWindow?.[1] ?? window[1] });
    setCommand('');
  };

  return (
    <div className="panel ai-console">
      <div className="panel-header">
        <div>
          <p className="eyebrow">AI Flight Instructor</p>
          <h2>NavigAGENT</h2>
        </div>
      </div>

      {initialDebrief && (
        <div className="initial-debrief">
          <p className="debrief-label">Post-Flight Debrief</p>
          <div className="debrief-markdown compact">
            <ReactMarkdown>{initialDebrief}</ReactMarkdown>
          </div>
        </div>
      )}

      <form className="ai-input" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Ask follow-up questions like 'Why did HF index spike at t=120?'"
          value={command}
          onChange={(event) => setCommand(event.target.value)}
          disabled={pending}
        />
        <button type="submit" disabled={pending}>
          {pending ? 'Analyzing…' : 'Ask'}
        </button>
      </form>

      <div className="preset-row">
        {presets.map((preset) => (
          <button
            key={preset.id}
            className={selectedPreset === preset.id ? 'chip active' : 'chip'}
            onClick={() => setSelectedPreset(preset.id)}
          >
            {preset.label}
          </button>
        ))}
      </div>

      {logs.length > 0 && (
        <div className="ai-log">
          {logs.map((entry) => (
            <div key={entry.id} className="ai-log-entry">
              <p className="ai-command">&gt;&gt;&gt; {entry.command}</p>
              <div className="ai-response">
                <ReactMarkdown>{entry.response}</ReactMarkdown>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="ai-actions">
        <button onClick={() => onSubmit('Analyze current window', { start: window[0], end: window[1] })}>
          Analyze Window
        </button>
        <button onClick={() => onSubmit('List top 5 HF risk hotspots', undefined)}>
          Top HF Hotspots
        </button>
        <button onClick={() => onSubmit('Compare to ACS standards', undefined)}>
          ACS Check
        </button>
      </div>
    </div>
  );
}
