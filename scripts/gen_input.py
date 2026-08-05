import argparse
import os
import random


def generate_values(distribution, n, seed):
    rng = random.Random(seed)
    if distribution == "random":
        return [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    elif distribution == "sorted":
        return list(range(n))
    elif distribution == "nearly_sorted":
        v = list(range(n))
        swaps = n // 20
        for _ in range(swaps):
            i = rng.randint(0, n - 1)
            j = rng.randint(0, n - 1)
            v[i], v[j] = v[j], v[i]
        return v
    elif distribution == "duplicates":
        return [rng.randint(-1_000, 1_000) for _ in range(n)]
    elif distribution == "all_equal":
        return [0] * n
    else:
        raise ValueError(
            f"invalid distribution: {distribution}. "
            "use random, sorted, nearly_sorted, duplicates, all_equal"
        )


def generate_operations(load, m, n, seed, query_ratio=1 / 3, update_range_ratio=1 / 3):
    rng = random.Random(seed + 1)
    ops = []
    for _ in range(m):
        if load == "query":
            l = rng.randint(0, n - 1)
            r = rng.randint(0, n - 1)
            if l > r:
                l, r = r, l
            ops.append(f"query {l} {r}")
        elif load == "update":
            op_type = rng.choice(["update_range", "update_point"])
            if op_type == "update_range":
                l = rng.randint(0, n - 1)
                r = rng.randint(0, n - 1)
                if l > r:
                    l, r = r, l
                value = rng.randint(-1_000, 1_000)
                ops.append(f"update_range {l} {r} {value}")
            else:
                index = rng.randint(0, n - 1)
                value = rng.randint(-1_000, 1_000)
                ops.append(f"update_point {index} {value}")
        elif load == "mixed":
            op_type = rng.choices(
                ["query", "update_range", "update_point"],
                weights=[query_ratio, update_range_ratio, 1 - query_ratio - update_range_ratio],
                k=1,
            )[0]
            if op_type == "query":
                l = rng.randint(0, n - 1)
                r = rng.randint(0, n - 1)
                if l > r:
                    l, r = r, l
                ops.append(f"query {l} {r}")
            elif op_type == "update_range":
                l = rng.randint(0, n - 1)
                r = rng.randint(0, n - 1)
                if l > r:
                    l, r = r, l
                value = rng.randint(-1_000, 1_000)
                ops.append(f"update_range {l} {r} {value}")
            else:
                index = rng.randint(0, n - 1)
                value = rng.randint(-1_000, 1_000)
                ops.append(f"update_point {index} {value}")
    return ops


def main():
    parser = argparse.ArgumentParser(
        description="Generate deterministic input files for segment tree benchmarks"
    )
    parser.add_argument("--n", type=int, required=True, help="Array size (N)")
    parser.add_argument(
        "--m", type=int, default=None, help="Number of operations (M, default: N)"
    )
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument(
        "--distribution",
        default="random",
        choices=["random", "sorted", "nearly_sorted", "duplicates", "all_equal"],
        help="Data distribution",
    )
    parser.add_argument(
        "--load",
        default="query",
        choices=["query", "update", "mixed"],
        help="Operation load type",
    )
    parser.add_argument(
        "--query-ratio",
        type=float,
        default=1 / 3,
        help="Proportion of query operations in mixed load (default: 0.33)",
    )
    parser.add_argument(
        "--update-range-ratio",
        type=float,
        default=1 / 3,
        help="Proportion of update_range operations in mixed load (default: 0.33)",
    )
    parser.add_argument(
        "--output", default="data/", help="Output directory"
    )
    args = parser.parse_args()

    n = args.n
    m = args.m if args.m is not None else n
    distribution = args.distribution
    load = args.load
    seed = args.seed
    query_ratio = args.query_ratio
    update_range_ratio = args.update_range_ratio

    if load == "mixed":
        total = query_ratio + update_range_ratio
        if total > 1.0:
            raise ValueError(
                f"query-ratio + update-range-ratio must be <= 1.0, got {total}"
            )

    values = generate_values(distribution, n, seed)
    ops = generate_operations(load, m, n, seed, query_ratio, update_range_ratio)

    if load == "mixed":
        filename = f"input_n{n}_m{m}_s{seed}_{distribution}_mixed_5050.txt"
    else:
        filename = f"input_n{n}_m{m}_s{seed}_{distribution}_{load}.txt"
    filepath = os.path.join(args.output, filename)

    os.makedirs(args.output, exist_ok=True)

    with open(filepath, "w") as f:
        f.write(f"{n} {len(ops)}\n")
        f.write(" ".join(map(str, values)) + "\n")
        for op in ops:
            f.write(op + "\n")

    print(f"Generated: {filepath}")


if __name__ == "__main__":
    main()