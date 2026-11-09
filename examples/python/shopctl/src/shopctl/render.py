from __future__ import annotations

from jinja2 import Environment, StrictUndefined


def render(template: str, **ctx: object) -> str:
    """StrictUndefined: a missing variable is an error, never an empty string."""
    env = Environment(undefined=StrictUndefined, autoescape=False, keep_trailing_newline=True)  # noqa: S701
    return env.from_string(template).render(**ctx)
