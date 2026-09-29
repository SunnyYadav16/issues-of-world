# issues-of-world: Setup Day + First Working Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish Phase 0 accounts/keys today, then by about Oct 7 have a local globe where clicking an Indian state opens a panel of real GDELT headlines for that state.

**Architecture:** A Python pipeline (`pipeline/`, package `iow`) reads GDELT GKG files, keeps articles whose dominant location is an Indian state, stores them in a JSONL file, and exports static JSON (`summary.json` + one `issues.json` per state). A Vite + React + MapLibre app (`apps/web/`) renders a globe with the Survey of India state polygons from a PMTiles file on Cloudflare R2, and shows the exported headlines in a side panel. No database, no classifier, no clustering, no dedup in this slice.

**Tech Stack:** Python 3.12 + uv + pydantic v2 + httpx + pytest + ruff; Vite + React 19 + TypeScript + MapLibre GL JS 5 + pmtiles + Vitest; Cloudflare R2 via `npx wrangler`.

**Spec:** `issues-of-world_ Project Plan v1.0.1.html` (repo root, kept local and gitignored, see Task A1). Section refs below (§) point at it. Task IDs (IOW-nnn) are that plan's backlog IDs.

## Coverage map

| Backlog ID | Where | Note |
|---|---|---|
| IOW-001 | A1 | Repo already exists and is public. Remaining: LICENSE, README, pin. |
| IOW-006 | A2 | |
| IOW-007 | A3 | |
| IOW-008 | A4 | |
| IOW-009 | B1 | Includes minimal `pipeline/` project setup (part of IOW-003). |
| IOW-020 | B4 | Uses the repo's prebuilt SoI state tiles (see D-015). |
| IOW-022 | B4 | Upload only. No tippecanoe build needed. |
| IOW-041 | B2 | Reads GDELT **GKG files**, not the DOC 2.0 API (see D-013). |
| IOW-050 | B3 | Writes JSON to `apps/web/public/`. R2 upload of JSON is deferred. |
| IOW-030, IOW-031 | B6 | |
| IOW-033 | B7 | Plain headline list, no category tabs. |

Not in this plan: IOW-021 (world ADM0), IOW-023 (boundary QA), IOW-036 (deploy). Consequence: **the app stays local-only** until those land (see Global Constraints).

## Global Constraints

Copied from the spec. Every task's requirements include these.

- India's national and state boundaries come only from Survey of India-aligned data (§4.1). This slice uses `SOI_States.pmtiles` from `yashveeeeeeer/india-geodata` (release tag `admin/states`).
- The basemap's own country-border and disputed-boundary layers are hidden, and our compliant boundaries are drawn on top (§4.1).
- Boundary QA (IOW-023) has not run in this slice, so **do not deploy the web app publicly** and do not share screenshots of J&K / Ladakh / Arunachal as "final".
- Display only headline, outlet, date, link (§4.4). Every source declares a `display_policy`; the exporter removes any field the policy does not allow.
- Excluded: YouTube scraping, ACLED, GADM, NewsAPI free tier (§4.4).
- Attribution: GDELT, india-geodata / Survey of India, OpenStreetMap / OpenFreeMap are credited on the `/data` page (page itself is IOW-035, later). Record them in `docs/DATA_LICENSES.md` now.
- Every exported JSON file carries `schema_version` and `generated_at` (§6.5).
- Python 3.12, uv, ruff, pytest, pydantic v2, httpx (§6.2). Web: Vite, React 19 + TypeScript, MapLibre GL JS 5.x (install as `maplibre-gl@5`; npm `latest` is now 6.x), PMTiles, OpenFreeMap style, Vitest (§6.1).
- Code is MIT-licensed (§10). Secrets (`RELIEFWEB_APPNAME`, API keys) are never committed; they live in GitHub secrets and a gitignored `.env`.

## Review Focus

Failure modes the spec implies but a happy-path build would miss. Each has a test in the task named in brackets.

1. **Foreign article that merely mentions India.** GKG rows list every place in an article. An article about Nagoya that names Delhi once must not appear under Delhi. Rule: the article's single most frequent ADM1 code (any country) must be an Indian state; ties go to the first seen. [B2]
2. **Country-level or unknown India tags.** `IN00` ("India (General)") and country-only rows have no state. They must be dropped, not guessed. [B2, B3]
3. **Missing, blank, or HTML-escaped headline.** No headline means nothing to show, so drop the row. `&amp;` must become `&`. [B2]
4. **Hostile or malformed links.** URLs come from third-party feeds. Non-http(s) URLs must never reach the JSON (exporter) or an `href` (web). [B3, B5]
5. **Short/garbage GKG rows and unpublished 15-minute slots.** A row with fewer than 27 columns is skipped; a 404 slot is skipped; other HTTP errors fail the run loudly instead of silently dropping data. [B2]
6. **Empty states.** All 36 states get an `issues.json` (empty list if no stories) so the panel never hits a 404. [B3, B7]
7. **Known gap, not testable here:** GDELT files every Hyderabad mention under Andhra Pradesh (`IN02`), so Telangana's panel will be empty and Andhra Pradesh's will contain Telangana stories. Same for Ladakh → J&K. Logged as D-016; fixed later by the gazetteer fallback (IOW-047).

## File structure

```
.gitignore                         (modify: append generated/secret paths)
LICENSE, README.md                 (A1)
.env.example                       (A3, A4)
scripts/factcheck_smoke.sh         (A3)
data/in/states.yaml                (B1)
docs/DATA_LICENSES.md              (B4)
docs/DECISIONS.md                  (B8)
pipeline/
  pyproject.toml
  iow/__init__.py
  iow/cli.py                       argparse entry: `iow fetch`, `iow export`
  iow/store.py                     JSONL store, dedupe by URL
  iow/core/{__init__,contracts,states}.py
  iow/plugins/{__init__}.py, plugins/sources/{__init__,gdelt}.py
  iow/stages/{__init__,export}.py
  tests/{test_states,test_gdelt,test_store,test_export}.py
tiles/cors.json                    (B4; the .pmtiles itself is gitignored)
apps/web/
  src/lib/data.ts (+ data.test.ts)
  src/map/MapView.tsx
  src/panel/StatePanel.tsx
  src/App.tsx, App.css, index.css
```

**Order:** A1-A4 (today, ~1 h of your time + waiting on ReliefWeb email) → B1 → B2 → B3 → B4 (can run in parallel with B2/B3) → B5 → B6 → B7 → B8.

**Time (12 h/week):** Part A about 1 h. Part B: B1 2 h, B2 3 h, B3 2 h, B4 2 h, B5 1 h, B6 3 h, B7 1.5 h, B8 1 h = about 15.5 h. That is roughly 1.3 weeks of capacity, so Oct 7 is tight but possible. If you fall behind, cut B4's R2 upload first: serve the PMTiles from `apps/web/public/` locally and finish R2 later. Do not cut tests.

---

# Part A: Today (setup and accounts)

Manual work, no TDD. Never paste a secret into a chat, an issue, or a commit.

### Task A1: Finish the repo (IOW-001), about 15 min

The GitHub repo `SunnyYadav16/issues-of-world` already exists and is public. Missing: MIT license, README skeleton, profile pin. Also keep the project-plan HTML out of the public repo: it names your other projects and your time budget (§1.3).

**Files:**
- Create: `LICENSE`, modify: `README.md`, `.gitignore`

- [ ] **Step 1: Add the MIT license**

Create `LICENSE`:

```
MIT License

Copyright (c) 2026 Sunny Yadav

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Write the README skeleton**

Replace `README.md` with:

```markdown
# issues-of-world

An interactive 3D globe. Click a place, see what is happening there, with a visible measure of how well each story is corroborated.

**Status:** early development (Phase 0). Starts with India's 36 states and union territories.

It is a corroboration engine, not a truth oracle: it reports how many independent sources confirm a story, never that a story is "true".

## Layout

- `pipeline/`: Python ingestion and export
- `apps/web/`: Vite + React + MapLibre globe
- `data/`: reference data (states, categories, sources)
- `docs/`: decisions, data licenses

## License

