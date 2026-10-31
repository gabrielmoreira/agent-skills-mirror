"""Fetch STDM conversations with read-only anonymous Apex (bt_fetch.py); nothing is deployed.

Python writes every query. The Apex generated around them only runs them, with
ConnectApi.CdpQuery.queryAnsiSqlV2 (nextBatchAnsiSqlV2 for later result pages), and prints each
page as one debug line, `STDM_RESULT_<query>_<page>:{"rows": [...], "more": <bool>}`, then
`STDM_RESULT_end:{}`. check_read_only() vets each script before it runs.

The rest happens here, where it is tested:
- the agent filter (participant API name, else the agent's planner ids) fails loudly when it
  matches nothing, as OfflineExperimentationService.findSessions now does (it ran unfiltered);
- candidates are the sessions started in the window with at least one TURN interaction, read
  in keyset pages;
- selection: channels (by default all but Builder*, Agent Builder's test traffic), excluded
  sessions, the split, then a salted-hash sample (or the most recent) up to the cap;
- details come in batches of a few sessions, halved when a batch hits an Apex limit or the
  20 MB debug log;
- assembly mirrors getMultipleConversationDetails: the same ConversationData fields, NOT_SET and
  blank values as null, SESSION_END interactions skipped, the same message-type inference. One
  deliberate difference: duration_ms is exact, where the class's timestamp parse drops milliseconds.

The queries name the DMOs and fields of the default data space (ssot__AiAgentSession__dlm,
ssot__Id__c). A data space that names them its own way takes a names map (StdmNames,
bt.stdm_names/1, bt_fetch.py --stdm-names); without one, nothing is renamed.
"""

import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone

from . import SCHEMA_FETCH, stdm
from .redact import redact
from .splits import DEFAULT_SALT as SPLIT_SALT
from .splits import session_split

SESSION = '"ssot__AiAgentSession__dlm"'
PARTICIPANT = '"ssot__AiAgentSessionParticipant__dlm"'
INTERACTION = '"ssot__AiAgentInteraction__dlm"'
MESSAGE = '"ssot__AiAgentInteractionMessage__dlm"'
STEP = '"ssot__AiAgentInteractionStep__dlm"'
PROBE_DMOS = {"session": SESSION, "participant": PARTICIPANT, "interaction": INTERACTION, "message": MESSAGE,
              "step": STEP, "generation": '"GenAIGeneration__dlm"', "gateway": '"GenAIGatewayRequest__dlm"'}
REQUIRED_DMOS = ("session", "participant", "interaction", "message", "step")  # the others: LLM step details only
STEP_COLUMNS = ("ssot__Id__c", "ssot__AiAgentInteractionId__c", "ssot__AiAgentInteractionStepType__c",
                "ssot__Name__c", "ssot__StartTimestamp__c", "ssot__EndTimestamp__c", "ssot__InputValueText__c",
                "ssot__OutputValueText__c", "ssot__ErrorMessageText__c", "ssot__PreStepVariableText__c",
                "ssot__PostStepVariableText__c", "ssot__GenerationId__c", "ssot__GenAiGatewayRequestId__c")

CANDIDATE_PAGE = 2000     # rows per candidates query; the next one starts after the last session id
MAX_CANDIDATES = 20000
MAX_PAGES = 50            # result pages the Apex follows per query
BATCH_SIZE = 3            # sessions per details run (the Apex heap is 6 MB)
MAX_SESSIONS = 50
SAMPLE_SALT = "bt-sample/1"
BUILDER_PREFIX = "builder"  # 'Builder', 'Builder: Voice Preview': test traffic from Agent Builder
APEX_TIMEOUT = 600
END = "STDM_RESULT_end"

_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,79}\Z")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,79}\Z")
_ORG = re.compile(r"[A-Za-z0-9_.@+][A-Za-z0-9_.@+-]{0,119}\Z")
_TIME = re.compile(r"(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,9}))?)?)?"
                   r"\s*(Z|UTC|GMT|[+-]\d{2}:?\d{2})?\Z", re.I)
# Errors a smaller batch can avoid: Apex limits, and a debug log cut at 20 MB.
_TOO_BIG = re.compile(r"heap size|cpu time|too many|exceed|probably truncated|pages missing|end marker", re.I)


class FetchError(Exception):
    pass


class BatchTooBig(FetchError):
    """The run hit an Apex limit or the debug-log cap: retry with fewer sessions."""


class ReadOnlyError(FetchError):
    pass


# --- literals ---------------------------------------------------------------------------------

def check_name(value, what="agent API name"):
    if not isinstance(value, str) or not _NAME.match(value):
        raise FetchError(f"not an {what} (a letter, then letters, digits or _): {value!r}")
    return value


def check_ids(ids, what="session id"):
    ids = list(ids)
    bad = sum(1 for i in ids if not isinstance(i, str) or not _ID.match(i))
    if bad:  # not echoed: ids name sessions
        raise FetchError(f"{bad} {what}s hold characters other than letters, digits, _ . : -")
    return ids


def check_org(value):
    if not isinstance(value, str) or not _ORG.match(value):
        raise FetchError(f"not an org alias or username: {value!r}")
    return value


def _lit(value):
    """A SQL string literal of an already-validated value."""
    if "'" in value or "\\" in value:
        raise FetchError("a quote or backslash in a query value")
    return "'" + value + "'"


def _in(ids, what="session id"):
    ids = check_ids(ids, what)
    if not ids:
        raise FetchError(f"no {what}s for an IN list")
    return "(" + ", ".join(_lit(i) for i in ids) + ")"


# --- timestamps -------------------------------------------------------------------------------

