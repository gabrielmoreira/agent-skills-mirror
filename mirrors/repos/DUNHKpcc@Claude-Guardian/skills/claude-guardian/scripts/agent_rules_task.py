"""Small supplied-snapshot task for an Agent using the supported 2.5.8 UI.

No file/app/network operations, approval restoration, native session or transaction
receipt. The real host binds sources and authorizes each actual scoped action.
Internal Tauri wrappers are not an external automation API. All comparisons here
describe supplied data, never observed native execution or effective routing.
"""
import copy
import hashlib
import math
import time

import clash_verge_258 as linkage
import config_edit_plan as config
import environment_entry as entry
import rules_extension_plan as rules

SCHEMA = 'guardian-agent-rules-task/0.1'
RESULT_SCHEMA = 'guardian-agent-rules-comparison/0.1'
_ROLES = {'app_plist', 'profile_index', 'extension', 'base'}
_REFS = {'task_ref', 'host_scope_ref', 'app_ref', 'profile_ref',
         'backup_ref', 'recovery_ref'}
_STEPS = (
    ('bind_and_review', 'Bind actual target/app/profile/extension; resolve relevant chain, group and protected-priority facts.'),
    ('backup_and_rescue', 'Verify private original content/metadata backup and independent offline recovery instructions.'),
    ('exact_host_approval', 'Review the exact rule, formatting scope and backup; obtain actual host approval for save, possible reload/core replacement, DNS synchronization and connectivity effects.'),
    ('fresh_editor_recheck', 'Revalidate the current configuration entry for this target in the real host before Save; resolve stale editors without discarding unapproved work, reread the same approved sources and address concurrent writers.'),
    ('app_edit_save', 'Use the verified supported app editor to make only the reviewed change and Save once; inspect an uncertain outcome before retrying.'),
    ('separate_verification', 'Read back selected content and linkage; separately observe app load and effective rules. Network tests need their own exact authorization.'),
    ('conflict_aware_recovery', 'Inspect current state first; restore only within freshly checked approval scope. Preserve later edits and seek a new recovery review on conflict.'),
)
_CHECKS = ('actual_host_target_user_namespace', 'installed_app_and_current_profile',
           'selected_extension_and_base', 'effective_chain_and_group_priority',
           'protected_control_scope', 'private_backup_and_offline_recovery',
           'supported_ui_and_concurrent_writers', 'current_configuration_entry',
           'current_exact_host_approval')


class TaskError(ValueError):
    """Fixed nonsecret error code only."""

    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _fail(code):
    raise TaskError(code) from None


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _duration(value, maximum, code):
    if type(value) not in (int, float) or not 0 < value <= maximum or not math.isfinite(value):
        _fail(code)


def _now():
    try:
        value = time.monotonic()
        if type(value) not in (int, float) or not math.isfinite(value):
            _fail('INVALID_CLOCK')
        return value
    except (OverflowError, TypeError, ValueError, OSError):
        _fail('INVALID_CLOCK')


def _entry(request, target_ref):
    try:
        entry.require_entry(request, 'offline_precheck', target_ref)
    except (entry.InvalidProjection, entry.EntryBlocked):
        _fail('ENVIRONMENT_ENTRY_REQUIRED')


def _guard(cancelled, deadline, *, previous=None, inspection=False):
    if not callable(cancelled):
        _fail('INVALID_CANCELLATION_CALLBACK')
    try:
        stopped = cancelled()
    except Exception:
        _fail('CANCELLED')
    if type(stopped) is not bool or stopped:
        _fail('CANCELLED')
    now = _now()
    if previous is not None:
        if now < previous[0]:
            _fail('INVALID_CLOCK')
        previous[0] = now
    if now >= deadline and not inspection:
        _fail('DEADLINE_EXCEEDED')
    return 'expired' if now >= deadline else 'current'


def _source_kinds(kinds):
    if type(kinds) is not dict or set(kinds) != _ROLES:
        _fail('INVALID_SOURCE_KINDS')
    for role, kind in kinds.items():
        allowed = ('file_bytes',) if role in ('app_plist', 'profile_index') else ('file_bytes', 'app_text')
        if type(kind) is not str or kind not in allowed:
            _fail('INVALID_SOURCE_KINDS')


def _references(refs):
    if type(refs) is not dict or set(refs) != _REFS:
        _fail('INVALID_TASK_REFERENCES')
    try:
        for value in refs.values():
            entry._alias(value)
    except entry.InvalidProjection:
        _fail('INVALID_TASK_REFERENCES')
    if len(set(refs.values())) != len(_REFS):
        _fail('INVALID_TASK_REFERENCES')


