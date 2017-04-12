"""
    sentiment.py
    Responsible for interfacing with the sentiment library
"""
# Add senti_classifier to path
from . import config
config.set_import_paths()

from senti_classifier import senti_classifier

def get_sentiment_for_text(text):
    pos_score, neg_score = senti_classifier.polarity_scores([text])
    return { 'pos': pos_score, 'neg': neg_score }
