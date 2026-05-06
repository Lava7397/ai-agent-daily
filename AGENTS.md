# AI Daily - Agent 行动指南

## 项目概述

每日 AI Agent 新闻聚合站。由定时任务自动采集 → 生成静态 H5 页面 → 部署到 Vercel。
聚焦两件事:**自动化内容生产** + **静态网站建设**。

## 项目结构

```
ai-daily-h5/
├── generate.py              # 主入口：daily_data → H5（HTML 模板在本文件；逻辑在 aidaily/）
├── aidaily/                 # 路径、常量、load/cap、归档、status、issue-data 桥接、render（build_html）
├── generate_image.py        # 生成每日封面图
├── deploy.py                # Vercel 部署脚本
├── screenshot.py            # 页面截图工具
├── today.html               # 当天刊(不是 index.html)
├── home.html                # 首页
├── status.json              # 构建元数据（generate 写入）
├── daily_data.json          # Hermes 写入；collect_manual.py 仅兜底
├── sources_registry.json    # 数据源注册表
├── archives/                # 历史归档 YYYY-MM-DD.html
├── issue-data/              # 各期紧凑 JSON；可 rerender_issue_from_data 重渲
├── images/                  # 每日封面图
├── journal-data.json        # Lava 期刊正文（手工写入；见 JOURNAL.md）
├── JOURNAL.md               # 期刊数据约定、风险与流程
├── shizi/                   # Next 导出（npm run build，不提交 git）
├── scripts/
│   ├── rerender_issue_from_data.py
│   ├── sync_issue_pages.py  # 已废弃，仅打印说明
│   ├── source_explorer.py
│   ├── source_evaluator.py
│   ├── source_evolution.py
│   ├── export_mascot_from_raw.py
│   └── compress_images.py
├── sites/four-persimmons/   # Next 源码
├── vercel.json
└── CNAME
```

## 技术栈

- Python 3.11(标准库优先,零第三方依赖)
- Vercel(静态托管)
- GitHub(代码 + 数据同存,push 即部署)
- Hermes Cron(定时触发)

## 数据流

```
Hermes Cron (每天 11:30 BJT)
      │
      ▼
 Hermes Agent 拉取各数据源 → 写入 daily_data.json
      │
      ▼
 generate.py → 生成 archives/YYYY-MM-DD.html + 更新 home.html
      │
      ▼
 git commit + push → GitHub
      │
      ▼
 Vercel 自动重新部署 → lava7397.com
```

## Vercel 配置

- 项目名:ai-agent-daily
- 部署命令:`cd ~/Hermes/ai-daily-h5 && vercel --prod --yes`
- 站点地址:[https://lava7397.com](https://lava7397.com)(自定义域名,配置在 Vercel dashboard)
- Vercel 默认域名:[https://ai-agent-daily-phi.vercel.app](https://ai-agent-daily-phi.vercel.app)(备用访问)
- 站点地址在代码里是单一常量:`aidaily.config` 的 `SITE_URL`(可用同名环境变量覆盖)
- **路由说明**:当日刊页面文件名为 `today.html`(不是 `index.html`)。静态托管普遍会把 URL `/` 映射到根目录的 `index.html`,其优先级会盖住 `vercel.json` 里把 `/` 重写到 `home.html` 的规则,导致首页误显示成「当天刊」。`www` 与 apex 域名在 Vercel 上行为一致。

## 定时任务

- Hermes Cron 每天北京时间 11:30 触发
- 内容:采集 AI Agent 领域最新研究 + GitHub 热门项目 + 模型动态 + 社区热议

## 约定

- 所有命令和路径使用 `~/Hermes/ai-daily-h5/` 为根目录
- 敏感文件(如 `.env`、以 `.json` 结尾的运行时状态)一律不进 git,见 `.gitignore`
- archives/ 下是不可变历史归档,不要删除或改写
- **shizi/**：部署时由 `npm run build` 生成；仓库 `.gitignore` 排除。本地要看 `/shizi` 前先 `npm run build`。
- **daily_data 主源**：Hermes；`collect_manual.py` 勿当作与 Hermes 并行的长期第二条管道。
- **issue-data 缺失的旧期**：从 git 取回当日 `daily_data.json` 再 `generate.py`，或手工补 issue-data；不提供稳定「HTML → issue-data」反解。
- **期刊 `journal-data.json`**：由 `journal.html` 读取；写入仅通过浏览器本地写盘 + 人工 git 提交（见 `JOURNAL.md`）。**不要**添加服务端写该文件的 API，以免匿名投稿与 SSRF 面扩大。单文件会随部署全量下发，体积见 `JOURNAL.md` 中的容量说明。