def _blobs(blobs):
    for role, raw in blobs.items():
        limit = linkage.MAX_PLIST_BYTES if role == 'app_plist' else config.MAX_BYTES
        if type(raw) is not bytes or not 0 < len(raw) <= limit:
            _fail('INVALID_OR_OVERSIZED_SNAPSHOT')


def _seqmap(raw):
    """Only three string sequences; comments use the existing YAML parser."""
    _, root = config._parse(raw)
    values = config._mapping(root)
    if set(values) != {'prepend', 'append', 'delete'}:
        _fail('UNSUPPORTED_AGENT_EXTENSION_FORMAT')
    result = tuple(tuple(rules._strings(values[key])) for key in ('prepend', 'append', 'delete'))
    if result[1] or result[2]:
        _fail('UNSUPPORTED_AGENT_EXTENSION_FORMAT')
    return result


class PrivateAgentRulesTask:
    __slots__ = ('_candidate', '_linkage', '_refs', '_request', '_selection',
                 '_kinds', '_hashes', '_entry', '_entry_basis', '_expires', '_cancelled',
                 '_clock', '_stopped')

    def __init__(self, candidate, ownership, refs, request, selection, kinds,
                 hashes, entry_request, entry_basis, expires, cancelled, clock):
        self._candidate, self._linkage = candidate, ownership
        self._refs, self._request = copy.deepcopy(refs), copy.deepcopy(request)
        self._selection, self._kinds, self._hashes = selection, dict(kinds), dict(hashes)
        self._entry, self._entry_basis = entry_request, copy.deepcopy(entry_basis)
        self._expires, self._cancelled = expires, cancelled
        self._clock = clock
        self._stopped = None

    def __repr__(self):
        return '<PrivateAgentRulesTask: supplied data only; no authority>'

    def __reduce_ex__(self, protocol):
        raise TypeError('private task serialization disabled')

    def _inspection_state(self, entry_request):
        # No new host reads happen here. Withdrawal/expiry must not hide already
        # retained originals needed to investigate an uncertain save or recover.
        if self._stopped is not None:
            return dict(self._stopped)
        try:
            freshness = _guard(self._cancelled, self._expires, previous=self._clock, inspection=True)
        except TaskError as exc:
            self._stopped = {'review_state': 'invalid_clock' if exc.code == 'INVALID_CLOCK' else 'cancelled',
                             'task_freshness': 'unknown'}
            return dict(self._stopped)
        state = freshness
        if self._entry != self._entry_basis or entry_request != self._entry_basis:
            state = 'entry_changed'
        else:
            try:
                _entry(entry_request, self._request['target_ref'])
            except TaskError:
                state = 'entry_changed'
        result = {'review_state': state, 'task_freshness': freshness}
        if state == 'entry_changed':
            self._stopped = dict(result)
        return result

    def public_report(self):
        state = self._inspection_state(self._entry)
        current = state['review_state'] == 'current'
        material = self._candidate.private_material()
        no_change = material['original_bytes'] == material['candidate_bytes']
        preview = self._candidate.preview()
        result = {
            'schema_version': SCHEMA, 'task_ref': self._refs['task_ref'],
            'target_ref': self._request['target_ref'], 'route_ref': self._request['route_ref'],
            'scope_refs': list(self._request['scope_refs']),
            'extension_ref': self._request['layer_ref'],
            'rule_refs': list(self._request['rule_refs']),
            'before_revision_ref': self._request['revision_ref'],
            'app_ref': self._refs['app_ref'], 'profile_ref': self._refs['profile_ref'],
            'product': 'clash-verge-rev', 'version': linkage.VERSION,
            'status': ('no_change' if no_change and current else 'needs_host_review' if current
                       else 'cancelled' if state['review_state'] == 'cancelled'
                       else state['review_state'] + '_needs_review'),
            **state,
            'executor': 'agent_supported_application', 'authority': 'none',
            'builtin_apply_supported': False, 'evidence_level': 'supplied_snapshots_only',
            'operation': 'none' if no_change else 'insert_selected_prepend_rules',
            'changed_rules': preview['added_rules'], 'matched_rules': preview['matched_rules'],
            'source_kinds': dict(self._kinds),
            'steps': [] if no_change or not current else [
                {'id': key, 'instruction': value} for key, value in _STEPS],
            'required_host_checks': [] if no_change else list(_CHECKS),
            'compiler_blockers': list(preview['blockers']),
            'linkage_blockers': list(self._linkage.public_report()['blockers']),
            'file_content': 'not_observed', 'file_metadata': 'not_observed',
            'app_save': 'not_run', 'application_load': 'not_run',
            'effective_rules': 'not_run', 'effective_routing': 'not_run', 'recovery': 'not_run',
        }
        if not no_change:
            result.update(backup_ref=self._refs['backup_ref'], recovery_ref=self._refs['recovery_ref'])
        return result

    def private_review(self):
        state = self._inspection_state(self._entry)
        material = self._candidate.private_material()
        return {
            'task_ref': self._refs['task_ref'], 'host_scope_ref': self._refs['host_scope_ref'],
            **state,
            'target_ref': self._request['target_ref'], 'selection': dict(zip(
                ('extension_uid', 'extension_basename', 'base_basename'), self._selection)),
            'source_sha256': dict(self._hashes), 'source_kinds': dict(self._kinds),
            'candidate_sha256': material['candidate_sha256'],
            'selected_additions': list(material['ordered_additions']),
            'matched_rule_refs': list(material['matched_rule_refs']),
            'known_priority_overlaps': list(material['known_priority_overlaps']),
            'format_scope': ('comment_preserving_three_sequence_yaml_exact_bytes_required'
                             if any(b'#' in material[key] for key in ('original_bytes', 'candidate_bytes'))
                             else 'comment_free_three_sequence_yaml_formatting_only'),
            'approval': 'real_host_exact_action_required',
            'backup_ref': self._refs['backup_ref'], 'recovery_ref': self._refs['recovery_ref'],
        }

    def private_material(self):
        state = self._inspection_state(self._entry)
        material = self._candidate.private_material()
        return {'original_bytes': material['original_bytes'],
                **state,
                'candidate_bytes': material['candidate_bytes'],
                'original_sha256': material['original_sha256'],
                'candidate_sha256': material['candidate_sha256']}


