#!/usr/bin/env python3
"""Emit the discrete VM shift / time-slot records that should be imported for a series.

This is the *deterministic materialization step* for the two VM entities whose count can
exceed hand-authoring size — ``JobPositionShift`` (a dated series) and ``TimeSlot`` (a
weekly window set). It does NOT write to the org: it emits a ``{"records": [...]}`` tree
object on stdout — the request body of a ``composite/tree`` call, and the file format of a
Salesforce CLI tree import — which the skill sends with the write call documented in
``references/mcp-invocation.md``. A tree call is all-or-nothing, so each batch either
lands whole or not at all.

Its contract is "given a series spec, emit the records that should be *created*" — which
includes NOT re-emitting shifts that already exist (``excludeExisting``). Expansion and
that set-difference both live here, in reviewed/tested code, because the alternative —
day/date arithmetic or dedup done by hand in the skill — is exactly the error-prone,
unreviewed work this script exists to replace (see SKILL.md: "Never build a series or a
records table by hand"). The agent passes a **spec** (args as data)
and never authors code per run.

Field API names come from ``references/field-guide.md`` — the standard-field authority.
No field is emitted that the field guide does not document, and fields that default
server-side are deliberately left unset: ``OperatingHours`` has no ``Type`` field at all,
while ``TimeSlot.Type`` DOES exist but is required-but-defaulted (unset yields ``Normal``,
which VM doesn't use) and ``TimeSlot.Name`` is auto-number — none are ever set here.

USAGE
-----
    python3 scripts/expand-series.py < spec.json          # one tree object to stdout (<=200 records)
    python3 scripts/expand-series.py --out-dir ./import <  spec.json   # one importable file per <=200 batch

    stdout carries a SINGLE importable tree object, so a series over 200 records
    (which must split into multiple files) requires --out-dir; the script fails with
    a message rather than printing a JSON array a tree call cannot read.

WINDOWS: uniform vs. per-day
----------------------------
Supply EXACTLY ONE of:
  * ``windows`` — a flat list applied UNIFORMLY to every day in the series. Use only
    when the time windows are the same on every ``daysOfWeek`` (or every explicit date).
  * ``windowsByDay`` — a map of day-name -> window list, when the windows VARY by weekday
    (e.g. Sat 08:00–12:00 + 12:00–17:00 but Sun 09:00–14:00). The map keys define which
    weekdays the series runs on, so do NOT also pass ``daysOfWeek`` with ``windowsByDay``.

Overlapping windows on the same day (e.g. 08:00–13:00 and 12:00–17:00) are ALLOWED and
emitted as-is — VM permits overlapping shift records; the script does not second-guess
intent. (For a same-day window — ``endDayOffset`` 0 — it still rejects an end that is not
after the start.) An EXACT duplicate window (same start/end/offset listed twice) collapses
to one shift — never emitted twice.

MULTI-DAY / OVERNIGHT shifts (JobPositionShift only)
----------------------------------------------------
A ``JobPositionShift`` has separate StartDate and EndDate, so a shift may span dates. Each
window may carry ``endDayOffset`` (int >= 0, default 0) — how many days AFTER its StartDate
the window ENDS:
  * 0 (default) — single-day shift; EndDate == StartDate; end time must be after start.
  * 1 — crosses midnight into the next day (e.g. 23:00 -> 03:00 the next morning).
  * N — an N-day span (e.g. a Mon 09:00 -> Fri 17:00 shift is endDayOffset 4).
The recurring/one-off date is the StartDate and EndDate = StartDate + offset; with an offset
the end time may be earlier than the start time (EndDate > StartDate already orders them).
EndDate can fall past ``dateRange.end`` — the range bounds START dates, not end dates.
``TimeSlot`` is a single-weekday window (no EndDate) and rejects ``endDayOffset``.

DATES: ranges + one-offs + removals (JobPositionShift)
------------------------------------------------------
The date set is the UNION of two optional sources (supply at least one):
  * ``dateRanges`` — a LIST of {start, end}; each range recurs on the series' weekdays
    (``daysOfWeek`` in flat-window mode, or the ``windowsByDay`` keys in per-day mode).
    ``dateRange`` (singular) is accepted as sugar for a one-element list.
  * ``oneOffDates`` — individual 'YYYY-MM-DD' dates added AS-IS (no weekday filter), for
    one-off extras/exceptions outside the recurring pattern.
So "every Tue/Thu across June and September, plus Aug 15" is ONE spec (multiple ranges +
a one-off) — no need to run the script per range. Overlapping ranges / a one-off already
inside a range collapse: each date appears once.

``excludeDates`` — an optional list of 'YYYY-MM-DD' dates to DROP from the union
(regardless of window). This is the in-memory removal ("skip the July 4th shift I was
about to create"); it is independent of ``excludeExisting`` below (which is org dedup by
full shift key, not date removal).

``count`` — an optional integer >= 1 that bounds the series by NUMBER OF DATES instead of
(or as well as) an end date: the series keeps the first ``count`` dates of the union, after
``excludeDates`` is applied, and every window on a kept date becomes a shift. With ``count``
a range may omit its ``end`` ("start 2027-06-05, 10 Saturdays"); with both an end and a
count the series stops at whichever comes first. A series always needs an end date or a
count, so an open-ended series can't be expressed. ``count`` is applied before
``excludeExisting``, so it counts the dates the user asked for, not only the missing ones.

SPEC (stdin JSON)
-----------------
JobPositionShift — ranges + one-offs, uniform windows:
    {
      "entity": "JobPositionShift",
      "parentId": "0Jp...",              # literal JobPosition Id  (or "parentRef")
      "parentRef": "JobPosition_1",      # @refId — only when the JobPosition is in the SAME tree file;
                                         # a parent from an earlier import is always a literal parentId
      "daysOfWeek": ["Tuesday", "Thursday"],   # weekdays the ranges recur on
      "windows": [{"start": "10:00", "end": "12:00"}, {"start": "14:00", "end": "16:00"}],
      "dateRanges": [                    # LIST of ranges (or "dateRange" for a single one)
        {"start": "2027-06-01", "end": "2027-06-30"},
        {"start": "2027-09-01", "end": "2027-09-30"}
      ],
      "oneOffDates": ["2027-08-15"],     # optional individual dates outside the ranges
      "excludeDates": ["2027-06-08"],    # optional whole dates to drop (in-memory removal)
      "timeZone": "America/New_York",
      "maximumAttendeesCount": 8,        # optional
      "status": "Upcoming",              # optional — omitted means "Upcoming", so pass the
                                         # value the user confirmed in the review
      "count": 10,                       # optional — keep only the first N dates
      "referenceIdPrefix": "JPS",        # optional
      "excludeExisting": [               # optional — shifts already in the org; skip re-creating these
        {"StartDate": "2027-06-01", "EndDate": "2027-06-01",
         "StartTime": "10:00:00.000Z", "EndTime": "12:00:00.000Z"}
      ]
    }

JobPositionShift — per-day windows (windows vary by weekday):
    {
      "entity": "JobPositionShift",
      "parentId": "0Jp...",
      "windowsByDay": {
        "Saturday": [{"start": "08:00", "end": "12:00"}, {"start": "12:00", "end": "17:00"}],
        "Sunday":   [{"start": "09:00", "end": "14:00"}]
      },
      "dateRange": {"start": "2027-06-05", "end": "2027-08-29"},
      "timeZone": "America/New_York"
    }

JobPositionShift — bounded by a count instead of an end date (10 Saturdays):
    {
      "entity": "JobPositionShift",
      "parentId": "0Jp...",
      "daysOfWeek": ["Saturday"],
      "windows": [{"start": "09:00", "end": "12:00"}],
      "dateRange": {"start": "2027-06-05"},
      "count": 10,
      "timeZone": "America/New_York"
    }

    ``oneOffDates`` may be used with either window form; with ``windowsByDay`` every date
    (range-derived OR one-off) must fall on a weekday present in the map. A spec of ONLY
    ``oneOffDates`` (no ranges) needs no ``daysOfWeek``.
    {
      "entity": "JobPositionShift",
      "parentId": "0Jp...",
      "oneOffDates": ["2026-09-06", "2026-09-20", "2026-10-11"],
      "windows": [{"start": "12:00", "end": "16:00"}],
      "timeZone": "America/New_York",
      "maximumAttendeesCount": 30
    }

excludeExisting (JobPositionShift only): a list of already-existing shifts to skip, matched
on the shift key ``JobPositionId + StartDate + EndDate + StartTime + EndTime``. A spec has one
JobPosition, so pass only that JobPosition's shifts and the four date/time fields are compared. Times accept "HH:MM",
"HH:MM:SS", or the Salesforce literal "HH:MM:SS.000Z" that a SOQL query returns, so a
query result can be passed straight through. ``EndDate`` defaults to ``StartDate`` if
omitted. If every generated shift is excluded, the script exits non-zero with a clear
"nothing to create" message rather than emitting an empty import.

TimeSlot (weekly windows — no dateRange; parent OperatingHours must be a LITERAL Id
because OperatingHoursId is master-detail). Supports uniform ``windows`` (+ ``daysOfWeek``)
or per-day ``windowsByDay``:
    {
      "entity": "TimeSlot",
      "parentId": "0OH...",              # literal OperatingHours Id (master-detail: no @ref)
      "daysOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "windows": [{"start": "10:00", "end": "12:00"}, {"start": "14:00", "end": "16:00"}],
      "referenceIdPrefix": "TS"          # optional
    }

Exit non-zero with a message on any spec error (unknown entity, bad day name, bad
time/date, both/neither windows forms, empty result, TimeSlot given a @ref parent, etc.).
"""

