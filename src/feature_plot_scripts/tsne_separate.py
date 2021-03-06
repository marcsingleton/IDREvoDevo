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
num_idx = int(argv[2])  # Number of index columns
type_name = argv[3]  # Name of column denoting segment type
T_name = argv[4]  # Name of True type in sentence case
F_name = argv[5]  # Name of False type in sentence case

paths = filter(lambda x: re.match('features_[0-9]+\.tsv', x), os.listdir(feature_dir))
for path in paths:
    # Read data
    df = pd.read_csv(feature_dir + path, sep='\t', index_col=list(range(num_idx)))

    # Get file index
    j0 = path.find('_')
    j1 = path.find('.tsv')
    i = path[j0+1:j1]

    # Get indices for type
    T_idx = df.index.get_level_values(type_name).array.astype(bool)
    F_idx = ~T_idx

    for idx, name, color in [(T_idx, T_name, 'C0'), (F_idx, F_name, 'C1')]:
        # Get indices for kappa and omega
        subset = df.loc[idx]
        k_idx = subset['kappa'] == -1
        o_idx = subset['omega'] == -1

        for key, fset in fsets.items():
            # Extract features and initialize
            features = fset(subset)
            kl_divs = []

            # Make output directories for feature sets
            cur_dir = f'out/tsne_separate/{i}/{key}/'
            if not os.path.exists(cur_dir):
                os.makedirs(cur_dir)  # Recursive folder creation

            for j in [5 * 2 ** x for x in range(8)]:
                # Calculate t-SNE and transform data
                tsne = TSNE(n_components=2, perplexity=j)
                transform = tsne.fit_transform(features.to_numpy())
                kl_divs.append((j, tsne.kl_divergence_))

                # Plot t-SNEs
                # One panel
                fig, ax = plt.subplots()
                fig.subplots_adjust(bottom=0.225)
                ax.scatter(transform[:, 0], transform[:, 1], s=2, alpha=0.1, label=name, color=color)
                ax.set_title(f't-SNE of Features in {name} Subsequences')
                leg = fig.legend(bbox_to_anchor=(0.5, 0.05), loc='lower center', markerscale=2.5)
                for lh in leg.legendHandles:
                    lh.set_alpha(1)
                plt.savefig(cur_dir + f'tsne{j}_{name}.png')
                plt.close()

                # Color code by kappa and omega
                fig, ax = plt.subplots()
                fig.subplots_adjust(bottom=0.225)
                for cond, label in labels.items():
                    ko_idx = list(map(lambda x: x == cond, zip(k_idx, o_idx)))
                    ax.scatter(transform[ko_idx, 0], transform[ko_idx, 1], s=2, alpha=0.1, label=label)
                ax.set_title('t-SNE of Features\nGrouped by Kappa and Omega Values')
                leg = fig.legend(bbox_to_anchor=(0.5, 0), loc='lower center', ncol=2, markerscale=2.5)
                for lh in leg.legendHandles:
                    lh.set_alpha(1)
                plt.savefig(cur_dir + f'tsne{j}_{name}_ko.png')
                plt.close()

                # Write model
                with open(cur_dir + f'model{j}_{name}.pickle', 'wb') as file:
                    pickle.dump(tsne, file)

            # Write model summaries
            with open(cur_dir + f'model_summary_{name}.txt', 'w') as file:
                file.write('#perplexity\tKL_divergence\n')
                for perp, kl_div in kl_divs:
                    file.write(f'{perp}\t{kl_div}\n')
