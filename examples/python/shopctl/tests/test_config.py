import pytest
from pydantic import ValidationError

from shopctl.config import load_config, token_from_env


def test_loads_valid_yaml(tmp_path):
    f = tmp_path / "c.yml"
    f.write_text("services:\n  - {name: api, url: https://api.example.com/health}\n")
    cfg = load_config(f)
    assert cfg.services[0].name == "api"
    assert cfg.services[0].timeout_s == 5.0


@pytest.mark.parametrize(
    "bad",
    [
        "services:\n  - {name: a, url: ftp://x}\n",
        "services:\n  - {name: a, url: http://x, timeout_s: 0}\n",
        "services: nope\n",
    ],
)
def test_rejects_invalid(tmp_path, bad):
    f = tmp_path / "c.yml"
    f.write_text(bad)
    with pytest.raises(ValidationError):
        load_config(f)


def test_yaml_cannot_run_code(tmp_path):
    f = tmp_path / "c.yml"
    f.write_text("services: !!python/object/apply:os.system ['echo pwned']\n")
    with pytest.raises(Exception):  # noqa: B017  safe_load refuses the python tag
        load_config(f)


def test_token_missing(monkeypatch):
    monkeypatch.delenv("SHOP_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="SHOP_TOKEN"):
        token_from_env()


def test_token_present(monkeypatch):
    monkeypatch.setenv("SHOP_TOKEN", "abc")
    assert token_from_env() == "abc"
