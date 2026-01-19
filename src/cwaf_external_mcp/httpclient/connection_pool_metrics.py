"""collect pool metrics"""

import os
import time

from cwaf_external_mcp.httpclient.aiohttp_client import collect_pool_metrics
from cwaf_external_mcp.utilities.logging import get_logger

logger = get_logger(__name__)


def poll_connection_pool_metrics() -> None:
    """Poll connection pool metrics periodically."""
    while True:
        if (
            os.environ.get("HTTP_CONNECTION_POOL_METRICS_JOB_ENABLED", "true").lower()
            == "true"
        ):
            try:
                collect_pool_metrics()
            except Exception as e:
                logger.error(
                    "Error collecting connection pool metrics: %s", e, exc_info=True
                )
        time.sleep(5)
