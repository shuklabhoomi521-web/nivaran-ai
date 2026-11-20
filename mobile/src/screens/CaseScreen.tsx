import * as Clipboard from 'expo-clipboard';
import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Linking, ScrollView, Text, TextInput, View } from 'react-native';
import type { Api } from '../api';
import { RUNG_LABEL, STATE_COLOR, STATE_LABEL, actionHeadline, addDays, categoryLabel, prettyDate, reminderLabel, todayIso } from '../format';
import { c, s } from '../theme';
import type { Draft, Match, NextResponse, PortalKit, TrackedCase } from '../types';
import { Button, Card, Chip, ErrorText } from '../ui';

export default function CaseScreen({ api, id, onBack, onCall }: { api: Api; id: string; onBack: () => void; onCall: () => void }) {
  const [tc, setTc] = useState<TrackedCase | null>(null);
  const [next, setNext] = useState<NextResponse | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [kit, setKit] = useState<PortalKit | null>(null);
  const [replies, setReplies] = useState<Match[] | null>(null);
  const [docket, setDocket] = useState('');
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [t, n] = await Promise.all([api.getCase(id), api.nextStep(id)]);
      setTc(t); setNext(n); setErr(null);
    } catch (e) { setErr((e as Error).message); }
  }, [api, id]);
  useEffect(() => { void load(); }, [load]);

  async function run<T>(label: string, fn: () => Promise<T>, after?: (r: T) => void) {
    setBusy(label); setErr(null);
    try { const r = await fn(); after?.(r); } catch (e) { setErr((e as Error).message); } finally { setBusy(null); }
  }

  const confirm = (title: string, message: string, ok: string, go: () => void) =>
    Alert.alert(title, message, [{ text: 'Cancel', style: 'cancel' }, { text: ok, style: 'destructive', onPress: go }]);

  if (!tc) {
    return (
      <View style={s.screen}>
        <View style={s.header}><Button label="Back" kind="ghost" onPress={onBack} /><Text style={s.title}>Case</Text></View>
        <View style={s.body}>{err ? <ErrorText message={err} /> : <Text style={s.soft}>Loading…</Text>}</View>
      </View>
    );
  }
  const open = tc.state !== 'resolved' && tc.state !== 'closed';
  const action = next?.action ?? null;

  return (
    <View style={s.screen}>
      <View style={s.header}><Button label="Back" kind="ghost" onPress={onBack} /><Text style={s.title}>{tc.company}</Text></View>
      <ScrollView contentContainerStyle={s.body} keyboardShouldPersistTaps="handled">
        <Card>
          <Chip text={STATE_LABEL[tc.state]} color={STATE_COLOR[tc.state]} />
          <Text style={s.text}>{tc.problem_summary}</Text>
          <Text style={s.soft}>{categoryLabel(tc.category)} · started {prettyDate(tc.created_on)}</Text>
          {tc.facts.map((f) => <Text key={f.name} style={s.text}>• {f.name.replace(/_/g, ' ')}: {f.value}</Text>)}
        </Card>
        {tc.purge_notice_on ? (
          <Card title="This case will be deleted">
            <Text style={s.text}>It has had no activity for a year. It will be deleted on {prettyDate(addDays(tc.purge_notice_on, 2))} unless you do something on it, such as adding a note.</Text>
          </Card>
        ) : null}
        <ErrorText message={err} />

        {next && (
          <Card title="Steps">
            {next.reminders.map((r) => <Text key={r.rung} style={[s.text, r.status === 'done' && { color: c.good }, r.status === 'due' && { color: c.warn, fontWeight: '700' }]}>{reminderLabel(r)}</Text>)}
          </Card>
        )}

        {open && action && (
          <Card title={`Next: ${actionHeadline(action)}`}>
            <Text style={s.text}>{action.reason}</Text>
            {action.note ? <Text style={s.soft}>{action.note}</Text> : null}
            {action.fell_back_from ? <Text style={s.soft}>No verified contact for "{RUNG_LABEL[action.fell_back_from]}", so this goes one step higher.</Text> : null}
            {action.target_value ? (
              <>
                <Text style={s.text}>{action.target_label}: {action.target_value}</Text>
                {action.source_quote ? <Text style={s.soft}>From the official page {action.source_url}: "{action.source_quote}"</Text> : null}
              </>
            ) : <Text style={s.soft}>No verified contact is listed for this step. Check the company's official page yourself.</Text>}

            {action.channel === 'email' && action.target_value && (
              <Button label="Write the letter" busy={busy === 'draft'} onPress={() => run('draft', () => api.makeDraft(id), setDraft)} />
            )}
            {action.channel === 'call' && (
              <Button label="Call for me (practice)" busy={false} onPress={onCall} />
            )}
            {action.channel === 'call' && action.target_value && (
              <Button label={`Call ${action.target_value} myself`} kind="ghost" onPress={() => void Linking.openURL(`tel:${action.target_value!.replace(/[^+\d]/g, '')}`)} />
            )}
            {action.channel === 'portal' && (
              <Button label="Open the filing kit" busy={busy === 'kit'} onPress={() => run('kit', () => api.portalKit(id), setKit)} />
            )}
            {action.channel !== 'email' && (
              <Button label="I did this step myself" kind="ghost" busy={busy === 'did'}
                onPress={() => run('did', () => api.markContacted(id, todayIso(), action.rung, action.channel, 'done by the user'), () => { setKit(null); void load(); })} />
            )}
          </Card>
        )}

        {draft && (
          <Card title="Your letter (nothing is sent until you approve and send)">
            <Text style={s.soft}>To: {draft.to} · {draft.status}</Text>
            <TextInput accessibilityLabel="Subject" style={s.input} value={draft.subject} editable={draft.status === 'pending'} onChangeText={(v) => setDraft({ ...draft, subject: v })} />
            <TextInput accessibilityLabel="Letter text" style={[s.input, s.area, { minHeight: 220 }]} multiline value={draft.body} editable={draft.status === 'pending'} onChangeText={(v) => setDraft({ ...draft, body: v })} />
            {draft.status === 'pending' && (
              <View style={s.row}>
                <View style={{ flex: 1 }}><Button label="Save my edits" kind="ghost" busy={busy === 'save'} onPress={() => run('save', () => api.editDraft(draft.id, draft.subject, draft.body), setDraft)} /></View>
                <View style={{ flex: 1 }}><Button label="Approve" busy={busy === 'approve'} onPress={() => run('approve', async () => { await api.editDraft(draft.id, draft.subject, draft.body); return api.approveDraft(draft.id); }, setDraft)} /></View>
              </View>
            )}
            {draft.status === 'approved' && (
              <Button label="Send this email" busy={busy === 'send'} onPress={() => confirm('Send this email?', `To: ${draft.to}\nSubject: ${draft.subject}\n\nIt will be sent from your email account.`, 'Send',
                () => run('send', () => api.sendDraft(draft.id), (r) => { setDraft(null); setTc(r.case); void load(); }))} />
            )}
            {(draft.status === 'pending' || draft.status === 'approved') && <Button label="Discard this letter" kind="ghost" onPress={() => run('reject', () => api.rejectDraft(draft.id), () => setDraft(null))} />}
          </Card>
        )}

        {kit && (
          <Card title={`File on: ${kit.regulator}`}>
            <Text style={s.text}>{kit.purpose}</Text>
            {kit.helpline ? <Text style={s.text}>Helpline: {kit.helpline}</Text> : null}
            <Button label="Open the official portal" kind="ghost" onPress={() => void Linking.openURL(kit.portal_url)} />
            {kit.steps.length > 0 && <Text style={s.h2}>Official steps</Text>}
            {kit.steps.map((st, i) => (
              <View key={i}><Text style={s.text}>{i + 1}. {st.text}</Text>{st.source ? <Text style={s.soft}>Official page says: "{st.source.quote}"</Text> : null}</View>
            ))}
            {kit.official_attach.map((st, i) => <Text key={`a${i}`} style={s.text}>• {st.text}</Text>)}
            <Text style={s.h2}>Our checklist (our advice, not an official rule)</Text>
            {kit.checklist.map((x, i) => <Text key={`c${i}`} style={s.text}>• {x}</Text>)}
            <Text style={s.h2}>Complaint text to paste</Text>
            <Text selectable style={[s.text, s.input]}>{kit.complaint_text}</Text>
            <Button label="Copy the complaint text" kind="ghost" onPress={() => { void Clipboard.setStringAsync(kit.complaint_text); Alert.alert('Copied', 'Paste it on the portal.'); }} />
            {kit.needs_check.length > 0 && <Text style={s.soft}>Not verified, check yourself: {kit.needs_check.join(' · ')}</Text>}
            {kit.warnings.map((w, i) => <Text key={`w${i}`} style={s.soft}>{w}</Text>)}
            <Text style={s.h2}>After you file</Text>
            <TextInput accessibilityLabel="Docket number" style={s.input} value={docket} onChangeText={setDocket} placeholder="Docket or complaint number" autoCapitalize="characters" />
            <Button label="Save the docket number" disabled={!docket.trim()} busy={busy === 'docket'}
              onPress={() => run('docket', () => api.markContacted(id, todayIso(), 'regulator', 'portal', `filed on ${kit.regulator}, docket ${docket.trim()}`).then(() => api.addNote(id, todayIso(), `docket ${docket.trim()}`, docket.trim())), () => { setDocket(''); setKit(null); void load(); })} />
          </Card>
        )}

        {replies && (
          <Card title={replies.length ? `${replies.length} new repl${replies.length === 1 ? 'y' : 'ies'}` : 'No new replies'}>
            {replies.map((m, i) => (
              <View key={i}>
                <Text style={s.text}>{m.message.subject}</Text>
                <Text style={s.soft}>{m.auto_acknowledgement ? 'Automatic acknowledgement' : 'Reply'} from {m.message.from_addr}{m.docket ? ` · reference ${m.docket}` : ''}{m.looks_resolved ? ' · looks like a solution: you decide whether it is solved' : ''}</Text>
              </View>
            ))}
          </Card>
        )}

        <Card title="Timeline">
          {tc.events.length === 0 ? <Text style={s.soft}>Nothing has happened yet.</Text> : tc.events.map((e, i) => (
            <Text key={i} style={s.soft}>{prettyDate(e.on)} · {e.kind.replace('_', ' ')}{e.rung ? ` (${RUNG_LABEL[e.rung]})` : ''}{e.text ? ` · ${e.text}` : ''}</Text>
          ))}
        </Card>

        <Button label="Check my inbox for replies" kind="ghost" busy={busy === 'replies'} onPress={() => run('replies', () => api.checkReplies(id), (r) => { setReplies(r.new_replies); setTc(r.case); void load(); })} />
        {open && (
          <>
            <Button label="It is solved" kind="ghost" onPress={() => confirm('Mark as solved?', 'We stop the reminders for this case.', 'Yes, solved', () => run('fin', () => api.finish(id, todayIso(), 'resolved'), () => void load()))} />
            <Button label="Stop this case" kind="ghost" onPress={() => confirm('Stop this case?', 'It will be closed without a solution.', 'Stop it', () => run('fin', () => api.finish(id, todayIso(), 'closed'), () => void load()))} />
          </>
        )}
        <Button label="Delete my data for this case" kind="ghost" onPress={() => confirm('Delete this case?', 'This removes the case and cannot be undone.', 'Delete', () => run('del', () => api.deleteCase(id), onBack))} />
      </ScrollView>
    </View>
  );
}