def parse_time(value):
    """An aware UTC datetime from an STDM timestamp ('2026-10-01 17:23:45.123 UTC'), ISO 8601
    with T, Z or an offset, or epoch milliseconds; None for None, blank or unparseable."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, timezone.utc)
    text = str(value).strip()
    if text.isdigit():
        return datetime.fromtimestamp(int(text) / 1000, timezone.utc)
    m = _TIME.match(text)
    if not m:
        return None
    y, mo, d, hh, mi, ss, frac, tz = m.groups()
    try:
        dt = datetime(int(y), int(mo), int(d), int(hh or 0), int(mi or 0), int(ss or 0),
                      int((frac or "0")[:6].ljust(6, "0")))
    except ValueError:
        return None
    if tz and tz.upper() not in ("Z", "UTC", "GMT"):
        digits = tz[1:].replace(":", "")
        offset = timedelta(hours=int(digits[:2]), minutes=int(digits[2:]))
        dt = dt - offset if tz[0] == "+" else dt + offset
    return dt.replace(tzinfo=timezone.utc)


def window_bound(text, end=False):
    """--start / --end as the literal the queries compare with, 'YYYY-MM-DDTHH:MM:SS.fffZ' (UTC).
    A date alone starts at 00:00:00.000, or as --end runs to 23:59:59.999."""
    text = (text or "").strip()
    dt = parse_time(text) if not text.isdigit() else None
    if dt is None:
        raise FetchError(f"not a date or ISO 8601 time: {text!r}")
    if end and re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        dt += timedelta(days=1, milliseconds=-1)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + "%03dZ" % (dt.microsecond // 1000)


def duration_ms(start, end):
    a, b = parse_time(start), parse_time(end)
    if a is None or b is None:
        return None
    return (b - a) // timedelta(milliseconds=1)


# --- queries ----------------------------------------------------------------------------------

_SESSION_COLS = ("s.ssot__Id__c, s.ssot__StartTimestamp__c, s.ssot__EndTimestamp__c, "
                 "s.ssot__AiAgentChannelType__c, s.ssot__AiAgentSessionEndType__c")


def candidates_sql(start, end, agent=None, participant_ids=None, after=None, limit=None):
    """Sessions of the agent started in [start, end] with at least one TURN, by session id, from
    after (exclusive), limit (default CANDIDATE_PAGE) rows; the last column counts their TURN interactions."""
    if participant_ids is not None:
        who = "p.ssot__ParticipantId__c IN " + _in(participant_ids, "planner id")
    else:
        who = "p.ssot__AiAgentApiName__c = " + _lit(check_name(agent))
    return ("SELECT " + _SESSION_COLS + ", COUNT(DISTINCT i.ssot__Id__c) FROM " + SESSION + " s"
            " JOIN " + PARTICIPANT + " p ON p.ssot__AiAgentSessionId__c = s.ssot__Id__c"
            " JOIN " + INTERACTION + " i ON i.ssot__AiAgentSessionId__c = s.ssot__Id__c"
            " WHERE " + who + " AND i.ssot__AiAgentInteractionType__c = 'TURN'"
            " AND s.ssot__StartTimestamp__c >= " + _lit(start) + " AND s.ssot__StartTimestamp__c <= " + _lit(end)
            + ("" if after is None else " AND s.ssot__Id__c > " + _lit(check_ids([after])[0]))
            + " GROUP BY " + _SESSION_COLS + " ORDER BY s.ssot__Id__c LIMIT "
            + str(int(CANDIDATE_PAGE if limit is None else limit)))


def details_sql(session_ids):
    """The four queries of getConversationDetails for a batch of sessions; messages and steps are
    joined to their interaction, so one run needs no interaction ids. Ties are ordered by id."""
    ids = _in(session_ids)
    return {
        "sessions": ("SELECT ssot__Id__c, ssot__StartTimestamp__c, ssot__EndTimestamp__c, "
                     "ssot__AiAgentChannelType__c, ssot__AiAgentSessionEndType__c, ssot__VariableText__c FROM "
                     + SESSION + " WHERE ssot__Id__c IN " + ids),
        "interactions": ("SELECT ssot__Id__c, ssot__AiAgentSessionId__c, ssot__TopicApiName__c, "
                         "ssot__AiAgentInteractionType__c, ssot__StartTimestamp__c, ssot__EndTimestamp__c, "
                         "ssot__TelemetryTraceId__c FROM " + INTERACTION + " WHERE ssot__AiAgentSessionId__c IN " + ids
                         + " ORDER BY ssot__StartTimestamp__c, ssot__Id__c"),
        "messages": ("SELECT m.ssot__Id__c, m.ssot__AiAgentInteractionId__c, m.ssot__AiAgentInteractionMessageType__c, "
                     "m.ssot__ContentText__c, m.ssot__MessageSentTimestamp__c FROM " + MESSAGE + " m JOIN "
                     + INTERACTION + " i ON i.ssot__Id__c = m.ssot__AiAgentInteractionId__c"
                     " WHERE i.ssot__AiAgentSessionId__c IN " + ids
                     + " ORDER BY m.ssot__MessageSentTimestamp__c, m.ssot__Id__c"),
        "steps": ("SELECT " + ", ".join("st." + c for c in STEP_COLUMNS) + " FROM " + STEP + " st JOIN "
                  + INTERACTION + " i ON i.ssot__Id__c = st.ssot__AiAgentInteractionId__c"
                  " WHERE i.ssot__AiAgentSessionId__c IN " + ids
                  + " ORDER BY st.ssot__StartTimestamp__c, st.ssot__Id__c"),
    }


def count_sql(table, where=None):
    return "SELECT COUNT(*) FROM " + table + ("" if where is None else " WHERE " + where)


def agents_in_window_sql(start, end):
    return ("SELECT p.ssot__AiAgentApiName__c, COUNT(DISTINCT s.ssot__Id__c) FROM " + SESSION + " s JOIN "
            + PARTICIPANT + " p ON p.ssot__AiAgentSessionId__c = s.ssot__Id__c"
            " WHERE s.ssot__StartTimestamp__c >= " + _lit(start) + " AND s.ssot__StartTimestamp__c <= " + _lit(end)
            + " GROUP BY p.ssot__AiAgentApiName__c")


# --- a data space's own names -----------------------------------------------------------------

SCHEMA_NAMES = "bt.stdm_names/1"
NO_MATCH = "bt_probe_none"  # a key no row has: the query-shape checks read nothing
SHAPES = {"qcands": "candidates by API name", "qbyid": "candidates by planner id", "qagents": "agents in a window",
          "qsessions": "session details", "qinteractions": "interactions", "qmessages": "messages", "qsteps": "steps"}
_NAMES_KEYS = frozenset(("schema", "about", "dmo_prefix", "field_prefix", "dmos", "fields", "user_agent"))
_PREFIX = re.compile(r"(?:[A-Za-z][A-Za-z0-9_]{0,39})?\Z")
_USER_AGENT = re.compile(r"[A-Za-z][A-Za-z0-9_.-]{0,39}\Z")
_DMO_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,74}__dlm\Z")
_FIELD_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,76}__c\Z")
_IDENT = re.compile(r'"([A-Za-z][A-Za-z0-9_]*)"|\b([A-Za-z][A-Za-z0-9_]*__c)\b')  # a quoted DMO, or a field


def _outside_literals(sql, fn):
    """sql with fn applied to the text between its string literals (_lit's hold no quote)."""
    return "".join(p if i % 2 else fn(p) for i, p in enumerate(re.split(r"('[^']*')", sql)))


def shape_queries():
    """Every query shape a fetch runs, with keys no row has: each reads 0 rows, or fails on a name
    the data space does not have."""
    start, end = window_bound("1970-01-01"), window_bound("1970-01-01", end=True)
    queries = {"qcands": candidates_sql(start, end, agent=NO_MATCH),
               "qbyid": candidates_sql(start, end, participant_ids=[NO_MATCH]),
               "qagents": agents_in_window_sql(start, end)}
    queries.update(("q" + name, sql) for name, sql in details_sql([NO_MATCH]).items())
    return queries


def default_names():
    """(the DMOs, the fields) the queries name, as the default data space names them."""
    fields = set()
    for sql in shape_queries().values():
        for text in re.split(r"'[^']*'", sql):  # the text between the literals
            fields.update(m.group(2) for m in _IDENT.finditer(text) if m.group(2))
    return [table.strip('"') for table in PROBE_DMOS.values()], sorted(fields)


class StdmNames:
    """A data space's own names for the STDM DMOs and their fields, a bt.stdm_names/1 map:
    dmo_prefix and field_prefix replace the ssot__ of the default names (default: ssot__ itself),
    dmos and fields rename single ones, keyed by the default name, and user_agent, when given, is
    the CdpQueryInput.userAgent of every query. GenAIGeneration__dlm and GenAIGatewayRequest__dlm
    have no ssot__: only dmos renames them."""

    def __init__(self, data, source="", sha256=""):
        if not isinstance(data, dict):
            raise FetchError("a names map is a JSON object")
        unknown = sorted(set(data) - _NAMES_KEYS)
        if unknown:
            raise FetchError("not a key of a names map: " + ", ".join(map(repr, unknown[:5])))
        if data.get("schema") != SCHEMA_NAMES:
            raise FetchError(f"not a {SCHEMA_NAMES} names map (schema {data.get('schema')!r})")
        self.source, self.sha256 = source, sha256
        self.about = data.get("about") or ""
        if not isinstance(self.about, str) or len(self.about) > 300 or not self.about.isprintable():
            raise FetchError("about: one line of text, at most 300 characters")
        prefix = {}
        for key in ("dmo_prefix", "field_prefix"):
            prefix[key] = data.get(key, "ssot__")
            if not isinstance(prefix[key], str) or not _PREFIX.match(prefix[key]):
                raise FetchError(f"{key}: empty, or a letter, then letters, digits or _: {prefix[key]!r}")
        self.user_agent = data.get("user_agent")
        if self.user_agent is not None and not (isinstance(self.user_agent, str) and _USER_AGENT.match(self.user_agent)):
            raise FetchError(f"user_agent: a letter, then letters, digits or _ . -: {self.user_agent!r}")
        dmos, fields = default_names()
        self._dmos = self._renamed(data.get("dmos"), "dmos", dmos, prefix["dmo_prefix"], _DMO_NAME)
        self._fields = self._renamed(data.get("fields"), "fields", fields, prefix["field_prefix"], _FIELD_NAME)

    @staticmethod
    def _renamed(given, key, defaults, prefix, shape):
        """{default name: this data space's} for each default name; refuses a name that cannot be
        one, a key that is no default name, and two default names given one name."""
        given = {} if given is None else given
        if not isinstance(given, dict):
            raise FetchError(f"{key}: an object of default name -> name")
        unknown = sorted(set(given) - set(defaults))
        if unknown:
            raise FetchError(f"{key}: not a name the queries use: " + ", ".join(map(repr, unknown[:5])))
        out = {}
        for name in defaults:
            new = given.get(name)
            if new is None:
                new = prefix + name[len("ssot__"):] if name.startswith("ssot__") else name
            if not isinstance(new, str) or not shape.match(new):
                raise FetchError(f"{key}: {name} -> {new!r}, not a {'DMO' if key == 'dmos' else 'field'} name")
            out[name] = new
        twice = sorted(n for n, c in Counter(out.values()).items() if c > 1)
        if twice:
            raise FetchError(f"{key}: two names map to {twice[0]}")
        return out

    def dmo(self, name):
        return self._dmos.get(name, name)

    def field(self, name):
        return self._fields.get(name, name)

    def sql(self, sql):
        """sql in this data space's names: its quoted DMOs and its fields, outside the literals."""
        def rename(m):
            return '"' + self.dmo(m.group(1)) + '"' if m.group(1) else self.field(m.group(2))
        return _outside_literals(sql, lambda text: _IDENT.sub(rename, text))

    def manifest(self):
        return {"file": self.source, "sha256": self.sha256, "about": self.about}


def load_names(path):
    """The StdmNames of a bt.stdm_names/1 file (--stdm-names)."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, ValueError) as e:
        raise FetchError(f"--stdm-names {path}: {e}") from None
    try:
        return StdmNames(data, os.path.basename(path), hashlib.sha256(raw).hexdigest()[:16])
    except FetchError as e:
        raise FetchError(f"--stdm-names {path}: {e}") from None


# --- Apex -------------------------------------------------------------------------------------

def apex_literal(text):
    return "'" + (text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
                  .replace("\r", "\\r").replace("\t", "\\t")) + "'"


_HEAD = ("// Generated by bt_fetch.py. Read-only: runs the SELECT queries below on Data Cloud and\n"
         "// prints the result rows as debug lines. No DML, no callouts, nothing deployed.\n")

_PAGES = """\
for (String name : queries.keySet()) {
    ConnectApi.CdpQueryInput input = new ConnectApi.CdpQueryInput();
    input.sql = queries.get(name);
    ConnectApi.CdpQueryOutputV2 out = ConnectApi.CdpQuery.queryAnsiSqlV2(input, dataspace);
    Integer page = 0;
    while (true) {
        List<List<Object>> rows = new List<List<Object>>();
        if (out.data != null) {
            for (ConnectApi.CdpQueryV2Row row : out.data) {
                rows.add(row.rowData);
            }
        }
        Boolean more = String.isNotBlank(out.nextBatchId);
        System.debug('STDM_RESULT_' + name + '_' + page + ':' + JSON.serialize(new Map<String, Object>{'rows' => rows, 'more' => more}));
        if (!more || page + 1 >= maxPages) {
            break;
        }
        out = ConnectApi.CdpQuery.nextBatchAnsiSqlV2(out.nextBatchId, dataspace);
        page++;
    }
}
System.debug('STDM_RESULT_end:{}');
"""

_PROBE = """\
for (String name : queries.keySet()) {
    ConnectApi.CdpQueryInput input = new ConnectApi.CdpQueryInput();
    input.sql = queries.get(name);
    try {
        ConnectApi.CdpQueryOutputV2 out = ConnectApi.CdpQuery.queryAnsiSqlV2(input, dataspace);
        List<List<Object>> rows = new List<List<Object>>();
        if (out.data != null) {
            for (ConnectApi.CdpQueryV2Row row : out.data) {
                rows.add(row.rowData);
            }
        }
        System.debug('STDM_RESULT_' + name + '_0:' + JSON.serialize(new Map<String, Object>{'rows' => rows, 'more' => false}));
    } catch (Exception e) {
        System.debug('STDM_RESULT_' + name + '_0:' + JSON.serialize(new Map<String, Object>{'error' => e.getMessage()}));
    }
}
System.debug('STDM_RESULT_end:{}');
"""

_PLANNERS = """\
List<GenAiPlannerDefinition> planners = [SELECT Id, DeveloperName, MasterLabel FROM GenAiPlannerDefinition WHERE DeveloperName LIKE :pattern OR MasterLabel = :agent LIMIT 200];
System.debug('STDM_RESULT_planners:' + JSON.serialize(planners));
System.debug('STDM_RESULT_end:{}');
"""


_SET_SQL = "    input.sql = queries.get(name);\n"


def query_script(queries, dataspace, probe=False, names=None):
    """Anonymous Apex running {name: sql}: every result page (or, probe: the first page, or the error).
    With names (StdmNames), the SQL is in the data space's names, and the map's userAgent is set."""
    lines = [_HEAD, "String dataspace = " + apex_literal(check_name(dataspace, "data space name")) + ";",
             "Integer maxPages = " + str(MAX_PAGES) + ";"]
    body = _PROBE if probe else _PAGES
    if names is not None and names.user_agent:
        lines.append("String userAgent = " + apex_literal(names.user_agent) + ";")
        body = body.replace(_SET_SQL, _SET_SQL + "    input.userAgent = userAgent;\n")
    lines.append("Map<String, String> queries = new Map<String, String>();")
    for name, sql in queries.items():
        if not re.fullmatch(r"[a-z]+", name):
            raise FetchError(f"query name {name!r}: lowercase letters only")
        if names is not None:
            sql = names.sql(sql)
        if not re.match(r"SELECT ", sql) or ";" in sql:
            raise FetchError(f"query {name}: one SELECT statement only")
        lines.append("queries.put(" + apex_literal(name) + ", " + apex_literal(sql) + ");")
    return "\n".join(lines) + "\n" + body


def planner_script(agent):
    """Anonymous Apex listing the GenAiPlannerDefinitions named like the agent (SOQL, read-only)."""
    check_name(agent)
    return (_HEAD + "String agent = " + apex_literal(agent) + ";\nString pattern = agent + " + apex_literal("%")
            + ";\n" + _PLANNERS)


# Every word the generated scripts use outside string literals. A script with any other word
# (insert, update, delete, Database, Http, a custom class...) is refused before it runs.
READ_ONLY_WORDS = frozenset("""
    string integer boolean object list map new for while if break true false null try catch exception e
    connectapi cdpqueryinput cdpquery queryansisqlv2 nextbatchansisqlv2 cdpqueryoutputv2 cdpqueryv2row
    sql data rowdata nextbatchid json serialize system debug isnotblank getmessage put get keyset add
    dataspace maxpages queries name input out page rows row more agent pattern planners useragent
    select id developername masterlabel from genaiplannerdefinition where like or limit
""".split())
_WRITE_SQL = re.compile(r"\b(insert|update|upsert|delete|undelete|merge|drop|create|alter|truncate|grant)\b", re.I)


def _lex(apex):
    """(the code with string literals emptied and comments removed, [string literal contents])."""
    code, literals, i, n = [], [], 0, len(apex)
    while i < n:
        c = apex[i]
        if c == "'":
            j, buf = i + 1, []
            while j < n and apex[j] != "'":
                if apex[j] == "\n":
                    raise ReadOnlyError("a string literal runs past the end of its line")
                if apex[j] == "\\" and j + 1 < n:
                    buf.append({"n": "\n", "r": "\r", "t": "\t"}.get(apex[j + 1], apex[j + 1]))
                    j += 2
                else:
                    buf.append(apex[j])
                    j += 1
            if j >= n:
                raise ReadOnlyError("an unterminated string literal")
            literals.append("".join(buf))
            code.append("''")
            i = j + 1
        elif apex.startswith("//", i):
            j = apex.find("\n", i)
            i = n if j < 0 else j
        elif apex.startswith("/*", i):
            j = apex.find("*/", i + 2)
            if j < 0:
                raise ReadOnlyError("an unterminated comment")
            code.append(" ")
            i = j + 2
        else:
            code.append(c)
            i += 1
    return "".join(code), literals


def check_read_only(apex):
    """Refuse a script that could do anything but read: every word outside string literals must
    be on READ_ONLY_WORDS, every SQL literal must be one SELECT, and no literal may hold a
    write statement keyword."""
    code, literals = _lex(apex)
    words = {w.lower() for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", code)}
    extra = sorted(words - READ_ONLY_WORDS)
    if extra:
        raise ReadOnlyError("not on the read-only word list: " + ", ".join(extra[:10]))
    for lit in literals:
        bad = _WRITE_SQL.search(lit)
        if bad:
            raise ReadOnlyError(f"a string literal holds {bad.group(1)!r}")
        if re.match(r"\s*(select|with|call|exec)\b", lit, re.I) and (not lit.startswith("SELECT ") or ";" in lit):
            raise ReadOnlyError("a query literal that is not one SELECT statement")


# --- running ----------------------------------------------------------------------------------

def sf_runner(argv, timeout):
    """Run the sf CLI (no shell): its --json output, on stdout (stderr if stdout is empty)."""
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    return proc.stdout if proc.stdout.strip() else proc.stderr


_UUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
_SFID = re.compile(r"\b(?=[A-Za-z0-9]*\d)[A-Za-z0-9]{15}(?:[A-Za-z0-9]{3})?\b")
_TENANT = re.compile(r"\b(a360|core)/[\w./-]+")


def mask_ids(text):
    """Error text with session/record ids and tenant ids masked, for printing."""
    text = _UUID.sub("<id>", redact(text))
    text = _TENANT.sub(lambda m: m.group(1) + "/<tenant>", text)
    return _SFID.sub("<id>", text)


def collect_pages(found, names):
    """{name: rows} from the {marker: payload} of a run of query_script: each query's pages, in
    order, all present, the last without more."""
    if END not in found:
        raise BatchTooBig("the Apex log has no end marker (the run stopped early, or the log was cut)")
    pages = {}
    for marker, payload in found.items():
        if marker == END or not marker or not marker.startswith("STDM_RESULT_"):
            continue
        name, _, page = marker[len("STDM_RESULT_"):].rpartition("_")
        if not page.isdigit():
            continue
        if not isinstance(payload, dict):
            raise FetchError(f"query {name}: a result page that is not an object")
        if "error" in payload:
            raise FetchError(f"query {name}: {mask_ids(str(payload['error']))[:300]}")
        if not isinstance(payload.get("rows"), list):
            raise FetchError(f"query {name}: a result page without rows")
        pages.setdefault(name, {})[int(page)] = payload
    out = {}
    for name in names:
        got = pages.get(name, {})
        last = got.get(len(got) - 1, {})
        # a page the log lost, the last one too: the Apex stops before the end only at maxPages
        if not got or sorted(got) != list(range(len(got))) or (last.get("more") and len(got) < MAX_PAGES):
            raise BatchTooBig(f"query {name}: result pages missing from the Apex log (cut at 20 MB?)")
        if last.get("more"):
            raise FetchError(f"query {name}: more than {MAX_PAGES} result pages; narrow the window or "
                             "lower --batch-size")
        out[name] = [row for i in range(len(got)) for row in got[i]["rows"]]
    return out


class Fetcher:
    """Runs generated, read-only Apex in an org: `sf apex run --json --file <script>`. Each script
    is kept in apex_dir (created 0700), numbered in run order; those of details hold session ids.
    names: the data space's StdmNames, or None for the default names."""

    def __init__(self, org, apex_dir, dataspace="default", runner=None, timeout=APEX_TIMEOUT, names=None):
        self.org = check_org(org)
        self.dataspace = check_name(dataspace, "data space name")
        self.apex_dir = apex_dir
        self.runner = runner or sf_runner
        self.timeout = timeout
        self.names = names
        self.runs = 0

    def run(self, apex, label):
        """{marker: payload} of one Apex run; BatchTooBig when a smaller batch could pass."""
        check_read_only(apex)
        self.runs += 1
        path = os.path.join(_private_dir(self.apex_dir), "%03d_%s.apex" % (self.runs, label))
        write_private(path, apex)
        argv = ["sf", "apex", "run", "--json", "--file", path, "--target-org", self.org]
        try:
            out = self.runner(argv, self.timeout)
        except subprocess.TimeoutExpired:
            raise BatchTooBig(f"{label}: sf apex run exceeded {self.timeout}s") from None
        except OSError as e:
            raise FetchError(f"could not run the sf CLI: {e}") from None
        try:
            data = json.loads(out or "")
        except ValueError:
            raise FetchError(f"{label}: sf apex run printed no JSON: {mask_ids((out or '').strip()[-300:])}") from None
        try:
            found = stdm.parse_sf_output(data, label)
        except stdm.StdmError as e:
            msg = mask_ids(str(e))
            raise (BatchTooBig if _TOO_BIG.search(msg) else FetchError)(msg) from None
        if found is None:
            raise FetchError(f"{label}: not the output of sf apex run --json")
        return found

    def query(self, queries, label):
        return collect_pages(self.run(query_script(queries, self.dataspace, names=self.names), label), queries)

    def candidates(self, start, end, agent=None, participant_ids=None):
        rows, after = [], None
        while True:
            page = self.query({"cands": candidates_sql(start, end, agent, participant_ids, after)}, "candidates")["cands"]
            rows.extend(page)
            if len(rows) > MAX_CANDIDATES:
                raise FetchError(f"more than {MAX_CANDIDATES} candidate sessions in the window; narrow it")
            if len(page) < CANDIDATE_PAGE:
                break
            after = col(page[-1], 0)
        seen, out = set(), []
        for r in rows:
            c = candidate(r)
            if c["session_id"] and c["session_id"] not in seen:  # a session's rows can repeat in the DMO
                seen.add(c["session_id"])
                out.append(c)
        return out

    def planners(self, agent):
        """(planners that are the agent: DeveloperName == agent or agent_<n> / agent_v<n>, or
        MasterLabel == agent; every DeveloperName the LIKE matched)."""
        rows = self.run(planner_script(agent), "planners").get("STDM_RESULT_planners")
        if not isinstance(rows, list):
            raise FetchError("planners: no result line")
        rows = [r for r in rows if isinstance(r, dict) and r.get("Id")]
        version = re.compile(re.escape(agent) + r"_v?\d+\Z")
        mine = [r for r in rows if r.get("DeveloperName") == agent or r.get("MasterLabel") == agent
                or version.match(r.get("DeveloperName") or "")]
        return mine, sorted({r.get("DeveloperName") or "?" for r in rows})

    def details(self, session_ids):
        return assemble(session_ids, self.query(details_sql(session_ids), "details"))


# --- rows -> records --------------------------------------------------------------------------

def col(row, i):
    """A column as the class's col(): null stays null, text as is, other values as text."""
    if row is None or i >= len(row) or row[i] is None:
        return None
    v = row[i]
    if isinstance(v, str):
        return v
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v)
    return str(v)


