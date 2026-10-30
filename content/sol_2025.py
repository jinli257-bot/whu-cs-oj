"""2025 年参考解与测试数据生成。"""
from __future__ import annotations

import heapq
from bisect import bisect_right


# ---------------- 2025-T1 线段树 ----------------
def t1(data: str) -> str:
    xs = list(map(int, data.split()))
    n, m = xs[0], xs[1]
    a = xs[2:2 + n]
    size = 1
    while size < n:
        size <<= 1
    tree = [-10 ** 30] * (2 * size)
    for i, v in enumerate(a):
        tree[size + i] = v
    for i in range(size - 1, 0, -1):
        tree[i] = max(tree[2 * i], tree[2 * i + 1])

    def update(pos, val):
        i = size + pos
        tree[i] = val
        i //= 2
        while i:
            tree[i] = max(tree[2 * i], tree[2 * i + 1])
            i //= 2

    def query(l, r):  # [l, r)
        l += size
        r += size
        res = -10 ** 30
        while l < r:
            if l & 1:
                res = max(res, tree[l])
                l += 1
            if r & 1:
                r -= 1
                res = max(res, tree[r])
            l //= 2
            r //= 2
        return res

    out = []
    i = 2 + n
    for _ in range(m):
        op, x, y = xs[i], xs[i + 1], xs[i + 2]
        i += 3
        if op == 1:
            update(x - 1, y)
        else:
            out.append(str(query(x - 1, y)))
    return "\n".join(out) + ("\n" if out else "")


# ---------------- 2025-T2 棋盘最小覆盖 ----------------
def t2(data: str) -> str:
    lines = [ln for ln in data.strip("\n").split("\n")]
    n, m = map(int, lines[0].split())
    g = [ln.strip() for ln in lines[1:1 + n]]
    if m > n:
        g = ["".join(g[r][c] for r in range(n)) for c in range(m)]
        n, m = m, n
    full = (1 << m) - 1
    empty = []
    for row in g:
        mask = 0
        for c, ch in enumerate(row):
            if ch == ".":
                mask |= 1 << c
        empty.append(mask)
    if all(x == 0 for x in empty):
        return "0\n"

    exp = [0] * (1 << m)
    for mask in range(1 << m):
        exp[mask] = (mask | (mask << 1) | (mask >> 1)) & full
    pc = [bin(x).count("1") for x in range(1 << m)]
    INF = 10 ** 9

    # dp[(P, C)]：P = 上一行放置掩码，C = 上一行已被上/自身/左右覆盖的掩码
    dp = {(0, 0): 0}
    for r in range(n):
        e = empty[r]
        e_prev = empty[r - 1] if r > 0 else 0
        # 行内状态：(P, C, Q)，Q 为当前行已经放置的掩码
        cur = {}
        for (P, C), cost in dp.items():
            cur[(P, C, 0)] = cost
        for c in range(m):
            bit = 1 << c
            can_place = bool(e & bit)
            nxt = {}
            for (P, C, Q), cost in cur.items():
                # 不放置
                if r > 0 and (e_prev & bit) and not (C & bit):
                    pass  # 该格必须由下方（当前行）覆盖，不能跳过
                else:
                    key = (P, C, Q)
                    if cost < nxt.get(key, INF):
                        nxt[key] = cost
                # 放置
                if can_place:
                    key = (P, C, Q | bit)
                    if cost + 1 < nxt.get(key, INF):
                        nxt[key] = cost + 1
            cur = nxt
            if not cur:
                return "-1\n"
        ndp = {}
        for (P, C, Q), cost in cur.items():
            key = (Q, P | exp[Q])
            if cost < ndp.get(key, INF):
                ndp[key] = cost
        dp = ndp

    ans = INF
    for (P, C), cost in dp.items():
        if (C & empty[n - 1]) == empty[n - 1]:
            ans = min(ans, cost)
    return f"{ans if ans < INF else -1}\n"


# ---------------- 2025-T3 定点单向通行最短路 ----------------
def t3(data: str) -> str:
    xs = list(map(int, data.split()))
    n, m = xs[0], xs[1]
    adj = [[] for _ in range(n + 1)]
    i = 2
    for _ in range(m):
        u, v, w, x = xs[i:i + 4]
        i += 4
        adj[u].append((v, w, x))
    INF = 10 ** 30
    dist = [INF] * (n + 1)
    dist[1] = 0
    pq = [(0, 1)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        if u == n:
            break
        for v, w, x in adj[u]:
            if d <= x:
                nd = x + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
    return f"{dist[n] if dist[n] < INF else -1}\n"


# ---------------- 2025-T4 星球引力旅行 ----------------
def t4(data: str) -> str:
    xs = list(map(int, data.split()))
    n = xs[0]
    g = [0] + xs[1:1 + n]
    i = 1 + n
    m = xs[i]
    i += 1
    adj = [[] for _ in range(n + 1)]
    for _ in range(m):
        u, v, w = xs[i:i + 3]
        i += 3
        c = w + abs(g[u] - g[v])
        adj[u].append((v, c))
        adj[v].append((u, c))
    s, e = xs[i], xs[i + 1]
    INF = 10 ** 30
    dist = [INF] * (n + 1)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]:
            continue
        if u == e:
            break
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return f"{dist[e] if dist[e] < INF else -1}\n"


