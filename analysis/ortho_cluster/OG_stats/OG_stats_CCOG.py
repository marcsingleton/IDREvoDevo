"""Plot various statistics of OGs relating to counts of CCs and OGs."""

import matplotlib.pyplot as plt
import os
import pandas as pd

# Load gn metadata
gnid2spid = {}
with open('../ppid2meta/out/ppid2meta.tsv') as file:
    for line in file:
        _, gnid, spid = line.split()
        gnid2spid[gnid] = spid

# Load OGs
rows = []
with open('../subcluster_xgraph/out/ggraph/gclusters.txt') as file:
    for line in file:
        CCid, OGid, edges = line.rstrip().split(':')
        gnids = set([node for edge in edges.split('\t') for node in edge.split(',')])
        for gnid in gnids:
            rows.append({'CCid': CCid, 'OGid': OGid, 'gnid': gnid, 'spid': gnid2spid[gnid]})
OGs = pd.DataFrame(rows)

# Load CCs
rows = []
with open('../connect_xgraph/out/gconnect.txt') as file:
    for line in file:
        CCid, nodes = line.rstrip().split(':')
        for gnid in nodes.split(','):
            rows.append({'CCid': CCid, 'gnid': gnid})
CCs = pd.DataFrame(rows)

# Make output directory
if not os.path.exists('out/CCOG'):
    os.makedirs('out/CCOG')  # Recursive folder creation

# Plots
# Distribution of genes across number of associated OGs
groups = OGs.groupby('gnid')
dist = groups.size().value_counts()
plt.bar(dist.index, dist.values)
plt.xlabel('Number of associated OGs')
plt.ylabel('Number of genes')
plt.title('Distribution of genes across\nnumber of associated OGs')
plt.savefig('out/CCOG/dist_gnnum-OGnum_1.png')
plt.close()

dist = dist.drop(1)
plt.bar(dist.index, dist.values)
plt.xlabel('Number of associated OGs')
plt.ylabel('Number of genes')
plt.title('Distribution of genes across\nnumber of associated OGs')
plt.savefig('out/CCOG/dist_gnnum-OGnum_2.png')
plt.close()

# Distribution of genes across number of associated OGs (segmented by species)
yo_gns = OGs['spid'].isin(['dpse', 'dyak'])
yo_dist = OGs[yo_gns].groupby('gnid').size().value_counts()
ncbifb_dist = OGs[~yo_gns].groupby('gnid').size().value_counts()
plt.bar(ncbifb_dist.index, ncbifb_dist.values, label='NCBI + FlyBase')
plt.bar(yo_dist.index, yo_dist.values, bottom=[ncbifb_dist.get(idx, 0) for idx in yo_dist.index], label=r'Yang $et\ al.$')
plt.xlabel('Number of associated OGs')
plt.ylabel('Number of genes')
plt.title('Distribution of genes across\nnumber of associated OGs')
plt.legend()
plt.savefig('out/CCOG/dist_gnnum-OGnum_species1.png')
plt.close()

yo_dist = yo_dist.drop(1)
ncbifb_dist = ncbifb_dist.drop(1)
plt.bar(ncbifb_dist.index, ncbifb_dist.values, label='NCBI + FlyBase')
plt.bar(yo_dist.index, yo_dist.values, bottom=[ncbifb_dist.get(idx, 0) for idx in yo_dist.index], label=r'Yang $et\ al.$')
plt.xlabel('Number of associated OGs')
plt.ylabel('Number of genes')
plt.title('Distribution of genes across\nnumber of associated OGs')
plt.legend()
plt.savefig('out/CCOG/dist_gnnum-OGnum_species2.png')
plt.close()

# Distribution of connected components across number of associated OGs
sizes = OGs.loc[:, ['CCid', 'OGid']].drop_duplicates().groupby('CCid').size()
dist = sizes.reindex(CCs['CCid'].drop_duplicates(), fill_value=0).value_counts()
plt.bar(dist.index, dist.values)
plt.xlabel('Number of OGs in connected component')
plt.ylabel('Number of connected components')
plt.title('Distribution of connected components\nacross number of associated OGs')
plt.savefig('out/CCOG/dist_connectnum-OGnum_1.png')
plt.xlim(-1, 17)
plt.savefig('out/CCOG/dist_connectnum-OGnum_2.png')
plt.close()

