"""珞珈机试 OJ —— 本地 Web 服务（零第三方依赖）。"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import threading
import time
import uuid
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import judge

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
PROBLEMS = ROOT / "problems"
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
SUBS = DATA / "submissions.jsonl"

INDEX = {}
_progress_lock = threading.Lock()
_sem = threading.Semaphore(2)


def load_index():
    global INDEX
    INDEX = json.loads((PROBLEMS / "index.json").read_text(encoding="utf-8"))


def read_submissions(limit=None):
    if not SUBS.exists():
        return []
    rows = []
    with SUBS.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    rows.reverse()
    return rows[:limit] if limit else rows


def progress():
    out = {}
    for r in read_submissions():
        pid = r.get("problemId")
        if not pid:
            continue
        if out.get(pid) == "AC":
            continue
        out[pid] = "AC" if r.get("status") == "AC" else "TRIED"
    return out


def append_submission(rec):
    with _progress_lock:
        with SUBS.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


class Handler(BaseHTTPRequestHandler):
    server_version = "WHUOJ/1.0"

    def log_message(self, fmt, *args):
        # 只记录 API 错误，避免刷屏
        if args and str(args[0]).startswith("4"):
            super().log_message(fmt, *args)

    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _err(self, msg, code=400):
        self._json({"error": msg}, code)

    def do_GET(self):
        u = urlparse(self.path)
        path = u.path
        if path == "/api/meta":
            prog = progress()
            subs = read_submissions()
            recent = [{k: v for k, v in r.items() if k != "code"} for r in subs[:8]]
            return self._json({
                "index": INDEX,
                "languages": judge.languages(),
                "progress": prog,
                "stats": {
                    "submissions": len(subs),
                    "solved": sum(1 for v in prog.values() if v == "AC"),
                    "recent": recent,
                },
                "serverTime": datetime.now().isoformat(timespec="seconds"),
            })
        if path.startswith("/api/problem/"):
            pid = path.rsplit("/", 1)[-1]
            if not re.fullmatch(r"[a-z0-9-]+", pid):
                return self._err("题目不存在", 404)
            f = PROBLEMS / f"{pid}.json"
            if not f.exists():
                return self._err("题目不存在", 404)
            return self._json(json.loads(f.read_text(encoding="utf-8")))
        if path == "/api/submissions":
            q = parse_qs(u.query)
            limit = int(q.get("limit", ["30"])[0])
            pid = q.get("problemId", [None])[0]
            rows = read_submissions()
            if pid:
                rows = [r for r in rows if r.get("problemId") == pid]
            rows = rows[:max(1, min(limit, 100))]
            for r in rows:
                r.pop("code", None)
            return self._json({"submissions": rows})
        if path.startswith("/api/submission/"):
            sid = path.rsplit("/", 1)[-1]
            for r in read_submissions():
                if r.get("id") == sid:
                    return self._json(r)
            return self._err("记录不存在", 404)
        if path == "/api/health":
            return self._json({"ok": True})
        if path.startswith("/api/"):
            return self._err("Not Found", 404)
        return self._static(path)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path not in ("/api/submit", "/api/run"):
            return self._err("Not Found", 404)
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n > 2 * 1024 * 1024:
                return self._err("请求过大", 413)
            body = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return self._err("请求格式错误")

        if u.path == "/api/run":
            lang = body.get("language", "python")
            code = body.get("code", "")
            if not isinstance(code, str) or len(code) > 200_000:
                return self._err("代码为空或过长")
            stdin_data = body.get("input", "")
            if not isinstance(stdin_data, str):
                return self._err("输入格式错误")
            res = judge.run_once(lang, code, stdin_data[:200_000])
            return self._json(res)

        pid = body.get("problemId", "")
        lang = body.get("language", "python")
        code = body.get("code", "")
        nickname = str(body.get("nickname", ""))[:24]
        if not pid or not isinstance(code, str):
            return self._err("缺少参数")
        if not re.fullmatch(r"[a-z0-9-]+", pid):
            return self._err("题目不存在", 404)
        if len(code) > 200_000:
            return self._err("代码过长")
        if not (PROBLEMS / f"{pid}.json").exists():
            return self._err("题目不存在", 404)

        with _sem:
            res = judge.judge(pid, lang, code)

        rec = {
            "id": uuid.uuid4().hex[:12],
            "ts": datetime.now().isoformat(timespec="seconds"),
            "problemId": pid,
            "language": lang,
            "nickname": nickname or "匿名",
            "status": res.get("status", "CE"),
            "passed": res.get("passed", 0),
            "total": res.get("total", 0),
            "runtime": res.get("time", 0),
            "code": code,
            "message": res.get("message", ""),
        }
        append_submission(rec)
        return self._json({**res, "submissionId": rec["id"]})

    def _static(self, path):
        if path == "/" or path == "":
            path = "/index.html"
        rel = path.lstrip("/")
        target = (WEB / rel).resolve()
        try:
            target.relative_to(WEB.resolve())
        except ValueError:
            return self._err("Forbidden", 403)
        if not target.is_file():
            # SPA fallback
            target = WEB / "index.html"
            if not target.is_file():
                return self._err("Not Found", 404)
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype += "; charset=utf-8"
        self._send(200, target.read_bytes(), ctype)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("WHUOJ_PORT", "8765")))
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--open", action="store_true", help="启动后打开浏览器")
    args = ap.parse_args()

    load_index()
    judge.languages()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"珞珈机试 OJ 已启动：{url}")
    print(f"题目数：{len(INDEX.get('problems', []))}，按 Ctrl+C 停止。")
    for k, v in judge.languages().items():
        print(f"  - {v['label']}: {'可用' if v['available'] else '未检测到'}")
    if args.open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
