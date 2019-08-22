"""Execute the aa_fraction.py script using the IUPRED2a segmented sequences as input."""

from subprocess import run

run('python ../../../src/aa_fraction.py ../segment_iupred2a/segment_iupred2a.tsv ordered Ordered Disordered', shell=True)

"""
OUTPUT
Number of ordered subsequences: 222324
Number of disordered subsequences: 200185
Number of ordered amino acids: 20401660
Number of disordered amino acids: 7683150

DEPENDENCIES
../../../src/aa_fraction.py
../segment_iupred2a/segment_iupred2a.py
    ../segment_iupred2a/segment_iupred2a.tsv
"""