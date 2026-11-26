import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from courier import Parcel, dijkstra, knapsack, merge_sort_parcels, nearest_neighbour, load_graph, load_parcels

class CourierTests(unittest.TestCase):
    def test_merge_sort_key_and_stability(self):
        a=Parcel('b','X',1,1,4,'2026-01-02'); b=Parcel('a','X',1,1,4,'2026-01-02'); c=Parcel('c','X',1,1,5,'2026-01-03')
        self.assertEqual([x.parcel_id for x in merge_sort_parcels([a,b,c])],['c','a','b'])
    def test_knapsack_optimum(self):
        ps=[Parcel('a','X',4,7,1,'d'),Parcel('b','Y',3,6,1,'d'),Parcel('c','Z',2,4,1,'d')]
        chosen,value=knapsack(ps,5)
        self.assertEqual(value,10); self.assertEqual({p.parcel_id for p in chosen},{'b','c'})
    def test_dijkstra_shortest_path(self):
        g={'A':{'B':2,'C':8},'B':{'A':2,'C':3},'C':{'A':8,'B':3}}
        d,prev=dijkstra(g,'A'); self.assertEqual(d['C'],5)
    def test_route_returns_to_depot(self):
        g=load_graph(Path(__file__).resolve().parents[1]/'data'/'road_network.json')
        route,distance=nearest_neighbour(g,'Depot',['North','Airport'])
        self.assertEqual(route[0],'Depot'); self.assertEqual(route[-1],'Depot'); self.assertGreater(distance,0)
    def test_sample_files(self):
        root=Path(__file__).resolve().parents[1]
        self.assertEqual(len(load_parcels(root/'data'/'parcels.csv')),12)
        self.assertEqual(len(load_graph(root/'data'/'road_network.json')),7)

if __name__=='__main__': unittest.main()
