"""Делит landmarks_300w.csv на исходную часть и порции «новых» данных.

Даты в 300W нет, поэтому делим случайно с фиксированным seed.
Запуск из корня репозитория:
    python src/facekp/data/split.py
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="data/raw/landmarks_300w.csv")
    ap.add_argument("--initial", default="data/interim/initial.csv")
    ap.add_argument("--incoming", default="data/incoming")
    ap.add_argument("--initial-frac", type=float, default=0.6)
    ap.add_argument("--batches", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.src)

    # перемешиваем внутри indoor и outdoor отдельно, чтобы доли были одинаковые везде
    rng = np.random.default_rng(args.seed)
    parts = {"initial": [], **{i: [] for i in range(args.batches)}}
    for _, g in df.groupby("subset"):
        g = g.iloc[rng.permutation(len(g))]
        n_init = round(len(g) * args.initial_frac)
        parts["initial"].append(g.iloc[:n_init])
        rest = g.iloc[n_init:]
        for i, idx in enumerate(np.array_split(np.arange(len(rest)), args.batches)):
            parts[i].append(rest.iloc[idx])

    summary = {}
    initial = pd.concat(parts["initial"]).sort_values("image")
    Path(args.initial).parent.mkdir(parents=True, exist_ok=True)
    initial.to_csv(args.initial, index=False)
    summary[args.initial] = len(initial)

    inc = Path(args.incoming)
    inc.mkdir(parents=True, exist_ok=True)
    for i in range(args.batches):
        batch = pd.concat(parts[i]).sort_values("image")
        path = inc / f"batch_{i + 1:02d}.csv"
        batch.to_csv(path, index=False)
        summary[path.as_posix()] = len(batch)

    # проверка: ничего не потерялось и не задвоилось
    total = sum(summary.values())
    assert total == len(df), f"строк {total}, а должно быть {len(df)}"

    for path, n in summary.items():
        print(f"{path}: {n} строк, sha256 {sha256(Path(path))[:12]}")
    Path(inc / "split_info.json").write_text(json.dumps(
        {"seed": args.seed, "initial_frac": args.initial_frac, "files": summary},
        ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
