"""Pure, versioned environment-entry eligibility; no executor, I/O or consent.

This contract is for environment actions, not a prerequisite for subscription
explanations. First select local/VM/VPS, then describe the network resources and
configuration, then evaluate diagnostic entry. Owning a VPS selects no route.

All inputs are sanitized declarations. Even ``effective`` is a reported state,
not a native observation. Distinct VM aliases do not prove distinct real targets.
The host must establish current target/user/namespace bindings and use the
existing workflow/contact/action authorization gates immediately before action.
No result from this module grants, persists, restores or revokes permission.

The input has no URLs, addresses, credentials, UUIDs, configuration text, clock,
approval flags or callbacks. Alias syntax reduces accidental disclosure; it
cannot prove that a caller supplied genuinely non-identifying aliases. The host
must do that sanitization. Local listener kinds and final proxy protocols follow
remedy_plans: an HTTP/mixed listener may lead to a SOCKS5 final proxy, while a
SOCKS listener is not direct Claude Code proxy configuration.
"""
import re


SCHEMA = 'guardian-environment-entry-input/0.1'
RESULT_SCHEMA = 'guardian-environment-entry/0.1'
ROUTES = ('local', 'vm', 'vps', 'compare', 'unknown', 'none')
ROUTE_STATES = ('unasked', 'selected', 'unknown', 'declined', 'conflict',
                'stale', 'withdrawn')
RESOURCE_SELECTIONS = ('selected', 'direct', 'unselected', 'comparing', 'unknown',
                       'declined', 'conflict', 'stale', 'withdrawn')
CONFIGURATION_STATES = ('absent', 'imported', 'effective', 'not_applicable',
                        'unknown', 'conflict', 'stale')
LOCAL_ENTRY_KINDS = ('http', 'mixed', 'socks', 'unknown', 'none')
# Keep these spellings aligned with remedy_plans facts.groups[*].protocol.
# Direct is a terminal kind there, not a proxy protocol.
FINAL_PROXY_PROTOCOLS = ('http', 'socks5', 'shadowsocks', 'vmess', 'vless',
                         'trojan', 'hysteria2', 'tuic', 'wireguard', 'unknown')
_TARGET_ROLES = ('local', 'vm_host', 'vm_guest', 'vps')
_REQUIRED_ROLES = {'local': ('local',), 'vm': ('vm_host', 'vm_guest'),
                   'vps': ('vps',)}
_CONFIGURATION_READINESS = {
    'absent': 'not_configured_plan_before_changes',
    'imported': 'imported_effectiveness_unverified',
    'effective': 'reported_effective_host_verification_required',
    'not_applicable': 'no_proxy_configuration_reported',
    'unknown': 'unknown_precheck_first',
    'conflict': 'revalidate_before_changes',
    'stale': 'revalidate_before_changes',
}


class InvalidProjection(ValueError):
    """Reject malformed input with a fixed code, never a submitted value."""


class EntryBlocked(ValueError):
    """Entry ineligible; ``gaps`` contains only fixed contract error codes."""

    def __init__(self, gaps):
        super().__init__('E_ENTRY_BLOCKED')
        self.gaps = tuple(gaps)


def _object(value, allowed, required):
    # Reject subclasses too: do not invoke caller-defined mapping/string hooks.
    if (type(value) is not dict or len(value) > len(allowed)
            or any(type(key) is not str for key in value)
            or set(value) - set(allowed) or set(required) - set(value)):
        raise InvalidProjection('E_OBJECT_SHAPE')


def _enum(value, choices):
    if type(value) is not str or value not in choices:
        raise InvalidProjection('E_ENUM_VALUE')


def _alias(value):
    # Match existing target/CLI alias spelling, without inventing new prefixes.
    # Syntax is not a guarantee of privacy: sanitization remains the host's job.
    if (type(value) is not str or len(value) > 48
            or re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,47}', value) is None
            or re.search(r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-'
                         r'[a-fA-F0-9]{4}-[a-fA-F0-9]{12}', value) is not None
            or re.fullmatch(r'[a-fA-F0-9]{32,48}', value) is not None):
        raise InvalidProjection('E_ALIAS')


