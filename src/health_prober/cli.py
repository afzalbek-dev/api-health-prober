import argparse
import asyncio
import json
import sys
from .models import EndpointConfig
from .prober import HealthProber


def main():
    parser = argparse.ArgumentParser(
        prog="api-health-prober",
        description="Concurrent synthetic API uptime and health prober CLI"
    )
    parser.add_argument("--url", help="Single URL to probe")
    parser.add_argument("--config", help="Path to JSON file containing list of endpoint configs")
    parser.add_argument("--concurrency", type=int, default=10, help="Max concurrent requests (default: 10)")

    args = parser.parse_args()

    endpoints = []
    if args.url:
        endpoints.append(EndpointConfig(name=args.url, url=args.url))
    elif args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                endpoints.append(EndpointConfig(**item))
    else:
        parser.print_help()
        sys.exit(1)

    prober = HealthProber(concurrency=args.concurrency)
    summary = asyncio.run(prober.probe_all(endpoints))

    print("\n" + "=" * 55)
    print("📊 API HEALTH PROBE REPORT")
    print("=" * 55)
    for r in summary.results:
        status_icon = "✅" if r.is_healthy else "❌"
        ssl_info = f", SSL: {r.ssl_days_remaining}d" if r.ssl_days_remaining is not None else ""
        print(f"{status_icon} [{r.endpoint_name}] {r.url} -> {r.latency_ms}ms (HTTP {r.status_code or 'ERR'}{ssl_info})")
        if r.error_message:
            print(f"   ↳ Error: {r.error_message}")

    print("-" * 55)
    print(f"Total: {summary.total_endpoints} | Healthy: {summary.healthy_count} | Unhealthy: {summary.unhealthy_count}")
    print(f"Latency Percentiles: p50={summary.p50_latency_ms}ms, p95={summary.p95_latency_ms}ms")
    print("=" * 55 + "\n")

    if not summary.is_all_healthy:
        sys.exit(1)


if __name__ == "__main__":
    main()
