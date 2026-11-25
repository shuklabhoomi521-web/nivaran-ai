import { StyleSheet } from 'react-native';

export const c = { bg: 'transparent', card: 'transparent', ink: '#2B2D33', soft: '#555B66', line: 'rgba(255,255,255,0.7)', brand: '#4A6FA5', pink: '#C4688A', brown: '#7A5A44', grey: '#8A909C', good: '#3F6F8F', warn: '#7A5A44', bad: '#A8456A' };

export const s = StyleSheet.create({
  screen: { flex: 1, paddingTop: 54 },
  header: { flexDirection: 'row', alignItems: 'center', paddingLeft: 16, paddingRight: 104, paddingBottom: 10, gap: 12 },
  title: { fontSize: 22, fontWeight: '700', color: c.ink, flex: 1 },
  body: { padding: 16, gap: 12, paddingBottom: 48 },
  card: { padding: 14, gap: 6 },
  h2: { fontSize: 16, fontWeight: '700', color: c.ink },
  text: { fontSize: 15, color: c.ink, lineHeight: 21 },
  soft: { fontSize: 13, color: c.soft, lineHeight: 18 },
  input: { backgroundColor: 'rgba(255,255,255,0.72)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.9)', borderRadius: 14, padding: 12, fontSize: 15, color: c.ink },
  area: { minHeight: 120, textAlignVertical: 'top' },
  btnInner: { paddingVertical: 13, paddingHorizontal: 16, alignItems: 'center', justifyContent: 'center', minHeight: 46 },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 15 },
    btnGhostText: { color: c.ink, fontWeight: '600', fontSize: 15 },
  btnOff: { opacity: 0.4 },
  err: { color: c.bad, fontSize: 14, lineHeight: 20 },
  chip: { paddingHorizontal: 11, paddingVertical: 4, borderWidth: 1 },
  chipText: { fontSize: 12, fontWeight: '700' },
  row: { flexDirection: 'row', gap: 10 },
  link: { color: c.brand, fontWeight: '600', fontSize: 15 },
});
