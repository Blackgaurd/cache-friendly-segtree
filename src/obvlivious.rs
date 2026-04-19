//! Naive cache-oblivious segtree implementation.

use crate::interface::SegTree;

#[derive(Debug)]
pub struct ObliviousSegTree {
    n: usize,
    nodes: Vec<i64>,
}

// helper functions
impl ObliviousSegTree {
    fn build_rec(nodes: &mut [i64], items: &[i64], idx: usize, l: usize, r: usize) {
        if l == r {
            nodes[idx] = items[l];
            return;
        }

        let mid = (l + r) / 2;
        Self::build_rec(nodes, items, idx * 2, l, mid);
        Self::build_rec(nodes, items, idx * 2 + 1, mid + 1, r);

        nodes[idx] = nodes[idx * 2] + nodes[idx * 2 + 1];
    }

    fn query_rec(&self, idx: usize, l: usize, r: usize, ql: usize, qr: usize) -> i64 {
        if ql > r || qr < l {
            // no overlap
            return 0;
        }
        if ql <= l && r <= qr {
            // total overlap
            return self.nodes[idx];
        }

        let mid = (l + r) / 2;
        self.query_rec(idx * 2, l, mid, ql, qr) + self.query_rec(idx * 2 + 1, mid + 1, r, ql, qr)
    }

    fn update_rec(&mut self, idx: usize, l: usize, r: usize, pos: usize, val: i64) {
        if l == r {
            self.nodes[idx] = val;
            return;
        }

        let mid = (l + r) / 2;
        if pos <= mid {
            self.update_rec(idx * 2, l, mid, pos, val);
        } else {
            self.update_rec(idx * 2 + 1, mid + 1, r, pos, val);
        }

        self.nodes[idx] = self.nodes[idx * 2] + self.nodes[idx * 2 + 1];
    }
}

impl SegTree for ObliviousSegTree {
    fn build(items: &[i64]) -> Self {
        let n = items.len();
        let mut nodes = vec![0; 4 * n];
        Self::build_rec(&mut nodes, items, 1, 0, n - 1);
        Self { n, nodes }
    }

    fn query(&self, l: usize, r: usize) -> i64 {
        self.query_rec(1, 0, self.n - 1, l, r)
    }

    fn update(&mut self, pos: usize, val: i64) {
        self.update_rec(1, 0, self.n - 1, pos, val);
    }
}
