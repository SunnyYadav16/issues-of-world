import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "fetch_logos.py"
spec = importlib.util.spec_from_file_location("fetch_logos", SCRIPT)
assert spec and spec.loader
fetch_logos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch_logos)


def test_accepts_images():
    assert fetch_logos.logo_problem(b"\x89PNG...", "image/png", "x.png") is None
    assert (
        fetch_logos.logo_problem(
            b'<svg xmlns="http://www.w3.org/2000/svg"><path d="M0"/></svg>', "image/svg+xml", "x.svg"
        )
        is None
    )


def test_rejects_non_images():
    assert fetch_logos.logo_problem(b"<html>Not found</html>", "text/html", "x.png")


def test_rejects_svg_that_can_run_code():
    # Served from our own domain, so a script inside an SVG would run as our site
    assert fetch_logos.logo_problem(b"<svg><script>alert(1)</script></svg>", "image/svg+xml", "x.svg")
    assert fetch_logos.logo_problem(b'<svg onload="alert(1)"></svg>', "image/svg+xml", "x.svg")
    assert fetch_logos.logo_problem(b'<svg><a href="javascript:alert(1)"/></svg>', "image/svg+xml", "x.svg")


def test_rejects_format_that_does_not_match_the_file_name():
    # Some CDNs answer with WebP or AVIF; saved as .png it would be served with the wrong content type
    assert fetch_logos.logo_problem(b"RIFF....WEBP", "image/webp", "x.png")
    assert fetch_logos.logo_problem(b"....ftypavif", "image/avif", "x.png")
    assert fetch_logos.logo_problem(b"\xff\xd8", "image/jpeg; charset=binary", "x.jpg") is None


def test_rejects_bytes_that_contradict_the_content_type():
    # thehindu.com labels its logo image/png but sends WebP bytes
    assert fetch_logos.logo_problem(b"RIFF\x00\x00\x00\x00WEBPVP8 ", "image/png", "x.png")
    assert fetch_logos.logo_problem(b"RIFF\x00\x00\x00\x00WEBPVP8 ", "image/webp", "x.webp") is None


def test_bytes_decide_the_format_not_the_label():
    # Mislabelled WebP is fine when it is saved under a .webp name
    assert fetch_logos.logo_problem(b"RIFF\x00\x00\x00\x00WEBPVP8 ", "image/png", "x.webp") is None
