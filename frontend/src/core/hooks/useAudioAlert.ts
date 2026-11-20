import { useCallback } from 'react';

export function useAudioAlert() {
  return useCallback(() => {
    try {
      const AudioContextConstructor = window.AudioContext;
      const context = new AudioContextConstructor();
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = 'sine';
      oscillator.frequency.value = 740;
      gain.gain.setValueAtTime(0.001, context.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.12, context.currentTime + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.34);
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.start();
      oscillator.stop(context.currentTime + 0.36);
      oscillator.onended = () => void context.close();
    } catch {
      // Audio is an optional operator alert and may be blocked until the first user gesture.
    }
  }, []);
}
