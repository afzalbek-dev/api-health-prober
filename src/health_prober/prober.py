import asyncio
import time
import urllib.error
import urllib.request
from typing import List, Optional

from .models import EndpointConfig, HealthSummary, ProbeResult
from .ssl_check import check_ssl_expiry


class HealthProber:
    """Concurrent async synthetic API uptime monitor and latency prober."""

    def __init__(self, concurrency: int = 10):
        self.semaphore = asyncio.Semaphore(concurrency)

    async def probe_endpoint(self, config: EndpointConfig) -> ProbeResult:
        async with self.semaphore:
            loop = asyncio.get_running_loop()
            start = time.time()
            status_code = None
            error_msg = None
            is_healthy = False

            def _sync_request():
                req = urllib.request.Request(
                    config.url,
                    headers={"User-Agent": "HealthProber/0.1.0", **config.headers},
                    method=config.method,
                )
                with urllib.request.urlopen(req, timeout=config.timeout_seconds) as resp:
                    body = resp.read().decode("utf-8", errors="ignore")
                    return resp.getcode(), body

            try:
                code, body = await loop.run_in_executor(None, _sync_request)
                status_code = code

                if code == config.expected_status:
                    if config.keyword_assertion:
                        if config.keyword_assertion in body:
                            is_healthy = True
                        else:
                            error_msg = f"Keyword '{config.keyword_assertion}' not found in body"
                    else:
                        is_healthy = True
                else:
                    error_msg = f"Expected status {config.expected_status}, got {code}"
            except urllib.error.HTTPError as e:
                status_code = e.code
                body = e.read().decode("utf-8", errors="ignore")
                if e.code == config.expected_status:
                    if config.keyword_assertion:
                        if config.keyword_assertion in body:
                            is_healthy = True
                        else:
                            error_msg = f"Keyword '{config.keyword_assertion}' not found in body"
                    else:
                        is_healthy = True
                else:
                    error_msg = f"Expected status {config.expected_status}, got {e.code}"
            except Exception as e:
                error_msg = str(e)

            latency = round((time.time() - start) * 1000, 2)

            ssl_days = None
            if config.check_ssl and config.url.startswith("https://"):
                ssl_days = await loop.run_in_executor(None, check_ssl_expiry, config.url)

            return ProbeResult(
                endpoint_name=config.name,
                url=config.url,
                is_healthy=is_healthy,
                status_code=status_code,
                latency_ms=latency,
                ssl_days_remaining=ssl_days,
                error_message=error_msg,
            )

    async def probe_all(self, endpoints: List[EndpointConfig]) -> HealthSummary:
        tasks = [self.probe_endpoint(ep) for ep in endpoints]
        results = await asyncio.gather(*tasks)

        healthy = [r for r in results if r.is_healthy]
        unhealthy = [r for r in results if not r.is_healthy]

        latencies = sorted([r.latency_ms for r in results])
        p50 = latencies[int(len(latencies) * 0.50)] if latencies else 0.0
        p95 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.95))] if latencies else 0.0

        return HealthSummary(
            total_endpoints=len(results),
            healthy_count=len(healthy),
            unhealthy_count=len(unhealthy),
            results=list(results),
            p50_latency_ms=p50,
            p95_latency_ms=p95,
        )
