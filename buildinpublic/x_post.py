"""X (旧 Twitter) API 投稿。

biz/socialist-sns/code/src/post.py の中核を最小コピー。
- _BIP サフィックス付きの環境変数を使用 (socialist-sns 用と物理分離)
- 画像アップロード・メトリクス取得は build-in-public 用途では当面不要なため除外
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import tweepy


@dataclass
class PostedThread:
    first_tweet_id: str
    first_url: str
    all_tweet_ids: list[str]


def _client() -> tweepy.Client:
    return tweepy.Client(
        consumer_key=os.environ["X_API_KEY_BIP"],
        consumer_secret=os.environ["X_API_SECRET_BIP"],
        access_token=os.environ["X_ACCESS_TOKEN_BIP"],
        access_token_secret=os.environ["X_ACCESS_SECRET_BIP"],
    )


def post_thread(thread: list[dict], *, dry_run: bool = False) -> PostedThread:
    """thread = [{"index":1,"text":"..."}, ...] を順に投稿する。

    in_reply_to_tweet_id でスレッド連結。失敗時は例外を上位へ。
    """
    handle = os.environ.get("X_HANDLE_BIP", "open_company_dev")
    if not thread:
        raise ValueError("empty thread")

    if dry_run:
        ids = [f"dryrun-{i}" for i in range(len(thread))]
        return PostedThread(
            first_tweet_id=ids[0],
            first_url=f"https://x.com/{handle}/status/{ids[0]}",
            all_tweet_ids=ids,
        )

    client = _client()
    parent_id: str | None = None
    ids: list[str] = []
    for post in thread:
        kwargs: dict = {"text": post["text"]}
        if parent_id:
            kwargs["in_reply_to_tweet_id"] = parent_id
        resp = client.create_tweet(**kwargs)
        tid = str(resp.data["id"])
        ids.append(tid)
        parent_id = tid

    return PostedThread(
        first_tweet_id=ids[0],
        first_url=f"https://x.com/{handle}/status/{ids[0]}",
        all_tweet_ids=ids,
    )


__all__ = ["PostedThread", "post_thread"]
