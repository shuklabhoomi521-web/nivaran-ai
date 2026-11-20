import { AudioModule, RecordingPresets, requestRecordingPermissionsAsync, setAudioModeAsync, useAudioRecorder } from 'expo-audio';
import { useRef, useState } from 'react';
import { Platform } from 'react-native';
import { fallbackMime, parseDataUrl } from './audioUtil';

async function readAsBase64(uri: string): Promise<{ mime: string; b64: string }> {
  const blob = await (await fetch(uri)).blob();
  const dataUrl: string = await new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onloadend = () => resolve(String(r.result));
    r.onerror = () => reject(new Error('Could not read the recording.'));
    r.readAsDataURL(blob);
  });
  const parsed = parseDataUrl(dataUrl);
  if (!parsed) throw new Error('The recording was empty.');
  return { mime: parsed.mime && parsed.mime !== 'application/octet-stream' ? parsed.mime : fallbackMime(Platform.OS), b64: parsed.b64 };
}

export type RecState = 'idle' | 'recording';
export const MAX_SECONDS = 60;

/** A tap-to-start, tap-to-stop recorder. `stop()` resolves with the audio as base64 and its type. The recording is never kept by the app. */
export function useVoiceRecorder() {
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const [state, setState] = useState<RecState>('idle');
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const auto = useRef<((r: { mime: string; b64: string }) => void) | null>(null);

  async function finish(): Promise<{ mime: string; b64: string }> {
    if (timer.current) clearTimeout(timer.current);
    await recorder.stop();
    setState('idle');
    if (!recorder.uri) throw new Error('Nothing was recorded.');
    return readAsBase64(recorder.uri);
  }

  return {
    state,
    async start(onAutoStop: (r: { mime: string; b64: string }) => void) {
      const perm = await requestRecordingPermissionsAsync();
      if (!perm.granted) throw new Error('Microphone permission was not given. You can type your problem instead.');
      await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
      await recorder.prepareToRecordAsync();
      recorder.record();
      setState('recording');
      auto.current = onAutoStop;
      timer.current = setTimeout(() => { void finish().then((r) => auto.current?.(r)).catch(() => undefined); }, MAX_SECONDS * 1000);
    },
    stop: finish,
    ready: AudioModule != null,
  };
}