def prepare_rules_task(request, binding, *, app_plist, profile_index, extension, base,
                       selected_uid, selected_basename, base_basename, entry_request,
                       refs, source_kinds, max_seconds=5, ttl_seconds=600,
                       cancelled=lambda: False):
    """Compile supplied snapshots into a fixed Agent task; perform no I/O.

The host must privately bind source objects/identities, current entry and actual
permission. Source kinds are labels, not attestations. Only the metadata inputs
require file bytes; extension/base may be app text, with no file-byte claim.
"""
    _duration(max_seconds, 60, 'INVALID_DEADLINE')
    _duration(ttl_seconds, 600, 'INVALID_EXPIRY')
    started = _now()
    deadline = started + max_seconds
    if deadline <= started or started + ttl_seconds <= started:
        _fail('INVALID_CLOCK')
    clock = [started]
    _guard(cancelled, deadline, previous=clock)
    if type(request) is not dict or type(request.get('target_ref')) is not str:
        _fail('INVALID_REMEDY_REQUEST')
    _entry(entry_request, request['target_ref'])
    basis = copy.deepcopy(entry_request)
    if type(binding) is not dict:
        _fail('INVALID_BINDING')
    try:
        request_basis, binding_basis = copy.deepcopy(request), copy.deepcopy(binding)
    except Exception:
        _fail('INVALID_REMEDY_REQUEST')
    guard_error = []
    def guard():
        try:
            _guard(cancelled, deadline, previous=clock)
            if entry_request != basis:
                _fail('ENVIRONMENT_ENTRY_CHANGED')
            if request != request_basis or binding != binding_basis:
                _fail('TASK_INPUT_CHANGED')
            _entry(entry_request, request['target_ref'])
            return False
        except TaskError as exc:
            guard_error[:] = [exc.code]
            raise
    _references(refs)
    _source_kinds(source_kinds)
    refs, source_kinds = dict(refs), dict(source_kinds)
    blobs = dict(app_plist=app_plist, profile_index=profile_index, extension=extension, base=base)
    _blobs(blobs)
    if type(base_basename) is not str or not linkage.BASENAME.fullmatch(base_basename):
        _fail('BASE_PROFILE_FILE_MISMATCH')
    try:
        ownership = linkage.inspect_linkage(app_plist, profile_index, extension,
            selected_uid=selected_uid, selected_basename=selected_basename,
            extension_kind='rules', max_seconds=max_seconds, cancelled=guard)
        if ownership.private_material()['base_basename'] != base_basename:
            _fail('BASE_PROFILE_FILE_MISMATCH')
        candidate = rules.compile_rules_extension(extension, base, request, binding,
                                                  max_seconds=max_seconds, cancelled=guard)
        # The existing compiler validates the entire request/binding before this
        # wrapper narrows it further. Do not synthesize missing semantic facts.
        if (len(binding['rule_order']) != 1
                or binding['rules'][binding['rule_order'][0]]['kind'] != 'DOMAIN'):
            _fail('UNSUPPORTED_AGENT_RULE_SCOPE')
        _seqmap(extension)
        _seqmap(candidate.private_material()['candidate_bytes'])
    except (linkage.OwnershipError, rules.RulesPlanError, config.EditPlanError) as exc:
        # All three existing libraries expose fixed privacy-preserving codes.
        _fail(guard_error[0] if guard_error else str(exc))
    guard()
    summary = {key: request[key] for key in ('target_ref', 'route_ref', 'scope_refs')}
    summary.update(layer_ref=binding['layer_ref'], rule_refs=binding['rule_order'],
                   revision_ref=request['revision_refs'][binding['layer_ref']])
    return PrivateAgentRulesTask(candidate, ownership, refs, summary,
        (selected_uid, selected_basename, base_basename), source_kinds,
        {role: _hash(raw) for role, raw in blobs.items()}, entry_request, basis,
        started + ttl_seconds, cancelled, clock)


