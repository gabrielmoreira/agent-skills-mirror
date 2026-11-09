"""Offline, private byte candidates for a deliberately narrow YAML rule subset.

No file, controller, transaction, or apply interface. Caller-supplied ownership,
versions and scope are declarations, not native evidence or authorization.
"""
import hashlib
import re

try:
    import yaml
except ImportError:
    yaml = None

from remedy_plans import compile_plan, InvalidProjection

MAX_BYTES = 4 * 1024 * 1024
MAX_NODES = 20000
_ALLOWED_BLOCKERS = {'NATIVE_SCHEMA_ADAPTER_NOT_IMPLEMENTED',
                     'NATIVE_ACCEPTANCE_NOT_RUN', 'VERSION_CAPABILITY_UNVERIFIED'}
_RULE = re.compile(r'(DOMAIN|DOMAIN-SUFFIX),([A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?),([A-Za-z][A-Za-z0-9_-]{0,63})\Z')
_GROUP = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,63}\Z')
_DOMAIN_LABEL = re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\Z')


class EditPlanError(ValueError):
    """Only fixed, non-sensitive codes are emitted."""


def _fail(code):
    raise EditPlanError(code) from None


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


class PrivateCandidate:
    """Explicit private access only; not a transaction plan or serializable report."""
    __slots__ = ('_original', '_candidate', '_count', '_binding', '_edits',
                 '_matched_refs', '_changed_refs')

    def __init__(self, original, candidate, count, binding, edits=(), *,
                 matched_rule_refs=(), changed_rule_refs=()):
        self._original, self._candidate, self._count = original, candidate, count
        self._binding = binding
        self._edits = tuple((start, end, original[start:end], replacement)
                            for start, end, replacement in edits)
        self._matched_refs = tuple(matched_rule_refs)
        self._changed_refs = tuple(changed_rule_refs)

    def __repr__(self):
        return '<PrivateCandidate: blocked, private content omitted>'

    def __reduce_ex__(self, protocol):
        raise TypeError('private candidate serialization disabled')

    def private_material(self):
        """Trusted local review only. Never log, export, or persist by default."""
        return {'original_bytes': self._original, 'candidate_bytes': self._candidate,
                'declared_binding': self._binding,
                'policy_token_edits': self._edits,
                'matched_rule_refs': self._matched_refs,
                'changed_rule_refs': self._changed_refs,
                'original_sha256': _hash(self._original),
                'candidate_sha256': _hash(self._candidate)}

    def preview(self):
        no_change = self._candidate == self._original
        return {'schema_version': 'guardian-config-edit-preview/0.1',
                'status': ('no_change_in_supplied_snapshot'
                           if no_change else 'candidate_only_blocked'),
                'changed_rules': self._count, 'matched_rules': len(self._matched_refs),
                'apply_supported': False,
                'authorization': 'not_required_for_snapshot_observation' if no_change else 'pending',
                'blockers': sorted(_ALLOWED_BLOCKERS) + ([] if no_change else ['ACTION_AUTHORIZATION_PENDING']),
                'native_compatibility': 'unknown', 'native_acceptance': 'not_run',
                'ownership_and_scope': 'declared_unverified',
                'unrelated_bytes': 'preserved'}


def _parse(raw):
    if yaml is None:
        _fail('PARSER_UNAVAILABLE')
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        _fail('INVALID_OR_OVERSIZED_SNAPSHOT')
    try:
        text = raw.decode('utf-8')
        depth = count = documents = 0
        for event in yaml.parse(text, Loader=yaml.SafeLoader):
            count += 1
            if count > MAX_NODES:
                _fail('YAML_BUDGET_EXCEEDED')
            if (isinstance(event, yaml.events.AliasEvent) or
                    getattr(event, 'anchor', None) or getattr(event, 'tag', None)):
                _fail('UNSUPPORTED_YAML')
            if isinstance(event, yaml.events.DocumentStartEvent):
                documents += 1
                if documents != 1 or event.version is not None or event.tags:
                    _fail('UNSUPPORTED_YAML')
            if isinstance(event, (yaml.events.SequenceStartEvent, yaml.events.MappingStartEvent)):
                depth += 1
                if depth > 48:
                    _fail('YAML_BUDGET_EXCEEDED')
            if isinstance(event, (yaml.events.SequenceEndEvent, yaml.events.MappingEndEvent)):
                depth -= 1
        root = yaml.compose(text, Loader=yaml.SafeLoader)
        # Validate every mapping, including unrelated nested keys; no merge keys.
        def visit(node):
            if isinstance(node, yaml.nodes.MappingNode):
                keys = set()
                for key, value in node.value:
                    if (not isinstance(key, yaml.nodes.ScalarNode) or
                            key.tag != 'tag:yaml.org,2002:str' or
                            key.value == '<<' or key.value in keys):
                        _fail('AMBIGUOUS_MAPPING')
                    keys.add(key.value)
                    visit(value)
            elif isinstance(node, yaml.nodes.SequenceNode):
                for child in node.value:
                    visit(child)
        if not isinstance(root, yaml.nodes.MappingNode) or root.flow_style:
            _fail('UNSUPPORTED_YAML')
        visit(root)
        return text, root
    except EditPlanError:
        raise
    except (UnicodeError, yaml.YAMLError, ValueError, TypeError, RecursionError):
        _fail('INVALID_YAML')


