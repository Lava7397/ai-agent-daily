#!/usr/bin/env python3
"""
已废弃：日刊 HTML 的唯一模板来源是仓库根目录的 generate.build_html()。

历史原因本脚本曾用「粘 CSS 片段」对齐旧归档；维护双路径容易漂移，已弃用。

请使用：
  - 日常：python3 generate.py（由 Hermes / GitHub Action 触发）
  - 某日已有 issue-data/*.json，仅需重渲归档页：
      python3 scripts/rerender_issue_from_data.py YYYY-MM-DD
    覆盖非「列表最新一期」的历史归档须加 --force。

旧版 800+ 行实现仍可通过 git 历史找回。
"""
from __future__ import annotations

import sys


def main() -> int:
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
