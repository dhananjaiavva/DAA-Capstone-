"""Integrated courier planning algorithms (standard library only)."""
from __future__ import annotations
import argparse, csv, heapq, json, random, time
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Parcel:
    parcel_id: str
    destination: str
    weight_kg: int
    value: int
    priority: int
    deadline: str

def load_parcels(path: Path) -> list[Parcel]:
    with path.open(newline='', encoding='utf-8') as f:
        return [Parcel(r['parcel_id'], r['destination'], int(r['weight_kg']), int(r['value']), int(r['priority']), r['deadline']) for r in csv.DictReader(f)]

def merge_sort_parcels(items: list[Parcel]) -> list[Parcel]:
    """Stable O(n log n) sort: priority desc, deadline asc, id asc."""
    if len(items) < 2: return items[:]
    mid = len(items)//2
    left, right = merge_sort_parcels(items[:mid]), merge_sort_parcels(items[mid:])
    out=[]; i=j=0
    key=lambda p: (-p.priority, p.deadline, p.parcel_id)
    while i<len(left) and j<len(right):
        if key(left[i]) <= key(right[j]): out.append(left[i]); i+=1
        else: out.append(right[j]); j+=1
    return out+left[i:]+right[j:]

def knapsack(parcels: list[Parcel], capacity: int) -> tuple[list[Parcel], int]:
    """0/1 DP maximizing value; ties keep the earlier (sorted) parcel set."""
    n=len(parcels); dp=[[0]*(capacity+1) for _ in range(n+1)]
    for i,p in enumerate(parcels,1):
        for c in range(capacity+1):
            dp[i][c]=dp[i-1][c]
            if p.weight_kg<=c:
                dp[i][c]=max(dp[i][c],dp[i-1][c-p.weight_kg]+p.value)
    chosen=[]; c=capacity
    for i in range(n,0,-1):
        if dp[i][c] != dp[i-1][c]:
            p=parcels[i-1]; chosen.append(p); c-=p.weight_kg
    chosen.reverse()
    return chosen, dp[n][capacity]

def load_graph(path: Path) -> dict[str,dict[str,float]]:
    obj=json.loads(path.read_text(encoding='utf-8'))
    graph={node:{} for node in obj['nodes']}
    for a,b,d in obj['edges']:
        if d<=0: raise ValueError('Road distances must be positive')
        graph[a][b]=float(d); graph[b][a]=float(d)
    return graph

def dijkstra(graph: dict[str,dict[str,float]], source: str) -> tuple[dict[str,float],dict[str,str|None]]:
    dist={v:float('inf') for v in graph}; prev={v:None for v in graph}; dist[source]=0
    heap=[(0,source)]
    while heap:
        d,u=heapq.heappop(heap)
        if d!=dist[u]: continue
        for v,w in graph[u].items():
            nd=d+w
            if nd<dist[v]: dist[v]=nd; prev[v]=u; heapq.heappush(heap,(nd,v))
    return dist,prev

def path_between(prev: dict[str,str|None], target: str) -> list[str]:
    path=[]; u=target
    while u is not None: path.append(u); u=prev[u]
    return path[::-1]

def nearest_neighbour(graph: dict[str,dict[str,float]], start: str, destinations: list[str]) -> tuple[list[str],float]:
    """TSP approximation on the complete metric closure of road shortest paths."""
    remaining=set(destinations)-{start}; order=[start]; total=0.0; current=start
    while remaining:
        dist,_=dijkstra(graph,current)
        nxt=min(remaining,key=lambda x:(dist[x],x)); total+=dist[nxt]; order.append(nxt); remaining.remove(nxt); current=nxt
    if current!=start:
        dist,_=dijkstra(graph,current); total+=dist[start]; order.append(start)
    return order,total

def plan(parcels: list[Parcel], graph: dict[str,dict[str,float]], capacity: int, depot: str='Depot') -> dict:
    ranked=merge_sort_parcels(parcels); selected,value=knapsack(ranked,capacity)
    destinations=sorted({p.destination for p in selected})
    route,distance=nearest_neighbour(graph,depot,destinations)
    return {'ranked':ranked,'selected':selected,'value':value,'weight':sum(p.weight_kg for p in selected),'route':route,'distance':distance}