def _mapping(node):
    if not isinstance(node, yaml.nodes.MappingNode):
        _fail('UNSUPPORTED_STRUCTURE')
    return {key.value: value for key, value in node.value}


def _signature(node):
    """Compare syntax-tree semantic values without running YAML constructors."""
    if isinstance(node, yaml.nodes.ScalarNode):
        return (node.tag, node.value)
    if isinstance(node, yaml.nodes.SequenceNode):
        return (node.tag, tuple(_signature(child) for child in node.value))
    return (node.tag, tuple((_signature(key), _signature(value)) for key, value in node.value))


def _valid_domain(value):
    # The editable slice is ASCII DNS labels, not a wildcard/IDNA interpreter.
    return len(value) <= 253 and all(_DOMAIN_LABEL.fullmatch(label)
                                     for label in value.split('.'))


def _provably_shadowed(rules, index, domain):
    """Detect only complete coverage by known, earlier, unconditional rules.

    Other rule types, modifiers and provider expansions remain unverified; this
    is not a first-match proof or native effective-configuration validation.
    """
    domain = domain.lower()
    for earlier in rules[:index]:
        if (not isinstance(earlier, yaml.nodes.ScalarNode) or
                earlier.tag != 'tag:yaml.org,2002:str'):
            continue
        fields = [field.strip() for field in earlier.value.split(',')]
        kind = fields[0].upper()
        if kind == 'MATCH' and len(fields) == 2 and fields[1]:
            return True
        if kind != 'DOMAIN-SUFFIX' or len(fields) != 3 or not fields[2]:
            continue
        suffix = fields[1].lower().rstrip('.')
        if _valid_domain(suffix) and (domain == suffix or domain.endswith('.' + suffix)):
            return True
    return False


