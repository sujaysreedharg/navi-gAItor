import { AnimatePresence, motion } from 'framer-motion';
import { useEffect, useMemo, useState } from 'react';
import { HeroHeader } from './components/HeroHeader';
import { UploadPanel } from './components/UploadPanel';
import { SummaryGrid } from './components/SummaryGrid';
import { ReferencesPanel } from './components/ReferencesPanel';
import { LoadingOverlay } from './components/LoadingOverlay';
import { useFlightAnalysis } from './hooks/useFlightAnalysis';
import { SignalStrip } from './components/SignalStrip';
import { RulePanel } from './components/RulePanel';
import { AiConsole } from './components/AiConsole';
import { useAiConsole } from './hooks/useAiConsole';
import './App.css';

function ResultHeader({ filename, counts }: { filename: string; counts: { critical: number; warning: number; info: number } }) {
  const chips = [
    { label: 'Critical', value: counts.critical, color: '#ff6b6b' },
    { label: 'Warning', value: counts.warning, color: '#ffc857' },
    { label: 'Info', value: counts.info, color: '#5cc8ff' },
  ];
  return (
    <div className="panel result-header">
      <div>
        <p className="eyebrow">Analyzed File</p>
        <h2>{filename}</h2>
      </div>
      <div className="chip-row">
        {chips.map((chip) => (
          <span key={chip.label} className="chip" style={{ borderColor: chip.color }}>
            <strong style={{ color: chip.color }}>{chip.value}</strong>
            {chip.label}
          </span>
        ))}
      </div>
    </div>
  );
}

function App() {
  const { analyze, reset, result, meta } = useFlightAnalysis();
  const [cursorTime, setCursorTime] = useState(0);
  const [windowRange, setWindowRange] = useState<[number, number]>([0, 0]);
  const ai = useAiConsole(result?.summary ?? null, result?.rule_events ?? []);

  useEffect(() => {
    if (!result) return;
    const duration = result.signal_matrix.at(-1)?.time_seconds ?? result.series_data.at(-1)?.time_seconds ?? 0;
    const defaultWindow = result.presets?.[0]?.window ?? [0, duration];
    setWindowRange(defaultWindow);
    setCursorTime(defaultWindow[0]);
  }, [result]);

  const presets = useMemo(() => {
    if (!result) return [];
    const duration =
      result.signal_matrix.at(-1)?.time_seconds ?? result.series_data.at(-1)?.time_seconds ?? 0;
    if (result.presets && result.presets.length > 0) return result.presets;
    return [{ id: 'full', label: 'Full Flight', window: [0, duration] as [number, number] }];
  }, [result]);

  return (
    <div className="app-shell">
      <HeroHeader />
      <UploadPanel
        disabled={meta.status === 'uploading' || meta.status === 'processing'}
        status={meta.status}
        progress={meta.progress}
        error={meta.error}
        onUpload={analyze}
        onReset={reset}
      />

      <AnimatePresence>
        {result && (
          <motion.div
            className="results-grid"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
          >
            <ResultHeader filename={result.filename} counts={result.events_count} />
            <SummaryGrid summary={result.summary} />
            <SignalStrip
              data={result.signal_matrix}
              meta={result.signal_meta}
              risk={result.risk_trace}
              cursor={cursorTime}
              onCursorChange={setCursorTime}
              window={windowRange}
              onWindowChange={setWindowRange}
              presets={presets}
            />
            <div className="grid two-column">
              <RulePanel events={result.rule_events} onJump={setCursorTime} />
              <AiConsole
                logs={ai.logs}
                onSubmit={(command, window) => ai.runCommand(command, window)}
                pending={ai.pending}
                window={windowRange}
                presets={presets}
                initialDebrief={result.debrief}
              />
            </div>
            <ReferencesPanel references={result.references} />
          </motion.div>
        )}
      </AnimatePresence>

      <LoadingOverlay status={meta.status} progress={meta.progress} />
    </div>
  );
}

export default App;
