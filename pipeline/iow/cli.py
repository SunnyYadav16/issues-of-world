# pipeline/iow/cli.py
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from iow import store
from iow.plugins.sources.gdelt import GdeltSource
from iow.stages.export import export


def main() -> None:
    p = argparse.ArgumentParser(prog="iow")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="pull recent GDELT articles into the local store")
    f.add_argument("--hours", type=float, default=3)
    e = sub.add_parser("export", help="write static JSON for the web app")
    e.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    now = datetime.now(timezone.utc)
    if args.cmd == "fetch":
        added = store.append_new(GdeltSource().fetch(now - timedelta(hours=args.hours)))
        print(f"stored {added} new items")
    else:
        counts = export(store.read_all(), args.out, now)
        national = counts.pop("national")
        lit = sum(1 for c in counts.values() if c)
        print(f"exported {sum(counts.values())} state cards across {lit} states, {national} national")
