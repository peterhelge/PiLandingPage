"""Guards for secrets, the Home Assistant token, and kiosk power actions.

This module must not import app_logging at module level. app_logging imports
redact() while it is still initializing.
"""

import ipaddress
import os
import re
import subprocess
from urllib.parse import quote, urlparse

_SECRET_ENV_VARS = (
    "OPENWEATHER_API_KEY",
    "SPOTIPY_CLIENT_SECRET",
    "HA_ACCESS_TOKEN",
    "TODOIST_API_TOKEN",
)
_MIN_SECRET_LEN = 8

_QUERY_SECRET_RE = re.compile(
    r"(?i)([?&](?:appid|api_key|access_token|refresh_token|client_secret|token)=)([^&\s]+)"
)
_BEARER_RE = re.compile(r"(?i)(Bearer\s+)([A-Za-z0-9\-._~+/]+=*)")
_JSON_SECRET_RE = re.compile(
    r'(?i)("(?:access_token|refresh_token|client_secret|api_token|appid|token)"\s*:\s*")[^"]*(")'
)
_USERINFO_RE = re.compile(r"(https?://)([^/\s:@]+):([^/\s@]+)@")

_LOCAL_SUFFIXES = (".local", ".localhost", ".home.arpa", ".internal", ".lan", ".home")
_ENTITY_ID_RE = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
_BLOCKED_IPS = {
    ipaddress.ip_address("169.254.169.254"),  # cloud instance metadata
    ipaddress.ip_address("fd00:ec2::254"),
}

INSECURE_HTTP_NOTICE = (
    "HTTP connection: access token is visible on this network"
)


def redact(text):
    """Remove known credentials and common token patterns from log text."""
    if not isinstance(text, str) or not text:
        return text
    try:
        secrets = []
        for name in _SECRET_ENV_VARS:
            value = os.getenv(name) or ""
            if len(value) >= _MIN_SECRET_LEN:
                secrets.append(value)
                encoded = quote(value, safe="")
                if encoded != value:
                    secrets.append(encoded)
        for secret in sorted(set(secrets), key=len, reverse=True):
            text = text.replace(secret, "***")
        text = _QUERY_SECRET_RE.sub(r"\1***", text)
        text = _BEARER_RE.sub(r"\1***", text)
        text = _JSON_SECRET_RE.sub(r"\1***\2", text)
        text = _USERINFO_RE.sub(r"\1\2:***@", text)
        return text
    except Exception:
        return text


def ha_url_problem(url, allow_insecure_http=False):
    """Return an error if this base URL must not receive the HA token.

    HTTPS is always accepted. Plain HTTP is accepted only for local names and
    private addresses, because a public HTTP URL would send the long-lived
    token across the internet. Set allow_insecure_http to skip that check.
    """
    if not url or not str(url).strip():
        return "HA_BASE_URL is empty"
    parts = urlparse(str(url).strip())
    scheme = (parts.scheme or "").lower()
    if scheme not in ("http", "https"):
        return "HA_BASE_URL must start with http:// or https://"
    if parts.username or parts.password:
        return "HA_BASE_URL must not contain a username or password"
    host = (parts.hostname or "").lower().rstrip(".")
    if not host:
        return "HA_BASE_URL is missing a host"
    if scheme == "https" or allow_insecure_http:
        return None
    if _host_is_local(host):
        return None
    return f"Refusing HTTP to {host}. Use HTTPS, or set HA_ALLOW_INSECURE_HTTP=1."


def url_is_http(url):
    parts = urlparse(str(url or "").strip())
    return (parts.scheme or "").lower() == "http"


def entity_id_ok(entity_id):
    """Home Assistant entity ids are domain.object, with no path characters."""
    return bool(entity_id) and _ENTITY_ID_RE.fullmatch(entity_id) is not None


def _host_is_local(host):
    if host == "localhost" or host.endswith(_LOCAL_SUFFIXES):
        return True
    ip = _parse_ip(host)
    if ip is not None:
        return _ip_is_local(ip)
    # Single-label names such as "homeassistant" are LAN/mDNS.
    # Numeric literals (2130706433, 0x7f000001) are not names.
    if "." not in host and not _is_numeric_host_literal(host):
        return True
    return False


