import { useCallback, useMemo, useState } from 'react';
import { analyzeFlight } from '../lib/api';
import type { AnalysisResponse } from '../types';

type Status = 'idle' | 'uploading' | 'processing' | 'ready' | 'error';

export function useFlightAnalysis() {
  const [status, setStatus] = useState<Status>('idle');
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const analyze = useCallback(async (file: File) => {
    setError(null);
    setProgress(0);
    setStatus('uploading');
    try {
      const response = await analyzeFlight(file, (p) => setProgress(p));
      setStatus('processing');
      // Simulate slight delay for animation polish
      await new Promise((resolve) => setTimeout(resolve, 400));
      setResult(response);
      setStatus('ready');
    } catch (err) {
      console.error(err);
      setError(
        err instanceof Error ? err.message : 'Analysis failed. Please try again.'
      );
      setStatus('error');
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setProgress(0);
    setStatus('idle');
    setError(null);
  }, []);

  const meta = useMemo(
    () => ({ status, progress, error, hasResult: Boolean(result) }),
    [status, progress, error, result]
  );

  return { analyze, reset, result, meta } as const;
}
