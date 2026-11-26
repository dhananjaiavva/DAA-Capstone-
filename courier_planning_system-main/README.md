# Courier Planning System (DAA Project)

A standard-library Python CLI that combines Merge Sort, 0/1 Knapsack dynamic programming, a weighted road graph, Dijkstra shortest paths, and a Nearest Neighbour TSP approximation. No website or third-party package is required.

## Project contents

- `src/courier.py` — algorithms, end-to-end planner, CLI and benchmark runner.
- `data/parcels.csv` — 12 sample parcels with destination, integer kg weight, value, priority and deadline.
- `data/road_network.json` — weighted undirected road graph with seven locations.
- `tests/test_courier.py` — correctness checks for sorting, packing, shortest paths and route output.
- `evidence/` — computed console trace, benchmark CSV, and SVG runtime chart.
- `reports/` — final project report in PDF, printable HTML, and Markdown.

## Requirements and execution

Python 3.10 or newer; only the Python standard library is used.

From this folder run:

```bash
python src/courier.py
python src/courier.py --capacity 35
python -m unittest discover -s tests -v
python src/courier.py --benchmark
```

Use alternate input files with `--parcels path/to/file.csv` and `--graph path/to/file.json`. Benchmark output defaults to `evidence/benchmark_results.csv`; override with `--out path.csv`.

## Algorithm flow

```text
CSV parcels -> Merge Sort by priority, deadline, ID
            -> 0/1 Knapsack chooses maximum-value feasible subset
JSON road graph -> Dijkstra shortest-path distances
Selected distinct destinations -> Nearest Neighbour route on shortest-path metric closure
            -> trip plan, trace, and runtime evidence
```

Knapsack decides **which parcels** fit. Routing decides **in what visit order** to serve the distinct destinations of those parcels. A selected destination may have multiple parcels, all delivered on that stop.

See `reports/FINAL_PROJECT_REPORT.html` or the Markdown version for design, all five assignment phases, analysis, results, limitations, and future work.
