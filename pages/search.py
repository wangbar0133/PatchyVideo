
import time

from flask import render_template, request, jsonify, redirect, session

from main import app
from utils.interceptors import loginOptional
from utils.html import buildPageSelector
from utils.tagtools import getTagColor
from services.listVideo import listVideo, listVideoQuery
from services.getVideo import getTagCategoryMap

@app.route('/search', methods = ['POST', 'GET'])
@loginOptional
def pages_search(rd, user):
    rd.page = int(request.values['page'] if 'page' in request.values else 1)
    rd.page_size = int(request.values['page_size'] if 'page_size' in request.values else 20)
    if rd.page_size > 500 :
        rd.reason = 'Page size too large(max 500 videos per page)'
        return 'content_videolist_failed.html'
    rd.query = request.values['query'] if 'query' in request.values else ""
    rd.order = "latest"
    #return 'content_videolist.html'
    if rd.query :
        if len(rd.query) > 256:
            rd.reason = 'Query too long(max 256 characters)'
            return 'content_videolist_failed.html'
        status, videos, related_tags, video_count = listVideoQuery(rd.query, rd.page - 1, rd.page_size)
        rd.videos = videos
    else :
        videos, related_tags = listVideo(rd.page - 1, rd.page_size)
        video_count = videos.count()
        rd.videos = [item for item in videos]
        status = "succeed"
        
    if status == "failed":
        rd.reason = "Syntax error in query"
        return 'content_videolist_failed.html'
    rd.count = video_count
    tag_category_map = getTagCategoryMap(related_tags)
    tag_color_map = getTagColor(tag_category_map)
    rd.tags_list = tag_color_map
    rd.title = 'Search'
    rd.page_count = (video_count - 1) // rd.page_size + 1
    rd.page_selector_text = buildPageSelector(rd.page, rd.page_count, lambda a: 'javascript:gotoPage(%d);'%a)
    return 'content_videolist.html'

