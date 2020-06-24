"""Extract clusters from connected components of ggraph."""

import matplotlib.pyplot as plt
import os
from itertools import combinations
from triDFS import cluster

# Parse best hits as graph
ggraph = {}
with open('../blast2ggraph/out/ggraph.tsv') as file:
    for line in file:
        node, adjs = line.rstrip('\n').split('\t')
        if node != 'null':  # Remove None first to prevent recognition later
            ggraph[node] = adjs.split(',')

# Parse connected components
CCs = []
with open('../connect_xgraph/out/gconnect.txt') as file:
    for line in file:
        _, nodes = line.rstrip().split(':')
        CCs.append(set(nodes.split(',')))

OGs = []
CCtypes = [{} for _ in range(5)]
for CC in CCs:
    subggraph = {node: ggraph[node] for node in CC}

    # Remove non-reciprocal hits
    for node, adjs in subggraph.items():
        # Search current node for non-reciprocal hits
        adj_idxs = []
        for adj_idx, adj in enumerate(adjs):
            try:  # Cannot test with "in" easily since it assumes the node is in the graph in the first place
                subggraph[adj].index(node)
            except (KeyError, ValueError):  # KeyError from adj not in pgraph; ValueError from node not in adjs
                adj_idxs.append(adj_idx)

        # Remove non-reciprocal hits after initial loop is completed to not modify list during loop
        for offset, adj_idx in enumerate(adj_idxs):
            del adjs[adj_idx - offset]

    # Cluster by triangle criterion
    subOGs = cluster(subggraph)
    OGs.append(subOGs)

    # Classify CCs
    subnOGs = [set([node for edge in subOG for node in edge]) for subOG in subOGs]
    if len(subnOGs) == 0:
        CCtypes[0][len(subnOGs)] = CCtypes[0].get(len(subnOGs), 0) + 1  # Component has no OGs
    elif len(subnOGs) == 1:
        if len(subnOGs[0]) == len(CC):
            CCtypes[1][len(subnOGs)] = CCtypes[1].get(len(subnOGs), 0) + 1  # Component and OG are equal
        else:
            CCtypes[2][len(subnOGs)] = CCtypes[2].get(len(subnOGs), 0) + 1  # Component has single OG which is a subset of the component
    elif any([set.intersection(nOG1, nOG2) for nOG1, nOG2 in combinations(subnOGs, 2)]):
        CCtypes[3][len(subnOGs)] = CCtypes[3].get(len(subnOGs), 0) + 1  # Component has multiple non-disjoint OGs
    else:
        CCtypes[4][len(subnOGs)] = CCtypes[4].get(len(subnOGs), 0) + 1  # Component has multiple pairwise disjoint OGs

# Make plots output directory
if not os.path.exists(f'out/ggraph'):
    os.makedirs(f'out/ggraph')  # Recursive folder creation

# Write OGs to file
j = 0
with open('out/ggraph/gclusters.txt', 'w') as file:
    for i, subOGs in enumerate(OGs):
        CCid = hex(i)[2:].zfill(4)
        for OG in subOGs:
            OGid = hex(j)[2:].zfill(4)
            file.write(CCid + ':' + OGid + ':' + '\t'.join([f'{node1},{node2}' for node1, node2 in OG]) + '\n')
            j += 1

# Plots
plt.bar(CCtypes[0].keys(), CCtypes[0].values(), label='Type 0')
plt.bar(CCtypes[1].keys(), CCtypes[1].values(), label='Type 1')
plt.bar(CCtypes[2].keys(), CCtypes[2].values(), bottom=CCtypes[1][1], label='Type 2')
plt.bar(CCtypes[3].keys(), CCtypes[3].values(), label='Type 3')
plt.bar(CCtypes[4].keys(), CCtypes[4].values(), bottom=[CCtypes[3].get(key, 0) for key in CCtypes[4]], label='Type 4')
plt.xlabel('Number of OGs in Connected Component')
plt.ylabel('Number of Connected Components')
plt.title('Distribution of Connected Components across Number of OGs')
plt.legend()
plt.savefig('out/ggraph/connectnum-OGnum_type_dist1-1.png')
plt.xlim((-1, 17))  # Adjust axis to truncate outliers
plt.savefig('out/ggraph/connectnum-OGnum_type_dist1-2.png')
plt.close()

plt.bar(CCtypes[3].keys(), CCtypes[3].values(), label='Type 3', color='C3')
plt.bar(CCtypes[4].keys(), CCtypes[4].values(), bottom=[CCtypes[3].get(key, 0) for key in CCtypes[4]], label='Type 4', color='C4')
plt.xlabel('Number of OGs in Connected Component')
plt.ylabel('Number of Connected Components')
plt.title('Distribution of Connected Components across Number of OGs')
plt.legend()
plt.savefig('out/ggraph/connectnum-OGnum_type_dist2-1.png')
plt.xlim((-1, 17))  # Adjust axis to truncate outliers
plt.savefig('out/ggraph/connectnum-OGnum_type_dist2-2.png')
plt.close()

plt.pie([sum(CCtype.values()) for CCtype in CCtypes], labels=[f'Type {i}' for i in range(len(CCtypes))])
plt.title('Connected Components by Type')
plt.savefig('out/ggraph/type_pie.png')
plt.close()

for i, CCtype in enumerate(CCtypes):
    print(f'Type {i}:', sum(CCtype.values()))

"""
OUTPUT
Type 0: 130
Type 1: 7128
Type 2: 958
Type 3: 852
Type 4: 788

DEPENDENCIES
../blast2ggraph/blast2ggraph.py
    ../blast2ggraph/out/ggraph.tsv
../connect_xgraph/connect_ggraph.py
    ../connect_xgraph/out/gconnect.txt
./triDFS.py
"""