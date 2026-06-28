# -*- coding: utf-8 -*-

import re

_LOCAL_IPS = frozenset({"127.0.0.1", "::1", "0:0:0:0:0:0:0:1", "localhost"})
_MOBILE_UA_KEYWORDS = (
    "android",
    "iphone",
    "ipod",
    "ipad",
    "mobile",
    "webos",
    "blackberry",
    "windows phone",
    "opera mini",
    "iemobile",
)


def resolve_client_ip(environ):
    """Return WAN/LAN client IP; skip loopback. Empty string if unknown."""
    if not environ:
        return ""
    candidates = []
    for header in (
        "HTTP_CF_CONNECTING_IP",
        "HTTP_TRUE_CLIENT_IP",
        "HTTP_X_REAL_IP",
        "HTTP_X_CLIENT_IP",
        "HTTP_X_FORWARDED_FOR",
        "REMOTE_ADDR",
    ):
        raw = environ.get(header)
        if not raw:
            continue
        if header == "HTTP_X_FORWARDED_FOR":
            parts = [part.strip() for part in raw.split(",") if part.strip()]
            candidates.extend(parts)
        else:
            candidates.append(raw.strip())
    for ip in candidates:
        if _is_usable_ip(ip):
            return ip
    return ""


def _is_usable_ip(ip):
    if not ip:
        return False
    normalized = ip.lower().strip()
    if normalized in _LOCAL_IPS:
        return False
    if normalized.startswith("127."):
        return False
    if normalized.startswith("::ffff:127."):
        return False
    return bool(re.match(r"^[\da-fA-F:.]+$", normalized))


def is_usable_client_ip(ip):
    return _is_usable_ip((ip or "").strip())


def device_category_from_meta(meta):
    """Classify client as PC, Laptop, or Di động."""
    ua = (meta.get("user_agent") or "").lower()
    platform = (meta.get("platform") or "").lower().strip('"').strip("'")
    mobile_hint = (meta.get("sec_ch_ua_mobile") or "").strip()

    if mobile_hint == "?1":
        return "Di động"
    if any(keyword in ua for keyword in _MOBILE_UA_KEYWORDS):
        return "Di động"
    if "ipad" in ua or "tablet" in ua:
        return "Di động"
    if "macintosh" in ua or "mac os" in platform or platform == "macos":
        return "Laptop"
    if "windows" in ua or "linux" in ua or "cros" in ua or platform in {"windows", "linux", "chrome os"}:
        return "PC"
    return "PC"


def collect_request_meta(environ):
    """Build metadata dict from a WSGI environ."""
    if not environ:
        return {}
    user_agent = environ.get("HTTP_USER_AGENT") or ""
    platform = (environ.get("HTTP_SEC_CH_UA_PLATFORM") or "").strip('"').strip("'")
    browser = environ.get("HTTP_SEC_CH_UA") or user_agent[:120]
    meta = {
        "user_agent": user_agent,
        "platform": platform,
        "browser": browser,
        "os": platform or user_agent[:80],
        "sec_ch_ua_mobile": environ.get("HTTP_SEC_CH_UA_MOBILE") or "",
    }
    meta["ip_address"] = resolve_client_ip(environ)
    meta["device_name"] = device_category_from_meta(meta)
    return meta
