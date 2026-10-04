# issues-of-world

[![CI](https://github.com/SunnyYadav16/issues-of-world/actions/workflows/ci.yml/badge.svg)](https://github.com/SunnyYadav16/issues-of-world/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An interactive 3D globe. Click a place and see what is happening there, with a visible measure of how well each story is corroborated.

Status: early development. India's 36 states and union territories come first. There is no public demo yet. Every number comes from a command in this repository, so it can be reproduced.

## Why I am building this

I am tired of how information reaches people. Four problems keep coming up.

1. Wire copy looks like consensus. If 50 outlets reprint one agency report, a reader sees 50 headlines and assumes 50 confirmations. It is one report copied 50 times.
2. Rumours and rage bait travel faster than facts, and corrections are buried.
3. Tools that label stories "true" or "false" hide their sources, and they are often wrong with great confidence.
4. Local news gets drowned by national noise. Open a regional feed and most of it is about Delhi or Mumbai.

This project is my attempt at a better approach. It is a corroboration engine, not a truth oracle. It never says a story is true. It shows how many independent sources report it, and says so plainly when the evidence is thin.

## Measured so far

The state tagging step is scored against a gold set of 200 real headlines (`evals/datasets/geoparse.jsonl`). The labels were drafted with AI assistance and then reviewed by me. 39 rows are marked unknown and left out, so 161 rows are scored. Reproduce with `uv run iow eval geoparse` from the `pipeline` folder.

| Metric | GDELT codes only | Current tagging |
|---|---|---|
| Accuracy, all scored rows | 52.2% | 79.5% |
| Accuracy, rows with a state label | 77.1% | 89.9% |
| National list precision | not applicable | 88.2% |
| National list recall | 0.0% | 57.7% |

The gold set is small and partly AI drafted, so treat these as a first estimate. National recall is the weak point.

## Data sources

The registry in `data/sources.yaml` lists 32 sources. Only GDELT is active, because it is the only one with a working plugin.

1. 25 news feeds copied from an earlier prototype are registered but inactive. They cover national, business, legal, governance and technology outlets, and include PIB.
2. ReliefWeb and the Google Fact Check API are registered for later milestones. Four more outlets (ThePrint, Deccan Herald, LiveLaw, Bar and Bench) have no usable feed yet.
3. Terms of use have been read and recorded for 10 of the 32. The rest are inactive until someone reads them.
4. Each source has a tier: 1 for official bodies, 2 for established outlets, 3 for aggregators. The tier says who published a story. The genre (top, world, business, technology, legal, governance) says what kind of feed it is.
5. What a card may show comes from the registry, never from the plugin that fetched it. A source missing from the registry, or marked inactive, is never exported.

To add a source, add one entry to `data/sources.yaml`. A source that needs a new way of fetching also needs a plugin registered in `pipeline/pyproject.toml` under `iow.sources`. To remove one, delete its entry or set `active: false`. Logos are downloaded once with `uv run --project pipeline python scripts/fetch_logos.py` and served from this site, not hotlinked.

## Known limits

1. The state boundary tiles carry a credit to the Survey of India, while the third party repository they came from calls its files CC0. These cannot both be right, so the licence basis is unresolved. It has to be settled before any public deploy.
2. State tagging is wrong for roughly one in five scored headlines. GDELT's location codes predate Telangana and Ladakh, so their stories can land under Andhra Pradesh and Jammu and Kashmir when the headline names no place.
3. Search sends the text of a city or country query from the browser to open-meteo.com.
4. The state tiles are not stored in this repository. They are hosted on Cloudflare R2.
5. Some outlet terms forbid scraping or limit reuse to personal, non commercial use. Those sources stay inactive until their terms are reviewed.

## Repository layout

| Path | Contents |
|---|---|
| `apps/web/` | The web app: React, TypeScript, Vite and MapLibre |
| `pipeline/` | Python package `iow`: sources, state tagging, export, evals and the command line tool |
| `data/` | States and crosswalks (`in/`), categories (`categories.yaml`) and the source registry (`sources.yaml`) |
| `tiles/` | Script and config for the state tiles and label points |
| `evals/` | Gold sets in `datasets/`. Reports in `reports/` are generated and not tracked. The eval code lives in `pipeline/iow/evals/` |
| `scripts/` | Helper scripts: logo download and an API smoke test |
| `db/migrations/` | Numbered SQL migrations, empty until Postgres arrives |
| `.github/workflows/` | Continuous integration |

## Tech stack

| Part | Technology |
|---|---|
| Pipeline | Python 3.12, uv, pydantic, httpx, PyYAML |
| Pipeline checks | pytest, ruff, pyright, pre-commit |
| Web app | React 19, TypeScript 6, Vite 8, MapLibre GL 5, PMTiles |
| Web checks | Vitest 5, oxlint, oxfmt |
| Continuous integration | GitHub Actions, one job for the pipeline and one for the web app |

## Getting started

You need Python 3.12 with [uv](https://docs.astral.sh/uv/), and Node 22.12, 24, or 26 and newer, the versions Vitest 5 supports. CI uses Node 22.

1. Create the data the web app reads. This calls GDELT and needs no API keys.

```bash
cd pipeline
uv sync
uv run iow fetch --hours 6
uv run iow export --out ../apps/web/public
```

2. Start the web app.

```bash
cd apps/web
npm ci
cp .env.example .env.local
npm run dev
```

Set `VITE_TILES_URL` in `.env.local` to a PMTiles file that holds the Survey of India state layer (source layer name `State_LGD`). The maintainer's copy is on Cloudflare R2 and its CORS rule allows only `http://localhost:5173`. The app runs at that address.

The command line tool has three commands: `iow fetch`, `iow export` and `iow eval` (suites `sample`, `review` and `geoparse`). The file `.env.example` at the repository root lists API keys for sources that are not active yet. The current pipeline needs none of them.

## Checks

CI runs these on every pull request and on every push to main.

```bash
cd pipeline
uv run pre-commit run --all-files   # ruff lint and format check
uv run pyright
uv run pytest

cd ../apps/web
npx oxlint
npx oxfmt --check
npx tsc -b
npx vitest run
```

## License

Code is released under the [MIT License](LICENSE). Data sources, map layers and feed contents keep their own licenses and display terms, recorded in `data/sources.yaml`.
