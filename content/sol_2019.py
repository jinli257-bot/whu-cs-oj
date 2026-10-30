"""2019 年参考解与测试数据生成。"""
from __future__ import annotations


def t1(data: str) -> str:
    n = int(data.strip())
    out = []
    for c in (25, 10, 5, 1):
        while n >= c:
            out.append(c)
            n -= c
    return " ".join(map(str, out)) + "\n"


def t2(data: str) -> str:
    s = data.strip()
    open_ch = "([{"
    pair = {")": "(", "]": "[", "}": "{"}
    stack = []
    deleted = [False] * len(s)
    for i, ch in enumerate(s):
        if ch in open_ch:
            stack.append(i)
        else:
            if stack and s[stack[-1]] == pair[ch]:
                stack.pop()
            else:
                j = len(stack) - 1
                while j >= 0 and s[stack[j]] != pair[ch]:
                    j -= 1
                if j >= 0:
                    for k in range(j + 1, len(stack)):
                        deleted[stack[k]] = True
                    del stack[j + 1:]
                    stack.pop()
                else:
                    deleted[i] = True
    for idx in stack:
        deleted[idx] = True
    res = "".join(ch for i, ch in enumerate(s) if not deleted[i])
    return ("合法" if res == s else res) + "\n"


def t3(data: str) -> str:
    xs = list(map(int, data.split()))
    n, a = xs[0], xs[1:1 + xs[0]]
    best = cur = a[0]
    for v in a[1:]:
        cur = max(v, cur + v)
        best = max(best, cur)
    return f"{best}\n"


def t4(data: str) -> str:
    xs = list(map(int, data.split()))
    n = xs[0]
    best = {}
    for i in range(n):
        d, s = xs[1 + 2 * i], xs[2 + 2 * i]
        if d not in best or s > best[d][1]:
            best[d] = (i + 1, s)
    chosen = sorted(v[0] for v in best.values())
    total = sum(v[1] for v in best.values())
    return " ".join(map(str, chosen)) + f"\n{total}\n"


def gen_t1(rng):
    return [f"{n}\n" for n in (63, 1, 2, 5, 10, 25, 99, 10000, 9999)]


def gen_t2(rng):
    return ["{[()]}\n", "{[(])}\n", "([)]\n", "(((\n", ")))\n", "()[]{}\n",
            "{[()]}\n", "(]\n", "{[(])}\n"]


def gen_t3(rng):
    return ["6\n-10 4 5 7 -11 23\n", "1\n-5\n", "5\n5 2 3 -1 -5\n",
            "4\n-1 -2 -3 -4\n", "5\n0 0 0 0 0\n", "7\n-2 1 -3 4 -1 2 1\n"]


def gen_t4(rng):
    return ["4\n1 2\n1 1\n2 1\n2 2\n",
            "1\n5 100\n",
            "5\n3 5\n1 9\n3 7\n2 4\n1 8\n",
            "6\n1 1\n1 2\n1 3\n2 1\n2 2\n2 3\n"]


CASES = {
    "2019-t1": {
        "solve": t1,
        "samples": [("63\n", "25 25 10 1 1 1")],
        "tests": gen_t1,
    },
    "2019-t2": {
        "solve": t2,
        "samples": [("{[()]}\n", "合法"), ("{[(])}\n", "{[]}")],
        "tests": gen_t2,
    },
    "2019-t3": {
        "solve": t3,
        "samples": [("6\n-10 4 5 7 -11 23\n", "28")],
        "tests": gen_t3,
    },
    "2019-t4": {
        "solve": t4,
        "samples": [("4\n1 2\n1 1\n2 1\n2 2\n", "1 4\n4")],
        "tests": gen_t4,
    },
}
