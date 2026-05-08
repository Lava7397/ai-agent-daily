#!/usr/bin/env python3
"""
AI Agent 日报 H5 页面生成器
读取 daily_data.json → 生成 today.html(当天刊) + 归档页面（版面见 aidaily/render.py）

生成结束后会自动压缩「北京时间当天」之前的历史 archives/*.html（空白 minify，
见 scripts/compress_archives.py）；可用 --no-compress-archives 关闭。

日志：设置环境变量 AI_DAILY_LOG_LEVEL=INFO|WARNING|DEBUG 时，失败路径会写入 stderr（含堆栈）。
"""
import argparse
import importlib.util
import sys

from aidaily.logutil import configure_cli_logging

LOG = configure_cli_logging("aidaily.generate")

from aidaily.archives import (
    apply_home_archive_override,
    extract_archive_meta,
    patch_polished_home_archives_data,
    sync_today_html_from_newest_archive,
)
from aidaily.config import (
    BASE_DIR,
    DATA_FILE,
    ISSUES_FILENAME,
    OUTPUT_DIR,
    TODAY_FILENAME,
)
from aidaily.constants import DEFAULT_MAX_SITE_ITEMS, SECTION_KEYS
from aidaily.data import (
    cap_data_for_site,
    current_beijing_date_str,
    get_issue_date,
    load_data,
    resolve_max_site_items,
    write_issue_data_json,
)
from aidaily.status import write_site_status

from aidaily.render import build_html, build_issues_html

def run_source_evolution():
    print("\n🧬 Running source evolution...")
    try:
        import subprocess
        evo_result = subprocess.run(
            ["python3", str(BASE_DIR / "scripts" / "source_evolution.py")],
            capture_output=True, text=True, timeout=60
        )
        if evo_result.returncode == 0:
            print(evo_result.stdout[-1500:] if len(evo_result.stdout) > 1500 else evo_result.stdout)
        else:
            print(f"⚠️  Evolution script returned {evo_result.returncode}")
    except Exception as e:
        print(f"⚠️  Evolution skipped: {e}")

