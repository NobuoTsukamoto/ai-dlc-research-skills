# AIコーディングエージェント 日次更新

`ai-coding-agent-updates` スキルを使用してください。

Asia/Tokyoの `{YYYY-MM-DD}` を対象に、対象ツールのprimary sourceをすべて確認してください。

- 公式アップデートだけを製品事実として扱う
- 新規候補は `update_log.py check` で重複確認する
- 公式文を転載せず、変更内容は自分の言葉で500文字以内に要約する
- 引用は短い語句（目安15語程度以下）に限定し、引用符とcanonical URLを付ける
- 公式事実と実務への影響（推論）を分ける
- 更新なしと確認不能を分ける
- dailyテンプレートでレポートを保存する
- 新規項目を `updates/update-log.jsonl` へ追加する
