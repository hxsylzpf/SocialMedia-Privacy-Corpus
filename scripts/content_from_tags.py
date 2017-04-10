import sys
from modules import api, helpers

# Command line argument is the tag
if len(sys.argv) != 2 and len(sys.argv) != 3:
    print("Usage: content_from_tags.py [tag1,tag2,...] [pageNum]")
    sys.exit(1)

if len(sys.argv) == 3:
    pageNum = int(sys.argv[2])
else:
    pageNum = 1

numPages, results = api.get_content_response_for_multiple_tags_query(sys.argv[1], pageNum)

print("Page {}/{}".format(pageNum, numPages))
for result in results:
    print("{}\n    id={}\n    url={}".format(result['title'], result['id'], result['url']))
