// The phone must reach the laptop running the backend: use the laptop's address on the same Wi-Fi, for example
//   EXPO_PUBLIC_API_URL=http://192.168.1.20:8000 npx expo start
export const API_URL: string = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';
// The pilot backend asks for a secret token (see scripts/run_pilot.sh): EXPO_PUBLIC_API_TOKEN=$(cat .pilot_token)
export const API_TOKEN: string | undefined = process.env.EXPO_PUBLIC_API_TOKEN || undefined;
