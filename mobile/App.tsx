import { StatusBar } from 'expo-status-bar';
import React, { useEffect, useMemo, useState } from 'react';
import { Text, View, useWindowDimensions } from 'react-native';
import { s } from './src/theme';
import { Button, Card } from './src/ui';
import { makeApi } from './src/api';
import { API_TOKEN, API_URL } from './src/config';
import { GlassBackground } from './src/glass';
import { Lang, LangProvider } from './src/i18n';
import { layoutFor } from './src/layout';
import { AppFrame, type Tab } from './src/nav';
import { firstName } from './src/greeting';
import CallHomeScreen from './src/screens/CallHomeScreen';
import CallScreen from './src/screens/CallScreen';
import CaseScreen from './src/screens/CaseScreen';
import CodeScreen from './src/screens/CodeScreen';
import ComplaintsScreen from './src/screens/ComplaintsScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import NewCaseScreen from './src/screens/NewCaseScreen';
import ProfileFormScreen from './src/screens/ProfileFormScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import { secureStore } from './src/secureStorage';
import { makeSession } from './src/session';
import type { Profile } from './src/types';

type Screen = { name: Tab } | { name: 'case'; id: string; from: Tab } | { name: 'call'; id: string } | { name: 'editProfile' };

function Plain({ children }: { children: React.ReactNode }) {   // sign-in and first-time details: no side bar yet
  const { width } = useWindowDimensions();
  const l = layoutFor(width);
  return <View style={{ flex: 1, alignItems: 'center', paddingVertical: l.gutter }}><View style={{ flex: 1, width: '100%', maxWidth: l.maxWidth ?? undefined }}>{children}</View></View>;
}

export default function App() {
  const session = useMemo(() => makeSession(secureStore), []);
  const [code, setCode] = useState<string | null | undefined>(API_TOKEN);          // undefined = still looking; null = none yet
  useEffect(() => { if (API_TOKEN) return; void session.load().then(setCode); }, [session]);
  const api = useMemo(() => makeApi(API_URL, fetch, 25000, code ?? undefined), [code]);
  const [profile, setProfile] = useState<Profile | null | undefined>(undefined);      // undefined = loading; null = not filled in yet
  const [profileErr, setProfileErr] = useState<string | null>(null);
  useEffect(() => {
    if (!code) { setProfile(undefined); return; }
    setProfileErr(null);
    api.getProfile().then((p) => { setProfile(p); if (p) setLang(p.preferred_language); }).catch((e) => { if ((e as { status?: number }).status === 401 && !API_TOKEN) { void session.clear(); setCode(null); } else setProfileErr((e as Error).message); });
  }, [api, code]);
  const [screen, setScreen] = useState<Screen>({ name: 'home' });
  const [lang, setLang] = useState<Lang>('en');
  const signOut = API_TOKEN ? undefined : () => { void session.clear(); setCode(null); setProfile(undefined); setScreen({ name: 'home' }); };

  if (code === undefined) return <GlassBackground><StatusBar style="dark" /></GlassBackground>;
  if (code === null) {
    return (
      <GlassBackground><StatusBar style="dark" />
        <Plain><CodeScreen baseUrl={API_URL} onAccepted={(c) => { void session.save(c); setCode(c); }} /></Plain>
      </GlassBackground>
    );
  }
  if (profileErr) {
    return <GlassBackground><Plain><Card title="Cannot reach Nivaran"><Text style={s.text}>{profileErr}</Text><Button label="Try again" onPress={() => { setProfileErr(null); setCode(code + ''); setCode(null); void session.load().then(setCode); }} /></Card></Plain></GlassBackground>;
  }
  if (profile === undefined) return <GlassBackground><StatusBar style="dark" /></GlassBackground>;
  if (profile === null) {
    return (
      <LangProvider value={{ lang, setLang }}><GlassBackground><StatusBar style="dark" />
        <Plain><ProfileFormScreen api={api} initial={null} onSaved={(p) => { setProfile(p); setLang(p.preferred_language); }} /></Plain>
      </GlassBackground></LangProvider>
    );
  }

  const tab: Tab | null = screen.name === 'case' ? screen.from : screen.name === 'call' ? 'callhome' : screen.name === 'editProfile' ? 'profile' : screen.name;
  const go = (t: Tab) => setScreen({ name: t });
  const openCase = (from: Tab) => (id: string) => setScreen({ name: 'case', id, from });
  return (
    <LangProvider value={{ lang, setLang }}>
      <GlassBackground><StatusBar style="dark" />
        <AppFrame current={tab} onGo={go}>
          {screen.name === 'home' && <DashboardScreen api={api} name={firstName(profile.full_name)} onOpen={openCase('home')} onChat={() => go('chat')} onCall={() => go('callhome')} onAll={() => go('complaints')} />}
          {screen.name === 'chat' && <NewCaseScreen api={api} defaultName={profile.full_name} onBack={() => go('home')} onCreated={(id) => setScreen({ name: 'case', id, from: 'complaints' })} />}
          {screen.name === 'callhome' && <CallHomeScreen api={api} onChat={() => go('chat')} onPractice={(id) => setScreen({ name: 'call', id })} />}
          {screen.name === 'complaints' && <ComplaintsScreen api={api} onOpen={openCase('complaints')} onChat={() => go('chat')} />}
          {screen.name === 'profile' && <ProfileScreen api={api} profile={profile} onEdit={() => setScreen({ name: 'editProfile' })} onSignOut={signOut} />}
          {screen.name === 'editProfile' && <ProfileFormScreen api={api} initial={profile} onSaved={(p) => { setProfile(p); setLang(p.preferred_language); go('profile'); }} onCancel={() => go('profile')} />}
          {screen.name === 'case' && <CaseScreen key={screen.id} api={api} id={screen.id} onBack={() => go(screen.from)} onCall={() => setScreen({ name: 'call', id: screen.id })} />}
          {screen.name === 'call' && <CallScreen api={api} id={screen.id} onBack={() => go('callhome')} />}
        </AppFrame>
      </GlassBackground>
    </LangProvider>
  );
}
