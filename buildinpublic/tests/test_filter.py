"""機密フィルタのユニットテスト。最重要：偽陰性 (漏らし) を 0 にする。"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from buildinpublic.collect import ProgressItem
from buildinpublic.filter import filter_items, is_blocked


def _ts() -> datetime:
    return datetime(2026, 5, 11, 12, 0, tzinfo=timezone.utc)


def _item(title: str = "t", body: str = "b", path: str | None = None) -> ProgressItem:
    return ProgressItem(
        source="git:test", timestamp=_ts(), title=title, body=body, path=path
    )


# ---------- 段 1：パスブロック ----------

class TestPathBlock:
    def test_assets_blocked(self) -> None:
        assert is_blocked(
            "Next.js を入れた", "/repo/biz/socialist-sns/assets/X運用戦略書.docx"
        ) is not None

    def test_obsidian_blocked(self) -> None:
        assert is_blocked(
            "アイデア", "/repo/.company/obsidian/Fleeting/2026-05-11.md"
        ) is not None

    def test_decisions_blocked(self) -> None:
        assert is_blocked(
            "雑談", "/repo/.company/ceo/notes/decisions/2026-05-11.md"
        ) is not None

    def test_ceo_inbox_blocked(self) -> None:
        assert is_blocked(
            "ToDo", "/repo/.company/ceo/inbox/2026-05-11.md"
        ) is not None

    def test_biz_notes_allowed(self) -> None:
        assert is_blocked(
            "Next.js 16 にアップグレードして HMR が速くなった",
            "/repo/biz/drone-vibe-game/notes/2026-05-11-decisions.md",
        ) is None


# ---------- 段 2：API キー検出 ----------

class TestSecretDetection:
    def test_anthropic_key_blocked(self) -> None:
        text = "デバッグログに sk-ant-api03-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789AbCdEfGh が出た"
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_openai_key_blocked(self) -> None:
        text = "OPENAI=sk-proj-AbCdEfGhIjKlMnOpQrStUv"
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_aws_key_blocked(self) -> None:
        text = "誤って commit した: AKIAIOSFODNN7QWERTYUI"
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_aws_key_with_inline_placeholder_word_bypassed(self) -> None:
        # 行内に独立した EXAMPLE 等のプレースホルダ語があれば誤検出を回避（word boundary 必須）
        text = "AWS access key: AKIAIOSFODNN7QWERTYUI EXAMPLE"
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is None

    def test_github_pat_blocked(self) -> None:
        text = "ghp_" + "a" * 36 + " が漏れた"
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_pem_blocked(self) -> None:
        text = "鍵: -----BEGIN RSA PRIVATE KEY-----\n..."
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_placeholder_not_blocked(self) -> None:
        text = ".env.example に YOUR_API_KEY=sk-ant-api03-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX と書いた"
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is None


# ---------- 段 3：機密キーワード / KPI ----------

class TestKeywordBlock:
    def test_revenue_yen_blocked(self) -> None:
        assert is_blocked("今月の売上は 35,000 円", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_revenue_word_blocked(self) -> None:
        assert is_blocked("売上は 12 だった", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_mrr_blocked(self) -> None:
        assert is_blocked("MRR は 50 ドル", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_north_star_blocked(self) -> None:
        assert is_blocked("北極星 KPI まで遠い", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_1000man_blocked(self) -> None:
        assert is_blocked("年内 1000 万円が目標", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_attainment_rate_blocked(self) -> None:
        assert is_blocked("達成率 12 %", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_board_blocked(self) -> None:
        assert is_blocked("取締役会から指示があった", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_owner_blocked(self) -> None:
        assert is_blocked("オーナーが言うには", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_email_blocked(self) -> None:
        assert is_blocked(
            "連絡先 training.music.nlp@gmail.com",
            "/repo/biz/x/notes/2026-05-11-t.md",
        ) is not None

    def test_strategy_doc_blocked(self) -> None:
        assert is_blocked("戦略書を読んだ", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_confidential_blocked(self) -> None:
        assert is_blocked("機密文書を更新した", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_unreleased_strategy_blocked(self) -> None:
        assert is_blocked("未公開戦略を共有", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_confidential_information_english_blocked(self) -> None:
        assert is_blocked("contains confidential information", "/repo/biz/x/notes/2026-05-11-t.md") is not None

    def test_security_filter_term_allowed(self) -> None:
        # 「機密フィルタ」「機密検出」「機密スキャン」等の技術用語は通す
        text = "機密フィルタを実装して機密漏れを防ぐ仕組みを作った"
        # 「機密漏れ」は今は通る (機密＋具体物 regex に該当しないため)。これは意図通り
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is None

    def test_未公開_alone_allowed(self) -> None:
        # 「未公開機能」「未公開 API」等の単独「未公開」は通す
        assert is_blocked("未公開機能の動作確認", "/repo/biz/x/notes/2026-05-11-t.md") is None

    def test_mistakes_ref_blocked(self) -> None:
        assert is_blocked("mistakes.md に追記", "/repo/biz/x/notes/2026-05-11-t.md") is not None


# ---------- ホワイトリスト：通すべき内容 ----------

class TestAllowedContent:
    def test_implementation_log_allowed(self) -> None:
        text = "Next.js 16 にアップグレードして HMR が速くなった。Turbopack も試した。"
        assert is_blocked(text, "/repo/biz/drone-vibe-game/notes/2026-05-11-t.md") is None

    def test_failure_log_allowed(self) -> None:
        text = "ドローン制御の PID チューニングで詰まった。微分項を入れすぎて発振した。"
        assert is_blocked(text, "/repo/biz/drone-vibe-game/notes/2026-05-11-t.md") is None

    def test_oss_progress_allowed(self) -> None:
        text = "v3 配達シーンの障害物配置を実装した。drone-vibe-game リポに push 済み。"
        assert is_blocked(text, "/repo/biz/drone-vibe-game/notes/2026-05-11-t.md") is None

    def test_release_announcement_allowed(self) -> None:
        text = "Promptdrone ローンチした。配達ドローン × Vibe Coding ゲーム。"
        assert is_blocked(text, "/repo/biz/drone-vibe-game/notes/2026-05-11-t.md") is None

    def test_design_discussion_allowed(self) -> None:
        text = "設計議論：tweepy の OAuth1.0a を選ぶ理由は v2 API の write エンドポイントが OAuth1 必要だから。"
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is None

    def test_co_authored_by_footer_ignored(self) -> None:
        # git commit の Co-Authored-By footer はメール regex で誤検知させない
        text = (
            "feat(buildinpublic): 新規モジュールを追加\n"
            "\n"
            "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
        )
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is None

    def test_signed_off_by_footer_ignored(self) -> None:
        text = "fix: バグ修正\n\nSigned-off-by: Dev <dev@example.com>"
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is None

    def test_real_email_still_blocked(self) -> None:
        # Co-Authored-By 以外の本文内メールは引き続きブロック
        text = "問い合わせは user@example.com まで"
        assert is_blocked(text, "/repo/biz/x/notes/2026-05-11-t.md") is not None


# ---------- filter_items の振る舞い ----------

class TestFilterItems:
    def test_separates_passed_and_rejected(self) -> None:
        items = [
            _item("ok", "Next.js 16 に上げた", "/repo/biz/drone-vibe-game/notes/2026-05-11-t.md"),
            _item("ng", "取締役会の指示", "/repo/biz/drone-vibe-game/notes/2026-05-11-t.md"),
            _item("ng2", "戦略書を更新", "/repo/biz/drone-vibe-game/notes/2026-05-11-t.md"),
        ]
        result = filter_items(items)
        assert result.passed_count == 1
        assert result.rejected_count == 2
        assert result.passed[0].title == "ok"
        rejected_titles = {item.title for item, _ in result.rejected}
        assert rejected_titles == {"ng", "ng2"}

    def test_empty_input(self) -> None:
        result = filter_items([])
        assert result.passed_count == 0
        assert result.rejected_count == 0

    def test_path_blocked_item_rejected(self) -> None:
        items = [_item("t", "harmless", "/repo/biz/socialist-sns/assets/secret.md")]
        result = filter_items(items)
        assert result.passed_count == 0
        assert result.rejected_count == 1
        assert "path blocklist" in result.rejected[0][1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
