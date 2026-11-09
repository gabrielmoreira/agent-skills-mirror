"""Agent-callable, offline repair preflight. No production write adapter admitted.

Explicit paths are private local inputs, not discovered from request documents.
No JSON field grants authority or native capability. Raw diffs require an
explicit authorized private-host review; ordinary output contains no file bytes or paths.
"""
import argparse
import copy
import json
import os
import sys
import time

sys.dont_write_bytecode = True
import config_edit_plan as edits
import clash_verge_258 as ownership
import rules_extension_plan as rules_edits
import recovery_cli
import transactions as tx
import environment_entry

SCHEMA = 'guardian-repair-request/0.1'
RESULT_SCHEMA = 'guardian-repair-result/0.1'
NATIVE_BLOCKERS = ('NATIVE_SCHEMA_ADAPTER_NOT_IMPLEMENTED',
                   'VERSION_CAPABILITY_UNVERIFIED', 'NATIVE_ACCEPTANCE_NOT_RUN')


class RepairError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def _guard(cancelled, deadline):
    try:
        stopped = cancelled()
    except Exception:
        raise RepairError('CANCELLED') from None
    if stopped:
        raise RepairError('CANCELLED')
    if time.monotonic() >= deadline:
        raise RepairError('DEADLINE_EXCEEDED')


def _load_request(path):
    # Reuse the bounded no-follow private-file reader; the content remains data.
    value = recovery_cli.load_receipt(path)
    if (type(value) is not dict or set(value) != {'schema_version', 'remedy_request', 'binding'}
            or value['schema_version'] != SCHEMA):
        raise RepairError('INVALID_REPAIR_REQUEST')
    return value


def _read_source(path):
    with tx._parent(path) as (fd, name):
        raw, snapshot = tx._read(fd, name)
        return raw, {'path': path, 'snapshot': snapshot, 'parent_identity': tx._identity(fd)}


def _check_source(source):
    if source is not None and _read_source(source['path'])[1] != source:
        raise RepairError('SOURCE_SNAPSHOT_CHANGED')


