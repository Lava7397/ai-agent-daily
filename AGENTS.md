# AI Daily - Agent 行动指南

## 项目概述

每日 AI Agent 新闻聚合站。由定时任务自动采集 → 生成静态 H5 页面 → 部署到 Vercel。
聚焦两件事:**自动化内容生产** + **静态网站建设**。

## 项目结构

```
ai-daily-h5/
├── generate.py              # 主脚本:读取 daily_data.json → 生成 H5
├── generate_image.py        # 生成每日封面图
├── deploy.py                # Vercel 部署脚本
├── screenshot.py            # 页面截图工具
├── today.html               # 当天刊(不是 index.html,避免与 `/` 冲突,见 vercel 说明)
├── home.html                # 首页(历史归档列表)
├── daily_data.json          # 当日采集的新闻数据
├── sources_registry.json    # 数据源注册表(带质量评分)
├── archives/                # 历史归档 (YYYY-MM-DD.html)
├── images/                  # 每日封面图 (YYYY-MM-DD.png)
├── scripts/
│   ├── source_explorer.py    # 发现新数据源
│   ├── source_evaluator.py   # 评估数据源质量
│   └── source_evolution.py   # 数据源自我迭代编排
├── vercel.json              # Vercel 部署配置
└── CNAME                    # 自定义域名
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
- 站点地址:<https://lava7397.com>(自定义域名,配置在 Vercel dashboard)
- Vercel 默认域名:<https://ai-agent-daily-phi.vercel.app>(备用访问)
- 站点地址在代码里是单一常量:`generate.py` 的 `SITE_URL`(可用同名环境变量覆盖)
- **路由说明**:当日刊页面文件名为 `today.html`(不是 `index.html`)。静态托管普遍会把 URL `/` 映射到根目录的 `index.html`,其优先级会盖住 `vercel.json` 里把 `/` 重写到 `home.html` 的规则,导致首页误显示成「当天刊」。`www` 与 apex 域名在 Vercel 上行为一致。

## 定时任务

- Hermes Cron 每天北京时间 11:30 触发
- 内容:采集 AI Agent 领域最新研究 + GitHub 热门项目 + 模型动态 + 社区热议

## 约定

- 所有命令和路径使用 `~/Hermes/ai-daily-h5/` 为根目录
- 敏感文件(如 `.env`、以 `.json` 结尾的运行时状态)一律不进 git,见 `.gitignore`
- archives/ 下是不可变历史归档,不要删除或改写
