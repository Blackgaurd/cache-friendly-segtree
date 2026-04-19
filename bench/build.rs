use cache_friendly_segtree::{
    friendly::FriendlySegTree,
    interface::SegTree,
    obvlivious::ObliviousSegTree,
};
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion, Throughput};
use oorandom::Rand64;

const MAX_VAL: i64 = 1_000_000;

/// Generates `n` pseudorandom i64 values in `[-MAX_VAL, MAX_VAL]` from the given seed.
/// The bounded range ensures the sum of any generated slice fits within i64.
fn gen_data(n: usize, seed: u64) -> Vec<i64> {
    let mut rng = Rand64::new(seed as u128);
    (0..n)
        .map(|_| (rng.rand_u64() as i64).rem_euclid(2 * MAX_VAL + 1) - MAX_VAL)
        .collect()
}

const SIZES: &[usize] = &[16, 64, 256, 1024, 4096, 16384, 65536, 262144];

/// Benchmarks wall-clock build time for both segment tree implementations.
fn bench_build(c: &mut Criterion) {
    let mut group = c.benchmark_group("build");
    for &n in SIZES {
        let data = gen_data(n, 42);
        group.throughput(Throughput::Elements(n as u64));
        group.bench_with_input(BenchmarkId::new("oblivious", n), &data, |b, d| {
            b.iter(|| ObliviousSegTree::build(d))
        });
        group.bench_with_input(BenchmarkId::new("friendly", n), &data, |b, d| {
            b.iter(|| FriendlySegTree::build(d))
        });
    }
    group.finish();
}

criterion_group!(benches, bench_build);
criterion_main!(benches);
