import React, { useEffect, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import type { Api } from '../api';
import { isOngoing } from '../profileUtil';
import { s } from '../theme';
import type { TrackedCase } from '../types';
import { Button, Card, ErrorText } from '../ui';

export default function CallHomeScreen({ api, onChat, onPractice }: { api: Api; onChat: () => void; onPractice: (id: string) => void }) {
  const [cases, setCases] = useState<TrackedCase[]>([]);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => { api.listCases().then(setCases).catch((e) => setErr((e as Error).message)); }, [api]);
  const open = cases.filter((x) => isOngoing(x.state));
  return (
    <View style={s.screen}>
      <View style={s.header}><Text style={s.title}>Tell our AI on a call</Text></View>
      <ScrollView contentContainerStyle={s.body}>
        <Card title="Talk to our AI by voice">
          <Text style={s.text}>You will be able to ring Nivaran and explain your problem aloud, in English, Hindi or Tamil. Our AI listens, asks what it needs, and opens your complaint for you.</Text>
          <Text style={[s.soft, { fontWeight: '700' }]}>Status: not available yet. The phone provider is still being set up, so no live calls work today.</Text>
          <Text style={s.soft}>Until then you can speak instead of typing in the chat: tap "Speak instead of typing".</Text>
          <Button label="Tell our AI in chat instead" onPress={onChat} />
        </Card>
        <Card title="Practice call for one of your complaints">
          <Text style={s.soft}>Practice mode only rings your own phone, so you can hear how Nivaran would speak to a company. It never calls a company.</Text>
          <ErrorText message={err} />
          {open.length === 0 ? <Text style={s.soft}>You have no ongoing complaints to practise with yet.</Text> : null}
          {open.map((x) => <Button key={x.id} kind="ghost" label={`Practice: ${x.company}`} onPress={() => onPractice(x.id)} />)}
        </Card>
      </ScrollView>
    </View>
  );
}
