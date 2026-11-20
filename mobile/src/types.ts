// Mirrors the backend models (backend/app/models/case.py, app/cases/models.py, app/letters/outbox.py, app/cases/kit.py).
export interface Fact { name: string; value: string }

export interface UnderstoodCase {
  company: string | null;
  category: string;
  category_confidence: 'high' | 'low';
  problem_summary: string;
  user_goal: string;
  details_known: Fact[];
  details_missing: string[];
  user_language: string;
  urgency: string;
  other_issues: string[];
}

export interface UnderstandResponse {
  case: UnderstoodCase;
  follow_up_question: string | null;
  redacted: string[];            // kinds of private data the server removed before the AI saw the text
}

export type CaseState = 'new' | 'waiting' | 'escalated' | 'resolved' | 'closed';
export type Rung = 'first_contact' | 'follow_up' | 'grievance_officer' | 'appellate' | 'regulator';

export interface CaseEvent {
  on: string;
  kind: 'contacted' | 'reply_received' | 'note' | 'resolved' | 'closed';
  rung: Rung | null;
  channel: string | null;
  text: string;
  docket: string | null;
  source_id: string | null;
}

export interface TrackedCase {
  id: string;
  company: string;
  category: string;
  problem_summary: string;
  user_goal: string;
  user_name: string | null;
  facts: Fact[];
  created_on: string;
  state: CaseState;
  events: CaseEvent[];
  purge_notice_on: string | null;
}

export interface ConsentNotice { version: string; text: string }

export interface Action {
  rung: Rung;
  due_on: string;
  days_overdue: number;
  channel: string;
  target_label: string;
  target_value: string | null;
  source_url: string | null;
  source_quote: string | null;
  reason: string;
  fell_back_from: Rung | null;
  note: string | null;
}

export interface Reminder { rung: Rung; due_on: string; status: 'done' | 'due' | 'upcoming' | 'closed' }
export interface NextResponse { action: Action | null; reminders: Reminder[] }

export type DraftStatus = 'pending' | 'approved' | 'sent' | 'rejected';
export interface Draft {
  id: string;
  case_id: string;
  rung: Rung;
  channel: 'email' | 'portal';
  to: string;
  subject: string;
  body: string;
  status: DraftStatus;
  created_on: string;
}

export interface SourceRef { url: string; quote: string; kind: string; checked_on: string }
export interface KitItem { text: string; source: SourceRef | null; ours: boolean }
export interface PortalKit {
  regulator_key: string;
  regulator: string;
  portal_url: string;
  helpline: string | null;
  purpose: string;
  purpose_source_url: string | null;
  purpose_quote: string | null;
  steps: KitItem[];
  official_attach: KitItem[];
  checklist: string[];
  complaint_text: string;
  warnings: string[];
  needs_check: string[];
}

export interface Match {
  message: { subject: string; from_addr: string; on: string; snippet: string };
  strength: 'strong' | 'weak';
  reason: string;
  auto_acknowledgement: boolean;
  looks_resolved: boolean;
  docket: string | null;
}
export interface CheckResponse { new_replies: Match[]; case: TrackedCase }

export interface TranscribeResponse { text: string; language: string | null; provider: string | null; redacted: string[] }
