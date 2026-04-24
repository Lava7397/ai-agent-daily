# AI Daily - 任务跟踪

## 聚焦范围

**自动化内容生产** + **静态网站建设**。不再做邮件 / 微信推送。

## 当前状态

- H5 页面生成 (generate.py)
- 每日封面图生成 (generate_image.py)
- Vercel 部署 (deploy.py)
- 定时任务 (Hermes cron,每天北京时间 11:30)
- 数据源质量评估与自我迭代 (scripts/source_*.py)

## 待办

- 优化新闻采集的数据源质量
- 解决 generate.py 里 "if exists: skip" 的非幂等问题
- H5 页面 UI 进一步优化
- 给主流程加失败告警(至少写日志,能被人看到)
- 把 `requirements.txt` 和 `.python-version` 补上,环境显式化

## 已完成

- 2026-04-24 缩小项目范围:去掉邮件和微信推送,聚焦自动化 + 网站
- 2026-04-24 敏感文件从 git 移除,`.gitignore` 补齐密钥防护
- 2026-04-09 推送时间改为 11:30
- 2026-04-09 项目从 ~/.hermes/ 迁移到 ~/Hermes/
- 2026-04-08 建立完整系统