import argparse
import datetime as dt
import json
import os
import sys

TREE_IMPORT_CAP = 200  # Composite Tree API caps at 200 records per call.

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_INDEX = {name: i for i, name in enumerate(DAY_NAMES)}


def fail(msg):
    sys.stderr.write("expand-series: %s\n" % msg)
    sys.exit(1)


def parse_time(value, label):
    """Accept 'HH:MM', 'HH:MM:SS', or the Salesforce literal 'HH:MM:SS.mmmZ'
    (as a SOQL query returns it) -> canonical 'HH:MM:SS.000Z'."""
    if not isinstance(value, str):
        fail("%s must be a string like '10:00' or '10:00:00'" % label)
    parts = value.strip().split(":")
    if len(parts) == 2:
        parts.append("00")
    if len(parts) != 3:
        fail("%s '%s' is not HH:MM or HH:MM:SS" % (label, value))
    # Tolerate a fractional-seconds / trailing-Z suffix on the seconds component so a
    # Salesforce time literal ('12:00:00.000Z') round-trips into the same canonical form.
    sec = parts[2].split(".")[0].rstrip("Zz")
    try:
        h, m, s = int(parts[0]), int(parts[1]), int(sec)
        dt.time(h, m, s)  # validate ranges
    except ValueError:
        fail("%s '%s' is not a valid time" % (label, value))
    return "%02d:%02d:%02d.000Z" % (h, m, s)


