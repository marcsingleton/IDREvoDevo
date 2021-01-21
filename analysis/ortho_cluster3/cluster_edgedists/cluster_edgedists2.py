"""Plot distribution of bitscores associated with edges in clustered ggraph."""

import matplotlib.pyplot as plt
import os
import pandas as pd
from numpy import linspace

# Load gn metadata
gnid2spid = {}
with open('../../ortho_search/ppid2meta/out/ppid2meta.tsv') as file:
    for line in file:
        _, gnid, spid = line.split()
        gnid2spid[gnid] = spid

# Load ggraph
ggraph = {}
with open('../hits2ggraph/out/ggraph2.tsv') as file:
    for line in file:
        node1, adjs = line.rstrip('\n').split('\t')
        bitscores = [adj.split(':') for adj in adjs.split(',')]
        ggraph[node1] = {node2: int(bitscore) for (node2, bitscore) in bitscores}

# Extract OG hits
rows = []
with open('../subcluster_ggraph/out/ggraph2/gclusters.txt') as file:
    for line in file:
        _, _, edges = line.rstrip().split(':')
        if len(edges.split('\t')) > 3:  # Discard edges in minimal OGs
            for edge in edges.split('\t'):
                node1, node2 = edge.split(',')
                row1 = {'qgnid': node1, 'sgnid': node2,
                        'qspid': gnid2spid[node1], 'sspid': gnid2spid[node2],
                        'bitscore': ggraph[node1][node2]}
                row2 = {'qgnid': node2, 'sgnid': node1,
                        'qspid': gnid2spid[node2], 'sspid': gnid2spid[node1],
                        'bitscore': ggraph[node2][node1]}
                rows.append(row1)
                rows.append(row2)
hits = pd.DataFrame(rows)

# Make output directory
if not os.path.exists('out/ggraph2/'):
    os.makedirs('out/ggraph2/')  # Recursive folder creation

bins = linspace(0, hits['bitscore'].max(), 300, endpoint=True)

# 1 Query plots
if not os.path.exists('out/ggraph2/qhists/'):
    os.mkdir('out/ggraph2/qhists/')
g = hits.groupby('qspid')

means = g['bitscore'].mean().sort_index()
plt.bar(means.index, means.values, width=0.75)
plt.xticks(rotation=60)
plt.xlabel('Species')
plt.ylabel('Mean bitscore as query')
plt.savefig('out/ggraph2/bar_bitscoremean-qspecies.png')
plt.close()

for qspid, group in g:
    plt.hist(group['bitscore'], bins=bins)
    plt.xlabel('Bitscore')
    plt.ylabel('Number of hits')
    plt.savefig(f'out/ggraph2/qhists/{qspid}.png')
    plt.close()

# 2 Subject plots
if not os.path.exists('out/ggraph2/shists/'):
    os.mkdir('out/ggraph2/shists/')
g = hits.groupby('sspid')

means = g['bitscore'].mean().sort_index()
plt.bar(means.index, means.values, width=0.75)
plt.xticks(rotation=60)
plt.xlabel('Species')
plt.ylabel('Mean bitscore as subject')
plt.savefig('out/ggraph2/bar_bitscoremean-sspecies.png')
plt.close()

for sspid, group in g:
    plt.hist(group['bitscore'], bins=bins)
    plt.xlabel('Bitscore')
    plt.ylabel('Number of hits')
    plt.savefig(f'out/ggraph2/shists/{sspid}.png')
    plt.close()

# 3 Query-subject plots
if not os.path.exists('out/ggraph2/qshists/'):
    os.mkdir('out/ggraph2/qshists/')
g = hits.groupby(['qspid', 'sspid'])

means = g['bitscore'].mean()
plt.hist(means, bins=50)
plt.xlabel('Mean bitscore')
plt.ylabel('Number of query-subject pairs')
plt.savefig('out/ggraph2/hist_qsnum-bitscoremean.png')
plt.close()

for (qspid, sspid), group in g:
    plt.hist(group['bitscore'], bins=bins)
    plt.xlabel('Bitscore')
    plt.ylabel('Number of hits')
    plt.savefig(f'out/ggraph2/qshists/{qspid}-{sspid}.png')
    plt.close()

"""
DEPENDENCIES
../../ortho_search/ppid2meta/ppid2meta.py
    ../../ortho_search/ppid2meta/out/ppid2meta.tsv
../hits2ggraph/out/hits2ggraph2.py
    ../hits2ggraph/out/ggraph2.tsv
../subcluster_ggraph/subcluster_ggraph2.py
    ../subcluster_ggraph/out/ggraph2/gclusters.txt
"""