---
name: ai-coding-agent-updates
description: Track, verify, summarize, and persist official product updates for GitHub Copilot, GitHub Copilot CLI, GitHub Copilot app, OpenAI Codex, Claude Code, Cursor, and Google Antigravity CLI. Use for Japanese daily digests, weekly rollups with evidence-based community buzz, monthly rollups with promising-tool discovery, update-log duplicate checks, and source-registry audits. Do not use for general AI news or academic literature reviews.
---

# AIコーディングエージェント更新情報

対象ツールの公式アップデートを追跡し、日次・週次・月次で重複なく蓄積する。

## 最初に読む

リポジトリルートを基準に、次のファイルを必要な範囲だけ読む。

1. `references/official-sources.md`
2. `references/output-templates.md`
3. 週次のバズ判定または月次の新規ツール探索を行う場合は `references/buzz-and-discovery.md`
4. 対象期間に対応する `updates/daily/`、`updates/weekly/`、`updates/monthly/`

更新候補の重複確認には `scripts/update_log.py` と `updates/update-log.jsonl` を使う。

## タスクを判定する

- **daily**: 対象日の公式更新を確認し、ツール別に要約する
- **weekly**: 対象週の日次レポートを統合し、コミュニティで注目された更新を抽出する
- **monthly**: 対象月の週次レポートを統合し、対象外の有望ツールを探索する
- **source-audit**: 公式情報源のURL、所有主体、更新状況、代替経路を再確認する

期間指定がなければ、現在日時をAsia/Tokyoで判定する。「今日」「今週」「今月」は進行中期間として扱い、レポートに `partial` と表示する。「昨日」「先週」「先月」は完了期間として扱う。

## 共通ルール

1. 製品の事実は一次情報で確認する。検索結果のスニペットだけで確定しない。
2. 公式Changelog、公式Release、公式Docs、公式Blogの順で確認し、同一更新の転載や重複掲載を統合する。
3. モデルの一般リリースは、対象ツールでの利用可能性や挙動変更が公式に明記された場合だけ対象に含める。
4. 公開日、対象バージョン、提供段階（stable、preview、experimental）、対象プラン、OSや地域の制限を分けて記録する。
5. 公式事実と「実務への影響」という推論を明示的に分ける。
6. 重要な主張には、確認した公式ページへの直接リンクを付ける。
7. 全primary sourceを確認できた場合だけ「更新なし」と断定する。取得不能があれば「確認不能」または `partial` とする。
8. 同一ツールで同じURL、または実質同じタイトルは1件に統合する。複数surfaceへ独立した変更を含む記事は、対象IDごとに記録してよい。
9. 日本語で簡潔に書き、製品名、コマンド名、バージョンは原表記を維持する。

## daily

1. 対象日と実行時刻をAsia/Tokyoで確定する。
2. `references/official-sources.md` のprimary sourceを全対象ツールについて確認する。
3. 候補ごとに `update_log.py check` を実行する。
4. 本文またはRelease本文を開き、タイトル、公開日、提供段階、変更内容、制約を確認する。
5. 同一更新を統合し、重要度を付ける。
   - **high**: 破壊的変更、セキュリティ、価格・利用制限、GA、大きなワークフロー変更
   - **medium**: 新機能、対応範囲拡大、重要な性能・品質改善
   - **low**: 小規模修正、保守、利用者への影響が限定的な変更
6. dailyテンプレートで `updates/daily/YYYY-MM-DD.md` を作る。
7. 新規項目を `update_log.py add` で `updates/update-log.jsonl` に記録する。
8. 更新がないツールも「更新なし」一覧に残す。確認できなかったツールは別に示す。

ユーザーが「調査だけ」「プレビュー」と指定した場合はファイルを変更しない。それ以外のdaily作成依頼は、レポートとログの保存までを含む。

## weekly

