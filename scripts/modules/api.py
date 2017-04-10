"""
    api.py
    Responsible for holding methods for accesing the Guardian API
"""
import os
import sys

from . import config, helpers
config.set_import_paths()
api_key = config.get_api_key()

from theguardian import theguardian_tag, theguardian_content

# Get all tag IDs that correspond to a query
def get_tag_ids_for_query(query):
    headers = {
        "q": query
    }
    tags = theguardian_tag.Tag(api=api_key, **headers)
    page_num = 1
    re = ""
    while True:
        try:
            tag_results = tags.get_references_in_page(page_num)
            for r in tag_results:
                if "sectionId" in r:
                    re = re + "id={}, sectionId={}\n".format(r["id"], r["sectionId"])
                else:
                    re = re + "id={}, sectionId=\n".format(r["id"])
            page_num = page_num + 1
        except ValueError:
            break
    return re.strip()

# Get content that corresponds to a tag ID query
def get_content_response_for_query(query):
    headers = {
        "q": query
    }
    tag = theguardian_tag.Tag(api=api_key, **headers)

    # get the results
    tag_content = tag.get_content_response()
    results = tag.get_results(tag_content)

    # get results for specific tag
    first_tag_apiUrl = results[0]["apiUrl"]

    # use this api url to content
    content = theguardian_content.Content(api=api_key, url=first_tag_apiUrl)

    # get content response
    return content.get_content_response()

# Get all content
def get_content_response_for_page(pageNum=1):
    headers = {
        "page": pageNum
    }

    # get content response
    return get_content_response(headers)

# Get content that corresponds to id query
def get_content_response_for_multiple_tags_query(tags, pageNum=1):
    headers = {
        "tag": tags,
        "page": pageNum
    }

    res = get_content_response(headers)

    numPages = res['response']['pages']
    return (numPages, [{ 'id': x['id'], 'title': x['webTitle'],'url': x['webUrl']} for x in res['response']['results']])

# Get a large number of ids that correspond to tag or keyword query
def get_ids_for_query(tags="", keywords="", pageNum=1):
    author_blacklist = ["Guardian readers", "Associated Press"]

    if tags is None or len(tags) == 0:
        tags = "type/article"
    else:
        tags += ",type/article"

    headers = {
        "tag": tags,
        "q": keywords,
        "page": pageNum,
        "page-size": 100,
        "show-fields": "byline"
    }

    res = get_content_response(headers)

    numPages = res['response']['pages']
    ids = [x['id'] for x in res['response']['results'] if "fields" not in x or x['fields']['byline'] not in author_blacklist]

    return (numPages, ids)

# Get content for an article with ID
def get_title_body_tags_for_article_id(articleId):
    headers = {
        "show-fields": "bodyText",
        "show-tags": "keyword"
    }
    content = theguardian_content.Content(api=api_key, **headers)
    single_id_content = content.find_by_id(articleId)
    res = content.get_results(single_id_content)
    title = str(helpers.sanitize(res[0]['webTitle']))
    body_text = str(helpers.sanitize(res[0]['fields']['bodyText']))
    tags = [x['id'] for x in res[0]['tags']]
    return (title, body_text, tags)

# Get content that corresponds to headers
def get_content_response(headers):
    content = theguardian_content.Content(api=api_key,  **headers)
    return content.get_content_response()
