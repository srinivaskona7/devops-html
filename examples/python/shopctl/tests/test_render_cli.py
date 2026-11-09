import pytest
from jinja2 import UndefinedError
from typer.testing import CliRunner

from shopctl.cli import app
from shopctl.render import render

runner = CliRunner()


def test_render_fills_values():
    assert render("port={{ port }}\n", port=8080) == "port=8080\n"


def test_render_missing_variable_is_an_error():
    with pytest.raises(UndefinedError):
        render("port={{ port }}")


def test_cli_version():
    r = runner.invoke(app, ["version"])
    assert r.exit_code == 0 and "0.1.0" in r.stdout


def test_cli_render(tmp_path):
    t = tmp_path / "t.j2"
    t.write_text("host={{ host }}\n")
    r = runner.invoke(app, ["render", str(t), "--var", "host=db1"])
    assert r.exit_code == 0 and r.stdout == "host=db1\n"


def test_cli_render_missing_var_fails(tmp_path):
    t = tmp_path / "t.j2"
    t.write_text("host={{ host }}\n")
    r = runner.invoke(app, ["render", str(t)])
    assert r.exit_code != 0


def test_cli_health_exit_codes(tmp_path, monkeypatch):
    import httpx

    cfg = tmp_path / "c.yml"
    cfg.write_text("services:\n  - {name: api, url: http://x/h}\n")
    real = httpx.Client

    def make(ok):
        def factory(**kw):
            return real(
                transport=httpx.MockTransport(lambda req: httpx.Response(200 if ok else 500)), **kw
            )

        return factory

    monkeypatch.setattr("shopctl.cli.httpx.Client", make(True))
    assert runner.invoke(app, ["health", str(cfg)]).exit_code == 0
    monkeypatch.setattr("shopctl.cli.httpx.Client", make(False))
    r = runner.invoke(app, ["health", str(cfg)])
    assert r.exit_code == 1 and "FAIL" in r.stdout
