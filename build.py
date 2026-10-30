"""把 README 题面、参考解、样例与生成数据构建成 OJ 题目包。

用法：  python build.py
产物：  problems/index.json, problems/<id>.json, tests/<id>.json
"""
from __future__ import annotations

import json
import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from content import sol_2014, sol_2015, sol_2016, sol_2017, sol_2018, sol_2019
from content import sol_2020, sol_2021, sol_2022, sol_2023, sol_2024, sol_2025
from content.common import norm_text
from content.overrides import OVERRIDES

MODULES = [sol_2014, sol_2015, sol_2016, sol_2017, sol_2018, sol_2019,
           sol_2020, sol_2021, sol_2022, sol_2023, sol_2024, sol_2025]

ESSAYS = {
    "2020-t2": {
        "title": "简答题",
        "tags": ["简答题"],
        "difficulty": 1,
    },
    "2020-t3": {
        "title": "设计题",
        "tags": ["设计题"],
        "difficulty": 1,
    },
}

TIME_LIMITS = {
    "2014-t4": 2.0,
    "2015-t4": 2.0,
    "2018-t3": 4.0,
    "2021-t4": 4.0,
    "2025-t1": 3.0,
    "2025-t2": 10.0,
    "2025-t3": 2.0,
    "2025-t5": 2.0,
    "2025-t6": 2.0,
}


def latex_to_text(s: str) -> str:
    """把 README 里轻量 LaTeX 转成可读的 Unicode 文本。"""
    s = s.replace("&nbsp;", " ")

    def frac(m):
        return f"({m.group(1)})/({m.group(2)})"

    s = re.sub(r"\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}", frac, s)
    s = re.sub(r"\\sqrt\{([^{}]*)\}", lambda m: "√(" + m.group(1) + ")", s)
    s = re.sub(r"\\text\{([^{}]*)\}", lambda m: m.group(1), s)
    s = re.sub(r"_\{([^{}]*)\}", r"_(\1)", s)
    s = re.sub(r"\^\{([^{}]*)\}", r"^(\1)", s)
    for a, b in [
        (r"\leq", "≤"), (r"\le", "≤"), (r"\geq", "≥"), (r"\ge", "≥"),
        (r"\times", "×"), (r"\cdot", "·"), (r"\circ", "°"),
        (r"\dots", "…"), (r"\cdots", "…"), (r"\infty", "∞"),
        (r"\left", ""), (r"\right", ""), (r"\,", " "), (r"\;", " "),
        (r"\!", ""), (r"\\", " "), (r"\{", "{"), (r"\}", "}"),
    ]:
        s = s.replace(a, b)
    s = s.replace("$", "")
    s = s.replace("{", "").replace("}", "")
    return s


def parse_table(readme: str):
    meta = {}
    row_re = re.compile(
        r"^\|\s*`(\d{4}-T\d+)`\s*\|\s*\[(.*?)\]\(#.*?\)\s*(?:&nbsp;)*\s*\|\s*(.*?)\s*\|\s*(⭐+)\s*\|"
    )
    for line in readme.splitlines():
        m = row_re.match(line.strip())
        if not m:
            continue
        pid, title, tags, stars = m.groups()
        pid = pid.lower()
        tags = [t.strip() for t in re.split(r"[、,，/]", tags) if t.strip()]
        meta[pid] = {
            "id": pid,
            "year": int(pid[:4]),
            "index": int(pid.split("t")[1]),
            "title": title.strip(),
            "tags": tags,
            "difficulty": len(stars),
        }
    return meta


def parse_sections(readme: str):
    lines = readme.splitlines()
    heads = []
    for i, line in enumerate(lines):
        m = re.match(r"^### (\d{4}-T\d+)\s+(.*)$", line)
        if m:
            heads.append((i, m.group(1), m.group(2).strip()))
    sections = {}
    for k, (i, pid, title) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        body = "\n".join(lines[i + 1:end])
        body = re.split(r"(?m)^\*\*样例", body, maxsplit=1)[0]
        body = re.sub(r"\n---\s*$", "", body).strip()
        sections[pid.lower()] = body
    return sections


