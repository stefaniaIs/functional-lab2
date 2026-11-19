"""CLI: читання JSON, запуск конвеєра, друк рейтингу (лише I/O)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import Record, build_pipeline, reduce_stats


def parse_coefs(items: list[str]) -> dict[str, float]:
    return {k: float(v) for k, v in (s.split("=", 1) for s in items)}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Рейтинг менеджерів з продажу")
    p.add_argument("--data", default=str(Path(__file__).with_name("sample_data.json")))
    p.add_argument("--top", type=int, default=3)
    p.add_argument("--min", dest="threshold", type=float, default=1000.0)
    p.add_argument(
        "--coef",
        nargs="*",
        default=["North=1.1", "South=0.95"],
        help="регіональні коефіцієнти: Region=1.1",
    )
    args = p.parse_args(argv)

    records: list[Record] = json.loads(Path(args.data).read_text(encoding="utf-8"))
    run = build_pipeline(
        coefs=parse_coefs(args.coef), threshold=args.threshold, top_n=args.top
    )
    ranking = run(records)

    print(f"Top-{args.top} менеджерів (мін. {args.threshold}):")
    for r in ranking:
        print(f"  #{r['rank']} {r['name']:<10} {r['region']:<6} {r['total']:>10.2f}")
    print("Статистика:", reduce_stats(ranking))


if __name__ == "__main__":
    main()