Code: MIT. Data files carry their own licenses, see `docs/DATA_LICENSES.md`.
```

- [ ] **Step 3: Ignore generated files, secrets, and the plan HTML**

Append to `.gitignore`:

```
# issues-of-world
.env
pipeline/var/
apps/web/public/data/
tiles/*.pmtiles
tiles/*.parquet
/issues-of-world_ Project Plan*.html
# the Python template's `lib/` rule would otherwise hide the web app's src/lib (plan §10)
!apps/web/src/lib/
```

- [ ] **Step 4: Verify what is and is not ignored**

Run: `git status --short`
Expected: lists `LICENSE`, `README.md`, `.gitignore`, `docs/` and does **not** list the `Project Plan` HTML.

Run: `git check-ignore -v apps/web/src/lib/data.ts; echo "exit=$?"` (the path need not exist yet)
Expected: no output line, `exit=1`. Without the `!apps/web/src/lib/` line it prints `.gitignore:17:lib/ ...` and `exit=0`.

- [ ] **Step 5: Commit and push**

```bash
git add LICENSE README.md .gitignore docs/superpowers/plans
git commit -m "chore: add MIT license, README skeleton, first-slice plan"
git push origin main
```

- [ ] **Step 6: Pin the repo (manual, 1 min)**

GitHub profile → "Customize your pins" → tick `issues-of-world`. (GitHub has no API for pins.)

Done when: `gh repo view SunnyYadav16/issues-of-world --json licenseInfo -q .licenseInfo.key` prints `mit` and the repo shows on your profile.

---

### Task A2: Request the ReliefWeb appname (IOW-006), about 10 min + wait

ReliefWeb needs a pre-approved appname since Nov 1, 2025. Format required: your (organization) name + purpose + random characters. Review takes about one business day.

- [ ] **Step 1: Generate the random part**

Run: `echo "issues-of-world-$(openssl rand -hex 4)"`
Expected: something like `issues-of-world-3fa91c07`. Copy it. This is your requested appname.

- [ ] **Step 2: Submit the form**

Open https://docs.google.com/forms/d/e/1FAIpQLScR5EE_SBhweLLg_2xMCnXNbT6md4zxqIB00OL0yZWyrqX_Nw/viewform?usp=header and fill in: your name, "issues-of-world (open-source portfolio project)", purpose "show ReliefWeb disaster reports for Indian states on a public map, headline + link only", and the appname from Step 1.

- [ ] **Step 3: When the approval email arrives, store the appname**

```bash
gh secret set RELIEFWEB_APPNAME -R SunnyYadav16/issues-of-world
```
Paste the approved appname at the prompt. Then add `RELIEFWEB_APPNAME=<appname>` to your local `.env` (gitignored).

- [ ] **Step 4: Verify nothing leaked into git (all history, not just the working tree)**

```bash
APP=$(sed -n 's/^RELIEFWEB_APPNAME=//p' .env)
[ -n "$APP" ] && ! git grep -qF "$APP" $(git rev-list --all) && echo clean
```
Expected: `clean`. (Checks your real appname, so the example value in this plan does not trip it.)

Done when: `gh secret list -R SunnyYadav16/issues-of-world` shows `RELIEFWEB_APPNAME`.

---

### Task A3: Google Fact Check key (IOW-007), about 20 min

**Files:**
- Create: `scripts/factcheck_smoke.sh`, `.env.example`

- [ ] **Step 1: Create the key**

Google Cloud Console → new project `issues-of-world` → APIs & Services → enable **Fact Check Tools API** → Credentials → Create API key → restrict it to "Fact Check Tools API". Copy the key.

- [ ] **Step 2: Store it**

```bash
gh secret set GOOGLE_FACTCHECK_API_KEY -R SunnyYadav16/issues-of-world
```
Also add `GOOGLE_FACTCHECK_API_KEY=<key>` to your local `.env`.

- [ ] **Step 3: Write the smoke-test script**

Create `scripts/factcheck_smoke.sh`:

```bash
#!/usr/bin/env bash
# Smoke test for IOW-007: the key works and returns ClaimReview items.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; [ -f .env ] && . ./.env; set +a
: "${GOOGLE_FACTCHECK_API_KEY:?set it in .env}"
curl -fsS -G 'https://factchecktools.googleapis.com/v1alpha1/claims:search' \
  --data-urlencode 'query=India' --data-urlencode 'languageCode=en' \
  --data-urlencode 'pageSize=5' --data-urlencode "key=${GOOGLE_FACTCHECK_API_KEY}" |
python3 -c '
import json, sys
claims = json.load(sys.stdin).get("claims", [])
assert claims, "no claims returned"
for c in claims:
    print(c["claimReview"][0]["publisher"]["name"], "|", c["text"][:80])
'
```

- [ ] **Step 4: Run it**

Run: `chmod +x scripts/factcheck_smoke.sh && ./scripts/factcheck_smoke.sh`
Expected: up to 5 lines of `Publisher | claim text`. Failure `no claims returned` means the key works but the query found nothing; try `query=Modi`. `curl: (22) ... error: 400` means the key is wrong (checked: an invalid key returns `400 API_KEY_INVALID`); `403` means the API is not enabled or the key restriction is wrong.

- [ ] **Step 5: Add `.env.example` and commit**

Create `.env.example`:

```
RELIEFWEB_APPNAME=
GOOGLE_FACTCHECK_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
```

```bash
git add scripts/factcheck_smoke.sh .env.example
git commit -m "chore: add fact-check smoke test and .env.example"
git push
```

Done when: the script prints India-related fact checks.

---

### Task A4: LLM keys and spend alerts (IOW-008), about 15 min

No LLM is called in the first slice (classification comes later), but the keys and the spend alerts are Phase 0 and cheap to do now.

- [ ] **Step 1: Create keys**

Anthropic Console → API keys → create `issues-of-world`. OpenAI dashboard → API keys → create `issues-of-world`. (Skip a provider you will not use; §9 estimates Claude Haiku 4.5 about $19/month and GPT-5 mini about $5-6/month.)

- [ ] **Step 2: Set spend limits first, before storing the keys**

Anthropic Console → Billing/Limits: set a monthly limit of $25 and an email alert at $10. OpenAI → Billing → Usage limits: hard limit $25, email threshold $10. (Matches the ≤ $25/month target in §8.2.)

- [ ] **Step 3: Store the keys**

```bash
gh secret set ANTHROPIC_API_KEY -R SunnyYadav16/issues-of-world
gh secret set OPENAI_API_KEY -R SunnyYadav16/issues-of-world
```
Also add both to local `.env`.

- [ ] **Step 4: Verify**

Run: `gh secret list -R SunnyYadav16/issues-of-world`
Expected: `RELIEFWEB_APPNAME` (once approved), `GOOGLE_FACTCHECK_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`.

Done when: keys are in GitHub secrets and both providers show a spend cap.

---

# Part B: First working slice (target Oct 7)

Slice acceptance: `iow fetch` + `iow export` fill `apps/web/public/data/`; `npm run dev` shows a globe with India's states; clicking Maharashtra opens a panel with real, dated headlines that link out.

### Task B1: states.yaml and the pipeline project (IOW-009), about 2 h

Creates the Python project (the minimum of IOW-003 the slice needs) and the reference data every later task reads. Key facts already verified against real data on 2026-09-28:

- The SoI tiles key each state by numeric `State_LGD` (1-24, 27-38). That is the join key between the map and this file.
- GDELT tags places with FIPS ADM1 codes. Observed in 24 h of GKG: 33 codes. `IN07` is Delhi (not `IN06`), `IN21` is "Orissa", `IN39` is "Uttaranchal", `IN00` is "India (General)".
- GDELT has no code for Telangana or Ladakh (Hyderabad → `IN02`). `IN05` (Chandigarh) and `IN29` (Sikkim) were not seen in the 24 h sample; they come from GeoNames and statoids.com (FIPS 10-4), which agree with GDELT on every code that was seen. Daman & Diu has no known code, so Dadra & Nagar Haveli's `IN06` stands for the merged UT.

**Files:**
- Create: `pipeline/pyproject.toml`, `pipeline/.python-version`, `pipeline/iow/__init__.py`, `pipeline/iow/core/__init__.py`, `pipeline/iow/core/states.py`, `data/in/states.yaml`, `pipeline/tests/test_states.py`

**Interfaces:**
- Produces: `State` model (`iso: str`, `lgd: int`, `name: str`, `type: "state"|"ut"`, `capital: str`, `aliases: list[str]`, `gdelt_fips: list[str]`); `load_states() -> list[State]` (36 entries); `fips_index() -> dict[str, State]` mapping a GDELT code such as `"IN07"` to its `State`.

- [ ] **Step 1: Create the project skeleton**

```bash
mkdir -p pipeline/iow/core pipeline/iow/plugins/sources pipeline/iow/stages pipeline/tests data/in
touch pipeline/iow/__init__.py pipeline/iow/core/__init__.py pipeline/iow/plugins/__init__.py \
      pipeline/iow/plugins/sources/__init__.py pipeline/iow/stages/__init__.py
echo "3.12" > pipeline/.python-version
```

Create `pipeline/pyproject.toml`:

```toml
[project]
name = "iow"
version = "0.0.1"
description = "issues-of-world pipeline"
requires-python = ">=3.12"
dependencies = ["pydantic>=2", "httpx>=0.27", "pyyaml>=6"]

[project.scripts]
iow = "iow.cli:main"

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["iow"]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I"]
```

- [ ] **Step 2: Install and confirm an empty suite passes**

Run: `cd pipeline && uv sync && uv run pytest`
Expected: `no tests ran` (exit code 5 is fine for an empty suite).

- [ ] **Step 3: Write the failing test**

Create `pipeline/tests/test_states.py`:

```python
# pipeline/tests/test_states.py
from iow.core.states import fips_index, load_states


def test_thirty_six_unique_states():
    states = load_states()
    assert len(states) == 36
    assert len({s.iso for s in states}) == 36
    assert {"OD", "CG", "TS", "UK"} <= {s.iso for s in states}  # ISO 3166-2:IN codes changed 2023-11-23
    # LGD codes used by the SoI tiles: 1-24 and 27-38
    assert {s.lgd for s in states} == set(range(1, 25)) | set(range(27, 39))


def test_fips_codes_are_unique_and_resolve():
    idx = fips_index()
    assert sum(len(s.gdelt_fips) for s in load_states()) == len(idx)  # no code claimed twice
    assert idx["IN07"].iso == "DL"
    assert idx["IN21"].name == "Odisha"  # GDELT still says "Orissa"
    assert idx["IN02"].iso == "AP"  # GDELT files Hyderabad here (D-016)
    assert "IN00" not in idx  # country-level "India (General)" is not a state


def test_former_names_are_aliases():
    alias = {a: s.iso for s in load_states() for a in s.aliases}
    assert alias["Orissa"] == "OD"
    assert alias["Pondicherry"] == "PY"
    assert alias["Bombay"] == "MH"
```

- [ ] **Step 4: Run it and see it fail**

Run: `cd pipeline && uv run pytest tests/test_states.py -v`
Expected: FAIL / collection error `ModuleNotFoundError: No module named 'iow.core.states'`.

- [ ] **Step 5: Write `data/in/states.yaml`**

```yaml
# data/in/states.yaml
# 36 states and union territories (IOW-009).
#   iso        ISO 3166-2:IN suffix (IN-MH -> MH)
#   lgd        Local Government Directory state code; equals State_LGD in the SoI tiles
#   gdelt_fips GDELT ADM1 codes that mean this state. Empty = GDELT has no code for it.
# Sources: ISO codes per ISO 3166-2:IN after the 2023-11-23 change (OD, CG, TS, UK).
# FIPS codes seen in 24 h of GDELT GKG (2026-09-28); IN05, IN29 from GeoNames + statoids.com (not yet seen in GDELT).
- {iso: JK, lgd: 1,  name: Jammu and Kashmir, type: ut, capital: Srinagar / Jammu, aliases: [Kashmir, J&K], gdelt_fips: [IN12]}
- {iso: HP, lgd: 2,  name: Himachal Pradesh, type: state, capital: Shimla, aliases: [], gdelt_fips: [IN11]}
- {iso: PB, lgd: 3,  name: Punjab, type: state, capital: Chandigarh, aliases: [], gdelt_fips: [IN23]}
- {iso: CH, lgd: 4,  name: Chandigarh, type: ut, capital: Chandigarh, aliases: [], gdelt_fips: [IN05]}
- {iso: UK, lgd: 5,  name: Uttarakhand, type: state, capital: Dehradun, aliases: [Uttaranchal], gdelt_fips: [IN39]}
- {iso: HR, lgd: 6,  name: Haryana, type: state, capital: Chandigarh, aliases: [], gdelt_fips: [IN10]}
- {iso: DL, lgd: 7,  name: Delhi, type: ut, capital: New Delhi, aliases: [NCT of Delhi, New Delhi], gdelt_fips: [IN07]}
- {iso: RJ, lgd: 8,  name: Rajasthan, type: state, capital: Jaipur, aliases: [], gdelt_fips: [IN24]}
- {iso: UP, lgd: 9,  name: Uttar Pradesh, type: state, capital: Lucknow, aliases: [], gdelt_fips: [IN36]}
- {iso: BR, lgd: 10, name: Bihar, type: state, capital: Patna, aliases: [], gdelt_fips: [IN34]}
- {iso: SK, lgd: 11, name: Sikkim, type: state, capital: Gangtok, aliases: [], gdelt_fips: [IN29]}
- {iso: AR, lgd: 12, name: Arunachal Pradesh, type: state, capital: Itanagar, aliases: [], gdelt_fips: [IN30]}
- {iso: NL, lgd: 13, name: Nagaland, type: state, capital: Kohima, aliases: [], gdelt_fips: [IN20]}
- {iso: MN, lgd: 14, name: Manipur, type: state, capital: Imphal, aliases: [], gdelt_fips: [IN17]}
- {iso: MZ, lgd: 15, name: Mizoram, type: state, capital: Aizawl, aliases: [], gdelt_fips: [IN31]}
- {iso: TR, lgd: 16, name: Tripura, type: state, capital: Agartala, aliases: [], gdelt_fips: [IN26]}
- {iso: ML, lgd: 17, name: Meghalaya, type: state, capital: Shillong, aliases: [], gdelt_fips: [IN18]}
- {iso: AS, lgd: 18, name: Assam, type: state, capital: Dispur, aliases: [], gdelt_fips: [IN03]}
- {iso: WB, lgd: 19, name: West Bengal, type: state, capital: Kolkata, aliases: [Bengal, Paschimbanga], gdelt_fips: [IN28]}
- {iso: JH, lgd: 20, name: Jharkhand, type: state, capital: Ranchi, aliases: [], gdelt_fips: [IN38]}
- {iso: OD, lgd: 21, name: Odisha, type: state, capital: Bhubaneswar, aliases: [Orissa], gdelt_fips: [IN21]}
- {iso: CG, lgd: 22, name: Chhattisgarh, type: state, capital: Raipur, aliases: [], gdelt_fips: [IN37]}
- {iso: MP, lgd: 23, name: Madhya Pradesh, type: state, capital: Bhopal, aliases: [], gdelt_fips: [IN35]}
- {iso: GJ, lgd: 24, name: Gujarat, type: state, capital: Gandhinagar, aliases: [], gdelt_fips: [IN09]}
- {iso: MH, lgd: 27, name: Maharashtra, type: state, capital: Mumbai, aliases: [Bombay], gdelt_fips: [IN16]}
- {iso: AP, lgd: 28, name: Andhra Pradesh, type: state, capital: Amaravati, aliases: [], gdelt_fips: [IN02]}
- {iso: KA, lgd: 29, name: Karnataka, type: state, capital: Bengaluru, aliases: [Mysore], gdelt_fips: [IN19]}
- {iso: GA, lgd: 30, name: Goa, type: state, capital: Panaji, aliases: [], gdelt_fips: [IN33]}
- {iso: LD, lgd: 31, name: Lakshadweep, type: ut, capital: Kavaratti, aliases: [], gdelt_fips: [IN14]}
- {iso: KL, lgd: 32, name: Kerala, type: state, capital: Thiruvananthapuram, aliases: [Keralam], gdelt_fips: [IN13]}
- {iso: TN, lgd: 33, name: Tamil Nadu, type: state, capital: Chennai, aliases: [Madras], gdelt_fips: [IN25]}
- {iso: PY, lgd: 34, name: Puducherry, type: ut, capital: Puducherry, aliases: [Pondicherry], gdelt_fips: [IN22]}
- {iso: AN, lgd: 35, name: Andaman and Nicobar Islands, type: ut, capital: Port Blair, aliases: [Andaman & Nicobar, A&N], gdelt_fips: [IN01]}
- {iso: TS, lgd: 36, name: Telangana, type: state, capital: Hyderabad, aliases: [], gdelt_fips: []}
- {iso: LA, lgd: 37, name: Ladakh, type: ut, capital: Leh, aliases: [], gdelt_fips: []}
- {iso: DH, lgd: 38, name: Dadra and Nagar Haveli and Daman and Diu, type: ut, capital: Daman, aliases: [Daman and Diu, Daman & Diu, Dadra and Nagar Haveli], gdelt_fips: [IN06]}
```

- [ ] **Step 6: Write the loader**

Create `pipeline/iow/core/states.py`:

```python
# pipeline/iow/core/states.py
from functools import cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

STATES_YAML = Path(__file__).resolve().parents[3] / "data" / "in" / "states.yaml"


class State(BaseModel):
    iso: str
    lgd: int
    name: str
    type: Literal["state", "ut"]
    capital: str
    aliases: list[str] = []
    gdelt_fips: list[str] = []


@cache
def load_states() -> list[State]:
    return [State(**row) for row in yaml.safe_load(STATES_YAML.read_text(encoding="utf-8"))]


@cache
def fips_index() -> dict[str, State]:
    """GDELT ADM1 code (e.g. "IN07") -> State."""
    return {code: s for s in load_states() for code in s.gdelt_fips}
```

- [ ] **Step 7: Run tests and see them pass**

Run: `cd pipeline && uv run pytest tests/test_states.py -v`
Expected: 3 passed.

- [ ] **Step 8: Spot-check ISO codes (5 min)**

Open https://en.wikipedia.org/wiki/ISO_3166-2:IN and confirm the 36 `iso` values (28 states + 8 UTs). Already checked on 2026-09-28: all 36 match, including the 2023 changes Odisha `OD`, Chhattisgarh `CG`, Telangana `TS`, Uttarakhand `UK` (was `UT`), plus `DH` and `LA`. Fix any typo and re-run Step 7. This clears the IOW-009 "VERIFY" for ISO codes.

- [ ] **Step 9: Commit**

```bash
git add pipeline data/in/states.yaml
git commit -m "feat: add pipeline project and states.yaml with GDELT crosswalk (IOW-009)"
```

---

### Task B2: GDELT source plugin (IOW-041), about 3 h

Reads GDELT's 15-minute GKG files (`https://data.gdeltproject.org/gdeltv2/<YYYYMMDDHHMMSS>.gkg.csv.zip`). Verified on 2026-09-28: 27 tab-separated columns; the ones used are `1` batch date, `3` outlet domain, `4` article URL, `9` locations, `26` extras XML containing `<PAGE_TITLE>` (all rows) and `<PAGE_PRECISEPUBTIMESTAMP>` (about half the rows). Column 9 entries are `Type#Name#Country#ADM1#Lat#Long#FeatureID` where Type 1 = country, 4 = world city, 5 = world state. About 6 % of rows are kept (3,266 of 54,905 in the 24 h sample). These are static files, so there is no 429 problem, unlike the DOC API.

Why not the DOC 2.0 API (named in IOW-041): its article list documents no location field, so it cannot give the ADM1 codes this slice depends on (D-013). I could not re-check the live DOC response while planning because it was rate-limiting; if you want to confirm, one call is `curl 'https://api.gdeltproject.org/api/v2/doc/doc?query=sourcecountry:india&mode=artlist&maxrecords=1&format=json'` after waiting 5 seconds.

**Files:**
- Create: `pipeline/iow/core/contracts.py`, `pipeline/iow/plugins/sources/gdelt.py`, `pipeline/iow/store.py`, `pipeline/tests/test_gdelt.py`, `pipeline/tests/test_store.py`

**Interfaces:**
- Produces: `RawItem` (spec §5.3 plus `geo_hint: str | None`), `SourcePlugin` protocol, `GdeltSource(client=None).fetch(since, until=None) -> Iterator[RawItem]`, `parse_row(cols) -> RawItem | None`, `primary_adm1(locations) -> str | None`, `batch_stamps(since, until) -> Iterator[str]`, `store.read_all(path=DEFAULT) -> list[RawItem]`, `store.append_new(items, path=DEFAULT) -> int`.
- `geo_hint` is the source-provided ADM1 code of the article's dominant location. Core maps it to a state via `fips_index()` (Task B3). This adds one optional field to the §5.3 contract (D-014).

- [ ] **Step 1: Write the contract**

Create `pipeline/iow/core/contracts.py`:

```python
# pipeline/iow/core/contracts.py
from collections.abc import Iterable
from datetime import datetime
from typing import Literal, Protocol

from pydantic import BaseModel

DisplayPolicy = Literal["headline_link", "snippet_20w", "full_redistribution"]


class RawItem(BaseModel):
    source_id: str
    url: str
    headline: str
    published_at: datetime
    snippet: str | None = None
    lang: str | None = None
    license_id: str
    display_policy: DisplayPolicy
    attribution: str
    geo_hint: str | None = None  # source-provided ADM1 code (GDELT FIPS), e.g. "IN07"


class SourcePlugin(Protocol):
    id: str

    def fetch(self, since: datetime) -> Iterable[RawItem]: ...
```

- [ ] **Step 2: Write the failing tests**

Create `pipeline/tests/test_gdelt.py`:

```python
# pipeline/tests/test_gdelt.py
import io
import zipfile
from datetime import datetime, timezone

import httpx
import pytest

from iow.plugins.sources.gdelt import GdeltSource, batch_stamps, parse_row

MUMBAI = "4#Mumbai, Maharashtra, India#IN#IN16#19.0#72.8#-2092174"
DELHI = "4#New Delhi, Delhi, India#IN#IN07#28.6#77.2#-2106102"
NAGOYA = "4#Nagoya, Aichi, Japan#JA#JA01#35.1#136.9#-237874"
INDIA_ONLY = "1#India#IN#IN#20#77#IN"
INDIA_GENERAL = "5#India (General)#IN#IN00#20#77#IN00"


def row(locs, title="Flood hits city", url="https://www.hindustantimes.com/india-news/a", extras=None):
    cols = [""] * 27
    cols[1] = "20260929013000"
    cols[3] = "hindustantimes.com"
    cols[4] = url
    cols[9] = ";".join(locs)
    cols[26] = extras if extras is not None else f"<PAGE_TITLE>{title}</PAGE_TITLE>"
    return cols


def test_indian_state_article_kept():
    item = parse_row(row([MUMBAI, MUMBAI, DELHI], title="Rain &amp; floods hit Mumbai"))
    assert item.geo_hint == "IN16"
    assert item.headline == "Rain & floods hit Mumbai"
    assert item.source_id == "gdelt" and item.display_policy == "headline_link"
    assert item.published_at == datetime(2026, 9, 29, 1, 30, tzinfo=timezone.utc)


def test_precise_publish_time_preferred():
    extras = "<PAGE_TITLE>T</PAGE_TITLE><PAGE_PRECISEPUBTIMESTAMP>20260928151700</PAGE_PRECISEPUBTIMESTAMP>"
    assert parse_row(row([MUMBAI], extras=extras)).published_at == datetime(
        2026, 9, 28, 15, 17, tzinfo=timezone.utc
    )


def test_foreign_primary_location_dropped():
    assert parse_row(row([NAGOYA, NAGOYA, DELHI])) is None


def test_tie_goes_to_first_seen():
    assert parse_row(row([DELHI, NAGOYA])).geo_hint == "IN07"
    assert parse_row(row([NAGOYA, DELHI])) is None


@pytest.mark.parametrize("locs", [[INDIA_ONLY], [INDIA_GENERAL], []])
def test_no_state_dropped(locs):
    assert parse_row(row(locs)) is None


def test_missing_or_blank_title_dropped():
    assert parse_row(row([MUMBAI], extras="")) is None
    assert parse_row(row([MUMBAI], title="  ")) is None


def test_short_row_dropped():
    assert parse_row(["x"] * 5) is None


def gkg_zip(rows):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("x.gkg.csv", "\n".join("\t".join(r) for r in rows))
    return buf.getvalue()


def test_batch_stamps_floor_to_quarter_hour():
    since = datetime(2026, 9, 29, 1, 7, tzinfo=timezone.utc)
    until = datetime(2026, 9, 29, 1, 40, tzinfo=timezone.utc)
    assert list(batch_stamps(since, until)) == ["20260929010000", "20260929011500", "20260929013000"]


def test_fetch_skips_404_and_parses_the_rest():
    blob = gkg_zip([row([MUMBAI]), row([NAGOYA])])

    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(404) if "010000" in req.url.path else httpx.Response(200, content=blob)

    src = GdeltSource(httpx.Client(transport=httpx.MockTransport(handler)))
    since = datetime(2026, 9, 29, 1, 7, tzinfo=timezone.utc)
    until = datetime(2026, 9, 29, 1, 20, tzinfo=timezone.utc)
    items = list(src.fetch(since, until))
    assert [i.geo_hint for i in items] == ["IN16"]


def test_fetch_fails_loudly_on_server_error():
    src = GdeltSource(httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))))
    since = datetime(2026, 9, 29, 1, 0, tzinfo=timezone.utc)
    with pytest.raises(httpx.HTTPStatusError):
        list(src.fetch(since, since))
```

- [ ] **Step 3: Run and see failure**

Run: `cd pipeline && uv run pytest tests/test_gdelt.py -v`
Expected: collection error `ModuleNotFoundError: No module named 'iow.plugins.sources.gdelt'`.

- [ ] **Step 4: Write the plugin**

Create `pipeline/iow/plugins/sources/gdelt.py`:

```python
# pipeline/iow/plugins/sources/gdelt.py
"""GDELT GKG 2.1 source: one tab-separated zip per 15 minutes.

Not the DOC 2.0 API: that returns no location codes, and this slice needs GDELT's own ADM1 codes.
"""
import csv
import html
import io
import re
import zipfile
from collections import Counter
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone

import httpx

from iow.core.contracts import RawItem

BASE = "https://data.gdeltproject.org/gdeltv2/"
NCOLS = 27
COL_DATE, COL_URL, COL_LOCS, COL_EXTRAS = 1, 4, 9, 26
TITLE = re.compile(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>", re.S)
PUBTS = re.compile(r"<PAGE_PRECISEPUBTIMESTAMP>(\d{14})</PAGE_PRECISEPUBTIMESTAMP>")

csv.field_size_limit(10**9)


def primary_adm1(locations: str) -> str | None:
    """Most frequent ADM1 code across all city/state mentions, any country. Ties go to the first seen."""
    codes = []
    for loc in locations.split(";"):
        f = loc.split("#")
        # Type#Name#Country#ADM1#Lat#Long#FeatureID; type 1 (country) carries no ADM1
        if len(f) >= 7 and f[0] != "1" and len(f[3]) > 2:
            codes.append(f[3])
    if not codes:
        return None
    counts = Counter(codes)
    top = max(counts.values())
    return next(c for c in codes if counts[c] == top)


def _ts(s: str) -> datetime:
    return datetime.strptime(s, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def parse_row(cols: list[str]) -> RawItem | None:
    if len(cols) < NCOLS:
        return None
    adm1 = primary_adm1(cols[COL_LOCS])
    if not adm1 or not adm1.startswith("IN") or adm1 == "IN00":
        return None
    m = TITLE.search(cols[COL_EXTRAS])
    headline = html.unescape(m.group(1)).strip() if m else ""
    if not headline:
        return None
    pub = PUBTS.search(cols[COL_EXTRAS])
    return RawItem(
        source_id="gdelt",
        url=cols[COL_URL],
        headline=headline,
        # ponytail: falls back to the GKG batch time (when GDELT saw it) when no publish timestamp is present
        published_at=_ts(pub.group(1) if pub else cols[COL_DATE]),
        license_id="gdelt-terms",
        display_policy="headline_link",
        attribution="GDELT Project",
        geo_hint=adm1,
    )


def batch_stamps(since: datetime, until: datetime) -> Iterator[str]:
    t = since.astimezone(timezone.utc).replace(second=0, microsecond=0)
    t -= timedelta(minutes=t.minute % 15)
    while t <= until:
        yield t.strftime("%Y%m%d%H%M%S")
        t += timedelta(minutes=15)


def _parse_zip(blob: bytes) -> Iterator[RawItem]:
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        text = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", errors="replace", newline="")
        for cols in csv.reader(text, delimiter="\t", quoting=csv.QUOTE_NONE):
            item = parse_row(cols)
            if item:
                yield item


class GdeltSource:
    id = "gdelt"

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or httpx.Client(timeout=60, follow_redirects=True)

    def fetch(self, since: datetime, until: datetime | None = None) -> Iterator[RawItem]:
        for stamp in batch_stamps(since, until or datetime.now(timezone.utc)):
            r = self.client.get(f"{BASE}{stamp}.gkg.csv.zip")
            if r.status_code == 404:  # slot not published yet, or GDELT skipped it
                continue
            r.raise_for_status()
            yield from _parse_zip(r.content)
```

- [ ] **Step 5: Run and see pass**

Run: `cd pipeline && uv run pytest tests/test_gdelt.py -v`
Expected: 12 passed (including 3 parametrized cases).

- [ ] **Step 6: Write the failing store test**

Create `pipeline/tests/test_store.py`:

```python
# pipeline/tests/test_store.py
from datetime import datetime, timezone

from iow import store
from iow.core.contracts import RawItem


def item(url):
    return RawItem(
        source_id="gdelt", url=url, headline="h", published_at=datetime(2026, 9, 29, tzinfo=timezone.utc),
        license_id="x", display_policy="headline_link", attribution="a", geo_hint="IN07",
    )


def test_append_new_skips_urls_already_stored(tmp_path):
    p = tmp_path / "raw.jsonl"
    assert store.append_new([item("https://a.example/1"), item("https://a.example/1")], p) == 1
    assert store.append_new([item("https://a.example/1"), item("https://a.example/2")], p) == 1
    assert [i.url for i in store.read_all(p)] == ["https://a.example/1", "https://a.example/2"]


def test_read_all_on_missing_file_is_empty(tmp_path):
    assert store.read_all(tmp_path / "nope.jsonl") == []
```

- [ ] **Step 7: Run and see failure, then write the store**

Run: `cd pipeline && uv run pytest tests/test_store.py -v`
Expected: FAIL `ImportError: cannot import name 'store' from 'iow'`.

Create `pipeline/iow/store.py`:

```python
# pipeline/iow/store.py
"""Raw-item store for the first slice: a JSONL file deduped by URL.
ponytail: replaced by the raw_items table when Postgres arrives (IOW-005)."""
from collections.abc import Iterable
from pathlib import Path

from iow.core.contracts import RawItem

DEFAULT = Path(__file__).resolve().parents[1] / "var" / "raw_items.jsonl"


def read_all(path: Path = DEFAULT) -> list[RawItem]:
    if not path.exists():
        return []
    return [RawItem.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def append_new(items: Iterable[RawItem], path: Path = DEFAULT) -> int:
    """Append items whose URL is not stored yet; return how many were added."""
    seen = {i.url for i in read_all(path)}
    fresh = []
    for i in items:
        if i.url not in seen:
            seen.add(i.url)
            fresh.append(i)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for i in fresh:
            f.write(i.model_dump_json() + "\n")
    return len(fresh)
```

Run: `cd pipeline && uv run pytest tests/test_store.py -v`
Expected: 2 passed.

- [ ] **Step 8: Prove it on real data**

Run this one-off (does not touch the store):

```bash
cd pipeline && uv run python - <<'EOF'
from datetime import datetime, timedelta, timezone
from iow.plugins.sources.gdelt import GdeltSource
now = datetime.now(timezone.utc)
items = list(GdeltSource().fetch(now - timedelta(minutes=45)))
print(len(items), "items")
for i in items[:3]:
    print(i.geo_hint, "|", i.published_at.isoformat(), "|", i.headline[:70], "|", i.url[:60])
EOF
```
Expected: tens to a few hundred items depending on the time of day (54 at 02:00 UTC during planning), each with a code like `IN07` and a readable English (or local-language) headline. If it prints `0 items`, check the newest file exists: `curl -s https://data.gdeltproject.org/gdeltv2/lastupdate.txt`.

- [ ] **Step 9: Commit**

```bash
git add pipeline
git commit -m "feat: GDELT GKG source plugin and JSONL store (IOW-041)"
```

---

### Task B3: Exporter, CLI, and geo lookup (IOW-050), about 2 h

Turns stored items into the static JSON the web app reads. File layout follows §6.5: `data/in/summary.json` and `data/in/<iso-lowercase>/issues.json`. `origin_count` is always 1 until dedup exists.

**Files:**
- Create: `pipeline/iow/stages/export.py`, `pipeline/iow/cli.py`, `pipeline/tests/test_export.py`

**Interfaces:**
- Consumes: `RawItem`, `fips_index()`, `load_states()` (B1, B2); `store.read_all`, `store.append_new`, `GdeltSource.fetch` (B2).
- Produces: `export(items, out_dir, now) -> dict[str, int]` (ISO code → card count); `card(item) -> dict`; `outlet(url) -> str`; the JSON schema below; CLI `iow fetch [--hours N]` and `iow export --out DIR`.

Schema (both files also carry `schema_version: 1` and `generated_at`):

```
summary.json: {"states": [{"iso","lgd","name","count"}, ... 36 entries]}
<iso>/issues.json: {"state": "MH", "issues": [{"id","headline","outlet","published_at","url","origin_count"}, ...]}
```

- [ ] **Step 1: Write the failing tests**

Create `pipeline/tests/test_export.py`:

```python
# pipeline/tests/test_export.py
import json
from datetime import datetime, timedelta, timezone

from iow.core.contracts import RawItem
from iow.stages.export import card, export, outlet

NOW = datetime(2026, 9, 29, tzinfo=timezone.utc)


def item(url="https://www.thehindu.com/a", hint="IN16", policy="headline_link", snippet=None, age_h=1):
    return RawItem(
        source_id="gdelt", url=url, headline="Headline", published_at=NOW - timedelta(hours=age_h),
        snippet=snippet, license_id="x", display_policy=policy, attribution="a", geo_hint=hint,
    )


def read(out, *parts):
    return json.loads((out.joinpath("data", "in", *parts)).read_text())


def test_writes_summary_and_one_file_per_state(tmp_path):
    counts = export([item(hint="IN16"), item("https://x.example/2", hint="IN07")], tmp_path, NOW)
    summary = read(tmp_path, "summary.json")
    assert summary["schema_version"] == 1
    assert summary["generated_at"] == "2026-09-29T00:00:00+00:00"
    assert len(summary["states"]) == 36
    by = {s["iso"]: s for s in summary["states"]}
    assert by["MH"]["count"] == 1 and by["DL"]["count"] == 1 and by["KL"]["count"] == 0
    assert by["MH"]["lgd"] == 27
    assert counts["MH"] == 1
    assert len(list((tmp_path / "data" / "in").glob("*/issues.json"))) == 36
    assert read(tmp_path, "kl", "issues.json")["issues"] == []  # empty state still has a file


