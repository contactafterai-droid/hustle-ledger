# Conductor brief

Standing instructions for every scheduled Claude run on this repo. The goal is revenue in the GTA space. These rules exist because breaking them gets the assets that earn the money (the site, the channel, the listings) taken down.

## Setup at the start of every run

1. Attach the repo with push access (`add_repo` owner `contactafterai-droid`, repo `hustle-ledger`, access `push`), clone it to `/home/claude/hustle-ledger`, and work there.
2. Live site: https://contactafterai-droid.github.io/hustle-ledger/ (served from the `gh-pages` branch).
3. Every push to `main` runs `.github/workflows/deploy.yml`, which builds and publishes. After pushing, check the run with `gh api repos/contactafterai-droid/hustle-ledger/actions/runs` and fix it if it failed.
4. The shell cannot reach github.io. To confirm the live page, use the built-in browser if one is available; otherwise a green deploy run is the check.

## What each run does

### Daily news run (every morning)
1. Search for GTA 6 news from the last 24 hours: Rockstar Newswire, Take-Two investor news, major outlets, r/GTA6 top posts.
2. Add at most 3 genuinely new items to `data/news.json`. Each item: date, title, a summary in our own words (under 320 characters, never copied sentences), source URL, source name.
3. If a fact in `data/facts.json` changed (release date, price, platforms, online, PC), update it, update `verified_on`, and say what changed in a news item.
4. Run `python build.py`. If it fails, fix the data, never the checks.
5. Commit with a message like `news: 2026-11-06 (2 items)` and push to `main`.

### Money board run (daily after launch, weekly before)
1. Collect reported money methods with in-game $ per hour figures from community testing (Reddit, guides, videos).
2. Rank a method in `data/money-methods.json` only when at least two independent sources agree within roughly 25%. Store both sources.
3. Never present an unverified figure as fact. Mark early numbers as early.

### Server directory run (weekly)
1. Read open issues labelled `server-listing` (`gh issue list --label server-listing`).
2. Approve a server only if it meets every rule in `data/servers.json`. Check its public site and store yourself; the checkboxes are a claim, not proof.
3. Add approved servers to `data/servers.json`, comment on the issue with the outcome and close it. Comment with the reason when declining.
4. Remove servers that stop meeting the rules or go offline.

### Improvement run (Wednesdays)
The standing question: what can be more automated, and what can earn more?
1. Review the last week: what was published, what earned, what took a human, what broke.
2. Pick the single change with the best payoff for the effort. Examples: a new page that answers a high-search question, a new API endpoint, a new revenue switch, removing a manual step.
3. Ship it in the same run if it fits inside the hard rules and needs no new account. Otherwise put it at the top of `IDEAS.md` with the account or decision it needs.
4. Record what changed and why in `CHANGELOG.md`.

### Weekly report run (Sundays)
Send Isaiah a short summary: traffic, subscribers, revenue, what was published, what broke, what the improvement run shipped, and one decision only if no run can make it.

## Hard rules

- No leaked or pre-release footage or images, no story spoilers, no isolated cutscenes.
- No cheat, glitch, money-drop, mod-menu or account-sale content.
- No Rockstar logos, cover art or the GTA wordmark in our branding.
- Never collect money for a server's perks or dues. Servers sell perks through Tebex only.
- No crypto, gambling or loot-box promotion.
- Every fact links a source. If two sources conflict, publish neither until a third settles it.
- Video: original script with a point of view in every upload; official footage or short credited streamer clips under commentary; no raw stream re-uploads; no in-game radio audio; max 1 long video and 4 Shorts a week.

## Files

- `data/*.json` is the only thing scheduled runs edit.
- `build.py` validates data and builds `dist/`. GitHub Actions deploys on every push to `main`.
- Commits end with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
