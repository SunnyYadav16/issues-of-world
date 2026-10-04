"""Download each source's logo once, so the web app serves it from our own domain instead of hotlinking.

Reads data/sources.yaml: downloads `logo_url` to apps/web/public/<logo> for every source that has both.
Run from the repo root: uv run --project pipeline python scripts/fetch_logos.py
A failed or rejected download is reported; remove that source's `logo` field (keep logo_url) until a URL works.
"""

import re
import sys
from pathlib import Path

import httpx
import yaml

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "apps" / "web" / "public"
# Same browser headers as news-scrap-test; some outlets refuse other user agents.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36",
}
# File extension -> the one content type we accept for it. The Accept header asks for exactly that type, because
# some CDNs otherwise answer with WebP or AVIF, which would then be served under the wrong extension.
TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".webp": "image/webp"}
# What the first bytes of each format look like; servers sometimes mislabel what they send.
MAGIC = {
    "image/png": lambda b: b.startswith(b"\x89PNG"),
    "image/jpeg": lambda b: b.startswith(b"\xff\xd8"),
    "image/webp": lambda b: b[:4] == b"RIFF" and b[8:12] == b"WEBP",
    "image/svg+xml": lambda b: b"<svg" in b[:2048].lower(),
}
SVG_CODE = re.compile(rb"<script|\son\w+\s*=|javascript:|<foreignObject", re.IGNORECASE)


def logo_problem(content: bytes, content_type: str, dest: str) -> str | None:
    """Why this download must not be saved as `dest`, or None if it is a usable image of the right format.

    The bytes decide the format; the server's content type is only reported, because some servers mislabel it.
    """
    want = TYPES.get(Path(dest).suffix.lower())
    if want is None:
        return f"{dest} has no known image extension"
    if not MAGIC[want](content):
        return f"bytes are not {want} (server said {content_type or 'nothing'})"
    if want == "image/svg+xml" and SVG_CODE.search(content):
        return "SVG contains script or event handlers"
    return None


def main() -> int:
    sources = yaml.safe_load((ROOT / "data" / "sources.yaml").read_text(encoding="utf-8"))
    jobs = {s["logo"]: s["logo_url"] for s in sources if s.get("logo") and s.get("logo_url")}
    failed = 0
    with httpx.Client(headers=HEADERS, timeout=20, follow_redirects=True) as client:
        for dest, url in sorted(jobs.items()):
            try:
                r = client.get(url, headers={"Accept": TYPES.get(Path(dest).suffix.lower(), "image/*")})
                r.raise_for_status()
                problem = logo_problem(r.content, r.headers.get("content-type", ""), dest)
            except httpx.HTTPError as e:
                problem = str(e)
            if problem:
                failed += 1
                print(f"FAIL {dest}: {problem} ({url})")
                continue
            (PUBLIC / dest).parent.mkdir(parents=True, exist_ok=True)
            (PUBLIC / dest).write_bytes(r.content)
            print(f"ok   {dest} ({len(r.content)} bytes)")
    print(f"{len(jobs) - failed} saved, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
