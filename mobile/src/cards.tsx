import React, { useEffect, useState } from 'react';
import { Pressable, Text } from 'react-native';
import type { Api } from './api';
import { STATE_COLOR, caseTitle, categoryLabel, followUpText, prettyDate } from './format';
import { GlassSurface } from './glass';
import { c, s } from './theme';
import type { NextResponse, TrackedCase } from './types';
import { isOngoing } from './profileUtil';
import { Chip } from './ui';

/** Loads the next-step info for each ongoing case (one small request each). */
export function useNexts(api: Api, cases: TrackedCase[]): Record<string, NextResponse | null> {
  const [m, setM] = useState<Record<string, NextResponse | null>>({});
  useEffect(() => {
    let live = true;
    cases.filter((x) => isOngoing(x.state)).forEach((x) => {
      api.nextStep(x.id).then((n) => { if (live) setM((o) => ({ ...o, [x.id]: n })); }).catch(() => { if (live) setM((o) => ({ ...o, [x.id]: null })); });
    });
    return () => { live = false; };
  }, [api, cases]);
  return m;
}

export function ComplaintCard({ item, next, onOpen }: { item: TrackedCase; next: NextResponse | null | undefined; onOpen: () => void }) {
  const ongoing = isOngoing(item.state);
  const line = ongoing && next === undefined ? 'Checking the schedule…' : followUpText(next ?? null, item.state);
  return (
    <Pressable accessibilityRole="button" accessibilityLabel={caseTitle(item.company, item.state)} onPress={onOpen} style={{ marginBottom: 12 }}>
      <GlassSurface style={s.card}>
        <Text style={s.h2}>{item.company}</Text>
        <Chip text={caseTitle(item.company, item.state).split(' · ')[1]} color={STATE_COLOR[item.state]} />
        <Text style={[s.soft, { color: c.ink }]} numberOfLines={2}>{item.problem_summary}</Text>
        <Text style={[s.soft, { fontWeight: '600', color: c.brand }]}>{line}</Text>
        <Text style={s.soft}>{categoryLabel(item.category)} · started {prettyDate(item.created_on)}</Text>
      </GlassSurface>
    </Pressable>
  );
}
