from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .config import Service

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Result:
    name: str
    ok: bool
    status: int | None
    elapsed_ms: float
    detail: str = ""


@retry(
    retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.01, max=0.05),
    reraise=True,
)
def _get(client: httpx.Client, svc: Service) -> httpx.Response:
    return client.get(svc.url, timeout=svc.timeout_s)


def check(client: httpx.Client, svc: Service) -> Result:
    try:
        resp = _get(client, svc)
    except httpx.HTTPError as exc:
        log.warning("%s failed: %s", svc.name, exc)
        return Result(svc.name, False, None, 0.0, type(exc).__name__)
    try:
        ms = resp.elapsed.total_seconds() * 1000
    except (
        RuntimeError
    ):  # .elapsed is only set once a response was fully read through a real transport
        ms = 0.0
    ok = resp.status_code == svc.expect_status
    return Result(svc.name, ok, resp.status_code, ms, "" if ok else f"expected {svc.expect_status}")


def check_all(client: httpx.Client, services: list[Service]) -> list[Result]:
    return [check(client, s) for s in services]
