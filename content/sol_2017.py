"""2017 年参考解与测试数据生成。"""
from __future__ import annotations

from functools import lru_cache

from . import sol_2016


def t1(data: str = "") -> str:
    peaches = 1
    for _ in range(9):
        peaches = (peaches + 1) * 2
    return f"{peaches}\n"


def t2(data: str) -> str:
    n = int(data.strip())
    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
    return f"{b if n >= 2 else 1}\n"


def t3(data: str) -> str:
    return sol_2016.t1(data)


def t4(data: str) -> str:
    xs = list(map(int, data.split()))
    x, n, arr = xs[0], xs[1], xs[2:2 + xs[1]]
    pos = [str(i) for i, v in enumerate(arr) if v == x]
    return f"count = {len(pos)}\npositions = {' '.join(pos) if pos else '-1'}\n"


def t5(data: str) -> str:
    n = int(data.strip())
    s = str(n + 1)
    L = len(s)

    @lru_cache(None)
    def go(pos, prev, tight):
        if pos == L:
            return ""
        if tight:
            lo, hi = int(s[pos]), 9
        else:
            lo, hi = (1 if pos == 0 else 0), 9
        for d in range(lo, hi + 1):
            if d == prev:
                continue
            sub = go(pos + 1, d, tight and d == int(s[pos]))
            if sub is not None:
                return str(d) + sub
        return None

    r = go(0, -1, True)
    if r is None:
        # 位数 +1 时的最小不重复数：1010...
        r = ("10" * ((L + 2) // 2))[:L + 1]
    return r + "\n"


def gen_t2(rng):
    return [f"{n}\n" for n in (1, 2, 3, 5, 10, 20, 30, 45)]


def gen_t4(rng):
    return ["5\n10\n1 2 5 3 4 5 6 5 8 9\n",
            "7\n5\n7 7 7 7 7\n",
            "0\n3\n0 0 0\n",
            "-1\n1\n0\n",
            "42\n8\n1 2 3 4 5 6 7 8\n"]


def gen_t5(rng):
    return [f"{n}\n" for n in (0, 1, 9, 10, 11, 98, 99, 110, 989, 999, 1234,
                               999999999, 1000000000)]


CASES = {
    "2017-t1": {
        "solve": t1,
        "samples": [("", "1534")],
        "tests": lambda rng: [""],
    },
    "2017-t2": {
        "solve": t2,
        "samples": [("5\n", "5"), ("1\n", "1")],
        "tests": gen_t2,
    },
    "2017-t3": {
        "solve": t3,
        "samples": [("90\n", "90=2*3*3*5")],
        "tests": lambda rng: ["12\n", "97\n", "1000000007\n", "360\n", "1024\n"],
    },
    "2017-t4": {
        "solve": t4,
        "samples": [("5\n10\n1 2 5 3 4 5 6 5 8 9\n", "count = 3\npositions = 2 5 7")],
        "tests": gen_t4,
    },
    "2017-t5": {
        "solve": t5,
        "samples": [("110\n", "120"), ("99\n", "101")],
        "tests": gen_t5,
    },
}
