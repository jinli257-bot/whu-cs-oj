import itertools
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from content import sol_2016, sol_2017, sol_2018, sol_2019, sol_2023, sol_2024, sol_2025


def digits_count(a, b):
    c = [0] * 10
    for x in range(a, b + 1):
        for ch in str(x):
            c[int(ch)] += 1
    return c


random.seed(7)

# 2018-T1 区间数码统计
for _ in range(30):
    a = random.randint(1, 3000)
    b = random.randint(a, 5000)
    got = list(map(int, sol_2018.t1(f"{a} {b}\n").split()))
    exp = digits_count(a, b)
    assert got == exp, (a, b, got, exp)
print("2018-t1 ok")

# 2018-T3 回文质数
for a, b in [(5, 500), (2, 1000), (100, 20000), (9990, 100000)]:
    got = [int(x) for x in sol_2018.t3(f"{a} {b}\n").split()]
    exp = [x for x in range(max(2, a), b + 1) if str(x) == str(x)[::-1] and sol_2018.is_prime(x)]
    assert got == exp, (a, b)
print("2018-t3 ok")

# 2017-T5 最小不重复数
def ok_no_repeat(x):
    s = str(x)
    return all(s[i] != s[i + 1] for i in range(len(s) - 1))


for n in list(range(0, 2000)) + [random.randint(0, 50000) for _ in range(200)]:
    x = n + 1
    while not ok_no_repeat(x):
        x += 1
    got = int(sol_2017.t5(f"{n}\n"))
    assert got == x, (n, got, x)
print("2017-t5 ok")

# 2023-T2 最大子段和与首个位置
for _ in range(200):
    n = random.randint(1, 20)
    a = [random.randint(-10, 10) for _ in range(n)]
    best, bl, br = -10 ** 9, 0, 0
    for l in range(n):
        s = 0
        for r in range(l, n):
            s += a[r]
            if s > best:
                best, bl, br = s, l, r
    got = list(map(int, sol_2023.t2(f"{n}\n" + " ".join(map(str, a)) + "\n").split()))
    assert got == [bl + 1, br + 1, best], (a, got, [bl + 1, br + 1, best])
print("2023-t2 ok")

# 2024-T2 三数之和
for _ in range(100):
    n = random.randint(0, 9)
    a = [random.randint(-6, 6) for _ in range(n)]
    exp = set()
    for i, j, k in itertools.combinations(range(n), 3):
        if a[i] + a[j] + a[k] == 0:
            exp.add(tuple(sorted((a[i], a[j], a[k]))))
    got_s = sol_2024.t2(f"{n}\n" + " ".join(map(str, a)) + "\n").strip()
    if got_s == "[]":
        got = set()
    else:
        import ast
        got = {tuple(t) for t in ast.literal_eval(got_s)}
    assert got == exp, (a, got, exp)
print("2024-t2 ok")

# 2025-T1 线段树
for _ in range(100):
    n = random.randint(1, 12)
    m = random.randint(1, 15)
    a = [random.randint(-20, 20) for _ in range(n)]
    lines = [f"{n} {m}", " ".join(map(str, a))]
    exp = []
    for _ in range(m):
        if random.random() < 0.5:
            p = random.randint(1, n)
            v = random.randint(-20, 20)
            a[p - 1] = v
            lines.append(f"1 {p} {v}")
        else:
            l = random.randint(1, n)
            r = random.randint(l, n)
            lines.append(f"2 {l} {r}")
            exp.append(str(max(a[l - 1:r])))
    got = sol_2025.t1("\n".join(lines) + "\n").split()
    assert got == exp, (lines, got, exp)
print("2025-t1 ok")

# 2025-T3 时变最短路：小图 Bellman-Ford 式松弛
def brute_t3(n, edges):
    INF = 10 ** 18
    dist = [INF] * (n + 1)
    dist[1] = 0
    for _ in range(n + 2):
        updated = False
        for u, v, w, x in edges:
            if dist[u] <= x and x + w < dist[v]:
                dist[v] = x + w
                updated = True
        if not updated:
            break
    return -1 if dist[n] >= INF else dist[n]


