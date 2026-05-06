# Journal（Lava 期刊正文）说明

`journal-data.json` 是 Lava 个人期刊正文的静态数据文件，由 `journal.html` 直接读取展示。

## 写入路径（仅手工）

本仓库**不存在服务端写接口** — `api/journal_url_preview.py` 只做远端 URL 元信息抓取。
新增条目走的是浏览器本地写盘 + 人工提交：

1. 打开 `https://lava7397.com/journal-submit.html`（线上）或本地 `journal-submit.html`。
2. 首次点「绑定」选中本机仓库下的 `journal-data.json`（File System Access API 句柄保存在浏览器）。
3. 填好链接 / 标题 / 正文，点「一键投稿写入」。
4. 终端切到本仓库目录：
   ```bash
   cd ~/Hermes/ai-daily-h5
   git add journal-data.json
   git commit -m "journal: <一句话>"
   git push origin main
   ```
5. Vercel 拉新 commit 自动重新部署。

## Schema 约定

```jsonc
{
  "schema_version": 1,
  "_meta": {                          // 仓库内附带的注解，写回时保留
    "purpose": "...",
    "writers": "manual only — no server API writes this file",
    "soft_cap_entries": 200,
    "doc": "JOURNAL.md"
  },
  "updated_at": "ISO 8601 UTC",
  "entries": [
    {
      "id": "uuid",
      "createdAt": "ISO 8601 UTC",
      "url": "https://...",          // 可空
      "title": "...",                // 可空
      "text": "..."                  // 可空，但三者至少有一项非空
    }
  ]
}
```

注意：

- `journal-submit.html` 在本机覆盖 `journal-data.json` 时会重建对象，**只有 `_meta` 被显式保留**（见 `mergeFromData`）。如果未来加新顶层字段，记得在那里也补一份 `data.<key> ? mergedPayload.<key> = data.<key>`，否则会被静默丢掉。
- `journal.html` 渲染时只读 `entries` 数组；其它字段不影响展示。

## 容量约束

`_meta.soft_cap_entries: 200` 是建议上限：

- 本文件每次部署都会被 Vercel 全量发到 CDN，单文件 > 1 MB 后会拖慢首屏。
- 当前增长完全由 Lava 手工触发，没有匿名提交风险，因此**不做硬限制**，超过 200 条时考虑：
  - 把过期条目挪到 `journal/archive-YYYY.json`，懒加载；
  - 或正式迁移到外部存储（Vercel KV / Edge Config / 自建小后端）。

## 不要做的事

- 不要在 `api/` 下加直接写 `journal-data.json` 的接口。一旦有匿名写盘路径，垃圾投稿和 SSRF 攻击面会立刻打开。
- 不要把 `_meta` 当成 entry 的字段；它是顶层注解。
