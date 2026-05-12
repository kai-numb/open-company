"""open-company の当日進捗を集約する。

ソース：
- 各 submodule (biz/*/code/) の git log 直近 24 時間分
- biz/*/notes/YYYY-MM-DD-*.md
- .company/ceo/notes/YYYY-MM-DD-*.md（フィルタ後に採用）
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


@dataclass
class ProgressItem:
    source: str          # "git:drone-vibe-game" / "notes:socialist-sns" / "ceo-notes"
    timestamp: datetime
    title: str
    body: str
    path: str | None = None


# ファイル命名規則：YYYY-MM-DD-topic.md
_DATED_NOTE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-.+\.md$")


def _safe_run(args: list[str], cwd: Path) -> str:
    try:
        proc = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    if proc.returncode != 0:
        return ""
    return proc.stdout


def _list_submodules(repo_root: Path) -> list[Path]:
    """biz/<name>/code/ を submodule として扱う。.gitmodules を厳密に読まず glob で十分。"""
    biz_dir = repo_root / "biz"
    if not biz_dir.is_dir():
        return []
    out: list[Path] = []
    for biz_path in sorted(biz_dir.iterdir()):
        code_dir = biz_path / "code"
        if code_dir.is_dir() and (code_dir / ".git").exists():
            out.append(code_dir)
    return out


def _git_log_since(submodule_path: Path, since: datetime) -> list[ProgressItem]:
    biz_name = submodule_path.parent.name
    since_iso = since.astimezone(timezone.utc).isoformat()
    fmt = "%H%x1f%aI%x1f%s%x1f%b%x1e"
    raw = _safe_run(
        ["git", "log", f"--since={since_iso}", f"--pretty=format:{fmt}"],
        cwd=submodule_path,
    )
    if not raw.strip():
        return []
    items: list[ProgressItem] = []
    for record in raw.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split("\x1f")
        if len(parts) < 3:
            continue
        sha, iso, subject = parts[0], parts[1], parts[2]
        body = parts[3] if len(parts) > 3 else ""
        try:
            ts = datetime.fromisoformat(iso)
        except ValueError:
            continue
        items.append(
            ProgressItem(
                source=f"git:{biz_name}",
                timestamp=ts,
                title=subject.strip(),
                body=body.strip(),
                path=None,
            )
        )
    return items


def _scan_dated_notes(notes_dir: Path, source_label: str, target: date) -> list[ProgressItem]:
    if not notes_dir.is_dir():
        return []
    items: list[ProgressItem] = []
    for entry in sorted(notes_dir.iterdir()):
        if not entry.is_file():
            continue
        m = _DATED_NOTE_RE.match(entry.name)
        if not m:
            continue
        try:
            d = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if d != target:
            continue
        try:
            text = entry.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        title = entry.name[:-3]  # strip .md
        ts = datetime(d.year, d.month, d.day, 12, 0, tzinfo=timezone.utc)
        items.append(
            ProgressItem(
                source=source_label,
                timestamp=ts,
                title=title,
                body=text,
                path=str(entry),
            )
        )
    return items


def collect_since(since: datetime, repo_root: Path, target_date: date | None = None) -> list[ProgressItem]:
    """since 以降の git log と target_date の notes を集める。

    target_date 省略時は since の日付を使う。
    """
    if target_date is None:
        target_date = since.astimezone(timezone.utc).date()

    items: list[ProgressItem] = []

    # git log from each submodule
    for sub in _list_submodules(repo_root):
        items.extend(_git_log_since(sub, since))

    # biz/<name>/notes/
    biz_dir = repo_root / "biz"
    if biz_dir.is_dir():
        for biz_path in sorted(biz_dir.iterdir()):
            notes = biz_path / "notes"
            items.extend(
                _scan_dated_notes(notes, f"notes:{biz_path.name}", target_date)
            )

    # .company/ceo/notes/ — フィルタを厳しく通すゾーン（path は ceo/notes/ を含むので段 3 で再評価）
    ceo_notes = repo_root / ".company" / "ceo" / "notes"
    items.extend(_scan_dated_notes(ceo_notes, "ceo-notes", target_date))

    # 並び順：時刻昇順
    items.sort(key=lambda x: x.timestamp)
    return items


__all__ = ["ProgressItem", "collect_since"]
