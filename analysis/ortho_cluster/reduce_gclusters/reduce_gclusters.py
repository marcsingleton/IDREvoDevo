"""Reduce gene clusters to representative polypeptides."""

import Bio.Phylo as Phylo
import json
import os
from copy import deepcopy
from itertools import chain, product


def reduce_node(node, OG):
    """Return representative ppids for all gnids associated with terminals in node."""

    leaf1, leaf2 = node.clades

    if leaf1.is_terminal() and leaf2.is_terminal():
        rOG = reduce_terminal(leaf1, leaf2, OG)
    elif leaf1.is_terminal() and not leaf2.is_terminal():
        distances = get_distances(node)
        rOG = reduce_nonterminal(leaf1, reduce_node(leaf2, OG), OG, distances)
    elif not leaf1.is_terminal() and leaf2.is_terminal():
        distances = get_distances(node)
        rOG = reduce_nonterminal(leaf2, reduce_node(leaf1, OG), OG, distances)
    else:
        rOG = reduce_node(leaf1, OG) + reduce_node(leaf2, OG)

    return rOG


def reduce_terminal(leaf1, leaf2, OG):
    # Get list of species ids
    spids1 = [leaf1.name for _ in range(len(leaf1.gnids))]
    spids2 = [leaf2.name for _ in range(len(leaf2.gnids))]

    # Get list of genes in OG for each species
    gnids1 = leaf1.gnids
    gnids2 = leaf2.gnids

    # Get sets of proteins corresponding to list of genes
    ppid_sets1 = [get_ppid_set(OG, gnid) for gnid in gnids1]
    ppid_sets2 = [get_ppid_set(OG, gnid) for gnid in gnids2]

    # Get all combinations of proteins with each gene represented once
    ppid_prods1 = product(*ppid_sets1)
    ppid_prods2 = product(*ppid_sets2)

    scores = []
    for ppid_prod1, ppid_prod2 in product(ppid_prods1, ppid_prods2):  # Separate species to sum only inter-species hits
        # Add gene ids to locate in OG and calculate products to sum hits bidirectionally
        z1 = list(zip(spids1, gnids1, ppid_prod1))
        z2 = list(zip(spids2, gnids2, ppid_prod2))
        p1 = product(z1, z2)
        p2 = product(z2, z1)

        score = 0
        for (_, gnid1, ppid1), (_, gnid2, ppid2) in chain(p1, p2):
            try:
                score += float(OG[gnid1][gnid2][ppid1][ppid2]['bitscore'])
            except KeyError:
                pass
        scores.append((score, z1 + z2))

    return max(scores)[1]


def reduce_nonterminal(leaf, rOG, OG, distances):
    spids = [leaf.name for _ in range(len(leaf.gnids))]  # Get list of species ids
    gnids = leaf.gnids  # Get list of genes in OG for species
    ppid_sets = [get_ppid_set(OG, gnid) for gnid in gnids]  # Get sets of proteins corresponding to list of genes
    ppid_prods = product(*ppid_sets)  # Get all combinations of proteins with each gene represented once
    d = sum(distances.values()) + (len(distances) - 2) * distances[leaf.name]

    scores = []
    for ppid_prod in ppid_prods:  # Separate species to sum only inter-species hits
        # Add species and gene ids to locate in OG and calculate products to sum hits bidirectionally
        z = list(zip(spids, gnids, ppid_prod))
        p1 = product(z, rOG)
        p2 = product(rOG, z)

        score = 0
        for (spid1, gnid1, ppid1), (spid2, gnid2, ppid2) in chain(p1, p2):
            try:
                weight = (distances[spid1] + distances[spid2]) / d
                score += weight * float(OG[gnid1][gnid2][ppid1][ppid2]['bitscore'])
            except KeyError:
                pass
        scores.append((score, z + rOG))

    return max(scores)[1]


def get_ppid_set(OG, gnid):
    """Return ppids associated with a given gnid in an orthologous group."""

    ppid_set = set()
    for ppids in OG[gnid].values():
        for ppid in ppids.keys():
            ppid_set.add(ppid)

    return ppid_set


def get_distances(node, d0=0):
    """Return distances to terminals from current node."""

    distances = {}
    for leaf in node.clades:
        if leaf.is_terminal():
            distances[leaf.name] = d0 + leaf.branch_length
        else:
            distances.update(get_distances(leaf, d0 + leaf.branch_length))

    return distances


# Load gn metadata
gnid2spid = {}
with open('../ppid2meta/out/ppid2meta.tsv') as file:
    for line in file:
        _, gnid, spid = line.split()
        gnid2spid[gnid] = spid

# Load ggraph
with open('../blast2ggraph/out/ggraph.json') as file:
    ggraph = json.load(file)

# Load OGs and tree
OGs = {}
with open('../subcluster_xgraph/out/ggraph/gclusters.txt') as file:
    for line in file:
        _, OGid, edges = line.rstrip().split(':')
        OGs[OGid] = [tuple(edge.split(',')) for edge in edges.split('\t')]
tree_template = Phylo.read('drosophila-10spec-tree.nwk', 'newick')

# Convert OG into subggraph
subggraphs = {}
for OGid, OG in OGs.items():
    subggraph = {}
    for node1, node2 in OG:
        try:
            subggraph[node1][node2] = ggraph[node1][node2]
        except KeyError:
            subggraph[node1] = {node2: ggraph[node1][node2]}
        try:
            subggraph[node2][node1] = ggraph[node2][node1]
        except KeyError:
            subggraph[node2] = {node1: ggraph[node2][node1]}
    subggraphs[OGid] = subggraph

rOGs = {}
for OGid, subggraph in subggraphs.items():
    # Add genes to leaves of tree
    tree = deepcopy(tree_template)
    terminals = {terminal.name: terminal for terminal in tree.get_terminals()}
    remain = set()
    for gnid in subggraph:
        spid = gnid2spid[gnid]
        remain.add(spid)
        try:
            terminals[spid].gnids.append(gnid)
        except AttributeError:
            terminals[spid].gnids = [gnid]

    # Remove unused terminals
    remove = set(terminals) - remain
    for terminal in remove:
        tree.prune(terminal)

    # Reduce OG
    rOG = reduce_node(tree.root, subggraph)  # Pass root since tree object has no clades attribute
    rOGs[OGid] = rOG

# Make output directory
if not os.path.exists('out/'):
    os.mkdir('out/')

# Write reduced clusters to file
with open('out/rclusters.tsv', 'w') as outfile:
    outfile.write('OGid\tspid\tgnid\tppid\n')
    for OGid, rOG in rOGs.items():
        for entry in rOG:
            outfile.write(OGid + '\t' + '\t'.join(entry) + '\n')

"""
DEPENDENCIES
../subcluster_xgraph/subcluster_ggraph.py
    ../subcluster_xgraph/out/ggraph/gclusters.txt
../ppid2meta/ppid2meta.py
    ../ppid2meta/out/ppid2meta.tsv
./drosophila-10spec-tree.nwk
"""