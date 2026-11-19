# Лабораторна робота №2 — Функції вищого порядку, lambda, композиція

**Варіант 3. Продажі менеджерів.** Іщенко Стефанія, ФеП-22.

Запис: `{id, name, region, sales: list[float]}`.

Конвеєр (зібраний через `compose`, є також `pipe`):
1. `normalize_names` — ім'я в Title Case (`map` + lambda);
2. `with_total` — загальний продаж = `sum(sales)` (`map`);
3. `apply_region_coef(coefs)` — регіональний коефіцієнт (генераторний вираз);
4. `min_total(threshold)` — відкинути менеджерів з малим результатом (`filter` + lambda);
5. `sort_by_total_desc` — сортування за двома ключами: total ↓, id ↑;
6. `take(n)` — Top-N (`itertools.islice`);
7. `with_rank` — номер у рейтингу.

`reduce_stats` (через `functools.reduce`): `count`, `revenue`, `avg_sales`, `best`.

Жодна функція не змінює вхідні записи — кожен етап створює нові словники `{**r, ...}`.

## Файли
- `core.py` — чисті функції; `main.py` — CLI та друк; `sample_data.json` — дані;
- `tests/test_core.py` — Top-N, немутація, reduce, compose/pipe, граничні випадки.

## Запуск
```bash
pip install -r requirements.txt
pytest -q
mypy . && black --check . && ruff check .
python main.py --top 3 --min 1000 --coef North=1.1 South=0.95
```