CCOG_pairs = OGs[['CCid', 'OGid']].drop_duplicates()
OG_OGgnnum = OGs.groupby('OGid').size().rename('OG_OGgnnum')
CC_OGgnnum = CCOG_pairs.join(OG_OGgnnum, on='OGid').groupby('CCid')['OG_OGgnnum']
CC_OGnum = CCOG_pairs.groupby('CCid').size().rename('CC_OGnum')
CC_CCgnnum = CCs.groupby('CCid').size()[OGs['CCid'].drop_duplicates()].rename('CC_CCgnnum')

# Correlation of number of OGs associated with CC and number of genes in CC
plt.scatter(CC_OGnum, CC_CCgnnum, alpha=0.5, s=10, edgecolors='none')
plt.xlabel('Number of OGs associated with CC')
plt.ylabel('Number of genes in CC')
plt.savefig('out/CCOG/scatter_CCgnnum-CCOGnum.png')
plt.close()

# Correlation of aggregate number of genes in OGs associated with CC with number of OGs associated with CC
plt.scatter(CC_OGgnnum.max(), CC_OGnum, alpha=0.5, s=12, edgecolors='none')
plt.xlabel('Max number of genes in OGs associated with CC')
plt.ylabel('Number of OGs associated with CC')
plt.savefig('out/CCOG/scatter_CCOGnum-CCOGgnmax.png')
plt.close()

plt.scatter(CC_OGgnnum.mean(), CC_OGnum, alpha=0.5, s=10, edgecolors='none')
plt.xlabel('Mean number of genes in OGs associated with CC')
plt.ylabel('Number of OGs associated with CC')
plt.savefig('out/CCOG/scatter_CCOGnum-CCOGgnmean.png')
plt.close()

# Correlation of aggregate number of genes in OGs associated with CC with number of genes in CC
plt.scatter(CC_OGgnnum.max(), CC_CCgnnum, alpha=0.5, s=10, edgecolors='none')
plt.xlabel('Max number of genes in OGs associated with CC')
plt.ylabel('Number of genes in CC')
plt.savefig('out/CCOG/scatter_CCgnnum-CCOGgnmax.png')
plt.close()

plt.scatter(CC_OGgnnum.mean(), CC_CCgnnum, alpha=0.5, s=10, edgecolors='none')
plt.xlabel('Mean number of genes in OGs associated with CC')
plt.ylabel('Number of genes in CC')
plt.savefig('out/CCOG/scatter_CCgnnum-CCOGgnmean.png')
plt.close()

OGgn_pairs = OGs[['OGid', 'gnid']].drop_duplicates()
CCgn_pairs = OGs[['CCid', 'gnid']].drop_duplicates()
gn_OGnum = OGgn_pairs.groupby('gnid').size().rename('gn_OGnum')
hitnum = pd.read_csv('../blast_stats/out/hitnum_reciprocal/sgnids.tsv', sep='\t', header=0, names=['gnid', 'hitnum', 'spid'], index_col=0)
df = CCgn_pairs.join(gn_OGnum, on='gnid').join(CC_CCgnnum, on='CCid').join(CC_OGnum, on='CCid').join(hitnum, on='gnid')

# Correlation of number of associated OGs with number of genes in CC for gene
plt.scatter(df['gn_OGnum'], df['CC_CCgnnum'], alpha=0.5, s=10, edgecolors='none')
plt.xlabel('Number of OGs associated with gene')
plt.ylabel('Number of genes in CC associated with gene')
plt.savefig('out/CCOG/scatter_CCgnnum-gnOGnum.png')
plt.close()

# Correlation of number of OGs associated with gene with number of OGs in CC associated with gene
plt.scatter(df['gn_OGnum'], df['CC_OGnum'], alpha=0.5, s=10, edgecolors='none')
plt.xlabel('Number of OGs associated with gene')
plt.ylabel('Number of OGs in CC associated with gene')
plt.savefig('out/CCOG/scatter_CCOGnum-gnOGnum.png')
plt.close()

# Correlation of number of unique reciprocal hits to gene with number of OGs associated with gene
plt.scatter(df['gn_OGnum'], df['hitnum'], alpha=0.5, s=10, edgecolors='none')
plt.xlabel('Number of OGs associated with gene')
plt.ylabel('Number of reciprocal hits to gene')
plt.savefig('out/CCOG/scatter_hitnum-gnOGnum.png')
plt.close()

"""
DEPENDENCIES
../connect_xgraph/connect_ggraph.py
    ../connect_xgraph/out/gconnect.txt
../blast_stats/blast_stats.py
    ../blast_stats/out/hitnum_reciprocal/sgnids.tsv
../ppid2meta/ppid2meta.py
    ../ppid2meta/out/ppid2meta.tsv
../subcluster_xgraph/subcluster_ggraph.py
    ../subcluster_xgraph/out/ggraph/gclusters.txt
"""