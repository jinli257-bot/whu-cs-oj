"""Shared helpers for reference solutions and test-data generation."""
from __future__ import annotations

import math
import re


def norm_text(s: str) -> str:
    """Normalise line endings and trailing whitespace (used by the build check)."""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.rstrip() for ln in s.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def ints(data: str):
    return [int(x) for x in re.findall(r"-?\d+", data)]


def fmt_matrix(rows, sep=" "):
    return "\n".join(sep.join(str(x) for x in row) for row in rows)


def f2(x: float) -> str:
    # round half away from zero, matching typical C printf("%.2f") for positives
    return f"{x + 0.0:.2f}"


def f4(x: float) -> str:
    return f"{x + 0.0:.4f}"


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    if n % 3 == 0:
        return n == 3
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def sieve(n: int):
    if n < 2:
        return []
    bs = bytearray(b"\x01") * (n + 1)
    bs[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if bs[i]:
            bs[i * i:n + 1:i] = b"\x00" * (((n - i * i) // i) + 1)
    return [i for i in range(2, n + 1) if bs[i]]
