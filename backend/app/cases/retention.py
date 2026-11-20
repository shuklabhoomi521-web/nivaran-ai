"""Retention: a case with no activity for a year is deleted, after a warning of at least 48 hours (see docs/notes/dpdp-basics.md).
Pure functions plus a store helper. Nothing is deleted here without a warning date that is old enough."""
from datetime import date, timedelta

from app.cases.models import TrackedCase

INACTIVE_DAYS = 365
NOTICE_DAYS = 2


def last_activity(case: TrackedCase) -> date:
    return max([case.created_on, *[e.on for e in case.events]])


def plan(cases: list[TrackedCase], today: date, inactive_days: int = INACTIVE_DAYS, notice_days: int = NOTICE_DAYS) -> tuple[list[TrackedCase], list[TrackedCase]]:
    """Returns (to_warn, to_delete). Warn when a case has been inactive for the full period and has not been warned yet.
    Delete only when the warning is at least `notice_days` old AND nothing happened on the case since the warning."""
    warn, delete = [], []
    for c in cases:
        idle = (today - last_activity(c)).days
        warned = c.purge_notice_on is not None and last_activity(c) <= c.purge_notice_on     # activity after the warning cancels it
        if warned:
            if (today - c.purge_notice_on).days >= notice_days:
                delete.append(c)
        elif idle >= inactive_days:
            warn.append(c)
    return warn, delete


def mark_warned(case: TrackedCase, today: date) -> TrackedCase:
    return case.model_copy(update={"purge_notice_on": today})
