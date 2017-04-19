"""
    summarize_corpus.py
    Performs various summarization tasks on the corpus.
"""
import re
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from modules import config, helpers, sentiment
import plotly
from plotly import tools
import plotly.graph_objs as go
from operator import itemgetter
from collections import Counter, defaultdict
from datetime import datetime
from dateutil import relativedelta
from scipy.sparse import csr_matrix
from scipy.cluster.hierarchy import fcluster, linkage, dendrogram
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.manifold import MDS

# Enable/disable certain features in this script
SENTIMENT_ALL_ARTICLES = False
ARTICLES_PER_MONTH = False
PLATFORM_FREQUENCY = False
HIERARCHICAL_CLUSTERING = False
KMEANS_CLUSTERING = True

# Load the corpus records
data_folder = config.get_test_data_folder_path()
corpus_folder, corpus_id_file = config.get_corpus_ids_path()
with open(corpus_id_file, 'r') as f:
    corpus_ids = [x.strip() for x in f.readlines()]
corpus_hashes = [helpers.md5_hash(x) for x in corpus_ids]
corpus_records = []
for corpus_hash in corpus_hashes:
    with open(os.path.join(data_folder, corpus_hash), 'r') as f:
        corpus_records.append(helpers.json_string_to_object(f.read().strip()))

""" Sentiment of all articles """
if SENTIMENT_ALL_ARTICLES:
    sentiments = []
    # Generate sentiment numbers, consider pos/neg only
    for record in corpus_records:
        sentiment_scores = sentiment.get_sentiment_for_text(record['content'])
        sentiments.append({
            'id': record['id'],
            'title': record['title'],
            'pos': sentiment_scores['pos'],
            'neg': sentiment_scores['neg'],
            'neu': sentiment_scores['neu']
        })
    # Sort by positive sentiment
    sentiments = sorted(sentiments, key=lambda x: x['neu'])
    titles = [x['title'] for x in sentiments]
    positives = [x['pos'] for x in sentiments]
    negatives = [x['neg'] for x in sentiments]
    neutrals = [x['neu'] for x in sentiments]
    # Plot
    trace1 = go.Bar(x=positives, y=titles, name='Positive', orientation='h', marker=dict(color='rgb(0, 190, 75)'))
    trace2 = go.Bar(x=neutrals, y=titles, name='Neutral', orientation='h', marker=dict(color='rgb(215, 215, 215)'))
    trace3 = go.Bar(x=negatives, y=titles, name='Negative', orientation='h', marker=dict(color='rgb(255, 75, 75)'))
    layout = go.Layout(
        barmode='stack',
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            domain=[0,1]
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False
        ),
        showlegend=True,
        title="Corpus Sentiments"
    )
    annotations = []
    for s in sentiments:
        annotations.append(dict(
            xref='paper',yref='y',
            x=0.14, y=s['title'], text=str(s['title']),
            xanchor='right', align='right',
        ))
    # layout['annotations'] = annotations
    fig = go.Figure(data=[trace1, trace2, trace3], layout=layout)
    plotly.offline.plot(fig, filename=config.get_plotly_path())

""" Stats on the number of articles per month """
if ARTICLES_PER_MONTH:
    # Pull the date from the article ID. Article IDs are in the format:
    #   {section}/{OPTIONAL author}/{year}/{month}/{day}/{...}
    def get_year_month_from_articleId(articleId):
        matches = re.match("\S+\/(20\d\d\/\w+)\/\d\d\/\S+", articleId)
        if matches:
            date = datetime.strptime(matches.group(1), '%Y/%b')
            return date

    # Get all dates from each article
    dates = []
    for record in corpus_records:
        dates.append(get_year_month_from_articleId(record['id']))
    # Get date frequency
    frequencies = Counter(dates)
    sorted_frequencies = sorted(frequencies.items(), key=itemgetter(0))
    backfilled_frequencies = []
    for i, freq in enumerate(sorted_frequencies):
        if i > 0:
            last_month = sorted_frequencies[i - 1][0]
            while last_month != freq[0]:
                last_month = last_month + relativedelta.relativedelta(months=1)
                backfilled_frequencies.append((last_month, 0))
        backfilled_frequencies.append(freq)

    # Print out results
    print("month,count")
    for freq in backfilled_frequencies:
        month_string = freq[0].strftime('%m/%Y')
        print("{},{}".format(month_string, freq[1]))
    print()
    average = len(dates)/len(backfilled_frequencies)
    print("Average={}".format(average))
    trace = plotly.graph_objs.Heatmap(
        z=[[x[1] for x in backfilled_frequencies]],
        x=[x[0] for x in backfilled_frequencies],
        y=['1', '2'],
        colorscale='Reds',
        reversescale=False,
        # showscale=False,
    )
    annotations = []
    for freq in sorted_frequencies:
        annotations.append(dict(
            text=freq[1],
            x=freq[0],
            y=['1'],
            xref='x1', yref='y1',
            showarrow=False,
            font=dict(color='black',size=24),
        ))
    fig = plotly.graph_objs.Figure(data=[trace])
    fig['layout'].update(
        title='Monthly Frequency of Social Media Privacy Incidents in Corpus',
        font=dict(color='black',size=24),
        xaxis=dict(ticks='', side='top', autotick=True, tickfont=dict(color='black',size=18)),
        yaxis=dict(ticks='', autotick=False, showticklabels=False),
        # annotations=annotations,
        width=1250,
        height=350,
    )
    plotly.offline.plot(fig, filename=config.get_plotly_path())

