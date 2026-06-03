"""MySQL CLI wrapper — credentials only from settings / .env."""

from __future__ import annotations

import os
import subprocess
from typing import Sequence

from lib import settings


def _base_cmd() -> list[str]:
    cfg = settings.mysql_config()
    return [
        "mysql",
        f"-h{cfg['host']}",
        f"-P{cfg['port']}",
        f"-u{cfg['user']}",
        cfg["database"],
        "--batch",
        "--skip-column-names",
    ]


def _env_with_password() -> dict[str, str]:
    """Pass password via MYSQL_PWD env (not argv) to avoid ps exposure of -p."""
    env = os.environ.copy()
    cfg = settings.mysql_config()
    env["MYSQL_PWD"] = str(cfg["password"])
    return env


def query(sql: str) -> list[list[str]]:
    cmd = _base_cmd() + ["-e", sql]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=_env_with_password(),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"MySQL query failed (code {result.returncode}): {result.stderr[:500]}"
        )
    if not result.stdout.strip():
        return []
    return [line.split("\t") for line in result.stdout.strip().split("\n") if line]


def execute(sql: str) -> None:
    cfg = settings.mysql_config()
    cmd = [
        "mysql",
        f"-h{cfg['host']}",
        f"-P{cfg['port']}",
        f"-u{cfg['user']}",
        cfg["database"],
    ]
    result = subprocess.run(
        cmd,
        input=sql,
        capture_output=True,
        text=True,
        env=_env_with_password(),
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"MySQL execute failed (code {result.returncode}): {result.stderr[:500]}"
        )


def query_rows(sql: str, min_cols: int) -> list[Sequence[str]]:
    return [r for r in query(sql) if len(r) >= min_cols]