for _ in range(100):
    n = random.randint(2, 6)
    m = random.randint(1, 10)
    edges = []
    for _ in range(m):
        u = random.randint(1, n)
        v = random.randint(1, n)
        edges.append((u, v, random.randint(0, 6), random.randint(0, 10)))
    inp = f"{n} {m}\n" + "".join(f"{u} {v} {w} {x}\n" for u, v, w, x in edges)
    got = int(sol_2025.t3(inp))
    exp = brute_t3(n, edges)
    assert got == exp, (inp, got, exp)
print("2025-t3 ok")

# 2025-T4 引力最短路
def brute_t4(n, g, edges, s, e):
    INF = 10 ** 18
    dist = [INF] * (n + 1)
    dist[s] = 0
    for _ in range(n):
        for u, v, w in edges:
            c = w + abs(g[u] - g[v])
            if dist[u] + c < dist[v]:
                dist[v] = dist[u] + c
            if dist[v] + c < dist[u]:
                dist[u] = dist[v] + c
    return -1 if dist[e] >= INF else dist[e]


for _ in range(60):
    n = random.randint(1, 6)
    g = [0] + [random.randint(0, 10) for _ in range(n)]
    m = random.randint(1, 8)
    edges = []
    for _ in range(m):
        edges.append((random.randint(1, n), random.randint(1, n), random.randint(0, 8)))
    s = random.randint(1, n)
    e = random.randint(1, n)
    inp = f"{n}\n" + " ".join(map(str, g[1:])) + f"\n{m}\n" + "".join(f"{u} {v} {w}\n" for u, v, w in edges) + f"{s} {e}\n"
    got = int(sol_2025.t4(inp))
    exp = brute_t4(n, g, edges, s, e)
    assert got == exp, (inp, got, exp)
print("2025-t4 ok")

# 2025-T5 连通性
for _ in range(100):
    k = random.randint(1, 12)
    items = []
    # 随机生成一个真实划分，再随机改 op，制造有解/无解
    labels = [random.randint(0, 2) for _ in range(6)]
    for _ in range(k):
        x = random.randint(1, 6)
        y = random.randint(1, 6)
        op = 1 if labels[x - 1] == labels[y - 1] else 0
        if random.random() < 0.25:
            op ^= 1
        items.append((x, y, op))
    inp = f"1\n{k}\n" + "".join(f"{x} {y} {op}\n" for x, y, op in items)
    got = sol_2025.t5(inp).strip()
    # brute: 枚举 6 个点的划分
    exp = "NO"
    for lab in itertools.product(range(6), repeat=6):
        if all(((lab[x - 1] == lab[y - 1]) == (op == 1)) for x, y, op in items):
            exp = "YES"
            break
    assert got == exp, (items, got, exp)
print("2025-t5 ok")

# 2025-T6 加权区间调度
def brute_t6(jobs):
    n = len(jobs)
    best = 0
    for mask in range(1 << n):
        sel = [jobs[i] for i in range(n) if mask >> i & 1]
        sel.sort()
        ok = all(sel[i][1] <= sel[i + 1][0] for i in range(len(sel) - 1))
        if ok:
            best = max(best, sum(j[2] for j in sel))
    return best


for _ in range(80):
    n = random.randint(1, 9)
    jobs = []
    for _ in range(n):
        x = random.randint(0, 10)
        y = random.randint(x + 1, 12)
        jobs.append((x, y, random.randint(1, 20)))
    inp = f"{n}\n" + "".join(f"{x} {y} {z}\n" for x, y, z in jobs)
    got = int(sol_2025.t6(inp))
    exp = brute_t6(jobs)
    assert got == exp, (jobs, got, exp)
print("2025-t6 ok")

# 2016-T3 放苹果
def brute_apples(m, n):
    ways = set()
    def rec(rem, parts, last):
        if rem == 0:
            ways.add(tuple(sorted(parts)))
            return
        for x in range(1, min(rem, last) + 1):
            rec(rem - x, parts + [x], x)
    rec(m, [], m)
    return sum(1 for w in ways if len(w) <= n)


for m in range(0, 12):
    for n in range(1, 8):
        got = int(sol_2016.t3(f"{m} {n}\n"))
        exp = brute_apples(m, n)
        assert got == exp, (m, n, got, exp)
print("2016-t3 ok")

print("ALL OK")
