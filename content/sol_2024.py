"""2024 年参考解与测试数据生成。"""
from __future__ import annotations


def t1(data: str) -> str:
    xs = list(map(int, data.split()))
    p = xs[1:1 + xs[0]]
    low = 10 ** 18
    best = 0
    for v in p:
        low = min(low, v)
        best = max(best, v - low)
    return f"{best}\n"


def t2(data: str) -> str:
    xs = list(map(int, data.split()))
    a = sorted(xs[1:1 + xs[0]])
    n = len(a)
    res = []
    for i in range(n - 2):
        if i > 0 and a[i] == a[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = a[i] + a[l] + a[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                res.append([a[i], a[l], a[r]])
                l += 1
                r -= 1
                while l < r and a[l] == a[l - 1]:
                    l += 1
                while l < r and a[r] == a[r + 1]:
                    r -= 1
    return "[" + ",".join("[" + ",".join(map(str, t)) + "]" for t in res) + "]\n"


def t3(data: str) -> str:
    s = data.strip()
    n = len(s)
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        if s[i - 1] != "0":
            dp[i] += dp[i - 1]
        if i >= 2 and 10 <= int(s[i - 2:i]) <= 26:
            dp[i] += dp[i - 2]
    return f"{dp[n]}\n"


def gen_t1(rng):
    return ["6\n7 1 5 3 6 4\n", "1\n5\n", "5\n7 6 4 3 1\n",
            "2\n2 4\n", "8\n3 3 5 0 0 3 1 4\n"]


def gen_t2(rng):
    return ["6\n-1 0 1 2 -1 -4\n", "3\n0 0 0\n", "4\n1 2 3 4\n",
            "5\n-2 0 1 1 2\n", "6\n-4 -2 -2 0 1 3\n", "1\n0\n"]


def gen_t3(rng):
    return ["12258\n", "0\n", "10\n", "101\n", "26\n", "27\n",
            "1201234\n", "1111111111\n"]


CASES = {
    "2024-t1": {
        "solve": t1,
        "samples": [("6\n7 1 5 3 6 4\n", "5")],
        "tests": gen_t1,
    },
    "2024-t2": {
        "solve": t2,
        "samples": [("6\n-1 0 1 2 -1 -4\n", "[[-1,-1,2],[-1,0,1]]")],
        "tests": gen_t2,
        "checker": "nowhitespace",
    },
    "2024-t3": {
        "solve": t3,
        "samples": [("12258\n", "5"), ("0\n", "0")],
        "tests": gen_t3,
    },
}
