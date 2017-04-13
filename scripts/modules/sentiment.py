"""
    sentiment.py
    Responsible for interfacing with the sentiment library
    NOTE: Sentiment API has a limit of 1000/day per IP
"""
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def get_sentiment_for_text(text):
    return analyzer.polarity_scores(text)
