---
created: "2026-05-10"
topic: "新規事業立ち上げ時の CEO チェックリスト"
type: checklist
status: active
purpose: |
  cc-company 配下で新規事業を立ち上げるとき、CEO が機械的に通すチェックリスト。
  /cc-new-project skill が完成するまでは手動で実施
---

# 新規事業立ち上げチェックリスト

CEO が新規事業を立ち上げるとき、このチェックリストを **上から順に通す**。

## Phase 1：取締役会との合意（5 分）

- [ ] 事業名（仮称で OK）の確認
- [ ] 事業の North Star（最終目的）を取締役会から聞き取り
- [ ] 対外公開ストーリー（公開する / しない / 段階公開）の方針確認
- [ ] 既存事業（drone-vibe-game / socialist-sns / 他）との独立性 / 関連性

## Phase 2：管理層スケルトン作成（10 分）

```bash
# cc-company 配下で実行
src=cc-company/skel/new-business-template
biz_mgmt=cc-company/.company/biz/[事業名]

# 1. 管理層ディレクトリ作成
mkdir -p $biz_mgmt/{inbox,todos,notes}

# 2. CLAUDE.md（管理層用）を skel から複製、事業名を書き換え
cp cc-company/.company/biz/drone-vibe-game/CLAUDE.md $biz_mgmt/CLAUDE.md
# → 事業名・概要・コードベース所在・差別化ポイントを書き換え

# 3. 当日の意思決定ノートを起こす
touch $biz_mgmt/notes/$(date +%Y-%m-%d)-decisions.md
```

- [ ] `cc-company/.company/biz/[事業名]/` ディレクトリ作成
- [ ] `CLAUDE.md`（事業概要・コードベース所在・ルール）作成
- [ ] `notes/YYYY-MM-DD-decisions.md` で立ち上げ決定を記録
- [ ] `cc-company/.company/CLAUDE.md` の「事業一覧」に追記

## Phase 3：実コード側スケルトン作成（15 分）

```bash
# 実コード側の場所（businesses/ または cc-company/biz-code/）に skel を複製
src=/Users/kaihasunuma/Desktop/Claude-test/cc-company/skel/new-business-template
dst=/Users/kaihasunuma/Desktop/Claude-test/businesses/[事業名]
# (submodule 化後は: dst=cc-company/biz-code/[事業名])

# skel をコピー（.git は含めない）
mkdir -p $dst
rsync -av --exclude='.git' $src/ $dst/

# scripts/ に check-secrets.sh と install-hooks.sh を配置
cp cc-company/.company/ceo/notes/templates/scripts/check-secrets.sh $dst/scripts/
cp cc-company/.company/ceo/notes/templates/scripts/install-hooks.sh $dst/scripts/
chmod +x $dst/scripts/*.sh

# CLAUDE.md と README.md の [事業名] を実際の事業名で sed 置換
cd $dst
sed -i '' "s/\[事業名\]/[ACTUAL_NAME]/g" CLAUDE.md README.md .env.example
```

- [ ] 実コード側ディレクトリに skel 複製
- [ ] `CLAUDE.md` / `README.md` / `.env.example` の `[事業名]` を実名に置換
- [ ] `scripts/check-secrets.sh` / `scripts/install-hooks.sh` 配置
- [ ] `.gitignore` の事業固有エントリを追加（必要なら）

## Phase 4：環境設定（10 分）

- [ ] `.env` を作成（`.env.example` をコピーして本物のキーを設定）
  - [ ] **CEO は `.env.example` を必ず Read** して、プレースホルダのみ確認（mistakes.md Case 4）
  - [ ] 本物のキーが `.env.example` に混入していないか目視
- [ ] git init して initial commit
  ```bash
  git init
  git add -A
  git commit -m "chore: initial scaffold from cc-company skel"
  ```
- [ ] pre-commit hook を有効化
  ```bash
  bash scripts/install-hooks.sh
  bash scripts/check-secrets.sh --all
  ```

## Phase 5：取締役会への 1 報（5 分）

- [ ] 「[事業名] の管理層 + 実コードスケルトンを作成、CEO ロールで起動可能」と取締役会へ報告
- [ ] 取締役会に必要なアクション（GitHub remote 作成 / 初回 push / 戦略書起案 etc.）を 1 リストで提示

## Phase 6：本格着手前の確認（CEO 単独）

- [ ] CLAUDE.md の `Environment` セクションが事業の実情と整合（OS / Runtime / Framework / DB / デプロイ先）
- [ ] CLAUDE.md が 200 行以内か確認（超えるなら `.claude/rules/` に分割）
- [ ] mistakes.md の Case 1〜8 を CEO が再確認（同じミスを繰り返さないため）

## 完了の判定

すべて [x] が付いたら、新規事業の立ち上げ完了。CEO は経営判断・実装段取りに移る。

---

## 想定所要時間

合計 **約 45 分**（Phase 1〜5 + Phase 6 の最終確認）。
将来 `/cc-new-project [事業名]` skill 化すれば 5 分以下に短縮可能（5/19〜5/20 実装予定）。
