### STDLIB IMPORTS
import re
import sys
import json
import string  
import socket
from collections import defaultdict

## INIT COMMANDS
sys.path.append('..')
socket.setdefaulttimeout(5)

### LOCAL IMPORTS
from utils import chunks
from utils import get_domain
from utils import rm_emojis
from utils import similar
from utils import most_similar_key

### PACKAGE IMPORTS
pass

### CONSTANTS
from constants import STATUS
from constants import SCHOOLS
from constants import EMAIL_BLACKLIST
from constants import ENGLISH_STOPWORDS
from constants import TWITTER_USER_LINK

### MACROS/LAMBDAS/GLOBALS

class TwitterDataExtractor:
	def __init__(self, users_dict):
		self.users_dict = users_dict

	### GENERAL UTIL FUNCS
	def is_user_valid(self, user_obj):
		uname = user_obj.name
		udesc = user_obj.description

		# check if school is in name. 
		# todo: figure out when school in name, but they went to that school
		if 'Penn' in uname:
			return False
		elif 'Penn_State' in udesc or 'Penn State' in udesc:
			return False

		return True

	def is_blocked_url(self, url):
		if url is not None:
			for blocked_url in EMAIL_BLACKLIST:
				if blocked_url in url:
					return True
		return False

	def gen_data_dict(self, user_obj, kwd_str):
		return {
		'name': rm_emojis(user_obj.name), 
		'profile_link': TWITTER_USER_LINK.format(user_obj.screen_name),
		'keywords_searched': kwd_str,
		'description': user_obj.description,
		'profile_url': user_obj.url,
		'description_urls': [],
		'valid_contact_emails': [],
		'checked_contact_domains': []
		}

	def gen_default_data_dicts(self):
		default_user_dicts = []
		for uid, user_data in self.users_dict.items():
			user_obj, kwd_str = user_data
			data_dict = self.gen_data_dict(user_obj, kwd_str)
			default_user_dicts.append((uid, data_dict))
		return default_user_dicts

	### FORMATTING FUNCS
	def fmt_description(self, desc):
		no_emoji_desc = rm_emojis(desc)
		fmt_desc = no_emoji_desc.replace('\n', ' ')

		fmt_desc = [re.sub(r'(?!_)(?!@)\W+', '', w) for w in fmt_desc.split(' ')]
		fmt_desc = [w.lower() for w in fmt_desc if w != '']
		fmt_desc = [w for w in fmt_desc if w not in ENGLISH_STOPWORDS]

		return fmt_desc

	# todo: also check profile url
	def get_probable_tlink(self, desc):
		for idx, word in enumerate(desc):
			for title in STATUS:
				if title in word:
					for word_pos in range(idx, len(desc)):
						if desc[word_pos][0] == '@':
							return desc[word_pos]

		# todo: check if title in desc string, and if that's in url
		return None

	def get_twitter_accounts_from_desc(self):
		pass

	def scrape_urls_from_descriptions(self):
		unames_dict = defaultdict(list)
		all_floating_urls = []

		# get all existing urls in descs + all @
		for uid in self.users_dict.keys():
			desc = users_dict[uid]['description']

			# get all "@" links
			split_desc = self.fmt_description(desc)
			tlinks = [self.get_probable_tlink(split_desc)]
			tlinks = [tl for tl in tlinks if tl is not None]
			tlinks = [tl[1:] for tl in tlinks if len(tl) > 1]
			tlinks = [tl for tl in tlinks if tl not in SCHOOLS]
			print('PRINTED DESCRIPTION', split_desc)

			# store "@" links in dict to search with twitter api
			for tlink in tlinks:
				if tlink is not None:
					unames_dict[tlink].append(uid)

			# retrieve and store any floating urls
			"""
			raw_urls = [d for d in split_desc if 'https://t.co' in d]
			raw_urls = [d.split('https://')[1][:15] for d in raw_urls]
			for url in raw_urls:
				all_floating_urls.append((uid, url))
			"""

		urls_dict = get_twitter_urls_by_unames(unames_dict)
		urls_final = all_floating_urls 

		for uname, uids in unames_dict.items():
			url = urls_dict[uname] 
			if url is not None:
				urls_final.extend([(uid, url) for uid in uids])

		# resolve all redirectable urls + save them in the users dict
		for uid, url in get_redirect_urls(urls_final):
			final_url = get_domain(url)
			# todo: apply filter to final url

			if '.edu' in final_url or '.mil' in final_url or '.gov' in final_url:
				continue

			if '.org' in final_url or '.net' in final_url:
				continue

			if is_blocked_url(url):
				continue

			users_dict[uid]['description_urls'].append(final_url)
		
	# todo: look behind, and see if current page is duplicate of prev page
	def format_users_dict(self):
		# format users dict: get data we want
		formatted_users = {}
		for uid in self.users_dict.keys():
			user_obj, kwd_str = self.users_dict[uid]

			# todo: filtering step. Name + Description
			if not self.is_user_valid(user_obj):
				continue

			formatted_users[uid] = self.gen_data_dict()

		# parse redirect urls & update urls in fmt_dict
		raw_urls = []
		for uid in formatted_users.keys():
			url = formatted_users[uid]['profile_url']
			raw_urls.append((uid, url))

		urls_data = get_redirect_urls(raw_urls)
		for uid, url in urls_data:
			# apply filter here
			local_url = get_domain(url)
			if url is None:
				local_url = None
			elif is_blocked_url(url):
				local_url = None
			elif '.net' in url or '.org' in url:
				local_url = None
			elif len(url) > 50:
				local_url = None
			elif '.edu' in url or '.mil' in url or '.gov' in url:
				local_url = None

			formatted_users[uid]['profile_url'] = local_url

		for k,v in formatted_users.items():
			url = v['profile_url']
			# todo, do a recursive resolution here
			if url is not None and '://t.co' in url:
				v['profile_url'] = None

		self.scrape_urls_from_descriptions()

		return formatted_users