def parse_date(value, label):
    if not isinstance(value, str):
        fail("%s must be a 'YYYY-MM-DD' string" % label)
    try:
        return dt.date.fromisoformat(value.strip())
    except ValueError:
        fail("%s '%s' is not a valid YYYY-MM-DD date" % (label, value))


def normalize_window_list(value, label, allow_span=True):
    """A list of {start, end[, endDayOffset]} -> list of (start, end, offset).

    ``endDayOffset`` (int >= 0, default 0) is how many days after StartDate the window
    ENDS: 0 = same day, 1 = crosses midnight into the next day, N = an N-day span. Only
    ``JobPositionShift`` supports it (it has a separate EndDate); ``TimeSlot`` windows are
    single-weekday (``allow_span=False``) and reject a nonzero offset. When the offset is 0
    the end must be after the start (a valid same-day window); once the window spans a later
    day any end time is valid, because EndDate > StartDate already makes the end datetime
    later than the start.
    """
    if not isinstance(value, list) or not value:
        fail("%s must be a non-empty list of {start, end}" % label)
    out = []
    for w in value:
        if not isinstance(w, dict) or "start" not in w or "end" not in w:
            fail("each %s entry needs a 'start' and 'end' (HH:MM)" % label)
        start = parse_time(w["start"], "%s.start" % label)
        end = parse_time(w["end"], "%s.end" % label)
        offset = w.get("endDayOffset", 0)
        # bool is an int subclass — reject it so a stray `true` isn't read as offset 1.
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            fail("%s endDayOffset must be an integer >= 0 "
                 "(0 = same day, 1 = next day, N = N-day span)" % label)
        if offset and not allow_span:
            fail("%s cannot span days — endDayOffset is only for JobPositionShift, "
                 "which has an EndDate (a TimeSlot is one weekday's window)" % label)
        if offset == 0 and end <= start:
            fail("%s end %s must be after start %s — for a shift that crosses midnight or "
                 "spans days, set endDayOffset (1 = next day, N = N-day span)"
                 % (label, w["end"], w["start"]))
        out.append((start, end, offset))
    return out


