import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import { ALL_RUNGS, planReminders, reminderId } from './reminderPlan';
import type { NextResponse, TrackedCase } from './types';

Notifications.setNotificationHandler?.({
  handleNotification: async () => ({ shouldShowBanner: true, shouldShowList: true, shouldPlaySound: false, shouldSetBadge: false }),
});

async function allowed(): Promise<boolean> {
  if (Platform.OS === 'web') return false;
  const cur = await Notifications.getPermissionsAsync();
  if (cur.granted) return true;
  if (!cur.canAskAgain) return false;
  return (await Notifications.requestPermissionsAsync()).granted;
}

/** Make the phone's reminders match the case: cancel this case's old ones, then schedule the ones still ahead. Never throws. */
export async function syncReminders(tc: TrackedCase, next: NextResponse): Promise<void> {
  try {
    await cancelReminders(tc.id);
    const plan = planReminders(tc, next, new Date());
    if (plan.length === 0 || !(await allowed())) return;
    for (const p of plan) {
      await Notifications.scheduleNotificationAsync({ identifier: p.id, content: { title: p.title, body: p.body }, trigger: { type: Notifications.SchedulableTriggerInputTypes.DATE, date: p.at } });
    }
  } catch { /* reminders are a convenience: a failure must never break the case screen */ }
}

export async function cancelReminders(caseId: string): Promise<void> {
  if (Platform.OS === 'web') return;
  try {
    for (const rung of ALL_RUNGS) await Notifications.cancelScheduledNotificationAsync(reminderId(caseId, rung));
  } catch { /* nothing to cancel */ }
}