# ---------------- 2025-T5 连通性逻辑校验 ----------------
def t5(data: str) -> str:
    xs = list(map(int, data.split()))
    t = xs[0]
    i = 1
    out = []
    for _ in range(t):
        k = xs[i]
        i += 1
        parent = {}

        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        constraints = []
        for _ in range(k):
            x, y, op = xs[i], xs[i + 1], xs[i + 2]
            i += 3
            if op == 1:
                rx, ry = find(x), find(y)
                if rx != ry:
                    parent[rx] = ry
            else:
                constraints.append((x, y))
        ok = True
        for x, y in constraints:
            if find(x) == find(y):
                ok = False
                break
        out.append("YES" if ok else "NO")
    return "\n".join(out) + "\n"


# ---------------- 2025-T6 工作最大收益 ----------------
def t6(data: str) -> str:
    xs = list(map(int, data.split()))
    n = xs[0]
    jobs = []
    i = 1
    for _ in range(n):
        x, y, z = xs[i], xs[i + 1], xs[i + 2]
        i += 3
        jobs.append((x, y, z))
    jobs.sort(key=lambda t: t[1])
    ends = [j[1] for j in jobs]
    dp = [0] * (n + 1)
    for i, (x, y, z) in enumerate(jobs, 1):
        p = bisect_right(ends, x)
        dp[i] = max(dp[i - 1], dp[p] + z)
    return f"{dp[n]}\n"


# ---------------- 生成器 ----------------
def gen_t1(rng):
    out = ["5 5\n1 5 2 4 3\n2 1 5\n1 2 10\n2 1 5\n2 3 4\n2 2 3\n",
           "1 3\n-5\n2 1 1\n1 1 7\n2 1 1\n",
           "6 4\n5 5 5 5 5 5\n2 1 6\n1 3 -7\n2 2 4\n2 3 3\n"]
    n = m = 20000
    a = [rng.randint(-10 ** 9, 10 ** 9) for _ in range(n)]
    ops = []
    for _ in range(m):
        if rng.random() < 0.5:
            ops.append(f"1 {rng.randint(1, n)} {rng.randint(-10 ** 9, 10 ** 9)}")
        else:
            l = rng.randint(1, n)
            r = rng.randint(l, n)
            ops.append(f"2 {l} {r}")
    out.append(f"{n} {m}\n" + " ".join(map(str, a)) + "\n" + "\n".join(ops) + "\n")
    return out


def gen_t2(rng):
    return ["4 4\n#...\n....\n....\n...#\n",
            "1 1\n.\n",
            "1 1\n#\n",
            "2 2\n..\n..\n",
            "3 3\n...\n...\n...\n",
            "2 3\n#.#\n.#.\n",
            "5 5\n.....\n.###.\n.#.#.\n.###.\n.....\n",
            "10 10\n" + "\n".join(["." * 10] * 10) + "\n"]


def gen_t3(rng):
    return ["3 3\n1 2 5 6\n1 3 20 1\n2 3 3 12\n",
            "2 1\n1 2 5 0\n",
            "2 1\n1 2 5 3\n",
            "4 5\n1 2 10 0\n2 4 5 10\n1 3 1 100\n3 4 1 11\n1 4 30 100\n",
            "3 1\n2 3 1 0\n"]


def gen_t4(rng):
    return ["3\n10 20 15\n3\n1 2 5\n2 3 2\n1 3 20\n1 3\n",
            "2\n5 10\n1\n1 2 3\n1 2\n",
            "3\n1 2 3\n1\n1 2 100\n1 3\n",
            "4\n0 10 20 30\n3\n1 2 1\n2 3 1\n3 4 1\n1 4\n"]


def gen_t5(rng):
    return ["2\n3\n1 2 1\n2 3 1\n1 3 0\n2\n1 2 1\n3 4 1\n",
            "1\n1\n1 2 0\n",
            "1\n2\n5 5 1\n5 5 0\n",
            "3\n2\n1 2 0\n1 2 1\n3\n1 2 1\n2 3 1\n1 3 0\n2\n10 20 0\n10 20 0\n"]


def gen_t6(rng):
    return ["3\n1 3 10\n3 5 10\n2 4 100\n",
            "1\n1 2 5\n",
            "4\n1 10 5\n2 3 6\n3 4 7\n10 11 3\n",
            "5\n1 2 3\n2 3 4\n3 4 5\n4 5 6\n5 6 7\n"]


CASES = {
    "2025-t1": {
        "solve": t1,
        "samples": [("5 5\n1 5 2 4 3\n2 1 5\n1 2 10\n2 1 5\n2 3 4\n2 2 3\n",
                     "5\n10\n4\n10")],
        "tests": gen_t1,
    },
    "2025-t2": {
        "solve": t2,
        "samples": [("4 4\n#...\n....\n....\n...#\n", "4")],
        "tests": gen_t2,
    },
    "2025-t3": {
        "solve": t3,
        "samples": [("3 3\n1 2 5 6\n1 3 20 1\n2 3 3 12\n", "15")],
        "tests": gen_t3,
    },
    "2025-t4": {
        "solve": t4,
        "samples": [("3\n10 20 15\n3\n1 2 5\n2 3 2\n1 3 20\n1 3\n", "22")],
        "tests": gen_t4,
    },
    "2025-t5": {
        "solve": t5,
        "samples": [("2\n3\n1 2 1\n2 3 1\n1 3 0\n2\n1 2 1\n3 4 1\n", "NO\nYES")],
        "tests": gen_t5,
    },
    "2025-t6": {
        "solve": t6,
        "samples": [("3\n1 3 10\n3 5 10\n2 4 100\n", "100")],
        "tests": gen_t6,
    },
}