def show_plan(result: dict, capacity: int) -> str:
    lines=['COURIER PLANNING SYSTEM','='*26,f"Vehicle capacity: {capacity} kg",f"Selected parcels: {len(result['selected'])} / {len(result['ranked'])}",f"Packed weight: {result['weight']} kg | Total value: {result['value']}",'','Priority order (Merge Sort):']
    lines += [f"  {p.parcel_id:4} | priority {p.priority} | deadline {p.deadline} | {p.weight_kg} kg | value {p.value} | {p.destination}" for p in result['ranked']]
    lines += ['', 'Knapsack selection:']+[f"  {p.parcel_id} -> {p.destination} ({p.weight_kg} kg, value {p.value})" for p in result['selected']]
    lines += ['', 'Delivery route (Nearest Neighbour over Dijkstra distances):']+[f'  {i+1}. {node}' for i,node in enumerate(result['route'])]
    lines += [f"Total road distance: {result['distance']:.1f} km",'','Model: Knapsack selects parcels by value under capacity; it does not impose delivery order. The route visits the distinct destinations of selected parcels.']
    return '\n'.join(lines)

def benchmark() -> list[dict]:
    rng=random.Random(781); rows=[]
    for label,n,nodes in [('small',40,12),('medium',160,30),('large',500,65)]:
        parcels=[Parcel(f'P{i:04}',f'N{rng.randrange(nodes):03}',rng.randrange(1,11),rng.randrange(10,101),rng.randrange(1,6),f'2026-12-{rng.randrange(1,29):02}') for i in range(n)]
        # Benchmark sorting independently.
        t=time.perf_counter(); merge_sort_parcels(parcels); sort_s=time.perf_counter()-t
        cap=100
        # Keep DP dimensions representative and manageable (O(nW)).
        t=time.perf_counter(); knapsack(parcels,cap); dp_s=time.perf_counter()-t
        graph={f'N{i:03}':{} for i in range(nodes)}
        for i in range(nodes):
            for j in range(i+1,nodes):
                if rng.random()<0.12 or j==i+1:
                    d=float(rng.randrange(2,40)); graph[f'N{i:03}'][f'N{j:03}']=d; graph[f'N{j:03}'][f'N{i:03}']=d
        t=time.perf_counter(); dijkstra(graph,'N000'); dij_s=time.perf_counter()-t
        stops=[f'N{i:03}' for i in range(1,min(nodes,16))]
        t=time.perf_counter(); nearest_neighbour(graph,'N000',stops); nn_s=time.perf_counter()-t
        rows.append({'scale':label,'parcels':n,'nodes':nodes,'capacity_kg':cap,'merge_sort_seconds':sort_s,'knapsack_seconds':dp_s,'dijkstra_seconds':dij_s,'nearest_neighbour_seconds':nn_s})
    return rows

def main():
    ap=argparse.ArgumentParser(description='Plan one courier trip from sample CSV and weighted graph JSON.')
    ap.add_argument('--parcels',type=Path,default=ROOT/'data'/'parcels.csv'); ap.add_argument('--graph',type=Path,default=ROOT/'data'/'road_network.json'); ap.add_argument('--capacity',type=int,default=30); ap.add_argument('--benchmark',action='store_true'); ap.add_argument('--out',type=Path,default=ROOT/'evidence'/'benchmark_results.csv')
    args=ap.parse_args()
    if args.benchmark:
        rows=benchmark(); args.out.parent.mkdir(parents=True,exist_ok=True)
        with args.out.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
        print(f'Wrote benchmark results: {args.out}'); [print(r) for r in rows]; return
    result=plan(load_parcels(args.parcels),load_graph(args.graph),args.capacity)
    print(show_plan(result,args.capacity))
if __name__=='__main__': main()
