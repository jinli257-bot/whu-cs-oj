# 部署说明

## 先看结论

这套项目最初是**本地 OJ**：评测机直接在当前机器上编译、运行提交的代码。

- 自己用、班级内网用：没问题。
- 放到公网给陌生人用：**不要直接暴露 `server.py`**。

原因很简单：任何人提交一段 C++/Python，都会在你的服务器上执行。没有容器隔离、内存限制、网络隔离和限流，等于开放了一个远程代码执行入口。

## 方式一：本机运行（推荐）

Windows：

```bat
run.bat
```

macOS / Linux：

```bash
./run.sh
```

访问 `http://127.0.0.1:8765`。

## 方式二：Docker 本地/内网运行

```bash
docker compose up -d --build
```

访问 `http://服务器IP:8765`。

镜像内已经安装了 `g++`、`gcc`、`nodejs`，所以 C++ / C / JavaScript 都能评测。

停止：

```bash
docker compose down
```

> 即使用了 Docker，也不要在没有额外防护的情况下把端口开放到公网。Docker 只提供进程隔离，不是安全沙箱。

## 方式三：部署到 VPS（仅限可信用户）

如果只是给同学用，可以：

1. 买一台 VPS，安装 Docker。
2. 克隆仓库，执行 `docker compose up -d --build`。
3. 用 Caddy / Nginx 反向代理到 `127.0.0.1:8765`，配置 HTTPS。
4. 用防火墙只开放 80/443，不要直接暴露 8765。
5. 最好再加一层 HTTP Basic Auth，或者只在内网/ Tailscale 中访问。

Caddy 示例：

```caddyfile
oj.example.com {
    reverse_proxy 127.0.0.1:8765
}
```

## 方式四：做成真正的公网在线 OJ

需要把“Web 服务”和“评测执行”拆开，并给评测加沙箱。大致架构：

```text
浏览器
  │
  ▼
Web API（登录、题目、提交、限流）
  │  提交任务
  ▼
消息队列（Redis / RabbitMQ）
  │
  ▼
评测 Worker（每个提交一个临时容器）
  ├─ 非 root 用户
  ├─ --network none
  ├─ --memory 256m
  ├─ --cpus 0.5
  ├─ --pids-limit 64
  ├─ 只读根文件系统
  ├─ 挂载只读输入 / 临时输出
  └─ 超时强制 kill
```

关键点：

- 评测容器不能访问外网。
- 不能挂载 Docker socket。
- 不能用 root 运行用户代码。
- 必须限制 CPU、内存、进程数、输出大小。
- 编译和运行分开计时。
- 提交要排队，不能无限并发。
- 需要有登录、限流、防刷和日志。

如果不想自己做沙箱，可以接 **Judge0** 这类现成的评测服务。

## GitHub Pages 能做什么

GitHub Pages 只能托管静态文件，**不能运行 Python 评测后端**。

所以：

- 可以用 Pages 放项目介绍页、截图、题目浏览页面；
- 但不能在 Pages 上真正提交代码并评测。

## 安全清单

上线前至少确认：

- [ ] 服务不是以 root 运行
- [ ] 评测进程不能联网
- [ ] 每次提交有超时
- [ ] 有内存 / CPU / 进程数限制
- [ ] 有并发限制和频率限制
- [ ] 不把 `data/submissions.jsonl` 暴露为静态文件
- [ ] 不在公网直接开放 8765
- [ ] 有 HTTPS
- [ ] 有日志和异常告警

如果这些做不到，建议保持“本地运行”或“内网访问”。