def test_card_fields_and_outlet(tmp_path):
    export([item()], tmp_path, NOW)
    c = read(tmp_path, "mh", "issues.json")["issues"][0]
    assert set(c) == {"id", "headline", "outlet", "published_at", "url", "origin_count"}
    assert c["outlet"] == "thehindu.com"  # "www." stripped
    assert c["origin_count"] == 1


def test_display_policy_blocks_snippet():
    assert "snippet" not in card(item(snippet="secret words", policy="headline_link"))
    long = " ".join(f"w{i}" for i in range(50))
    assert len(card(item(snippet=long, policy="snippet_20w"))["snippet"].split()) == 20


def test_duplicate_url_once_and_newest_first(tmp_path):
    export([item("https://a.example/old", age_h=5), item("https://a.example/new", age_h=1),
            item("https://a.example/new", age_h=1)], tmp_path, NOW)
    urls = [c["url"] for c in read(tmp_path, "mh", "issues.json")["issues"]]
    assert urls == ["https://a.example/new", "https://a.example/old"]


def test_unsafe_scheme_dropped(tmp_path):
    export([item("javascript:alert(1)"), item("ftp://x.example/f")], tmp_path, NOW)
    assert read(tmp_path, "mh", "issues.json")["issues"] == []


def test_unmapped_or_missing_hint_dropped(tmp_path):
    items = [
        item(hint="IN00"),
        item("https://a.example/2", hint=None),
        item("https://a.example/3", hint="XX01"),
    ]
    assert sum(export(items, tmp_path, NOW).values()) == 0


