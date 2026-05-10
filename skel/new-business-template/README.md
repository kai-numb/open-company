# [事業名]

[1〜2 行で事業の概要を書く]

open-company（取締役会の仮想組織）配下の事業。命令系統・ルールは `../open-company/.company/CLAUDE.md` を参照。

---

## クイックスタート

```bash
# 1. 依存をインストール
[npm install / pnpm install / pip install -r requirements.txt]

# 2. 環境変数を設定
cp .env.example .env
# .env を開いて本物のキーを設定

# 3. pre-commit hook を有効化（open-company 横断ルール）
bash scripts/install-hooks.sh
# 動作確認：
bash scripts/check-secrets.sh --all

# 4. 起動
[npm run dev / pnpm dev / python main.py / 他]
```

---

## ディレクトリ

```
[事業名]/
├── CLAUDE.md              ← Claude Code 起動時に自動読込（CEO ロール）
├── .claude/               ← プロジェクト固有設定
│   ├── settings.json      ← 追加権限・拒否
│   ├── rules/             ← 必要なら配置
│   ├── skills/            ← このプロジェクト専用 skill
│   └── agents/            ← このプロジェクト専用 agent
├── .gitignore             ← open-company 最低ライン
├── .env.example           ← プレースホルダのみ
├── scripts/
│   ├── check-secrets.sh   ← pre-commit シークレット検出
│   └── install-hooks.sh   ← hook 配置スクリプト
├── src/                   ← ソースコード
└── README.md
```

---

## 関連ドキュメント

- 本社：`../open-company/.company/CLAUDE.md`
- 事業管理層：`../open-company/.company/biz/[事業名]/`
- CEO の振る舞い：`../open-company/.company/ceo/CLAUDE.md`
- 過去のミスと対策：`../open-company/.company/ceo/notes/mistakes.md`
- 横断ルール（env-example）：`../open-company/.company/ceo/notes/2026-05-10-env-example-rule-proposal.md`

---

## ライセンス

[個人開発・非公開 / その他]