def _validate(request):
    fields = ('schema_version', 'route', 'targets', 'network', 'local_entry',
              'final_egress', 'client')
    _object(request, fields, fields)
    if type(request['schema_version']) is not str or request['schema_version'] != SCHEMA:
        raise InvalidProjection('E_SCHEMA_VERSION')
    route = request['route']
    _object(route, ('choice', 'state'), ('choice', 'state'))
    _enum(route['choice'], ROUTES)
    _enum(route['state'], ROUTE_STATES)
    targets = request['targets']
    if type(targets) is not list or len(targets) > len(_TARGET_ROLES):
        raise InvalidProjection('E_TARGET_LIST')
    roles, aliases = set(), set()
    for target in targets:
        _object(target, ('role', 'target_ref'), ('role', 'target_ref'))
        _enum(target['role'], _TARGET_ROLES)
        _alias(target['target_ref'])
        if target['role'] in roles:
            raise InvalidProjection('E_DUPLICATE_TARGET_ROLE')
        roles.add(target['role'])
        # Equal aliases cannot declare separate host and guest targets. Unequal
        # aliases still require independent verification by the host.
        if target['target_ref'] in aliases:
            raise InvalidProjection('E_DUPLICATE_TARGET_ALIAS')
        aliases.add(target['target_ref'])
    network = request['network']
    fields = ('possession', 'selection', 'configuration', 'path', 'resource_ref')
    _object(network, fields, fields[:-1])
    _enum(network['possession'], ('present', 'none', 'unknown'))
    _enum(network['selection'], RESOURCE_SELECTIONS)
    _enum(network['configuration'], CONFIGURATION_STATES)
    _enum(network['path'], ('explicit', 'tun', 'direct', 'unknown'))
    if 'resource_ref' in network:
        _alias(network['resource_ref'])
    entry = request['local_entry']
    _object(entry, ('kind', 'entry_ref'), ('kind',))
    _enum(entry['kind'], LOCAL_ENTRY_KINDS)
    if 'entry_ref' in entry:
        _alias(entry['entry_ref'])
    egress = request['final_egress']
    _object(egress, ('kind', 'protocol'), ('kind', 'protocol'))
    _enum(egress['kind'], ('proxy', 'direct', 'unknown'))
    _enum(egress['protocol'], FINAL_PROXY_PROTOCOLS)
    _enum(request['client'], ('claude_code', 'browser', 'desktop', 'unknown'))


def _gate(gaps, extra_requirements=()):
    return {
        'status': 'blocked' if gaps else 'eligible_for_existing_gate',
        'gaps': list(dict.fromkeys(gaps)),
        'host_requirements': [
            'CURRENT_TARGET_USER_NAMESPACE_BINDING',
            'EXISTING_SCOPED_ACTION_AUTHORIZATION',
            'EXISTING_CONTACT_AND_WORKFLOW_GATES',
            'EXACT_ADAPTER_AND_OPERATION_CAPABILITY',
        ] + list(extra_requirements),
    }


