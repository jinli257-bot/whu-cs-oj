"""2014 年参考解与测试数据生成。"""
from __future__ import annotations

import math

from .common import norm_text


def t1(data: str) -> str:
    x = float(data.strip())
    if x > 0:
        y = (math.sqrt(x) + math.exp(x)) / (5 * x + 5)
    else:
        y = (2 / 3 + math.sin(math.radians(60))) * abs(x)
    return f"{y:.4f}\n"


def t2(data: str) -> str:
    s = data.strip()
    return "".join(sorted(s)) + "\n"


def t3(data: str = "") -> str:
    res = []
    for n in range(2, 1001):
        s = 0
        for d in range(1, n // 2 + 1):
            if n % d == 0:
                s += d
        if s == n:
            res.append(n)
    return " ".join(map(str, res)) + "\n"


def t4(data: str) -> str:
    n = int(data.strip())
    a = [[0] * n for _ in range(n)]
    r, c = 0, n // 2
    for k in range(1, n * n + 1):
        a[r][c] = k
        if k % n == 0:
            r = (r + 1) % n
        else:
            r = (r - 1) % n
            c = (c + 1) % n
    return "\n".join(" ".join(map(str, row)) for row in a) + "\n"


def t5(data: str = "") -> str:
    # 完全背包计数：1/2/5 分凑 100 分
    dp = [0] * 101
    dp[0] = 1
    for coin in (1, 2, 5):
        for s in range(coin, 101):
            dp[s] += dp[s - coin]
    return f"{dp[100]}\n"


def gen_t1(rng):
    vals = ["-100", "-12.5", "-2", "-0.5", "0", "0.5", "1", "3.75", "20", "100"]
    return [v + "\n" for v in vals] + [f"{rng.uniform(-50, 80):.2f}\n" for _ in range(4)]


def gen_t2(rng):
    out = []
    for _ in range(8):
        n = rng.randint(1, 60)
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-="
        out.append("".join(rng.choice(alphabet) for _ in range(n)) + "\n")
    return out


def gen_t4(rng):
    return [f"{n}\n" for n in (3, 5, 7, 9, 11, 21)]


CASES = {
    "2014-t1": {
        "solve": t1,
        "samples": [("1\n", "0.3718"), ("-2\n", None)],
        "tests": gen_t1,
        "checker": "float",
        "tol": 5e-5,
    },
    "2014-t2": {
        "solve": t2,
        "samples": [("gfedcba\n", "abcdefg"), ("HelloWorld\n", None)],
        "tests": gen_t2,
    },
    "2014-t3": {
        "solve": t3,
        "samples": [("", "6 28 496")],
        "tests": lambda rng: [""],
    },
    "2014-t4": {
        "solve": t4,
        "samples": [("3\n", None), ("5\n", None)],
        "tests": gen_t4,
    },
    "2014-t5": {
        "solve": t5,
        "samples": [("", "541")],
        "tests": lambda rng: [""],
    },
}
