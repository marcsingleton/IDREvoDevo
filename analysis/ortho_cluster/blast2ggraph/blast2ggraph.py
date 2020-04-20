"""Parse BLAST results as gene graph."""

import json
import os
import re
from itertools import permutations


def get_BH_ppids(subjects):
    if not subjects:
        return [(db_species, None, None)]

    BHs = []
    gnid = pp_meta[re.search(pp_regex[params[db_species]], subjects[0][1]).group(1)][0]
    for subject in subjects:
        BH_ppid = re.search(pp_regex[params[db_species]], subject[1]).group(1)
        BH_gnid = pp_meta[BH_ppid][0]  # First entry is gnid, second is species
        if BH_gnid != gnid:
            break
        BHs.append((BH_ppid, BH_gnid, subject[-1]))  # Last subject entry is bit score
        gnid = BH_gnid

    return BHs


def add_BH(ggraph, query_ppid, query_gnid, BH_ppid, BH_gnid, bscore=None):
    BH = BH_ppid if bscore is None else (BH_ppid, bscore)
    try:
        ggraph[query_gnid][BH_gnid][query_ppid].append(BH)
    except KeyError as err:
        if err.args[0] == query_gnid:
            ggraph[query_gnid] = {BH_gnid: {query_ppid: [BH]}}
        elif err.args[0] == BH_gnid:
            ggraph[query_gnid][BH_gnid] = {query_ppid: [BH]}
        elif err.args[0] == query_ppid:
            ggraph[query_gnid][BH_gnid] = {query_ppid: [BH]}


pp_regex = {'flybase': r'(FBpp[0-9]+)',
            'ncbi': r'(XP_[0-9]+(\.[0-9]+)?)',
            'YO': r'(YOtr[A-Z0-9]+\|orf[0-9]+)'}

# Load pp metadata
pp_meta = {}
with open('../ppid2meta/out/ppid2meta.tsv') as infile:
    for line in infile:
        pp_id, meta = line.split()
        pp_meta[pp_id] = meta.split(',')

# Parse parameters
params = {}
with open('params.tsv') as infile:
    fields = infile.readline().split()  # Skip header
    for line in infile:
        species, _, source = line.split()
        params[species] = source

# Parse BLAST results
ggraph = {}
for query_species, db_species in permutations(params.keys(), 2):
    with open(f'../blast_AAA/out/{query_species}/{db_species}.blast') as file:
        query_ppid, subjects = None, []
        line = file.readline()
        while line:
            while line.startswith('#'):
                if line == '# BLASTP 2.10.0+\n' and query_ppid is not None:  # Skip for first line
                    add_BH(ggraph, query_ppid, query_gnid, db_species, None)
                elif line.startswith('# Query:'):
                    query_ppid = re.search(pp_regex[params[query_species]], line).group(1)
                    query_gnid = pp_meta[query_ppid][0]  # First entry is gnid, second is species
                line = file.readline()

            subjects = []  # Or "hits," but using the BLAST jargon here
            while line and not line.startswith('#'):
                subjects.append(line.split())
                line = file.readline()
            for BH_ppid, BH_gnid, bscore in get_BH_ppids(subjects):
                add_BH(ggraph, query_ppid, query_gnid, BH_ppid, BH_gnid, bscore)

# Make output directory
if not os.path.exists(f'out/'):
    os.mkdir(f'out/')

# Write graph as adjacency list to file
with open('out/ggraph.json', 'w') as outfile:
    json.dump(ggraph, outfile, indent=1)

"""
DEPENDENCIES
../blast_AAA/blast_AAA.py
    ../blast_AAA/out/*
./params.tsv
"""