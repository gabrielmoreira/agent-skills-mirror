"""Fixed macOS admission for Clash Verge Rev 2.5.8 rules-extension writes.

This is the only reviewed native adapter behind ``repair_execution._native_session``.
It admits exactly one scope: candidate kind ``rules-prepend`` on Darwin, with the
application metadata, profile index, base profile and target all at the fixed
Clash Verge Rev locations of the effective user. Anything else is reported as
``NATIVE_REPAIR_ADAPTER_UNAVAILABLE`` without touching a file.

Writer exclusion on macOS is detect-and-fail, not prevention: there is no
mandatory file lock, so the adapter requires that the application (the only writer of the
profile files) is not running and rechecks that, plus the identity of the metadata files, at
every call of the recheck callable (before commit and after readback). A running
writer or a changed file fails the session; the transaction engine then keeps
its own backup and recovery batch. This cannot stop a process that starts and
writes between two rechecks.
"""
from contextlib import contextmanager
import os
import stat
import subprocess
import sys

import transactions as tx

APP_BUNDLE = '/Applications/Clash Verge.app/'
APP_INFO = APP_BUNDLE + 'Contents/Info.plist'
SUPPORT_DIRECTORY = 'Library/Application Support/io.github.clash-verge-rev.clash-verge-rev'
# Only the GUI application writes profiles.yaml and the profile/extension files. The sidecar
# core (verge-mihomo) and the root service helper (clash-verge-service, a KeepAlive
# LaunchDaemon that survives quitting the app) do not, so they do not block a write; the
# real-device run showed that blocking on them forces `sudo launchctl bootout` and drops
# the TUN for no benefit. Quit the app (Cmd-Q); the new rules load when it is reopened.
PROCESS_NAMES = frozenset({'clash-verge'})
PS = '/bin/ps'
PS_TIMEOUT = 5
_UNAVAILABLE = 'NATIVE_REPAIR_ADAPTER_UNAVAILABLE'


def _platform():
    return sys.platform


def _support_directory():
    import pwd  # POSIX only; this adapter is admitted on Darwin alone.
    return os.path.join(pwd.getpwuid(os.geteuid()).pw_dir, SUPPORT_DIRECTORY)


def _list_processes():
    """Executable paths of all processes; fixed command, no shell, minimal environment."""
    try:
        done = subprocess.run([PS, '-axo', 'comm='], capture_output=True, text=True,
                              timeout=PS_TIMEOUT, check=False, shell=False,
                              env={'PATH': '/usr/bin:/bin', 'LC_ALL': 'C'})
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise tx.TransactionError('PROCESS_LIST_UNAVAILABLE') from None
    if done.returncode != 0 or not done.stdout.strip():
        raise tx.TransactionError('PROCESS_LIST_UNAVAILABLE')
    return [line.strip() for line in done.stdout.splitlines() if line.strip()]


def _writer_running():
    for command in _list_processes():
        if command.startswith(APP_BUNDLE) or os.path.basename(command) in PROCESS_NAMES:
            return True
    return False


def _snapshot(path):
    with tx._parent(path) as (fd, name):
        raw, snapshot = tx._read(fd, name)
        return {'path': path, 'snapshot': snapshot, 'parent_identity': tx._identity(fd)}


def _admitted(document):
    """True only for the fixed rules-prepend scope; never raises on malformed input."""
    try:
        if document['candidate_kind'] != 'rules-prepend':
            return False
        support = _support_directory()
        profiles = support + '/profiles'
        sources = document['metadata_sources']
        return (sources['app_info']['path'] == APP_INFO
                and sources['profile_index']['path'] == support + '/profiles.yaml'
                and os.path.dirname(document['base_source']['path']) == profiles
                and os.path.dirname(document['plan']['path']) == profiles)
    except (KeyError, TypeError, OSError):
        return False


def _trusted_metadata():
    """The application metadata must belong to root or the effective user and not be shared-writable."""
    try:
        info = os.lstat(APP_INFO)
    except OSError:
        raise tx.TransactionError('APP_METADATA_NOT_TRUSTED') from None
    if (not stat.S_ISREG(info.st_mode) or info.st_uid not in (0, os.geteuid())
            or info.st_mode & 0o022):
        raise tx.TransactionError('APP_METADATA_NOT_TRUSTED')


@contextmanager
def session(document):
    if _platform() != 'darwin' or not _admitted(document):
        raise tx.TransactionError(_UNAVAILABLE)
    expected = [document['base_source'], document['metadata_sources']['app_info'],
                document['metadata_sources']['profile_index']]

    def recheck():
        if _writer_running():
            raise tx.TransactionError('CLASH_VERGE_RUNNING')
        _trusted_metadata()
        for source in expected:
            if _snapshot(source['path']) != source:
                raise tx.TransactionError('SOURCE_SNAPSHOT_CHANGED')

    recheck()
    yield recheck