def test_outlet_handles_odd_urls():
    assert outlet("https://sub.example.co.in/x") == "sub.example.co.in"
    assert outlet("not a url") == ""
```

- [ ] **Step 2: Run and see failure**

Run: `cd pipeline && uv run pytest tests/test_export.py -v`
Expected: collection error `ModuleNotFoundError: No module named 'iow.stages.export'`.

- [ ] **Step 3: Write the exporter**

Create `pipeline/iow/stages/export.py`:

```python
# pipeline/iow/stages/export.py
import hashlib
import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from iow.core.contracts import RawItem
from iow.core.states import fips_index, load_states

SCHEMA_VERSION = 1
MAX_PER_STATE = 100  # ponytail: newest 100 per state; paginate when one file gets too big


def outlet(url: str) -> str:
    return (urlparse(url).hostname or "").removeprefix("www.")


def card(item: RawItem) -> dict:
    """One card. Fields beyond headline/outlet/date/link exist only when display_policy allows them."""
    d = {
        "id": hashlib.sha1(item.url.encode()).hexdigest()[:12],
        "headline": item.headline,
        "outlet": outlet(item.url),
        "published_at": item.published_at.isoformat(),
        "url": item.url,
        "origin_count": 1,  # ponytail: no wire/near-duplicate detection yet (IOW-046); each article is its own origin
    }
    if item.display_policy != "headline_link" and item.snippet:
        d["snippet"] = " ".join(item.snippet.split()[:20])
    return d


