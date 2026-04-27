use std::{env, fs, path::Path};

fn main() {
    let node_sz: usize = env::var("SEGTREE_NODE_SZ")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(8);

    let out = format!("pub const NODE_SZ: usize = {};\n", node_sz);
    fs::write(Path::new("src/constants.rs"), out).unwrap();

    println!("cargo:rerun-if-env-changed=SEGTREE_NODE_SZ");
}
