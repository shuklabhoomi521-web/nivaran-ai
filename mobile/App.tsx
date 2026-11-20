import { StatusBar } from 'expo-status-bar';
import React, { useMemo, useState } from 'react';
import { makeApi } from './src/api';
import { API_URL } from './src/config';
import { GlassBackground } from './src/glass';
import CaseScreen from './src/screens/CaseScreen';
import CasesScreen from './src/screens/CasesScreen';
import NewCaseScreen from './src/screens/NewCaseScreen';

type Screen = { name: 'cases' } | { name: 'new' } | { name: 'case'; id: string };

export default function App() {
  const api = useMemo(() => makeApi(API_URL), []);
  const [screen, setScreen] = useState<Screen>({ name: 'cases' });
  return (
    <GlassBackground>
      <StatusBar style="dark" />
      {screen.name === 'cases' && <CasesScreen key="cases" api={api} onOpen={(id) => setScreen({ name: 'case', id })} onNew={() => setScreen({ name: 'new' })} />}
      {screen.name === 'new' && <NewCaseScreen api={api} onBack={() => setScreen({ name: 'cases' })} onCreated={(id) => setScreen({ name: 'case', id })} />}
      {screen.name === 'case' && <CaseScreen key={screen.id} api={api} id={screen.id} onBack={() => setScreen({ name: 'cases' })} />}
    </GlassBackground>
  );
}