""" Frequency of incidents per platform """
if PLATFORM_FREQUENCY:
    # Compute counts
    platform_counts = []
    social_media_platforms = ["Facebook", "Snapchat", "Twitter",
        "Instagram", "LinkedIn", "Reddit", "WhatsApp", "Google+", "Myspace",
        "Tumblr", "Pinterest", "Hangouts"]
    for platform in social_media_platforms:
        counts = { 'platform': platform, 'total_count': 0, 'presence_count': 0 }
        for record in corpus_records:
            text = "\n".join([record['title'], record['lead'], record['content']]).lower()
            count = text.count(platform.lower())
            counts['total_count'] += count
            counts['presence_count'] += 1 if count > 0 else 0
        platform_counts.append(counts)
    # Print out statistics
    print("platform,total,unique")
    for counts in platform_counts:
        print("{},{},{}".format(counts['platform'], counts['total_count'], counts['presence_count']))
    # Generate heatmap
    trace = plotly.graph_objs.Heatmap(
        z=[[x['presence_count'] for x in platform_counts]],
        x=[x['platform'] for x in platform_counts],
        y=['1', '2'],
        colorscale='Reds',
        reversescale=False,
        # showscale=False,
    )
    annotations = []
    for count in platform_counts:
        annotations.append(dict(
            text=count['presence_count'],
            x=count['platform'],
            y=['1'],
            xref='x1', yref='y1',
            showarrow=False,
            font=dict(color='black',size=20),
        ))
    fig = plotly.graph_objs.Figure(data=[trace])
    fig['layout'].update(
        title='Relative Prevalence of Social Media Platforms in Corpus',
        font=dict(color='black',size=20),
        xaxis=dict(ticks='', side='top', autotick=False, tickfont=dict(color='black',size=16)),
        yaxis=dict(ticks='', autotick=False, showticklabels=False),
        annotations=annotations,
        width=1250,
        height=350,
    )
    plotly.offline.plot(fig, filename=config.get_plotly_path())

""" Hierarchical Clustering """
if HIERARCHICAL_CLUSTERING:
    # Convert core word data to CSR matrix as below
    #
    #    Article1   Word1   Count                       Word1   Word2   Word3   ...
    #    Article1   Word2   Count    ===>  Article1     Count   Count   Count
    #    Article2   Word1   Count          Article2     Count   Count   Count
    #    ...                               ...
    #
    matrix_rows = []
    all_core_words = list(set([x for record in corpus_records for x in record['words'].keys()]))
    for record_num, record in enumerate(corpus_records):
        for word_num, word in enumerate(all_core_words):
            row = [record_num, word_num, record['words'][word] if word in record['words'] else 0]
            matrix_rows.append(row)
    matrix_array = np.asarray(matrix_rows)
    matrix = csr_matrix((matrix_array[:, 2], (matrix_array[:, 0], matrix_array[:, 1])))

    # Clustering
    dist = 1 - cosine_similarity(matrix)
    linkage_matrix = linkage(dist, method='ward')
    fig, ax = plt.subplots(figsize=(15, 20)) # set size
    ax = dendrogram(
        linkage_matrix,
        orientation="right",
        labels=[x['title'] for x in corpus_records],
        color_threshold=0.7*max(linkage_matrix[:,2]));
    plt.tick_params(\
        axis= 'x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off')
    plt.tight_layout()
    # plt.show()
    plt.savefig(config.get_matplotlib_path())

    # Get words per color - http://www.nxn.se/valent/extract-cluster-elements-by-color-in-python
    cluster_idxs = defaultdict(list)
    for c, pi in zip(ax['color_list'], ax['icoord']):
        for leg in pi[1:3]:
            i = (leg - 5.0) / 10.0
            if abs(i - int(i)) < 1e-5:
                cluster_idxs[c].append(int(i))
    cluster_classes = {}
    for c, l in cluster_idxs.items():
        i_l = [ax['ivl'][i] for i in l]
        cluster_classes[c] = [record for record in corpus_records if record['title'] in i_l]
    top_core_words = {}
    for c, cluster_records in cluster_classes.items():
        cluster_core_words_dicts = [record['words'] for record in cluster_records]
        cluster_core_words_counters = [Counter(d) for d in cluster_core_words_dicts]
        cluster_core_words = sum(cluster_core_words_counters, Counter())
        top_core_words[c] = [w for w, wc in cluster_core_words.most_common(35)]
    for c, top_words in top_core_words.items():
        others = set(sum([v for k, v in top_core_words.items() if k != c], []))
        disjoint = set(top_words) - others
        ordered_disjoint = [x for x in top_words if x in disjoint]
        print("{}: {}".format(c, ordered_disjoint))

