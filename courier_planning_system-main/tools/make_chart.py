"""Render benchmark CSV as a dependency-free SVG chart."""
import csv, math
from pathlib import Path

root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'evidence'/'benchmark_results.csv').open(encoding='utf-8')))
keys=['merge_sort_seconds','knapsack_seconds','dijkstra_seconds','nearest_neighbour_seconds']
labels=['Merge Sort','Knapsack DP','Dijkstra','Nearest Neighbour']
colors=['#1884b5','#e05a47','#28a17b','#8b6fd1']
W,H=920,500; left,right,top,bottom=90,25,45,80
values=[float(r[k]) for r in rows for k in keys]
lo,hi=math.log10(min(values)),math.log10(max(values)); plot_h=H-top-bottom
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/><text x="{W/2}" y="25" text-anchor="middle" font-family="Arial" font-size="19" font-weight="bold">Measured Algorithm Runtime (log scale)</text>']
for tick in range(math.floor(lo),math.ceil(hi)+1):
    y=top+plot_h*(hi-tick)/(hi-lo)
    svg.append(f'<line x1="{left}" x2="{W-right}" y1="{y}" y2="{y}" stroke="#dce4ea"/><text x="{left-12}" y="{y+4}" text-anchor="end" font-family="Arial" font-size="11">10^{tick} s</text>')
centers=[220,445,670]; scales=['small','medium','large']; bw,gap=22,6
for si,row in enumerate(rows):
    for j,key in enumerate(keys):
        y=top+plot_h*(hi-math.log10(float(row[key])))/(hi-lo)
        svg.append(f'<rect x="{centers[si]-63+j*(bw+gap)}" y="{y}" width="{bw}" height="{H-bottom-y}" fill="{colors[j]}"><title>{labels[j]} {float(row[key]):.6g} seconds</title></rect>')
    svg.append(f'<text x="{centers[si]}" y="{H-bottom+24}" text-anchor="middle" font-family="Arial" font-size="14">{scales[si]} ({row["parcels"]} parcels)</text>')
for j,label in enumerate(labels):
    x=170+j*180
    svg.append(f'<rect x="{x}" y="{H-25}" width="13" height="13" fill="{colors[j]}"/><text x="{x+18}" y="{H-14}" font-family="Arial" font-size="12">{label}</text>')
svg.append('</svg>')
(root/'evidence'/'runtime_chart.svg').write_text(''.join(svg),encoding='utf-8')