def _write(path: Path, payload: dict, now: datetime) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"schema_version": SCHEMA_VERSION, "generated_at": now.isoformat(), **payload}
    path.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def export(items: Iterable[RawItem], out_dir: Path, now: datetime) -> dict[str, int]:
    """Write summary.json and one issues.json per state under out_dir/data/in. Returns card counts by ISO code."""
    fips = fips_index()
    states = load_states()
    by_state: dict[str, dict[str, RawItem]] = {s.iso: {} for s in states}
    for it in items:
        state = fips.get(it.geo_hint or "")
        if state is None or urlparse(it.url).scheme not in ("http", "https"):
            continue
        by_state[state.iso].setdefault(it.url, it)

    root = out_dir / "data" / "in"
    counts: dict[str, int] = {}
    for s in states:
        newest = sorted(by_state[s.iso].values(), key=lambda i: i.published_at, reverse=True)[:MAX_PER_STATE]
        counts[s.iso] = len(newest)
        _write(root / s.iso.lower() / "issues.json", {"state": s.iso, "issues": [card(i) for i in newest]}, now)
    summary = [{"iso": s.iso, "lgd": s.lgd, "name": s.name, "count": counts[s.iso]} for s in states]
    _write(root / "summary.json", {"states": summary}, now)
    return counts
```

- [ ] **Step 4: Run and see pass**

Run: `cd pipeline && uv run pytest tests/test_export.py -v`
Expected: 7 passed.

- [ ] **Step 5: Write the CLI**

Create `pipeline/iow/cli.py`:

```python
# pipeline/iow/cli.py
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from iow import store
from iow.plugins.sources.gdelt import GdeltSource
from iow.stages.export import export


def main() -> None:
    p = argparse.ArgumentParser(prog="iow")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="pull recent GDELT articles into the local store")
    f.add_argument("--hours", type=float, default=3)
    e = sub.add_parser("export", help="write static JSON for the web app")
    e.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    now = datetime.now(timezone.utc)
    if args.cmd == "fetch":
        added = store.append_new(GdeltSource().fetch(now - timedelta(hours=args.hours)))
        print(f"stored {added} new items")
    else:
        counts = export(store.read_all(), args.out, now)
        print(f"exported {sum(counts.values())} cards across {sum(1 for c in counts.values() if c)} states")
