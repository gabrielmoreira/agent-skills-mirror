"""Offline additions or exact-repeat recognition for a narrow prepend list.

This is not the merge-mapping policy-token editor. It never replaces base rules,
executes scripts, writes files, or admits native repair. Supplied graph/ownership/
protected-index facts remain declarations. Source semantics are pinned to
4337bd85758d54d7b9044b2da3c9ac1176eae1f3/src-tauri/src/enhance/seq.rs.
"""
import hashlib
import re
import time

import config_edit_plan as config
from remedy_plans import compile_plan, InvalidProjection

SCHEMA = 'guardian-rules-extension-binding/0.1'
NATIVE_BLOCKERS = ('NATIVE_SCHEMA_ADAPTER_NOT_IMPLEMENTED',
                   'VERSION_CAPABILITY_UNVERIFIED', 'NATIVE_ACCEPTANCE_NOT_RUN')


class RulesPlanError(ValueError):
    """Stable codes without supplied private values."""


def _fail(code):
    raise RulesPlanError(code) from None


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _parse(raw):
    try:
        return config._parse(raw)
    except config.EditPlanError as exc:
        _fail(str(exc))


def _mapping(node):
    try:
        return config._mapping(node)
    except config.EditPlanError:
        _fail('UNSUPPORTED_STRUCTURE')


def _strings(node):
    yaml = config.yaml
    if not isinstance(node, yaml.nodes.SequenceNode):
        _fail('EXPECTED_RULE_SEQUENCE')
    values = []
    for item in node.value:
        if not isinstance(item, yaml.nodes.ScalarNode) or item.tag != 'tag:yaml.org,2002:str':
            _fail('UNSUPPORTED_RULE_VALUE')
        values.append(item.value)
    return values


def _selector(value):
    fields = [part.strip() for part in value.split(',')]
    if len(fields) < 2 or fields[0].upper() not in ('DOMAIN', 'DOMAIN-SUFFIX'):
        return None
    domain = fields[1].lower().rstrip('.')
    return (fields[0].upper(), domain)


def _known_rule(value):
    fields = [part.strip() for part in value.split(',')]
    if len(fields) == 2 and fields[0].upper() == 'MATCH' and fields[1]:
        return ('MATCH', '', fields[1])
    selected = _selector(value)
    if (selected is None or len(fields) != 3 or not fields[2]
            or not config._valid_domain(selected[1])):
        return None
    return (*selected, fields[2])


def _overlap(a, b):
    if a[0] == 'MATCH' or b[0] == 'MATCH':
        return True
    if a[0] == b[0] == 'DOMAIN':
        return a[1] == b[1]
    def inside(domain, suffix):
        return domain == suffix or domain.endswith('.' + suffix)
    if a[0] == 'DOMAIN' and b[0] == 'DOMAIN-SUFFIX':
        return inside(a[1], b[1])
    if b[0] == 'DOMAIN' and a[0] == 'DOMAIN-SUFFIX':
        return inside(b[1], a[1])
    return inside(a[1], b[1]) or inside(b[1], a[1])


class PrivateRulesCandidate:
    __slots__ = ('_original', '_candidate', '_binding', '_additions', '_overlaps',
                 '_edit', '_unknown', '_matched_refs')

    def __init__(self, original, candidate, binding, additions, overlaps, edit, unknown, *,
                 matched_rule_refs=()):
        self._original, self._candidate = original, candidate
        self._binding, self._additions = binding, tuple(additions)
        self._overlaps, self._edit, self._unknown = tuple(overlaps), edit, unknown
        self._matched_refs = tuple(matched_rule_refs)

    def __repr__(self):
        return '<PrivateRulesCandidate: native apply blocked; private data omitted>'

    def __reduce_ex__(self, protocol):
        raise TypeError('private rules candidate serialization disabled')

    def preview(self):
        no_change = self._candidate == self._original
        return {'schema_version': 'guardian-rules-extension-preview/0.1',
                'status': ('no_change_in_supplied_snapshot'
                           if no_change else 'candidate_only_blocked'),
                'apply_supported': False,
                'operation': 'insert_selected_prepend_rules', 'added_rules': len(self._additions),
                'matched_rules': len(self._matched_refs),
                'placement': 'explicit_prepend_before_base_rules',
                'known_base_overlap_count': sum(x[1] == 'base' for x in self._overlaps),
                'known_append_overlap_count': sum(x[1] == 'append' for x in self._overlaps),
                'unknown_base_or_append_rule_count': self._unknown,
                'protected_index_coverage': 'caller_declared_unverified',
                'other_bytes': 'preserved', 'append_and_delete': 'unchanged',
                'authorization': 'not_required_for_snapshot_observation' if no_change else 'pending',
                'native_acceptance': 'not_run',
                'blockers': list(NATIVE_BLOCKERS) + ['EFFECTIVE_RULE_PRIORITY_UNVERIFIED',
                    'BASE_RULE_GRAPH_UNVERIFIED', 'GROUP_GRAPH_UNVERIFIED',
                    'PROTECTED_RULE_COVERAGE_UNVERIFIED',
                    'LATER_MERGE_SCRIPT_EFFECTS_UNVERIFIED']
                    + ([] if no_change else ['ACTION_AUTHORIZATION_PENDING'])}

    def private_material(self):
        """Only the authorized private host/user dialogue; never public exports."""
        return {'original_bytes': self._original, 'candidate_bytes': self._candidate,
                'original_sha256': _hash(self._original), 'candidate_sha256': _hash(self._candidate),
                'declared_binding': self._binding,
                'ordered_additions': self._additions,
                'matched_rule_refs': self._matched_refs,
                'known_priority_overlaps': self._overlaps,
                'byte_insertion': self._edit}


