# 事業: socialist-sns（社会主義SNS運用）

## 事業概要
X（旧Twitter）で「社会主義の認知を生活実感の言葉で広げる」ことを目的としたメディア運用事業。
賃金・家賃・育児費・医療など読者の生活領域から入り、思想用語は後出しで補う方針。
完全自動投稿パイプライン（Anthropic API + Google Sheets + GitHub Actions + X API v2）を構築済み。

## 資産・コードベース所在
- 戦略書・運用ドキュメント・assets: `/Users/kaihasunuma/Desktop/Claude-test/businesses/socialist-sns/`
- 自動運用キット（独立 git リポ）: `/Users/kaihasunuma/Desktop/Claude-test/businesses/socialist-sns/automation_kit/`
- 本フォルダは管理層のみ

## アカウント設計
- **ペルソナ**: 30代後半・都市部会社員。「活動家」ではなく「隣の席のちょっと詳しい人」
- **トーン**: 温度38度（怒っているが声を荒げない）/ 距離1.5m（隣に座るが肩は組まない）/ 速度普通
- **プロフィール案**: A.静かな専門家（推奨）/ B.当事者・共感 / C.中道・データドリブン
- **共通必須要素**: 「Automated」表示、1次ソース重視宣言、煽らない宣言、「社会主義」は初動3接点までは使わない

## コンテンツ設計
**4モード**（モードによってフォーマットを切り替える）
- A. 当事者モード（賃金/家賃/医療で困る20-40代）
- B. 知的好奇モード（歴史・思想・経済を知りたい層）
- C. 中道説得モード（経済合理性で動く社会人）
- D. 物語モード（ニュースに疲れて感情で読む層）

**5本柱**
- ①生活データ 30% / ②労働の現場 25% / ③歴史と思想 20% / ④国際比較 15% / ⑤ミーム反転 10%

**8フォーマット**
- F1: 数字フック / F2: 比較スレッド / F3: 歴史小話 / F4: ミーム反転 / F5: FAB / F6: 1人の物語 / F7: Q&A返信 / F8: 週次まとめ

**投稿スケジュール**: 平日4本・土日2本 = 週24本。スレッドは週6本目標。

## KPI（最上位は「保存+引用RT合計/月」）

| 階層 | 指標 | 30日目標 | 90日目標 | 180日目標 |
|---|---|---|---|---|
| 北極星 | 保存+引用RT/月 | 200 | 1,500 | 5,000 |
| 量 | 総imp/月 | 10万 | 60万 | 200万 |
| 量 | フォロワー | 500 | 3,000 | 10,000 |
| 質 | 平均eng率 | 3% | 4% | 5% |
| 質 | 新規プロフィールクリック/月 | 2,000 | 8,000 | 25,000 |
| 健全性 | ブロック+ミュート率 | <1% | <1% | <1% |

「フォロワー数」は副作用（攻撃的投稿の量産誘発）があるため最上位KPIに置かない。

## 倫理ガードレール（戦略ではなく契約）
- **採用しない**: 催眠誘導 / 脆弱層（派遣・病人・障害者）の勧誘 / 事実歪曲 / 自演RT / 所属感や選ばれた感での囲い込み
- **採用する**: 企画段階の構造化、タイトル/見出しの効かせ方（数字・疑問・逆説）、起承転結 / FAB、ラポール（誠実版「私も〜だった」）

## 現状ステータス（2026-05-09 時点）
- **フェーズ**: Phase 1（0-30日「土台」）の途中。**運用は未ローンチ**
- 戦略書 v1.0 完成 / 30日カレンダー作成済み / プロフィール清書版あり / automation_kit コード整備済み
- 直近の週次レポート（2026-05-17 週次レポート、生成日 2026-05-08）では **計画24本に対し投稿0本（達成率0%）**
- → **GitHub Actions の cron / API認証 / プロフィール公開がまだ完了していない可能性**
- 詳細は `notes/2026-05-09-business-summary.md` を参照

## フォルダ構成
- `inbox/` - 未整理のクイックキャプチャ
- `todos/` - 日次タスク管理（1日1ファイル）
- `notes/` - 壁打ち・コンセプト・リサーチ・意思決定ログ

## ルール（共通ルール `cc-company/.company/CLAUDE.md` を継承 + 事業固有）
- 日次ファイル名: `YYYY-MM-DD.md`、トピックファイル名: `kebab-case.md`
- 同日ファイルは追記、新規作成しない
- 意思決定は `notes/YYYY-MM-DD-decisions.md`
- **事業固有**: 投稿原稿の編集・レビュー業務が発生したら、戦略書「7. デザインの文法 × X 適用マッピング」と「禁止事項リスト」に沿って判断する

## 関連ドキュメント（資産側）
- `/Users/kaihasunuma/Desktop/Claude-test/businesses/socialist-sns/X運用戦略書.docx`（v1.0 / 2026年）
- `/Users/kaihasunuma/Desktop/Claude-test/businesses/socialist-sns/プロフィール・固定ポスト清書.md`（v1.0 / 2026年5月）
- `/Users/kaihasunuma/Desktop/Claude-test/businesses/socialist-sns/週次運用チェック.md`
- `/Users/kaihasunuma/Desktop/Claude-test/businesses/socialist-sns/デザインの文法.txt`
- `/Users/kaihasunuma/Desktop/Claude-test/businesses/socialist-sns/X投稿カレンダー_30日.xlsx`
- `/Users/kaihasunuma/Desktop/Claude-test/businesses/socialist-sns/automation_kit/README.md`
- `/Users/kaihasunuma/Desktop/Claude-test/businesses/socialist-sns/weekly_reports/週次レポート_2026-05-17.md`
