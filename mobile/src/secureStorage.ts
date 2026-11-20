import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import type { KeyValue } from './session';

/** The phone's secure storage (Keychain on iPhone, Keystore on Android). In a browser preview there is no secure storage: the code is kept
 *  only for the open tab (sessionStorage) so nothing lingers. */
export const secureStore: KeyValue = {
  async get(key) {
    if (Platform.OS === 'web') return globalThis.sessionStorage?.getItem(key) ?? null;
    return SecureStore.getItemAsync(key);
  },
  async set(key, value) {
    if (Platform.OS === 'web') { globalThis.sessionStorage?.setItem(key, value); return; }
    await SecureStore.setItemAsync(key, value);
  },
  async remove(key) {
    if (Platform.OS === 'web') { globalThis.sessionStorage?.removeItem(key); return; }
    await SecureStore.deleteItemAsync(key);
  },
};
