# AI Daily（AI Agent 日报）

每日 **AI Agent** 相关新闻与项目的静态 H5 聚合站：采集数据 → 用 Python 生成页面 → 托管在 Vercel。

**在线站点**

- 自定义域名：<https://lava7397.com>
- Vercel 默认域名：<https://ai-agent-daily-phi.vercel.app>

## 技术栈

- **Python 3.11**（标准库优先，运行时无强依赖第三方包）
- **纯静态 HTML** + Vercel 静态托管
- 内容通过 **GitHub** 与仓库同步；**Hermes Cron** 在每天北京时间 11:30 触发采集与生成流水线

## 仓库结构（要点）

| 路径 | 说明 |
|------|------|
| `generate.py` | 主入口：读 `daily_data.json`，生成 `today.html`、对应 `archives/YYYY-MM-DD.html`，并更新 `home.html` |
| `daily_data.json` | 当日条目数据（由采集侧写入） |
| `today.html` | 当天刊（故意不用 `index.html`，见下节） |
| `home.html` | 首页：历史期刊列表 |
| `archives/` | 按日期的不可变归档页 |
| `images/` | 每日封面图等资源（若使用 `generate_image.py` 等） |
| `sources_registry.json` | 数据源注册与质量信息 |
| `scripts/source_*.py` | 数据源探索、评估、迭代 |
| `deploy.py` / `screenshot.py` | 部署与截图工具 |
| `vercel.json` | 路由与重写 |
| `AGENTS.md` | 面向自动化 Agent 的详细流程与约定 |

## 本地生成

需要已存在 `daily_data.json`（字段结构需与生成器期望一致，可参考仓库内示例或历史提交）。

```bash
cd ~/Hermes/ai-daily-h5   # 或你的克隆路径
python3 generate.py
```

可选：在生成结束后执行数据源迭代脚本：

```bash
python3 generate.py --run-source-evolution
```

## 环境变量

- **`SITE_URL`**：站点规范 URL，未设置时默认为 `https://lava7397.com`（见 `generate.py`）。部署到其它域名时可覆盖。

请勿将密钥、`.env` 等敏感文件提交到 git（见 `.gitignore`）。

## 部署

Vercel 项目名：`ai-agent-daily`。本地可用 CLI 推送生产部署，例如：

```bash
cd ~/Hermes/ai-daily-h5 && vercel --prod --yes
```

（实际以你本机已登录的 Vercel 项目为准。）

## 路由说明（必读）

根路径 `/` 在 `vercel.json` 中重写为 **`home.html`**（首页）。

当天刊文件名为 **`today.html`**，而不是 `index.html`：许多静态托管会把 `/` 默认映射到根目录的 `index.html`，会压过「`/` → `home.html`」的重写，导致首页误显示为「当天刊」。因此本仓库刻意避免用 `index.html` 作为当天刊。

`/index.html` 会 **301 重定向** 到 `/today.html`。

## 约定

- **`archives/`** 中的历史页面视为归档，不要随意删改。
- 更完整的自动化流程、数据流与定时说明见 **[AGENTS.md](./AGENTS.md)**。
