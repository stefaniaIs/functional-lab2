from copy import deepcopy

import pytest

from core import (
    Record,
    apply_region_coef,
    build_pipeline,
    compose,
    min_total,
    pipe,
    reduce_stats,
    sort_by_total_desc,
    take,
    with_total,
)

COEFS = {"North": 1.1, "South": 0.95}


@pytest.fixture
def records() -> list[Record]:
    return [
        {"id": 1, "name": " olena ", "region": "North", "sales": [500, 700, 300]},
        {"id": 2, "name": "petro", "region": "South", "sales": [1200, 800]},
        {"id": 3, "name": "iryna", "region": "West", "sales": [400, 300]},
        {"id": 4, "name": "taras", "region": "North", "sales": [900, 950]},
        {"id": 5, "name": "oksana", "region": "East", "sales": [2000]},
        {"id": 6, "name": "max", "region": "West", "sales": []},
    ]


def test_with_total_and_coef(records: list[Record]) -> None:
    out = list(apply_region_coef(COEFS)(with_total()(records)))
    assert [r["total"] for r in out] == [1650.0, 1900.0, 700.0, 2035.0, 2000.0, 0.0]


def test_top_n(records: list[Record]) -> None:
    res = build_pipeline(coefs=COEFS, threshold=1000, top_n=3)(records)
    assert [r["id"] for r in res] == [4, 5, 2]
    assert [r["rank"] for r in res] == [1, 2, 3]
    assert res[0]["name"] == "Taras"


def test_top_n_bigger_than_data(records: list[Record]) -> None:
    res = build_pipeline(coefs={}, threshold=0, top_n=100)(records)
    assert len(res) == len(records)


def test_sort_tiebreak_by_id() -> None:
    recs: list[Record] = [{"id": 2, "total": 10.0}, {"id": 1, "total": 10.0}]
    assert [r["id"] for r in sort_by_total_desc()(recs)] == [1, 2]


def test_filter_threshold(records: list[Record]) -> None:
    out = list(min_total(1000)(with_total()(records)))
    assert {r["id"] for r in out} == {1, 2, 4, 5}


def test_no_mutation(records: list[Record]) -> None:
    original = deepcopy(records)
    build_pipeline(coefs=COEFS, threshold=0, top_n=10)(records)
    assert records == original


def test_reduce_stats() -> None:
    recs: list[Record] = [{"total": 100.0}, {"total": 300.0}, {"total": 200.0}]
    assert reduce_stats(recs) == {
        "count": 3,
        "revenue": 600.0,
        "avg_sales": 200.0,
        "best": 300.0,
    }


def test_reduce_stats_empty() -> None:
    assert reduce_stats([]) == {
        "count": 0,
        "revenue": 0.0,
        "avg_sales": 0.0,
        "best": 0.0,
    }


def test_compose_vs_pipe() -> None:
    inc = lambda x: x + 1  # noqa: E731
    dbl = lambda x: x * 2  # noqa: E731
    assert compose(dbl, inc)(3) == 8  # dbl(inc(3))
    assert pipe(dbl, inc)(3) == 7  # inc(dbl(3))


def test_take_zero_and_negative() -> None:
    assert take(0)([{"id": 1}]) == []
    assert take(-5)([{"id": 1}]) == []
