"""本地评测机：编译 / 运行 / 比对，支持 Python、C、C++、JavaScript。"""
from __future__ import annotations

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBLEMS = ROOT / "problems"
TESTS = ROOT / "tests"
WORK = ROOT / "work"
WORK.mkdir(exist_ok=True)

MAX_OUTPUT = 16 * 1024 * 1024
COMPILE_TIMEOUT = 25

_LANG_CACHE = None


def _mkwork(prefix: str) -> Path:
    WORK.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(WORK)))


def _find_node():
    cands = [
        os.environ.get("WHUOJ_NODE"),
        shutil.which("node"),
        r"C:\Program Files\nodejs\node.exe",
        os.path.expandvars(r"%ProgramFiles%\nodejs\node.exe"),
        os.path.expandvars(r"%USERPROFILE%\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\node\bin\node.exe"),
    ]
    for p in cands:
        if p and Path(p).exists():
            return str(p)
    return None


def _find_compiler(name):
    env = os.environ.get("WHUOJ_" + name.upper())
    cands = [env]
    for n in (name, name + ".exe"):
        w = shutil.which(n)
        if w:
            cands.append(w)
    cands += [
        rf"C:\msys64\mingw64\bin\{name}.exe",
        rf"C:\msys64\ucrt64\bin\{name}.exe",
        rf"C:\MinGW\bin\{name}.exe",
        rf"C:\mingw64\bin\{name}.exe",
        rf"C:\Program Files\LLVM\bin\{name}.exe",
        rf"C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\{name}.exe",
        rf"C:\Program Files\Dev-Cpp\MinGW64\bin\{name}.exe",
        rf"C:\Program Files (x86)\Dev-Cpp\TDM-GCC-64\bin\{name}.exe",
        rf"C:\Program Files\Dev-Cpp\TDM-GCC-64\bin\{name}.exe",
        rf"D:\Dev-Cpp\MinGW64\bin\{name}.exe",
        rf"D:\Dev-Cpp\TDM-GCC-64\bin\{name}.exe",
        rf"D:\Program Files (x86)\Dev-Cpp\TDM-GCC-64\bin\{name}.exe",
        rf"D:\Program Files\Dev-Cpp\TDM-GCC-64\bin\{name}.exe",
        rf"D:\Program Files (x86)\Dev-Cpp\MinGW64\bin\{name}.exe",
        rf"D:\Program Files\Dev-Cpp\MinGW64\bin\{name}.exe",
        rf"D:\msys64\mingw64\bin\{name}.exe",
    ]
    # 项目内自带/解压的工具链也可以直接用
    for base in (ROOT / "tools", ROOT / "toolchain", ROOT / "mingw64"):
        try:
            for p in base.glob(f"**/bin/{name}.exe"):
                cands.append(str(p))
        except OSError:
            pass
    for p in cands:
        if p and Path(p).exists():
            return str(p)
    return None


def languages():
    global _LANG_CACHE
    if _LANG_CACHE is None:
        _LANG_CACHE = {
            "python": {"label": "Python 3", "available": True,
                       "template": "import sys\n\ndef main():\n    data = sys.stdin.read().split()\n    # TODO\n\nif __name__ == \"__main__\":\n    main()\n"},
            "cpp": {"label": "C++17", "available": bool(_find_compiler("g++")),
                    "template": "#include <bits/stdc++.h>\nusing namespace std;\n\nint main() {\n    ios::sync_with_stdio(false);\n    cin.tie(nullptr);\n\n    return 0;\n}\n"},
            "c": {"label": "C11", "available": bool(_find_compiler("gcc")),
                  "template": "#include <stdio.h>\n\nint main(void) {\n    \n    return 0;\n}\n"},
            "javascript": {"label": "JavaScript (Node)", "available": bool(_find_node()),
                           "template": "const fs = require('fs');\nconst data = fs.readFileSync(0, 'utf8').trim().split(/\\s+/);\n\n// TODO\n"},
        }
    return _LANG_CACHE


