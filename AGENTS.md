# AI駆動開発リサーチ Skillsリポジトリ

このリポジトリは、AI駆動ソフトウェア開発に関する調査を継続的に行うAgent Skillsを管理します。

## ルーティング

### ai-dlc-research

次の依頼では `.agents/skills/ai-dlc-research/SKILL.md` を使用してください。

- 最新論文・調査報告の週次探索
- 読むべき1～2本の選定
- 候補論文の比較・採点
- PDF論文の精読
- `research/reading-log.md` の重複確認・更新
- 月次の知見統合

### ai-coding-agent-updates

次の依頼では `.agents/skills/ai-coding-agent-updates/SKILL.md` を使用してください。

- GitHub Copilot、Copilot CLI、GitHub Copilot appの公式更新調査
- Codex、Claude Code、Cursor、Antigravity CLIの公式更新調査
- AIコーディングエージェント更新の日次・週次・月次まとめ
- 週次のコミュニティ反応・バズ判定
- 月次の対象外有望ツール探索
- `updates/update-log.jsonl` の重複確認・更新

通常のコーディング依頼には、このスキルを使用しないでください。

## 永続データ

- 方針: `research/research-policy.md`
- 読書ログ: `research/reading-log.md`
- 更新ログ: `updates/update-log.jsonl`
- 更新レポート: `updates/daily/`、`updates/weekly/`、`updates/monthly/`

出力は日本語とし、事実・著者の主張・推論を区別してください。
`research/reading-log.md` は、ユーザーが明示的に更新を依頼した場合のみ変更してください。
更新レポート作成の依頼では、プレビュー指定がない限りレポートと `updates/update-log.jsonl` を更新してください。
