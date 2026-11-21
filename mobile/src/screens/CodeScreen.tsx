import React, { useState } from 'react';
import { ScrollView, Text, TextInput, View } from 'react-native';
import { makeApi } from '../api';
import { cleanCode } from '../session';
import { Logo } from '../logo';
import { s } from '../theme';
import { Button, Card, ErrorText } from '../ui';

export default function CodeScreen({ baseUrl, onAccepted }: { baseUrl: string; onAccepted: (code: string) => void }) {
  const [code, setCode] = useState('');
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function check() {
    const clean = cleanCode(code);
    setBusy(true); setErr(null);
    try {
      await makeApi(baseUrl, fetch, 25000, clean).listCases();      // a wrong code answers 401
      onAccepted(clean);
    } catch (e) {
      const m = (e as Error & { status?: number }).status === 401 ? 'That code is not right. Check it with the person who gave it to you.' : (e as Error).message;
      setErr(m);
    } finally { setBusy(false); }
  }

  return (
    <View style={s.screen}>
      <View style={{ alignItems: 'center', paddingTop: 8 }}><Logo size={84} caption="Customer care, made easy" /></View>
      <ScrollView contentContainerStyle={s.body} keyboardShouldPersistTaps="handled">
        <Card title="Sign in">
          <Text style={s.text}>Type the code you were given for this pilot. It keeps your cases private: nobody else can see them with their own code.</Text>
          <TextInput accessibilityLabel="Access code" style={s.input} value={code} onChangeText={setCode} secureTextEntry autoCapitalize="none" autoCorrect={false} placeholder="Access code" />
          <ErrorText message={err} />
          <Button label="Continue" onPress={check} disabled={cleanCode(code).length < 8} busy={busy} />
        </Card>
        <Text style={s.soft}>Do not share your code. If you lose it or think someone else has it, ask for it to be revoked and get a new one.</Text>
      </ScrollView>
    </View>
  );
}
