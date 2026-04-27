//! Optimized cache-friendly segtree implementation.

use std::cmp::{max, min};

use crate::interface::SegTree;

include!("constants.rs"); // NODE_SZ constant

fn slice_sum(slice: &[i64]) -> i64 {
    // TODO: check the compiled code to see if this is simd
    slice.iter().sum()
}

/// Return smallest x >= n such that x is a power of base.
fn round_to_next_power_of(n: usize, base: usize) -> usize {
    debug_assert!(base > 1, "base must be greater than 1");

    let mut ret = 1;
    while ret < n {
        ret *= base;
    }
    ret
}

#[derive(Debug)]
pub struct FriendlySegTree {
    n: usize,
    nodes: Vec<i64>,
}

// helper functions
impl FriendlySegTree {
    fn build_rec(nodes: &mut [i64], items: &[i64], start_idx: usize, l: usize, r: usize) {
        let length = r - l + 1;
        if length == NODE_SZ {
            // fill nodes
            let items_r = min(r, items.len() - 1);
            let items_slice = &items[l..=items_r];
            nodes[start_idx..start_idx + items_slice.len()].copy_from_slice(items_slice);
            return;
        }

        let next_length = length / NODE_SZ;
        for i in 0..NODE_SZ {
            let next_start_idx = (start_idx + 1 + i) * NODE_SZ;
            let next_l = l + i * next_length;
            let next_r = next_l + next_length - 1;
            if next_l >= items.len() {
                break;
            }

            Self::build_rec(nodes, items, next_start_idx, next_l, next_r);
            nodes[start_idx + i] = slice_sum(&nodes[next_start_idx..next_start_idx + NODE_SZ]);
        }
    }

    fn query_rec(&self, start_idx: usize, l: usize, r: usize, ql: usize, qr: usize) -> i64 {
        let length = r - l + 1;
        if length == NODE_SZ {
            // leaf: sum only the overlapping portion
            let from = ql.saturating_sub(l);
            let to = min(qr - l, NODE_SZ - 1);
            return slice_sum(&self.nodes[start_idx + from..=start_idx + to]);
        }

        if ql <= l && r <= qr {
            // total overlap at internal node
            return slice_sum(&self.nodes[start_idx..start_idx + NODE_SZ]);
        }

        // partial overlap at internal node
        let mut sum = 0;
        let chunk_size = length / NODE_SZ;
        let mut first = (ql.saturating_sub(l)) / chunk_size;
        let mut last = min((qr - l) / chunk_size, NODE_SZ - 1);

        // left boundary — partial overlap, recurse
        if ql > l + first * chunk_size {
            let next_start_idx = (start_idx + 1 + first) * NODE_SZ;
            let next_l = l + first * chunk_size;
            let next_r = next_l + chunk_size - 1;
            sum += self.query_rec(next_start_idx, next_l, next_r, ql, qr);
            first += 1;
        }
        // right boundary — partial overlap, recurse
        if last >= first && qr < l + (last + 1) * chunk_size - 1 {
            let next_start_idx = (start_idx + 1 + last) * NODE_SZ;
            let next_l = l + last * chunk_size;
            let next_r = next_l + chunk_size - 1;
            sum += self.query_rec(next_start_idx, next_l, next_r, ql, qr);
            if last > 0 {
                last -= 1;
            } else {
                return sum;
            }
        }
        // middle children — all total overlap, branchless contiguous sum
        if first <= last {
            sum += slice_sum(&self.nodes[start_idx + first..=start_idx + last]);
        }
        sum
    }

    fn update_rec(&mut self, start_idx: usize, l: usize, r: usize, pos: usize, val: i64) {
        let length = r - l + 1;
        if length == NODE_SZ {
            let offset = pos - l;
            self.nodes[start_idx + offset] = val;
            return;
        }

        let chunk_size = length / NODE_SZ;
        let i = (pos - l) / chunk_size;
        let next_start_idx = (start_idx + 1 + i) * NODE_SZ;
        let next_l = l + i * chunk_size;
        let next_r = next_l + chunk_size - 1;
        self.update_rec(next_start_idx, next_l, next_r, pos, val);
        self.nodes[start_idx + i] =
            slice_sum(&self.nodes[next_start_idx..next_start_idx + NODE_SZ]);
    }
}

impl SegTree for FriendlySegTree {
    fn build(items: &[i64]) -> Self {
        let n = max(NODE_SZ, round_to_next_power_of(items.len(), NODE_SZ));
        let mut nodes = vec![0; 4 * n]; // probably bounded above by 4
        Self::build_rec(&mut nodes, items, 0, 0, n - 1);
        Self { n, nodes }
    }

    fn query(&self, l: usize, r: usize) -> i64 {
        self.query_rec(0, 0, self.n - 1, l, r)
    }

    fn update(&mut self, pos: usize, val: i64) {
        self.update_rec(0, 0, self.n - 1, pos, val);
    }
}
