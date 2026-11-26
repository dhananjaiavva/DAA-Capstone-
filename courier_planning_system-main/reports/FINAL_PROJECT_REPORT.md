# Intelligent Courier Planning System
## Design and Analysis of Algorithms — Final Project Report

**Project type:** Integrated Python CLI prototype  
**Algorithms:** Merge Sort, 0/1 Knapsack DP, Dijkstra, Nearest Neighbour TSP approximation  
**Runtime:** Python 3.10+ standard library  

## Abstract

This project models one courier vehicle leaving a depot, selecting a feasible collection of parcels, and visiting the selected customers before returning. It combines four algorithmic techniques in a single reproducible application. The packing stage exactly maximizes the total parcel value subject to a vehicle weight limit. The route stage computes shortest road distances and uses a greedy Nearest Neighbour heuristic to approximate a low-distance closed tour. The stages are deliberately distinct: parcel selection is not a routing constraint, and the heuristic route does not claim global optimality.

## Phase 1 — Courier Problem Design and Planning (20 marks)

### Problem definition

Given parcels, a vehicle capacity, a depot, and a weighted road graph, produce (1) a prioritized parcel list, (2) the maximum-value feasible subset for one trip, (3) shortest paths in the network, and (4) an approximate ordered tour through the selected customers.

### Data model

| Entity | Fields | Meaning |
|---|---|---|
| Parcel | ID, destination, weight (kg), value, priority, deadline | A candidate delivery; weights and values are positive integers |
| Location | Unique string node | Depot or customer location |
| Road | Endpoints, distance (km) | Positive, undirected edge; missing edge means no direct road |
| Vehicle | Capacity (kg) | Maximum total parcel weight carried |

The road graph is sparse adjacency data constructed from the JSON edge list. For routing among stops, Dijkstra distances form a complete metric closure: an edge between any reachable pair has the length of its shortest road path. The reported route distance uses these shortest paths, not straight-line distances.

### Integrated design

`parcels.csv -> Merge Sort -> 0/1 Knapsack -> unique selected stops -> Dijkstra distances -> Nearest Neighbour -> closed route`.

Priority sorting is useful for transparent dispatch order and deterministic tie-breaking. The knapsack objective is value maximization; priority and deadline do not force inclusion. If priorities must be binding, the objective or constraints would need to change. The route stage starts and ends at Depot.

## Phase 2 — Package Prioritization and Box Filling (20 marks)

Merge Sort orders by descending priority, then ascending deadline, then parcel ID. Its stable divide-and-conquer structure gives O(n log n) time and O(n) auxiliary memory. The final ID tie-break makes displayed output deterministic.

The 0/1 Knapsack recurrence is `DP[i,c] = max(DP[i-1,c], DP[i-1,c-w_i] + v_i)` when parcel i fits, otherwise `DP[i,c] = DP[i-1,c]`. Each parcel is either selected once or omitted. The implementation uses O(nW) time and O(nW) memory for n parcels and integer capacity W, then backtracks to recover selected parcels. This is exact for the modeled integer weights and values.

## Phase 3 — Route Maker and Graph Processing (20 marks)

Dijkstra's algorithm runs from a source location on a positive-weight graph. With an adjacency list and binary heap it takes O((V+E) log V) time and O(V+E) space. It provides shortest road distances and predecessors, from which a road path can be reconstructed.

Nearest Neighbour repeatedly selects the closest unvisited destination under the shortest-path metric and finally returns to the depot. It is an approximation for the metric TSP and has O(k^2) selection work with k stops, plus repeated shortest-path calculations in this straightforward implementation. It does not guarantee the optimal tour. The graph is assumed connected for the supplied depot and sample customer set.

## Phase 4 — System Integration and Testing (20 marks)

The CLI loads CSV and JSON inputs, validates positive road lengths, runs each component, and prints a computed plan. Tests cover sort ordering, a known knapsack optimum, a known shortest-path distance, route closure, and sample data loading. Run `python -m unittest discover -s tests -v` from the project folder.

The sample contains 12 parcels, seven graph nodes, and a configurable 30 kg default vehicle. The saved trace in `evidence/sample_run.txt` shows the output generated from these input files. All displayed selections, path lengths, and totals are computed at run time.

## Phase 5 — Performance Analysis, Results and Submission (20 marks)

The benchmark uses deterministic synthetic inputs at small (40 parcels, 12 nodes), medium (160, 30), and large (500, 65) scales. Each algorithm is timed using Python `time.perf_counter`; the benchmark reports one measurement per scale, so values are indicative rather than statistically conclusive. Knapsack capacity is fixed at 100 kg to show its dependence on both n and W. Dijkstra is timed for one source; route approximation uses up to 15 stops. See `evidence/benchmark_results.csv` and `evidence/runtime_chart.svg`.

| Component | Small | Medium | Large |
|---|---:|---:|---:|
| Merge Sort | See benchmark CSV | See benchmark CSV | See benchmark CSV |
| Knapsack DP | See benchmark CSV | See benchmark CSV | See benchmark CSV |
| Dijkstra | See benchmark CSV | See benchmark CSV | See benchmark CSV |
| Nearest Neighbour | See benchmark CSV | See benchmark CSV | See benchmark CSV |

Execution evidence is retained as a text trace rather than a screenshot, making it readable and reproducible from the included source and data. The SVG chart visualizes measured runtimes on a logarithmic scale so fast components remain visible beside DP.

## Results interpretation

Merge Sort and Dijkstra scale according to their expected asymptotic bounds. Knapsack runtime grows with parcel count and capacity, not just parcel count. Nearest Neighbour repeatedly invokes shortest-path searches and greedily chooses the next stop; practical results depend on graph density and number of stops. Timing is machine- and interpreter-dependent, and small durations are sensitive to system noise. The included benchmark is an educational comparison, not a statistically rigorous benchmark suite.

## Limitations and assumptions

1. One trip, one vehicle, one integer capacity, and positive integer parcel weights and values.
2. Road edges are undirected, static, and have positive distance. Traffic, time windows, service durations, and vehicle speed are not modeled.
3. Multiple parcels at one destination share a single visit. The route is calculated only after packing.
4. Knapsack maximizes value, with deterministic iteration-order tie handling; priority and deadline only determine display/order of candidates and do not enforce service deadlines.
5. Nearest Neighbour is approximate and is not guaranteed to find an optimal tour. Disconnected required destinations are not a supported planning case.
6. Benchmark samples are deterministic but each cell is measured once; no claim is made about universal performance.

## Future improvements

Add capacity in volume as well as weight; make deadline urgency part of a clearly defined multi-objective selection score; support multiple vehicles/trips; introduce directed roads and time-dependent travel costs; compare route heuristics with exact TSP on small cases; add repeated trials and summary statistics; and handle disconnected networks with explicit diagnostics.

## Reproduction

See the root README for setup and CLI commands. The project uses no third-party dependencies. Regenerate the plan with `python src/courier.py`, test with unittest discovery, and regenerate performance data with `python src/courier.py --benchmark`.