def normalize_windows_by_day(raw, allow_span=True):
    """A map dayName -> [{start,end}] -> {dayName: [(start,end,offset)]}."""
    if not isinstance(raw, dict) or not raw:
        fail("windowsByDay must be a non-empty map of dayName -> [{start, end}]")
    out = {}
    for day, wins in raw.items():
        if day not in DAY_INDEX:
            fail("unknown day '%s' in windowsByDay — use %s" % (day, ", ".join(DAY_NAMES)))
        out[day] = normalize_window_list(wins, "windowsByDay['%s']" % day, allow_span)
    return out


def resolve_windows(spec, allow_span=True):
    """Return ('flat', [(start,end,offset)]) or ('by_day', {day: [(start,end,offset)]}).

    Exactly one of ``windows`` / ``windowsByDay`` must be supplied. ``allow_span`` gates the
    per-window ``endDayOffset`` (JobPositionShift only); TimeSlot passes ``allow_span=False``.
    """
    flat = spec.get("windows")
    by_day = spec.get("windowsByDay")
    if (flat is None) == (by_day is None):
        fail("supply exactly one of 'windows' (uniform) or 'windowsByDay' (per-day)")
    if flat is not None:
        return "flat", normalize_window_list(flat, "windows", allow_span)
    return "by_day", normalize_windows_by_day(by_day, allow_span)


def normalize_days(spec):
    days = spec.get("daysOfWeek")
    if not isinstance(days, list) or not days:
        fail("daysOfWeek must be a non-empty list of day names")
    out = []
    for d in days:
        if d not in DAY_INDEX:
            fail("unknown day '%s' — use %s" % (d, ", ".join(DAY_NAMES)))
        out.append(d)
    return out


def dates_in_range(date_range, wanted_days, open_limit=None):
    """Dates in ``date_range`` that fall on ``wanted_days``.

    A range without an ``end`` is only valid when the spec sets ``count``; it then yields
    ``open_limit`` matching dates from its start, which is enough to fill ``count`` after
    ``excludeDates`` removes any of them.
    """
    start = parse_date(date_range.get("start"), "dateRange.start")
    end = None
    if date_range.get("end") is None:
        if open_limit is None:
            fail("dateRange.end is required unless the spec sets 'count' — a series needs "
                 "an end date or a count")
    else:
        end = parse_date(date_range.get("end"), "dateRange.end")
        if end < start:
            fail("dateRange.end must be on/after dateRange.start")
    wanted = {DAY_INDEX[d] for d in wanted_days}
    out = []
    cur = start
    one = dt.timedelta(days=1)
    while end is None or cur <= end:
        if end is None and len(out) >= open_limit:
            break
        if cur.weekday() in wanted:
            out.append(cur)
        cur += one
    return out


