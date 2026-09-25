# AIコーディングエージェント 日次更新

`ai-coding-agent-updates` スキルを使用してください。

Asia/Tokyoの `{YYYY-MM-DD}` を対象に、対象ツールのprimary sourceをすべて確認してください。

- 公式アップデートだけを製品事実として扱う
- 新規候補は `update_log.py check` で重複確認する
- 変更内容は自分の言葉で500文字以内に要約する
- 引用は短い語句（目安40文字以内）に限定し、引用符とcanonical URLを付ける
- 変更内容の要約と実務への影響（推論）を分ける
- 更新なしと確認不能を分ける
- Cursorは公式RSSの`pubDate`をAsia/Tokyoへ変換して対象日を判定し、候補があれば個別Changelog本文を確認する
- dailyテンプレートでレポートを `updates/daily/{YYYY-MM-DD}.md` に保存する
- 新規項目を `updates/update-log.jsonl` へ追加する

最終回答だけで済ませず、ファイル書き込みツールまたはshellツールで上記2ファイルを実際に作成・更新してください。作業完了前に、指定されたレポートパスとログパスが存在し、レポートが空でないことを確認してください。