def assess_entry(request):
    """Return entry eligibility, fixed gaps and suggested check depth only.

    The caller must supply the full sanitized versioned projection. Missing or
    invented fields/states raise InvalidProjection with a fixed error code.
    Valid incomplete/withdrawn declarations return blocked gates. No input is
    mutated, no targets are inspected, and no native checks or repairs occur.

    ``offline_precheck`` is target-scoped, offline, read-only prechecking under
    the original authorization. ``configuration`` describes entry to separate
    plan/change gates, never an executable plan. Direct selection needs no
    purchased proxy. VPS scope stays basic and non-intrusive.
    """
    _validate(request)
    route, network = request['route'], request['network']
    entry, egress = request['local_entry'], request['final_egress']
    selected = route['state'] == 'selected' and route['choice'] in _REQUIRED_ROLES
    base_gaps = []
    if not selected:
        base_gaps.append('EXPLICIT_CURRENT_ROUTE_SELECTION_REQUIRED')
    else:
        roles = {target['role'] for target in request['targets']}
        expected = set(_REQUIRED_ROLES[route['choice']])
        if expected - roles:
            base_gaps.append('ROUTE_TARGET_DECLARATIONS_REQUIRED')
        if roles - expected:
            base_gaps.append('TARGET_ROLE_ROUTE_MISMATCH')

    resource_gaps = []
    direct = network['selection'] == 'direct'
    if network['selection'] not in ('selected', 'direct'):
        resource_gaps.append('EXPLICIT_CURRENT_NETWORK_SELECTION_REQUIRED')
    if network['selection'] == 'selected':
        if network['possession'] != 'present':
            resource_gaps.append('SELECTED_RESOURCE_AVAILABILITY_REQUIRED')
        if 'resource_ref' not in network:
            resource_gaps.append('SELECTED_RESOURCE_ALIAS_REQUIRED')
        if network['path'] not in ('explicit', 'tun'):
            resource_gaps.append('SELECTED_PROXY_PATH_REQUIRED')
    if direct and (network['path'] != 'direct' or egress['kind'] != 'direct'
                   or egress['protocol'] != 'unknown' or entry['kind'] != 'none'
                   or 'entry_ref' in entry):
        resource_gaps.append('DIRECT_PATH_DECLARATION_CONFLICT')

    protocol_gaps = []
    if request['client'] == 'unknown':
        protocol_gaps.append('CLIENT_SCOPE_REQUIRED')
    if not direct:
        if network['path'] == 'explicit':
            if entry['kind'] in ('unknown', 'none') or 'entry_ref' not in entry:
                protocol_gaps.append('LOCAL_PROXY_ENTRY_REQUIRED')
            if request['client'] == 'claude_code' and entry['kind'] == 'socks':
                protocol_gaps.append('CLAUDE_CODE_HTTP_MIXED_ENTRY_REQUIRED')
        if egress['kind'] != 'proxy' or egress['protocol'] == 'unknown':
            protocol_gaps.append('FINAL_PROXY_PROTOCOL_REQUIRED')

    configuration_gaps = base_gaps + resource_gaps + protocol_gaps
    if network['configuration'] in ('unknown', 'conflict', 'stale'):
        configuration_gaps.append('CONFIGURATION_STATE_REVIEW_REQUIRED')
    if not direct and network['configuration'] == 'not_applicable':
        configuration_gaps.append('PROXY_CONFIGURATION_STATE_REQUIRED')
    if selected and route['choice'] == 'vps':
        configuration_gaps.append('VPS_CONFIGURATION_OUTSIDE_BASIC_CHECK_SCOPE')

    depth = ('none' if base_gaps else
             'basic_nonintrusive' if route['choice'] == 'vps' else 'detailed')
    scopes = []
    if not base_gaps:
        for role in _REQUIRED_ROLES[route['choice']]:
            target = next(item for item in request['targets'] if item['role'] == role)
            scopes.append({'role': role, 'target_ref': target['target_ref'],
                           'check_depth': depth, 'binding_status': 'declaration_only'})
    result = {
        'schema_version': RESULT_SCHEMA,
        'assessment_kind': 'entry_eligibility_only',
        'evidence_level': 'sanitized_declarations_not_observations',
        'authorization_status': 'not_evaluated_use_existing_action_gates',
        'binding_status': 'not_verified_by_this_module',
        'interview_and_explanation': 'available',
        'suggested_check_depth': depth,
        'target_scopes': scopes,
        'configuration_readiness': _CONFIGURATION_READINESS[network['configuration']],
        'gates': {
            'offline_precheck': _gate(base_gaps, ('OFFLINE_READ_ONLY_SCOPE',)),
            'configuration': _gate(configuration_gaps, (
                'EXACT_REVIEWED_PLAN_AND_SEMANTIC_DIFF',
                'TARGET_RECHECK_BACKUP_AND_RECOVERY')),
        },
        'host_revalidation': {
            'status': 'required_on_every_evaluation',
            'route_unusable': 'yes' if not selected else 'no',
            'network_selection_unusable': (
                'yes' if network['selection'] not in ('selected', 'direct') else 'no'),
            'on_route_or_target_change': [
                'INVALIDATE_DEPENDENT_CONFIRMATIONS',
                'INVALIDATE_OLD_TARGET_BINDINGS',
                'INVALIDATE_DEPENDENT_PLANS',
            ],
            'on_network_or_configuration_change': [
                'INVALIDATE_DEPENDENT_CONFIRMATIONS',
                'INVALIDATE_DEPENDENT_PLANS',
                'REVALIDATE_TARGET_NETWORK_BINDING',
            ],
            'performed_by_this_module': 'none',
        },
    }
    return result


def require_entry(request, purpose, target_ref):
    """Require current operation-specific entry for one declared target.

    ``purpose`` is offline_precheck or configuration.
    A missing or malformed projection raises InvalidProjection; an ineligible or mismatched
    target raises EntryBlocked with fixed gaps. The returned record is only an
    entry prerequisite, never authorization. The caller must still check its
    original exact target/user/namespace, action and contact gates.

    Explanations, purely offline plans that inspect no device, and recovery of an
    existing receipt do not use this new-action entry gate. Such recovery must
    retain the original receipt, target, authorization and restoration checks.
    """
    _enum(purpose, ('offline_precheck', 'configuration'))
    _alias(target_ref)
    assessment = assess_entry(request)
    gate = assessment['gates'][purpose]
    gaps = list(gate['gaps'])
    target = next((scope for scope in assessment['target_scopes']
                   if scope['target_ref'] == target_ref), None)
    if target is None:
        gaps.append('REQUESTED_TARGET_NOT_IN_CURRENT_ROUTE')
    if gaps:
        raise EntryBlocked(gaps)
    return {
        'schema_version': assessment['schema_version'],
        'status': 'eligible_for_existing_gate',
        'purpose': purpose,
        'target_ref': target_ref,
        'target_role': target['role'],
        'check_depth': target['check_depth'],
        'binding_status': assessment['binding_status'],
        'authorization_status': assessment['authorization_status'],
        'configuration_readiness': assessment['configuration_readiness'],
        'host_requirements': list(gate['host_requirements']),
    }
