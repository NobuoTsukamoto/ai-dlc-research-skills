# Repository instructions

This repository contains Agent Skills for AI-driven software development research.

For weekly literature scans, paper ranking, critical paper reviews, duplicate checks, reading-log updates, or monthly evidence synthesis, use the `ai-dlc-research` agent skill in `.agents/skills/ai-dlc-research/`.

For official product-update and event tracking, daily digests, weekly rollups, monthly rollups, or promising AI coding-agent discovery, use the `ai-coding-agent-updates` skill in `.agents/skills/ai-coding-agent-updates/`.

Before evaluating material, always read:

- `research/research-policy.md`

For weekly scans and candidate reviews, do not load the entire `research/reading-log.md`. Check each candidate with `.agents/skills/ai-dlc-research/scripts/reading_log.py check`. Read the full log only for log updates and monthly synthesis.

Respond in Japanese. Prefer primary sources and peer-reviewed research. Distinguish facts, authors' claims, and inference. Do not modify `research/reading-log.md` unless the user explicitly asks to record or update it.

For coding-agent update reports, verify product facts with the official source registry. Keep official event announcements separate from product updates and inference; do not collect community buzz. Unless the user requests a preview, save reports under `updates/` and add new canonical product updates to `updates/update-log.jsonl`.