```

- [ ] **Step 6: Run the whole suite plus lint**

Run: `cd pipeline && uv run pytest && uv run ruff check .`
Expected: 24 tests pass; ruff prints `All checks passed!`. (If ruff reports import-order (`I001`) issues, run `uv run ruff check . --fix` once.)

- [ ] **Step 7: Run it for real**

```bash
cd pipeline
uv run iow fetch --hours 6
uv run iow export --out ../apps/web/public
ls ../apps/web/public/data/in | head -5
```
Expected: `stored N new items` with N in the hundreds or more; `exported M cards across K states` with K ≥ 15 (the full 24 h sample reached 32 states); running `uv run iow fetch --hours 6` a second time prints `stored 0 new items`; the directory listing shows `summary.json` and state folders like `ap`, `br`. Then `python3 -c "import json;d=json.load(open('../apps/web/public/data/in/dl/issues.json'));print(len(d['issues']), d['issues'][0])"` shows a real card. (First fetch downloads about 24 files × 3.7 MB.)

- [ ] **Step 8: Commit**

```bash
git add pipeline
git commit -m "feat: static JSON exporter with display_policy enforcement and CLI (IOW-050)"
```

---

### Task B4: State tiles on R2 (IOW-020, IOW-022), about 2 h

The repo already publishes ready-made PMTiles, so nothing is built. Verified on 2026-09-28: `SOI_States.pmtiles` is 5.6 MB, zoom 0-11, one vector layer named `SOI_States`, properties `STATE`, `State_LGD`, `STATE_C`; 40 features = 36 states + 4 "DISPUTED" sliver polygons with `State_LGD = 0`. License of release files: CC0. Source: Survey of India.

**Files:**
- Create: `docs/DATA_LICENSES.md`, `tiles/cors.json`
- Uses (gitignored): `tiles/SOI_States.pmtiles`

- [ ] **Step 1: Download**

```bash
mkdir -p tiles
gh release download admin/states -R yashveeeeeeer/india-geodata -p SOI_States.pmtiles -D tiles --clobber
shasum -a 256 tiles/SOI_States.pmtiles
```
Expected: a ~5.6 MB file. Copy the SHA-256.

- [ ] **Step 2: Confirm layer and properties (guards against the file changing upstream)**

```bash
uv run --quiet --with pmtiles --with mapbox-vector-tile python - <<'EOF'
import gzip
from pmtiles.reader import Reader, MmapSource
import mapbox_vector_tile as mvt
with open("tiles/SOI_States.pmtiles", "rb") as f:
    r = Reader(MmapSource(f))
    layer = mvt.decode(gzip.decompress(r.get(0, 0, 0)))["SOI_States"]
    lgd = sorted({x["properties"]["State_LGD"] for x in layer["features"]})
    print(len(layer["features"]), "features; LGD codes:", lgd)
EOF
```
Expected: `40 features; LGD codes: [0, 1, 2, ..., 24, 27, ..., 38]`.

- [ ] **Step 3: Record data licenses (IOW-020 done-when)**

Create `docs/DATA_LICENSES.md` (replace `<sha256>` with the value from Step 1):

```markdown
# Data licenses and attribution

| Data | Source | License | Used for |
|---|---|---|---|
| `SOI_States.pmtiles` (India state boundaries) | [yashveeeeeeer/india-geodata](https://github.com/yashveeeeeeer/india-geodata), release tag `admin/states`; underlying data © Survey of India | CC0-1.0 (release files, per the repo's `states/README.md`) | State polygons. SHA-256 `<sha256>`, downloaded 2026-09-28 |
| GDELT GKG 2.1 | [The GDELT Project](https://www.gdeltproject.org/) | Free and open; attribution required | Article discovery and ADM1 location codes |
| Basemap | [OpenFreeMap](https://openfreemap.org/) style "liberty", data © OpenStreetMap contributors (ODbL) | ODbL | Basemap only. All its boundary layers are hidden (see plan §4.1) |

Still to verify (plan §16): OpenFreeMap usage terms; per-file SoI provenance for the tiles.
```

- [ ] **Step 4: Create the R2 bucket (manual, needs your Cloudflare login)**

```bash
npx wrangler login
npx wrangler r2 bucket create iow-tiles
npx wrangler r2 bucket dev-url enable iow-tiles
```
The last command prints a public URL like `https://pub-<hash>.r2.dev`. Copy it. (r2.dev URLs are rate-limited and meant for development; a custom domain replaces it when the site is deployed, IOW-036.)

- [ ] **Step 5: Set CORS so range requests work from the dev server**

Create `tiles/cors.json`:

```json
{
  "rules": [
    {
      "allowed": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "HEAD"],
        "headers": ["range", "if-match"]
      },
      "exposeHeaders": ["etag", "content-length", "content-range"],
      "maxAgeSeconds": 3600
    }
  ]
}
```

Run: `npx wrangler r2 bucket cors set iow-tiles --file tiles/cors.json`

The `rules` / `allowed` shape is the one the Cloudflare R2 CORS docs give for wrangler. If wrangler still rejects it, set the same rule in the dashboard instead: R2 → `iow-tiles` → Settings → CORS policy → add, using the dashboard's own format:

```json
[{"AllowedOrigins": ["http://localhost:5173"], "AllowedMethods": ["GET", "HEAD"], "AllowedHeaders": ["range", "if-match"], "ExposeHeaders": ["etag", "content-length", "content-range"], "MaxAgeSeconds": 3600}]
```

- [ ] **Step 6: Upload (note `--remote`; wrangler writes to a local emulator otherwise)**

```bash
npx wrangler r2 object put iow-tiles/in_adm1.pmtiles --file tiles/SOI_States.pmtiles \
  --content-type application/octet-stream --remote
```

- [ ] **Step 7: Verify range requests and CORS**

```bash
URL=https://pub-<hash>.r2.dev/in_adm1.pmtiles   # your URL from Step 4
curl -s -o /dev/null -D - -H 'Origin: http://localhost:5173' -H 'Range: bytes=0-16383' "$URL" | grep -iE '^(HTTP|content-range|access-control-allow-origin|accept-ranges)'
```
Expected: `HTTP/2 206`, a `content-range: bytes 0-16383/...` line, and `access-control-allow-origin: http://localhost:5173`. A `200` instead of `206` means ranges are not honoured; recheck the URL.

- [ ] **Step 8: Save the URL for the web app and commit**

Note the URL for Task B5 (`VITE_TILES_URL`).

```bash
git add docs/DATA_LICENSES.md tiles/cors.json
git commit -m "feat: SoI state tiles on R2 and data license record (IOW-020, IOW-022)"
```

---

### Task B5: Web scaffold and data loader, about 1 h

**Files:**
- Create: `apps/web/` (Vite template), `apps/web/src/lib/data.ts`, `apps/web/src/lib/data.test.ts`, `apps/web/.env.local`, `apps/web/.env.example`

**Interfaces:**
- Produces: `StateSummary {iso, lgd, name, count}`, `Card {id, headline, outlet, published_at, url, origin_count}`, `loadSummary(): Promise<StateSummary[]>`, `loadCards(iso: string): Promise<Card[]>`, `safeHref(url: string): string`.

- [ ] **Step 1: Scaffold**

```bash
mkdir -p apps
npm create vite@latest apps/web -- --template react-ts --no-interactive
cd apps/web && npm install
npm install maplibre-gl@5 pmtiles
npm install -D vitest
```
Pin `maplibre-gl@5`: plain `npm install maplibre-gl` now installs 6.x, which has no default export, and `MapView.tsx` fails to compile (`TS1192: ... has no default export`). The spec says 5.x (§6.1, D-001); this was checked with 5.24.0. The template (checked 2026-09-28) ships React 19, Vite 8, TypeScript 6, and `oxlint` as `npm run lint`. Swapping it for Biome is IOW-004, not this slice.

- [ ] **Step 2: Add the test script and env files**

In `apps/web/package.json` add to `"scripts"`: `"test": "vitest run"`.

Create `apps/web/.env.local` (gitignored by the template's `*.local` rule), with the URL from B4:

```
VITE_TILES_URL=https://pub-<hash>.r2.dev/in_adm1.pmtiles
```

Create `apps/web/.env.example`:

```
VITE_TILES_URL=
```

- [ ] **Step 3: Write the failing test**

Create `apps/web/src/lib/data.test.ts`:

```ts
// apps/web/src/lib/data.test.ts
import { afterEach, expect, test, vi } from "vitest";
import { loadCards, safeHref } from "./data";

const stub = (body: unknown, ok = true, status = 200) =>
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok, status, json: async () => body }));

afterEach(() => vi.unstubAllGlobals());

test("loadCards returns the issues array from the lowercase state path", async () => {
  stub({ schema_version: 1, issues: [{ id: "a" }] });
  expect(await loadCards("MH")).toEqual([{ id: "a" }]);
  expect(fetch).toHaveBeenCalledWith("/data/in/mh/issues.json");
});

test("rejects an unknown schema_version", async () => {
  stub({ schema_version: 2, issues: [] });
  await expect(loadCards("MH")).rejects.toThrow(/schema_version/);
});

test("rejects HTTP errors", async () => {
  stub({}, false, 404);
  await expect(loadCards("MH")).rejects.toThrow(/404/);
});

test("safeHref only lets http(s) links through", () => {
  expect(safeHref("javascript:alert(1)")).toBe("#");
  expect(safeHref("data:text/html,x")).toBe("#");
  expect(safeHref("https://a.example/x")).toBe("https://a.example/x");
});
```

- [ ] **Step 4: Run and see failure**

Run: `cd apps/web && npm test`
Expected: FAIL, cannot resolve `./data`.

- [ ] **Step 5: Write the loader**

Create `apps/web/src/lib/data.ts`:

```ts
// apps/web/src/lib/data.ts
export type StateSummary = { iso: string; lgd: number; name: string; count: number };
export type Card = {
  id: string;
  headline: string;
  outlet: string;
  published_at: string;
  url: string;
  origin_count: number;
};

const SCHEMA_VERSION = 1;
const BASE = import.meta.env.VITE_DATA_BASE ?? "/data";

async function getJson(path: string): Promise<Record<string, unknown>> {
  const res = await fetch(`${BASE}/${path}`);
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
  const doc = await res.json();
  if (doc.schema_version !== SCHEMA_VERSION) {
    throw new Error(`${path}: unsupported schema_version ${doc.schema_version}`);
  }
  return doc;
}

export async function loadSummary(): Promise<StateSummary[]> {
  return (await getJson("in/summary.json")).states as StateSummary[];
}

export async function loadCards(iso: string): Promise<Card[]> {
  return (await getJson(`in/${iso.toLowerCase()}/issues.json`)).issues as Card[];
}

/** Links come from third-party feeds; only http(s) may become an href. */
export function safeHref(url: string): string {
  return /^https?:\/\//i.test(url) ? url : "#";
}
```

- [ ] **Step 6: Run and see pass**

Run: `cd apps/web && npm test`
Expected: 4 passed.

- [ ] **Step 7: Confirm the app still builds**

Run: `cd apps/web && npm run build`
Expected: exits 0 (the untouched template still compiles).

- [ ] **Step 8: Commit**

```bash
git add apps/web .gitignore
git commit -m "feat: web scaffold and typed data loader with schema check"
```

---

### Task B6: Globe with clickable states (IOW-030, IOW-031), about 3 h

Verified API notes (MapLibre 5 docs): globe is enabled with `map.setProjection({ type: "globe" })` after `style.load`; the PMTiles protocol is registered once with `maplibregl.addProtocol("pmtiles", new Protocol().tile)`; a vector source URL is `pmtiles://<https url>`; `promoteId` can be an object mapping a source-layer to a property, which makes `State_LGD` the feature id so `setFeatureState` works; `setFeatureState` on a vector source needs `sourceLayer`.

Compliance handling: all basemap layers whose `source-layer` is `boundary` (the OpenMapTiles boundary layer, which carries country, state, and disputed lines) are hidden. Only our SoI polygons draw borders. The four `State_LGD = 0` sliver polygons are filtered out.

**Files:**
- Create: `apps/web/src/map/MapView.tsx`
- Modify: `apps/web/src/App.tsx`, `apps/web/src/App.css`, `apps/web/src/index.css`

**Interfaces:**
- Consumes: `StateSummary`, `loadSummary` (B5); `VITE_TILES_URL`.
- Produces: `<MapView selected={number|null} onSelect={(lgd: number|null) => void} />`. `selected` is a `State_LGD`. In dev builds the map is also exposed as `window.__map` for browser checks.

- [ ] **Step 1: Write the map component**

Create `apps/web/src/map/MapView.tsx`:

```tsx
// apps/web/src/map/MapView.tsx
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { Protocol } from "pmtiles";
import { useEffect, useRef } from "react";

const TILES_URL = import.meta.env.VITE_TILES_URL as string;
const STYLE_URL = "https://tiles.openfreemap.org/styles/liberty";
const SOURCE = "in_states";
const SOURCE_LAYER = "SOI_States";
const FILL = "in-fill";

maplibregl.addProtocol("pmtiles", new Protocol().tile);

type Props = { selected: number | null; onSelect: (lgd: number | null) => void };

export function MapView({ selected, onSelect }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const onSelectRef = useRef(onSelect);
  useEffect(() => {
    onSelectRef.current = onSelect;
  });
  const shown = useRef<number | null>(null); // feature currently marked selected

  useEffect(() => {
    const map = new maplibregl.Map({
      container: container.current!,
      style: STYLE_URL,
      center: [79, 22],
      zoom: 3,
    });
    mapRef.current = map;
    if (import.meta.env.DEV) (window as unknown as { __map: maplibregl.Map }).__map = map;

    map.on("style.load", () => {
      map.setProjection({ type: "globe" });

      // Compliance (plan §4.1): never show the basemap's own borders. Only SoI-aligned states are drawn.
      for (const layer of map.getStyle().layers) {
        if ("source-layer" in layer && layer["source-layer"] === "boundary") {
          map.setLayoutProperty(layer.id, "visibility", "none");
        }
      }

      map.addSource(SOURCE, {
        type: "vector",
        url: `pmtiles://${TILES_URL}`,
        promoteId: { [SOURCE_LAYER]: "State_LGD" },
      });
      // State_LGD 0 = the four inter-state "DISPUTED" sliver polygons; they are not states.
      const filter: maplibregl.FilterSpecification = [">", ["get", "State_LGD"], 0];
      map.addLayer({
        id: FILL,
        type: "fill",
        source: SOURCE,
        "source-layer": SOURCE_LAYER,
        filter,
        paint: {
          "fill-color": "#3b6ea5",
          "fill-opacity": [
            "case",
            ["boolean", ["feature-state", "selected"], false], 0.7,
            ["boolean", ["feature-state", "hover"], false], 0.5,
            0.25,
          ],
        },
      });
      map.addLayer({
        id: "in-line",
        type: "line",
        source: SOURCE,
        "source-layer": SOURCE_LAYER,
        filter,
        paint: { "line-color": "#1d3557", "line-width": 0.8 },
      });

      const target = (id: number) => ({ source: SOURCE, sourceLayer: SOURCE_LAYER, id });
      let hovered: number | null = null;
      map.on("mousemove", FILL, (e) => {
        const id = e.features?.[0]?.id as number | undefined;
        if (id === undefined || id === hovered) return;
        if (hovered !== null) map.setFeatureState(target(hovered), { hover: false });
        hovered = id;
        map.setFeatureState(target(id), { hover: true });
        map.getCanvas().style.cursor = "pointer";
      });
      map.on("mouseleave", FILL, () => {
        if (hovered !== null) map.setFeatureState(target(hovered), { hover: false });
        hovered = null;
        map.getCanvas().style.cursor = "";
      });
      map.on("click", (e) => {
        const f = map.queryRenderedFeatures(e.point, { layers: [FILL] })[0];
        onSelectRef.current((f?.id as number | undefined) ?? null);
      });
    });

    return () => map.remove();
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const set = (id: number, on: boolean) =>
      map.setFeatureState({ source: SOURCE, sourceLayer: SOURCE_LAYER, id }, { selected: on });
    if (shown.current !== null) set(shown.current, false);
    if (selected !== null) set(selected, true);
    shown.current = selected;
  }, [selected]);

  return <div ref={container} className="map" />;
}
```

- [ ] **Step 2: Wire it into the app (panel comes in B7)**

Replace `apps/web/src/App.tsx`:

```tsx
// apps/web/src/App.tsx
import { useState } from "react";
import "./App.css";
import { MapView } from "./map/MapView";

