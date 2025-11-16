import { motion } from 'framer-motion';

interface LoadingOverlayProps {
  status: 'idle' | 'uploading' | 'processing' | 'ready' | 'error';
  progress: number;
}

export function LoadingOverlay({ status, progress }: LoadingOverlayProps) {
  if (status === 'idle' || status === 'ready' || status === 'error') return null;
  const label = status === 'uploading' ? 'Uploading flight log…' : 'Analyzing telemetry…';

  return (
    <motion.div
      className="loading-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="loading-card">
        <div className="spinner" />
        <p>{label}</p>
        {status === 'uploading' && <p className="muted">{progress}%</p>}
      </div>
    </motion.div>
  );
}