def preflight(request_path, target_path, target_ref, *, max_seconds=30,
              cancelled=lambda: False, candidate_kind='merge-policy', base_path=None,
              app_info_path=None, profile_index_path=None, extension_uid=None, entry_request=None):
    """Read only explicit authorized request/target and optional base; never discover paths.

    The return value is private in-process material, not a native authorization.
    Call public_report for agent-visible data. A host must have independently
    bound target, user and namespace before invoking even this read-only API.
    """
    try:
        environment_entry.require_entry(entry_request, 'offline_precheck', target_ref)
    except (environment_entry.InvalidProjection, environment_entry.EntryBlocked):
        raise RepairError('ENVIRONMENT_ENTRY_REQUIRED') from None
    if type(max_seconds) not in (int, float) or not 0 < max_seconds <= 60:
        raise RepairError('INVALID_DEADLINE')
    deadline = time.monotonic() + max_seconds
    entry_basis = copy.deepcopy(entry_request)
    def entry_guard():
        _guard(cancelled, deadline)
        if entry_request != entry_basis:
            raise RepairError('ENVIRONMENT_ENTRY_CHANGED')
        try:
            environment_entry.require_entry(entry_request, 'offline_precheck', target_ref)
        except (environment_entry.InvalidProjection, environment_entry.EntryBlocked):
            raise RepairError('ENVIRONMENT_ENTRY_REQUIRED') from None
    entry_guard()
    if candidate_kind not in ('merge-policy', 'rules-prepend'):
        raise RepairError('UNSUPPORTED_CANDIDATE_KIND')
    extra = (base_path, app_info_path, profile_index_path, extension_uid)
    if ((candidate_kind == 'rules-prepend' and (not all(extra) or base_path == target_path))
            or (candidate_kind == 'merge-policy' and any(item is not None for item in extra))):
        raise RepairError('EXPLICIT_RULES_SOURCE_SCOPE_REQUIRED')
    if candidate_kind == 'rules-prepend':
        for path in (target_path, base_path, app_info_path, profile_index_path):
            tx._path(path)
        if (os.path.dirname(base_path) != os.path.dirname(target_path)
                or os.path.dirname(target_path) != os.path.dirname(profile_index_path) + '/profiles'):
            raise RepairError('PROFILE_DIRECTORY_SCOPE_MISMATCH')
    tx._support()
    request = _load_request(request_path)
    fingerprint = tx.digest(request)
    entry_guard()
    semantic, binding = request['remedy_request'], request['binding']
    if (type(semantic) is not dict or semantic.get('target_ref') != target_ref
            or type(binding) is not dict or binding.get('target_ref') != target_ref):
        raise RepairError('TARGET_MISMATCH')
    # Read the explicit path only after the request's target binding is checked.
    with tx._parent(target_path) as (fd, name):
        original, snapshot = tx._read(fd, name)
        parent_identity = tx._identity(fd)
    entry_guard()
    base_source, metadata_sources, linkage = None, {}, None
    if candidate_kind == 'rules-prepend':
        base_raw, base_source = _read_source(base_path)
        info_raw, metadata_sources['app_info'] = _read_source(app_info_path)
        entry_guard()
        index_raw, metadata_sources['profile_index'] = _read_source(profile_index_path)
        entry_guard()
        linkage = ownership.inspect_linkage(info_raw, index_raw, original,
                                            selected_uid=extension_uid,
                                            selected_basename=os.path.basename(target_path),
                                            extension_kind='rules', max_seconds=max_seconds,
                                            cancelled=lambda: (entry_guard() or False))
        if linkage.private_material()['base_basename'] != os.path.basename(base_path):
            raise RepairError('BASE_PROFILE_FILE_MISMATCH')
        entry_guard()
        candidate = rules_edits.compile_rules_extension(original, base_raw, semantic, binding,
                                                        max_seconds=max_seconds, cancelled=lambda: (entry_guard() or False))
    else:
        candidate = edits.compile_edit_plan(original, semantic, binding)
    material = candidate.private_material()
    entry_guard()
    target_source = {'path': target_path, 'snapshot': snapshot,
                     'parent_identity': parent_identity}
    # An observation of matching bytes is not an action plan. In particular,
    # tx.plan would invent an action ID even when no file change is needed.
    plan = None
    if material['candidate_bytes'] != original:
        plan = tx.plan(target_path, material['candidate_bytes'], target_ref,
                       ttl_seconds=600)
        if plan['before'] != snapshot or plan['parent_identity'] != parent_identity:
            raise RepairError('STALE_FILE')
    entry_guard()
    _check_source(base_source)
    for source in metadata_sources.values():
        entry_guard()
        _check_source(source)
    entry_guard()
    if tx.digest(_load_request(request_path)) != fingerprint:
        raise RepairError('REQUEST_CHANGED')
    entry_guard()
    if candidate_kind == 'rules-prepend':
        review = [{'rule_ref': ref, 'position': index, 'added_rule': value}
                  for index, (ref, value) in enumerate(material['ordered_additions'])]
    else:
        review = [{'rule_ref': ref, 'index': item['index'],
                   'selector': ','.join(item['expected'].split(',')[:2]),
                   'before_policy': item['expected'].split(',')[2],
                   'after_policy': binding['group_name']}
                  for ref, item in binding['rules'].items()
                  if ref in material['changed_rule_refs']]
    prepared = PrivatePreflight(candidate, plan, fingerprint, review, candidate_kind, base_source,
                                metadata_sources, extension_uid, linkage, deadline,
                                request_path=request_path, cancelled=cancelled,
                                target_source=target_source, target_ref=target_ref,
                                entry_request=entry_request, entry_basis=entry_basis)
    if plan is None:
        prepared.recheck_review()
    return prepared


