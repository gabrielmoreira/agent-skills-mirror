#!/usr/bin/env python3
"""Tests for expand-series.py.

Run manually (the repo has no Python test runner wired into CI today):

    cd contributed-skills/npc-titan/nonprofit-volunteer-management-records-create/scripts/tests
    python3 -m unittest test_expand_series -v

These lock down the behaviors that a silent regression would corrupt: per-day windows
(the cross-product bug), the uniform-window path, composite date sets (multiple
dateRanges + oneOffDates union), excludeDates in-memory removal, dedup via excludeExisting,
exact-duplicate collapse, the count bound, the >200 batching, and the spec-validation failures.
"""

import datetime as dt
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest


def dt_date(iso):
    return dt.date.fromisoformat(iso)

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "expand-series.py")


def run(spec, args=None):
    """Invoke the script with a spec on stdin; return (returncode, records_or_None, stderr)."""
    proc = subprocess.run(
        [sys.executable, SCRIPT] + (args or []),
        input=json.dumps(spec),
        capture_output=True,
        text=True,
    )
    records = None
    out = proc.stdout.strip()
    # stdout is a tree-import object by default, but a list of file paths under --out-dir.
    if proc.returncode == 0 and out.startswith("{"):
        records = json.loads(out)["records"]
    return proc.returncode, records, proc.stderr


def keys(records):
    return [(r["StartDate"], r["EndDate"], r["StartTime"], r["EndTime"]) for r in records]


class UniformWindows(unittest.TestCase):
    def test_flat_windows_apply_to_every_day(self):
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday", "Thursday"],
            "windows": [{"start": "15:30", "end": "17:30"}],
            "dateRange": {"start": "2026-09-01", "end": "2026-09-14"},  # 2 Tue + 2 Thu
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 4)
        for r in recs:
            self.assertEqual(r["StartTime"], "15:30:00.000Z")
            self.assertEqual(r["EndTime"], "17:30:00.000Z")
            self.assertEqual(r["StartDate"], r["EndDate"])
            self.assertEqual(r["TimeZone"], "America/New_York")

    def test_capacity_and_status_defaults(self):
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentRef": "JobPosition_1",
            "oneOffDates": ["2026-09-06"],
            "windows": [{"start": "12:00", "end": "16:00"}],
            "timeZone": "America/New_York",
            "maximumAttendeesCount": 30,
        })
        self.assertEqual(rc, 0)
        self.assertEqual(recs[0]["JobPositionId"], "@JobPosition_1")
        self.assertEqual(recs[0]["Status"], "Upcoming")
        self.assertEqual(recs[0]["MaximumAttendeesCount"], 30)


class PerDayWindows(unittest.TestCase):
    """The cross-product bug: windows must NOT bleed across days in per-day mode."""

    def test_windows_vary_by_day(self):
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "windowsByDay": {
                "Saturday": [{"start": "08:00", "end": "12:00"}, {"start": "12:00", "end": "17:00"}],
                "Sunday": [{"start": "09:00", "end": "14:00"}],
            },
            "dateRange": {"start": "2026-09-05", "end": "2026-09-13"},  # Sat 5,12 / Sun 6,13
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        got = set(keys(recs))
        # Saturdays get BOTH windows; Sundays get ONLY the 09-14 window.
        self.assertIn(("2026-09-05", "2026-09-05", "08:00:00.000Z", "12:00:00.000Z"), got)
        self.assertIn(("2026-09-05", "2026-09-05", "12:00:00.000Z", "17:00:00.000Z"), got)
        self.assertIn(("2026-09-06", "2026-09-06", "09:00:00.000Z", "14:00:00.000Z"), got)
        # The bug would have put Saturday's windows on Sunday too — assert it does NOT.
        self.assertNotIn(("2026-09-06", "2026-09-06", "08:00:00.000Z", "12:00:00.000Z"), got)
        self.assertNotIn(("2026-09-13", "2026-09-13", "12:00:00.000Z", "17:00:00.000Z"), got)
        self.assertEqual(len(recs), 6)  # 2 Sat x 2 + 2 Sun x 1

    def test_by_day_rejects_redundant_daysofweek(self):
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Saturday"],
            "windowsByDay": {"Saturday": [{"start": "08:00", "end": "12:00"}]},
            "dateRange": {"start": "2026-09-05", "end": "2026-09-13"},
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("daysOfWeek", err)

    def test_explicit_date_without_matching_day_fails(self):
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2026-09-07"],  # a Monday
            "windowsByDay": {"Saturday": [{"start": "08:00", "end": "12:00"}]},
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("windowsByDay", err)


