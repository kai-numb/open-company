"""build-in-public 日次パイプラインのエントリポイント。

使い方:
  python -m buildinpublic.run                     # 当日 (UTC) を本番投稿
  python -m buildinpublic.run --dry-run           # 投稿せずログのみ
  python -m buildinpublic.run --date 2026-05-11   # 指定日

環境変数 DRY_RUN=true でも dry-run になる (GitHub Actions vars 経由)。
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .collect import collect_since
from .filter import filter_items
from .log import append_log
from .summarize import generate_thread
from .x_post import PostedThread, post_thread

REPO_ROOT = Path(__file__).resolve().parent.parent


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="buildinpublic")
    p.add_argument("--date", help="YYYY-MM-DD (default: today UTC)")
    p.add_argument("--dry-run", action="store_true", help="投稿しない")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        help="git log を遡る時間幅 (default: 24h)",
    )
    return p.parse_args(argv)


def _is_truthy_env(name: str) -> bool:
    return os.environ.get(name, "").lower() in {"1", "true", "yes"}


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    dry_run = args.dry_run or _is_truthy_env("DRY_RUN")

    if args.date:
        target_date = date.fromisoformat(args.date)
    else:
        target_date = datetime.now(tz=timezone.utc).date()

    since = datetime(
        target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc
    ) - timedelta(hours=max(0, args.hours - 24))

    print(f"[buildinpublic] target_date={target_date} since={since.isoformat()} dry_run={dry_run}")

    items = collect_since(since=since, repo_root=REPO_ROOT, target_date=target_date)
    print(f"[buildinpublic] collected {len(items)} item(s)")

    filtered = filter_items(items)
    print(f"[buildinpublic] passed={filtered.passed_count} rejected={filtered.rejected_count}")
    for item, reason in filtered.rejected:
        print(f"  rejected [{item.source}] {item.title[:60]} -- {reason}")

    if filtered.passed_count == 0:
        print("[buildinpublic] nothing to post (0 passed). exit success.")
        append_log(target_date, None, [], filtered, dry_run=dry_run)
        return 0

    thread = generate_thread(filtered.passed, target_date=target_date, dry_run=dry_run)
    print(f"[buildinpublic] thread length: {len(thread)}")
    for t in thread:
        text = t.get("text", "")
        print(f"  [{t.get('index')}] {text}")

    if not thread:
        print("[buildinpublic] model returned empty thread. exit success.")
        append_log(target_date, None, [], filtered, dry_run=dry_run)
        return 0

    posted: PostedThread | None
    if dry_run:
        posted = post_thread(thread, dry_run=True)
        print(f"[buildinpublic] DRY-RUN posted preview: {posted.first_url}")
    else:
        posted = post_thread(thread, dry_run=False)
        print(f"[buildinpublic] POSTED: {posted.first_url}")

    log_path = append_log(target_date, posted, thread, filtered, dry_run=dry_run)
    print(f"[buildinpublic] log: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
