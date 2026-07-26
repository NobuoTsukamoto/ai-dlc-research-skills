---
name: ai-dlc-research
description: Research, rank, critically review, and log papers and industry reports about AI-driven software development. Use for weekly literature scans, selecting 1-2 readings, duplicate checks, PDF deep reviews, reading-log updates, and monthly evidence synthesis. Do not use for ordinary coding tasks or generic AI news.
license: MIT
---

# AI駆動開発リサーチ

AI駆動ソフトウェア開発に関する資料を、証拠の強さと実務適用性を重視して収集・評価する。

## 必ず最初に確認するもの

リポジトリルートを基準として、次の順に確認する。

1. `research/research-policy.md`
2. 依頼がどのタスクに該当するか
3. タスクに応じて必要なファイルだけを読む

`research/reading-log.md` の扱いは次のとおり。

- **weekly-scan / candidate-review**: 全文を読まず、候補ごとに `reading_log.py check` で照合する
- **deep-review**: 重複・ステータス確認を依頼された場合だけ `reading_log.py check` で照合する
- **log-update / monthly-synthesis**: 全文を読む

`research/research-policy.md` が存在しない場合は欠落を明記する。重複確認が必要なタスクで `research/reading-log.md` または照合スクリプトが存在しない場合も検索・評価は続行してよいが、重複判定は「不完全」と表示する。

## タスクの判定

- **weekly-scan**: 最新資料を探索し、今週読む1～2本を推薦
- **candidate-review**: 指定候補を比較・採点
- **deep-review**: PDFや本文を精読し、方法・結果・妥当性を評価
- **log-update**: `research/reading-log.md` を確認または更新
- **monthly-synthesis**: 読了資料を横断して知見を統合

複数に該当する場合は、探索 → 重複確認 → 評価 → 出力 → 明示依頼がある場合のみログ更新、の順に進める。

## weekly-scan

1. 現在日を確認する。
2. 直近7日を検索し、弱い場合のみ30日へ拡張する。
3. 査読済みジャーナル、査読済み国際会議、体系的レビュー、方法・データが明示されたプレプリント、方法論が明示された産業調査、ベンダー記事の順で優先する。
4. タイトル、著者、日付、掲載先、査読状況、DOI、本文アクセスを一次情報で確認する。
5. 候補ごとに `reading_log.py check` を実行する。DOIを優先し、DOIがなければ正規化したタイトルで確認する。
6. プレプリントと採録版が同一研究なら同一資料として扱い、採録版を優先する。
7. `research/research-policy.md` の10点基準で採点する。
8. 原則7点以上から最大2本を推薦する。
9. 良質な新規資料がなければ「新着推薦0件」と明記し、新着を水増ししない。
10. 直近30日に7点以上の新規資料がない場合は、過去の未読重要研究を探し、候補ごとに重複確認・採点したうえで最大1本をバックログ推薦する。
11. バックログ推薦は新着推薦と混ぜず、「過去の未読重要研究」と表示する。該当資料がなければ推薦なしとする。

検索語と探索先は `references/search-strategy.md`、情報源と証拠の評価は `references/source-quality.md` を参照する。

## candidate-review

評価前に `references/source-quality.md` を読む。重複確認が必要な場合は、候補ごとに `reading_log.py check` を実行する。

候補ごとに次を確認する。

- 研究タイプ
- サンプルと対象タスク
- 比較対象・対照群
- 自己申告か実測か
- 評価指標
- 統計手法と効果量
- データ・コード公開
- 内的妥当性、外的妥当性、再現性
- 著者・資金提供者・製品提供者との関係
- 現在のモデルやツールへの適用可能性

書誌情報や方法が確認できない資料は、証拠の強さを高く評価しない。

## deep-review

精読前に `references/source-quality.md` を読み、資料区分に応じた証拠評価の観点を確認する。

PDFまたは本文が提供された場合、単なる要約ではなく次を行う。

1. Research Questions / Hypothesesを特定する。
2. サンプル、対象者、対象プロジェクト、対象タスクを確認する。
3. 実験・調査・分析方法を確認する。
4. 評価指標、統計手法、効果量を確認する。
5. 表・図・付録を確認する。
6. Threats to Validityと再現可能性を評価する。
7. 著者の主張と、データから直接支持される結論を分ける。
8. 結論がデータを超えていないか確認する。
9. GitHub Copilot、Codex、Claude Code、AGENTS.md、Agent Skills、MCPとの関連を評価する。
10. チームで検証すべき仮説を提案する。

数値や図表には、可能な限りページ、表番号、図番号を付ける。記載がないことは「不明」とする。

## monthly-synthesis

1. 対象月を明示する。
2. `research/reading-log.md` から、ステータスが `read` かつ `読了日` が対象月に含まれる資料だけを選ぶ。
3. `読了日` が空欄の `read` 資料は統合対象に含めず、不完全な記録として件数を示す。
4. 個別要約の列挙ではなく、一致する知見、矛盾、証拠の強さ、適用条件を横断して整理する。

## 採点

合計10点。

- 関心との関連性: 0～3
- 研究方法・証拠の強さ: 0～3
- 実務・研修への適用可能性: 0～2
- 新規性: 0～1
- 本文へのアクセス性: 0～1

各項目の理由を1文で示す。

## 出力

`references/output-templates.md` の該当テンプレートを使う。

- 日本語で回答する。
- 事実、著者の主張、エージェントの推論を区別する。
- 重要な主張には一次情報の参照先を付ける。
- ベンダー調査は利益相反、サンプル偏り、自己申告/実測、対照群の有無を明記する。
- 新しさだけで推薦しない。
- 推薦は1～2本に絞る。
- 推定読了時間を示す。
- 不明点は不明と書く。

## reading-log

既定ではログを読み取り専用として扱う。ユーザーが「記録して」「更新して」「追加して」と明示した場合のみ変更する。

必要に応じて次を使う。

```bash
python .agents/skills/ai-dlc-research/scripts/reading_log.py check --log research/reading-log.md --title "Paper title" --doi "10.xxxx/xxxxx"
```

`check` は `DUPLICATE` と `NOT_FOUND` のどちらも正常終了 `0` とし、標準出力で判定する。引数や実行のエラーだけを非ゼロとする。

`add` でステータスを `read` にする場合は `--read-date YYYY-MM-DD` を必須とする。

変更前後の差分を確認する。

## 禁止事項

- 二次記事だけで研究結果を断定しない。
- ベンダーの主張を独立研究と同じ強さで扱わない。
- 検索結果スニペットだけで研究方法を断定しない。
- プレプリントを査読済みと表現しない。
- ログを無断で変更しない。
- 7点未満を枠埋めのために推薦しない。