def compile_edit_plan(raw, remedy_request, binding):
    """Compile bytes supplied by the caller; never read the user's configuration.

    binding has exact schema: schema_version, target_ref, scope_refs, layer_ref,
    layer_kind, group_name, rules (rule-ref -> {index, expected}). Binding strings
    are private. All assertions remain unverified. No authorization flags accepted.
    """
    try:
        semantic = compile_plan(remedy_request)
    except (InvalidProjection, TypeError, ValueError, RecursionError):
        _fail('INVALID_REMEDY_REQUEST')
    fields = {'schema_version', 'target_ref', 'scope_refs', 'layer_ref',
              'layer_kind', 'group_name', 'rules'}
    if type(binding) is not dict or set(binding) != fields:
        _fail('INVALID_BINDING')
    if (binding['schema_version'] != 'guardian-config-edit-binding/0.1' or
            binding['layer_kind'] != 'owned-profile-extension'):
        _fail('UNSUPPORTED_BINDING')
    if (binding['target_ref'] != remedy_request['target_ref'] or
            binding['scope_refs'] != remedy_request['scope_refs']):
        _fail('TARGET_OR_SCOPE_MISMATCH')
    layer = binding['layer_ref']
    if type(layer) is not str or layer not in remedy_request['revisions']:
        _fail('REVISION_BINDING_MISSING')
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        _fail('INVALID_OR_OVERSIZED_SNAPSHOT')
    if _hash(raw) != remedy_request['revisions'][layer]:
        _fail('SNAPSHOT_REVISION_MISMATCH')
    if (remedy_request['template'] != 'keep-existing' or
            {item['code'] for item in semantic['blockers']} != _ALLOWED_BLOCKERS):
        _fail('SEMANTIC_PLAN_BLOCKED')
    proposals = semantic['proposed_changes']
    if len(proposals) != 1 or proposals[0]['kind'] != 'bind_selected_rules':
        _fail('UNSUPPORTED_REMEDY')
    rule_bindings, group = binding['rules'], binding['group_name']
    if (type(rule_bindings) is not dict or not rule_bindings or
            set(rule_bindings) != set(proposals[0]['rule_refs']) or
            type(group) is not str or not _GROUP.fullmatch(group) or group in ('DIRECT', 'REJECT')):
        _fail('INVALID_RULE_BINDING')
    # The group alias must bind to this exact private name, not a different graph.
    if group != proposals[0]['egress_group_ref']:
        _fail('EGRESS_BINDING_MISMATCH')
    text, root = _parse(raw)
    top = _mapping(root)
    rules = top.get('rules')
    groups = top.get('proxy-groups')
    if (not isinstance(rules, yaml.nodes.SequenceNode) or rules.flow_style or
            not isinstance(groups, yaml.nodes.SequenceNode)):
        _fail('UNSUPPORTED_STRUCTURE')
    names = []
    for node in groups.value:
        name = _mapping(node).get('name')
        if not isinstance(name, yaml.nodes.ScalarNode) or name.tag != 'tag:yaml.org,2002:str':
            _fail('UNSUPPORTED_STRUCTURE')
        names.append(name.value)
    if len(names) != len(set(names)) or names.count(group) != 1:
        _fail('EGRESS_GROUP_MISSING_OR_AMBIGUOUS')
    edits, indexes, matched_refs, changed_refs = [], set(), [], []
    for ref in proposals[0]['rule_refs']:
        item = rule_bindings[ref]
        if type(item) is not dict or set(item) != {'index', 'expected'}:
            _fail('INVALID_RULE_BINDING')
        index = item['index']
        if type(index) is not int or not 0 <= index < len(rules.value) or index in indexes:
            _fail('AMBIGUOUS_RULE_SELECTION')
        indexes.add(index)
        node = rules.value[index]
        if (not isinstance(node, yaml.nodes.ScalarNode) or node.style is not None or
                node.tag != 'tag:yaml.org,2002:str' or
                node.start_mark.line != node.end_mark.line or node.value != item['expected']):
            _fail('UNSUPPORTED_OR_CHANGED_RULE')
        match = _RULE.fullmatch(node.value)
        if not match or not _valid_domain(match.group(2)):
            _fail('AMBIGUOUS_OR_UNSUPPORTED_RULE')
        # Conservative comparison only, never broaden the editable grammar.
        # Case, field padding and DNS root-dot variants may denote the same
        # selector even when their spelling is outside this compiler's subset.
        def selector(value):
            parts = value.split(',')
            if len(parts) < 2:
                return None
            return (parts[0].strip().upper(), parts[1].strip().lower().rstrip('.'))
        selected = selector(node.value)
        if sum(selector(n.value) == selected for n in rules.value
               if isinstance(n, yaml.nodes.ScalarNode)) != 1:
            _fail('AMBIGUOUS_OR_UNSUPPORTED_RULE')
        if _provably_shadowed(rules.value, index, match.group(2)):
            _fail('SELECTED_RULE_SHADOWED')
        # PyYAML indexes Unicode characters; splice bytes only after conversion.
        start_char = node.start_mark.index + match.start(3)
        end_char = node.end_mark.index
        if text[node.start_mark.index:end_char] != node.value:
            _fail('UNSUPPORTED_SCALAR_ENCODING')
        # Matching policy tokens still require every selection/semantic check.
        # They are reported separately and never become empty byte edits.
        if match.group(3) == group:
            matched_refs.append(ref)
            continue
        start, end = len(text[:start_char].encode('utf-8')), len(text[:end_char].encode('utf-8'))
        edits.append((start, end, group.encode('ascii')))
        changed_refs.append(ref)
        node.value = node.value[:match.start(3)] + group
    edits.sort()
    if any(left[1] > right[0] for left, right in zip(edits, edits[1:])):
        _fail('OVERLAPPING_EDITS')
    candidate = raw
    for start, end, replacement in reversed(edits):
        candidate = candidate[:start] + replacement + candidate[end:]
    _, after = _parse(candidate)
    if _signature(root) != _signature(after):
        _fail('UNEXPECTED_SEMANTIC_DELTA')
    declared_binding = (remedy_request['target_ref'], tuple(remedy_request['scope_refs']),
                        layer, tuple(sorted(remedy_request['revisions'].items())),
                        tuple(sorted(remedy_request['facts']['versions'].items())))
    return PrivateCandidate(raw, candidate, len(edits), declared_binding, edits,
                            matched_rule_refs=matched_refs, changed_rule_refs=changed_refs)
