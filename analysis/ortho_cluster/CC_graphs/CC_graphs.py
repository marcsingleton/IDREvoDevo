"""Draw largest connected components."""

import matplotlib.pyplot as plt
import networkx as nx
import os
from math import exp

# Parse best hits as graph
ggraph = {}
with open('../blast2ggraph/out/ggraph.tsv') as file:
    for line in file:
        node, adjs = line.rstrip('\n').split('\t')
        if node != 'null':  # Remove None first to prevent recognition later
            ggraph[node] = adjs.split(',')

# Parse connected components
CCs = {}
with open('../connect_xgraph/out/gconnect.txt') as file:
    for line in file:
        CCid, nodes = line.rstrip().split(':')
        CCs[CCid] = set(nodes.split(','))

# Make output directory
if not os.path.exists('out/'):
    os.mkdir('out/')

CCids = sorted(CCs, key=lambda x: len(CCs[x]), reverse=True)[:50]  # 50 largest CCs
for i, CCid in enumerate(CCids):
    subggraph = {node: ggraph[node] for node in CCs[CCid]}

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

    # Create graph and segment nodes by data source
    G = nx.Graph()
    for node in subggraph:
        G.add_node(node)
        for adj in subggraph[node]:
            G.add_edge(node, adj)
    FB = [node for node in G.nodes if node.startswith('FBgn')]
    YO = [node for node in G.nodes if node.startswith('YOgn')]
    NCBI = G.nodes - (FB + YO)

    # Get positions and canvas limits
    pos = nx.kamada_kawai_layout(G)
    xs = [xy[0] for xy in pos.values()]
    xmin, xmax = min(xs), max(xs)
    xlen = xmax - xmin
    ys = [xy[1] for xy in pos.values()]
    ymin, ymax = min(ys), max(ys)
    ylen = ymax - ymin

    # Adjust dimensions so aspect ratio is 1:1
    max_dim = 8
    if xlen > ylen:
        figsize = (max_dim, max_dim * ylen/xlen)
    else:
        figsize = (max_dim * xlen/ylen, max_dim)
    node_size = 35/(1 + exp(0.01*(len(subggraph)-400))) + 10  # Adjust node size

    # Determine best position for legend
    locs = ['lower left', 'lower right', 'upper left', 'upper right']
    delset = set()
    for x, y in pos.values():
        xnorm = (x-xmin)/(xmax-xmin)
        ynorm = (y-ymin)/(ymax-ymin)
        if xnorm > 0.9 and ynorm > 0.9:
            delset.add('upper right')
        elif xnorm < 0.1 and ynorm > 0.9:
            delset.add('upper left')
        elif xnorm > 0.9 and ynorm < 0.1:
            delset.add('lower right')
        elif xnorm < 0.1 and ynorm < 0.1:
            delset.add('lower left')
    for loc in delset:
        locs.remove(loc)

    # Draw graph
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    nx.draw_networkx_edges(G, pos, alpha=0.25, width=0.5)
    nx.draw_networkx_nodes(NCBI, pos, node_size=node_size, linewidths=0, node_color='C0', label='NCBI')
    nx.draw_networkx_nodes(YO, pos, node_size=node_size, linewidths=0, node_color='C1', label=r'Yang $et\ al.$')
    nx.draw_networkx_nodes(FB, pos, node_size=node_size, linewidths=0, node_color='C2', label='FlyBase')

    fig.legend(markerscale=(1 if node_size > 22.5 else 22.5/node_size), loc=locs.pop())
    fig.tight_layout()
    ax.axis('off')
    fig.savefig(f'out/{i}_{CCid}.png')
    plt.close()

"""
DEPENDENCIES
../blast2ggraph/blast2ggraph.py
    ../blast2ggraph/out/ggraph.tsv
../connect_xgraph/connect_ggraph.py
    ../connect_xgraph/out/gconnect.txt
"""