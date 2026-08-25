#!/usr/bin/env python3
"""Verify the normal 5180 entry, its SPA routes, and its API proxy.

This script intentionally uses only the Python standard library so a local runtime
can be checked without adding a browser-test dependency. It verifies delivery
reachability and the Vite API proxy, not the visual fidelity of the Three.js room;
visual checks remain a separate acceptance step.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


CORE_ROUTES = (
    "/",
    "/study",
    "/study/plan",
    "/study/knowledge",
    "/study/wordbook",
    "/study/cards",
    "/work",
    "/work/tech-stack",
    "/novel",
)


@dataclass(frozen=True)
class CheckFailure:
    target: str
    detail: str


def request(base_url: str, path: str, timeout: float) -> tuple[int, bytes]:
    with urlopen(f"{base_url.rstrip('/')}{path}", timeout=timeout) as response:
        return response.status, response.read()


def check_spa_routes(base_url: str, timeout: float) -> list[CheckFailure]:
    failures: list[CheckFailure] = []
    for route in CORE_ROUTES:
        try:
            status, body = request(base_url, route, timeout)
        except HTTPError as error:
            failures.append(CheckFailure(route, f"HTTP {error.code}"))
            continue
        except URLError as error:
            failures.append(CheckFailure(route, f"unreachable: {error.reason}"))
            continue

        text = body.decode("utf-8", errors="replace")
        if status != 200:
            failures.append(CheckFailure(route, f"HTTP {status}"))
        elif 'id="root"' not in text:
            failures.append(CheckFailure(route, "does not return the spatial SPA root"))
    return failures


def check_api_proxy(base_url: str, timeout: float) -> CheckFailure | None:
    target = "/api/health"
    try:
        status, body = request(base_url, target, timeout)
    except HTTPError as error:
        return CheckFailure(target, f"HTTP {error.code}")
    except URLError as error:
        return CheckFailure(target, f"unreachable: {error.reason}")

    if status != 200:
        return CheckFailure(target, f"HTTP {status}")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return CheckFailure(target, "did not return JSON through the Vite proxy")
    if payload.get("status") != "ok":
        return CheckFailure(target, f"unexpected health payload: {payload!r}")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:5180")
    parser.add_argument("--timeout", default=5.0, type=float)
    args = parser.parse_args()

    failures = check_spa_routes(args.base_url, args.timeout)
    proxy_failure = check_api_proxy(args.base_url, args.timeout)
    if proxy_failure:
        failures.append(proxy_failure)

    if failures:
        for failure in failures:
            print(f"FAIL {failure.target}: {failure.detail}", file=sys.stderr)
        return 1

    print(f"PASS 5180 spatial routes: {', '.join(CORE_ROUTES)}")
    print("PASS 5180 API proxy: /api/health")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
