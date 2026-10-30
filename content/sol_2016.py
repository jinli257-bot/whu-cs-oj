"""2016 年参考解与测试数据生成。"""
from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP


def t1(data: str) -> str:
    n = int(data.strip())
    x = n
    fs = []
    d = 2
    while d * d <= x:
        while x % d == 0:
            fs.append(d)
            x //= d
        d += 1
    if x > 1:
        fs.append(x)
    return f"{n}=" + "*".join(map(str, fs)) + "\n"


def t2(data: str) -> str:
    n = int(data.strip())
    rows = []
    for r in range(n, 0, -1):
        row = [math.comb(r - 1, k) for k in range(r)]
        rows.append(" ".join(map(str, row)))
    return "please input a number:\n" + "\n".join(rows) + "\n"


def t3(data: str) -> str:
    m, n = map(int, data.split())

    from functools import lru_cache

    @lru_cache(None)
    def f(a, b):
        if a == 0 or b == 1:
            return 1
        if b > a:
            return f(a, a)
        return f(a, b - 1) + f(a - b, b)

    return f"{f(m, n)}\n"


def t4(data: str) -> str:
    s = data.strip()
    d = Decimal(s).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    text = f"{d:.2f}"
    ip, fp = text.split(".")
    out = []
    while len(ip) > 3:
        out.append(ip[-3:])
        ip = ip[:-3]
    out.append(ip)
    return "$" + ",".join(reversed(out)) + "." + fp + "\n"


def t5(data: str) -> str:
    x, y = map(int, data.split())
    if y > 0:
        z = math.sqrt(abs(x)) / (5 + 2 * y)
    elif x < 0:
        z = math.sin(math.radians(35)) - 6 * x + y * y
    else:
        z = y ** x - 2
    return f"{z:.2f}\n"


def gen_t1(rng):
    return [f"{n}\n" for n in (90, 7, 2, 97, 100, 123456789, 1000000007, 2147483647,
                               9699690, 999999937, 536870912)]


def gen_t2(rng):
    return [f"{n}\n" for n in (1, 2, 3, 5, 8, 12, 20)]


def gen_t3(rng):
    return ["7 3\n", "1 1\n", "5 5\n", "10 4\n", "20 10\n", "30 7\n", "100 100\n"]


def gen_t4(rng):
    return ["1234.5678\n", "0\n", "1000000000\n", "999.999\n", "0.005\n",
            "1234567.891\n", "12\n", "999999999.995\n"]


def gen_t5(rng):
    return ["4 2\n", "-3 4\n", "-2 -3\n", "2 -3\n", "1 -2\n", "9 1\n",
            "-5 -1\n", "3 -1\n"]


CASES = {
    "2016-t1": {
        "solve": t1,
        "samples": [("90\n", "90=2*3*3*5"), ("7\n", "7=7")],
        "tests": gen_t1,
    },
    "2016-t2": {
        "solve": t2,
        "samples": [("5\n", "please input a number:\n1 4 6 4 1\n1 3 3 1\n1 2 1\n1 1\n1")],
        "tests": gen_t2,
    },
    "2016-t3": {
        "solve": t3,
        "samples": [("7 3\n", "8")],
        "tests": gen_t3,
    },
    "2016-t4": {
        "solve": t4,
        "samples": [("1234.5678\n", "$1,234.57"), ("1000\n", "$1,000.00")],
        "tests": gen_t4,
    },
    "2016-t5": {
        "solve": t5,
        "samples": [("4 2\n", "0.22"), ("-2 -3\n", None)],
        "tests": gen_t5,
        "checker": "float",
        "tol": 5e-3,
    },
}
