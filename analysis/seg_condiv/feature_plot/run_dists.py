"""Execute the dists.py script using the features of the unshuffled sequences as input."""

from subprocess import run

run('python ../../../src/feature_plot_scripts/dists.py ../feature_calc/', shell=True)

"""
DEPENDENCIES
../feature_plot_scripts/dists.py
../feature_calc/feature_calc.py
    ../feature_calc/features_*.tsv
"""