def _norm(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")


def _tokens(s: str):
    return _norm(s).split()


def _compare(checker: str, inp: str, out: str, expected: str, tol):
    if checker == "nowhitespace":
        return re.sub(r"\s+", "", _norm(out)) == re.sub(r"\s+", "", _norm(expected))
    if checker == "twosum":
        return _check_twosum(inp, out)
    a, b = _tokens(out), _tokens(expected)
    if checker == "float":
        if len(a) != len(b):
            return False
        try:
            return all(abs(float(x) - float(y)) <= (tol or 1e-6) for x, y in zip(a, b))
        except ValueError:
            return False
    return a == b


def _check_twosum(inp: str, out: str) -> bool:
    xs = [int(x) for x in inp.split()]
    n, arr, x = xs[0], xs[1:1 + xs[0]], xs[1 + xs[0]]
    t = out.split()
    if out.strip() == "error":
        seen = set()
        for v in arr:
            if x - v in seen:
                return False
            seen.add(v)
        return True
    if len(t) != 2:
        return False
    try:
        a, b = int(t[0]), int(t[1])
    except ValueError:
        return False
    if a + b != x:
        return False
    if a == b:
        return arr.count(a) >= 2
    return a in arr and b in arr


def _kill_tree(proc):
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        else:
            proc.kill()
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def _run(cmd, cwd, stdin_data: bytes, limit: float):
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    start = time.perf_counter()
    p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env)
    try:
        out, err = p.communicate(input=stdin_data, timeout=limit)
        elapsed = time.perf_counter() - start
    except subprocess.TimeoutExpired:
        _kill_tree(p)
        try:
            p.communicate(timeout=2)
        except Exception:
            pass
        return {"status": "TLE", "time": limit, "stdout": "", "stderr": ""}
    if len(out) > MAX_OUTPUT:
        return {"status": "OLE", "time": elapsed, "stdout": "", "stderr": ""}
    return {
        "status": "OK" if p.returncode == 0 else "RE",
        "time": elapsed,
        "stdout": out.decode("utf-8", "replace"),
        "stderr": err.decode("utf-8", "replace")[:4000],
        "returncode": p.returncode,
    }


def judge(problem_id: str, lang: str, code: str):
    langs = languages()
    if lang not in langs:
        return {"status": "CE", "message": "不支持的语言", "tests": []}
    if not langs[lang]["available"]:
        return {"status": "CE", "message": f"{langs[lang]['label']} 在本机不可用", "tests": []}

    pfile = PROBLEMS / f"{problem_id}.json"
    tfile = TESTS / f"{problem_id}.json"
    if not pfile.exists() or not tfile.exists():
        return {"status": "CE", "message": "题目不存在", "tests": []}
    prob = json.loads(pfile.read_text(encoding="utf-8"))
    pack = json.loads(tfile.read_text(encoding="utf-8"))
    if prob.get("type") == "essay":
        return {"status": "CE", "message": "主观题不参与评测", "tests": []}

    work = None
    try:
        if lang == "python" and len(code) <= 28000:
            # 直接 -c 运行，避免在受限环境里写临时文件
            cmd = [sys.executable, "-X", "utf8", "-c", code]
        elif lang == "javascript" and len(code) <= 20000:
            b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
            cmd = [_find_node(), "-e",
                   f"eval(Buffer.from('{b64}','base64').toString('utf8'))"]
        elif lang == "python":
            work = _mkwork("whuoj_")
            src = work / "main.py"
            src.write_text(code, encoding="utf-8")
            cmd = [sys.executable, "-X", "utf8", str(src)]
        elif lang == "javascript":
            work = _mkwork("whuoj_")
            src = work / "main.js"
            src.write_text(code, encoding="utf-8")
            cmd = [_find_node(), str(src)]
        elif lang in ("cpp", "c"):
            work = _mkwork("whuoj_")
            compiler = _find_compiler("g++" if lang == "cpp" else "gcc")
            src = work / ("main.cpp" if lang == "cpp" else "main.c")
            src.write_text(code, encoding="utf-8")
            exe = work / ("main.exe" if os.name == "nt" else "main")
            cflags = ["-O2", "-std=c++17", "-pipe", "-static"] if lang == "cpp" else ["-O2", "-std=c11", "-pipe", "-static"]
            try:
                cp = subprocess.run([compiler, *cflags, str(src), "-o", str(exe)],
                                    capture_output=True, timeout=COMPILE_TIMEOUT)
            except subprocess.TimeoutExpired:
                return {"status": "CE", "message": "编译超时", "tests": []}
            if cp.returncode != 0:
                return {"status": "CE", "message": cp.stderr.decode("utf-8", "replace")[:8000], "tests": []}
            cmd = [str(exe)]
        else:
            return {"status": "CE", "message": "不支持的语言", "tests": []}

        checker = pack.get("checker", "tokens")
        tol = pack.get("tol")
        limit = float(pack.get("timeLimit") or prob.get("timeLimit") or 2.0)
        results = []
        total = len(pack["tests"])
        passed = 0
        for i, case in enumerate(pack["tests"], 1):
            r = _run(cmd, work or ROOT, case["input"].encode("utf-8"), limit + 0.25)
            if r["status"] == "TLE":
                results.append({"i": i, "status": "TLE", "time": round(r["time"], 3)})
                return {"status": "TLE", "passed": passed, "total": total, "time": round(r["time"], 3),
                        "tests": results, "message": "运行超时", "firstFail": i}
            if r["status"] == "RE":
                results.append({"i": i, "status": "RE", "time": round(r["time"], 3),
                                "stderr": r["stderr"][:1500]})
                return {"status": "RE", "passed": passed, "total": total, "time": round(r["time"], 3),
                        "tests": results, "message": "运行时错误", "firstFail": i}
            if r["status"] == "OLE":
                results.append({"i": i, "status": "OLE", "time": round(r["time"], 3)})
                return {"status": "OLE", "passed": passed, "total": total, "time": round(r["time"], 3),
                        "tests": results, "message": "输出超过限制", "firstFail": i}
            ok = _compare(checker, case["input"], r["stdout"], case["output"], tol)
            if ok:
                passed += 1
                results.append({"i": i, "status": "AC", "time": round(r["time"], 3)})
            else:
                results.append({"i": i, "status": "WA", "time": round(r["time"], 3),
                                "stdout": r["stdout"][:800]})
                return {"status": "WA", "passed": passed, "total": total, "time": round(r["time"], 3),
                        "tests": results, "message": "答案错误", "firstFail": i}
        return {"status": "AC", "passed": passed, "total": total,
                "time": round(max((x["time"] for x in results), default=0), 3), "tests": results}
    finally:
        if work:
            shutil.rmtree(work, ignore_errors=True)