""" K-Means Clustering """
if KMEANS_CLUSTERING:
    # Convert word data to CSR matrix as below
    #
    #    Article1   Word1   Count                       Word1   Word2   Word3   ...
    #    Article1   Word2   Count    ===>  Article1     Count   Count   Count
    #    Article2   Word1   Count          Article2     Count   Count   Count
    #    ...                               ...
    #
    matrix_rows = []
    all_core_words = list(set([x for record in corpus_records for x in record['core-words'].keys()]))
    for record_num, record in enumerate(corpus_records):
        for word_num, word in enumerate(all_core_words):
            row = [record_num, word_num, record['core-words'][word] if word in record['core-words'] else 0]
            matrix_rows.append(row)
    matrix_array = np.asarray(matrix_rows)
    matrix = csr_matrix((matrix_array[:, 2], (matrix_array[:, 0], matrix_array[:, 1])))

    # Clustering. Use k-means++ to initialize cluster. Use parallel computation.
    num_clusters = 5
    km = KMeans(n_clusters=num_clusters, init='k-means++', n_jobs=-1)
    km.fit(matrix)

    # Print out per-cluster info
    clusters = km.labels_.tolist()
    articles = { 'id': [record['id'] for record in corpus_records], 'cluster': clusters }
    frame = pd.DataFrame(articles, index=[clusters], columns=['id', 'cluster'])
    print(frame['cluster'].value_counts())

    # Print out top words per cluster
    top_core_words = {}
    for i in range(num_clusters):
        cluster_records = [corpus_records[j] for j in range(len(corpus_records)) if clusters[j] == i]
        cluster_core_words_dicts = [record['core-words'] for record in cluster_records]
        cluster_core_words_counters = [Counter(d) for d in cluster_core_words_dicts]
        cluster_core_words = sum(cluster_core_words_counters, Counter())
        top_core_words[i] = [w for w, wc in cluster_core_words.most_common(30)]
    for c, top_words in top_core_words.items():
        others = set(sum([v for k, v in top_core_words.items() if k != c], []))
        disjoint = set(top_words) - others
        ordered_disjoint = [x for x in top_words if x in disjoint]
        print("{}: {}".format(c, ordered_disjoint))

    # Make a visual plot using MDS
    mds = MDS(n_components=2, dissimilarity="precomputed", random_state=1)
    dist = 1 - cosine_similarity(matrix)
    pos = mds.fit_transform(dist)
    xs, ys = pos[:, 0], pos[:, 1]
    cluster_colors = {0: '#F44336', 1: '#3F51B5', 2: '#4CAF50', 3: '#FFC107', 4: '#00BCD4' }#, 5: '#9C27B0'}
    cluster_names = {0: '1', 1: '2', 2: '3', 3: '4', 4: '5'}#, 5: '6'}
    df = pd.DataFrame(dict(x=xs, y=ys, label=clusters, id=[record['id'] for record in corpus_records]))
    groups = df.groupby('label')
    fig, ax = plt.subplots(figsize=(17, 9)) # set size
    ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling
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
    plt.savefig(config.get_matplotlib_path(), dpi=300)
    plt.show()
