import { cleanCode, cleanServer, isPlaceholderServer, makeSession, type KeyValue } from '../src/session';

function fake(initial: Record<string, string> = {}): KeyValue & { data: Record<string, string> } {
  const data = { ...initial };
  return { data, get: async (k) => data[k] ?? null, set: async (k, v) => { data[k] = v; }, remove: async (k) => { delete data[k]; } };
}

describe('access code on the phone', () => {
  it('saves, loads and clears the code', async () => {
    const store = fake();
    const s = makeSession(store);
    expect(await s.load()).toBeNull();
    await s.save('  abc123XYZ  ');
    expect(await s.load()).toBe('abc123XYZ');
    await s.clear();
    expect(await s.load()).toBeNull();
    expect(Object.keys(store.data)).toEqual([]);
  });
  it('treats an empty or broken store as no code', async () => {
    expect(await makeSession(fake({ nivaran_access_code: '   ' })).load()).toBeNull();
    const broken: KeyValue = { get: async () => { throw new Error('keychain locked'); }, set: async () => undefined, remove: async () => { throw new Error('x'); } };
    expect(await makeSession(broken).load()).toBeNull();
    await expect(makeSession(broken).clear()).resolves.toBeUndefined();
  });
  it('cleans a pasted code', () => {
    expect(cleanCode(' abc 123\nXYZ ')).toBe('abc123XYZ');
    expect(cleanCode('Bearer abc123')).toBe('abc123');
  });
});

describe('server address on the phone', () => {
  it('cleans what a person types', () => {
    expect(cleanServer('192.168.1.20:8000')).toBe('http://192.168.1.20:8000');
    expect(cleanServer(' http://10.3.147.45:8000/ ')).toBe('http://10.3.147.45:8000');
    expect(cleanServer('https://nivaran.example.com')).toBe('https://nivaran.example.com');
    expect(cleanServer('')).toBeNull();
    expect(cleanServer('not an address!')).toBeNull();
    expect(cleanServer('http://a b')).toBe('http://ab');
  });
  it('remembers the address and keeps it when the code is cleared', async () => {
    const s = makeSession(fake());
    expect(await s.loadServer()).toBeNull();
    await s.saveServer(' http://10.0.0.5:8000 ');
    await s.save('code12345');
    await s.clear();
    expect(await s.load()).toBeNull();
    expect(await s.loadServer()).toBe('http://10.0.0.5:8000');
  });
  it('spots the build placeholder', () => {
    expect(isPlaceholderServer('http://CHANGE-ME-LAPTOP-IP:8000')).toBe(true);
    expect(isPlaceholderServer('http://10.0.0.5:8000')).toBe(false);
  });
});