def run_once(lang: str, code: str, stdin_data: str):
    langs = languages()
    if lang not in langs or not langs[lang]["available"]:
        return {"status": "CE", "message": "语言不可用"}
    work = None
    try:
        if lang == "python" and len(code) <= 28000:
            cmd = [sys.executable, "-X", "utf8", "-c", code]
        elif lang == "javascript" and len(code) <= 20000:
            b64 = base64.b64encode(code.encode("utf-8")).decode("ascii")
            cmd = [_find_node(), "-e",
                   f"eval(Buffer.from('{b64}','base64').toString('utf8'))"]
        elif lang == "python":
            work = _mkwork("whuoj_run_")
            (work / "main.py").write_text(code, encoding="utf-8")
            cmd = [sys.executable, "-X", "utf8", str(work / "main.py")]
        elif lang == "javascript":
            work = _mkwork("whuoj_run_")
            (work / "main.js").write_text(code, encoding="utf-8")
            cmd = [_find_node(), str(work / "main.js")]
        elif lang in ("cpp", "c"):
            work = _mkwork("whuoj_run_")
            compiler = _find_compiler("g++" if lang == "cpp" else "gcc")
            src = work / ("main.cpp" if lang == "cpp" else "main.c")
            src.write_text(code, encoding="utf-8")
            exe = work / ("main.exe" if os.name == "nt" else "main")
            cflags = ["-O2", "-std=c++17", "-pipe", "-static"] if lang == "cpp" else ["-O2", "-std=c11", "-pipe", "-static"]
            cp = subprocess.run([compiler, *cflags, str(src), "-o", str(exe)],
                                capture_output=True, timeout=COMPILE_TIMEOUT)
            if cp.returncode != 0:
                return {"status": "CE", "message": cp.stderr.decode("utf-8", "replace")[:8000]}
            cmd = [str(exe)]
        else:
            return {"status": "CE", "message": "不支持的语言"}
        r = _run(cmd, work or ROOT, stdin_data.encode("utf-8"), 5.0)
        return {"status": r["status"], "stdout": r.get("stdout", ""),
                "stderr": r.get("stderr", ""), "time": round(r.get("time", 0), 3)}
    finally:
        if work:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    print(json.dumps(languages(), ensure_ascii=False, indent=2))
