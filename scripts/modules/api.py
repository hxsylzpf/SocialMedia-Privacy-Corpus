"""
    api.py
    Responsible for holding methods for accesing the Guardian API
"""
import os
import sys

from . import config
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

# Get body content for an article with ID
def get_body_content(articleId):
    headers = {
        "ids": articleId,
        "show-blocks": "body"
    }
    content = theguardian_content.Content(api=api_key, **headers)
    res = content.get_results(content.get_content_response())
    body_text = str(res[0]['blocks']['body'][0]['bodyTextSummary'])
    return body_text