def _parse_ip(host):
    literal = host.split("%", 1)[0]
    try:
        return ipaddress.ip_address(literal)
    except ValueError:
        return None


def _ip_is_local(ip):
    if ip in _BLOCKED_IPS:
        return False
    if ip.is_multicast or ip.is_unspecified or ip.is_reserved:
        return False
    return bool(ip.is_loopback or ip.is_private or ip.is_link_local)


def _is_numeric_host_literal(host):
    if host.isdigit():
        return True
    if host.startswith("0x"):
        try:
            int(host, 16)
        except ValueError:
            return False
        return True
    return False


def restrict_owner_only(path):
    """chmod a file to 0600 or a directory to 0700. Symlinks are left alone."""
    if not path or os.path.islink(path) or not os.path.exists(path):
        return
    mode = 0o700 if os.path.isdir(path) else 0o600
    try:
        os.chmod(path, mode)
    except OSError:
        pass


def restrict_owner_tree(path):
    """Lock down a directory tree the app owns. Does not follow symlinks."""
    if not path or os.path.islink(path) or not os.path.isdir(path):
        return
    try:
        os.chmod(path, 0o700)
        for root, dirs, files in os.walk(path, followlinks=False):
            dirs[:] = [name for name in dirs if not os.path.islink(os.path.join(root, name))]
            for name in dirs:
                try:
                    os.chmod(os.path.join(root, name), 0o700)
                except OSError:
                    pass
            for name in files:
                file_path = os.path.join(root, name)
                if os.path.islink(file_path):
                    continue
                try:
                    os.chmod(file_path, 0o600)
                except OSError:
                    pass
    except OSError:
        pass


def spotify_cache_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")


def restrict_known_secret_files():
    """Tighten permissions on credential files this app creates or reads."""
    root = os.path.dirname(os.path.abspath(__file__))
    restrict_owner_tree(os.path.join(root, "logs"))
    restrict_owner_tree(os.path.join(root, "todo_data"))
    directories = {root}
    try:
        directories.add(os.getcwd())
    except OSError:
        pass
    for directory in directories:
        try:
            names = os.listdir(directory)
        except OSError:
            continue
        for name in names:
            if name == ".env" or name == ".cache" or name.startswith(".cache-"):
                restrict_owner_only(os.path.join(directory, name))


def system_power_argv(action):
    """Non-interactive power commands. `sudo -n` fails instead of prompting."""
    if action == "shutdown":
        return ["sudo", "-n", "shutdown", "-h", "now"]
    if action == "reboot":
        return ["sudo", "-n", "reboot"]
    raise ValueError(f"unknown power action: {action}")


def run_power_action(action, runner=None):
    """Run a power command. Returns (ok, user_message).

    On non-Linux this logs a mock and succeeds, matching the old dev behavior.
    Pass runner(argv) -> (returncode, stderr) to avoid invoking sudo in tests.
    """
    import platform

    argv = system_power_argv(action)
    if platform.system() != "Linux":
        _logger().info("[Mock] %s", " ".join(argv))
        return True, ""
    if runner is None:
        runner = _subprocess_runner
    try:
        returncode, err = runner(argv)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _logger().error("Power action failed: %s", exc)
        return False, "Failed"
    if returncode != 0:
        _logger().error("Power action failed (%s): %s", returncode, err)
        return False, "Needs passwordless sudo"
    return True, ""


def _subprocess_runner(argv):
    result = subprocess.run(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        timeout=15,
        check=False,
    )
    err = (result.stderr or b"").decode("utf-8", "replace").strip()
    return result.returncode, err


def _logger():
    from app_logging import logger
    return logger


class ConfirmGate:
    """Two-step arming for destructive kiosk buttons.

    The first press arms a key. A second press of the same key confirms.
    Pressing a different key moves the arm instead of confirming.
    """

    def __init__(self):
        self.pending = None

    def arm(self, key):
        if self.pending == key:
            self.pending = None
            return True
        self.pending = key
        return False

    def clear(self):
        self.pending = None
