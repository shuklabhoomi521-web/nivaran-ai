from datetime import date, timedelta

from app.cases import engine
from app.cases.models import Event, EventKind
from app.cases.retention import last_activity, mark_warned, plan
from tests.test_case_engine import understood

D0 = date(2026, 1, 10)


def case(cid="c1", on=D0):
    return engine.new_case(understood(), on, cid)


def test_active_cases_are_left_alone_and_old_ones_are_warned_first():
    fresh, old = case("a", D0 + timedelta(days=300)), case("b", D0)
    warn, delete = plan([fresh, old], D0 + timedelta(days=365))
    assert [c.id for c in warn] == ["b"] and delete == []                       # a year idle: warn, never delete in the same step


def test_activity_resets_the_clock():
    c = engine.apply(case(), Event(on=D0 + timedelta(days=200), kind=EventKind.note, text="docket"))
    assert last_activity(c) == D0 + timedelta(days=200)
    assert plan([c], D0 + timedelta(days=365)) == ([], [])
    assert [x.id for x in plan([c], D0 + timedelta(days=565))[0]] == ["c1"]


def test_delete_only_after_a_48_hour_warning_and_only_if_nothing_happened_since():
    c = mark_warned(case(), D0 + timedelta(days=365))
    assert plan([c], D0 + timedelta(days=366)) == ([], [])                       # 1 day after the warning: too early
    warn, delete = plan([c], D0 + timedelta(days=367))
    assert warn == [] and [x.id for x in delete] == ["c1"]                       # 2 days: now it may go
    back = engine.apply(c, Event(on=D0 + timedelta(days=366), kind=EventKind.note, text="I am back"))
    assert plan([back], D0 + timedelta(days=400)) == ([], [])                    # the user returned after the warning: not deleted
