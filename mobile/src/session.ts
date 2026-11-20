/** Remembers the person's access code on the phone. `Storage` is anything with get, set and remove, so tests can use a fake one. */
export interface KeyValue {
  get(key: string): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
  remove(key: string): Promise<void>;
}

const KEY = 'nivaran_access_code';

export function makeSession(store: KeyValue) {
  return {
    async load(): Promise<string | null> {
      const v = await store.get(KEY).catch(() => null);
      return v && v.trim() ? v.trim() : null;
    },
    async save(code: string): Promise<void> {
      await store.set(KEY, code.trim());
    },
    async clear(): Promise<void> {
      await store.remove(KEY).catch(() => undefined);
    },
  };
}

/** Cleans what a person pastes: spaces, line breaks, a leading "Bearer ". */
export function cleanCode(raw: string): string {
  return raw.replace(/\s+/g, '').replace(/^bearer/i, '');
}