export default function App() {
  const [selected, setSelected] = useState<number | null>(null);
  return (
    <div className="app">
      <MapView selected={selected} onSelect={setSelected} />
    </div>
  );
}
```

Replace `apps/web/src/index.css`:

```css
html, body, #root { height: 100%; margin: 0; }
body { font-family: system-ui, sans-serif; }
```

Replace `apps/web/src/App.css`:

```css
.app { position: relative; height: 100%; }
/* Two classes on purpose: maplibre-gl.css loads later and its `.maplibregl-map { position: relative }`
   would win over a single `.map`, collapsing the map to 0 px height so clicks never reach it. */
.app .map { position: absolute; inset: 0; }
```

- [ ] **Step 3: Confirm it type-checks and lints**

Run: `cd apps/web && npm run build && npm run lint`
Expected: build exits 0; oxlint reports no warnings.

- [ ] **Step 4: Run and look**

Run: `cd apps/web && npm run dev` (leave running). Open http://localhost:5173.
Expected: a globe centred near India, India's states tinted blue with dark outlines, no other country borders anywhere on the globe.

- [ ] **Step 5: Machine-check the four IOW-030/031 conditions in the browser**

With the dev server running, use the Playwright tools: navigate to `http://localhost:5173`, wait 5 s, then evaluate:

```js
() => {
  const m = window.__map;
  const visibleBoundary = m.getStyle().layers.filter(
    l => l["source-layer"] === "boundary" && (l.layout?.visibility ?? "visible") !== "none").length;
  const p = m.project([77.2, 28.6]); // Delhi
  return {
    projection: m.getProjection?.().type ?? m.getStyle().projection?.type,
    visibleBoundaryLayers: visibleBoundary,
    hasStateSource: !!m.getSource("in_states"),
    delhiFeatures: m.queryRenderedFeatures([p.x, p.y], { layers: ["in-fill"] }).map(f => f.id),
    delhiPixel: [Math.round(p.x), Math.round(p.y)],
  };
}
```
Expected: `projection: "globe"`, `visibleBoundaryLayers: 0`, `hasStateSource: true`, `delhiFeatures: [7]` (all four seen during planning at a 1280×800 viewport). If `delhiFeatures` is empty, zoom in once (`m.setZoom(4)`) and retry: the point may be off-screen. Also confirm the canvas fills the window: `document.querySelector("canvas.maplibregl-canvas").getBoundingClientRect().height` equals the window height. A value of `300` means the CSS in Step 2 was not applied.

Then click that pixel (`page.mouse.click(x, y)` via the run-code tool with `delhiPixel`) and evaluate `window.__map.getFeatureState({source:"in_states",sourceLayer:"SOI_States",id:7})`.
Expected: `{ "selected": true, ... }`. Hover over another state first and confirm its fill gets more opaque (0.5 vs 0.25).

- [ ] **Step 6: Eyeball the disputed regions and the basemap labels (plan §16, risk in §13)**

Take a screenshot zoomed on J&K / Ladakh and on Arunachal Pradesh. Confirm: SoI outline is drawn, no second dashed border, and note which place names the basemap labels show in these areas. Write findings into a scratch note; they go into `docs/DECISIONS.md` in B8. This is not the formal QA (IOW-023), so nothing here is public.

- [ ] **Step 7: Commit**

```bash
git add apps/web
git commit -m "feat: MapLibre globe with clickable SoI state layer (IOW-030, IOW-031)"
```

---

### Task B7: State panel with plain headlines (IOW-033), about 1.5 h

**Files:**
- Create: `apps/web/src/panel/StatePanel.tsx`
- Modify: `apps/web/src/App.tsx`, `apps/web/src/App.css`

**Interfaces:**
- Consumes: `loadSummary`, `loadCards`, `safeHref`, `StateSummary`, `Card` (B5); `<MapView>` (B6).
- Produces: `<StatePanel state={StateSummary} onClose={() => void} />`.

- [ ] **Step 1: Write the panel**

Create `apps/web/src/panel/StatePanel.tsx`:

