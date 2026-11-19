"""Варіант 3. Продажі менеджерів: функціональний конвеєр без мутацій."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from functools import reduce
from itertools import islice
from typing import Any, TypedDict


class Record(TypedDict, total=False):
    id: int
    name: str
    region: str
    sales: list[float]
    total: float
    rank: int


class Stats(TypedDict):
    count: int
    revenue: float
    avg_sales: float
    best: float


Stage = Callable[[Any], Any]


# --- композиція ---------------------------------------------------------------
def compose(*funcs: Stage) -> Stage:
    """compose(f, g, h)(x) == f(g(h(x))) - справа наліво."""
    return lambda x: reduce(lambda acc, f: f(acc), reversed(funcs), x)


def pipe(*funcs: Stage) -> Stage:
    """pipe(f, g, h)(x) == h(g(f(x))) - зліва направо (читається як конвеєр)."""
    return lambda x: reduce(lambda acc, f: f(acc), funcs, x)


# --- чисті трансформації (кожна - фабрика етапу) -----------------------------
def normalize_names() -> Callable[[Iterable[Record]], Iterator[Record]]:
    return lambda recs: map(
        lambda r: {**r, "name": str(r.get("name", "")).strip().title()}, recs
    )


def with_total() -> Callable[[Iterable[Record]], Iterator[Record]]:
    """total = сума всіх продажів менеджера."""
    return lambda recs: map(
        lambda r: {**r, "total": round(float(sum(r.get("sales", []))), 2)}, recs
    )


def apply_region_coef(
    coefs: Mapping[str, float], default: float = 1.0
) -> Callable[[Iterable[Record]], Iterator[Record]]:
    """Множить total на коефіцієнт регіону (якого немає в мапі - default)."""

    def _stage(recs: Iterable[Record]) -> Iterator[Record]:
        return (
            {
                **r,
                "total": round(
                    r.get("total", 0.0) * coefs.get(r.get("region", ""), default), 2
                ),
            }
            for r in recs
        )

    return _stage


def min_total(threshold: float) -> Callable[[Iterable[Record]], Iterator[Record]]:
    return lambda recs: filter(lambda r: r.get("total", 0.0) >= threshold, recs)


def sort_by_total_desc() -> Callable[[Iterable[Record]], list[Record]]:
    """Два ключі: total спадно, при рівності - id зростанням."""
    return lambda recs: sorted(
        recs, key=lambda r: (-r.get("total", 0.0), r.get("id", 0))
    )


def take(n: int) -> Callable[[Iterable[Record]], list[Record]]:
    return lambda recs: list(islice(recs, max(n, 0)))


def with_rank() -> Callable[[Iterable[Record]], list[Record]]:
    return lambda recs: [{**r, "rank": i} for i, r in enumerate(recs, start=1)]


# --- reduce-агрегація ---------------------------------------------------------
def reduce_stats(recs: Iterable[Record]) -> Stats:
    init: tuple[int, float, float] = (0, 0.0, 0.0)
    count, revenue, best = reduce(
        lambda acc, r: (
            acc[0] + 1,
            acc[1] + r.get("total", 0.0),
            max(acc[2], r.get("total", 0.0)),
        ),
        recs,
        init,
    )
    return {
        "count": count,
        "revenue": round(revenue, 2),
        "avg_sales": round(revenue / count, 2) if count else 0.0,
        "best": best,
    }


# --- збирання конвеєра -------------------------------------------------------
def build_pipeline(
    *,
    coefs: Mapping[str, float],
    threshold: float,
    top_n: int,
) -> Callable[[Iterable[Record]], list[Record]]:
    return compose(
        with_rank(),
        take(top_n),
        sort_by_total_desc(),
        min_total(threshold),
        apply_region_coef(coefs),
        with_total(),
        normalize_names(),
    )
