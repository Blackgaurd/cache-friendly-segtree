#!/usr/bin/env python3
import subprocess
import os
import sys
import math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt

# append to path so we can import from parse_cachegrind
sys.path.append(os.path.join(os.path.dirname(__file__)))
from parse_cachegrind import parse

BINARIES = ["bin_build", "bin_query_point", "bin_query_range", "bin_update_point"]
TREE_TYPES = ["F", "O"]
ELEMENT_COUNTS = [4**x for x in range(12 + 1)]
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
    "Bm": 17,
    # L1 data miss
    "L1m": 14,
    # all cache data miss
    "LLm": 294,
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


def compile_binaries() -> None:
    for binary in BINARIES:
        print(f"Compiling {binary}...")
        subprocess.run(
            ["cargo", "build", "--release", "--bin", binary],
            check=True,
            capture_output=True,
        )

def _cargo_build_node_sz(binary: str, node_sz: int) -> None:
    print(f"Compiling {binary} with NODE_SZ={node_sz}...")
    subprocess.run(
        ["cargo", "build", "--release", "--bin", binary],
        env={**os.environ, "SEGTREE_NODE_SZ": str(node_sz)},
        check=True,
        capture_output=True,
    )


def _run_valgrind_node_sz(binary: str, node_sz: int, num_elements: int) -> dict[str, int]:
    print(f"Running {binary} with NODE_SZ={node_sz}, {num_elements} elements...")
    out_file = f"cachegrind.out.{binary}.nodesz{node_sz}.{num_elements}"
    num_queries = NUM_QUERIES if "query" in binary or "update" in binary else None
    cmd = [
        "valgrind",
        "--tool=cachegrind",
        "--cache-sim=yes",
        "--branch-sim=yes",
        f"--cachegrind-out-file={out_file}",
        f"./target/release/{binary}",
        str(num_elements),
    ]
    if num_queries is not None:
        cmd.append(str(num_queries))
    cmd.append("F")
    subprocess.run(cmd, check=True, capture_output=True)

    filter_str = BINARY_FN_FILTERS[binary]
    events, totals = parse(out_file, filter_str)
    os.remove(out_file)
    return {event: sum(t[i] for t in totals.values()) for i, event in enumerate(events)}


def run_num_elements_bench(
    binary: str, num_elements: int, tree_type: str, num_queries: int | None
) -> dict[str, int]:
    print(f"Running {binary} with {num_elements} elements, type {tree_type}...")
    out_file = f"cachegrind.out.{binary}.{num_elements}.{tree_type}"

    cmd = [
        "valgrind",
        "--tool=cachegrind",
        "--cache-sim=yes",
        "--branch-sim=yes",
        f"--cachegrind-out-file={out_file}",
        f"./target/release/{binary}",
        str(num_elements),
    ]
    if num_queries is not None:
        cmd.append(str(num_queries))
    cmd.append(tree_type)

    subprocess.run(cmd, check=True, capture_output=True)

    filter_str = BINARY_FN_FILTERS[binary]
    events, totals = parse(out_file, filter_str)
    os.remove(out_file)

    return {
        event: sum(t[i] for t in totals.values()) for i, event in enumerate(events)
    }



def plot_num_elements(max_workers: int = 8):
    results = defaultdict(lambda: defaultdict(dict))
    event_names = None

    compile_binaries()

    tasks = [
        (binary, n, t, NUM_QUERIES if "query" in binary or "update" in binary else None)
        for binary in BINARIES
        for n in ELEMENT_COUNTS
        for t in TREE_TYPES
    ]
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(run_num_elements_bench, *task): task for task in tasks}
        for fut in as_completed(futs):
            binary, n, t, _ = futs[fut]
            summary = fut.result()
            if event_names is None:
                event_names = list(summary.keys())
            results[binary][n][t] = summary

    if event_names is None:
        print("\nNo results to display.")
        return

    fig, axes = plt.subplots(1, len(BINARIES), figsize=(6 * len(BINARIES), 5))
    if len(BINARIES) == 1:
        axes = [axes]

    for ax, binary in zip(axes, BINARIES):
        for t in TREE_TYPES:
            xs = ELEMENT_COUNTS
            ys = [math.log2(compute_cest(results[binary][n][t])) for n in xs]
            ax.plot(xs, ys, marker="o", label=t)
        ax.set_xscale("log")
        ax.set_xlabel("Number of Elements")
        ax.set_ylabel("log2(CEst)")
        ax.set_ylim(bottom=0)
        ax.set_title(binary)
        ax.legend()

    plt.tight_layout()
    plt.savefig("bench_results_num_elements.png", dpi=150)
    print("Saved bench_results_num_elements.png")


NODE_SZ_ELEMENT_COUNTS = [4**x for x in range(4, 10)]


def plot_node_sz(max_workers: int = 6):
    node_sizes = list(range(2, 33))
    results = defaultdict(lambda: defaultdict(dict))

    for binary in BINARIES:
        for node_sz in node_sizes:
            _cargo_build_node_sz(binary, node_sz)
            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                futs = {ex.submit(_run_valgrind_node_sz, binary, node_sz, n): n
                        for n in NODE_SZ_ELEMENT_COUNTS}
                for fut in as_completed(futs):
                    n = futs[fut]
                    results[binary][node_sz][n] = fut.result()

    fig, axes = plt.subplots(1, len(BINARIES), figsize=(6 * len(BINARIES), 5))
    if len(BINARIES) == 1:
        axes = [axes]

    for ax, binary in zip(axes, BINARIES):
        for n in NODE_SZ_ELEMENT_COUNTS:
            ys = [math.log2(compute_cest(results[binary][node_sz][n])) for node_sz in node_sizes]
            ax.plot(node_sizes, ys, marker="o", label=str(n))
        for x in [8, 16, 32]:
            ax.axvline(x=x, color="gray", linestyle="--", linewidth=0.8)
        ax.set_xlabel("NODE_SZ")
        ax.set_ylabel("log2(CEst)")
        ax.set_title(binary)
        ax.legend(title="num_elements")

    plt.tight_layout()
    plt.savefig("bench_results_node_sz.png", dpi=150)
    print("Saved bench_results_node_sz.png")


if __name__ == "__main__":
    plot_num_elements()
    plot_node_sz()
