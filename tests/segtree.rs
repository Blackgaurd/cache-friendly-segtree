use cache_friendly_segtree::friendly::FriendlySegTree;
use cache_friendly_segtree::interface::SegTree;
use cache_friendly_segtree::obvlivious::ObliviousSegTree;

macro_rules! segtree_tests {
    ($T:ty, $mod:ident) => {
        mod $mod {
            use super::*;

            #[test]
            fn build_only() {
                let _ = <$T>::build(&[1, 2, 3, 4, 5]);
            }

            #[test]
            fn build_only_65() {
                let data: Vec<i64> = (1..=65).collect();
                let _ = <$T>::build(&data);
            }

            #[test]
            fn sum_all() {
                let t = <$T>::build(&[1, 2, 3, 4, 5]);
                assert_eq!(t.query(0, 4), 15);
            }

            #[test]
            fn sum_range() {
                let t = <$T>::build(&[1, 2, 3, 4, 5]);
                assert_eq!(t.query(1, 3), 9);
            }

            #[test]
            fn sum_single() {
                let t = <$T>::build(&[1, 2, 3, 4, 5]);
                assert_eq!(t.query(2, 2), 3);
            }

            #[test]
            fn update_then_query() {
                let mut t = <$T>::build(&[1, 2, 3, 4, 5]);
                t.update(2, 10);
                assert_eq!(t.query(0, 4), 22);
                assert_eq!(t.query(1, 3), 16);
            }

            #[test]
            fn update_first() {
                let mut t = <$T>::build(&[1, 2, 3, 4, 5]);
                t.update(0, 0);
                assert_eq!(t.query(0, 4), 14);
            }

            #[test]
            fn update_last() {
                let mut t = <$T>::build(&[1, 2, 3, 4, 5]);
                t.update(4, 0);
                assert_eq!(t.query(0, 4), 10);
            }

            #[test]
            fn single_element_query() {
                let t = <$T>::build(&[42]);
                assert_eq!(t.query(0, 0), 42);
            }

            #[test]
            fn single_element_update() {
                let mut t = <$T>::build(&[42]);
                t.update(0, 7);
                assert_eq!(t.query(0, 0), 7);
            }
        }
    };
}

segtree_tests!(ObliviousSegTree, oblivious_tests);
segtree_tests!(FriendlySegTree, friendly_tests);
