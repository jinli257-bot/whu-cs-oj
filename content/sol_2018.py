"""2018 年参考解与测试数据生成。"""
from __future__ import annotations

from .common import is_prime


def _count_digit(n: int, d: int) -> int:
    if n <= 0:
        return 0
    cnt = 0
    factor = 1
    while factor <= n:
        high = n // (factor * 10)
        cur = (n // factor) % 10
        low = n % factor
        if d == 0:
            if high == 0:
                break
            cnt += (high - 1) * factor
            if cur == 0:
                cnt += low + 1
            elif cur > 0:
                cnt += factor
        else:
            cnt += high * factor
            if cur == d:
                cnt += low + 1
            elif cur > d:
                cnt += factor
        factor *= 10
    return cnt


def t1(data: str) -> str:
    a, b = map(int, data.split())
    return " ".join(str(_count_digit(b, d) - _count_digit(a - 1, d)) for d in range(10)) + "\n"


def t2(data: str) -> str:
    n = int(data.strip())
    out, cur = [], 1
    for i in range(1, n + 1):
        out.append(" ".join(str(cur + k) for k in range(i)))
        cur += i
    return "\n".join(out) + "\n"


def _palindromes(length: int):
    if length == 1:
        for d in range(1, 10):
            yield d
        return
    if length % 2 == 0:
        half = length // 2
        lo, hi = 10 ** (half - 1), 10 ** half
        for h in range(lo, hi):
            s = str(h)
            yield int(s + s[::-1])
    else:
        half = (length + 1) // 2
        lo, hi = 10 ** (half - 1), 10 ** half
        for h in range(lo, hi):
            s = str(h)
            yield int(s + s[-2::-1])


def t3(data: str) -> str:
    a, b = map(int, data.split())
    out = []
    for length in range(1, len(str(b)) + 1):
        for p in _palindromes(length):
            if p < a or p > b:
                continue
            if p >= 2 and is_prime(p):
                out.append(p)
    out.sort()
    return "\n".join(map(str, out)) + ("\n" if out else "")


def t4(data: str) -> str:
    xs = list(map(int, data.split()))
    i, blocks = 0, []
    while i < len(xs):
        n = xs[i]
        i += 1
        mat = [xs[i + r * n:i + (r + 1) * n] for r in range(n)]
        i += n * n
        for k in range(n - 1):
            best = max(range(k, n), key=lambda r: (mat[r][k], -r))
            mat[k], mat[best] = mat[best], mat[k]
        blocks.append("\n".join(" ".join(map(str, row)) for row in mat))
    return "\n".join(blocks) + "\n"


def t5(data: str) -> str:
    lines = [ln.strip() for ln in data.split("\n") if ln.strip() != ""]
    if len(lines) < 2 or not all(ln.isdigit() for ln in lines[:2]):
        return "Input Error\n"
    s1, s2 = lines[0], lines[1]
    return str(int(s1) + int(s2)) + "\n"


def gen_t1(rng):
    return ["1 11\n", "1 1\n", "10 10\n", "100 1000\n", "999 10000\n",
            "1 1000000000\n", "123456 987654321\n", "1 9\n"]


def gen_t2(rng):
    return [f"{n}\n" for n in (1, 2, 3, 5, 9)]


def gen_t3(rng):
    return ["5 500\n", "5 5\n", "100 10000\n", "1000000 10000000\n",
            "99900000 100000000\n", "2 100\n"]


def gen_t4(rng):
    return ["4\n3 6 8 7\n6 7 5 3\n8 6 5 3\n9 8 7 2\n",
            "1\n5\n",
            "2\n1 2\n3 4\n3\n9 1 2\n3 4 5\n6 7 8\n",
            "3\n5 5 5\n5 5 5\n5 5 5\n"]


def gen_t5(rng):
    return ["999999999999999999999\n999999999999999999999\n",
            "123\n456\n", "0\n0\n", "000123\n000077\n",
            "12a\n34\n", "12\n3x\n", "1\n999999999999999999999999999999\n"]


CASES = {
    "2018-t1": {
        "solve": t1,
        "samples": [("1 11\n", "1 4 1 1 1 1 1 1 1 1")],
        "tests": gen_t1,
    },
    "2018-t2": {
        "solve": t2,
        "samples": [("3\n", "1\n2 3\n4 5 6")],
        "tests": gen_t2,
    },
    "2018-t3": {
        "solve": t3,
        "samples": [("5 500\n", None)],
        "tests": gen_t3,
    },
    "2018-t4": {
        "solve": t4,
        "samples": [("4\n3 6 8 7\n6 7 5 3\n8 6 5 3\n9 8 7 2\n", None)],
        "tests": gen_t4,
    },
    "2018-t5": {
        "solve": t5,
        "samples": [("999999999999999999999\n999999999999999999999\n", "1999999999999999999998")],
        "tests": gen_t5,
    },
}
