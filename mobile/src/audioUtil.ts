/** "data:audio/webm;codecs=opus;base64,AAAA" -> { mime: "audio/webm", b64: "AAAA" } */
export function parseDataUrl(dataUrl: string): { mime: string; b64: string } | null {
  const m = /^data:([^;,]*)(?:;[^,]*)*;base64,(.*)$/s.exec(dataUrl);
  if (!m || !m[2]) return null;
  return { mime: m[1] || '', b64: m[2] };
}

/** The type to send when the platform does not tell us one. */
export function fallbackMime(os: string): string {
  return os === 'web' ? 'audio/webm' : 'audio/mp4';
}
