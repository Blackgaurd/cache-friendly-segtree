import json
import pathlib
import matplotlib.pyplot as plt
import numpy as np

SIZES = [16, 64, 256, 1024, 4096, 16384, 65536, 262144]
IMPLS = ["oblivious", "friendly"]
CRITERION_DIR = pathlib.Path("target/criterion/build")


def load_estimates(impl: str, size: int) -> tuple[float, float]:
    """Return (mean_ns, std_dev_ns) for a given impl and array size."""
    path = CRITERION_DIR / impl / str(size) / "new" / "estimates.json"
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


means = {impl: [] for impl in IMPLS}
stds = {impl: [] for impl in IMPLS}

for impl in IMPLS:
    for size in SIZES:
        mean, std = load_estimates(impl, size)
        means[impl].append(mean)
        stds[impl].append(std)

scale, unit = best_unit(max(max(means[i]) for i in IMPLS))

x = np.arange(len(SIZES))
bar_width = 0.35
colors = {"oblivious": "#4c72b0", "friendly": "#dd8452"}

fig, ax = plt.subplots(figsize=(11, 6))
fig.canvas.manager.set_window_title("Segment Tree Build Time Comparison")

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
ax.set_xticklabels([str(s) for s in SIZES])
ax.set_xlabel("Array size (elements)")
ax.set_ylabel(f"Wall-clock build time ({unit})")
ax.set_title("Segment tree wall-clock build time: oblivious vs cache-friendly")
ax.legend()
ax.set_yscale("log")
ax.yaxis.grid(True, linestyle="--", alpha=0.7)
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig("build_times.png", dpi=150)
plt.show()
