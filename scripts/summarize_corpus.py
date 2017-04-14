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
from collections import Counter
from datetime import datetime
from dateutil import relativedelta

# Enable/disable certain features in this script
SENTIMENT_ALL_ARTICLES = False
ARTICLES_PER_MONTH = True
PLATFORM_FREQUENCY = False

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
            font=dict(color='black',size=24),
        ))
    fig = plotly.graph_objs.Figure(data=[trace])
    fig['layout'].update(
        title='Relative Prevalence of Social Media Platforms in Corpus',
        font=dict(color='black',size=24),
        xaxis=dict(ticks='', side='top', autotick=False, tickfont=dict(color='black',size=18)),
        yaxis=dict(ticks='', autotick=False, showticklabels=False),
        annotations=annotations,
        width=1250,
        height=350,
    )
    plotly.offline.plot(fig, filename=config.get_plotly_path())