def parse_count(spec):
    """``count`` (optional int >= 1) — the number of series dates to keep."""
    count = spec.get("count")
    if count is None:
        return None
    # bool is an int subclass — reject it so a stray `true` isn't read as 1.
    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
        fail("count must be an integer >= 1 (the number of dates in the series)")
    return count


def parent_value(spec, entity):
    literal = spec.get("parentId")
    ref = spec.get("parentRef")
    if literal and ref:
        fail("supply only one of parentId / parentRef")
    if literal:
        return literal
    if ref:
        if entity == "TimeSlot":
            fail("TimeSlot.OperatingHoursId is master-detail — the parent must be a "
                 "literal Id (parentId), not a @ref. Create OperatingHours first.")
        return "@" + str(ref).lstrip("@")
    fail("supply a parentId (literal) or parentRef (@refId) for the parent")


def resolve_shift_dates(spec, mode, windows):
    """Return the ordered, de-duplicated list of dt.date for a shift series.

    The date set is the UNION of two optional sources (supply at least one):
      * ``dateRanges`` — a list of {start, end} ranges, each expanded on the series'
        recurring weekdays (``daysOfWeek`` in flat mode, or the ``windowsByDay`` keys in
        per-day mode). ``dateRange`` (singular) is accepted as sugar for a one-element list.
      * ``oneOffDates`` — individual 'YYYY-MM-DD' dates added AS-IS (no weekday filter);
        use for one-off extras/exceptions that fall outside the recurring pattern.
    ``excludeDates`` (optional) then removes whole dates from the union — an in-memory
    removal (e.g. a holiday), independent of ``excludeExisting`` (which is org-dedup by
    the full shift key). Overlapping ranges and a one-off that also lands in a range both
    collapse — a date appears once. ``count`` (optional) finally keeps the first N dates.
    """
    if spec.get("dates") is not None:
        fail("'dates' was renamed for clarity — use 'oneOffDates' for individual dates "
             "and 'dateRanges' (or 'dateRange') for recurring ranges")

    # Collect ranges: singular sugar + list form.
    ranges = []
    single = spec.get("dateRange")
    if single is not None:
        if not isinstance(single, dict):
            fail("dateRange must be a single {start, end} object; for multiple ranges use 'dateRanges'")
        ranges.append(single)
    many = spec.get("dateRanges")
    if many is not None:
        if not isinstance(many, list) or not many:
            fail("dateRanges must be a non-empty list of {start, end} objects")
        for r in many:
            if not isinstance(r, dict):
                fail("each dateRanges entry must be a {start, end} object")
        ranges.extend(many)

    one_offs = spec.get("oneOffDates")
    if one_offs is not None and (not isinstance(one_offs, list) or not one_offs):
        fail("oneOffDates must be a non-empty list of 'YYYY-MM-DD' strings")

    if not ranges and one_offs is None:
        fail("JobPositionShift needs 'dateRanges' (or 'dateRange') and/or 'oneOffDates'")

    # Weekdays the ranges recur on.
    if mode == "by_day":
        if spec.get("daysOfWeek") is not None:
            fail("windowsByDay already defines the weekdays — do not also pass daysOfWeek")
        wanted_days = list(windows.keys())
    else:
        wanted_days = normalize_days(spec) if ranges else None

    count = parse_count(spec)
    excl = spec.get("excludeDates")
    if excl is not None and not isinstance(excl, list):
        fail("excludeDates must be a list of 'YYYY-MM-DD' strings")
    open_limit = count + len(excl or []) if count is not None else None

    collected = set()
    for r in ranges:
        for day in dates_in_range(r, wanted_days, open_limit):
            collected.add(day)
    if one_offs is not None:
        seen = set()
        for d in one_offs:
            day = parse_date(d, "oneOffDates[]")
            if day in seen:
                fail("duplicate date '%s' in oneOffDates" % d)
            seen.add(day)
            collected.add(day)

    # Per-day mode: every date (incl. one-offs) must map to a windowsByDay entry.
    if mode == "by_day":
        for day in collected:
            name = DAY_NAMES[day.weekday()]
            if name not in windows:
                fail("date %s falls on %s, which has no entry in windowsByDay"
                     % (day.isoformat(), name))

    if excl is not None:
        for d in excl:
            collected.discard(parse_date(d, "excludeDates[]"))

    ordered = sorted(collected)
    return ordered[:count] if count is not None else ordered