def not_set(value):
    """The class's notSet(): blank or 'NOT_SET' is null (Apex compares strings ignoring case)."""
    return None if value is None or not value.strip() or value.upper() == "NOT_SET" else value


def candidate(row):
    turns = col(row, 5)
    return {"session_id": col(row, 0), "start_time": col(row, 1), "end_time": col(row, 2), "channel": col(row, 3),
            "end_type": not_set(col(row, 4)), "turns": int(float(turns)) if turns else 0}


def session_summary(c):
    """A SessionSummary of findSessions, with an exact duration."""
    return {"session_id": c["session_id"], "start_time": c["start_time"], "end_time": c["end_time"],
            "channel": c["channel"], "duration_ms": duration_ms(c["start_time"], c["end_time"]),
            "end_type": c["end_type"]}


def infer_message_types(messages):
    """getConversationDetails' fill-in of null message types: all null alternate Input/Output from
    the first; otherwise each null is the opposite of the one before, and a first null is Input."""
    types = [m["message_type"] for m in messages]
    if None not in types:
        return
    if all(t is None for t in types):
        for i, m in enumerate(messages):
            m["message_type"] = "Input" if i % 2 == 0 else "Output"
        return
    for i, m in enumerate(messages):
        if m["message_type"] is None:
            if i > 0 and messages[i - 1]["message_type"] is not None:
                m["message_type"] = "Output" if messages[i - 1]["message_type"] == "Input" else "Input"
            elif i == 0:
                m["message_type"] = "Input"


