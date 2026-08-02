import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit

from backend.core.conf import settings


async def validate_outbound_http_url(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {'http', 'https'} or not parsed.hostname:
        raise ValueError('Model endpoint must be an absolute HTTP or HTTPS URL')
    if parsed.username or parsed.password:
        raise ValueError('Model endpoint must not contain credentials')
    if settings.ALLOW_PRIVATE_LLM_ENDPOINTS:
        return url

    try:
        addresses = await asyncio.to_thread(socket.getaddrinfo, parsed.hostname, parsed.port or 443)
    except socket.gaierror as exc:
        raise ValueError('Model endpoint hostname cannot be resolved') from exc
    for address in addresses:
        ip = ipaddress.ip_address(address[4][0].split('%', 1)[0])
        if not ip.is_global:
            raise ValueError('Private or local model endpoints are disabled')
    return url
