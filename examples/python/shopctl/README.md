# shopctl: the CLI built in the Python Scripting video

Tested with Python 3.14, uv 0.13, pytest 9, ruff 0.17, mypy 2.4 (strict), Typer 0.28, httpx 0.28, moto 5.

```bash
uv venv && . .venv/bin/activate
uv pip install -e ".[dev]"
pytest                      # 22 tests, 98% coverage, no AWS account needed (moto)
ruff check . && ruff format --check .
mypy src                    # strict
shopctl --help
```
