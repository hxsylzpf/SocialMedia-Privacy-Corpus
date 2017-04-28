""" Sorts ids in an ID file by date """
import sys
import re
from datetime import datetime

def get_year_month_day_from_articleId(articleId):
    matches = re.match("\S+\/(20\d\d\/\w+\/\d\d)\/\S+", articleId)
    if matches:
        date = datetime.strptime(matches.group(1), '%Y/%b/%d')
        return date

if len(sys.argv) != 2:
    print("Usage: sort_ids_by_date.py [path to id file]")
    sys.exit()
else:
    filepath = sys.argv[1]

with open(filepath, 'r') as f:
    ids = f.readlines()

ids = sorted(ids, key=lambda x: get_year_month_day_from_articleId(x))

with open(filepath, 'w') as f:
    f.write("".join(ids))
