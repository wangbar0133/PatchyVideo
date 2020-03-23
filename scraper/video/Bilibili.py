
from . import Crawler
from utils.jsontools import *
from utils.encodings import makeUTF8
from utils.html import getInnerText
from dateutil.parser import parse
from datetime import timedelta, datetime
from services.config import Config
import aiohttp
import re

import os

class Bilibili( Crawler ) :
	NAME = 'bilibili'
	PATTERN = r'^(https:\/\/|http:\/\/)?((www|m)\.)?(bilibili\.com\/video\/([aA][vV][\d]+|BV[a-zA-Z0-9]+)|b23\.tv\/([aA][vV][\d]+|BV[a-zA-Z0-9]+))'
	SHORT_PATTERN = r'^([aA][Vv][\d]+|BV[a-zA-Z0-9]+)$'
	VID_MATCH_REGEX = r"([aA][Vv][\d]+|BV[a-zA-Z0-9]+)"
	HEADERS = makeUTF8( { 'Referer' : 'https://www.bilibili.com/', 'User-Agent': '"Mozilla/5.0 (X11; Ubuntu; Linu…) Gecko/20100101 Firefox/65.0"' } )
	HEADERS_NO_UTF8 = { 'Referer' : 'https://www.bilibili.com/', 'User-Agent': '"Mozilla/5.0 (X11; Ubuntu; Linu…) Gecko/20100101 Firefox/65.0"' }

	def get_cookie(self) :
		return {
			'SESSDATA' : Config.BILICOOKIE_SESSDATA,
			'bili_jct' : Config.BILICOOKIE_bili_jct
		}

	def extract_link(self, link) :
		ret = re.search(self.VID_MATCH_REGEX, link)
		vid = ret.group(1)
		if vid[:2].lower() == 'av' :
			vid = vid.lower()
		return vid

	def normalize_url( self, link ) :
		return "https://www.bilibili.com/video/" + self.extract_link(link)

	def expand_url( self, short ) :
		return "https://www.bilibili.com/video/" + short

	def unique_id( self, link ) :
		return 'bilibili:%s' % self.extract_link(link)
	
	def run( self, content, xpath, link, update_video_detail ) :
		raise NotImplementedError()

	async def unique_id_async( self, link ) :
		return self.unique_id(self = self, link = link)
		
	async def run_async(self, content, xpath, link, update_video_detail) :
		vidid = self.extract_link(link)
		try :
			thumbnailURL = xpath.xpath( '//meta[@itemprop="thumbnailUrl"]/@content' )[0]
			title = xpath.xpath( '//h1[@class="video-title"]/@title' )[0]
			desc = getInnerText(xpath.xpath( '//div[@class="info open"]/node()' ))
			uploadDate = parse(xpath.xpath( '//meta[@itemprop="uploadDate"]/@content' )[0]) - timedelta(hours = 8) # convert from Beijing time to UTC
			utags = xpath.xpath( '//meta[@itemprop="keywords"]/@content' )[0]
			utags = list(filter(None, utags.split(',')[1: -4]))
		except :
			return makeResponseSuccess({
				'thumbnailURL': '',
				'title' : '已失效视频',
				'desc' : '已失效视频',
				'site': 'bilibili',
				'uploadDate' : datetime.now(),
				"unique_id": "bilibili:%s" % vidid,
				"utags": [],
				"placeholder": True
			})
		return makeResponseSuccess({
			'thumbnailURL': thumbnailURL,
			'title' : title,
			'desc' : desc,
			'site': 'bilibili',
			'uploadDate' : uploadDate,
			"unique_id": "bilibili:%s" % vidid,
			"utags": utags
		})