def normalize_exclusions(spec):
    """Build the set of already-existing shift keys to skip.

    Key = (StartDate, EndDate, StartTime, EndTime), all canonicalized to the same form
    the generator emits so a SOQL query result matches byte-for-byte. EndDate
    defaults to StartDate when omitted (single-day shift).
    """
    raw = spec.get("excludeExisting")
    if raw is None:
        return set()
    if not isinstance(raw, list):
        fail("excludeExisting must be a list of {StartDate, EndDate, StartTime, EndTime}")
    out = set()
    for i, e in enumerate(raw):
        if not isinstance(e, dict):
            fail("excludeExisting[%d] must be an object" % i)
        sd = parse_date(e.get("StartDate"), "excludeExisting[%d].StartDate" % i).isoformat()
        ed_raw = e.get("EndDate")
        ed = parse_date(ed_raw, "excludeExisting[%d].EndDate" % i).isoformat() if ed_raw else sd
        st = parse_time(e.get("StartTime"), "excludeExisting[%d].StartTime" % i)
        et = parse_time(e.get("EndTime"), "excludeExisting[%d].EndTime" % i)
        out.add((sd, ed, st, et))
    return out


def build_shifts(spec):
    """Return (records, generated_count, skipped_count).

    ``generated_count`` is every (date x window) the series describes; ``skipped_count`` is
    how many of those were dropped as already-existing (excludeExisting). ``records`` is
    what remains to import.
    """
    mode, windows = resolve_windows(spec)
    shift_dates = resolve_shift_dates(spec, mode, windows)
    tz = spec.get("timeZone")
    if not tz:
        fail("JobPositionShift needs a timeZone (IANA, e.g. America/New_York)")
    parent = parent_value(spec, "JobPositionShift")
    status = spec.get("status", "Upcoming")
    cap = spec.get("maximumAttendeesCount")
    prefix = spec.get("referenceIdPrefix", "JPS")
    exclude = normalize_exclusions(spec)

    records = []
    generated = 0
    skipped = 0
    n = 0
    seen = set()
    for day in shift_dates:
        iso = day.isoformat()
        day_windows = windows if mode == "flat" else windows[DAY_NAMES[day.weekday()]]
        for (start, end, offset) in day_windows:
            # EndDate = StartDate + offset days: 0 = single-day, 1 = crosses midnight, N =
            # an N-day span. The key mirrors the org natural key (JobPositionId is fixed per
            # spec) so a queried existing shift matches exactly.
            end_iso = (day + dt.timedelta(days=offset)).isoformat()
            key = (iso, end_iso, start, end)
            if key in seen:
                continue  # exact-duplicate (dates, window) — never emit the same shift twice
            seen.add(key)
            generated += 1
            if key in exclude:
                skipped += 1
                continue
            n += 1
            fields = {
                "attributes": {"type": "JobPositionShift",
                               "referenceId": "%s_%d" % (prefix, n)},
                "JobPositionId": parent,
                "Status": status,
                "StartDate": iso,
                "EndDate": end_iso,
                "StartTime": start,
                "EndTime": end,
                "TimeZone": tz,
            }
            if cap is not None:
                fields["MaximumAttendeesCount"] = cap
            records.append(fields)
    return records, generated, skipped


