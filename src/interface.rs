pub trait SegTree {
    fn build(items: &[i64]) -> Self;

    fn query(&self, l: usize, r: usize) -> i64;

    fn update(&mut self, index: usize, val: i64);
}
