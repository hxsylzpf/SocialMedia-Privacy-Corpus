# Include the modules from parent directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from modules import sentiment

sentences = [
    'This wonderful sentence should be amazing and positive',
    'This sentence is trash. Horrible and the worst ever.'
]
for s in sentences:
    print(sentiment.get_sentiment_for_text(s))
