/** Remembers the person's access code on the phone. `Storage` is anything with get, set and remove, so tests can use a fake one. */
export interface KeyValue {
  get(key: string): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
  remove(key: string): Promise<void>;
}

const KEY = 'nivaran_access_code';
const SERVER_KEY = 'nivaran_server_url';

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
      await store.remove(KEY).catch(() => undefined);      // the server address is kept on purpose
    },
    async loadServer(): Promise<string | null> {
      const v = await store.get(SERVER_KEY).catch(() => null);
      return v && v.trim() ? v.trim() : null;
    },
    async saveServer(url: string): Promise<void> {
      await store.set(SERVER_KEY, url.trim());
    },
  };
}

/** Cleans what a person pastes: spaces, line breaks, a leading "Bearer ". */
export function cleanCode(raw: string): string {
  return raw.replace(/\s+/g, '').replace(/^bearer/i, '');
}

/** Cleans a server address typed on the phone: "192.168.1.20:8000" -> "http://192.168.1.20:8000". Returns null if it cannot be an address. */
export function cleanServer(raw: string): string | null {
  let v = raw.trim().replace(/\s+/g, '');
  if (!v) return null;
  if (!/^https?:\/\//i.test(v)) v = `http://${v}`;
  v = v.replace(/\/+$/, '');
  return /^https?:\/\/[A-Za-z0-9.-]+(:\d{2,5})?$/.test(v) ? v : null;
}

/** True for the placeholder baked into a build that was made without a real address. */
export function isPlaceholderServer(url: string): boolean {
  return /CHANGE-ME/i.test(url);
}
