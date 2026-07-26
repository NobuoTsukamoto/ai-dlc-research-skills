# AI駆動開発リサーチ Agent Skill

AI-DLCのリサーチを行うために、CodexとGitHub Copilot Appの両方で使えるリポジトリスコープの`Agent Skills`です。

## 構成

```text
.
├── AGENTS.md
├── LICENSE
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/ci.yml
├── .agents/skills/ai-dlc-research/
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/
│   └── tests/
├── research/
│   ├── research-policy.md
│   └── reading-log.md
├── prompts/
└── docs/
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
uv run .agents/skills/ai-dlc-research/scripts/validate_skill.py
uv run python -m unittest discover -s .agents/skills/ai-dlc-research/tests -p "test_*.py"
```

以後は、このリポジトリ直下で `uv run ...` を使えば、`.venv` の Python でそのまま実行できます。

## 日常コマンド

よく使う確認・検証コマンドです。

```bash
# スキル定義と必須ファイルの整合性確認
uv run .agents/skills/ai-dlc-research/scripts/validate_skill.py

# 付属テストの実行
uv run python -m unittest discover -s .agents/skills/ai-dlc-research/tests -p "test_*.py"

# 読書ログの重複確認
uv run python .agents/skills/ai-dlc-research/scripts/reading_log.py check --log research/reading-log.md --title "Paper title" --doi "10.xxxx/xxxxx"

# 読書ログへの追加
uv run python .agents/skills/ai-dlc-research/scripts/reading_log.py add --log research/reading-log.md --date "2026-07-26" --status candidate --title "Paper title" --authors "Author A; Author B" --year 2026 --type "査読論文" --venue "ICSE" --topics "agents; evaluation" --score 8 --url "https://doi.org/10.xxxx/xxxxx" --notes "first pass"
```

`--status read` で追加する場合は、対象月を正確に判定できるよう `--read-date "YYYY-MM-DD"` も指定してください。

## 使い方

使い方の詳細（暗黙呼び出し・明示呼び出し・Copilot Appでの利用・動作確認・同梱プロンプト・重複確認手順）は、次を参照してください。

- `docs/usage.md`

## 検証

```bash
uv run .agents/skills/ai-dlc-research/scripts/validate_skill.py
uv run python -m unittest discover -s .agents/skills/ai-dlc-research/tests -p "test_*.py"
```

GitHub Actionsでも、UbuntuとWindowsの両方で同じ検証を実行します。

## 注意

Web検索や外部サイトへのアクセス可否は、実行ホストと権限設定に依存します。検索が使えない場合も、ローカルPDFや候補一覧の評価には利用できます。

## ライセンス

MIT License。詳細は`LICENSE`を参照してください。