def assemble(session_ids, rows):
    """ConversationData for each session id, in order, from the rows of details_sql()."""
    header = {}
    for r in rows["sessions"]:
        header.setdefault(col(r, 0), r)  # the class reads the first row
    convos, by_session, turn_of, convo_of = [], {}, {}, {}
    for sid in session_ids:
        c = {"session_id": sid, "start_time": None, "end_time": None, "channel": None, "duration_ms": None,
             "end_type": None, "session_variables": None, "turn_count": 0, "action_error_count": 0, "turns": []}
        r = header.get(sid)
        if r is not None:
            c.update(start_time=col(r, 1), end_time=col(r, 2), channel=col(r, 3), end_type=not_set(col(r, 4)),
                     session_variables=not_set(col(r, 5)))
            c["duration_ms"] = duration_ms(c["start_time"], c["end_time"])
        convos.append(c)
        by_session[sid] = c
    for r in rows["interactions"]:
        c = by_session.get(col(r, 1))
        if c is None or (col(r, 3) or "").upper() == "SESSION_END":
            continue
        t = {"interaction_id": col(r, 0), "topic": col(r, 2), "start_time": col(r, 4), "end_time": col(r, 5),
             "duration_ms": duration_ms(col(r, 4), col(r, 5)), "telemetry_trace_id": not_set(col(r, 6)),
             "messages": [], "steps": []}
        c["turns"].append(t)
        turn_of[t["interaction_id"]] = t
        convo_of[t["interaction_id"]] = c
    for c in convos:
        c["turn_count"] = len(c["turns"])
    for r in rows["messages"]:
        t = turn_of.get(col(r, 1))
        if t is not None:
            t["messages"].append({"message_id": col(r, 0), "message_type": col(r, 2), "text": col(r, 3),
                                  "sent_at": col(r, 4)})
    for t in turn_of.values():
        infer_message_types(t["messages"])
    for r in rows["steps"]:
        t = turn_of.get(col(r, 1))
        if t is None:
            continue
        s = {"step_id": col(r, 0), "step_type": col(r, 2), "name": col(r, 3), "start_time": col(r, 4),
             "end_time": col(r, 5), "duration_ms": duration_ms(col(r, 4), col(r, 5)), "input": not_set(col(r, 6)),
             "output": not_set(col(r, 7)), "error": not_set(col(r, 8)), "pre_vars": not_set(col(r, 9)),
             "post_vars": not_set(col(r, 10)), "generation_id": not_set(col(r, 11)),
             "gateway_request_id": not_set(col(r, 12))}
        if s["error"] is not None and (s["step_type"] or "").upper() == "ACTION_STEP":
            convo_of[col(r, 1)]["action_error_count"] += 1
        t["steps"].append(s)
    return convos


