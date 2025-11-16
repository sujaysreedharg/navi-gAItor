import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

interface DebriefPanelProps {
  text: string;
}

export function DebriefPanel({ text }: DebriefPanelProps) {
  return (
    <div className="panel grow debrief-panel-container">
      <div className="panel-header">
        <div>
          <p className="eyebrow">CFI Debrief</p>
          <h2>✈️ Gemini Analysis</h2>
        </div>
      </div>
      <motion.div
        className="debrief-markdown"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <ReactMarkdown>{text}</ReactMarkdown>
      </motion.div>
    </div>
  );
}

