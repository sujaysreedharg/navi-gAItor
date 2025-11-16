import { useCallback, useRef, useState } from 'react';
import type { ChangeEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PaperPlaneIcon, ReloadIcon } from '@radix-ui/react-icons';

interface UploadPanelProps {
  disabled: boolean;
  status: 'idle' | 'uploading' | 'processing' | 'ready' | 'error';
  progress: number;
  error: string | null;
  onUpload: (file: File) => Promise<void> | void;
  onReset: () => void;
}

export function UploadPanel({ disabled, status, progress, error, onUpload, onReset }: UploadPanelProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFile = useCallback(
    (fileList: FileList | null) => {
      if (!fileList || !fileList[0]) return;
      const file = fileList[0];
      setSelectedFile(file);
      onUpload(file);
    },
    [onUpload]
  );

  const onInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    handleFile(event.target.files);
  };

  const openFileDialog = () => inputRef.current?.click();

  const busy = status === 'uploading' || status === 'processing';

  return (
    <div className="panel upload-panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Flight Log</p>
          <h2>Drop your CSV or tap to browse</h2>
        </div>
        {selectedFile && (
          <button className="ghost-btn" onClick={() => { setSelectedFile(null); onReset(); }}>
            <ReloadIcon /> Reset
          </button>
        )}
      </div>

      <div
        className={`dropzone ${busy ? 'dropzone-busy' : ''}`}
        onClick={openFileDialog}
      >
        <input ref={inputRef} type="file" accept=".csv" hidden onChange={onInputChange} disabled={disabled} />
        <AnimatePresence mode="wait">
          <motion.div
            key={status}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
          >
            {busy && (
              <div className="progress-track">
                <div className="progress-bar" style={{ width: `${progress}%` }} />
                <span>{progress}%</span>
              </div>
            )}
            {!busy && (
              <div className="dropzone-content">
                <PaperPlaneIcon />
                <p>
                  {selectedFile ? selectedFile.name : 'Supports Garmin G1000 + T-38C CSV exports'}
                </p>
                <small>Data never leaves your machine except for the backend run locally.</small>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {error && <p className="error-text">⚠️ {error}</p>}
    </div>
  );
}
