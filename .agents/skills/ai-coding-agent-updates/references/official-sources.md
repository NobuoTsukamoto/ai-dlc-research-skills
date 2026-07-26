# 公式情報源レジストリ

最終確認日: 2026-07-26

## 使い方

- `primary` はdailyで必ず確認する。
- `secondary` はprimaryの補完、発表の背景、提供条件の確認に使う。
- GitHub Releasesではstableを優先し、pre-releaseは明示して分ける。
- URLが移動していた場合は同一ベンダーの公式Docs、公式Blog、公式Organization内で移転先を探す。非公式ミラーへ切り替えない。

## 対象ID

更新ログの `tool` には次のIDだけを使う。

| ID | 表示名 | 含む範囲 |
|---|---|---|
| `github-copilot` | GitHub Copilot | IDE、GitHub.com、cloud agent、code review、Spacesなど一般機能 |
| `github-copilot-cli` | GitHub Copilot CLI | `@github/copilot` とagentic CLI。旧`gh-copilot`は移行情報だけ |
| `github-copilot-app` | GitHub Copilot app | Windows、macOS、Linux向けのGitHub公式デスクトップapp |
| `openai-codex` | OpenAI Codex | Codex app、CLI、IDE extension、cloud、SDK |
| `claude-code` | Claude Code | CLI、IDE、web、GitHub連携、Agent SDKとの直接連携 |
| `cursor` | Cursor | Editor、Agent、CLI、cloud agents、関連SDK |
| `antigravity-cli` | Google Antigravity CLI | `agy` CLI。Antigravity IDE/SDKはCLIへ直接影響する場合だけ |

## GitHub Copilot

### primary

- GitHub Changelog - Copilot: https://github.blog/changelog/label/copilot/
- GitHub Changelog feed: https://github.blog/changelog/feed/

### secondary

- GitHub Copilot documentation: https://docs.github.com/en/copilot
- GitHub Blog - Copilot: https://github.blog/ai-and-ml/github-copilot/

Changelog本文で対象surfaceを確認し、適切な対象IDへ振り分ける。同じ記事を複数IDへ記録するのは、各surfaceに独立した変更がある場合だけにする。Copilot cloud agentはこのIDへ含める。

## GitHub Copilot CLI

### primary

- Official releases: https://github.com/github/copilot-cli/releases
- Releases Atom feed: https://github.com/github/copilot-cli/releases.atom
- Official changelog: https://github.com/github/copilot-cli/blob/main/changelog.md

### secondary

- Product page: https://github.com/features/copilot/cli
- Official repository: https://github.com/github/copilot-cli
- GitHub Changelog - Copilot: https://github.blog/changelog/label/copilot/

Release notesが空または保守情報だけの場合、ユーザー影響を推測で補わない。CLI内 `/changelog` にしかない情報は、取得できた本文を公式情報として扱い、バージョンを記録する。

## GitHub Copilot app

### primary

- GitHub Changelog - Copilot: https://github.blog/changelog/label/copilot/

### secondary

- Product page: https://github.com/features/ai/github-app
- Getting started: https://docs.github.com/en/copilot/how-tos/github-copilot-app/getting-started

GitHub Copilot appは独立したデスクトップ製品として扱い、Copilot cloud agentと混同しない。CLIとappの共通runtimeに関する更新は、各surfaceへの影響が公式に明記された場合だけ両方へ記録する。

## OpenAI Codex

### primary

- Codex changelog: https://learn.chatgpt.com/docs/changelog
- Codex CLI releases: https://github.com/openai/codex/releases
- Releases Atom feed: https://github.com/openai/codex/releases.atom

### secondary

- What's new weekly digest: https://learn.chatgpt.com/docs/whats-new
- Codex documentation: https://developers.openai.com/codex/
- Official repository: https://github.com/openai/codex

製品Changelogをapp、desktop、cloud、IDE、mobileを含む横断更新の基準にする。GitHub ReleasesはCLIのversioned updateに使う。alphaやbetaをstableと混ぜない。

## Claude Code

### primary

- Official changelog: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- Official releases: https://github.com/anthropics/claude-code/releases
- Releases Atom feed: https://github.com/anthropics/claude-code/releases.atom

### secondary

- Claude Code documentation: https://code.claude.com/docs/en/overview
- Anthropic News: https://www.anthropic.com/news

CHANGELOGの細かな修正はまとめてよいが、セキュリティ、権限、データ処理、既定値変更は独立項目として扱う。

## Cursor

### primary

- Official changelog: https://cursor.com/changelog

### secondary

- Cursor documentation: https://docs.cursor.com/
- Cursor blog: https://cursor.com/blog

公式RSSが利用不能な場合はChangelogページを直接確認する。Forum投稿はCursor社員の発言であっても、製品仕様のprimary sourceにはしない。

## Google Antigravity CLI

### primary

- Product changelog: https://antigravity.google/changelog
- Official changelog file: https://github.com/google-antigravity/antigravity-cli/blob/main/CHANGELOG.md
- Official releases: https://github.com/google-antigravity/antigravity-cli/releases
- Releases Atom feed: https://github.com/google-antigravity/antigravity-cli/releases.atom

### secondary

- Official repository: https://github.com/google-antigravity/antigravity-cli
- Product site: https://antigravity.google/

Google所有ドメインまたは`google-antigravity` Organizationを公式とする。コミュニティ運営の類似ドメインを公式情報源にしない。

## source-type

更新ログでは次から選ぶ。

- `official-changelog`
- `official-release`
- `official-docs`
- `official-blog`
- `official-repository`

同じ更新が複数ソースにある場合、最も詳細で変更単位が明確なURLを記録し、他の公式URLはレポート本文の補足に使う。
