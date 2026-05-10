# cc-company — オーナーの仮想組織（本社）

連続起業家として複数事業を並走運営するための、Claude Code ベースの **仮想組織本社**。
取締役会（オーナー本人）から CEO（AI、Claude）へ唯一の窓口で命令、CEO は連続自走で事業を立ち上げ・目標設定・目標達成する。

## 命令系統

```
取締役会（オーナー本人、最終意思決定者）
   ↓ ビジョン・方針・案件
CEO（AI、唯一の窓口、連続起業家として振る舞う）
   ↓ タスク委任 / 事業管理
部下（必要時のみ新設）/ 各事業（biz/<事業名>/code/ に submodule で内包）
```

- **取締役会** = オーナー本人。北極星 KPI（売上 1000 万円 / 12 ヶ月）を設定
- **CEO** = AI、唯一の対話相手。**連続起業家**（ロールモデル：小澤隆生氏）として **5 ミッション** を担う：
  1. **新事業の立ち上げ**（壁打ち、コンセプト、競合、命名、MVP スコープ）
  2. **目標設定**（North Star / KPI 階層 / マイルストーン / スコープ）
  3. **現在地の把握**（事業のメトリクス / 反応データ / 進捗の可視化）
  4. **段取り**（目標から現在地への道筋、Agent / Skill / 部下の最適配分）
  5. **目標達成**（実装の進行管理、ボトルネック解消、取締役会工数最小化）
- **部下** = 同領域タスクが 1 週間 3 回以上 / 複数事業反復 / 取締役会の明示指示で新設（高い閾値）
- **事業** = `biz/<事業名>/` 配下に **管理層 + 実コード（submodule）** を同居、各事業は独立リポ

## 構成

```
cc-company/
├── CLAUDE.md                    ← Claude Code 起動時に読む本社ルール（CEO モード起動）
├── README.md                    ← 本ファイル
├── .company/                    ← CEO 横断ワークスペース（git 管理外）
│   ├── CLAUDE.md                本社固有ルール
│   └── ceo/
│       ├── ceo-core.md          CEO の振る舞い（横断・再利用可能）
│       ├── CLAUDE.md            CEO ワークスペース定義
│       ├── inbox/  todos/  notes/   横断ノート
│       └── notes/
│           ├── mistakes.md      過去のミス Case（再発防止チェックリスト）
│           ├── agent-playbook/  Plan/Explore/general-purpose の呼出ノウハウ
│           ├── templates/       横断テンプレ（scripts / agents 定義）
│           └── archive/         古いログのアーカイブ
├── biz/                         ← 各事業（管理層 + 実コード同居）
│   ├── drone-vibe-game/         Promptdrone 配達ゲーム
│   │   ├── CLAUDE.md             ← 事業固有ルール（git 管理対象）
│   │   ├── notes/  todos/  inbox/    ← 管理ノート（.gitignore 対象、機密保持）
│   │   └── code/                 ← submodule → kai-numb/drone-vibe-game.git
│   └── socialist-sns/           となりの席の労働ニュース
│       ├── CLAUDE.md
│       ├── notes/  todos/  inbox/
│       └── code/                ← submodule → kai-numb/tonari-news-bot.git
├── skel/                        新規事業立ち上げ用スケルトン
│   ├── new-business-template/   CLAUDE.md + .claude/ + scripts/ + .env.example + .gitignore
│   └── new-business-checklist.md
└── .claude/                     ralph-loop 等のローカル設定（git 管理外）
```

## 運用の核

### 1. CEO の連続自走（24 時間運用）

- 取締役会・CEO ともに **作業時間制約なし**
- CEO は **「次は？」を待たず連続自走**、止まらず先送りせず判断スピード重視
- 取締役会への質問は **複数選択肢 + CEO 推奨 + 判断材料同梱**（その場で判断できる形）

### 2. 連続起業家の 8 原則（ロールモデル：小澤隆生氏）

1. 「凡人」のスタンス：天才（取締役会）のビジョンを実装する官僚側として徹底する
2. 凡事徹底：当たり前を徹底
3. 再現性 3 ステップ：ゴール設定 → 仮説検証 → 徹底実行
4. 決めて前に進める：判断保留が最大のリスク
5. 変化を恐れない：振れ幅が大きいほど成長
6. ワンフレーズで意識を変える：シンプルで「ワクワクする希望」
7. 経験 = 過去のミス + 知見の蓄積（mistakes.md / agent-playbook / skel）
8. 顧客の根源的欲求を見抜く

### 3. 戦略順序（事業に共通）

```
実装 → 公開 → 反応観察 → 資本判断
```

完璧な準備より、まず動かして反応を見る（Lean Startup）。
マネタイズ判断は反応データを見てから。

### 4. 横断ルール

- **env-example シークレット混入防止**：scripts/check-secrets.sh + .gitignore 最低ライン
- **メモリ階層**：`~/.claude/projects/<id>/memory/` に feedback / user / project / reference タイプで蓄積
- **質問の作法**：複数選択肢を提示、CEO 推奨明示、判断材料を同梱

## 進行中の事業

| 事業 | 状態 |
|---|---|
| **drone-vibe-game**（プロダクト名 **Promptdrone**） | MVP 実装中。v3 配達タイムアタック（3 軒に荷物を届ける）+ Rapier 物理 + Kenney CC0 アセット。F3 公開準備完了 |
| **socialist-sns** | 5/11 ローンチ日。@tonari_news_jp、Automated 自動投稿（automation_kit）、scheduled_at に従って投稿開始 |

詳細は `biz/<事業名>/CLAUDE.md` を参照。

## ライセンス

個人開発・非公開（取締役会オーナー所有）。
