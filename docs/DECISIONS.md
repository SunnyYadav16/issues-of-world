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
| D-021 | Use a Gemini API key as the first LLM provider (`GEMINI_API_KEY`); Anthropic and OpenAI keys deferred | Anthropic Haiku 4.5 / OpenAI GPT-5 mini as costed in plan §9 | Key already in hand; nothing calls an LLM yet (A4/IOW-008). The adapter (D-008) will need a Gemini backend before IOW-048; its classification F1 and cost must be measured on the gold set like any other model, and §9 has no Gemini cost row. Set a Google Cloud budget alert: the free tier has no hard cap on paid use. |
| D-022 | State tiles served from R2 bucket `iow-tiles` (object `in_adm1.pmtiles`) via the `r2.dev` public URL; CORS allows only `http://localhost:5173` | Custom domain now; serve tiles from the web app's `public/` folder | Free tier covers it (10 GB, 10M reads/month, free egress; checked on Cloudflare's pricing page 2026-09-29). `r2.dev` is meant for development. Before deploying (IOW-036): attach a custom domain and add the production origin to CORS. Set a Cloudflare billing alert (a card is on file). |

## Notes from the B6 basemap check (informal, not IOW-023 QA)

- J&K / Ladakh: the SoI outline is one dark line covering Gilgit-Baltistan and Ladakh including Aksai Chin; no second dashed border. The basemap still labels "GILGIT-BALTISTAN" (small caps) *inside* the India-drawn polygon, and labels Pakistan / China places nearby. **Carry into IOW-023:** decide whether to hide or override basemap place labels in disputed areas (plan §13, last risk row).
- Arunachal Pradesh: SoI outline encloses the whole state; basemap labels "ARUNACHAL PRADESH" and "Itanagar" as Indian. No conflict seen.

## Notes from the first end-to-end run (2026-09-29)

- 6 h of GDELT → 798 items stored, 735 cards across 27 states. Re-fetch stored 0 (URL dedupe works).
- Precision is visibly low, as D-016 predicted: of 85 Maharashtra cards, only 30 headlines name the state or an obvious local term; many are national stories (SEBI, Supreme Court, Adani) tagged to Mumbai or Delhi. Delhi is worse (17 of 100). Syndicated copies appear several times (no dedup until IOW-046). Measure it properly with the ADM1 geoparse gold set (IOW-061) before trusting any number here.
