use cache_friendly_segtree::{
    friendly::FriendlySegTree,
    interface::SegTree,
    obvlivious::ObliviousSegTree,
};
use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion, Throughput};
use std::time::Duration;
use oorandom::Rand64;

const MAX_VAL: i64 = 1_000_000;

fn gen_data(n: usize, seed: u64) -> Vec<i64> {
    let mut rng = Rand64::new(seed as u128);
    (0..n)
        .map(|_| (rng.rand_u64() as i64).rem_euclid(2 * MAX_VAL + 1) - MAX_VAL)
        .collect()
}

const SIZES: &[usize] = &[4, 16, 64, 65536, 262144, 1048576];

fn bench_query_point(c: &mut Criterion) {
    let mut group = c.benchmark_group("query_point");
    group.measurement_time(Duration::from_secs(8));
    for &n in SIZES {
        let data = gen_data(n, 42);
        let oblivious = ObliviousSegTree::build(&data);
        let friendly = FriendlySegTree::build(&data);
        let idx = n / 2;
        group.throughput(Throughput::Elements(1));
        group.bench_function(BenchmarkId::new("oblivious", n), |b| {
            b.iter(|| black_box(oblivious.query(idx, idx)))
        });
        group.bench_function(BenchmarkId::new("friendly", n), |b| {
            b.iter(|| black_box(friendly.query(idx, idx)))
        });
    }
    group.finish();
}

criterion_group!(benches, bench_query_point);
criterion_main!(benches);