def build_timeslots(spec):
    mode, windows = resolve_windows(spec, allow_span=False)
    if spec.get("dateRange"):
        fail("TimeSlot is a weekly window set — do not pass a dateRange")
    if spec.get("dates"):
        fail("TimeSlot is a weekly window set — do not pass a 'dates' list "
             "(that belongs to a JobPositionShift spec)")
    if spec.get("count") is not None:
        fail("TimeSlot is a weekly window set — 'count' belongs to a JobPositionShift spec")
    parent = parent_value(spec, "TimeSlot")  # enforces literal Id
    prefix = spec.get("referenceIdPrefix", "TS")

    if mode == "flat":
        seen_day, days = set(), []
        for d in normalize_days(spec):
            if d not in seen_day:  # collapse a day listed twice → no duplicate slots
                seen_day.add(d)
                days.append(d)
        day_windows = [(d, windows) for d in days]
    else:
        if spec.get("daysOfWeek") is not None:
            fail("windowsByDay already defines the days — do not also pass daysOfWeek")
        day_windows = [(d, windows[d]) for d in windows.keys()]

    records = []
    n = 0
    seen = set()
    for day, wins in day_windows:
        for (start, end, _offset) in wins:  # offset is always 0 here (allow_span=False)
            if (day, start, end) in seen:
                continue  # exact-duplicate (day, window) — never emit the same slot twice
            seen.add((day, start, end))
            n += 1
            records.append({
                "attributes": {"type": "TimeSlot",
                               "referenceId": "%s_%d" % (prefix, n)},
                "OperatingHoursId": parent,
                "DayOfWeek": day,
                "StartTime": start,
                "EndTime": end,
            })
    if not records:
        fail("no time slots produced — check daysOfWeek / windows")
    return records


def chunk(records, size):
    return [records[i:i + size] for i in range(0, len(records), size)]


def main():
    ap = argparse.ArgumentParser(description="Expand a VM shift/time-slot series to tree-import JSON.")
    ap.add_argument("--out-dir", help="write one JSON file per <=200-record batch here; "
                                      "print the paths instead of the JSON")
    args = ap.parse_args()

    raw = sys.stdin.read()
    if not raw.strip():
        fail("no spec on stdin — pipe a JSON spec (see the module docstring)")
    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as e:
        fail("spec is not valid JSON: %s" % e)

    if not isinstance(spec, dict):
        fail("spec must be a JSON object (got %s) — see the module docstring" % type(spec).__name__)

    entity = spec.get("entity")
    if entity == "JobPositionShift":
        records, generated, skipped = build_shifts(spec)
        if generated == 0:
            fail("no shifts produced — check dateRanges/oneOffDates against the weekdays "
                 "(daysOfWeek or windowsByDay), or whether excludeDates removed them all")
        if not records:
            fail("all %d requested shift(s) already exist (excludeExisting); nothing to create"
                 % generated)
        if skipped:
            sys.stderr.write("expand-series: excluded %d already-existing shift(s); "
                             "%d to create\n" % (skipped, len(records)))
    elif entity == "TimeSlot":
        records = build_timeslots(spec)
    else:
        fail("entity must be 'JobPositionShift' or 'TimeSlot' (got %r)" % entity)

    batches = chunk(records, TREE_IMPORT_CAP)

    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
        paths = []
        for i, batch in enumerate(batches, 1):
            path = os.path.join(args.out_dir, "%s-%02d.json" % (entity, i))
            with open(path, "w") as fh:
                json.dump({"records": batch}, fh, indent=2)
                fh.write("\n")
            paths.append(path)
        sys.stderr.write("expand-series: %d record(s) -> %d file(s)\n"
                         % (len(records), len(paths)))
        print("\n".join(paths))
    else:
        # stdout carries a SINGLE importable tree object ({records:[...]}). Once the
        # series splits past the 200-record cap, no single stdout payload is valid
        # tree-import input, so require --out-dir and write one importable file per
        # batch rather than emitting a JSON array a tree call cannot read.
        if len(batches) > 1:
            fail("%d record(s) exceed the %d-record tree-import cap (%d batches). "
                 "Re-run with --out-dir <dir> to write one importable file per batch, "
                 "then import each file separately."
                 % (len(records), TREE_IMPORT_CAP, len(batches)))
        json.dump({"records": batches[0]}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        sys.stderr.write("expand-series: %d record(s) in %d batch(es)\n"
                         % (len(records), len(batches)))


if __name__ == "__main__":
    main()
