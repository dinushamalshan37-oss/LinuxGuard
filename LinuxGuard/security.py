"""Read-only local security checks. No exploitation or automated remediation."""
import platform
import re
import subprocess
import psutil

FAILURE_PATTERN = re.compile(r'Failed password|Invalid user|authentication failure', re.IGNORECASE)


def recent_ssh_failures():
    """Return (count, notes). journalctl --since bounds the time window."""
    if platform.system() != 'Linux':
        return None, 'SSH audit is supported on Linux only.'
    try:
        result = subprocess.run(
            ['journalctl', '--since', '1 hour ago', '-n', '1000', '--no-pager', '-o', 'cat',
             '_SYSTEMD_UNIT=ssh.service', '+', '_SYSTEMD_UNIT=sshd.service'],
            capture_output=True, text=True, timeout=5, check=False
        )
        if result.returncode != 0:
            return None, 'SSH journal unavailable. Check journalctl permissions or service names.'
        if not result.stdout.strip():
            return 0, 'No readable SSH journal entries in the last hour; this does not prove no failed logins.'
        count = sum(bool(FAILURE_PATTERN.search(line)) for line in result.stdout.splitlines())
        return count, 'Counted matching SSH journal messages from the past hour (up to 1,000 entries).'
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None, 'Cannot read systemd journal; check access or whether systemd is installed.'


def listening_ports():
    entries = []
    access_limited = False
    try:
        connections = psutil.net_connections(kind='inet')
    except (psutil.AccessDenied, OSError):
        connections = []
        access_limited = True
    for conn in connections:
        if conn.status != psutil.CONN_LISTEN or not conn.laddr:
            continue
        host, port = conn.laddr.ip, conn.laddr.port
        entries.append({'host': host, 'port': int(port),
                        'public_bind': host in ('0.0.0.0', '::'), 'pid': conn.pid})
    entries = sorted(entries, key=lambda row: (not row['public_bind'], row['port']))
    return entries[:40], access_limited


def run_security_scan(store):
    ports, limited = listening_ports()
    failures, details = recent_ssh_failures()
    public = [p for p in ports if p['public_bind']]
    findings = []
    if public:
        findings.append(f'{len(public)} visible service(s) listen on all network interfaces; review firewall rules.')
    if failures is not None and failures >= 5:
        store.add_alert('warning', 'Repeated SSH authentication failures',
                        f'{failures} matching SSH failure messages in the last hour. Review SSH access logs.',
                        'security', 'ssh-failures', cooldown=600)
        findings.append('Repeated failed SSH authentication attempts detected. Verify the source and credentials.')
    if limited:
        findings.append('Port visibility may be limited by account permissions.')
    if failures is None:
        findings.append('SSH event visibility unavailable; results are incomplete.')
    if not findings:
        findings.append('No findings using these limited local checks; not a full vulnerability scan.')
    return {'ssh_failures_last_hour': failures, 'ssh_note': details,
            'listeners': ports, 'all_interface_count': len(public),
            'port_access_limited': limited, 'findings': findings}
