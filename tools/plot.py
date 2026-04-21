import json
import pathlib
import matplotlib.pyplot as plt
import numpy as np

SMALL_SIZES = [4, 16, 64]
LARGE_SIZES = [65536, 262144, 1048576]
IMPLS = ["oblivious", "friendly"]

BENCHES = [
    {
        "name": "build",
        "dir": pathlib.Path("target/criterion/build"),
        "ylabel": "Wall-clock time",
        "title": "Build time",
    },
    {
        "name": "query_point",
        "dir": pathlib.Path("target/criterion/query_point"),
        "ylabel": "Wall-clock time",
        "title": "Point query time",
    },
    {
        "name": "query_range",
        "dir": pathlib.Path("target/criterion/query_range"),
        "ylabel": "Wall-clock time",
        "title": "Range query time (half-array)",
    },
]


def load_estimates(
    criterion_dir: pathlib.Path, impl: str, size: int
) -> tuple[float, float]:
    """Return (mean_ns, std_dev_ns) for a given impl and array size."""
    path = criterion_dir / impl / str(size) / "new" / "estimates.json"
    with path.open() as f:
        data = json.load(f)
    return data["mean"]["point_estimate"], data["std_dev"]["point_estimate"]


def best_unit(max_ns: float) -> tuple[float, str]:
    if max_ns >= 1e9:
        return 1e9, "s"
    if max_ns >= 1e6:
        return 1e6, "ms"
    if max_ns >= 1e3:
        return 1e3, "µs"
    return 1.0, "ns"


def load_group(criterion_dir: pathlib.Path, sizes):
    means = {impl: [] for impl in IMPLS}
    stds = {impl: [] for impl in IMPLS}
    for impl in IMPLS:
        for size in sizes:
            mean, std = load_estimates(criterion_dir, impl, size)
            means[impl].append(mean)
            stds[impl].append(std)
    return means, stds


def plot_group(ax, sizes, means, stds, title, ylabel):
    scale, unit = best_unit(max(max(means[i]) for i in IMPLS))
    x = np.arange(len(sizes))
    bar_width = 0.35
    colors = {"oblivious": "#4c72b0", "friendly": "#dd8452"}

    for i, impl in enumerate(IMPLS):
        scaled_means = [v / scale for v in means[impl]]
        scaled_stds = [v / scale for v in stds[impl]]
        offset = (i - 0.5) * bar_width
        ax.bar(
            x + offset,
            scaled_means,
            bar_width,
            yerr=scaled_stds,
            label=impl,
            color=colors[impl],
            error_kw={"capsize": 4, "capthick": 1.2, "elinewidth": 1.2},
        )

    ax.set_xticks(x)
    ax.set_xticklabels([str(s) for s in sizes])
    ax.set_xlabel("Array size (elements)")
    ax.set_ylabel(f"{ylabel} ({unit})")
    ax.set_title(title)
    ax.legend()
    ax.set_yscale("log")
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)


fig, axes = plt.subplots(len(BENCHES), 2, figsize=(14, 6 * len(BENCHES)))
fig.canvas.manager.set_window_title("Segment Tree Benchmark Comparison")

for row, bench in enumerate(BENCHES):
    small_means, small_stds = load_group(bench["dir"], SMALL_SIZES)
    large_means, large_stds = load_group(bench["dir"], LARGE_SIZES)
    plot_group(
        axes[row, 0],
        SMALL_SIZES,
        small_means,
        small_stds,
        f"{bench['title']} — small arrays",
        bench["ylabel"],
    )
    plot_group(
        axes[row, 1],
        LARGE_SIZES,
        large_means,
        large_stds,
        f"{bench['title']} — large arrays",
        bench["ylabel"],
    )

fig.suptitle("Segment tree benchmarks: oblivious vs cache-friendly", y=1.01)
plt.tight_layout()
plt.savefig("bench_times.png", dpi=150, bbox_inches="tight")
plt.show()
