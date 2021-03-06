
from db import tagdb as db
from bson import ObjectId
from utils.exceptions import UserError
from services.tcb import filterSingleVideo
from scraper.video import dispatch

def getVideoDetail(vid, user, raise_error = False):
	return filterSingleVideo(vid, user, raise_error)

def getVideoDetailWithTags(vid, language, user) :
	video_obj = filterSingleVideo(vid, user)
	return db.retrive_item_with_tag_category_map(video_obj, language)

def getTagCategoryMap(tags) :
	return db.get_tag_category_map(tags)

def getVideoDetailNoFilter(vid):
	return db.retrive_item(vid)

def getVideoByURL(url) :
	obj, cleanURL = dispatch(url)
	if obj is None:
		raise UserError('UNSUPPORTED_WEBSITE')
	if not cleanURL :
		raise UserError('EMPTY_URL')
	uid = obj.unique_id(obj, cleanURL)
	obj = db.retrive_item({'item.unique_id': uid})
	if obj :
		return obj
	raise UserError('VIDEO_NOT_EXIST')
