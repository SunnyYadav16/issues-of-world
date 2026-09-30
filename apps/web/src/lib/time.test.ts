import { expect, test } from "vitest";
import { ago } from "./time";

const NOW = Date.parse("2026-09-29T12:00:00Z");

test("picks the largest sensible unit", () => {
  expect(ago("2026-09-29T09:00:00Z", NOW)).toBe("3 hr. ago");
  expect(ago("2026-09-27T12:00:00Z", NOW)).toBe("2 days ago");
  expect(ago("2026-09-29T11:55:00Z", NOW)).toBe("5 min. ago");
});

test("just now and bad input", () => {
  expect(ago("2026-09-29T12:00:00Z", NOW)).toBe("now");
  expect(ago("not a date", NOW)).toBe("");
});
