import { StyleSheet } from 'react-native';

export const c = { bg: '#f6f7f9', card: '#ffffff', ink: '#16191d', soft: '#5b6470', line: '#e1e4e8', brand: '#1d4ed8', good: '#1b7f3b', warn: '#b26a00', bad: '#b3261e' };

export const s = StyleSheet.create({
  screen: { flex: 1, backgroundColor: c.bg, paddingTop: 54 },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingBottom: 10, gap: 12 },
  title: { fontSize: 22, fontWeight: '700', color: c.ink, flex: 1 },
  body: { padding: 16, gap: 12, paddingBottom: 48 },
  card: { backgroundColor: c.card, borderRadius: 14, padding: 14, borderWidth: 1, borderColor: c.line, gap: 6 },
  h2: { fontSize: 16, fontWeight: '700', color: c.ink },
  text: { fontSize: 15, color: c.ink, lineHeight: 21 },
  soft: { fontSize: 13, color: c.soft, lineHeight: 18 },
  input: { backgroundColor: c.card, borderWidth: 1, borderColor: c.line, borderRadius: 10, padding: 12, fontSize: 15, color: c.ink },
  area: { minHeight: 120, textAlignVertical: 'top' },
  btn: { backgroundColor: c.brand, borderRadius: 10, paddingVertical: 12, paddingHorizontal: 16, alignItems: 'center' },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 15 },
  btnGhost: { borderRadius: 10, paddingVertical: 11, paddingHorizontal: 16, alignItems: 'center', borderWidth: 1, borderColor: c.line, backgroundColor: c.card },
  btnGhostText: { color: c.ink, fontWeight: '600', fontSize: 15 },
  btnOff: { opacity: 0.4 },
  err: { color: c.bad, fontSize: 14, lineHeight: 20 },
  chip: { alignSelf: 'flex-start', borderRadius: 999, paddingHorizontal: 10, paddingVertical: 3, borderWidth: 1 },
  chipText: { fontSize: 12, fontWeight: '700' },
  row: { flexDirection: 'row', gap: 10 },
  link: { color: c.brand, fontWeight: '600', fontSize: 15 },
});
