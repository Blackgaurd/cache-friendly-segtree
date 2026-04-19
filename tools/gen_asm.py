#!/usr/bin/env python3
import os
import subprocess

os.makedirs("asm", exist_ok=True)

symbols = [
    ("friendly_build",       "<cache_friendly_segtree::friendly::FriendlySegTree as cache_friendly_segtree::interface::SegTree>::build"),
    ("friendly_build_rec",   "cache_friendly_segtree::friendly::FriendlySegTree::build_rec"),
    ("friendly_query",       "<cache_friendly_segtree::friendly::FriendlySegTree as cache_friendly_segtree::interface::SegTree>::query"),
    ("friendly_query_rec",   "cache_friendly_segtree::friendly::FriendlySegTree::query_rec"),
    ("friendly_update",      "<cache_friendly_segtree::friendly::FriendlySegTree as cache_friendly_segtree::interface::SegTree>::update"),
    ("friendly_update_rec",  "cache_friendly_segtree::friendly::FriendlySegTree::update_rec"),
    ("oblivious_build",      "<cache_friendly_segtree::obvlivious::ObliviousSegTree as cache_friendly_segtree::interface::SegTree>::build"),
    ("oblivious_build_rec",  "cache_friendly_segtree::obvlivious::ObliviousSegTree::build_rec"),
    ("oblivious_query",      "<cache_friendly_segtree::obvlivious::ObliviousSegTree as cache_friendly_segtree::interface::SegTree>::query"),
    ("oblivious_query_rec",  "cache_friendly_segtree::obvlivious::ObliviousSegTree::query_rec"),
    ("oblivious_update",     "<cache_friendly_segtree::obvlivious::ObliviousSegTree as cache_friendly_segtree::interface::SegTree>::update"),
    ("oblivious_update_rec", "cache_friendly_segtree::obvlivious::ObliviousSegTree::update_rec"),
]

for name, sym in symbols:
    out_path = f"asm/{name}.asm"
    print(f"Generating {out_path} ...")
    result = subprocess.run(
        ["cargo", "asm", "--lib", sym],
        capture_output=True, text=True
    )
    with open(out_path, "w") as f:
        f.write(result.stdout)

print("\nDone. Files in asm/:")
for f in sorted(os.listdir("asm")):
    print(f"  {f}")
