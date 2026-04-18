from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.services.clients.alpha_vantage import AlphaVantageClient


def build_client() -> AlphaVantageClient:
    return AlphaVantageClient(
        api_key="demo",
        base_url="https://example.com",
        timeout_seconds=5.0,
        cache_ttl_seconds=60,
    )


def main() -> int:
    client = build_client()

    first = client._cache_key(
        {
            "apikey": "secret-one",
            "function": "TIME_SERIES_DAILY",
            "symbol": "NVDA",
        }
    )
    second = client._cache_key(
        {
            "symbol": "NVDA",
            "function": "TIME_SERIES_DAILY",
            "apikey": "secret-two",
        }
    )

    assert first == second, "cache key should ignore apikey and input ordering"
    assert "secret-one" not in first
    assert "secret-two" not in second
    assert first == '{"function":"TIME_SERIES_DAILY","symbol":"NVDA"}'

    print("alpha vantage cache key tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