def compile_rules_extension(raw, base_raw, request, binding, *, max_seconds=5,
                            cancelled=lambda: False):
    """Compile explicit selected prepend additions, without any I/O or approval.

    Every protected index supplied by the caller is checked. An empty index list
    declares no known protected entries; it never proves their actual absence.
    Unknown rule forms and later transformations never become a safety proof.
    """
    if type(max_seconds) not in (int, float) or not 0 < max_seconds <= 60:
        _fail('INVALID_DEADLINE')
    deadline = time.monotonic() + max_seconds
    def guard():
        try:
            stopped = cancelled()
        except Exception:
            _fail('CANCELLED')
        if stopped:
            _fail('CANCELLED')
        if time.monotonic() >= deadline:
            _fail('DEADLINE_EXCEEDED')
    guard()
    try:
        semantic = compile_plan(request)
    except (InvalidProjection, TypeError, ValueError, RecursionError):
        _fail('INVALID_REMEDY_REQUEST')
    fields = {'schema_version', 'operation', 'target_ref', 'scope_refs', 'layer_ref',
              'base_layer_ref', 'layer_kind', 'placement', 'group_name', 'rules',
              'rule_order', 'protected_rule_indexes'}
    if type(binding) is not dict or set(binding) != fields:
        _fail('INVALID_BINDING')
    if (binding['schema_version'] != SCHEMA or binding['operation'] != 'insert_selected_prepend_rules'
            or binding['layer_kind'] != 'owned-profile-rules-extension'
            or binding['placement'] != 'prepend'):
        _fail('EXPLICIT_PREPEND_OPERATION_REQUIRED')
    if binding['target_ref'] != request['target_ref'] or binding['scope_refs'] != request['scope_refs']:
        _fail('TARGET_OR_SCOPE_MISMATCH')
    if (request['template'] != 'keep-existing'
            or {item['code'] for item in semantic['blockers']} != set(NATIVE_BLOCKERS)):
        _fail('SEMANTIC_PLAN_BLOCKED')
    versions = request['facts']['versions']
    if versions['product'] != 'clash-verge-rev' or versions['gui'] != '2.5.8':
        _fail('UNSUPPORTED_PRODUCT_OR_VERSION')
    layer, base_layer = binding['layer_ref'], binding['base_layer_ref']
    if (type(layer) is not str or type(base_layer) is not str or layer == base_layer
            or layer not in request['revisions'] or base_layer not in request['revisions']):
        _fail('REVISION_BINDING_MISSING')
    for blob, ref in ((raw, layer), (base_raw, base_layer)):
        if type(blob) is not bytes or len(blob) > config.MAX_BYTES:
            _fail('INVALID_OR_OVERSIZED_SNAPSHOT')
        if _hash(blob) != request['revisions'][ref]:
            _fail('SNAPSHOT_REVISION_MISMATCH')
    proposals = semantic['proposed_changes']
    if len(proposals) != 1 or proposals[0]['kind'] != 'bind_selected_rules':
        _fail('UNSUPPORTED_REMEDY')
    order = binding['rule_order']
    rules, group = binding['rules'], binding['group_name']
    if (type(order) is not list or order != proposals[0]['rule_refs']
            or type(rules) is not dict or set(rules) != set(order)
            or type(group) is not str or not config._GROUP.fullmatch(group)
            or group in ('DIRECT', 'REJECT') or group != proposals[0]['egress_group_ref']):
        _fail('INVALID_RULE_SELECTION')
    guard()
    text, root = _parse(raw)
    extension = _mapping(root)
    # Unknown extension fields remain byte-for-byte intact, but cannot replace
    # any of the three mandatory SeqMap fields in this supported format.
    prepend = extension.get('prepend')
    existing = {key: _strings(extension.get(key)) for key in ('prepend', 'append', 'delete')}
    if existing['delete']:
        _fail('DELETE_SEQUENCE_UNSUPPORTED')
    start_char, end_char = prepend.start_mark.index, prepend.end_mark.index
    if existing['prepend']:
        if not prepend.flow_style or prepend.start_mark.line != prepend.end_mark.line:
            _fail('NONEMPTY_PREPEND_UNSUPPORTED')
    elif (prepend.start_mark.line != prepend.end_mark.line
            or not re.fullmatch(r'\[[ \t]*\]', text[start_char:end_char])):
        _fail('EMPTY_INLINE_PREPEND_REQUIRED')
    _, base_root = _parse(base_raw)
    base = _mapping(base_root)
    base_rules = _strings(base.get('rules'))
    groups = base.get('proxy-groups')
    if not isinstance(groups, config.yaml.nodes.SequenceNode):
        _fail('BASE_GROUPS_REQUIRED')
    names = []
    for item in groups.value:
        node = _mapping(item).get('name')
        if not isinstance(node, config.yaml.nodes.ScalarNode) or node.tag != 'tag:yaml.org,2002:str':
            _fail('INVALID_BASE_GROUP')
        names.append(node.value)
    if len(names) != len(set(names)) or names.count(group) != 1:
        _fail('EGRESS_GROUP_MISSING_OR_AMBIGUOUS')
    protected = binding['protected_rule_indexes']
    if (type(protected) is not list or any(type(i) is not int or not 0 <= i < len(base_rules)
                                         for i in protected) or len(set(protected)) != len(protected)):
        _fail('INVALID_PROTECTED_RULE_INDEXES')
    known = [_known_rule(value) for value in base_rules]
    append_known = [_known_rule(value) for value in existing['append']]
    if any(known[i] is None for i in protected):
        _fail('PROTECTED_RULE_TYPE_UNSUPPORTED')
    additions, selectors, overlaps = [], [], []
    all_existing = base_rules + existing['append']
    for ref in order:
        guard()
        item = rules[ref]
        if (type(item) is not dict or set(item) != {'kind', 'domain'}
                or item['kind'] not in ('DOMAIN', 'DOMAIN-SUFFIX')
                or type(item['domain']) is not str or not item['domain'].isascii()
                or not config._valid_domain(item['domain'])):
            _fail('INVALID_SELECTED_RULE')
        selected = (item['kind'], item['domain'].lower())
        if any(_overlap(selected, other) for other in selectors):
            _fail('OVERLAPPING_SELECTED_RULES')
        if any(_selector(value) == selected for value in all_existing):
            _fail('RULE_SELECTOR_ALREADY_PRESENT')
        layered = ([('base', index, value) for index, value in enumerate(known)]
                   + [('append', index, value) for index, value in enumerate(append_known)])
        for source, index, existing_rule in layered:
            if index % 128 == 0:
                guard()
            if existing_rule is None or not _overlap(selected, existing_rule):
                continue
            if source == 'base' and index in protected:
                _fail('PROTECTED_RULE_PRIORITY_CONFLICT')
            if len(overlaps) >= 2048:
                _fail('PRIORITY_ANALYSIS_BUDGET_EXCEEDED')
            original_rule = base_rules[index] if source == 'base' else existing['append'][index]
            overlaps.append((ref, source, index, original_rule))
        selectors.append(selected)
        additions.append((ref, item['kind'] + ',' + item['domain'] + ',' + group))
    matched_refs = ()
    if existing['prepend']:
        # Only a complete ordered repeat is supported, never a partial merge.
        # Base/append selectors, protected priority and every selection have
        # already been checked, even when the supplied bytes need no edit.
        if existing['prepend'] != [rule for _, rule in additions]:
            _fail('NONEMPTY_PREPEND_UNSUPPORTED')
        candidate, edit = raw, None
        matched_refs, additions = tuple(order), []
    else:
        insertion = ', '.join("'" + rule + "'" for _, rule in additions).encode('ascii')
        offset = len(text[:start_char + 1].encode('utf-8'))
        candidate = raw[:offset] + insertion + raw[offset:]
        edit = (offset, b'', insertion)
        prepend.value = [config.yaml.nodes.ScalarNode('tag:yaml.org,2002:str', rule)
                         for _, rule in additions]
    if len(candidate) > config.MAX_BYTES:
        _fail('CANDIDATE_TOO_LARGE')
    guard()
    _, after = _parse(candidate)
    # Compare the entire syntax tree, changing only the expected prepend values.
    if config._signature(root) != config._signature(after):
        _fail('UNEXPECTED_SEMANTIC_DELTA')
    guard()
    declared = (request['target_ref'], tuple(request['scope_refs']), layer, base_layer,
                tuple(sorted(request['revisions'].items())), tuple(sorted(versions.items())),
                tuple(protected), tuple(order), 'prepend')
    unknown = sum(item is None for item in known) + sum(item is None for item in append_known)
    return PrivateRulesCandidate(raw, candidate, declared, additions, overlaps,
                                 edit, unknown, matched_rule_refs=matched_refs)
