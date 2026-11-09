"""STUN (RFC 8489) binding request and strict response parser; no I/O.

``network_check.py`` sends the request over UDP and compares the mapped address
with the TCP exit.
"""
import ipaddress
import secrets
import struct
import zlib

COOKIE = 0x2112A442
MAX_PACKET = 4096
ERRORS = frozenset({
    'invalid_scope', 'approval_required', 'target_changed', 'cancelled',
    'invalid_budget', 'timeout', 'receive_budget_exhausted',
    'transport_error', 'permission_denied', 'callback_error', 'cleanup_failed',
    'poll_budget_exhausted', 'invalid_clock', 'server_error',
    'malformed_packet', 'wrong_transaction', 'wrong_type', 'missing_mapping',
    'unsupported_attribute', 'invalid_fingerprint', 'unexpected_address_family',
})


class StunError(ValueError):
    """Only fixed codes cross the public API; never exception/packet text."""
    def __init__(self, code):
        super().__init__(code if code in ERRORS else 'transport_error')


def binding_request(transaction_id=None):
    """Return a bare request; production IDs use the OS cryptographic RNG."""
    txid = secrets.token_bytes(12) if transaction_id is None else transaction_id
    if type(txid) is not bytes or len(txid) != 12:
        raise StunError('malformed_packet')
    return struct.pack('!HHI', 0x0001, 0, COOKIE) + txid


def parse_binding_response(packet, transaction_id):
    """Pure strict parser returning (IP, port, IP version), no source claims.

    Unknown mandatory attributes are rejected. Optional attributes are skipped;
    FINGERPRINT, if supplied, is checked but is not authentication. Authentication
    attributes are unsupported, rather than silently treating them as verified.
    """
    if (type(packet) is not bytes or not 20 <= len(packet) <= MAX_PACKET
            or type(transaction_id) is not bytes or len(transaction_id) != 12):
        raise StunError('malformed_packet')
    kind, length, cookie = struct.unpack('!HHI', packet[:8])
    if length % 4 or length != len(packet) - 20 or cookie != COOKIE:
        raise StunError('malformed_packet')
    if packet[8:20] != transaction_id:
        raise StunError('wrong_transaction')
    if kind not in (0x0101, 0x0111):
        raise StunError('wrong_type')
    offset, mapped = 20, None
    unsupported, error_code = False, False
    while offset < len(packet):
        if offset + 4 > len(packet):
            raise StunError('malformed_packet')
        attr, size = struct.unpack('!HH', packet[offset:offset + 4])
        end = offset + 4 + size
        padded_end = end + (-size % 4)
        if padded_end > len(packet):
            raise StunError('malformed_packet')
        value = packet[offset + 4:end]
        if attr == 0x0020:
            if size not in (8, 20) or value[1] not in (1, 2):
                raise StunError('malformed_packet')
            version = 4 if value[1] == 1 else 6
            if size != (8 if version == 4 else 20):
                raise StunError('malformed_packet')
            mask = struct.pack('!I', COOKIE) + transaction_id
            address = bytes(a ^ b for a, b in zip(value[4:], mask))
            mapping = (str(ipaddress.ip_address(address)),
                       struct.unpack('!H', value[2:4])[0] ^ (COOKIE >> 16), version)
            if mapped is None:  # RFC 8489: first occurrence governs
                mapped = mapping
        elif attr == 0x0009 and kind == 0x0111:
            if size < 4 or not 3 <= (value[2] & 7) <= 6 or value[3] > 99:
                raise StunError('malformed_packet')
            try:
                reason = value[4:].decode('utf-8')
            except UnicodeDecodeError:
                raise StunError('malformed_packet') from None
            if len(reason) >= 128:
                raise StunError('malformed_packet')
            error_code = True
        elif attr == 0x8028:
            if size != 4 or padded_end != len(packet):
                raise StunError('invalid_fingerprint')
            if struct.unpack('!I', value)[0] != (zlib.crc32(packet[:offset]) ^ 0x5354554e):
                raise StunError('invalid_fingerprint')
        elif attr < 0x8000:
            unsupported = True
        offset = padded_end
    # Only after the complete envelope/TLVs/fingerprint are validated may a
    # correlated response end the transaction. Never let an early mandatory
    # attribute hide a corrupt tail that should instead be discarded.
    if kind == 0x0111:
        if not error_code:
            raise StunError('malformed_packet')
        raise StunError('server_error')
    if unsupported:
        raise StunError('unsupported_attribute')
    if mapped is None:
        raise StunError('missing_mapping')
    return mapped