```tsx
// apps/web/src/panel/StatePanel.tsx
import { useEffect, useState } from "react";
import { type Card, type StateSummary, loadCards, safeHref } from "../lib/data";

type Props = { state: StateSummary; onClose: () => void };

export function StatePanel({ state, onClose }: Props) {
  const [cards, setCards] = useState<Card[] | "error" | null>(null);

  // App remounts this component per state (key={state.iso}), so `cards` starts at null for each state.
  useEffect(() => {
    let live = true;
    loadCards(state.iso)
      .then((c) => live && setCards(c))
      .catch(() => live && setCards("error"));
    return () => {
      live = false;
    };
  }, [state.iso]);

  return (
    <aside className="panel">
      <button className="close" onClick={onClose} aria-label="Close panel">
        ×
      </button>
      <h2>{state.name}</h2>
      <p className="note">
        Stories are placed on the map automatically from GDELT location tags and can be wrong.
      </p>
      {cards === null && <p>Loading…</p>}
      {cards === "error" && <p role="alert">Couldn't load stories for {state.name}.</p>}
      {Array.isArray(cards) && cards.length === 0 && <p>No stories yet.</p>}
      {Array.isArray(cards) && (
        <ul className="cards">
          {cards.map((c) => (
            <li key={c.id}>
              <a href={safeHref(c.url)} target="_blank" rel="noopener noreferrer">
                {c.headline}
              </a>
              <div className="meta">
                {c.outlet} · {new Date(c.published_at).toLocaleString()}
              </div>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
```

`origin_count` is deliberately not shown: with no dedup yet, "1 source" on every card would claim independence that has not been checked.

- [ ] **Step 2: Wire it into the app**

Replace `apps/web/src/App.tsx`:

```tsx
// apps/web/src/App.tsx
import { useEffect, useState } from "react";
import "./App.css";
import { type StateSummary, loadSummary } from "./lib/data";
import { MapView } from "./map/MapView";
import { StatePanel } from "./panel/StatePanel";

export default function App() {
  const [states, setStates] = useState<StateSummary[]>([]);
  const [selected, setSelected] = useState<number | null>(null);

  useEffect(() => {
    loadSummary().then(setStates).catch(console.error);
  }, []);

  const current = states.find((s) => s.lgd === selected) ?? null;
  return (
    <div className="app">
      <MapView selected={selected} onSelect={setSelected} />
      {current && <StatePanel key={current.iso} state={current} onClose={() => setSelected(null)} />}
    </div>
  );
}
```

- [ ] **Step 3: Style the panel**

Append to `apps/web/src/App.css`:

```css
.panel {
  position: absolute; top: 0; right: 0; bottom: 0; width: min(380px, 100%);
  overflow-y: auto; box-sizing: border-box; padding: 16px;
  background: #fff; color: #111; box-shadow: -2px 0 12px rgba(0, 0, 0, 0.25);
}
.panel h2 { margin: 0 32px 8px 0; }
.panel .note { font-size: 12px; color: #555; margin: 0 0 12px; }
.panel .close { position: absolute; top: 8px; right: 12px; font-size: 24px; border: 0; background: none; cursor: pointer; }
.cards { list-style: none; margin: 0; padding: 0; }
.cards li { padding: 10px 0; border-top: 1px solid #ddd; }
.cards a { color: #0b3d91; font-weight: 600; text-decoration: none; }
.cards a:hover { text-decoration: underline; }
.cards .meta { margin-top: 2px; font-size: 12px; color: #555; }
```

- [ ] **Step 4: Build and unit tests**

Run: `cd apps/web && npm run build && npm test && npm run lint`
Expected: build exits 0; 4 tests pass; oxlint reports no warnings.

- [ ] **Step 5: Check it in the browser**

With `npm run dev` running and the JSON from Task B3 in `apps/web/public/data/`, use the Playwright tools: navigate to `http://localhost:5173`, click Maharashtra (project `[75.7, 19.7]` with `window.__map.project(...)` and click there), then snapshot.
Expected: a right-hand panel titled "Maharashtra" with several headline links, each with `outlet · date`. Click on the sea (project `[70, 15]` clicks off-land) and confirm the panel closes.
Also click Telangana (`[79, 17.9]`): expect "No stories yet." (known gap, D-016).
Finally check links: `document.querySelectorAll('.cards a')[0].getAttribute('rel')` is `noopener noreferrer`.

- [ ] **Step 6: Commit**

```bash
git add apps/web
git commit -m "feat: state panel listing exported headlines (IOW-033)"
```

---

### Task B8: End-to-end check and decision log, about 1 h

**Files:**
- Create: `docs/DECISIONS.md`

- [ ] **Step 1: Fresh end-to-end run**

```bash
rm -rf pipeline/var apps/web/public/data
cd pipeline && uv run pytest && uv run iow fetch --hours 6 && uv run iow export --out ../apps/web/public
cd ../apps/web && npm test && npm run build
```
Expected: all green; `stored N new items`; `exported M cards across K states`.

- [ ] **Step 2: Slice acceptance in the browser**

`npm run dev`, then confirm each:
1. Globe renders with India's states and no other borders (B6 Step 5 conditions still hold).
2. Hover lightens a state; click selects it and opens the panel.
3. The panel shows real headlines with outlet and date; links open the article in a new tab.
4. Closing the panel or clicking off-land clears the selection.

- [ ] **Step 3: Write the decision log**

Create `docs/DECISIONS.md` (the D-001…D-012 log lives in the project plan §14 until IOW-012 copies it here; decisions made from now on are recorded below):

```markdown
# Decisions

D-001 to D-012: see project plan §14 (to be transcribed here under IOW-012).

| ID | Decision | Alternatives | Reason |
|---|---|---|---|
| D-013 | GDELT source reads GKG 2.1 files, not the DOC 2.0 API | DOC 2.0 (named in IOW-041) | GKG rows carry FIPS ADM1 codes and page titles; DOC article lists document no location field. Static files also avoid the 1-request-per-5-seconds limit. |
| D-014 | `RawItem` gets optional `geo_hint` (source-provided ADM1 code) | Resolve state inside the plugin | Keeps the crosswalk (`states.yaml`) in core; plugin only reports what the source says. |
| D-015 | Use the prebuilt `SOI_States.pmtiles` release asset; no tippecanoe build | Build from GeoJSON with mapshaper + tippecanoe (IOW-020/022 as written) | Same SoI data, already tiled, CC0, joins on `State_LGD`. Build toolchain returns with IOW-021 (world ADM0). |
| D-016 | GDELT codes are the only geoparsing for now; accept Telangana → Andhra Pradesh and Ladakh → Jammu & Kashmir | Add a name gazetteer now | GDELT's gazetteer predates both states (147 Hyderabad mentions in 24 h all carried `IN02`). Gazetteer fallback arrives with IOW-047. |
| D-017 | No database in the first slice; JSONL store deduped by URL | Postgres + pgvector now (IOW-005) | Nothing in the slice needs queries or vectors. |
| D-018 | The web app stays local-only until IOW-021 and IOW-023 are done | Deploy the slice | No world ADM0 layer and no boundary QA yet (plan §4.1). |
| D-019 | Hide every basemap layer with `source-layer = boundary` | Hide only admin-level-2 and disputed layers by ID | Robust to style changes; our SoI polygons are the only borders drawn. Revisit if state lines are wanted elsewhere. |
| D-020 | Pin `maplibre-gl@5` | Move to 6.x (npm `latest` since the spec was written) | The spec says 5.x (D-001). 6.x drops the default export, so moving would be a migration. Revisit at IOW-109. |

## Notes from B6 basemap check
<!-- paste what the basemap labelled in J&K / Ladakh / Arunachal here -->
```

Replace the HTML comment line with what you actually saw in B6 Step 6.

- [ ] **Step 4: Commit and push**

```bash
git add docs/DECISIONS.md
git commit -m "docs: record first-slice decisions D-013 to D-020"
git push origin main
```

Done when: the four acceptance checks in Step 2 pass and `git status` is clean.

---

## Self-review

**Spec coverage:** IOW-001 (A1), IOW-006 (A2), IOW-007 (A3), IOW-008 (A4), IOW-009 (B1), IOW-020 + IOW-022 (B4), IOW-030 + IOW-031 (B6), IOW-041 (B2), IOW-050 (B3), IOW-033 (B7). Every "done when" in the spec maps to a step: license recorded (B4 S3), tiles via range requests (B4 S7), globe renders with no basemap borders (B6 S5), hover/click (B6 S5), hourly fetch without 429 (static files, B2 S8; the hourly cron itself is IOW-051, out of scope), contract test on leaked fields (B3 `test_display_policy_blocks_snippet`), panel renders from `issues.json` (B7 S5).

**Deviations from the spec, all logged:** D-013 (GKG vs DOC), D-014 (`geo_hint`), D-015 (prebuilt tiles), D-017 (no DB), D-019 (hide all boundary layers), D-020 (pin `maplibre-gl@5`). Unlisted-but-needed: minimal `pipeline/` project (part of IOW-003) and `apps/web` scaffold (part of IOW-004).

**Placeholder scan:** none left. Values you must supply are things only you have: the R2 public URL (`<hash>`), the tile file's SHA-256, your API keys, and the B6 basemap-label notes.

**Type consistency:** `RawItem.geo_hint` (B2) is what `export` reads (B3); `State.gdelt_fips`/`fips_index()` (B1) is what `export` calls (B3); `summary.json` keys `iso, lgd, name, count` (B3) match `StateSummary` (B5); `issues.json` card keys match `Card` (B5); `MapView.onSelect` returns `State_LGD` (B6) and `App` matches it to `StateSummary.lgd` (B7); `GdeltSource.fetch(since, until=None)` is compatible with `SourcePlugin.fetch(since)`.

**Validated during planning (2026-09-28), in a scratch copy using this plan's exact code:**
- 24 pytest tests pass and ruff is clean.
- `iow fetch` and `iow export` ran against live GDELT, and a second fetch stored 0.
- On a real Vite react-ts template with `maplibre-gl@5.24.0`: build, 4 Vitest tests, and oxlint all pass.
- In a browser against real data and the real SoI tiles (served locally), all B6 Step 5 and B7 Step 5 checks pass: globe, no basemap borders, hover, select, panel with 100 headlines, Telangana empty, sea click closes.
- Confirmed against sources: ISO codes (Wikipedia), FIPS codes (statoids), the wrangler CORS JSON shape (Cloudflare docs), and the OpenFreeMap `boundary` layers (live style).

**Still unverified:**
- R2 upload and CORS on r2.dev: needs your Cloudflare login. B4 Step 7 checks it.
- Whether GDELT ever emits `IN05` or `IN29`.
- The live DOC 2.0 response shape (rate-limited while planning).
- The Fact Check API with a real key (A3).
