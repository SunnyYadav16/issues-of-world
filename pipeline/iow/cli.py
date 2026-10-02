# pipeline/iow/cli.py
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from iow import store
from iow.core.registry import load_source, source_ids
from iow.evals import geoparse
from iow.stages.export import export


def main() -> None:
    p = argparse.ArgumentParser(prog="iow")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="pull recent articles from the registered sources into the local store")
    f.add_argument("--source", choices=source_ids(), help="one source ID (default: all registered)")
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
        since = now - timedelta(hours=args.hours)
        for source_id in [args.source] if args.source else source_ids():
            print(f"{source_id}: stored {store.append_new(load_source(source_id).fetch(since))} new items")
    else:
        counts = export(store.read_all(), args.out, now)
        national = counts.pop("national")
        lit = sum(1 for c in counts.values() if c)
        print(f"exported {sum(counts.values())} state cards across {lit} states, {national} national")
