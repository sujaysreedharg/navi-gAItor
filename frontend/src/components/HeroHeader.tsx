import { motion } from 'framer-motion';

export function HeroHeader() {
  return (
    <div className="hero-wrapper">
      <motion.div
        className="hero-glow"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 0.9, scale: 1 }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
      />
      <motion.div
        className="hero-content"
        initial={{ y: 40, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      >
        <p className="hero-tag">navi-gAItor</p>
        <h1>Flight Data Intelligence at Your Fingertips</h1>
        <p className="hero-subtitle">
          Real-time telemetry analysis meets AI-powered debriefs. Powered by Gemini for 
          intelligent insights and You.com for FAA regulatory context.
        </p>
      </motion.div>
    </div>
  );
}
