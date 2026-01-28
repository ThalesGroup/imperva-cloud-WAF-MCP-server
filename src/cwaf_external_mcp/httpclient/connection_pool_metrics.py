# Copyright Thales 2026
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
