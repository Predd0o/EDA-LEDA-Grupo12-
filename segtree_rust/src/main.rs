mod lazy_recursive;

use std::fs::File;
use std::io::{BufRead, BufReader};
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

#[derive(Debug, Clone)]
enum Op {
    QuerySum { l: usize, r: usize },
    QueryMin { l: usize, r: usize },
    QueryMax { l: usize, r: usize },
    UpdateRange { l: usize, r: usize, value: i64 },
    UpdatePoint { index: usize, value: i64 },
}

fn parse_input(path: &str) -> (usize, usize, Vec<i64>, Vec<Op>) {
    let file = File::open(path).expect(&format!("cannot open input file: {}", path));
    let reader = BufReader::new(file);
    let mut lines = reader.lines();

    let header = lines.next().unwrap().expect("empty input file");
    let parts: Vec<&str> = header.split_whitespace().collect();
    let n: usize = parts[0].parse().expect("invalid N in header");
    let m: usize = parts[1].parse().expect("invalid M in header");

    let values_line = lines.next().unwrap().expect("missing values line");
    let values: Vec<i64> = values_line
        .split_whitespace()
        .take(n)
        .map(|s| s.parse().expect("invalid value"))
        .collect();

    let mut ops = Vec::with_capacity(m);
    for line in lines {
        let line = line.expect("failed to read line");
        let tokens: Vec<&str> = line.split_whitespace().collect();
        if tokens.is_empty() {
            continue;
        }
        match tokens[0] {
            "query" => {
                let l: usize = tokens[1].parse().expect("invalid l");
                let r: usize = tokens[2].parse().expect("invalid r");
                ops.push(Op::QuerySum { l, r });
                ops.push(Op::QueryMin { l, r });
                ops.push(Op::QueryMax { l, r });
            }
            "update_range" => {
                let l: usize = tokens[1].parse().expect("invalid l");
                let r: usize = tokens[2].parse().expect("invalid r");
                let value: i64 = tokens[3].parse().expect("invalid value");
                ops.push(Op::UpdateRange { l, r, value });
            }
            "update_point" => {
                let index: usize = tokens[1].parse().expect("invalid index");
                let value: i64 = tokens[2].parse().expect("invalid value");
                ops.push(Op::UpdatePoint { index, value });
            }
            _ => {}
        }
    }

    (n, m, values, ops)
}

fn load_operations(load: &str, all_ops: &[Op]) -> Vec<Op> {
    match load {
        "query" => all_ops
            .iter()
            .filter(|op| matches!(op, Op::QuerySum { .. } | Op::QueryMin { .. } | Op::QueryMax { .. }))
            .cloned()
            .collect(),
        "update" => all_ops
            .iter()
            .filter(|op| matches!(op, Op::UpdateRange { .. } | Op::UpdatePoint { .. }))
            .cloned()
            .collect(),
        "mixed" => all_ops.to_vec(),
        _ => panic!("invalid --load: use query, update, or mixed"),
    }
}

fn emit(
    language: &str,
    n: usize,
    m: usize,
    load: &str,
    input_file: &str,
    ops_executed: usize,
    op: &str,
    time_ns: u128,
    nodes_visited: u64,
) {
    println!(
        "{},{},{},{},{},{},{},{},{}",
        language, n, m, load, input_file, ops_executed, op, time_ns, nodes_visited
    );
}

fn main() {
    let args = std::env::args().collect::<Vec<_>>();

    const WARMUP: usize = 5;

    let input_path = parse_arg(&args, "--input")
        .expect("required: --input <path>");
    let load_arg = parse_arg(&args, "--load").unwrap_or_else(|| "query".to_string());
    let repetitions: usize = parse_arg_usize(&args, "--repetitions", 1);

    let (n, m, values, all_ops) = parse_input(&input_path);
    let load_ops = load_operations(&load_arg, &all_ops);
    let ops_executed = load_ops.len();

    for _ in 0..WARMUP {
        let mut segtree = SegmentTree::build(&values);
        for op in &load_ops {
            match op {
                Op::QuerySum { l, r } => { let _ = segtree.query_sum(*l, *r); }
                Op::QueryMin { l, r } => { let _ = segtree.query_min(*l, *r); }
                Op::QueryMax { l, r } => { let _ = segtree.query_max(*l, *r); }
                Op::UpdateRange { l, r, value } => { segtree.update_range(*l, *r, *value); }
                Op::UpdatePoint { index, value } => { segtree.update_point(*index, *value); }
            }
        }
    }

    for _ in 0..repetitions {
        let build_start = Instant::now();
        let mut segtree = SegmentTree::build(&values);
        let build_time = build_start.elapsed();
        let build_nodes = segtree.counters().nodes_visited;

        emit("rust", n, m, &load_arg, &input_path, ops_executed, "build", build_time.as_nanos(), build_nodes);

        segtree.reset_counters();
        let batch_start = Instant::now();
        for op in &load_ops {
            match op {
                Op::QuerySum { l, r } => { let _ = segtree.query_sum(*l, *r); }
                Op::QueryMin { l, r } => { let _ = segtree.query_min(*l, *r); }
                Op::QueryMax { l, r } => { let _ = segtree.query_max(*l, *r); }
                Op::UpdateRange { l, r, value } => { segtree.update_range(*l, *r, *value); }
                Op::UpdatePoint { index, value } => { segtree.update_point(*index, *value); }
            }
        }
        let batch_time = batch_start.elapsed();
        let batch_nodes = segtree.counters().nodes_visited;

        emit("rust", n, m, &load_arg, &input_path, ops_executed, "batch_ops", batch_time.as_nanos(), batch_nodes);
    }
}