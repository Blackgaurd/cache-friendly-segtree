use cache_friendly_segtree::{
    friendly::FriendlySegTree, interface::SegTree, obvlivious::ObliviousSegTree,
};
use oorandom::Rand64;

const SEED: u64 = 42;
const MAX_VAL: i64 = 1_000_000;

fn gen_data(n: usize, seed: u64) -> Vec<i64> {
    let mut rng = Rand64::new(seed as u128);
    (0..n)
        .map(|_| (rng.rand_u64() as i64).rem_euclid(2 * MAX_VAL + 1) - MAX_VAL)
        .collect()
}

fn gen_ranges(n: usize, seed: u64, num_elements: usize) -> impl Iterator<Item = (usize, usize)> {
    let mut rng = Rand64::new(seed as u128);
    (0..n).map(move |_| {
        let range = rng.rand_range(0..(num_elements as u64)) as usize;
        let start = rng.rand_range(0..((num_elements - range) as u64)) as usize;
        (start, start + range)
    })
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 4 {
        eprintln!("Usage: {} <NUM_ELEMENTS> <NUM_QUERIES> <F|O>", args[0]);
        std::process::exit(1);
    }

    let num_elements: usize = args[1].parse().expect("NUM_ELEMENTS must be a valid usize");
    let num_queries: usize = args[2].parse().expect("NUM_QUERIES must be a valid usize");
    let tree_type = &args[3];

    let data = gen_data(num_elements, SEED);
    if tree_type == "F" {
        let friendly = FriendlySegTree::build(&data);
        for (start, end) in gen_ranges(num_queries, SEED, num_elements) {
            std::hint::black_box(friendly.query(start, end));
        }
    } else if tree_type == "O" {
        let oblivious = ObliviousSegTree::build(&data);
        for (start, end) in gen_ranges(num_queries, SEED, num_elements) {
            std::hint::black_box(oblivious.query(start, end));
        }
    }
}
