import type { StateSummary } from "./data";

/** What choosing a search result does: which panel opens and where the camera goes. */
export type Target =
  | { kind: "state"; lgd: number }
  | { kind: "national" }
  | { kind: "city"; lgd: number; city: string; lng: number; lat: number }
  | { kind: "uncovered"; name: string; lng: number; lat: number; zoom: number };

export type Result = { key: string; label: string; detail: string; target: Target };

type Geo = {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  feature_code: string;
  country_code: string;
  country?: string;
  admin1?: string;
};

const norm = (s: string) =>
  s
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, " ")
    .trim();

/** The state a geocoder's admin1 name refers to ("National Capital Territory of Delhi" -> Delhi). */
export function matchState(admin1: string | undefined, states: StateSummary[]): StateSummary | undefined {
  const a = norm(admin1 ?? "");
  if (!a) return undefined;
  return states.find((s) => [s.name, ...(s.aliases ?? [])].some((n) => a === norm(n) || a.endsWith(` of ${norm(n)}`)));
}

/** States (by name, alias, or the start of any word in either) and India itself. Instant and works offline. */
export function searchLocal(q: string, states: StateSummary[]): Result[] {
  const n = norm(q);
  if (!n) return [];
  const hit = (name: string) =>
    norm(name)
      .split(" ")
      .some((w) => w.startsWith(n)) || norm(name).startsWith(n);
  const out: Result[] = states
    .filter((s) => [s.name, ...(s.aliases ?? [])].some(hit))
    .slice(0, 5)
    .map((s) => ({
      key: `state-${s.lgd}`,
      label: s.name,
      detail: "State · India",
      target: { kind: "state", lgd: s.lgd },
    }));
  if (hit("India") || hit("national")) {
    out.unshift({ key: "national", label: "India", detail: "Country · national news", target: { kind: "national" } });
  }
  return out;
}

const isCountry = (code: string) => code.startsWith("PCL");

/** Turn a geocoder hit into a result. Indian cities open their state's news; everything else has no news yet. */
export function toResult(g: Geo, states: StateSummary[]): Result | null {
  const key = `geo-${g.id}`;
  if (g.country_code === "IN") {
    if (isCountry(g.feature_code)) return null; // searchLocal already offers India
    const state = matchState(g.admin1, states);
    if (!state) return null;
    return {
      key,
      label: g.name,
      detail: `City · ${state.name}`,
      target: { kind: "city", lgd: state.lgd, city: g.name, lng: g.longitude, lat: g.latitude },
    };
  }
  const where = isCountry(g.feature_code) ? "Country" : [g.admin1, g.country].filter(Boolean).join(", ");
  return {
    key,
    label: g.name,
    detail: where,
    target: {
      kind: "uncovered",
      name: g.name,
      lng: g.longitude,
      lat: g.latitude,
      zoom: isCountry(g.feature_code) ? 4 : 8,
    },
  };
}

const GEOCODER = "https://geocoding-api.open-meteo.com/v1/search";

/** Cities and countries worldwide. The query text leaves the browser for open-meteo.com (no key, no account). */
export async function searchRemote(q: string, states: StateSummary[], signal?: AbortSignal): Promise<Result[]> {
  const res = await fetch(
    `${GEOCODER}?${new URLSearchParams({ name: q, count: "6", language: "en", format: "json" })}`,
    { signal },
  );
  if (!res.ok) throw new Error(`geocoder: HTTP ${res.status}`);
  const { results = [] } = (await res.json()) as { results?: Geo[] };
  return results.flatMap((g) => toResult(g, states) ?? []);
}

/** Does a headline name this place? Whole words, case-insensitive. */
export function mentions(headline: string, place: string): boolean {
  const esc = place.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return new RegExp(`(?<!\\p{L})${esc}(?!\\p{L})`, "iu").test(headline);
}
