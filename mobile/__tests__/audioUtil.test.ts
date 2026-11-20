import { fallbackMime, parseDataUrl } from '../src/audioUtil';

describe('recording helpers', () => {
  it('splits a data URL into type and base64', () => {
    expect(parseDataUrl('data:audio/webm;codecs=opus;base64,AAAA')).toEqual({ mime: 'audio/webm', b64: 'AAAA' });
    expect(parseDataUrl('data:audio/mp4;base64,QUJD')).toEqual({ mime: 'audio/mp4', b64: 'QUJD' });
    expect(parseDataUrl('data:;base64,QUJD')).toEqual({ mime: '', b64: 'QUJD' });
  });
  it('rejects empty or broken data URLs', () => {
    expect(parseDataUrl('data:audio/mp4;base64,')).toBeNull();
    expect(parseDataUrl('not a data url')).toBeNull();
  });
  it('picks a sensible type when the platform gives none', () => {
    expect(fallbackMime('web')).toBe('audio/webm');
    expect(fallbackMime('ios')).toBe('audio/mp4');
    expect(fallbackMime('android')).toBe('audio/mp4');
  });
});
