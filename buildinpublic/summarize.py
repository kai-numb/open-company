"""filter 通過 items を Claude API で 3-5 ツイートのスレッドに圧縮。"""
from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from anthropic import Anthropic

from .collect import ProgressItem

MODEL = "claude-opus-4-7"
SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "system.md"
MAX_INPUT_CHARS_PER_ITEM = 2000


def _load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")


def _format_items(items: list[ProgressItem]) -> str:
    lines: list[str] = []
    for i, item in enumerate(items, start=1):
        body = item.body
        if len(body) > MAX_INPUT_CHARS_PER_ITEM:
            body = body[:MAX_INPUT_CHARS_PER_ITEM] + "\n…(truncated)"
        lines.append(
            f"### Item {i} [{item.source}] {item.timestamp.isoformat()}\n"
            f"Title: {item.title}\n"
            f"Body:\n{body}\n"
        )
    return "\n".join(lines)


def _extract_json_array(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        # ```json ... ``` を剥がす
        text = text.split("```", 2)[1] if "```" in text else text
        if text.startswith("json"):
            text = text[len("json"):].lstrip()
        text = text.rsplit("```", 1)[0] if "```" in text else text
    text = text.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"no JSON array found in model output: {text[:200]}")
    return json.loads(text[start : end + 1])


def generate_thread(
    items: list[ProgressItem],
    *,
    target_date: date,
    dry_run: bool = False,
) -> list[dict]:
    """ProgressItem のリストを 3-5 ツイートのスレッドに圧縮して返す。

    返却値：[{"index": 1, "text": "..."}, ...]。
    items が空なら [] を返す（投稿しないシグナル）。
    """
    if not items:
        return []

    system_prompt = _load_system_prompt()
    user_msg = (
        f"## 当日の日付\n{target_date.isoformat()}\n\n"
        f"## 進捗ログ ({len(items)} 件)\n\n"
        f"{_format_items(items)}\n\n"
        "上記を build-in-public スレッドに圧縮してください。JSON 配列のみ出力。"
    )

    if dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
        # ローカル dry-run でキーが無いとき：実 API を叩かずプレビューを返す
        return [
            {"index": 1, "text": f"[dry-run preview] {target_date} - {len(items)} item(s) collected"},
            {"index": 2, "text": "[dry-run preview] (ANTHROPIC_API_KEY 未設定のため要約スキップ)"},
            {"index": 3, "text": "[dry-run preview] 本番では Claude API でスレッド生成"},
        ]

    client = Anthropic(max_retries=5)   # 529 Overloaded / 429 等のリトライを多めに
    resp = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = "".join(
        block.text for block in resp.content if getattr(block, "type", None) == "text"
    )
    thread = _extract_json_array(text)

    # 簡易バリデーション：各要素は {"index": int, "text": str}
    cleaned: list[dict] = []
    for i, t in enumerate(thread, start=1):
        if not isinstance(t, dict):
            continue
        idx = t.get("index", i)
        body = t.get("text", "").strip()
        if not body:
            continue
        cleaned.append({"index": int(idx), "text": body})

    return cleaned


__all__ = ["generate_thread", "MODEL"]
