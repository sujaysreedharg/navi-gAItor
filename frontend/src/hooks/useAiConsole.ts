import { useCallback, useState } from 'react';
import { runAiAgent } from '../lib/api';
import type { FlightSummary, RuleEvent } from '../types';

export interface AiLogEntry {
  id: string;
  command: string;
  response: string;
  timestamp: number;
}

export function useAiConsole(summary: FlightSummary | null, ruleEvents: RuleEvent[]) {
  const [logs, setLogs] = useState<AiLogEntry[]>([]);
  const [pending, setPending] = useState(false);

  const runCommand = useCallback(
    async (command: string, window?: { start: number; end: number }) => {
      if (!summary || !command.trim()) return;
      setPending(true);
      const id = `${Date.now()}-${Math.random()}`;
      try {
        const response = await runAiAgent({
          command,
          window_start: window?.start,
          window_end: window?.end,
          summary,
          rule_events: ruleEvents,
        });
        setLogs((prev) => [
          ...prev,
          {
            id,
            command,
            response: response.log,
            timestamp: Date.now(),
          },
        ]);
      } catch (error) {
        setLogs((prev) => [
          ...prev,
          {
            id,
            command,
            response: `ERROR: ${(error as Error).message}`,
            timestamp: Date.now(),
          },
        ]);
      } finally {
        setPending(false);
      }
    },
    [summary, ruleEvents]
  );

  const reset = useCallback(() => {
    setLogs([]);
  }, []);

  return { logs, runCommand, pending, reset } as const;
}
