import { layoutFor } from '../src/layout';

test('phone uses the full width', () => {
  expect(layoutFor(390)).toEqual({ kind: 'phone', maxWidth: null, gutter: 0 });
  expect(layoutFor(699).kind).toBe('phone');
});
test('tablet and laptop get a centred column', () => {
  expect(layoutFor(700).kind).toBe('tablet');
  expect(layoutFor(1023).maxWidth).toBe(680);
  expect(layoutFor(1024)).toEqual({ kind: 'desktop', maxWidth: 820, gutter: 24 });
  expect(layoutFor(2560).maxWidth).toBe(820);
});
