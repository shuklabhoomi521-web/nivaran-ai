import { ApiError, makeApi } from '../src/api';

function fakeFetch(status: number, body: unknown, capture?: { url?: string; init?: RequestInit }): typeof fetch {
  return (async (url: string, init?: RequestInit) => {
    if (capture) { capture.url = url; capture.init = init; }
    return { ok: status >= 200 && status < 300, status, json: async () => body } as Response;
  }) as unknown as typeof fetch;
}

describe('api client', () => {
  it('sends JSON to the right address and trims the trailing slash', async () => {
    const cap: { url?: string; init?: RequestInit } = {};
    const api = makeApi('http://192.168.1.20:8000/', fakeFetch(200, { id: 'c1' }, cap));
    await api.createCase({ company: 'Swiggy' } as never, 'Bhoomi');
    expect(cap.url).toBe('http://192.168.1.20:8000/tracked-cases');
    expect(cap.init?.method).toBe('POST');
    expect(JSON.parse(String(cap.init?.body))).toEqual({ case: { company: 'Swiggy' }, user_name: 'Bhoomi' });
  });

  it('GET calls send no body', async () => {
    const cap: { url?: string; init?: RequestInit } = {};
    await makeApi('http://x', fakeFetch(200, [], cap)).listCases();
    expect(cap.init?.body).toBeUndefined();
  });

  it('turns a server error into a readable message', async () => {
    await expect(makeApi('http://x', fakeFetch(409, { detail: 'the user has not approved this draft' })).sendDraft('d1')).rejects.toMatchObject({
      message: 'the user has not approved this draft', status: 409,
    });
  });

  it('reads validation errors that come as a list', async () => {
    const api = makeApi('http://x', fakeFetch(422, { detail: [{ msg: 'field required' }, { msg: 'bad value' }] }));
    await expect(api.understand('')).rejects.toThrow('field required; bad value');
  });

  it('explains a network failure in plain words', async () => {
    const failing = (async () => { throw new TypeError('Network request failed'); }) as unknown as typeof fetch;
    const err = await makeApi('http://10.0.0.5:8000', failing).listCases().catch((e) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect(err.message).toContain('Cannot reach the Nivaran server at http://10.0.0.5:8000');
    expect(err.message).toContain('same Wi-Fi');
  });

  it('falls back to a generic message when the error body is not JSON', async () => {
    const f = (async () => ({ ok: false, status: 500, json: async () => { throw new Error('no json'); } })) as unknown as typeof fetch;
    await expect(makeApi('http://x', f).listCases()).rejects.toThrow('The server answered with an error (500).');
  });
});

describe('api client, more calls', () => {
  it('records a step the user did by hand with its rung', async () => {
    const cap: { url?: string; init?: RequestInit } = {};
    await makeApi('http://x', fakeFetch(200, {}, cap)).markContacted('c1', '2026-12-05', 'regulator', 'portal', 'done by the user');
    expect(cap.url).toBe('http://x/tracked-cases/c1/events');
    expect(JSON.parse(String(cap.init?.body))).toEqual({ on: '2026-12-05', kind: 'contacted', rung: 'regulator', channel: 'portal', text: 'done by the user' });
  });
  it('sends a draft only through its own address', async () => {
    const cap: { url?: string; init?: RequestInit } = {};
    await makeApi('http://x', fakeFetch(200, {}, cap)).sendDraft('d9');
    expect(cap.url).toBe('http://x/drafts/d9/send');
    expect(cap.init?.method).toBe('POST');
  });
  it('deletes a case with DELETE', async () => {
    const cap: { url?: string; init?: RequestInit } = {};
    await makeApi('http://x', fakeFetch(200, { deleted: 'c1' }, cap)).deleteCase('c1');
    expect(cap.init?.method).toBe('DELETE');
  });
});