1. 対象週を月曜00:00から日曜23:59:59までのAsia/Tokyoで確定する。
2. 対象期間の `updates/daily/` を読み、存在する日と欠落日を列挙する。
3. 日次項目を機能、モデル、エージェント実行、拡張性、セキュリティ、価格・制限、保守に整理する。
4. 同一機能の段階的ロールアウトや連続パッチを1つの流れとして統合する。
5. `references/buzz-and-discovery.md` に従い、対象週のコミュニティ反応を追加調査する。
6. 根拠が十分なものだけ最大3件を「バズ」として掲載する。不十分なら「該当なし」とする。
7. dailyの欠落や公式sourceの取得不能があれば、網羅性を `partial` とする。
8. weeklyテンプレートで `updates/weekly/YYYY-Www.md` を作る。

weeklyでは公式更新の事実とコミュニティ反応を混ぜない。反応数や投稿日は観測時点を併記する。

## monthly

1. 対象月をAsia/Tokyoの暦月で確定する。
2. 公式情報源レジストリの最終確認から31日以上経過していればsource-auditを行う。
3. 対象月と重なる `updates/weekly/` を読み、欠落週を列挙する。
4. 月内の日次項目に戻って件数を確認し、週境界をまたぐ項目の二重計上を避ける。
5. 単なる週次要約の列挙ではなく、主要変化、継続トレンド、実務への影響を統合する。
6. `references/buzz-and-discovery.md` に従って対象外ツールを探索する。
7. 公式に存在と機能を確認でき、かつ有望性の根拠があるツールだけ最大5件を示す。
8. 条件を満たす候補がなければ、必ず「対象外の有望ツール: なし」と書く。
9. monthlyテンプレートで `updates/monthly/YYYY-MM.md` を作る。

対象外ツールを翌月から追跡対象へ自動追加しない。追加はユーザーの明示判断を待つ。

## source-audit

1. `references/official-sources.md` の全primary URLを直接開く。
2. redirectされたURLは、所有主体が同じでcanonical URLと確認できた場合だけ置き換える。
3. 公式Organization、公式Docs、公式product pageの相互リンクで所有主体を確認する。
4. 取得不能なsourceには理由と代替の公式経路を記録する。
5. 全件確認後に「最終確認日」を更新する。

## 更新ログCLI

既定ログは `updates/update-log.jsonl`。

```bash
uv run python .agents/skills/ai-coding-agent-updates/scripts/update_log.py check \
  --log updates/update-log.jsonl \
  --tool openai-codex \
  --title "Update title" \
  --url "https://example.com/official-update"
```

`DUPLICATE` と `NOT_FOUND` はどちらも正常終了 `0`。引数、日付、ファイル形式のエラーだけを非ゼロにする。

追加例:

```bash
uv run python .agents/skills/ai-coding-agent-updates/scripts/update_log.py add \
  --log updates/update-log.jsonl \
  --tool openai-codex \
  --published-date 2026-07-26 \
  --discovered-date 2026-07-26 \
  --title "Update title" \
  --url "https://example.com/official-update" \
  --source-type official-changelog \
  --release-stage stable \
  --importance medium \
  --summary "公式発表の要約" \
  --impact "実務への影響"
```

期間抽出:

```bash
uv run python .agents/skills/ai-coding-agent-updates/scripts/update_log.py list \
  --log updates/update-log.jsonl \
  --from-date 2026-07-20 \
  --to-date 2026-07-26 \
  --format markdown
```

## 禁止事項

- 非公式記事を製品仕様の根拠にしない。
- 投稿日が対象期間内という理由だけで、過去の更新を新着として扱わない。
- 反応数を確認せず「バズった」と断定しない。
- 検索順位や検索結果件数を人気の証拠にしない。
- previewやexperimentalをGAと表現しない。
- 更新なし、バズなし、有望ツールなしを枠埋めしない。
- URL短縮サービスや転載ページをcanonical sourceにしない。