# --- selection --------------------------------------------------------------------------------

def channel_kept(channel, channels=None):
    """With channels: one of them (case-insensitive). Without: any but the Builder* channels."""
    name = (channel or "").strip().lower()
    if channels:
        return name in {c.strip().lower() for c in channels}
    return not name.startswith(BUILDER_PREFIX)


def sample_key(session_id, salt=SAMPLE_SALT):
    return hashlib.sha256(f"{salt}\0{session_id}".encode("utf-8")).hexdigest()


def select(cands, channels=None, exclude=frozenset(), split=None, val_fraction=None, split_salt=SPLIT_SALT,
           order="hash", sample_salt=SAMPLE_SALT, max_sessions=MAX_SESSIONS):
    """(the sessions to fetch, in rank order; counts). Channel, excluded sessions and split filter
    in that order; the rest is ranked (a salted hash, or newest first) and cut at max_sessions."""
    counts = {"candidates": len(cands),
              "by_channel": dict(sorted(Counter(c["channel"] or "(none)" for c in cands).items()))}
    kept = [c for c in cands if channel_kept(c["channel"], channels)]
    counts["dropped_channel"] = len(cands) - len(kept)
    n = len(kept)
    kept = [c for c in kept if c["session_id"] not in exclude]
    counts["excluded"] = n - len(kept)
    n = len(kept)
    if split is not None:
        kept = [c for c in kept if session_split(c["session_id"], val_fraction, split_salt) == split]
    counts["other_split"] = n - len(kept)
    counts["available"] = len(kept)
    if order == "recent":
        oldest = datetime.min.replace(tzinfo=timezone.utc)
        kept.sort(key=lambda c: c["session_id"])
        kept.sort(key=lambda c: parse_time(c["start_time"]) or oldest, reverse=True)
    elif order == "hash":
        kept.sort(key=lambda c: sample_key(c["session_id"], sample_salt))
    else:
        raise FetchError(f"unknown order {order!r}")
    chosen = kept[:max_sessions]
    counts["selected"] = len(chosen)
    return chosen, counts


