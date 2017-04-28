# Include the modules from parent directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import random
from modules import api, helpers

# Command line argument is the page number
if len(sys.argv) != 2:
    print("Usage: get_random_articles.py [numRandomArticles]")
    sys.exit(1)

numRandomArticles = int(sys.argv[1])
print(numRandomArticles)

numPages = 100000
resultsPerPage = 10

for i in range( 0, numRandomArticles):
    # pick a random page number from the results
    pageNum = random.randint(1 , numPages - 1)
    results = api.get_content_response_for_page(pageNum)

    resultIdx = random.randint(0 , resultsPerPage - 1)

    resultsList = results['response']['results']
    article_id = resultsList[resultIdx]['id']
    print(article_id)
