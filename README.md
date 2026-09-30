# issues-of-world

[![CI](https://github.com/SunnyYadav16/issues-of-world/actions/workflows/ci.yml/badge.svg)](https://github.com/SunnyYadav16/issues-of-world/actions/workflows/ci.yml)

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
