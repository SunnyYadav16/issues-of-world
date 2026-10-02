import { afterEach, expect, test, vi } from "vitest";
import { matchState, mentions, searchLocal, searchRemote, toResult } from "./places";

const states = [
  { iso: "MH", lgd: 27, name: "Maharashtra", aliases: ["Bombay"], count: 1 },
  { iso: "DL", lgd: 7, name: "Delhi", aliases: ["NCT of Delhi", "New Delhi"], count: 1 },
  { iso: "UP", lgd: 9, name: "Uttar Pradesh", aliases: [], count: 1 },
  { iso: "UK", lgd: 5, name: "Uttarakhand", aliases: [], count: 1 },
  { iso: "WB", lgd: 19, name: "West Bengal", aliases: ["Bengal"], count: 1 },
];
const geo = (o: object) => ({
  id: 1,
  name: "X",
  latitude: 1,
  longitude: 2,
  feature_code: "PPL",
  country_code: "IN",
  ...o,
});

afterEach(() => vi.unstubAllGlobals());

test("admin1 names map to states, including the long official ones", () => {
  expect(matchState("Maharashtra", states)?.iso).toBe("MH");
  expect(matchState("National Capital Territory of Delhi", states)?.iso).toBe("DL");
  expect(matchState("Bombay", states)?.iso).toBe("MH");
  expect(matchState("Oecusse", states)).toBeUndefined();
  expect(matchState(undefined, states)).toBeUndefined();
});

test("local search matches the start of any word and offers India", () => {
  expect(searchLocal("uttar", states).map((r) => r.label)).toEqual(["Uttar Pradesh", "Uttarakhand"]);
  expect(searchLocal("beng", states)[0].label).toBe("West Bengal");
  expect(searchLocal("ind", states)[0].target).toEqual({ kind: "national" });
  expect(searchLocal("zzz", states)).toEqual([]);
});

test("an Indian city opens its state's news and flies to the city", () => {
  const r = toResult(geo({ name: "Pune", admin1: "Maharashtra", latitude: 18.5, longitude: 73.8 }), states);
  expect(r?.target).toEqual({ kind: "city", lgd: 27, city: "Pune", lng: 73.8, lat: 18.5 });
  expect(r?.detail).toBe("City · Maharashtra");
});

test("Indian results that would duplicate India or cannot be placed are dropped", () => {
  expect(toResult(geo({ name: "India", feature_code: "PCLI" }), states)).toBeNull();
  expect(toResult(geo({ name: "Nowhere", admin1: "Unknown" }), states)).toBeNull();
});

test("places outside India are flown to but have no news", () => {
  const city = toResult(geo({ name: "Paris", country_code: "FR", country: "France", admin1: "Île-de-France" }), states);
  expect(city?.target).toMatchObject({ kind: "uncovered", name: "Paris", zoom: 8 });
  expect(city?.detail).toBe("Île-de-France, France");
  const country = toResult(geo({ name: "Japan", country_code: "JP", feature_code: "PCLI" }), states);
  expect(country?.target).toMatchObject({ kind: "uncovered", zoom: 4 });
});

test("searchRemote sends the query and maps results", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ results: [geo({ name: "Pune", admin1: "Maharashtra" })] }) }),
  );
  expect((await searchRemote("pune", states)).map((r) => r.label)).toEqual(["Pune"]);
  expect(String((fetch as ReturnType<typeof vi.fn>).mock.calls[0][0])).toContain("name=pune");
});

test("searchRemote fails on HTTP errors and copes with no results", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 429 }));
  await expect(searchRemote("x", states)).rejects.toThrow(/429/);
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) }));
  expect(await searchRemote("zzzz", states)).toEqual([]);
});

test("mentions matches whole words only", () => {
  expect(mentions("Pune police arrest two", "Pune")).toBe(true);
  expect(mentions("Pune's traffic", "pune")).toBe(true);
  expect(mentions("Puneri misal", "Pune")).toBe(false);
  expect(mentions("Delhi (NCR) smog", "Delhi (NCR)")).toBe(true); // regex characters are escaped
});
