# AIコーディングエージェント 日次更新

`ai-coding-agent-updates` スキルを使用してください。

Asia/Tokyoの `{YYYY-MM-DD}` を対象に、対象ツールのprimary sourceをすべて確認してください。

- 公式アップデートだけを製品事実として扱う
- 新規候補は `update_log.py check` で重複確認する
- 公式事実と実務への影響（推論）を分ける
- 更新なしと確認不能を分ける
- dailyテンプレートでレポートを保存する
- 新規項目を `updates/update-log.jsonl` へ追加する
