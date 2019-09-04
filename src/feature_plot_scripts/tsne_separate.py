"""Plot t-SNE of feature sets for two classes of subsequences separately."""

import matplotlib.pyplot as plt
import os
import pandas as pd
import pickle
import re
from shared import fsets, labels
from sklearn.manifold import TSNE
from sys import argv

# Input variables
feature_dir = argv[1]  # Feature directory must end in /
T_idx = argv[2]  # Index of True class in sentence case
F_idx = argv[3]  # Index of False class in sentence case
T_name = argv[4]  # Name of True class in sentence case
F_name = argv[5]  # Name of False class in sentence case

paths = filter(lambda x: re.match('features_[0-9]+\.tsv', x), os.listdir(feature_dir))
for path in paths:
    # Load data
    df = pd.read_csv(feature_dir + path, sep='\t', index_col=[0, 1])

    # Get file index
    j0 = path.find('_')
    j1 = path.find('.tsv')
    i = path[j0+1:j1]

    for subset, name, color in [(T_idx, T_name, 'C0'), (F_idx, F_name, 'C1')]:
        # Get indices for plotting
        df_subset = df.loc[subset, :]
        k = df_subset['kappa'] == -1
        o = df_subset['omega'] == -1

        for key, fset in fsets.items():
            # Calculate features and initialize
            feat = fset(df_subset)
            kl_divs = []

            # Make output directories for feature sets
            cur_dir = f'tsne_separate/{i}/{key}/'
            if not os.path.exists(cur_dir):
                os.makedirs(cur_dir)  # Recursive folder creation

            for j in [5 * 2 ** x for x in range(8)]:
                # Calculate t-SNE and transform data
                tsne = TSNE(n_components=2, perplexity=j)
                trans = tsne.fit_transform(feat.to_numpy())
                kl_divs.append((j, tsne.kl_divergence_))

                # Plot t-SNEs
                # One panel
                fig, ax = plt.subplots()
                fig.subplots_adjust(bottom=0.225)
                ax.scatter(trans[:, 0], trans[:, 1], s=2, alpha=0.1, label=name, color=color)
                ax.set_title(f't-SNE of Features in {name} Subsequences')
                leg = fig.legend(bbox_to_anchor=(0.5, 0.05), loc='lower center', markerscale=2.5)
                for lh in leg.legendHandles:
                    lh.set_alpha(1)
                plt.savefig(cur_dir + f'tsne{j}_{subset}.png')
                plt.close()

                # Color code by kappa and omega
                fig, ax = plt.subplots()
                fig.subplots_adjust(bottom=0.225)
                for cond, label in labels.items():
                    ko_idx = list(map(lambda x: x == cond, zip(k, o)))
                    ax.scatter(trans[ko_idx, 0], trans[ko_idx, 1], s=2, alpha=0.1, label=label)
                ax.set_title('t-SNE of Features\nGrouped by Kappa and Omega Values')
                leg = fig.legend(bbox_to_anchor=(0.5, 0), loc='lower center', ncol=2, markerscale=2.5)
                for lh in leg.legendHandles:
                    lh.set_alpha(1)
                plt.savefig(cur_dir + f'tsne{j}_{subset}_ko.png')
                plt.close()

                # Write model
                with open(cur_dir + f'model{j}_{subset}.pickle', 'wb') as file:
                    pickle.dump(tsne, file)

            # Write model summaries
            with open(cur_dir + f'model_summary_{subset}.txt', 'w') as file:
                file.write('#perplexity\tKL_divergence\n')
                for perp, kl_div in kl_divs:
                    file.write(f'{perp}\t{kl_div}\n')
