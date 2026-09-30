# pipeline/iow/cli.py
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from iow import store
from iow.evals import geoparse
from iow.plugins.sources.gdelt import GdeltSource
from iow.stages.export import export


def main() -> None:
    p = argparse.ArgumentParser(prog="iow")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="pull recent GDELT articles into the local store")
    f.add_argument("--hours", type=float, default=3)
    e = sub.add_parser("export", help="write static JSON for the web app")
    e.add_argument("--out", type=Path, required=True)
    ev = sub.add_parser("eval", help="gold-set tools and evals")
    ev.add_argument("suite", choices=["sample", "review", "geoparse"])
    ev.add_argument("--n", type=int, default=200)
    ev.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    now = datetime.now(timezone.utc)
    if args.cmd == "eval":
        if args.suite == "sample":
            rows = geoparse.sample(store.read_all(), args.n, args.seed)
            geoparse.save(rows)
            print(f"wrote {len(rows)} rows to {geoparse.DATASET}")
        elif args.suite == "review":
            geoparse.review()
        else:
            r = geoparse.report(geoparse.load())
            print(f"wrote {geoparse.REPORTS / 'geoparse.md'} ({r['systems']['geo']['n']} rows scored)")
    elif args.cmd == "fetch":
        added = store.append_new(GdeltSource().fetch(now - timedelta(hours=args.hours)))
        print(f"stored {added} new items")
    else:
        counts = export(store.read_all(), args.out, now)
        national = counts.pop("national")
        lit = sum(1 for c in counts.values() if c)
        print(f"exported {sum(counts.values())} state cards across {lit} states, {national} national")
