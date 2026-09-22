# 使い方

このドキュメントは、GitHub Copilotベースで本リポジトリのAgent Skillを使うための実用手順です。

## 暗黙呼び出し

通常の日本語プロンプトで呼び出せます。

```text
AI駆動開発の最新論文を調査し、
今週読む価値が高いものを1～2本選んでください。
```

## 明示呼び出し

Codex CLIやIDEでは、`/skills`から選択するか、次のように指定できます。

```text
$ai-dlc-research

直近7日間のAI駆動開発に関する論文を調査し、
research/research-policy.mdに従って最大2本を推薦してください。
```

Codex公式ドキュメントでサポートされる2つの流儀:

- `/skills`または`$`による明示指定
- 説明文（description）に基づく暗黙選択

公式アップデート追跡は次のように呼び出します。

```text
$ai-coding-agent-updates

昨日のGitHub Copilot、Copilot CLI、GitHub Copilot app、
Codex、Claude Code、Cursor、Antigravity CLIの公式更新を確認し、
日次レポートへ保存してください。
```

`Codex - Claude Code` は2つの独立した対象として扱います。GitHub Copilot appはデスクトップ製品、Copilot cloud agentはGitHub Copilotの一般機能として区別します。

## Copilot Appで使う

Copilot Appで対象リポジトリを選択し、次のように依頼します。

```text
このリポジトリのAgent Skillを使用してください。

research/research-policy.mdを確認し、
reading_log.py checkで候補ごとに重複確認を行って、
AI駆動開発に関する今週の推薦を作成してください。

ログはまだ変更しないでください。
```

GitHub Copilot Appでは、プロンプトとスキルの`description`が一致すると、該当する`SKILL.md`がコンテキストへ読み込まれます。

## 動作確認

CodexとCopilot Appの両方で、次を実行してください。

```text
ai-dlc-researchスキルを使用して、
このリポジトリの設定を確認してください。

まだWeb検索は行わず、次だけ報告してください。

1. 認識した調査テーマ
2. 資料の評価基準
3. 重複判定方法
4. reading-log.mdを変更する条件
5. 週次推薦の出力項目
```

期待する結果:

- 評価は「関連性3、証拠3、適用可能性2、新規性1、アクセス性1」の合計10点
- 原則7点以上を推薦
- 推薦は最大2本
- DOIまたは正規化タイトルで重複確認
- 週次探索では`reading-log.md`を全文読み込みせず、候補ごとに照合
- プレプリントと採録版は同一研究として処理
- `research/reading-log.md`は明示依頼がなければ変更しない

## 用意したプロンプト

### コーディングエージェント更新

- 日次: `prompts/daily-tool-updates.md`
- 週次: `prompts/weekly-tool-updates.md`
- 月次: `prompts/monthly-tool-updates.md`

日次は公式情報だけを要約して `updates/daily/` と `updates/update-log.jsonl` へ保存します。週次は日次を統合して根拠のあるバズを最大3件抽出します。月次は週次を統合し、対象外の有望ツールを最大5件示します。根拠がなければ「該当なし」とします。

更新レポートをファイルへ保存せず確認だけ行う場合は、プロンプトに「プレビュー」「調査だけ」と指定してください。

### 週次調査

- `prompts/weekly-scan.md`

直近7日を対象にし、必要なら30日へ拡張して新規資料を最大2本推薦します。7点以上の新規資料がなければ、過去の未読重要研究から最大1本をバックログ推薦します。

### 論文精読

- `prompts/deep-review.md`

研究方法、効果量、内的・外的妥当性、再現性、表・図・ページ番号まで評価します。

### 月次統合

- `prompts/monthly-synthesis.md`

個別要約の列挙ではなく、複数研究の一致点・矛盾・実務仮説を統合します。

## reading-logの重複確認

簡単なPythonスクリプトを同梱しています。

```bash
uv run python .agents/skills/ai-dlc-research/scripts/reading_log.py check \
  --log research/reading-log.md \
  --title "論文タイトル" \
  --doi "10.xxxx/xxxxx"
```

結果は次のいずれかです。

```text
NOT_FOUND
```

または、

```text
DUPLICATE
```

`DUPLICATE`と`NOT_FOUND`はどちらも正常な判定結果で、終了コードは`0`です。引数や実行のエラーだけが非ゼロになります。

スキルは、ユーザーがログ更新を明示的に依頼したことを確認してから`reading_log.py add`を実行します。スクリプト単体はユーザー意図を判定しません。

月次統合では、ステータスが`read`で、かつ`読了日`が対象月に含まれる資料だけを使用します。CLIで`read`として追加する場合は`--read-date "YYYY-MM-DD"`が必須です。

## update-logの重複確認

公式アップデートのcanonical記録はJSONLで保持します。

```bash
uv run python .agents/skills/ai-coding-agent-updates/scripts/update_log.py check \
  --log updates/update-log.jsonl \
  --tool openai-codex \
  --title "Update title" \
  --url "https://example.com/official-update"
```

同一ツール内で、URLの追跡パラメータ違いまたは正規化タイトル一致を重複として判定します。1つの記事が複数surfaceへ独立した変更を含む場合は、対象IDごとに記録できます。週次・月次の期間抽出には `update_log.py list` を使用します。

要約の転載を防ぐため、`summary` と `impact` はそれぞれ500文字以内にし、両欄で40文字以上連続して一致する文章を避けます。ログ全体の検証は次のコマンドで実行できます。

```bash
uv run python .agents/skills/ai-coding-agent-updates/scripts/update_log.py validate \
  --log updates/update-log.jsonl
```

この連続一致検出は転載の防波堤であり、公式文との類似性を完全に判定するものではありません。公式文の引用は短い語句に限定し、引用符とcanonical URLを付けてください。
