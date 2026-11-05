# Hustle Ledger

GTA 6 money board, news, roleplay server directory and free JSON API.

- `data/*.json` holds all content. Scheduled runs edit only these.
- `python build.py` validates the data and builds `dist/`.
- `.github/workflows/deploy.yml` deploys `dist/` to GitHub Pages on every push to `main`, and rebuilds daily.
- `CONDUCTOR.md` is the standing brief for every scheduled run.

Not affiliated with Rockstar Games or Take-Two Interactive.
