# AI駆動開発リサーチ Agent Skill

AI-DCLのリサーチを行うために、CodexとGitHub Copilot Appの両方で使えるリポジトリスコープの`Agent Skills`です。

## 構成

```text
.
├── AGENTS.md
├── .github/copilot-instructions.md
├── .agents/skills/ai-driven-development-research/
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/
│   └── tests/
├── research/
│   ├── research-policy.md
│   └── reading-log.md
└── prompts/
```

## 導入

1. この一式を専用Gitリポジトリのルートへ展開する。
2. Gitへコミットする。
3. `uv sync` を実行して `.venv` を作成する。
4. CodexまたはGitHub Copilot Appでリポジトリを開く。
5. 初期テストを実行する。

## 最短手順

初回セットアップから検証までの最短手順です。

```bash
uv sync
uv run .agents/skills/ai-driven-development-research/scripts/validate_skill.py
uv run python -m unittest discover -s .agents/skills/ai-driven-development-research/tests -p "test_*.py"
```

以後は、このリポジトリ直下で `uv run ...` を使えば、`.venv` の Python でそのまま実行できます。

## 日常コマンド

よく使う確認・検証コマンドです。

```bash
# スキル定義と必須ファイルの整合性確認
uv run .agents/skills/ai-driven-development-research/scripts/validate_skill.py

# 付属テストの実行
uv run python -m unittest discover -s .agents/skills/ai-driven-development-research/tests -p "test_*.py"

# 読書ログの重複確認
uv run python .agents/skills/ai-driven-development-research/scripts/reading_log.py check --log research/reading-log.md --title "Paper title" --doi "10.xxxx/xxxxx"

# 読書ログへの追加
uv run python .agents/skills/ai-driven-development-research/scripts/reading_log.py add --log research/reading-log.md --date "2026-07-26" --status candidate --title "Paper title" --authors "Author A; Author B" --year 2026 --type "査読論文" --venue "ICSE" --topics "agents; evaluation" --score 8 --url "https://doi.org/10.xxxx/xxxxx" --notes "first pass"
```

## Codex

暗黙呼び出し:

```text
AI駆動開発の最新論文を調査し、今週読む1～2本を選んでください。
```

明示呼び出し:

- `/skills`から選択
- または`$ai-driven-development-research`を指定

## GitHub Copilot App

通常のプロンプトで対象タスクを依頼すると、スキルの`description`との一致により選択されます。

```text
このリポジトリのresearch-policy.mdとreading-log.mdに従って、
AI駆動開発の今週の推薦を作成してください。
```

## 初期テスト

```text
スキルを使って設定を確認してください。
まだWeb検索は行わず、次だけ報告してください。

1. 認識した調査テーマ
2. 評価基準
3. 重複判定方法
4. ログを変更する条件
5. 週次推薦の出力項目
```

## 検証

```bash
uv run .agents/skills/ai-driven-development-research/scripts/validate_skill.py
uv run python -m unittest discover -s .agents/skills/ai-driven-development-research/tests -p "test_*.py"
```

## 注意

Web検索や外部サイトへのアクセス可否は、実行ホストと権限設定に依存します。検索が使えない場合も、ローカルPDFや候補一覧の評価には利用できます。
