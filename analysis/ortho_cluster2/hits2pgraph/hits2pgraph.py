"""Convert hits to a directed pgraph."""

import os


def add_edge(qppid, sppid, pgraph):
    try:
        pgraph[qppid].add(sppid)
    except KeyError:
        pgraph[qppid] = set([sppid])


columns = {'qppid': str, 'qgnid': str, 'qspid': str,
           'sppid': str, 'sgnid': str, 'sspid': str,
           'hspnum': int, 'chspnum': int,
           'qlen': int, 'nqa': int, 'cnqa': int,
           'slen': int, 'nsa': int, 'cnsa': int,
           'bitscore': float}

# Make pgraphs
pgraph1 = {}
pgraph2 = {}
for qspid in os.listdir('../hsps2hits/out/'):
    for sspid in os.listdir(f'../hsps2hits/out/{qspid}/'):
        with open(f'../hsps2hits/out/{qspid}/{sspid}') as file:
            file.readline()  # Skip header
            for line in file:
                d = {column: f(field) for (column, f), field in zip(columns.items(), line.split())}
                qppid, sppid = d['qppid'], d['sppid']
                qlen, cnqa = d['qlen'], d['cnqa']

                add_edge(qppid, sppid, pgraph1)
                if cnqa / qlen >= 0.5:
                    add_edge(qppid, sppid, pgraph2)

# Make output directory
if not os.path.exists('out/'):
    os.mkdir('out/')

# Write to file
with open('out/pgraph1.tsv', 'w') as file:
    for qppid, sppids in pgraph1.items():
        file.write(qppid + '\t' + ','.join(sppids) + '\n')
with open('out/pgraph2.tsv', 'w') as file:
    for qppid, sppids in pgraph2.items():
        file.write(qppid + '\t' + ','.join(sppids) + '\n')

"""
DEPENDENCIES
../hsps2hits/hsps2hits.py
    ../hsps2hits/out/*/*.tsv
"""