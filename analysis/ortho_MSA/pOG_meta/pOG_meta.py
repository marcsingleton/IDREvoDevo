"""Extract metadata from pOGs including numbers of edges, genes, species, and unique sequences."""

import os
import pandas as pd

# Load seq metadata
ppid2meta = {}
with open('../../ortho_search/seq_meta/out/seq_meta.tsv') as file:
    for line in file:
        ppid, gnid, spid, _ = line.split()
        ppid2meta[ppid] = (gnid, spid)

# Load pOGs
rows = []
with open('../../ortho_cluster3/clique4+_pcommunity/out/5clique/pclusters.txt') as file:
    for line in file:
        OGid, pOGid, edges = line.rstrip().split(':')
        ppids = set([node for edge in edges.split('\t') for node in edge.split(',')])
        gnids = set([ppid2meta[ppid][0] for ppid in ppids])
        spids = set([ppid2meta[ppid][1] for ppid in ppids])
        rows.append({'OGid': OGid, 'pOGid': pOGid,
                     'edgenum': len(edges), 'ppidnum': len(ppids), 'gnidnum': len(gnids), 'spidnum': len(spids)})
pOGs = pd.DataFrame(rows)

# Print counts
num = 26
ppnum = pOGs['ppidnum'] == num
gnnum = pOGs['gnidnum'] == num
spnum = pOGs['spidnum'] == num

print('Total pOGs:', len(pOGs))
print(f'pOGs with {num} genes:', len(pOGs[gnnum]))
print(f'pOGs with {num} genes and species:', len(pOGs[gnnum & spnum]))
print(f'pOGs with {num} genes, species, and sequences:', len(pOGs[gnnum & spnum & ppnum]))

# Make output directory
if not os.path.exists('out/'):
    os.mkdir('out/')

pOGs.to_csv('out/pOG_meta.tsv', sep='\t', index=False)

"""
OUTPUT 
Total OGs: 20685
OGs with 26 genes: 7938
OGs with 26 genes and species: 7748
OGs with 26 genes, species, and sequences: 5663

DEPENDENCIES
../../ortho_search/seq_meta/seq_meta.py
    ../../ortho_search/seq_meta/out/seq_meta.tsv
../../ortho_cluster3/clique4+_gcommunity/clique4+_gcommunity.py
    ../../ortho_cluster3/clique4+_gcommunity/out/ggraph2/5clique/gclusters.txt
"""