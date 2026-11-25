import React, { useState } from 'react';
import { ScrollView, Text, TextInput, View } from 'react-native';
import { makeApi } from '../api';
import { Platform } from 'react-native';
import { cleanCode, cleanServer, isPlaceholderServer } from '../session';
import { Logo } from '../logo';
import { s } from '../theme';
import { Button, Card, ErrorText } from '../ui';

export default function CodeScreen({ baseUrl, onAccepted }: { baseUrl: string; onAccepted: (code: string, server: string) => void }) {
  const askServer = Platform.OS !== 'web';       // on a phone the person types where the server is; the web page already knows
  const [server, setServer] = useState(isPlaceholderServer(baseUrl) ? '' : baseUrl);
  const [code, setCode] = useState('');
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function check() {
    const clean = cleanCode(code);
    const where = askServer ? cleanServer(server) : baseUrl;
    if (where === null) { setErr('Type the server address from the laptop, for example 192.168.1.20:8000'); return; }
    setBusy(true); setErr(null);
    try {
      await makeApi(where, fetch, 25000, clean).listCases();      // a wrong code answers 401
      onAccepted(clean, where);
    } catch (e) {
      const m = (e as Error & { status?: number }).status === 401 ? 'That code is not right. Check it with the person who gave it to you.' : (e as Error).message;
      setErr(m);
    } finally { setBusy(false); }
  }

  return (
    <View style={s.screen}>
      <View style={{ alignItems: 'center', paddingTop: 8 }}><Logo size={84} caption="Customer care, resolved" /></View>
      <ScrollView contentContainerStyle={s.body} keyboardShouldPersistTaps="handled">
        <Card title="Sign in">
          <Text style={s.text}>Type the code you were given for this pilot. It keeps your cases private: nobody else can see them with their own code.</Text>
          {askServer ? <>
            <Text style={s.soft}>Server address (the laptop running Nivaran; it prints this address when it starts)</Text>
            <TextInput accessibilityLabel="Server address" style={s.input} value={server} onChangeText={setServer} autoCapitalize="none" autoCorrect={false} keyboardType="url" placeholder="192.168.1.20:8000" />
          </> : null}
          <TextInput accessibilityLabel="Access code" style={s.input} value={code} onChangeText={setCode} secureTextEntry autoCapitalize="none" autoCorrect={false} placeholder="Access code" />
          <ErrorText message={err} />
          <Button label="Continue" onPress={check} disabled={cleanCode(code).length < 8 || (askServer && !server.trim())} busy={busy} />
        </Card>
        <Text style={s.soft}>Do not share your code. If you lose it or think someone else has it, ask for it to be revoked and get a new one.</Text>
      </ScrollView>
    </View>
  );
}
