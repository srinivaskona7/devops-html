import httpx

from shopctl.config import Service
from shopctl.health import check


def client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_ok():
    c = client(lambda req: httpx.Response(200))
    r = check(c, Service(name="api", url="http://x/h"))
    assert r.ok and r.status == 200


def test_wrong_status():
    c = client(lambda req: httpx.Response(503))
    r = check(c, Service(name="api", url="http://x/h"))
    assert not r.ok and r.status == 503 and "expected 200" in r.detail


def test_retries_then_succeeds():
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        if calls["n"] < 3:
            raise httpx.ConnectError("boom")
        return httpx.Response(200)

    r = check(client(handler), Service(name="api", url="http://x/h"))
    assert r.ok and calls["n"] == 3


def test_gives_up_after_three_attempts():
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        raise httpx.ConnectError("down")

    r = check(client(handler), Service(name="api", url="http://x/h"))
    assert not r.ok and r.status is None and calls["n"] == 3 and r.detail == "ConnectError"


def test_does_not_retry_on_http_error_status():
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        return httpx.Response(500)

    check(client(handler), Service(name="api", url="http://x/h"))
    assert calls["n"] == 1