def clean_statement(s: str) -> str:
    s = latex_to_text(s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() + "\n"


def build():
    readme = (ROOT / "source" / "README.md").read_text(encoding="utf-8")
    meta = parse_table(readme)
    sections = parse_sections(readme)
    cases = {}
    for mod in MODULES:
        cases.update(mod.CASES)

    all_ids = sorted(meta.keys(), key=lambda x: (int(x[:4]), int(x.split("t")[1])))
    problems_dir = ROOT / "problems"
    tests_dir = ROOT / "tests"
    problems_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)

    index = []
    errors = []

    for pid in all_ids:
        m = meta[pid]
        statement = OVERRIDES.get(pid) or clean_statement(sections.get(pid, ""))
        statement = statement.strip() + "\n"
        entry = {
            "id": pid,
            "year": m["year"],
            "index": m["index"],
            "title": m["title"],
            "tags": m["tags"],
            "difficulty": m["difficulty"],
            "type": "essay" if pid in ESSAYS else "program",
            "timeLimit": TIME_LIMITS.get(pid, 2.0),
            "memoryLimit": 256,
            "statement": statement,
            "samples": [],
            "checker": "tokens",
        }
        if pid in ESSAYS:
            entry["tags"] = ESSAYS[pid]["tags"]
            entry["title"] = ESSAYS[pid]["title"]
            (problems_dir / f"{pid}.json").write_text(
                json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
            index.append({k: entry[k] for k in
                          ("id", "year", "index", "title", "tags", "difficulty", "type")})
            continue

        if pid not in cases:
            errors.append(f"{pid}: 缺少参考解")
            continue
        c = cases[pid]
        solve = c["solve"]
        checker = c.get("checker", "tokens")
        entry["checker"] = checker
        if "tol" in c:
            entry["tol"] = c["tol"]

        sample_inputs = []
        for si, (inp, expected) in enumerate(c["samples"]):
            got = solve(inp)
            if expected is not None:
                if checker == "float":
                    a = [float(x) for x in got.split()]
                    b = [float(x) for x in expected.split()]
                    ok = len(a) == len(b) and all(abs(x - y) <= c.get("tol", 1e-6) for x, y in zip(a, b))
                elif checker == "nowhitespace":
                    ok = re.sub(r"\s+", "", got) == re.sub(r"\s+", "", expected)
                else:
                    ok = norm_text(got) == norm_text(expected)
                if not ok:
                    errors.append(f"{pid} 样例{si + 1} 不符：\n  期望={expected!r}\n  实得={got!r}")
            entry["samples"].append({"input": inp, "output": got})
            sample_inputs.append(inp)

        rng = random.Random(pid)
        inputs = [x if x.endswith("\n") else x + "\n" for x in c["tests"](rng)]
        # 样例也纳入评测，避免样例通过而隐藏点全错的假象
        seen = set()
        tests = []
        for inp in sample_inputs + inputs:
            key = norm_text(inp)
            if key in seen:
                continue
            seen.add(key)
            out = solve(inp)
            tests.append({"input": inp, "output": out})

        if not tests:
            errors.append(f"{pid}: 没有测试数据")
        max_out = max((len(t["output"]) for t in tests), default=0)
        test_pack = {
            "id": pid,
            "checker": checker,
            "tol": c.get("tol"),
            "timeLimit": entry["timeLimit"],
            "tests": tests,
        }
        (tests_dir / f"{pid}.json").write_text(
            json.dumps(test_pack, ensure_ascii=False), encoding="utf-8")
        (problems_dir / f"{pid}.json").write_text(
            json.dumps(entry, ensure_ascii=False, indent=1), encoding="utf-8")
        index.append({k: entry[k] for k in
                      ("id", "year", "index", "title", "tags", "difficulty", "type")})
        print(f"{pid:9s} samples={len(entry['samples'])} tests={len(tests):2d} "
              f"maxout={max_out:6d} {m['title']}")

    index.sort(key=lambda x: (x["year"], x["index"]))
    years = {}
    for p in index:
        years.setdefault(p["year"], []).append(p["id"])
    out = {
        "title": "珞珈机试 OJ",
        "subtitle": "武汉大学计算机学院考研复试机试真题 2014–2025",
        "years": [{"year": y, "problems": ids} for y, ids in sorted(years.items())],
        "problems": index,
    }
    (problems_dir / "index.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    if errors:
        print("\n构建失败：")
        for e in errors:
            print(" -", e)
        return 1
    print(f"\nOK：{len(index)} 道题，输出目录 {problems_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())
