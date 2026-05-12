"""3 段機密フィルタ：パス -> API キー -> キーワード/KPI。

build in public の方針上、実装トピック・OSS進捗・設計議論・失敗・学びは通すが、
売上数字・北極星 KPI 進捗・各事業収益・未公開戦略・個人情報は除外する。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .collect import ProgressItem


# ---------- 段 1：パスホワイトリスト / ブラックリスト ----------

PATH_BLOCKLIST_SUBSTR: tuple[str, ...] = (
    "/assets/",
    ".company/obsidian/",
    ".company/ceo/notes/decisions/",
    "ceo/notes/mistakes.md",
    "ceo/notes/templates/",
    "ceo/notes/agent-playbook/",
    "ceo/inbox/",
    "ceo/todos/",
    "biz/socialist-sns/assets/",
)


def _path_blocked(path: str | None) -> str | None:
    if path is None:
        return None
    p = path.replace("\\", "/")
    for blocked in PATH_BLOCKLIST_SUBSTR:
        if blocked in p:
            return f"path blocklist: {blocked}"
    return None


# ---------- 段 2：API キー検出（check-secrets.sh から移植） ----------

_SECRET_PATTERNS: tuple[str, ...] = (
    r"sk-ant-(api03|sid01)-[A-Za-z0-9_-]{40,}",                       # Anthropic
    r"sk-(proj|svcacct)?-?[A-Za-z0-9_-]{20,}",                        # OpenAI
    r"AKIA[0-9A-Z]{16}",                                              # AWS Access Key
    r"AIza[0-9A-Za-z_-]{35}",                                         # Google API
    r"gh[pousr]_[A-Za-z0-9]{36,}",                                    # GitHub PAT
    r"github_pat_[A-Za-z0-9_]{82}",                                   # GitHub fine-grained PAT
    r"sk_(live|test)_[A-Za-z0-9]{24,}",                               # Stripe
    r"xox[abprs]-[A-Za-z0-9-]+",                                      # Slack
    r"-----BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----",     # PEM
    r"(postgres|postgresql|mysql|mongodb(\+srv)?)://[^:\s]+:[^@\s]+@",  # DB URL with password
)
SECRET_RE = re.compile("|".join(_SECRET_PATTERNS))

_PLACEHOLDER_PATTERNS: tuple[str, ...] = (
    r"\bYOUR\b",
    r"\bEXAMPLE\b",
    r"\bPLACEHOLDER\b",
    r"X{4,}",
    r"\bchange-me\b",
    r"\bdummy\b",
    r"\bredacted\b",
    r"<[A-Za-z_-]+>",
)
PLACEHOLDER_RE = re.compile("|".join(_PLACEHOLDER_PATTERNS), re.IGNORECASE)


def _secret_detected(text: str) -> str | None:
    for line in text.splitlines():
        if SECRET_RE.search(line) and not PLACEHOLDER_RE.search(line):
            return "secret-like value detected"
    return None


# ---------- 段 3：機密キーワード / KPI 数字 ----------

_BLOCK_KEYWORDS_RE: tuple[tuple[str, re.Pattern[str]], ...] = (
    # 売上数字
    ("revenue: ja yen amount",
     re.compile(r"\b\d{1,3}(,?\d{3})*\s*円")),
    ("revenue: 売上 + 数字",
     re.compile(r"売上[^\n]{0,12}?\d")),
    ("revenue: MRR/ARR",
     re.compile(r"\b(MRR|ARR)[^\n]{0,10}?\d", re.IGNORECASE)),
    ("revenue: 月商/年商",
     re.compile(r"(月商|年商)[^\n]{0,12}?\d")),

    # 北極星 KPI 進捗
    ("north star",
     re.compile(r"北極星|north\s*star", re.IGNORECASE)),
    ("north star: 1000 万円",
     re.compile(r"1[,\s]?000\s*万円?")),
    ("kpi 達成率",
     re.compile(r"(達成率|進捗率|達成度)[^\n]{0,10}?\d+\s*%")),

    # 個人情報
    ("personal: 取締役会",
     re.compile(r"取締役会")),
    ("personal: オーナー",
     re.compile(r"オーナー(?!シップ)")),
    ("personal: email",
     re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),

    # 未公開戦略
    ("unreleased: 戦略書",
     re.compile(r"戦略書")),
    ("unreleased: assets path",
     re.compile(r"\bassets/")),
    ("unreleased: 未公開/機密/confidential",
     re.compile(r"未公開|機密|confidential", re.IGNORECASE)),

    # 取締役会名指しの反省
    ("reflection: mistakes.md ref",
     re.compile(r"mistakes\.md")),
)


def _keyword_blocked(text: str) -> str | None:
    for label, pattern in _BLOCK_KEYWORDS_RE:
        if pattern.search(text):
            return f"keyword: {label}"
    return None


# ---------- パブリック API ----------

def is_blocked(text: str, path: str | None) -> str | None:
    """ブロック理由を返す。OK なら None。

    順序：段 1 (path) → 段 2 (secret) → 段 3 (keyword)。
    """
    reason = _path_blocked(path)
    if reason:
        return reason
    reason = _secret_detected(text)
    if reason:
        return reason
    reason = _keyword_blocked(text)
    if reason:
        return reason
    return None


@dataclass
class FilterResult:
    passed: list["ProgressItem"] = field(default_factory=list)
    rejected: list[tuple["ProgressItem", str]] = field(default_factory=list)

    @property
    def passed_count(self) -> int:
        return len(self.passed)

    @property
    def rejected_count(self) -> int:
        return len(self.rejected)


def filter_items(items: list["ProgressItem"]) -> FilterResult:
    result = FilterResult()
    for item in items:
        text = f"{item.title}\n{item.body}"
        reason = is_blocked(text, item.path)
        if reason:
            result.rejected.append((item, reason))
        else:
            result.passed.append(item)
    return result


__all__ = [
    "FilterResult",
    "filter_items",
    "is_blocked",
    "SECRET_RE",
    "PLACEHOLDER_RE",
    "PATH_BLOCKLIST_SUBSTR",
]
