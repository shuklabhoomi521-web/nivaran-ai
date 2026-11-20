import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import type { Api } from '../api';
import { CALL_LANGUAGES, nextSince } from '../format';
import { c, s } from '../theme';
import type { CallEvent, CallPreview } from '../types';
import { Button, Card, ErrorText } from '../ui';

const WHO: Record<string, string> = { ai: 'Nivaran (AI)', agent: 'Company', system: 'Info', info: 'Info' };

export default function CallScreen({ api, id, onBack }: { api: Api; id: string; onBack: () => void }) {
  const [lang, setLang] = useState('en-IN');
  const [pv, setPv] = useState<CallPreview | null>(null);
  const [agree, setAgree] = useState(false);
  const [callId, setCallId] = useState<string | null>(null);
  const [events, setEvents] = useState<CallEvent[]>([]);
  const [over, setOver] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const since = useRef(0);

  const load = useCallback(async () => {
    try { setPv(await api.callPreview(id, lang)); setErr(null); } catch (e) { setErr((e as Error).message); }
  }, [api, id, lang]);
  useEffect(() => { void load(); }, [load]);

  // live transcript: ask every 1.5 seconds while a call is on
  useEffect(() => {
    if (!callId || over) return;
    const timer = setInterval(async () => {
      try {
        const fresh = await api.callEvents(id, since.current);
        if (fresh.length) { since.current = nextSince(fresh, since.current); setEvents((old) => [...old, ...fresh]); }
      } catch { /* a missed poll is fine; the next one will catch up */ }
    }, 1500);
    return () => clearInterval(timer);
  }, [api, id, callId, over]);

  async function start() {
    setBusy(true); setErr(null);
    try { const r = await api.startCall(id, lang); since.current = 0; setEvents([]); setCallId(r.call_id); setOver(false); } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }

  async function hangUp() {
    if (!callId) return;
    try { await api.hangUp(id, callId); } catch (e) { setErr((e as Error).message); }
    setOver(true);
  }

  const live = !!callId && !over;
  return (
    <View style={s.screen}>
      <View style={s.header}><Button label="Back" kind="ghost" onPress={() => { if (live) void hangUp(); onBack(); }} /><Text style={s.title}>Call for me</Text></View>
      <ScrollView contentContainerStyle={s.body}>
        {!pv ? <>{err ? <ErrorText message={err} /> : <Text style={s.soft}>Loading…</Text>}</> : (
          <>
            <Card title={pv.mode === 'practice' ? 'Practice call' : 'Call to the company'}>
              {pv.mode === 'practice'
                ? <Text style={s.text}>Nivaran will ring <Text style={{ fontWeight: '700' }}>your own phone</Text> ({pv.will_ring ?? 'number not set'}). You play the company. No real company is called.</Text>
                : <Text style={s.text}>Nivaran will call the company's verified number: {pv.will_ring}.</Text>}
              {pv.company_number ? <Text style={s.soft}>{pv.company} customer care (from the official page, for your information): {pv.company_number}</Text> : null}
            </Card>

            {!live && !callId && (
              <View style={[s.row, { flexWrap: 'wrap' }]}>
                {CALL_LANGUAGES.map((l) => (
                  <Pressable key={l.code} accessibilityRole="button" accessibilityState={{ selected: lang === l.code }} onPress={() => setLang(l.code)}
                    style={{ paddingVertical: 6, opacity: lang === l.code ? 1 : 0.55 }}>
                    <Text style={[s.link, lang === l.code && { textDecorationLine: 'underline' }]}>{l.label}</Text>
                  </Pressable>
                ))}
              </View>
            )}

            <Card title="The first thing it says (fixed text, never written by the AI)">
              <Text style={s.text}>"{pv.disclosure}"</Text>
            </Card>
            <Card title="The only facts it may use">
              {pv.facts.map((f, i) => <Text key={i} style={s.text}>• {f}</Text>)}
            </Card>
            <Card title="Rules">
              {pv.rules.map((r, i) => <Text key={i} style={s.soft}>• {r}</Text>)}
            </Card>

            {pv.why_not ? <ErrorText message={pv.why_not} /> : null}
            <ErrorText message={err} />

            {!callId && (
              <>
                <Pressable accessibilityRole="checkbox" accessibilityState={{ checked: agree }} onPress={() => setAgree(!agree)}>
                  <Text style={s.text}>{agree ? '☑' : '☐'} I understand this call and I want Nivaran to make it.</Text>
                </Pressable>
                <Button label="Start the call" onPress={start} disabled={!agree || !pv.can_start} busy={busy} />
              </>
            )}

            {callId && (
              <Card title={live ? 'Call in progress' : 'Call finished'}>
                {events.length === 0 ? <Text style={s.soft}>{live ? 'Ringing… answer your phone and play the company.' : 'No transcript was captured.'}</Text> :
                  events.map((e) => <Text key={e.n} style={e.kind === 'ai' ? [s.text, { color: c.brand }] : s.text}>{(WHO[e.kind] ?? e.kind)}: {e.text}</Text>)}
                {live ? <Button label="Hang up now" onPress={hangUp} /> : (
                  <>
                    <Text style={s.soft}>{pv.mode === 'practice' ? 'This was only a practice. The case was not changed except for a note.' : 'Go back to the case and record what happened.'}</Text>
                    <Button label="Back to the case" onPress={onBack} />
                  </>
                )}
              </Card>
            )}
          </>
        )}
      </ScrollView>
    </View>
  );
}
