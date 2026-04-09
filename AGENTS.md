# AI Daily - Agent 行动指南

## 项目概述

每日 AI Agent 新闻摘要系统。自动采集、生成 H5 页面、部署到 Vercel、邮件推送。

## 项目结构

```
ai-daily-h5/
├── generate.py          # 主脚本：采集新闻 → 生成 H5 页面
├── generate_image.py    # 生成每日动漫风格封面图
├── deploy.py            # Vercel 部署脚本
├── index.html           # 生成的 H5 页面
├── daily_data.json      # 当日采集的新闻数据
├── archives/            # 历史归档 (YYYY-MM-DD.html)
├── images/              # 每日封面图 (YYYY-MM-DD.png)
├── scripts/
│   ├── send_daily_email.py    # 邮件发送
│   └── ai-daily-email.json    # 邮件配置
└── vercel.json          # Vercel 部署配置
```

## 技术栈

- Python 3.11
- Vercel (静态托管)
- SMTP (163邮箱推送)

## Vercel 配置

- 项目名: ai-agent-daily
- Project ID: prj_9SDG4DvUaz3vM4vAnYVIqRKH4qBl
- Team ID: team_E50GFnf2zER9xjKfwsvxAGbO
- 部署: `cd ~/Hermes/ai-daily-h5 && vercel --prod --yes`
- SSO 必须关闭才能公开访问

## 定时任务

- Cron Job ID: 05d76b94779e
- 每天北京时间 11:30 执行
- 内容：采集 AI Agent 领域最新研究 + GitHub 热门项目

## 邮件配置

- 发件: [cflava@163.com](mailto:cflava@163.com) (SMTP)
- 配置文件: scripts/ai-daily-email.json

## 约定

- 所有命令和路径使用 ~/Hermes/ai-daily-h5/ 为根目录
- 修改代码后需要重新部署到 Vercel
- 邮件密码在 ai-daily-email.json 中，不要提交到 git