class WindowsFormValidation(unittest.TestCase):
    def test_both_windows_forms_rejected(self):
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "10:00", "end": "12:00"}],
            "windowsByDay": {"Tuesday": [{"start": "10:00", "end": "12:00"}]},
            "dateRange": {"start": "2026-09-01", "end": "2026-09-08"},
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("exactly one", err)

    def test_neither_windows_form_rejected(self):
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "dateRange": {"start": "2026-09-01", "end": "2026-09-08"},
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("exactly one", err)

    def test_window_end_before_start_rejected(self):
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2026-09-06"],
            "windows": [{"start": "17:00", "end": "12:00"}],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("after start", err)

    def test_overlapping_windows_allowed(self):
        # Overlap is intentional-friendly: VM permits overlapping shift records.
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2026-09-06"],
            "windows": [{"start": "08:00", "end": "13:00"}, {"start": "12:00", "end": "17:00"}],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 2)


class Dedup(unittest.TestCase):
    BASE = {
        "entity": "JobPositionShift",
        "parentId": "0PS000000000001",
        "daysOfWeek": ["Tuesday", "Thursday"],
        "windows": [{"start": "15:30", "end": "17:30"}],
        "dateRange": {"start": "2026-09-01", "end": "2026-09-14"},  # Tue 1,8 / Thu 3,10
        "timeZone": "America/New_York",
    }

    def test_excludes_matching_shifts(self):
        spec = dict(self.BASE)
        # Exclude the two Tuesdays (query-style literal times, EndDate omitted).
        spec["excludeExisting"] = [
            {"StartDate": "2026-09-01", "StartTime": "15:30:00.000Z", "EndTime": "17:30:00.000Z"},
            {"StartDate": "2026-09-08", "StartTime": "15:30:00.000Z", "EndTime": "17:30:00.000Z"},
        ]
        rc, recs, err = run(spec)
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 2)  # only the two Thursdays remain
        self.assertEqual({r["StartDate"] for r in recs}, {"2026-09-03", "2026-09-10"})
        self.assertIn("excluded 2", err)

    def test_all_excluded_fails_cleanly(self):
        spec = dict(self.BASE)
        spec["excludeExisting"] = [
            {"StartDate": d, "StartTime": "15:30", "EndTime": "17:30"}
            for d in ("2026-09-01", "2026-09-08", "2026-09-03", "2026-09-10")
        ]
        rc, recs, err = run(spec)
        self.assertEqual(rc, 1)
        self.assertIsNone(recs)
        self.assertIn("already exist", err)
        self.assertIn("nothing to create", err)

    def test_time_only_no_date_match_keeps_all(self):
        # Same times but a date outside the series -> no match, nothing excluded.
        spec = dict(self.BASE)
        spec["excludeExisting"] = [
            {"StartDate": "2025-01-01", "StartTime": "15:30", "EndTime": "17:30"},
        ]
        rc, recs, _ = run(spec)
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 4)


