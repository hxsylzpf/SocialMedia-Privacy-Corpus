"""
    cluster_test_data.py
    Perform clustering on positive test data
    Reference: http://brandonrose.org/clustering
"""
import glob
import numpy as np
from modules import config, helpers

# TODO: switch to real data
(DATA_FOLDER_PATH, YES_FOLDER_PATH, NO_FOLDER_PATH) = config.get_training_data_folder_paths()
training_data_files = glob.glob(YES_FOLDER_PATH + "/*")
training_data = []
for fp in training_data_files:
    with open(fp, 'r') as f:
        record = helpers.json_string_to_object(f.read().strip())
        training_data.append(record)

records = training_data

# Import all core words
all_core_words = list(set([x for record in records for x in record['core-words'].keys()]))

# Convert core word data to CSR matrix as below
#
#    Article1   Word1   Count                       Word1   Word2   Word3   ...
#    Article1   Word2   Count    ===>  Article1     Count   Count   Count
#    Article2   Word1   Count          Article2     Count   Count   Count
#    ...                               ...
#
from scipy.sparse import csr_matrix

matrix_rows = []
for record_num, record in enumerate(records):
    for word_num, word in enumerate(all_core_words):
        row = [record_num, word_num, record['core-words'][word] if word in record['core-words'] else 0]
        matrix_rows.append(row)
matrix_array = np.asarray(matrix_rows)
matrix = csr_matrix((matrix_array[:, 2], (matrix_array[:, 0], matrix_array[:, 1])))

# Clustering
from sklearn.cluster import KMeans

num_clusters = 5
km = KMeans(n_clusters=num_clusters)
km.fit(matrix)

# Print out info
import pandas as pd

clusters = km.labels_.tolist()
articles = { 'id': [record['id'] for record in records], 'cluster': clusters }
frame = pd.DataFrame(articles, index=[clusters], columns=['id', 'cluster'])

print(frame['cluster'].value_counts())

""" Print top terms per cluster """
from collections import Counter

print()
print("Top word per cluster:")
for i in range(num_clusters):
    cluster_records = [records[j] for j in range(len(records)) if clusters[j] == i]
    cluster_core_words_dicts = [record['core-words'] for record in cluster_records]
    cluster_core_words_counters = [Counter(d) for d in cluster_core_words_dicts]
    cluster_core_words = sum(cluster_core_words_counters, Counter())
    print("{}: {}".format(i, cluster_core_words.most_common(8)))

""" Multidimensional scaling """
from sklearn.manifold import MDS
from sklearn.metrics.pairwise import cosine_similarity

mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)
dist = 1 - cosine_similarity(matrix)
pos = mds.fit_transform(dist)
xs, ys = pos[:, 0], pos[:, 1]

""" Visualize document clusters """
import matplotlib.pyplot as plt
import matplotlib as mpl

if True:
    cluster_colors = {0: '#1b9e77', 1: '#d95f02', 2: '#7570b3', 3: '#e7298a', 4: '#66a61e'}
    cluster_names = {0: '1', 1: '2', 2: '3', 3: '4', 4: '5'}

    #create data frame that has the result of the MDS plus the cluster numbers and ids
    df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, id=[record['id'] for record in records]))

    # Group by cluster label
    groups = df.groupby('label')

    # set up plot
    fig, ax = plt.subplots(figsize=(17, 9)) # set size
    ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling

    #iterate through groups to layer the plot
    #note that I use the cluster_name and cluster_color dicts with the 'name' lookup to return the appropriate color/label
    for name, group in groups:
        ax.plot(group.x, group.y, marker='o', linestyle='', ms=12, label=cluster_names[name], color=cluster_colors[name], mec='none')
        ax.set_aspect('auto')
        ax.tick_params(\
            axis= 'x',          # changes apply to the x-axis
            which='both',      # both major and minor ticks are affected
            bottom='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelbottom='off')
        ax.tick_params(\
            axis= 'y',         # changes apply to the y-axis
            which='both',      # both major and minor ticks are affected
            left='off',      # ticks along the bottom edge are off
            top='off',         # ticks along the top edge are off
            labelleft='off')

    ax.legend(numpoints=1)  #show legend with only 1 point

    #add label in x,y position with the label
    # for i in range(len(df)):
    #     ax.text(df.ix[i]['x'], df.ix[i]['y'], df.ix[i]['id'], size=8)
    plt.show()

""" Hierarchical Clustering """
if False:
    from scipy.cluster.hierarchy import ward, dendrogram

    linkage_matrix = ward(dist)

    fig, ax = plt.subplots(figsize=(15, 20)) # set size
    ax = dendrogram(linkage_matrix, orientation="right", labels=[x['title'] for x in records]);

    plt.tick_params(\
        axis= 'x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off')

    plt.tight_layout()

    plt.show()
