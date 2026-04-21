#!/usr/bin/env python3
"""Parse a cachegrind.out file and print cumulative events grouped by function."""

from collections import defaultdict
import json
import argparse


def parse(path: str, filter_str: str) -> tuple[list[str], dict[str, list[int]]]:
    events: list[str] = []
    totals: dict[str, list[int]] = defaultdict(lambda: [0] * len(events))
    current_fn: str | None = None

    with open(path) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("events:"):
                events = line.split()[1:]
                totals = defaultdict(lambda: [0] * len(events))
            elif line.startswith("fn=") and filter_str in line:
                current_fn = line[3:]
            elif current_fn and line and line[0].isdigit():
                parts = line.split()
                counts = [int(x) for x in parts[1:]]
                acc = totals[current_fn]
                for i, v in enumerate(counts):
                    acc[i] += v

    return events, dict(totals)


def main():
    parser = argparse.ArgumentParser(description="Parse cachegrind output.")
    parser.add_argument(
        "path", nargs="?", default="cachegrind.out", help="Path to cachegrind.out"
    )
    parser.add_argument("--filter", default="", help="Filter for fn= lines")
    args = parser.parse_args()

    events, totals = parse(args.path, args.filter)

    print(json.dumps({"events": events, "totals": totals}))


if __name__ == "__main__":
    main()
