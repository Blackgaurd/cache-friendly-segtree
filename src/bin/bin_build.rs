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

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        eprintln!("Usage: {} <NUM_ELEMENTS> <F|O>", args[0]);
        std::process::exit(1);
    }

    let num_elements: usize = args[1].parse().expect("NUM_ELEMENTS must be a valid usize");
    let tree_type = &args[2];

    let data = gen_data(num_elements, SEED);
    if tree_type == "F" {
        std::hint::black_box(FriendlySegTree::build(&data));
    } else if tree_type == "O" {
        std::hint::black_box(ObliviousSegTree::build(&data));
    }
}
