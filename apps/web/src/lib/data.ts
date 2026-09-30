// apps/web/src/lib/data.ts
export type StateSummary = { iso: string; lgd: number; name: string; aliases?: string[]; count: number };
export type Card = {
  id: string;
  headline: string;
  outlet: string;
  published_at: string;
  url: string;
  scope: "national" | "state" | "local";
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

/** Stories that belong to no one state. Shaped like a state so the list and panel treat it as one; it has no map shape. */
export const NATIONAL_LGD = 0;
/** A searched place outside India (or one we cannot place): the panel says there is no coverage instead of loading. */
export const UNCOVERED_LGD = -1;
export const noNational: StateSummary = { iso: "national", lgd: NATIONAL_LGD, name: "India: national", count: 0 };

export type Summary = { states: StateSummary[]; national: StateSummary; generatedAt: string };

export async function loadSummary(): Promise<Summary> {
  const doc = await getJson("in/summary.json");
  const { count } = doc.national as { count: number };
  return {
    states: doc.states as StateSummary[],
    national: { ...noNational, count },
    generatedAt: doc.generated_at as string,
  };
}

export async function loadCards(iso: string): Promise<Card[]> {
  return (await getJson(`in/${iso.toLowerCase()}/issues.json`)).issues as Card[];
}

/** Links come from third-party feeds; only http(s) may become an href. */
export function safeHref(url: string): string {
  return /^https?:\/\//i.test(url) ? url : "#";
}
