# Import libraries
import logging
import os
import re
import time

import config
from alerting.telegram import send_alert

log = logging.getLogger(__name__)

IP_RE = re.compile(r'from (\S+)')


def _ip(line):
    match = IP_RE.search(line)
    return match.group(1) if match else '?'


def classify(line, trusted_ip=None):
    '''
    Returns the Telegram message for an auth.log line, or None if not relevant.
    '''
    if "Accepted password" in line or "Accepted publickey" in line:
        ip = _ip(line)
        if trusted_ip and ip == trusted_ip:
            return f"✅ SSH connection from trusted IP: {ip}"
        return f"🚨 INTRUSION !!! From IP: {ip}"
    if "Failed password" in line:
        return f"⚠️ Someone tried to connect to the server but entered a wrong password !!!\n IP: {_ip(line)}"
    if "Invalid user" in line:
        return f"🚨 Unauthorized SSH attempt from: {_ip(line)}"
    return None


def _rotated(path, inode, position):
    '''
    True if the log was rotated (new inode) or truncated since it was opened.
    '''
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return False  # logrotate between move and create: wait for the new file
    return st.st_ino != inode or st.st_size < position


def monitor(path=None, trusted_ip=None):
    '''
    Follows auth.log like `tail -F`: reopens the file after a rotation.
    Reading auth.log requires the `adm` group: sudo usermod -aG adm <user>
    '''
    path = path or config.auth_log_path
    trusted_ip = trusted_ip if trusted_ip is not None else config.trusted_ip
    if not trusted_ip:
        log.warning("TRUSTED_IP is empty: every SSH login will be reported as unknown")
    from_start = False  # first open: skip history; after a rotation: read the new file entirely
    while True:
        try:
            f = open(path, 'r', errors='replace')
        except PermissionError:
            log.error("Cannot read %s (add the user to the 'adm' group). SSH monitoring disabled.", path)
            return
        except FileNotFoundError:
            time.sleep(5)
            from_start = True
            continue
        with f:
            inode = os.fstat(f.fileno()).st_ino
            if not from_start:
                f.seek(0, 2)  # 0 = offset, 2 = since the end of the file
            while True:
                line = f.readline()
                if line:
                    message = classify(line, trusted_ip)
                    if message:
                        send_alert(message)
                    continue
                time.sleep(1)
                if _rotated(path, inode, f.tell()):
                    from_start = True
                    break


if __name__ == "__main__":
    monitor()
