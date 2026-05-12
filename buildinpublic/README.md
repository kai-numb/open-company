# buildinpublic — open-company の日次進捗を X に自動投稿

socialist-sns (@tonari_news_jp) とは別の新規 X アカウントから、毎日 22:00 JST に当日サマリ 1 スレッド (3-5 ツイート) を build-in-public スタイルで自動投稿するパイプライン。

## アーキテクチャ
`collect` → `filter` (3 段機密フィルタ) → `summarize` (Claude API) → `x_post` (tweepy) → `log` (JSONL)。socialist-sns submodule のコードは一切触らない。

## セットアップ (取締役会タスク)
1. 新規 X アカウント作成 (例: `@open_company_dev`)
2. X Developer Portal で OAuth1.0a トークン 4 種取得
3. GitHub Secrets 登録 (open-company リポジトリに):
   - `X_API_KEY_BIP` / `X_API_SECRET_BIP` / `X_ACCESS_TOKEN_BIP` / `X_ACCESS_SECRET_BIP`
   - `ANTHROPIC_API_KEY` (既存があれば再利用可)
4. GitHub Variables 登録:
   - `X_HANDLE_BIP` (新アカウントのハンドル名)
   - `DRY_RUN` (初日は `true`、Day 2 から `false`)

## ローカル実行
```bash
python3 -m venv buildinpublic/.venv
buildinpublic/.venv/bin/pip install -r buildinpublic/requirements.txt
PYTHONPATH=. buildinpublic/.venv/bin/python -m buildinpublic.run --dry-run
```

## テスト
```bash
PYTHONPATH=. buildinpublic/.venv/bin/python -m pytest buildinpublic/tests/ -v
```

## 機密フィルタ仕様
- 段 1: パス — `assets/`, `.company/obsidian/`, `.company/ceo/notes/decisions/` 等を除外
- 段 2: API キー — check-secrets.sh の regex を再利用 (Anthropic/OpenAI/AWS/Google/GitHub/Stripe/Slack/PEM/DB URL)
- 段 3: キーワード/KPI — 売上数字, 北極星, 取締役会, オーナー, 戦略書, 未公開, mistakes.md, メールアドレス

詳細は `filter.py` 内の定数および `tests/test_filter.py` を参照。

## 運用ノート
- Day 1 のみ `DRY_RUN=true` で起動 → Actions ログ確認 → `DRY_RUN=false` に切替
- 週 1 回 `logs/YYYY-MM-DD.jsonl` を grep し、フィルタ過剰 (rejected 0 が続く) になっていないか確認
