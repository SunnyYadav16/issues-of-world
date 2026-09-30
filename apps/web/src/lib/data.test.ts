// apps/web/src/lib/data.test.ts
import { afterEach, expect, test, vi } from "vitest";
import { loadCards, loadSummary, safeHref } from "./data";

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

test("loadSummary returns states, the national list and the export time", async () => {
  stub({
    schema_version: 1,
    generated_at: "2026-09-29T02:19:00+00:00",
    states: [{ iso: "MH", lgd: 27, name: "Maharashtra", count: 3 }],
    national: { count: 5 },
  });
  expect(await loadSummary()).toEqual({
    generatedAt: "2026-09-29T02:19:00+00:00",
    states: [{ iso: "MH", lgd: 27, name: "Maharashtra", count: 3 }],
    national: { iso: "national", lgd: 0, name: "India: national", count: 5 },
  });
});

test("the national list is read from its own folder", async () => {
  stub({ schema_version: 1, issues: [] });
  await loadCards("national");
  expect(fetch).toHaveBeenCalledWith("/data/in/national/issues.json");
});
