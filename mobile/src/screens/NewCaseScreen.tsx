import React, { useEffect, useState } from 'react';
import { Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import type { Api } from '../api';
import { GOAL_LABEL, categoryLabel } from '../format';
import { s } from '../theme';
import type { UnderstandResponse } from '../types';
import { useVoiceRecorder } from '../voice';
import { Button, Card, ErrorText } from '../ui';

export default function NewCaseScreen({ api, onBack, onCreated }: { api: Api; onBack: () => void; onCreated: (id: string) => void }) {
  const [text, setText] = useState('');
  const [name, setName] = useState('');
  const [company, setCompany] = useState('');
  const [result, setResult] = useState<UnderstandResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [agree, setAgree] = useState(false);
  const [adult, setAdult] = useState(false);
  const rec = useVoiceRecorder();
  const [heard, setHeard] = useState<string | null>(null);

  useEffect(() => { api.consentNotice().then((n) => setNotice(n.text)).catch((e) => setErr((e as Error).message)); }, [api]);

  async function understand() {
    setBusy(true); setErr(null);
    try {
      const r = await api.understand(text.trim());
      setResult(r);
      setCompany(r.case.company ?? '');
    } catch (e) {
      setErr((e as Error).message);
    } finally { setBusy(false); }
  }

  async function transcribe(r: { mime: string; b64: string }) {
    setBusy(true); setErr(null);
    try {
      const t = await api.transcribe(r.b64, r.mime);
      setText((old) => (old.trim() ? `${old.trim()} ${t.text}` : t.text));
      setHeard(t.redacted.length ? `We removed payment details we heard (${t.redacted.join(', ')}).` : 'Check the text below and fix any word we heard wrong.');
    } catch (e) {
      setErr((e as Error).message);
    } finally { setBusy(false); }
  }

  async function toggleMic() {
    setErr(null);
    try {
      if (rec.state === 'idle') await rec.start((r) => void transcribe(r));
      else await transcribe(await rec.stop());
    } catch (e) { setErr((e as Error).message); }
  }

  async function create() {
    if (!result) return;
    setBusy(true); setErr(null);
    try {
      const t = await api.createCase({ ...result.case, company: company.trim() || null }, name.trim() || null, agree, adult);
      onCreated(t.id);
    } catch (e) {
      setErr((e as Error).message);
    } finally { setBusy(false); }
  }

  return (
    <View style={s.screen}>
      <View style={s.header}>
        <Button label="Back" kind="ghost" onPress={onBack} />
        <Text style={s.title}>New case</Text>
      </View>
      <ScrollView contentContainerStyle={s.body} keyboardShouldPersistTaps="handled">
        {!result ? (
          <>
            <Text style={s.text}>Tell us the problem once, in your own words and your own language.</Text>
            <TextInput accessibilityLabel="Describe your problem" style={[s.input, s.area]} multiline value={text} onChangeText={setText}
              placeholder="For example: my Swiggy order 4839201 arrived cold and I got no refund" />
            <Button label={rec.state === 'recording' ? 'Stop and write it down' : 'Speak instead of typing'} kind="ghost" onPress={toggleMic} busy={busy} />
            {rec.state === 'recording' ? <Text style={s.soft}>Listening… speak for up to a minute, then tap again.</Text> : null}
            {heard ? <Text style={s.soft}>{heard}</Text> : null}
            <Text style={s.soft}>Do not type or say a card number, PIN, CVV or OTP. We remove them, and Nivaran never needs them.</Text>
            <ErrorText message={err} />
            <Button label="Understand my problem" onPress={understand} disabled={text.trim().length < 5} busy={busy} />
          </>
        ) : (
          <>
            {result.redacted.length > 0 && <Text style={s.soft}>Private data was removed before the AI read your text ({result.redacted.join(', ')}).</Text>}
            <Card title="Is this right?">
              <Text style={s.text}>{result.case.problem_summary}</Text>
              <Text style={s.soft}>Category: {categoryLabel(result.case.category)} · You want: {GOAL_LABEL[result.case.user_goal] ?? result.case.user_goal}</Text>
              {result.case.details_known.map((f) => <Text key={f.name} style={s.text}>• {f.name.replace(/_/g, ' ')}: {f.value}</Text>)}
              {result.case.details_missing.length > 0 && <Text style={s.soft}>Still missing: {result.case.details_missing.join(', ')}</Text>}
              {result.follow_up_question ? <Text style={s.text}>{result.follow_up_question}</Text> : null}
            </Card>
            <Text style={s.soft}>Company (we only write to companies in our verified list):</Text>
            <TextInput accessibilityLabel="Company name" style={s.input} value={company} onChangeText={setCompany} placeholder="Company name" />
            <Text style={s.soft}>Your name, used only to sign letters you approve:</Text>
            <TextInput accessibilityLabel="Your name" style={s.input} value={name} onChangeText={setName} placeholder="Your name" />
            <Card title="Privacy">
              <Text style={s.soft}>{notice ?? 'Loading the privacy notice…'}</Text>
              <Pressable accessibilityRole="checkbox" accessibilityState={{ checked: agree }} onPress={() => setAgree(!agree)}>
                <Text style={s.text}>{agree ? '☑' : '☐'} I have read this and agree.</Text>
              </Pressable>
              <Pressable accessibilityRole="checkbox" accessibilityState={{ checked: adult }} onPress={() => setAdult(!adult)}>
                <Text style={s.text}>{adult ? '☑' : '☐'} I am 18 years old or older.</Text>
              </Pressable>
            </Card>
            <ErrorText message={err} />
            <Button label="Create case" onPress={create} disabled={!company.trim() || !agree || !adult || !notice} busy={busy} />
            <Button label="Change my text" kind="ghost" onPress={() => setResult(null)} />
          </>
        )}
      </ScrollView>
    </View>
  );
}
