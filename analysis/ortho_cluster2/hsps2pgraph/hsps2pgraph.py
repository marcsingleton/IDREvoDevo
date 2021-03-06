"""Convert HSPs to a directed pgraph."""

import os
from itertools import groupby


def line2key(line):
    fields = line.split()
    return fields[0], fields[3]


# Make pgraph
pgraph = {}
for qspid in os.listdir('../blast2hsps/out/hsps/'):
    for sspid in os.listdir(f'../blast2hsps/out/hsps/{qspid}/'):
        with open(f'../blast2hsps/out/hsps/{qspid}/{sspid}') as file:
            file.readline()  # Skip header
            for key, _ in groupby(file, key=line2key):
                qppid, sppid = key[0], key[1]
                try:
                    pgraph[qppid].add(sppid)
                except KeyError:
                    pgraph[qppid] = set([sppid])

# Make output directory
if not os.path.exists('out/'):
    os.mkdir('out/')

# Write to file
with open('out/pgraph.tsv', 'w') as file:
    for qppid, sppids in pgraph.items():
        file.write(qppid + '\t' + ','.join(sppids) + '\n')

"""
DEPENDENCIES
../blast2hsps/blast2hsps.py
    ../blast2hsps/out/hsps/*/*.tsv
"""