from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EndpointConfig:
    name: str
    url: str
    method: str = "GET"
    expected_status: int = 200
    timeout_seconds: float = 5.0
    headers: Dict[str, str] = field(default_factory=dict)
    keyword_assertion: Optional[str] = None
    check_ssl: bool = True


@dataclass
class ProbeResult:
    endpoint_name: str
    url: str
    is_healthy: bool
    status_code: Optional[int]
    latency_ms: float
    ssl_days_remaining: Optional[int] = None
    error_message: Optional[str] = None


@dataclass
class HealthSummary:
    total_endpoints: int
    healthy_count: int
    unhealthy_count: int
    results: List[ProbeResult]
    p50_latency_ms: float
    p95_latency_ms: float

    @property
    def is_all_healthy(self) -> bool:
        return self.unhealthy_count == 0
