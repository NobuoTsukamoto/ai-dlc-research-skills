# 出力テンプレート

プレースホルダーを実値へ置き換え、該当しない説明行は削除する。

## daily

```markdown
---
report_type: daily
period_start: YYYY-MM-DDT00:00:00+09:00
period_end: YYYY-MM-DDTHH:MM:SS+09:00
timezone: Asia/Tokyo
coverage: complete | partial
generated_at: YYYY-MM-DDTHH:MM:SS+09:00
---

# AIコーディングエージェント更新情報 YYYY-MM-DD

## サマリー

- 重要アップデート: N件
- その他の更新: N件
- 更新なし: Nツール
- 確認不能: Nツール

## 重要アップデート

### Tool name

#### [公式タイトル](canonical URL)

- 公開日: YYYY-MM-DD
- バージョン / 提供段階: version / stable | preview | experimental
- 重要度: high | medium
- 変更内容（要約）: 確認できた変更内容を自分の言葉で要約
- 制約: 対象プラン、OS、地域、段階的展開など。なければ「明記なし」
- 実務への影響（推論）: 変更が利用者やチームへ与える意味

## その他の更新

- **Tool name**: [タイトル](canonical URL) - 1～2文の要約（low）

## 更新なし

- Tool name

## 確認不能

- Tool name: 取得できなかったsourceと理由

## 調査メモ

- 確認したprimary source: N/N
- 過去日付で新たに発見した項目: なし | 一覧
```

## weekly

```markdown
---
report_type: weekly
period_start: YYYY-MM-DDT00:00:00+09:00
period_end: YYYY-MM-DDT23:59:59+09:00
timezone: Asia/Tokyo
coverage: complete | partial
generated_at: YYYY-MM-DDTHH:MM:SS+09:00
---

# AIコーディングエージェント週次まとめ YYYY-Www

## 週の要点

1. 最重要の変化
2. 次に重要な変化
3. 必要な場合だけ3点目

## ツール別まとめ

### Tool name

- 主要変更: 変更内容（要約）の統合
- 流れ: 複数更新を横断した整理
- 実務への影響（推論）: 判断や試行につながる示唆
- 公式ソース: [タイトル](URL)

## バズ

### [話題](official anchor URL)

- 変更内容（要約）: 対象更新の内容を自分の言葉で要約
- 観測した反応: 媒体、投稿日、観測日時、反応数または具体的シグナル
- 判定: confirmed | emerging
- 注目された理由（推論）: 反応と機能の関係
- コミュニティソース: [source 1](URL)、[source 2](URL)

十分な根拠がない場合:

**バズ: 該当なし**

## 来週の確認事項

- rollout、未解決の制約、次版で確認する項目

## 網羅性

- 利用したdaily: YYYY-MM-DD, ...
- 欠落daily: なし | YYYY-MM-DD, ...
- 取得不能source: なし | 一覧
```

## monthly

```markdown
---
report_type: monthly
period_start: YYYY-MM-01T00:00:00+09:00
period_end: YYYY-MM-DDT23:59:59+09:00
timezone: Asia/Tokyo
coverage: complete | partial
generated_at: YYYY-MM-DDTHH:MM:SS+09:00
---

# AIコーディングエージェント月次まとめ YYYY-MM

## エグゼクティブサマリー

- 月を代表する変化
- 複数ツールに共通した流れ
- 利用者・チームが判断すべきこと

## 主要アップデート

### テーマ

- 対象ツール: Tool A, Tool B
- 変更内容（要約）: 月内の変更を自分の言葉で要約
- 変化の方向: 前月または月初との比較
- 実務への影響（推論）: 導入、運用、ガバナンスへの意味
- 公式ソース: [source](URL)

## ツール別概況

| ツール | 主な更新 | 重要度 | 月末時点の提供段階 |
|---|---|---:|---|
| Tool | Summary | high / medium / low | stable / preview / experimental |

## 月間バズ

- 週次で確認された反応を統合する。根拠がなければ「該当なし」

## 対象外の有望ツール

| ツール | 公式URL | 何が有望か（要約） | 有望性の根拠（推論） | 成熟度 | 次の確認 |
|---|---|---|---|---|---|
| Tool | URL | Facts | Inference | stable / preview / experimental | Watch item |

条件を満たす候補がない場合:

**対象外の有望ツール: なし**

## 翌月へのウォッチ項目

- rollout、価格変更、previewのGA化、互換性、セキュリティ

## 網羅性

- 利用したweekly: YYYY-Www, ...
- 欠落weekly: なし | YYYY-Www, ...
- 月内のcanonical update: N件
- 取得不能source: なし | 一覧
```
