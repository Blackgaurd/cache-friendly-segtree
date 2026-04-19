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

fn bench_query_range(c: &mut Criterion) {
    let mut group = c.benchmark_group("query_range");
    group.measurement_time(Duration::from_secs(8));
    for &n in SIZES {
        let data = gen_data(n, 42);
        let oblivious = ObliviousSegTree::build(&data);
        let friendly = FriendlySegTree::build(&data);
        let l = n / 4;
        let r = 3 * n / 4 - 1;
        group.throughput(Throughput::Elements((n / 2) as u64));
        group.bench_function(BenchmarkId::new("oblivious", n), |b| {
            b.iter(|| black_box(oblivious.query(l, r)))
        });
        group.bench_function(BenchmarkId::new("friendly", n), |b| {
            b.iter(|| black_box(friendly.query(l, r)))
        });
    }
    group.finish();
}

criterion_group!(benches, bench_query_range);
criterion_main!(benches);
