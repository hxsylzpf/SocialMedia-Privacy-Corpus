"""
    nlp.py
    Responsible for the NLP and summarizer using a tf-idf algorithm.
"""
import math
import nltk
import spacy
import heapq
import string
from collections import Counter, OrderedDict

# Start spacy
print("Loading NLP model...")
nlp = spacy.load('en')

# Download nltk if necessary
print("Downloading nltk (if necessary)...")
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download("stopwords")

# A custom stoplist
STOPLIST = set(nltk.corpus.stopwords.words('english') + ["n't", "'s", "'m", "ca", "’s", "n’t"])

# List of symbols we don't care about
SYMBOLS = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve", "’"]

# Indicates whether a token is valid
def is_valid_token(t):
    return t.ent_type == 0 and not t.is_stop and not t.is_punct and not t.is_space and not t.like_num

# Summarize an article by returning a list of the n best sentences
def summarize(title, text, nLargest=10):
    # Process
    doc = nlp(text)
    title_doc = nlp(title)

    # Extract unique tokens from the document.
    # Filter out stop words, puncutation, and whitespace. If a word is part of a
    # named entity, consider the entire entity, not the individual words.
    tokens = [str(t.lemma_).lower() for t in doc if is_valid_token(t)] + [str(e.lemma_).lower() for e in doc.ents]

    # additional filtering of stopwords and puncutation that spacy didn't catch
    tokens = [t for t in tokens if t not in STOPLIST]
    tokens = [t for t in tokens if t not in SYMBOLS]

    # Count the occurrences of each unique lemma in the text
    # Filter out stop words, puncutation, and whitespace
    lemma_counts = Counter()
    for token in tokens:
        lemma_counts[token] += 1

    # Score the sentences
    sentence_scores = {}
    title_lemmas = [str(t.lemma_).lower() for t in title_doc if is_valid_token(t)] + [str(e.lemma_).lower() for e in title_doc.ents]
    for i, sent in enumerate(doc.sents):
        score = 0
        sent_doc = nlp(sent.text)
        sent_tokens = [str(t.lemma_).lower() for t in sent_doc if is_valid_token(t)] + [str(e.lemma_).lower() for e in sent_doc.ents]
        for token in sent_tokens:
            # tf --> Use raw relative frequencies
            tf = lemma_counts[token] / float(sum(lemma_counts.values()))
            # idf
            # TODO: may not make sense for this application
            idf = 1
            # Give a bonus to this word if it appears in the title
            if token in title_lemmas:
                tf *= 1.1
            score += (tf * idf)
        sentence_scores[i] = score

    # Print out top N sentences in order
    sentences = [s.text.strip() for s in doc.sents]
    best_sentences = heapq.nlargest(nLargest, sentence_scores, key=sentence_scores.get)
    return "\n".join([sentences[i] for i in sorted(best_sentences)])

# Pull out the top words from text, where the words are not stopwords or
# puncutation or whitespace.
def top_words(title, lead, text):
    # Combine the title, lead, and text into a single string
    to_process = "\n".join([title, lead, text])

    # Parse
    doc = nlp(to_process)

     # lemmatize
    tokens = [str(t.lemma_).lower() for t in doc if is_valid_token(t)]

    # additional filtering of stopwords and puncutation that spacy didn't catch
    tokens = [t for t in tokens if t not in STOPLIST]
    tokens = [t for t in tokens if t not in SYMBOLS]

    # Take the most frequent
    return Counter(tokens)

# Pull out all unique words from the text, where the words are not stopwords or
# puncutation or whitespace
def all_words(title, lead, text):
    # Combine the title, lead, and text into a single string
    to_process = "\n".join([title, lead, text])

    # Parse
    doc = nlp(to_process)

     # lemmatize
    tokens = [str(t.lemma_).lower() for t in doc if is_valid_token(t)]

    # additional filtering of stopwords and puncutation that spacy didn't catch
    tokens = [t for t in tokens if t not in STOPLIST]
    tokens = [t for t in tokens if t not in SYMBOLS]

    # Take the most frequent
    return Counter(tokens)