# --- the fetch --------------------------------------------------------------------------------

def write_private(path, text):
    """Write text to a file only the user can read, also before the text is in."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.chmod(path, 0o600)  # an existing file keeps its mode through os.open
        f = os.fdopen(fd, "w", encoding="utf-8")
    except BaseException:
        os.close(fd)
        raise
    with f:
        f.write(text)


def _private_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path, mode=0o700)
        os.chmod(path, 0o700)
    return path


def _resumed(path):
    """The sessions of an earlier fetch's batch file, or None (absent, or cut short)."""
    try:
        with open(path, encoding="utf-8") as fh:
            got = json.load(fh)
    except (OSError, ValueError):
        return None
    return got if isinstance(got, list) else None


def digest(ids):
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()[:16]


def code_sha():
    """Hash of the modules a fetch runs, the same in the skill and in a kit."""
    here = os.path.dirname(os.path.abspath(__file__))
    h = hashlib.sha256()
    for name in ("fetch.py", "redact.py", "splits.py", "stdm.py"):
        with open(os.path.join(here, name), "rb") as f:
            h.update(name.encode() + b"\0" + f.read() + b"\0")
    return h.hexdigest()[:16]


def find_candidates(f, agent, start, end):
    """(candidates, how the agent was matched): by participant API name, else by the planner ids
    of the agent's GenAiPlannerDefinitions. Matching nothing raises, with what the data space holds."""
    cands = f.candidates(start, end, agent=agent)
    if cands:
        return cands, {"by": "agent_api_name"}
    planners, seen, error = [], [], None
    try:
        planners, seen = f.planners(agent)
    except FetchError as e:
        error = str(e)
    ids = []
    for p in planners:
        ids += [p["Id"]] + ([p["Id"][:15]] if len(p["Id"]) == 18 else [])
    if ids:
        cands = f.candidates(start, end, participant_ids=ids)
        if cands:
            return cands, {"by": "planner_id", "planners": sorted(p.get("DeveloperName") or "?" for p in planners)}
    raise FetchError(diagnose(f, agent, start, end, ids, planners, seen, error))


