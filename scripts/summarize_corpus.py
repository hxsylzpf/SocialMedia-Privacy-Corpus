"""
    summarize_corpus.py
    Performs various summarization tasks on the corpus.
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from modules import config, helpers, sentiment
import plotly
from plotly import tools
import plotly.graph_objs as go

# Enable/disable certain features in this script
SENTIMENT_ALL_ARTICLES = True

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

    # fig, ax = plt.subplots(figsize=(17, 9))
    # p1 = ax.barh(indices, positives, color=(0, 0.75, 0.25))
    # p2 = ax.barh(indices, negatives, left=positives, color=(1, .25, .25))
    # ax.set_title("Corpus Sentiment")
    # ax.set_xticklabels(())
    # ax.set_yticklabels([x['title'] for x in sentiments])
    # ax.legend((p1[0], p2[0]), ('Positive', 'Negative'))
    # plt.show()