class TimeSlots(unittest.TestCase):
    def test_flat_timeslots(self):
        rc, recs, _ = run({
            "entity": "TimeSlot",
            "parentId": "0OH000000000001",
            "daysOfWeek": ["Monday", "Tuesday"],
            "windows": [{"start": "10:00", "end": "12:00"}, {"start": "14:00", "end": "16:00"}],
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 4)
        self.assertEqual({r["DayOfWeek"] for r in recs}, {"Monday", "Tuesday"})

    def test_per_day_timeslots(self):
        rc, recs, _ = run({
            "entity": "TimeSlot",
            "parentId": "0OH000000000001",
            "windowsByDay": {
                "Monday": [{"start": "09:00", "end": "17:00"}],
                "Saturday": [{"start": "10:00", "end": "14:00"}],
            },
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 2)
        by_day = {r["DayOfWeek"]: (r["StartTime"], r["EndTime"]) for r in recs}
        self.assertEqual(by_day["Monday"], ("09:00:00.000Z", "17:00:00.000Z"))
        self.assertEqual(by_day["Saturday"], ("10:00:00.000Z", "14:00:00.000Z"))

    def test_timeslot_rejects_ref_parent(self):
        rc, _, err = run({
            "entity": "TimeSlot",
            "parentRef": "OperatingHours_1",
            "daysOfWeek": ["Monday"],
            "windows": [{"start": "10:00", "end": "12:00"}],
        })
        self.assertEqual(rc, 1)
        self.assertIn("master-detail", err)


class Batching(unittest.TestCase):
    def test_over_200_requires_out_dir(self):
        spec = {
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "windows": [{"start": "09:00", "end": "12:00"}],
            "dateRange": {"start": "2026-01-01", "end": "2026-12-31"},  # >200 weekdays
            "timeZone": "America/New_York",
        }
        rc, _, err = run(spec)
        self.assertEqual(rc, 1)
        self.assertIn("--out-dir", err)

    def test_out_dir_splits_into_batches(self):
        spec = {
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "windows": [{"start": "09:00", "end": "12:00"}],
            "dateRange": {"start": "2026-01-01", "end": "2026-12-31"},
            "timeZone": "America/New_York",
        }
        with tempfile.TemporaryDirectory() as d:
            rc, _, err = run(spec, ["--out-dir", d])
            self.assertEqual(rc, 0)
            files = sorted(f for f in os.listdir(d) if f.endswith(".json"))
            self.assertGreater(len(files), 1)
            total = 0
            for f in files:
                with open(os.path.join(d, f)) as fh:
                    batch = json.load(fh)["records"]
                self.assertLessEqual(len(batch), 200)
                total += len(batch)
            self.assertEqual(total, 261)  # 261 weekdays that are Mon-Fri in 2026


class CompositeDates(unittest.TestCase):
    """Scenario 1: multiple ranges + one-off dates unioned in a single spec."""

    def test_multiple_ranges_union(self):
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "10:00", "end": "12:00"}],
            "dateRanges": [
                {"start": "2027-06-01", "end": "2027-06-14"},  # Tue 1, 8
                {"start": "2027-09-01", "end": "2027-09-14"},  # Tue 7, 14
            ],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual({r["StartDate"] for r in recs},
                         {"2027-06-01", "2027-06-08", "2027-09-07", "2027-09-14"})

    def test_ranges_plus_one_offs(self):
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "10:00", "end": "12:00"}],
            "dateRange": {"start": "2027-06-01", "end": "2027-06-14"},  # Tue 1, 8
            "oneOffDates": ["2027-08-15"],  # a Sunday — taken as-is, no weekday filter
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual({r["StartDate"] for r in recs},
                         {"2027-06-01", "2027-06-08", "2027-08-15"})

    def test_one_off_inside_range_collapses(self):
        # A one-off that also lands in the range appears once, not twice.
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "10:00", "end": "12:00"}],
            "dateRange": {"start": "2027-06-01", "end": "2027-06-14"},  # Tue 1, 8
            "oneOffDates": ["2027-06-08"],  # already a Tuesday in the range
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 2)

    def test_only_one_offs_needs_no_daysofweek(self):
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "windows": [{"start": "10:00", "end": "12:00"}],
            "oneOffDates": ["2027-06-02", "2027-06-05"],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 2)

    def test_no_dates_at_all_fails(self):
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "10:00", "end": "12:00"}],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("dateRanges", err)

    def test_old_dates_key_guided_to_new_names(self):
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "dates": ["2027-06-01"],
            "windows": [{"start": "10:00", "end": "12:00"}],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("oneOffDates", err)

    def test_dateranges_must_be_list_of_objects(self):
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "10:00", "end": "12:00"}],
            "dateRange": [{"start": "2027-06-01", "end": "2027-06-14"}],  # list under singular key
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("dateRanges", err)  # steered to the list key


class ExcludeDates(unittest.TestCase):
    """Scenario 2: in-memory removal of whole dates before writing."""

    def test_excludes_a_whole_date(self):
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "10:00", "end": "12:00"}, {"start": "14:00", "end": "16:00"}],
            "dateRange": {"start": "2027-06-01", "end": "2027-06-14"},  # Tue 1, 8
            "excludeDates": ["2027-06-08"],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        # Both windows on the 1st survive; the 8th (both windows) is gone.
        self.assertEqual({r["StartDate"] for r in recs}, {"2027-06-01"})
        self.assertEqual(len(recs), 2)

    def test_excluding_all_dates_fails_cleanly(self):
        rc, recs, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "10:00", "end": "12:00"}],
            "dateRange": {"start": "2027-06-01", "end": "2027-06-14"},
            "excludeDates": ["2027-06-01", "2027-06-08"],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIsNone(recs)
        self.assertIn("no shifts produced", err)


