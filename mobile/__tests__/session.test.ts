import { cleanCode, makeSession, type KeyValue } from '../src/session';

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
