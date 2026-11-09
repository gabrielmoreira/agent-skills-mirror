"""Dashboard projection of a network_check.py report (guardian-network-check/0.1).

The report holds no IP addresses; only its fixed fields are read. A result older than
24 hours, or from the future, shows as unknown. A measured pass shows as verified for
that card only; settings the check cannot see keep their own cards.
"""
from datetime import datetime, timedelta, timezone

import network_check

SCHEMA = network_check.SCHEMA
MAX_AGE = timedelta(hours=24)
STATUSES = frozenset({'pass', 'fail', 'warn', 'not_run', 'error'})
CARDS = {'route': ('tun',), 'exit_ipv4': ('ipv4',), 'exit_via_proxy': ('proxy',), 'ipv6': ('ipv6',),
         'dns_leak': ('dns_leak', 'dns'), 'udp': ('udp', 'stun'), 'failure_drill': ('failure',),
         'webrtc': ('browser',)}
STATE = {'pass': 'verified', 'fail': 'error', 'warn': 'unknown', 'not_run': 'not_run', 'error': 'unknown'}


class NetworkReportError(ValueError):
    pass


def _validate(report):
    if not isinstance(report, dict) or report.get('schema_version') != SCHEMA:
        raise NetworkReportError('INVALID_NETWORK_REPORT')
    results = report.get('results')
    if not isinstance(results, dict) or not {'route', 'exit_ipv4', 'ipv6', 'dns_leak', 'udp',
                                             'failure_drill', 'webrtc'} <= set(results):
        raise NetworkReportError('INVALID_NETWORK_REPORT')
    for key, item in results.items():
        if key not in CARDS or not isinstance(item, dict) or item.get('status') not in STATUSES:
            raise NetworkReportError('INVALID_NETWORK_REPORT')
    if report.get('overall') not in ('pass', 'fail', 'incomplete') or not isinstance(report.get('target_ref'), str) \
            or report.get('platform') not in ('macos', 'windows', 'linux'):
        raise NetworkReportError('INVALID_NETWORK_REPORT')
    try:
        checked = datetime.strptime(report.get('checked_at', ''), '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        rows = network_check.describe(report)
    except (TypeError, ValueError, KeyError, AttributeError):
        raise NetworkReportError('INVALID_NETWORK_REPORT') from None
    return checked, rows


def project_network(report, now):
    """{card_key: {'state', 'text', 'checked_at'}} for the cards this report covers."""
    checked, rows = _validate(report)
    fresh = timedelta(0) <= now - checked <= MAX_AGE
    cards = {}
    for key, label, status, detail in rows:
        for card in CARDS[key]:
            state = STATE[status] if fresh else 'unknown'
            text = '%s：%s' % (label, detail) + ('' if fresh else '（结果超过 24 小时，重新检测）')
            if card in cards:  # two results share a card: the worse one wins
                order = ('error', 'unknown', 'not_run', 'verified')
                cards[card]['text'] += '；' + text
                if order.index(state) < order.index(cards[card]['state']):
                    cards[card]['state'] = state
            else:
                cards[card] = {'state': state, 'text': text, 'checked_at': checked}
    return cards