class ExactDuplicateCollapse(unittest.TestCase):
    def test_duplicate_window_emits_once(self):
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2027-06-01"],
            "windows": [{"start": "10:00", "end": "12:00"}, {"start": "10:00", "end": "12:00"}],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 1)

    def test_duplicate_day_timeslot_emits_once(self):
        rc, recs, _ = run({
            "entity": "TimeSlot",
            "parentId": "0OH000000000001",
            "daysOfWeek": ["Monday", "Monday"],
            "windows": [{"start": "10:00", "end": "12:00"}],
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 1)


class MultiDayShifts(unittest.TestCase):
    """endDayOffset: a JobPositionShift may cross midnight / span days (EndDate > StartDate)."""

    def test_overnight_offset_one(self):
        # 23:00 -> 03:00 the NEXT day: EndDate = StartDate + 1, end time earlier than start.
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2026-11-18"],
            "windows": [{"start": "23:00", "end": "03:00", "endDayOffset": 1}],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["StartDate"], "2026-11-18")
        self.assertEqual(recs[0]["EndDate"], "2026-11-19")
        self.assertEqual(recs[0]["StartTime"], "23:00:00.000Z")
        self.assertEqual(recs[0]["EndTime"], "03:00:00.000Z")

    def test_multi_day_span_offset_n(self):
        # Tue 02:00 -> Thu 18:00 (2-day span) recurring across a range.
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "02:00", "end": "18:00", "endDayOffset": 2}],
            "dateRange": {"start": "2026-07-01", "end": "2026-07-31"},  # Tue 7,14,21,28
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 4)
        for r in recs:
            sd = dt_date(r["StartDate"])
            ed = dt_date(r["EndDate"])
            self.assertEqual((ed - sd).days, 2)  # every EndDate is StartDate + 2

    def test_end_date_may_pass_range_end(self):
        # dateRange bounds START dates; a spanning shift's EndDate can fall past range.end.
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "daysOfWeek": ["Tuesday"],
            "windows": [{"start": "02:00", "end": "18:00", "endDayOffset": 2}],
            "dateRange": {"start": "2026-09-28", "end": "2026-09-30"},  # only Tue 9-29
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["StartDate"], "2026-09-29")
        self.assertEqual(recs[0]["EndDate"], "2026-10-01")  # past range.end, as intended

    def test_offset_zero_is_default_single_day(self):
        # No endDayOffset -> EndDate == StartDate (regression guard for same-day shifts).
        rc, recs, _ = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2026-11-18"],
            "windows": [{"start": "09:00", "end": "17:00"}],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 0)
        self.assertEqual(recs[0]["StartDate"], recs[0]["EndDate"])

    def test_same_day_end_before_start_still_rejected(self):
        # offset 0 with end <= start is a typo, not an overnight shift — reject it loudly.
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2026-11-18"],
            "windows": [{"start": "23:00", "end": "03:00"}],  # no offset
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("endDayOffset", err)  # steered toward the span opt-in

    def test_negative_offset_rejected(self):
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2026-11-18"],
            "windows": [{"start": "09:00", "end": "17:00", "endDayOffset": -1}],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("endDayOffset", err)

    def test_bool_offset_rejected(self):
        # bool is an int subclass; a stray `true` must not be read as offset 1.
        rc, _, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2026-11-18"],
            "windows": [{"start": "09:00", "end": "17:00", "endDayOffset": True}],
            "timeZone": "America/New_York",
        })
        self.assertEqual(rc, 1)
        self.assertIn("endDayOffset", err)

    def test_timeslot_rejects_offset(self):
        # A TimeSlot is one weekday's window — no EndDate — so endDayOffset is invalid.
        rc, _, err = run({
            "entity": "TimeSlot",
            "parentId": "0OH000000000001",
            "daysOfWeek": ["Monday"],
            "windows": [{"start": "22:00", "end": "02:00", "endDayOffset": 1}],
        })
        self.assertEqual(rc, 1)
        self.assertIn("endDayOffset", err)

    def test_exclude_existing_matches_multi_day_key(self):
        # Dedup key includes EndDate: a spanning shift is excluded by its full key.
        rc, recs, err = run({
            "entity": "JobPositionShift",
            "parentId": "0PS000000000001",
            "oneOffDates": ["2026-11-18", "2026-11-25"],
            "windows": [{"start": "23:00", "end": "03:00", "endDayOffset": 1}],
            "timeZone": "America/New_York",
            "excludeExisting": [
                {"StartDate": "2026-11-18", "EndDate": "2026-11-19",
                 "StartTime": "23:00:00.000Z", "EndTime": "03:00:00.000Z"},
            ],
        })
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["StartDate"], "2026-11-25")
        self.assertIn("excluded 1", err)


SAT = {
    "entity": "JobPositionShift",
    "parentId": "0PS000000000001",
    "daysOfWeek": ["Saturday"],
    "windows": [{"start": "09:00", "end": "12:00"}],
    "timeZone": "America/New_York",
}


