import sys, random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from content.sol_2025 import t2


def brute(n, m, g):
    cells = [(r, c) for r in range(n) for c in range(m) if g[r][c] == "."]
    best = 10 ** 9
    for mask in range(1 << len(cells)):
        cnt = bin(mask).count("1")
        if cnt >= best:
            continue
        cov = set()
        for i, (r, c) in enumerate(cells):
            if mask >> i & 1:
                for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    if 0 <= r + dr < n and 0 <= c + dc < m:
                        cov.add((r + dr, c + dc))
        if all(p in cov for p in cells):
            best = cnt
    return best if best < 10 ** 9 else -1


random.seed(1)
for n, m in [(1, 1), (2, 2), (2, 3), (3, 3), (3, 4), (4, 4)]:
    for t in range(60):
        g = ["".join("." if random.random() < 0.75 else "#" for _ in range(m)) for _ in range(n)]
        if all(ch == "#" for row in g for ch in row):
            continue
        inp = f"{n} {m}\n" + "\n".join(g) + "\n"
        a = int(t2(inp))
        b = brute(n, m, g)
        if a != b:
            print("MISMATCH", n, m, g, a, b)
            sys.exit(1)
    print("ok", n, m)
print("all ok")
