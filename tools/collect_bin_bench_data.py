#!/usr/bin/env python3
import subprocess
import os
import sys
from collections import defaultdict

# append to path so we can import from parse_cachegrind
sys.path.append(os.path.join(os.path.dirname(__file__)))
from parse_cachegrind import parse

BINARIES = ["bin_build", "bin_query_point", "bin_query_range", "bin_update_point"]
TREE_TYPES = ["F", "O"]
ELEMENT_COUNTS = [8**1, 8**2, 8**3, 8**4, 8**5, 8**6]
NUM_QUERIES = 1_000

# each binary should point at one specific function substring for parse(..., filter_str).
BINARY_FN_FILTERS = {
    "bin_build": "build_rec",
    "bin_query_point": "query_rec",
    "bin_query_range": "query_rec",
    "bin_update_point": "update_rec",
}

CEST_WEIGHTS = {
    # instructions
    "Ir": 1,
    # branch misses
    "Bm": 15,
    # L1 data miss
    "L1m": 5,
    # all cache data miss
    "LLm": 150,
}


def compute_cest(data: dict[str, int]) -> int:
    # use data-side misses only for cache miss terms.
    bm = data["Bm"] if "Bm" in data else data.get("Bcm", 0) + data.get("Bim", 0)
    l1m = data.get("D1mr", 0) + data.get("D1mw", 0)
    llm = data.get("DLmr", 0) + data.get("DLmw", 0)
    ir = data.get("Ir", 0)

    return (
        CEST_WEIGHTS["Ir"] * ir
        + CEST_WEIGHTS["Bm"] * bm
        + CEST_WEIGHTS["L1m"] * l1m
        + CEST_WEIGHTS["LLm"] * llm
    )


def run_bench(
    binary: str, num_elements: int, tree_type: str, num_queries: int | None
) -> dict[str, int]:
    print(f"Running {binary} with {num_elements} elements, type {tree_type}...")

    # run command
    cmd = [
        "valgrind",
        "--tool=cachegrind",
        "--cache-sim=yes",
        "--branch-sim=yes",
        "--cachegrind-out-file=cachegrind.out",
        f"./target/release/{binary}",
        str(num_elements),
    ]
    if num_queries is not None:
        cmd.append(str(num_queries))
    cmd.append(tree_type)

    subprocess.run(cmd, check=True, capture_output=True)

    # parse only functions matching this binary's configured filter.
    filter_str = BINARY_FN_FILTERS[binary]
    events, totals = parse("cachegrind.out", filter_str)

    # calculate sum of all functions for each event
    summary = {
        event: sum(t[i] for t in totals.values()) for i, event in enumerate(events)
    }
    return summary


def compile_binaries() -> None:
    for binary in BINARIES:
        print(f"Compiling {binary}...")
        subprocess.run(
            ["cargo", "build", "--release", "--bin", binary],
            check=True,
            capture_output=True,
        )


def main():
    results = defaultdict(lambda: defaultdict(dict))
    event_names = None

    compile_binaries()

    for binary in BINARIES:
        num_queries = NUM_QUERIES if "query" in binary or "update" in binary else None
        for n in ELEMENT_COUNTS:
            for t in TREE_TYPES:
                summary = run_bench(binary, n, t, num_queries)
                if event_names is None:
                    event_names = list(summary.keys())
                results[binary][n][t] = summary

    # simple summary presentation
    if event_names is None:
        print("\nNo results to display.")
        return

    print("\nSummary of Results (all events + CEst):")
    header = ["Binary", "N", "Type"] + event_names + ["CEst"]
    widths = [20, 10, 5] + [15] * len(event_names) + [15]
    header_line = " ".join(f"{col:<{widths[i]}}" for i, col in enumerate(header))
    print(header_line)
    print("-" * len(header_line))

    for binary in BINARIES:
        for n in ELEMENT_COUNTS:
            for t in TREE_TYPES:
                data = results[binary][n][t]
                cest = compute_cest(data)
                row = (
                    [binary, str(n), t]
                    + [f"{data.get(ev, 0):,}" for ev in event_names]
                    + [f"{cest:,}"]
                )
                row_line = " ".join(f"{val:<{widths[i]}}" for i, val in enumerate(row))
                print(row_line)


if __name__ == "__main__":
    main()
