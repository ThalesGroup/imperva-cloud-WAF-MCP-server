"""Asynchronous HTTP client using aiohttp with connection pooling and metrics."""

import logging
import os
import ssl

import aiohttp
from aiohttp import ClientTimeout
from prometheus_client import Gauge

SESSION = None


def _build_session() -> aiohttp.ClientSession:
    """Build and configure the aiohttp ClientSession with connection pooling."""
    ssl_context = ssl.create_default_context()

    if os.environ.get("DISABLE_SSL_VERIFICATION", "false").lower() == "true":
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(
        limit=int(os.environ.get("CONNECTION_POOL_SIZE", "50")),  #
        limit_per_host=int(os.environ.get("CONNECTION_POOL_MAX_KEEP_ALIVE", "20")),
        keepalive_timeout=30,
        ttl_dns_cache=300,
        ssl=ssl_context,
    )

    timeout = ClientTimeout(
        total=float(os.environ.get("READ_TIME_OUT", 30.0)),
        connect=float(
            os.environ.get("CONNECTION_TIME_OUT", 15.0)
        ),  # queue-in-pool + TCP + TLS handshake
        sock_connect=float(
            os.environ.get("CONNECTION_TIME_OUT", 10.0)
        ),  # TCP+TLS handshake only (no queue time)
        sock_read=5.0,  # gap allowed between successive reads
    )

    if os.environ.get("AIOHTTP_DEBUG_MODE_ENABLED", "false").lower() == "true":
        aiohttp_log = logging.getLogger("aiohttp.client")
        aiohttp_log.setLevel(logging.DEBUG)
        aiohttp_log.addHandler(logging.StreamHandler())

    return aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        raise_for_status=False,  # optional: auto-raise on 4xx/5xx
    )


async def setup_session() -> None:
    """Initialise the global SESSION exactly once."""
    global SESSION
    if SESSION is None or SESSION.closed:
        SESSION = _build_session()


def get_async_client() -> aiohttp.ClientSession:
    """Get the configured HTTP client for making asynchronous requests."""
    global SESSION
    if SESSION is None or SESSION.closed:
        SESSION = _build_session()
    return SESSION


USED = Gauge("aiohttp_pool_used", "Active (leased) connections", ["host"])
IDLE = Gauge("aiohttp_pool_idle", "Idle keep-alive connections", ["host"])
TOTAL = Gauge("aiohttp_pool_total", "Total open sockets", ["host"])


def _host_label(key: aiohttp.client_reqrep.ConnectionKey) -> str:
    """Generate a host label for Prometheus metrics from a ConnectionKey."""
    # key.host already includes the port for Unix / proxy cases
    return f"{key.host}:{key.port or (443 if key.ssl else 80)}"


def collect_pool_metrics() -> None:
    """Collect metrics for the aiohttp connection pool."""
    if SESSION is None or SESSION.closed:
        return
    c = SESSION.connector  # type: aiohttp.BaseConnector
    busy_total = len(c._acquired)  # used across all hosts
    idle_total = sum(len(q) for q in c._conns.values())
    TOTAL.labels(host="*").set(busy_total + idle_total)
    USED.labels(host="*").set(busy_total)
    IDLE.labels(host="*").set(idle_total)

    # ─ per-host breakdown ─
    for key, idle_q in c._conns.items():
        host = _host_label(key)
        idle = len(idle_q)
        busy = len(c._acquired_per_host.get(key, ()))
        USED.labels(host=host).set(busy)
        IDLE.labels(host=host).set(idle)
        TOTAL.labels(host=host).set(busy + idle)
