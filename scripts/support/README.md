# Scripts
Contained within this folder are various support scripts. These files aren't core to the project but are useful for development or investigation.

##### compare_summarizer.py
Prints out the results of the summarizer on training data to compare to commercially available solutions, or just to see the results.

Parameters: If none, selects a random article and returns the 7 best sentences. Optionally, 1st argument is the number of sentences to return, and optionally, 2nd argument is the hash of the file to compare (optional)

##### content_from_tags.py
Prints out content (title and web URL) for a tag query. You can use boolean operators in the tag query.

Parameters: the tag query and the page number of results (i.e. `python content_from_tags.py "technology/apple" 3`)

##### content_response.py
Not sure what this does.

##### evaluate_precision_recall.py
Shows the precision and recall errors for the KeywordPrivacyClassifier. Useful for tuning the keyword threshold parameter.

##### find_random_articles.py
Prints out the article IDs of a number of random articles in the API.

Parameters: the number of articles to get (i.e. `python find_random_articles.py 50`)

##### find_tags.py
Find tags for a query.

Parameters: the query (i.e. `python find_tags.py apple`)

##### find_test_data.py
Given a tag or content search string, find all articles relating to that in the API.

Parameters: type (tag or content), the search string (exactly as it would appear to search The Guardian API directly), whether to write to the test data ID file (true) or print to console (false). Example: `python find_test_data.py tag world/privacy|technology/apple false`

##### get_random_articles.py
Get `n` number of random article IDs from the API.

Parameters: the number of articles to retrieve

##### sort_ids_by_data.py
Given an ID file, sort the IDs by date. This will write back to the file.

Parameters: the id file
