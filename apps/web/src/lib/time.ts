const fmt = new Intl.RelativeTimeFormat("en", { numeric: "auto", style: "short" });
const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["day", 86400],
  ["hour", 3600],
  ["minute", 60],
];

/** "3 hr. ago", "now". Empty string for an unparseable date so the UI shows nothing instead of "NaN". */
export function ago(iso: string, now = Date.now()): string {
  const seconds = Math.round((new Date(iso).getTime() - now) / 1000);
  if (Number.isNaN(seconds)) return "";
  for (const [unit, size] of UNITS) if (Math.abs(seconds) >= size) return fmt.format(Math.round(seconds / size), unit);
  return fmt.format(0, "second");
}
