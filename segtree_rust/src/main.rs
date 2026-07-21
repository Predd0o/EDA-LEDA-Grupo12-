mod lazy_recursive;

use std::time::Instant;
use lazy_recursive::SegmentTree;

fn main() {
    let args = std::env::args().collect::<Vec<_>>();
    let n = args
        .iter()
        .position(|a| a == "--size")
        .map(|i| args[i + 1].parse::<usize>().expect("invalid --size"))
        .unwrap_or(100_000);
    let m = args
        .iter()
        .position(|a| a == "--ops")
        .map(|i| args[i + 1].parse::<usize>().expect("invalid --ops"))
        .unwrap_or(n);
    let load = args
        .iter()
        .position(|a| a == "--load")
        .map(|i| args[i + 1].as_str())
        .unwrap_or("query");

    let values: Vec<i64> = (0..n).map(|x| x as i64).collect();

    let start = Instant::now();
    let mut segtree = SegmentTree::build(&values);
    let build_time = start.elapsed();

    let start = Instant::now();
    segtree.query_sum(0, n - 1);
    let query_sum_time = start.elapsed();

    let start = Instant::now();
    segtree.query_min(0, n - 1);
    let query_min_time = start.elapsed();

    let start = Instant::now();
    segtree.query_max(0, n - 1);
    let query_max_time = start.elapsed();

    let start = Instant::now();
    for _ in 0..m {
        segtree.update_range(0, n - 1, 0);
    }
    let update_range_time = start.elapsed();

    let start = Instant::now();
    segtree.update_point(0, 0);
    let update_point_time = start.elapsed();

    println!(
        r#"{{"language": "rust", "n": {}, "m": {}, "load": "{}", "op": "build", "time_ns": {}}}"#,
        n,
        m,
        load,
        build_time.as_nanos()
    );
    println!(
        r#"{{"language": "rust", "n": {}, "m": {}, "load": "{}", "op": "query_sum", "time_ns": {}}}"#,
        n,
        m,
        load,
        query_sum_time.as_nanos()
    );
    println!(
        r#"{{"language": "rust", "n": {}, "m": {}, "load": "{}", "op": "query_min", "time_ns": {}}}"#,
        n,
        m,
        load,
        query_min_time.as_nanos()
    );
    println!(
        r#"{{"language": "rust", "n": {}, "m": {}, "load": "{}", "op": "query_max", "time_ns": {}}}"#,
        n,
        m,
        load,
        query_max_time.as_nanos()
    );
    println!(
        r#"{{"language": "rust", "n": {}, "m": {}, "load": "{}", "op": "update_range", "time_ns": {}}}"#,
        n,
        m,
        load,
        update_range_time.as_nanos()
    );
    println!(
        r#"{{"language": "rust", "n": {}, "m": {}, "load": "{}", "op": "update_point", "time_ns": {}}}"#,
        n,
        m,
        load,
        update_point_time.as_nanos()
    );
}