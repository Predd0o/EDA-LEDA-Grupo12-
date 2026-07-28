mod lazy_recursive;

use rand::rngs::StdRng;
use rand::Rng;
use rand::SeedableRng;
use std::time::Instant;
use lazy_recursive::SegmentTree;

fn parse_arg(args: &[String], flag: &str) -> Option<String> {
    args.iter()
        .position(|a| a == flag)
        .map(|i| args[i + 1].clone())
}

fn parse_arg_usize(args: &[String], flag: &str, default: usize) -> usize {
    parse_arg(args, flag)
        .map(|v| v.parse::<usize>().expect(&format!("invalid {}", flag)))
        .unwrap_or(default)
}

fn load_operations(load: &str) -> Vec<&'static str> {
    match load {
        "query" => vec!["query_sum", "query_min", "query_max"],
        "update" => vec!["update_range", "update_point"],
        "mixed" => vec!["query_sum", "query_min", "query_max", "update_range", "update_point"],
        _ => panic!("invalid --load: use query, update, or mixed"),
    }
}

fn generate_values(distribution: &str, n: usize, seed: u64) -> Vec<i64> {
    let mut rng = StdRng::seed_from_u64(seed);
    match distribution {
        "random" => (0..n).map(|_| rng.gen_range(-1_000_000..=1_000_000)).collect(),
        "sorted" => (0..n).map(|x| x as i64).collect(),
        "nearly_sorted" => {
            let mut v: Vec<i64> = (0..n).map(|x| x as i64).collect();
            let swaps = n / 20;
            for _ in 0..swaps {
                let i = rng.gen_range(0..n);
                let j = rng.gen_range(0..n);
                v.swap(i, j);
            }
            v
        }
        "duplicates" => (0..n).map(|_| rng.gen_range(-1_000..=1_000)).collect(),
        "all_equal" => vec![0i64; n],
        _ => panic!(
            "invalid --distribution: use random, sorted, nearly_sorted, duplicates, all_equal"
        ),
    }
}

fn random_range(rng: &mut StdRng, n: usize) -> (usize, usize) {
    let l = rng.gen_range(0..n);
    let r = rng.gen_range(0..n);
    if l <= r {
        (l, r)
    } else {
        (r, l)
    }
}

fn main() {
    let args = std::env::args().collect::<Vec<_>>();

    let n = parse_arg_usize(&args, "--size", 100_000);
    let m = parse_arg_usize(&args, "--ops", n);
    let load_arg = parse_arg(&args, "--load").unwrap_or_else(|| "query".to_string());
    let load_ops = load_operations(&load_arg);
    let distribution = parse_arg(&args, "--distribution")
        .unwrap_or_else(|| "random".to_string());
    let seed: u64 = parse_arg(&args, "--seed")
        .map(|v| v.parse().expect("invalid --seed"))
        .unwrap_or(42);
    let warmup: usize = parse_arg_usize(&args, "--warmup", 1);
    let repetitions: usize = parse_arg_usize(&args, "--repetitions", 1);
    let output_format = parse_arg(&args, "--output").unwrap_or_else(|| "json".to_string());

    let values = generate_values(&distribution, n, seed);
    let is_csv = output_format == "csv";

    if is_csv {
        println!(
            "language,n,m,load,distribution,seed,op,time_ns"
        );
    }

    for _ in 0..warmup {
        let mut segtree = SegmentTree::build(&values);
        let mut rng = StdRng::seed_from_u64(seed.wrapping_add(1));
        for _ in 0..m {
            let op = load_ops[rng.gen_range(0..load_ops.len())];
            let (l, r) = random_range(&mut rng, n);
            match op {
                "query_sum" => { let _ = segtree.query_sum(l, r); }
                "query_min" => { let _ = segtree.query_min(l, r); }
                "query_max" => { let _ = segtree.query_max(l, r); }
                "update_range" => {
                    let value = rng.gen_range(-1_000..=1_000);
                    segtree.update_range(l, r, value);
                }
                "update_point" => {
                    let value = rng.gen_range(-1_000..=1_000);
                    segtree.update_point(l, value);
                }
                _ => {}
            }
        }
    }

    for _ in 0..repetitions {
        let build_start = Instant::now();
        let mut segtree = SegmentTree::build(&values);
        let build_time = build_start.elapsed();

        if is_csv {
            println!(
                "{},{},{},{},{},{},{},{}",
                "rust", n, m, load_arg, distribution, seed, "build", build_time.as_nanos()
            );
        } else {
            println!(
                r#"{{"language": "rust", "n": {}, "m": {}, "load": "{}", "distribution": "{}", "seed": {}, "op": "build", "time_ns": {}}}"#,
                n, m, load_arg, distribution, seed, build_time.as_nanos()
            );
        }

        let mut rng = StdRng::seed_from_u64(seed.wrapping_add(1));
        for _ in 0..m {
            let op = load_ops[rng.gen_range(0..load_ops.len())];
            let (l, r) = random_range(&mut rng, n);
            match op {
                "query_sum" => {
                    let start = Instant::now();
                    let _ = segtree.query_sum(l, r);
                    let time_ns = start.elapsed().as_nanos();
                    emit(&output_format, "rust", n, m, &load_arg, &distribution, seed, "query_sum", time_ns);
                }
                "query_min" => {
                    let start = Instant::now();
                    let _ = segtree.query_min(l, r);
                    let time_ns = start.elapsed().as_nanos();
                    emit(&output_format, "rust", n, m, &load_arg, &distribution, seed, "query_min", time_ns);
                }
                "query_max" => {
                    let start = Instant::now();
                    let _ = segtree.query_max(l, r);
                    let time_ns = start.elapsed().as_nanos();
                    emit(&output_format, "rust", n, m, &load_arg, &distribution, seed, "query_max", time_ns);
                }
                "update_range" => {
                    let value = rng.gen_range(-1_000..=1_000);
                    let start = Instant::now();
                    segtree.update_range(l, r, value);
                    let time_ns = start.elapsed().as_nanos();
                    emit(&output_format, "rust", n, m, &load_arg, &distribution, seed, "update_range", time_ns);
                }
                "update_point" => {
                    let value = rng.gen_range(-1_000..=1_000);
                    let start = Instant::now();
                    segtree.update_point(l, value);
                    let time_ns = start.elapsed().as_nanos();
                    emit(&output_format, "rust", n, m, &load_arg, &distribution, seed, "update_point", time_ns);
                }
                _ => {}
            }
        }
    }
}

fn emit(
    format: &str,
    language: &str,
    n: usize,
    m: usize,
    load: &str,
    distribution: &str,
    seed: u64,
    op: &str,
    time_ns: u128,
) {
    if format == "csv" {
        println!(
            "{},{},{},{},{},{},{},{}",
            language, n, m, load, distribution, seed, op, time_ns
        );
    } else {
        println!(
            r#"{{"language": "{}", "n": {}, "m": {}, "load": "{}", "distribution": "{}", "seed": {}, "op": "{}", "time_ns": {}}}"#,
            language, n, m, load, distribution, seed, op, time_ns
        );
    }
}