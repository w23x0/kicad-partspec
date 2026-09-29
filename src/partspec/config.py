"""Environment-backed limits.

Every limit is read from the environment at call time; invalid values raise
``ValueError`` instead of being clamped silently.
"""

from __future__ import annotations

import os

_DEFAULT_MAX_SEXPR_TOKENS = 1_000_000
_DEFAULT_MAX_SEXPR_DEPTH = 512
_DEFAULT_MAX_CLI_OUTPUT_BYTES = 1 * 1024 * 1024


def env_int(
    name: str,
    default: int,
    *,
    minimum: int = 1,
    maximum: int | None = None,
) -> int:
    """Read a bounded positive integer from the environment."""
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw, 10)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value < minimum or (maximum is not None and value > maximum):
        bound = f" between {minimum} and {maximum}" if maximum is not None else f" >= {minimum}"
        raise ValueError(f"{name} must be{bound}")
    return value


def cli_timeout(name: str, default: int, *, maximum: int) -> int:
    return env_int(name, default, maximum=maximum)


def max_sexpr_tokens() -> int:
    return env_int("PARTSPEC_MAX_SEXPR_TOKENS", _DEFAULT_MAX_SEXPR_TOKENS, maximum=10_000_000)


def max_sexpr_depth() -> int:
    return env_int("PARTSPEC_MAX_SEXPR_DEPTH", _DEFAULT_MAX_SEXPR_DEPTH, maximum=10_000)


def max_cli_output_bytes() -> int:
    return env_int("PARTSPEC_MAX_CLI_OUTPUT_BYTES", _DEFAULT_MAX_CLI_OUTPUT_BYTES, maximum=64 * 1024 * 1024)