def run_compress_historic_archives() -> int:
    """将「北京时间当天」之前的历史 archives/*.html 做 HTML 空白压缩（见 scripts/compress_archives.py）。"""
    path = BASE_DIR / "scripts" / "compress_archives.py"
    if not path.is_file():
        print(f"⚠️  compress_archives: missing {path}")
        return 0
    spec = importlib.util.spec_from_file_location("compress_archives", path)
    if spec is None or spec.loader is None:
        print("⚠️  compress_archives: could not load module spec")
        return 0
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    n = mod.compress_historic_archives(BASE_DIR, current_beijing_date_str(), dry_run=False)
    if n:
        print(
            f"\n📦 Historical archives: minified {n} file(s) (BJT date < {current_beijing_date_str()})."
        )
    return n


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate the AI Daily site from daily_data.json."
    )
    parser.add_argument(
        "--run-source-evolution",
        action="store_true",
        help="also run scripts/source_evolution.py after generating site files",
    )
    parser.add_argument(
        "--no-compress-archives",
        action="store_true",
        help="do not minify historical archives/*.html (only YYYY-MM-DD < today BJT)",
    )
    parser.add_argument(
        "--max-site-items",
        type=int,
        default=None,
        metavar="N",
        help=(
            "max cards site-wide across sections "
            "(default: env AI_DAILY_MAX_SITE_ITEMS or %d)" % DEFAULT_MAX_SITE_ITEMS
        ),
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found. Please create daily_data.json first.")
        sys.exit(1)

    data = load_data()
    raw_item_total = sum(len(data.get(k, [])) for k in SECTION_KEYS)
    max_site_items = resolve_max_site_items(args.max_site_items)
    data = cap_data_for_site(data, max_items=max_site_items)
    date_str = get_issue_date(data)
    today_str = current_beijing_date_str()

    html = build_html(data)
    write_issue_data_json(data, date_str)

    # Write today.html (当天刊; 不是 index.html,见模块顶注释)
    today_path = BASE_DIR / TODAY_FILENAME
    previous_today = today_path.read_text(encoding="utf-8") if today_path.exists() else None
    today_path.write_text(html, encoding="utf-8")
    if previous_today is None:
        print(f"Generated: {today_path}")
    elif previous_today == html:
        print(f"Up-to-date: {today_path}")
    else:
        print(f"Updated: {today_path}")

    # Write archive page
    OUTPUT_DIR.mkdir(exist_ok=True)
    archive_path = OUTPUT_DIR / f"{date_str}.html"
    archive_paths_sorted = sorted(
        OUTPUT_DIR.glob("????-??-??.html"), key=lambda p: p.stem
    )
    tip_stem = archive_paths_sorted[-1].stem if archive_paths_sorted else None
    if archive_path.exists():
        previous_archive = archive_path.read_text(encoding="utf-8")
        if previous_archive == html:
            print(f"Up-to-date: {archive_path}")
        elif date_str == today_str:
            archive_path.write_text(html, encoding="utf-8")
            print(f"Updated: {archive_path} (today's issue refreshed)")
        elif tip_stem == date_str:
            # calendars 已跨过该日，但 daily_data 仍在订正「列表里最新日期」那一期：
            # 若不写盘，下文 sync 会用旧 archives/*.html 盖掉刚写好的 today.html（例如缺 research）
            archive_path.write_text(html, encoding="utf-8")
            print(f"Updated: {archive_path} (tip issue refreshed; daily_data date == newest archive)")
        else:
            print(f"Skipped: {archive_path} (historical archive preserved)")
    else:
        archive_path.write_text(html, encoding="utf-8")
        print(f"Generated: {archive_path}")

    # 用日期最新的一期覆盖 today.html，与首页列表第一条、/today 直链 三者一致
    # （Hermes 若只更新了较新的 archive、daily_data 仍滞后，否则会 4/24 vs 4/23 打架）
    sync_today_html_from_newest_archive()
    archive_paths_after = sorted(
        OUTPUT_DIR.glob("????-??-??.html"), key=lambda p: p.stem
    )
    tip_after = archive_paths_after[-1].stem if archive_paths_after else None
    if tip_after == date_str and today_path.read_text(encoding="utf-8") != html:
        today_path.write_text(html, encoding="utf-8")
        print(
            f"Refreshed {TODAY_FILENAME} from current daily_data "
            f"(sync had copied stale archive; data date {date_str} is newest)"
        )

    site_total = sum(len(data.get(k, [])) for k in SECTION_KEYS)
    if raw_item_total > max_site_items:
        print(
            f"\nTotal items (site): {site_total} (raw {raw_item_total}, display cap {max_site_items}, fair split by section)"
        )
    else:
        print(f"\nTotal items: {site_total}")
    print("Done!")

    # ── issues.html（期刊归档列表）与 home.html（仅同步 ALL_ARCHIVES 供 atlas 统计）──
    print("\n🏠 Generating home page...")
    try:
        # 扫描所有归档日期（YYYY-MM-DD.html）并提取头条信息（全量写入 issues.html）
        archive_files = sorted(
            OUTPUT_DIR.glob("????-??-??.html"),
            key=lambda p: p.stem,
            reverse=True   # 最新日期排前面
        )
        archive_infos = []
        for p in archive_files:
            headline, total, summary = extract_archive_meta(p)
            archive_infos.append((p.stem, headline, total, summary))

        archive_infos = apply_home_archive_override(archive_infos, data)

        if archive_infos:
            home_path = BASE_DIR / "home.html"
            # 生成完整新页面（用于提取新存档列表）
            new_issues_html = build_issues_html(archive_infos)
            issues_path = BASE_DIR / ISSUES_FILENAME
            issues_path.write_text(new_issues_html, encoding="utf-8")
            print(f"Generated: {issues_path} ({len(archive_infos)} issues)")

            existing_home_html = (
                home_path.read_text(encoding="utf-8") if home_path.exists() else ""
            )
            is_polished = home_path.exists() and (
                "项目地图" in existing_home_html
                or "atlas-nav-sticky" in existing_home_html
            )
            if (
                is_polished
                or (
                    "const ALL_ARCHIVES = " in existing_home_html
                    and "const LANG_STORAGE =" in existing_home_html
                )
            ):
                home_path.write_text(
                    patch_polished_home_archives_data(
                        existing_home_html,
                        archive_infos,
                    ),
                    encoding="utf-8",
                )
            else:
                print(
                    "⚠️  home.html has no ALL_ARCHIVES markers; skipping home data patch"
                )
            # 打印头条预览
            for d_row, headline, total, _summary in archive_infos[:3]:
                print(f"  {d_row}: {headline[:50]}...")
        else:
            print("⚠️  No archives found, skipping home.html")
    except Exception as e:
        print(f"⚠️  Home page generation failed: {e}")

    try:
        write_site_status(
            data,
            date_str=date_str,
            raw_item_total=raw_item_total,
            site_total=site_total,
            max_site_items=max_site_items,
        )
    except Exception as e:
        print(f"⚠️  status.json: {e}")

    if not args.no_compress_archives:
        try:
            run_compress_historic_archives()
        except Exception as e:
            print(f"⚠️  compress_archives failed: {e}")

    if args.run_source_evolution:
        run_source_evolution()
    else:
        print("\nℹ️  Skipping source evolution (pass --run-source-evolution to enable)")


if __name__ == "__main__":
    main()
