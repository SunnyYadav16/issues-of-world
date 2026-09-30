# Data licenses and attribution

| Data | Source | License | Used for |
|---|---|---|---|
| `SOI_States.pmtiles` (India state boundaries) | [yashveeeeeeer/india-geodata](https://github.com/yashveeeeeeer/india-geodata), release tag `admin/states`; underlying data © Survey of India | CC0-1.0 (release files, per the repo's `states/README.md`) | State polygons. SHA-256 `fb39ed0184502eeab048e4961fd4a049046532a60878b0e99e65c2bd01caca79`, downloaded 2026-09-28 |
| GDELT GKG 2.1 | [The GDELT Project](https://www.gdeltproject.org/) | Free and open; attribution required | Article discovery and ADM1 location codes |
| Basemap | [OpenFreeMap](https://openfreemap.org/) style "liberty", data © OpenStreetMap contributors (ODbL) | ODbL | Basemap only. All its boundary layers are hidden (see plan §4.1) |

Still to verify (plan §16): OpenFreeMap usage terms; per-file SoI provenance for the tiles.

## Open before any public deploy

**Survey of India state boundaries: licence is unclear.** The tiles' own metadata credits "© Survey Of India", while the india-geodata repo describes its release files as CC0. A third-party repo cannot place Survey of India's copyrighted data in the public domain, so at most one of these can be true. Ask the repo owner where the CC0 claim comes from, or read Survey of India's terms, and record the answer here. This is open question #4 in the project plan (§16). The app stays local-only (D-018) until it is settled.