class CountBound(unittest.TestCase):
    """``count`` bounds a series by number of dates instead of (or as well as) an end date."""

    def test_count_without_end_date(self):
        rc, recs, _ = run(dict(SAT, dateRange={"start": "2027-06-05"}, count=3))
        self.assertEqual(rc, 0)
        self.assertEqual([r["StartDate"] for r in recs],
                         ["2027-06-05", "2027-06-12", "2027-06-19"])

    def test_count_stops_before_end_date(self):
        rc, recs, _ = run(dict(SAT, dateRange={"start": "2027-06-05", "end": "2027-08-28"},
                               count=2))
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 2)

    def test_end_date_stops_before_count(self):
        rc, recs, _ = run(dict(SAT, dateRange={"start": "2027-06-05", "end": "2027-06-12"},
                               count=10))
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 2)

    def test_count_is_dates_not_shifts(self):
        spec = dict(SAT, dateRange={"start": "2027-06-05"}, count=2,
                    windows=[{"start": "09:00", "end": "12:00"},
                             {"start": "13:00", "end": "16:00"}])
        rc, recs, _ = run(spec)
        self.assertEqual(rc, 0)
        self.assertEqual(len(recs), 4)  # 2 dates x 2 windows
        self.assertEqual(sorted({r["StartDate"] for r in recs}), ["2027-06-05", "2027-06-12"])

    def test_excluded_dates_do_not_use_up_the_count(self):
        rc, recs, _ = run(dict(SAT, dateRange={"start": "2027-06-05"}, count=3,
                               excludeDates=["2027-06-12"]))
        self.assertEqual(rc, 0)
        self.assertEqual([r["StartDate"] for r in recs],
                         ["2027-06-05", "2027-06-19", "2027-06-26"])

    def test_count_applies_before_exclude_existing(self):
        rc, recs, err = run(dict(SAT, dateRange={"start": "2027-06-05"}, count=3,
                                 excludeExisting=[{"StartDate": "2027-06-05",
                                                   "StartTime": "09:00:00.000Z",
                                                   "EndTime": "12:00:00.000Z"}]))
        self.assertEqual(rc, 0)
        self.assertEqual([r["StartDate"] for r in recs], ["2027-06-12", "2027-06-19"])
        self.assertIn("excluded 1", err)

    def test_count_with_one_off_dates(self):
        spec = dict(SAT, oneOffDates=["2027-07-01", "2027-07-02", "2027-07-03"], count=2)
        del spec["daysOfWeek"]
        rc, recs, _ = run(spec)
        self.assertEqual(rc, 0)
        self.assertEqual([r["StartDate"] for r in recs], ["2027-07-01", "2027-07-02"])

    def test_missing_end_without_count_fails(self):
        rc, _, err = run(dict(SAT, dateRange={"start": "2027-06-05"}))
        self.assertEqual(rc, 1)
        self.assertIn("end date or a count", err)

    def test_invalid_count_rejected(self):
        for bad in (0, -1, 2.5, "3", True):
            rc, _, err = run(dict(SAT, dateRange={"start": "2027-06-05"}, count=bad))
            self.assertEqual(rc, 1, bad)
            self.assertIn("count must be an integer", err)

    def test_timeslot_rejects_count(self):
        rc, _, err = run({
            "entity": "TimeSlot",
            "parentId": "0OH000000000001",
            "daysOfWeek": ["Monday"],
            "windows": [{"start": "09:00", "end": "17:00"}],
            "count": 3,
        })
        self.assertEqual(rc, 1)
        self.assertIn("count", err)

    def test_status_defaults_to_upcoming(self):
        rc, recs, _ = run(dict(SAT, dateRange={"start": "2027-06-05"}, count=1))
        self.assertEqual(rc, 0)
        self.assertEqual(recs[0]["Status"], "Upcoming")

    def test_status_passes_through(self):
        rc, recs, _ = run(dict(SAT, dateRange={"start": "2027-06-05"}, count=1,
                               status="In Progress"))
        self.assertEqual(rc, 0)
        self.assertEqual(recs[0]["Status"], "In Progress")


class SpecGuards(unittest.TestCase):
    def test_non_object_json_fails_cleanly(self):
        # A top-level array/scalar must fail() with a message, not crash with a traceback.
        for bad in ("[]", "42", "\"x\""):
            proc = subprocess.run(
                [sys.executable, SCRIPT], input=bad, capture_output=True, text=True,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("JSON object", proc.stderr)
            self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