def diagnose(f, agent, start, end, ids, planners, seen, planner_error):
    """Why the agent filter matched nothing, from counts only."""
    lines = [f"no session of agent {agent!r} started in [{start}, {end}] with a TURN interaction in data space "
             f"{f.dataspace!r}; nothing fetched."]
    if planner_error:
        lines.append(f"Its planner ids could not be looked up: {planner_error}")
    elif planners:
        lines.append("Its planners (" + ", ".join(sorted(p.get("DeveloperName") or "?" for p in planners))
                     + ") matched no session either.")
    else:
        lines.append(f"No GenAiPlannerDefinition is named {agent} or {agent}_<n>"
                     + (" (named like it: " + ", ".join(seen[:10]) + ")." if seen else "."))
    queries = {"byname": count_sql(PARTICIPANT, "ssot__AiAgentApiName__c = " + _lit(agent)),
               "agents": agents_in_window_sql(start, end)}
    if ids:
        queries["byid"] = count_sql(PARTICIPANT, "ssot__ParticipantId__c IN " + _in(ids, "planner id"))
    try:
        got = f.query(queries, "diagnose")
    except FetchError as e:
        lines.append(f"(The diagnostic queries failed too: {e})")
        return " ".join(lines)
    lines.append(f"Participant rows of {agent!r} at any time: {col(got['byname'][0], 0) if got['byname'] else 0} "
                 "by API name" + (f", {col(got['byid'][0], 0) if got['byid'] else 0} by planner id." if ids else "."))
    agents = sorted(((col(r, 0) or "(no API name)", int(float(col(r, 1) or 0))) for r in got["agents"]),
                    key=lambda a: (-a[1], a[0]))
    if agents:
        lines.append("Agents with sessions in the window: "
                     + ", ".join(f"{name} ({n})" for name, n in agents[:10]) + ("..." if len(agents) > 10 else "") + ".")
    else:
        lines.append("No session of any agent started in the window: widen --start/--end.")
    return " ".join(lines)


OUTPUTS = ("details.json", "sessions.json", "fetch.json")


def clear_outputs(out_dir):
    """Remove an earlier fetch's files from out_dir: only the names a fetch writes."""
    for name in OUTPUTS:
        p = os.path.join(out_dir, name)
        if os.path.isfile(p):
            os.remove(p)
    for sub, pattern in (("batches", r"b_[0-9a-f]{16}\.json"), ("apex", r"\d{3}_[a-z]+\.apex")):
        d = os.path.join(out_dir, sub)
        if os.path.isdir(d):
            for name in os.listdir(d):
                if re.fullmatch(pattern, name):
                    os.remove(os.path.join(d, name))