def assess_supplied_readback(task, *, app_plist, profile_index, extension, base,
                             selected_uid, selected_basename, base_basename,
                             entry_request, source_kinds):
    """Compare supplied current snapshots only; never infer save/load/permission.

    An unchanged original may mean no save, failed save or app restoration; it is
    not proof of any of them. A formatting-only normalized original is deliberately
    unexpected_delta unless its bytes match; restoration is never inferred. A
    differing snapshot requires fresh conflict-aware review. Semantic candidate
    comparison is available only when original, candidate and readback contain
    no hash marker; comments must never be discarded as formatting.
    """
    if type(task) is not PrivateAgentRulesTask:
        _fail('INVALID_AGENT_TASK')
    state = task._inspection_state(entry_request)
    _source_kinds(source_kinds)
    source_kinds = dict(source_kinds)
    blobs = dict(app_plist=app_plist, profile_index=profile_index, extension=extension, base=base)
    _blobs(blobs)
    result = {
        'schema_version': RESULT_SCHEMA, 'task_ref': task._refs['task_ref'],
        'target_ref': task._request['target_ref'], 'comparison': 'binding_changed',
        'evidence_level': 'supplied_snapshot_comparison', 'authority': 'none',
        **state,
        'content_basis': source_kinds['extension'],
        'file_content': 'not_observed', 'file_metadata': 'not_observed',
        'app_save': 'not_run', 'application_load': 'not_run',
        'effective_rules': 'not_run', 'effective_routing': 'not_run', 'recovery': 'not_run',
        'recovery_relation': 'conflict_requires_new_review',
    }
    def interrupted(current):
        result.update(current)
        if current['review_state'] in ('current', 'expired'):
            return False
        result['comparison'] = ('binding_changed' if current['review_state'] == 'entry_changed'
                                else 'not_compared')
        result['recovery_relation'] = 'conflict_requires_new_review'
        return True
    if interrupted(state):
        return result
    if ((selected_uid, selected_basename, base_basename) != task._selection
            or any(_hash(blobs[role]) != task._hashes[role]
                   or source_kinds[role] != task._kinds[role]
                   for role in ('app_plist', 'profile_index', 'base'))):
        interrupted(task._inspection_state(entry_request))
        return result
    material = task._candidate.private_material()
    guard_state = []
    def guard():
        current = task._inspection_state(entry_request)
        if current['review_state'] not in ('current', 'expired'):
            guard_state[:] = [current]
            return True
        return False
    try:
        linkage.inspect_linkage(app_plist, profile_index, extension,
            selected_uid=selected_uid, selected_basename=selected_basename,
            extension_kind='rules', cancelled=guard)
        signature = _seqmap(extension)
        expected = _seqmap(material['candidate_bytes'])
    except (linkage.OwnershipError, rules.RulesPlanError, config.EditPlanError, TaskError) as exc:
        # Scope/clock/cancellation must not be mistaken for malformed content.
        if guard_state:
            interrupted(guard_state[0])
            return result
        if isinstance(exc, TaskError) and exc.code != 'UNSUPPORTED_AGENT_EXTENSION_FORMAT':
            raise
        if str(exc) in ('PARSER_UNAVAILABLE', 'DEADLINE_EXCEEDED'):
            result['comparison'] = 'not_compared'
            result['error_code'] = str(exc)
        else:
            result['comparison'] = 'unexpected_delta'
        interrupted(task._inspection_state(entry_request))
        return result
    if extension == material['candidate_bytes']:
        result['comparison'] = 'exact_match'
        result['recovery_relation'] = ('no_change_task' if extension == material['original_bytes']
                                       else 'candidate_matches_supplied_snapshot')
    elif extension == material['original_bytes']:
        result['comparison'] = 'unchanged'
        result['recovery_relation'] = 'original_matches_supplied_snapshot'
    elif (not any(b'#' in raw for raw in (material['original_bytes'],
                                         material['candidate_bytes'], extension))
          and signature == expected):
        result['comparison'] = 'semantic_match_bytes_differ'
        result['recovery_relation'] = 'candidate_semantics_match_supplied_snapshot'
    else:
        result['comparison'] = 'unexpected_delta'
    interrupted(task._inspection_state(entry_request))
    return result
