"""2023 年参考解与测试数据生成。"""
from __future__ import annotations


def t1(data: str) -> str:
    xs = list(map(int, data.split()))
    n, a, x = xs[0], xs[1:1 + xs[0]], xs[1 + xs[0]]
    seen = {}
    for i, v in enumerate(a):
        if x - v in seen and seen[x - v] != i:
            return f"{x - v} {v}\n"
        seen[v] = i
    return "error\n"


def t2(data: str) -> str:
    xs = list(map(int, data.split()))
    a = xs[1:1 + xs[0]]
    best = cur = a[0]
    bl = br = start = 0
    for i in range(1, len(a)):
        if cur < 0:
            cur, start = 0, i
        cur += a[i]
        if cur > best:
            best, bl, br = cur, start, i
    return f"{bl + 1} {br + 1} {best}\n"


def t3(data: str) -> str:
    s = data.strip()
    # 方向：0 东, 1 北, 2 西, 3 南
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    d = 0
    x = y = 0
    for ch in s:
        if ch == ".":
            x += dx[d]
            y += dy[d]
        elif ch == "<":
            d = (d + 1) % 4
        elif ch == ">":
            d = (d - 1) % 4
    return f"({x},{y})\n"


def gen_t1(rng):
    return ["5\n2 7 11 15 3\n9\n",
            "3\n1 2 3\n7\n",
            "2\n3 3\n6\n",
            "1\n5\n5\n",
            "6\n-1 0 1 2 -1 -4\n0\n",
            "4\n1 1 1 1\n2\n"]


def gen_t2(rng):
    return ["5\n5 2 3 -1 -5\n", "1\n-7\n", "6\n-2 1 -3 4 -1 2 1\n",
            "4\n-1 -2 -3 -4\n", "5\n0 0 0 0 0\n", "8\n1 -2 3 4 -1 2 -5 6\n"]


def gen_t3(rng):
    return [".<.<.\n", "\n", "....\n", ">>>>\n", "<<<<\n",
            ".>.<.>.<\n", "..>>..<<\n"]


CASES = {
    "2023-t1": {
        "solve": t1,
        "samples": [("5\n2 7 11 15 3\n9\n", "2 7"), ("3\n1 2 3\n7\n", "error")],
        "tests": gen_t1,
        "checker": "twosum",
    },
    "2023-t2": {
        "solve": t2,
        "samples": [("5\n5 2 3 -1 -5\n", "1 3 10")],
        "tests": gen_t2,
    },
    "2023-t3": {
        "solve": t3,
        "samples": [(".<.<.\n", "(0,1)")],
        "tests": gen_t3,
    },
}
