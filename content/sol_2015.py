"""2015 年参考解与测试数据生成。"""
from __future__ import annotations

from .common import is_prime


def t1(data: str = "") -> str:
    lines = []
    for i in range(9):
        lines.append("*" * i + "".join(str(d) for d in range(9 - i, 0, -1)))
    return "\n".join(lines) + "\n"


def t2(data: str = "") -> str:
    fib = [1, 1]
    while len(fib) < 30:
        fib.append(fib[-1] + fib[-2])
    ps = [x for x in fib if is_prime(x)]
    return " ".join(map(str, ps)) + f"\n{len(ps)}\n"


def t3(data: str = "") -> str:
    out = []
    for r in range(3):
        for g in range(4):
            y = 8 - r - g
            if 0 <= y <= 5:
                out.append(f"Red: {r}, Green: {g}, Yellow: {y}")
    return "\n".join(out) + "\n"


def t4(data: str) -> str:
    n = int(data.strip())
    out = []

    def dfs(rem, mx, path):
        if rem == 0:
            out.append("+".join(map(str, path)))
            return
        for x in range(min(rem, mx), 0, -1):
            path.append(x)
            dfs(rem - x, x, path)
            path.pop()

    dfs(n, n, [])
    return "\n".join(out) + "\n"


def t5(data: str) -> str:
    parts = data.strip().split(".")
    return ".".join(format(int(p), "08b") for p in parts) + "\n"


def gen_t4(rng):
    return [f"{n}\n" for n in (1, 2, 3, 5, 6, 7, 8, 10)]


def gen_t5(rng):
    out = []
    fixed = ["0.0.0.0", "255.255.255.255", "192.168.1.1", "10.0.0.254", "127.0.0.1"]
    for s in fixed:
        out.append(s + "\n")
    for _ in range(5):
        out.append(".".join(str(rng.randint(0, 255)) for _ in range(4)) + "\n")
    return out


CASES = {
    "2015-t1": {
        "solve": t1,
        "samples": [("", "987654321\n*87654321\n**7654321\n***654321\n****54321\n*****4321\n******321\n*******21\n********1")],
        "tests": lambda rng: [""],
    },
    "2015-t2": {
        "solve": t2,
        "samples": [("", "2 3 5 13 89 233 1597 28657 514229\n9")],
        "tests": lambda rng: [""],
    },
    "2015-t3": {
        "solve": t3,
        "samples": [("", "Red: 0, Green: 3, Yellow: 5\nRed: 1, Green: 2, Yellow: 5\nRed: 1, Green: 3, Yellow: 4\nRed: 2, Green: 1, Yellow: 5\nRed: 2, Green: 2, Yellow: 4\nRed: 2, Green: 3, Yellow: 3")],
        "tests": lambda rng: [""],
    },
    "2015-t4": {
        "solve": t4,
        "samples": [("4\n", "4\n3+1\n2+2\n2+1+1\n1+1+1+1")],
        "tests": gen_t4,
    },
    "2015-t5": {
        "solve": t5,
        "samples": [("128.1.2.128\n", "10000000.00000001.00000010.10000000")],
        "tests": gen_t5,
    },
}