def fetch(f, agent, start, end, out_dir=None, channels=None, exclude=frozenset(), split=None, val_fraction=None,
          split_salt=SPLIT_SALT, order="hash", sample_salt=SAMPLE_SALT, max_sessions=MAX_SESSIONS,
          batch_size=BATCH_SIZE, dry_run=False, log=lambda line: None, params=None):
    """Find, select and fetch the agent's sessions; writes details.json, sessions.json and
    fetch.json to out_dir (not with dry_run) and returns the bt.fetch/1 manifest."""
    check_name(agent)
    start, end = window_bound(start), window_bound(end, end=True)
    if parse_time(start) > parse_time(end):
        raise FetchError(f"--start {start} is after --end {end}")
    if split is not None and not (val_fraction and 0 < val_fraction < 1):
        raise FetchError("--split needs --val-fraction in (0, 1)")
    if batch_size < 1 or max_sessions < 1:
        raise FetchError("--batch-size and --max-sessions must be >= 1")

    cands, matched = find_candidates(f, agent, start, end)
    chosen, counts = select(cands, channels, exclude, split, val_fraction, split_salt, order, sample_salt,
                            max_sessions)
    log(f"candidates: {counts['candidates']} sessions of {agent} in the window (matched by "
        f"{matched['by'].replace('_', ' ')})")
    log("  by channel: " + ", ".join(f"{k} {v}" for k, v in counts["by_channel"].items()))
    log(f"  dropped: {counts['dropped_channel']} by channel, {counts['excluded']} excluded, "
        f"{counts['other_split']} in the other split; {counts['available']} available, {counts['selected']} selected")
    if not chosen:
        raise FetchError("no session left to fetch after the channel, exclusion and split filters "
                         "(see the counts above)")
    ids = [c["session_id"] for c in chosen]
    manifest = {"schema": SCHEMA_FETCH, "org": f.org, "dataspace": f.dataspace, "agent": agent, "window": [start, end],
                "agent_filter": matched,
                "selection": {"channels": list(channels) if channels else None, "order": order,
                              "sample_salt": sample_salt if order == "hash" else None, "max_sessions": max_sessions,
                              "split": None if split is None else {"split": split, "val_fraction": val_fraction,
                                                                   "salt": split_salt},
                              "excluded_ids": len(exclude)},
                "params": params or {}, "counts": counts, "digests": {"selection": digest(ids)},
                "code": {"fetch_sha256": code_sha()}, "dry_run": dry_run}
    if f.names is not None:
        manifest["stdm_names"] = f.names.manifest()
    if dry_run:
        return manifest

    batch_dir = _private_dir(os.path.join(out_dir, "batches"))
    convos, stats = [], {"batches": 0, "retries": 0, "resumed": 0}
    pending = [ids[i:i + batch_size] for i in range(0, len(ids), batch_size)]
    while pending:
        batch = pending.pop(0)
        path = os.path.join(batch_dir, "b_" + digest(batch) + ".json")
        got = _resumed(path)  # an interrupted fetch got this batch already
        if got is not None:
            stats["resumed"] += 1
        else:
            try:
                got = f.details(batch)
            except BatchTooBig as e:
                if len(batch) == 1:
                    raise FetchError(f"one session is too big for a single Apex run ({e}); fetch it another way, "
                                     "or leave it out with --exclude-sessions") from None
                half = (len(batch) + 1) // 2
                pending[:0] = [batch[:half], batch[half:]]
                stats["retries"] += 1
                log(f"  a batch of {len(batch)} sessions was too big ({str(e)[:120]}); halving it")
                continue
            write_private(path, json.dumps(got, ensure_ascii=False))
            stats["batches"] += 1
        convos.extend(got)
        log(f"  fetched {len(convos)}/{len(ids)} sessions")

    no_turns = sum(1 for c in convos if not c["turns"])
    turns = sum(len(c["turns"]) for c in convos)
    llm = sum(1 for c in convos for t in c["turns"] for s in t["steps"] if s.get("step_type") == "LLM_STEP")
    counts.update(fetched=len(convos), turns=turns, llm_steps=llm, no_turns=no_turns, apex_runs=f.runs, **stats)
    if no_turns:
        log(f"  warning: {no_turns} sessions came back without turns")
    details = json.dumps(convos, ensure_ascii=False, indent=1)
    write_private(os.path.join(out_dir, "details.json"), details + "\n")
    write_private(os.path.join(out_dir, "sessions.json"),
                  json.dumps([session_summary(c) for c in chosen], ensure_ascii=False, indent=1) + "\n")
    manifest["digests"]["details"] = hashlib.sha256((details + "\n").encode("utf-8")).hexdigest()[:16]
    manifest["fetched"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    write_private(os.path.join(out_dir, "fetch.json"), json.dumps(manifest, indent=2) + "\n")
    for name in os.listdir(batch_dir):  # merged: the batches are not needed any more
        if re.fullmatch(r"b_[0-9a-f]{16}\.json", name):
            os.remove(os.path.join(batch_dir, name))
    if not os.listdir(batch_dir):
        os.rmdir(batch_dir)
    return manifest


def probe(f, agent=None, start=None, end=None):
    """{key: row count, or the error} for every STDM DMO, plus the agent's participant rows and
    the sessions in the window when given. Errors are caught in the Apex, one per query. With a
    names map, also each query shape a fetch runs (SHAPES; 0 rows each), to check every name."""
    queries = {key: count_sql(table) for key, table in PROBE_DMOS.items()}
    if agent:
        queries["agent"] = count_sql(PARTICIPANT, "ssot__AiAgentApiName__c = " + _lit(check_name(agent)))
    if start and end:
        queries["window"] = count_sql(SESSION, "ssot__StartTimestamp__c >= " + _lit(window_bound(start))
                                      + " AND ssot__StartTimestamp__c <= " + _lit(window_bound(end, end=True)))
    if f.names is not None:
        queries.update(shape_queries())
    found = f.run(query_script(queries, f.dataspace, probe=True, names=f.names), "probe")
    if END not in found:
        raise FetchError("probe: the Apex log has no end marker")
    out = {}
    for key in queries:
        page = found.get(f"STDM_RESULT_{key}_0")
        if not isinstance(page, dict):
            out[key] = {"error": "no result line"}
        elif "error" in page:
            out[key] = {"error": mask_ids(str(page["error"]))[:500]}
        else:
            rows = page.get("rows") or []
            if key in SHAPES:  # a query shape: the rows of its first page, not a count
                out[key] = {"rows": len(rows)}
            else:
                out[key] = {"rows": int(float(col(rows[0], 0) or 0)) if rows else 0}
    return out
