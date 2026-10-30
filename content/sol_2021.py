"""2021 年参考解与测试数据生成。"""
from __future__ import annotations

from .common import sieve


def t1(data: str) -> str:
    xs = list(map(int, data.split()))
    i, t = 0, xs[0]
    out = []
    for _ in range(t):
        n = xs[i + 1]
        arr = xs[i + 2:i + 2 + n]
        i += 1 + n
        seen, keep = set(), []
        for v in arr:
            if v not in seen:
                seen.add(v)
                keep.append(v)
        out.append(" ".join(map(str, keep)))
    return "\n".join(out) + "\n"


def t2(data: str) -> str:
    xs = list(map(int, data.split()))
    n, m = xs[0], xs[1]
    a = [xs[2 + r * m:2 + (r + 1) * m] for r in range(n)]
    out = []
    for r in range(n):
        row = []
        for c in range(m):
            s, cnt = a[r][c], 1
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < m:
                    s += a[nr][nc]
                    cnt += 1
            row.append(f"{s / cnt:.2f}")
        out.append(" ".join(row))
    return "\n".join(out) + "\n"


def t3(data: str = "") -> str:
    return "a=z\nb=x\nc=y\n"


def t4(data: str) -> str:
    n = int(data.strip())
    out = []
    for x in range(10 ** (n - 1) if n > 1 else 1, 10 ** n):
        s = str(x)
        desc = int("".join(sorted(s, reverse=True)))
        asc = int("".join(sorted(s)))
        if desc - asc == x:
            out.append(str(x))
    return "\n".join(out) + ("\n" if out else "")


def t5(data: str) -> str:
    n = int(data.strip())
    return " ".join(map(str, sieve(n))) + "\n"


def gen_t1(rng):
    return ["2\n15\n123 456 78 90 1 23 456 7 8 90 12 34 56 7 890\n5\n10 10 10 20 10\n",
            "3\n1\n5\n1\n-1\n4\n1 2 1 2\n",
            "3\n5\n1 1 2 3 3\n4\n9 8 9 8\n2\n-1 -1\n",
            "2\n6\n0 0 1 0 2 0\n3\n5 4 5\n"]


def gen_t2(rng):
    return ["3 3\n1 2 3\n2 3 4\n3 4 5\n",
            "1 1\n5\n",
            "1 4\n1 2 3 4\n",
            "4 1\n1\n2\n3\n4\n",
            "2 2\n10 20\n30 40\n"]


def gen_t4(rng):
    return [f"{n}\n" for n in (2, 3, 4, 5, 6)]


def gen_t5(rng):
    return [f"{n}\n" for n in (2, 10, 100, 999, 10000)]


CASES = {
    "2021-t1": {
        "solve": t1,
        "samples": [("2\n15\n123 456 78 90 1 23 456 7 8 90 12 34 56 7 890\n5\n10 10 10 20 10\n",
                     "123 456 78 90 1 23 7 8 12 34 56 890\n10 20")],
        "tests": gen_t1,
    },
    "2021-t2": {
        "solve": t2,
        "samples": [("3 3\n1 2 3\n2 3 4\n3 4 5\n", None)],
        "tests": gen_t2,
    },
    "2021-t3": {
        "solve": t3,
        "samples": [("", "a=z\nb=x\nc=y")],
        "tests": lambda rng: [""],
    },
    "2021-t4": {
        "solve": t4,
        "samples": [("3\n", "495"), ("4\n", "6174")],
        "tests": gen_t4,
    },
    "2021-t5": {
        "solve": t5,
        "samples": [("10\n", "2 3 5 7")],
        "tests": gen_t5,
    },
}
