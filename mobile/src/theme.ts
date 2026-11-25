import { Platform, StyleSheet } from 'react-native';

/** Nivaran design tokens: a calm, professional look (deep navy, slate greys, one steel-blue accent, muted warm tones for status).
 *  No gradients, no blur, no playful shapes: this is software people use to deal with companies and regulators. */
export const c = {
  bg: '#F3F5F8', card: '#FFFFFF', ink: '#172033', soft: '#5A6577', line: '#D8DEE8', lineSoft: '#E8ECF2',
  navy: '#14253F', navyDeep: '#0E1B30', brand: '#1F4E8C', brandSoft: '#E6EEF8',
  pink: '#A5546B', brown: '#8A6A4A', grey: '#6B7280',            // muted rose and warm brown, used for status only
  good: '#2F6F8F', warn: '#8A6A4A', bad: '#A5546B',
};

export const font = Platform.select({ web: 'Inter, "Segoe UI", system-ui, -apple-system, Roboto, Helvetica, Arial, sans-serif', default: undefined });
const shadow = Platform.select({
  web: { boxShadow: '0 1px 2px rgba(16,24,40,0.06), 0 1px 3px rgba(16,24,40,0.04)' } as object,
  default: { shadowColor: '#101828', shadowOpacity: 0.06, shadowRadius: 3, shadowOffset: { width: 0, height: 1 }, elevation: 1 },
});

export const s = StyleSheet.create({
  screen: { flex: 1, paddingTop: 20 },
  header: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 20, paddingBottom: 12, gap: 12 },
  title: { fontFamily: font, fontSize: 22, fontWeight: '600', color: c.ink, flex: 1, letterSpacing: -0.2 },
  body: { padding: 20, gap: 14, paddingBottom: 48 },
  card: { padding: 16, gap: 8 },
  h2: { fontFamily: font, fontSize: 15, fontWeight: '600', color: c.ink },
  text: { fontFamily: font, fontSize: 14.5, color: c.ink, lineHeight: 21 },
  soft: { fontFamily: font, fontSize: 13, color: c.soft, lineHeight: 19 },
  input: { fontFamily: font, backgroundColor: '#FFFFFF', borderWidth: 1, borderColor: '#BFC8D6', borderRadius: 8, paddingVertical: 11, paddingHorizontal: 12, fontSize: 14.5, color: c.ink },
  area: { minHeight: 120, textAlignVertical: 'top' },
  btnInner: { paddingVertical: 12, paddingHorizontal: 16, alignItems: 'center', justifyContent: 'center', minHeight: 44 },
  btnText: { fontFamily: font, color: '#fff', fontWeight: '600', fontSize: 14.5 },
  btnGhostText: { fontFamily: font, color: c.navy, fontWeight: '600', fontSize: 14.5 },
  btnOff: { opacity: 0.4 },
  err: { fontFamily: font, color: c.bad, fontSize: 13.5, lineHeight: 19 },
  chip: { paddingHorizontal: 9, paddingVertical: 3, borderWidth: 1 },
  chipText: { fontFamily: font, fontSize: 11.5, fontWeight: '600', letterSpacing: 0.2 },
  row: { flexDirection: 'row', gap: 10 },
  link: { fontFamily: font, color: c.brand, fontWeight: '600', fontSize: 14.5 },
  shadow: shadow as object,
});