class PrivatePreflight:
    __slots__ = ('_candidate', '_plan', '_request_digest', '_review', '_candidate_kind', '_base_source',
                 '_metadata_sources', '_extension_uid', '_linkage', '_deadline', '_request_path',
                 '_cancelled', '_target_source', '_target_ref', '_entry_request', '_entry_basis')

    def __init__(self, candidate, plan, request_digest, review, candidate_kind='merge-policy', base_source=None,
                 metadata_sources=None, extension_uid=None, linkage=None, deadline=None, *,
                 request_path=None, cancelled=lambda: False, target_source=None, target_ref=None,
                 entry_request=None, entry_basis=None):
        self._entry_request, self._entry_basis = entry_request, entry_basis
        self._deadline = deadline
        self._request_path, self._cancelled = request_path, cancelled
        self._candidate_kind, self._base_source = candidate_kind, base_source
        self._metadata_sources = metadata_sources or {}
        self._extension_uid, self._linkage = extension_uid, linkage
        self._candidate = candidate
        self._plan = plan
        self._request_digest = request_digest
        self._review = tuple(tuple(sorted(item.items())) for item in review)
        self._target_source, self._target_ref = target_source, target_ref

    def __repr__(self):
        return '<PrivatePreflight: native apply blocked; private data omitted>'

    def __reduce_ex__(self, protocol):
        raise TypeError('private repair preflight serialization disabled')

    def public_report(self, command='preflight'):
        if self._plan is None:
            self.recheck_review()
        result = {'schema_version': RESULT_SCHEMA, 'command': command,
                'status': 'planned_but_blocked', 'apply_supported': False,
                'changed_rules': self._candidate.preview().get('changed_rules', 0),
                'diff': {'operation': 'replace_existing_policy_tokens',
                         'other_bytes': 'preserved', 'values': 'private_review_required'},
                'blockers': list(NATIVE_BLOCKERS) + ['ACTION_AUTHORIZATION_PENDING'],
                'phase': 'PC0', 'claude_contact': 'not_performed',
                'context': 'host_binding_required',
                'file_freshness': 'matched_during_preflight',
                'application_reload': 'not_run', 'effective_routing': 'not_run',
                'recovery': 'not_needed_no_write', 'candidate_kind': self._candidate_kind}
        result['matched_rules'] = self._candidate.preview()['matched_rules']
        if self._candidate_kind == 'rules-prepend':
            candidate = self._candidate.preview()
            result['ownership'] = self._linkage.public_report()
            result['added_rules'] = candidate['added_rules']
            result['diff']['operation'] = candidate['operation']
            result['blockers'] = list(dict.fromkeys(candidate['blockers'] + self._linkage.public_report()['blockers']))
            result['priority_review'] = {key: candidate[key] for key in (
                'placement', 'known_base_overlap_count', 'known_append_overlap_count',
                'unknown_base_or_append_rule_count', 'protected_index_coverage')}
        if self._plan is None:
            result.update({'status': 'no_change_in_supplied_snapshot',
                           'artifact_write': 'not_created_no_change',
                           'native_acceptance': 'not_run'})
            result['diff'] = {'operation': 'none', 'other_bytes': 'preserved',
                              'values': 'no_changes'}
            result['blockers'] = [code for code in result['blockers']
                                  if code != 'ACTION_AUTHORIZATION_PENDING']
        return result

    def recheck_review(self, request_path=None, *, cancelled=None):
        """Fresh explicit-input check within the original preflight's scope/budget."""
        if self._request_path is None or self._deadline is None:
            raise RepairError('INVALID_REPAIR_REQUEST')
        if request_path is not None and request_path != self._request_path:
            raise RepairError('REQUEST_CHANGED')
        request_path = self._request_path
        def guard():
            _guard(self._cancelled, self._deadline)
            if self._entry_request != self._entry_basis:
                raise RepairError('ENVIRONMENT_ENTRY_CHANGED')
            try:
                environment_entry.require_entry(self._entry_request, 'offline_precheck', self._target_ref)
            except (environment_entry.InvalidProjection, environment_entry.EntryBlocked):
                raise RepairError('ENVIRONMENT_ENTRY_REQUIRED') from None
            if cancelled is not None:
                _guard(cancelled, self._deadline)
                if self._entry_request != self._entry_basis:
                    raise RepairError('ENVIRONMENT_ENTRY_CHANGED')
        guard()
        if self._plan is not None:
            tx._validate(self._plan, time.time())
            target_source = {'path': self._plan['path'], 'snapshot': self._plan['before'],
                             'parent_identity': self._plan['parent_identity']}
        else:
            if self._target_source is None:
                raise RepairError('INVALID_REPAIR_REQUEST')
            target_source = self._target_source
        if tx.digest(_load_request(request_path)) != self._request_digest:
            raise RepairError('REQUEST_CHANGED')
        guard()
        current = _read_source(target_source['path'])[1]
        if current != target_source:
            raise RepairError('STALE_FILE')
        for source in [self._base_source] + list(self._metadata_sources.values()):
            guard()
            _check_source(source)
        guard()

    def private_review(self):
        """For the authorized private host/user dialogue only. Never publish or log."""
        if self._plan is None:
            self.recheck_review()
        material = self._candidate.private_material()
        result = {'target_path': self._plan['path'] if self._plan is not None else self._target_source['path'],
                  'target_ref': self._plan['target_ref'] if self._plan is not None else self._target_ref,
                  'candidate_kind': self._candidate_kind,
                  'before_sha256': material['original_sha256'],
                  'after_sha256': material['candidate_sha256'],
                  'selected_rule_changes': [dict(item) for item in self._review],
                  'matched_rule_refs': list(material['matched_rule_refs']),
                  'blockers': self.public_report()['blockers'],
                  'application_reload': 'not_run', 'effective_routing': 'not_run'}
        if self._plan is not None:
            result['plan_digest'] = tx.digest(self._plan)
        else:
            result['status'] = 'no_change_in_supplied_snapshot'
        if self._candidate_kind == 'rules-prepend':
            insertion = material['byte_insertion']
            result.update({'operation': 'none' if insertion is None else 'insert_selected_prepend_rules',
                           'placement': 'before_all_base_rules',
                           'extension_uid': self._extension_uid,
                           'metadata_sources': {name: {'path': value['path'],
                                                       'sha256': value['snapshot']['sha256']}
                                                for name, value in self._metadata_sources.items()},
                           'base_source': {'path': self._base_source['path'],
                                           'sha256': self._base_source['snapshot']['sha256']},
                           'known_priority_overlaps': [
                               {'rule_ref': ref, 'source': source, 'index': index, 'rule': value}
                               for ref, source, index, value in material['known_priority_overlaps']],
                           'byte_insertion': None if insertion is None else {
                               'offset': insertion[0], 'text': insertion[2].decode('ascii')}})
        else:
            result['policy_token_edits'] = [
                {'start': start, 'end': end, 'before': before.decode('ascii'), 'after': after.decode('ascii')}
                for start, end, before, after in material['policy_token_edits']]
        return result


class PrivateArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, '{"status":"blocked","code":"INVALID_ARGUMENTS"}\n')


def main(argv=None):
    parser = PrivateArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'preflight', 'diff', 'execute'))
    parser.add_argument('--request', required=True, help='Exact private request JSON file')
    parser.add_argument('--target-path', required=True, help='Exact owned extension candidate')
    parser.add_argument('--target-ref', required=True)
    parser.add_argument('--entry-file', required=True, help='Explicit local sanitized environment-entry projection')
    parser.add_argument('--candidate-kind', choices=('merge-policy', 'rules-prepend'), default='merge-policy')
    parser.add_argument('--app-info', help='Exact separately authorized application Info.plist')
    parser.add_argument('--profile-index', help='Exact separately authorized profiles.yaml')
    parser.add_argument('--extension-uid', help='Explicit selected rules extension UID')
    parser.add_argument('--base-path', help='Exact separately authorized base configuration for rules-prepend')
    parser.add_argument('--max-seconds', type=float, default=30)
    parser.add_argument('--private-review', action='store_true',
                        help='Explicit private-host selected-rule diff; never public logs or exports')
    parser.add_argument('--plan-file', help='Exact retained private plan artifact')
    parser.add_argument('--plan-digest', help='Exact reviewed plan digest; integrity, not approval')
    parser.add_argument('--backup-directory', help='Already-existing private recovery root')
    args = parser.parse_args(argv)
    try:
        import repair_execution as execution
        import inventory_cli
        try:
            entry_request = inventory_cli.read_request(args.entry_file)
            environment_entry.require_entry(entry_request,
                'configuration' if args.command == 'execute' else 'offline_precheck', args.target_ref)
        except (inventory_cli.InputError, environment_entry.InvalidProjection, environment_entry.EntryBlocked):
            raise RepairError('ENVIRONMENT_ENTRY_REQUIRED') from None
        if args.command == 'execute':
            if args.private_review:
                raise RepairError('INVALID_ARGUMENTS')
            if not all((args.plan_file, args.plan_digest, args.backup_directory)):
                raise RepairError('EXACT_RETAINED_PLAN_REQUIRED')
            result = execution.execute(request_path=args.request, plan_path=args.plan_file,
                                       plan_digest=args.plan_digest, target_path=args.target_path,
                                       target_ref=args.target_ref, backup_directory=args.backup_directory,
                                       max_seconds=args.max_seconds, candidate_kind=args.candidate_kind,
                                       base_path=args.base_path, app_info_path=args.app_info,
                                       profile_index_path=args.profile_index, extension_uid=args.extension_uid,
                                       entry_request=entry_request)
            print(json.dumps(result, sort_keys=True), flush=True)
            return 0
        if args.plan_digest or (args.backup_directory and not args.plan_file):
            raise RepairError('INVALID_ARGUMENTS')
        if args.plan_file and (args.command != 'plan' or not args.backup_directory):
            raise RepairError('INVALID_ARGUMENTS')
        if args.private_review and args.command not in ('diff', 'plan'):
            raise RepairError('INVALID_ARGUMENTS')
        prepared = preflight(args.request, args.target_path, args.target_ref,
                             max_seconds=args.max_seconds, candidate_kind=args.candidate_kind,
                             base_path=args.base_path, app_info_path=args.app_info,
                                       profile_index_path=args.profile_index, extension_uid=args.extension_uid,
                                       entry_request=entry_request)
        result = prepared.public_report(args.command)
        if args.plan_file and prepared._plan is not None:
            result['retained_plan_digest'] = execution.retain(prepared, plan_path=args.plan_file,
                                                            backup_directory=args.backup_directory)
            result['artifact_write'] = 'private_plan_retained'
            result['recovery'] = 'no_target_write_private_plan_retained'
        review = None
        if args.private_review:
            prepared.recheck_review(args.request)
            review = prepared.private_review()
            if args.plan_file and prepared._plan is not None:
                review.update({'retained_plan_digest': result['retained_plan_digest'],
                               'backup_directory': args.backup_directory,
                               'action_id': prepared._plan['action_id'],
                               'expires_at': prepared._plan['expires_at']})
        if prepared._plan is None:
            prepared.recheck_review()
        if review is not None:
            print(json.dumps(review, sort_keys=True), flush=True)
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0
    except (RepairError, tx.TransactionError, edits.EditPlanError, rules_edits.RulesPlanError, ownership.OwnershipError) as exc:
        print(json.dumps({'schema_version': RESULT_SCHEMA, 'status': 'blocked',
                          'code': getattr(exc, 'code', str(exc)),
                          'apply_supported': False,
                          'recovery_id': getattr(exc, 'recovery_id', None),
                          'recovery': 'inspect_retained_batch_no_automatic_retry'
                          if getattr(exc, 'recovery_id', None) else 'no_receipt_reported'}), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print('{"status":"blocked","code":"CANCELLED"}', file=sys.stderr)
        return 130
    except OSError:
        print('{"status":"blocked","code":"IO_FAILURE"}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
