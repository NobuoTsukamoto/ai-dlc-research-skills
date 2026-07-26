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

## Copilot Appで使う

Copilot Appで対象リポジトリを選択し、次のように依頼します。

```text
このリポジトリのAgent Skillを使用してください。

research/research-policy.mdと
research/reading-log.mdを確認し、
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
- プレプリントと採録版は同一研究として処理
- `research/reading-log.md`は明示依頼がなければ変更しない

## 用意したプロンプト

### 週次調査

- `prompts/weekly-scan.md`

直近7日を対象にし、必要なら30日へ拡張して最大2本を推薦します。

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

ログ更新は、スキル上でもスクリプト上でも明示的な依頼がある場合だけ行う設計です。
