import React, { useState } from 'react';
import { Pressable, ScrollView, Text, TextInput, View } from 'react-native';
import type { Api } from '../api';
import { LANGS } from '../i18n';
import { GENDERS, ageOn, dobToInput, parseDob } from '../profileUtil';
import { c, s } from '../theme';
import type { Profile } from '../types';
import { Button, Card, ErrorText } from '../ui';

function Choice({ options, value, onPick }: { options: { code: string; label: string }[]; value: string; onPick: (v: string) => void }) {
  return (
    <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
      {options.map((o) => (
        <Pressable key={o.code} accessibilityRole="button" accessibilityState={{ selected: value === o.code }} onPress={() => onPick(o.code)}
          style={{ paddingVertical: 8, paddingHorizontal: 14, borderRadius: 999, borderWidth: 1, borderColor: value === o.code ? c.brand : 'rgba(0,0,0,0.18)', backgroundColor: value === o.code ? 'rgba(74,111,165,0.16)' : 'rgba(255,255,255,0.6)' }}>
          <Text style={{ color: value === o.code ? c.brand : c.ink, fontWeight: '600' }}>{o.label}</Text>
        </Pressable>
      ))}
    </View>
  );
}

export default function ProfileFormScreen({ api, initial, onSaved, onCancel }: { api: Api; initial: Profile | null; onSaved: (p: Profile) => void; onCancel?: () => void }) {
  const [name, setName] = useState(initial?.full_name ?? '');
  const [gender, setGender] = useState(initial?.gender ?? '');
  const [dob, setDob] = useState(initial ? dobToInput(initial.date_of_birth) : '');
  const [phone, setPhone] = useState(initial?.phone ?? '');
  const [email, setEmail] = useState(initial?.email ?? '');
  const [city, setCity] = useState(initial?.city ?? '');
  const [lang, setLang] = useState<string>(initial?.preferred_language ?? 'en');
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function save() {
    const iso = parseDob(dob);
    if (!name.trim()) return setErr('Please type your name.');
    if (!gender) return setErr('Please choose one option for gender.');
    if (!iso) return setErr('Type your date of birth as DD/MM/YYYY, for example 15/06/2000.');
    if (ageOn(iso, new Date()) < 18) return setErr('Nivaran is for people aged 18 or older.');
    setBusy(true); setErr(null);
    try {
      onSaved(await api.saveProfile({ full_name: name.trim(), gender, date_of_birth: iso, phone: phone.trim() || null, email: email.trim() || null, city: city.trim() || null, preferred_language: lang as Profile['preferred_language'] }));
    } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <View style={s.screen}>
      <View style={s.header}><Text style={s.title}>{initial ? 'Edit your details' : 'Tell us about you'}</Text></View>
      <ScrollView contentContainerStyle={s.body} keyboardShouldPersistTaps="handled">
        <Card>
          <Text style={s.soft}>These details stay encrypted on the server and are used only to sign the letters you approve and to greet you. You can delete them any time.</Text>
          <Text style={s.h2}>Full name *</Text>
          <TextInput accessibilityLabel="Full name" style={s.input} value={name} onChangeText={setName} placeholder="Your full name" />
          <Text style={s.h2}>Gender *</Text>
          <Choice options={GENDERS} value={gender} onPick={setGender} />
          <Text style={s.h2}>Date of birth *</Text>
          <TextInput accessibilityLabel="Date of birth" style={s.input} value={dob} onChangeText={setDob} placeholder="DD/MM/YYYY" keyboardType="numbers-and-punctuation" />
          <Text style={s.h2}>Mobile number (optional)</Text>
          <TextInput accessibilityLabel="Mobile number" style={s.input} value={phone} onChangeText={setPhone} placeholder="+91 98765 43210" keyboardType="phone-pad" />
          <Text style={s.h2}>Email (optional)</Text>
          <TextInput accessibilityLabel="Email" style={s.input} value={email} onChangeText={setEmail} placeholder="you@example.com" autoCapitalize="none" keyboardType="email-address" />
          <Text style={s.h2}>City (optional)</Text>
          <TextInput accessibilityLabel="City" style={s.input} value={city} onChangeText={setCity} placeholder="Chennai" />
          <Text style={s.h2}>Preferred language</Text>
          <Choice options={LANGS.map((l) => ({ code: l.code, label: l.label }))} value={lang} onPick={setLang} />
          <ErrorText message={err} />
          <Button label="Save and continue" onPress={save} busy={busy} />
          {onCancel ? <Button label="Cancel" kind="ghost" onPress={onCancel} /> : null}
        </Card>
      </ScrollView>
    </View>
  );
}
