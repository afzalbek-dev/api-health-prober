from datetime import datetime, timezone
import socket
import ssl
from typing import Optional
from urllib.parse import urlparse


def check_ssl_expiry(url: str, timeout: float = 3.0) -> Optional[int]:
    """Check remaining days before SSL certificate expires using standard library."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return None

    hostname = parsed.hostname
    port = parsed.port or 443

    if not hostname:
        return None

    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if not cert or "notAfter" not in cert:
                    return None

                # Format example: 'Jun 15 12:00:00 2026 GMT'
                expire_str = cert["notAfter"]
                expire_date = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                remaining = (expire_date - now).days
                return max(0, remaining)
    except Exception:
        return None
