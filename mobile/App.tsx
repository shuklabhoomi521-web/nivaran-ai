import { StatusBar } from 'expo-status-bar';
import { View, useWindowDimensions } from 'react-native';
import { layoutFor } from './src/layout';
import React, { useEffect, useMemo, useState } from 'react';
import { makeApi } from './src/api';
import { Lang, LangProvider } from './src/i18n';
import { API_TOKEN, API_URL } from './src/config';
import { GlassBackground } from './src/glass';
import CodeScreen from './src/screens/CodeScreen';
import { secureStore } from './src/secureStorage';
import { makeSession } from './src/session';
import CallScreen from './src/screens/CallScreen';
import CaseScreen from './src/screens/CaseScreen';
import CasesScreen from './src/screens/CasesScreen';
import NewCaseScreen from './src/screens/NewCaseScreen';

type Screen = { name: 'cases' } | { name: 'new' } | { name: 'case'; id: string } | { name: 'call'; id: string };

function Shell({ children }: { children: React.ReactNode }) {
  const { width } = useWindowDimensions();
  const l = layoutFor(width);
  return (
    <View style={{ flex: 1, alignItems: 'center', paddingVertical: l.gutter }}>
      <View style={{ flex: 1, width: '100%', maxWidth: l.maxWidth ?? undefined }}>{children}</View>
    </View>
  );
}

export default function App() {
  const session = useMemo(() => makeSession(secureStore), []);
  const [code, setCode] = useState<string | null | undefined>(API_TOKEN);          // undefined = still looking; null = none yet
  useEffect(() => { if (API_TOKEN) return; void session.load().then(setCode); }, [session]);
  const api = useMemo(() => makeApi(API_URL, fetch, 25000, code ?? undefined), [code]);
  const [screen, setScreen] = useState<Screen>({ name: 'cases' });
  const [lang, setLang] = useState<Lang>('en');
  if (code === undefined) return <GlassBackground><StatusBar style="dark" /></GlassBackground>;
  if (code === null) {
    return (
      <GlassBackground>
        <StatusBar style="dark" />
        <Shell><CodeScreen baseUrl={API_URL} onAccepted={(c) => { void session.save(c); setCode(c); }} /></Shell>
      </GlassBackground>
    );
  }
  return (
    <LangProvider value={{ lang, setLang }}>
    <GlassBackground>
      <StatusBar style="dark" />
      <Shell>
      {screen.name === 'cases' && <CasesScreen key="cases" api={api} onOpen={(id) => setScreen({ name: 'case', id })} onNew={() => setScreen({ name: 'new' })} onSignOut={API_TOKEN ? undefined : () => { void session.clear(); setCode(null); }} />}
      {screen.name === 'new' && <NewCaseScreen api={api} onBack={() => setScreen({ name: 'cases' })} onCreated={(id) => setScreen({ name: 'case', id })} />}
      {screen.name === 'case' && <CaseScreen key={screen.id} api={api} id={screen.id} onBack={() => setScreen({ name: 'cases' })} onCall={() => setScreen({ name: 'call', id: screen.id })} />}
      {screen.name === 'call' && <CallScreen api={api} id={screen.id} onBack={() => setScreen({ name: 'case', id: screen.id })} />}
      </Shell>
    </GlassBackground>
    </LangProvider>
  );
}
