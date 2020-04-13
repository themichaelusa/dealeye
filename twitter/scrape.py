

### STDLIB IMPORTS
import re
import sys
import json
import string  
import socket
from collections import defaultdict

## INIT COMMANDS
sys.append('..')
socket.setdefaulttimeout(5)

### LOCAL IMPORTS
from utils import to_json_file
from utils import from_json_file
from utils import chunks
from utils import get_domain
from utils import rm_emojis
from utils import similar
from utils import most_similar_key

### PACKAGE IMPORTS
import twitter
import requests 
import pandas as pd
from pyhunter import PyHunter

### CONSTANTS
from constants import TWITTER_CONSUMER_KEY
from constants import TWITTER_CONSUMER_SECRET
from constants import TWITTER_ACCESS_TOKEN_KEY
from constants import TWITTER_ACCESS_TOKEN_SECRET
from constants import HUNTER_API_KEY

from constants import STATUS
from constants import SCHOOLS
from constants import TWITTER_DB_COLUMNS
from constants import EMAIL_BLACKLIST
from constants import TWITTER_USER_SEARCH_PAGE_SIZE
from constants import ENGLISH_STOPWORDS
from constants import TWITTER_USER_LINK

### MACROS/LAMBDAS/GLOBALS

#keywords_list = ['penn co-founder', 'penn founder', 'penn startup', 'penn ceo', 'penn cfo', 'penn cto', 'penn entrepreneur', 'wharton founder','wharton startup', 'wharton co-founder', 'wharton ceo', 'wharton cfo', 'wharton cto', 'penn entrepreneur', 'harvard startup', 'harvard co-founder', 'harvard founder', 'harvard ceo', 'harvard cfo', 'harvard cto', 'harvard entrepreneur', 'stanford startup', 'stanford co-founder', 'stanford founder', 'stanford cto', 'stanford ceo', 'stanford cto', 'stanford entrepreneur', 'hbs startup', 'hbs co-founder', 'hbs founder', 'hbs cto', 'hbs ceo', 'hbs cto', 'hbs entrepreneur', 'gsb startup', 'gsb co-founder', 'gsb founder', 'gsb cto', 'gsb ceo', 'gsb cto', 'gsb entrepreneur']

class TwitterScraper:
	def __init__(self):
		self.api = twitter.Api(
			consumer_key=TWITTER_CONSUMER_KEY, 
			consumer_secret=TWITTER_CONSUMER_SECRET, 
			access_token_key=TWITTER_ACCESS_TOKEN_KEY, 
			access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)

	### GENERAL UTILITIES
	def gen_keyword_space(self):
		pass

	# todo: look behind, and see if current page is duplicate of prev page
	def pull_users_by_keywords_list(self, keywords_list, user_count=250):
		users_dict = defaultdict(int)

		for kw_str in keywords_list:
			pages = range(int(user_count/TWITTER_USER_SEARCH_PAGE_SIZE))

			for page_num in pages:
				search = self.api.GetUsersSearch(term=kw_str, 
					count=user_count, page=page_num, include_entities=True)

				for user in search:
					uid = str(user.id)
					if users_dict[uid] == 0:
						users_dict[uid] = (user, kw_str)
					else:
						print('duplicate:', uid)

		return users_dict

	def get_twitter_urls_by_unames(self, unames_dict):
		uname_keys = list(unames_dict.keys())
		all_unames = chunks(uname_keys, 100)
		urls_dict = {un: None for un in uname_keys}

		for unames_group in all_unames:
			users = self.api.UsersLookup(screen_name=unames_group)

			# check similarity bc of discrepancy in screen name + actual name
			for user in users:
				closest_key = most_similar_key(user.screen_name, uname_keys)
				print('CLOSEST KEY to {} is {}'.format(user.screen_name, closest_key))
				urls_dict[closest_key] = user.url

		return urls_dict

# filter by username, 
def is_user_valid(self, user_obj):
	uname = user_obj.name
	udesc = user_obj.description

	# check if school is in name. todo: figure out when school in name, but they went to that school
	if 'Penn' in uname:
		return False
	elif 'Penn_State' in udesc or 'Penn State' in udesc:
		return False

	return True

def is_blocked_url(url):
	if url is not None:
		for blocked_url in cst.EMAIL_BLACKLIST:
			if blocked_url in url:
				return True
	return False

def fmt_description(desc):
	no_emoji_desc = rm_emojis(desc)
	fmt_desc = no_emoji_desc.replace('\n', ' ')

	fmt_desc = [re.sub(r'(?!_)(?!@)\W+', '', w) for w in fmt_desc.split(' ')]
	fmt_desc = [w.lower() for w in fmt_desc if w != '']
	fmt_desc = [w for w in fmt_desc if w not in ENGLISH_STOPWORDS]

	return fmt_desc

# todo: also check profile url
def get_probable_tlink(desc):
	#titles = {'ceo', 'cfo', 'cto', 'founder', 'co-founder', 'cofounder'}
	for idx, word in enumerate(desc):
		for title in STATUS:
			if title in word:
				for word_pos in range(idx, len(desc)):
					if desc[word_pos][0] == '@':
						return desc[word_pos]

	# todo: check for examples like these : @cryptonomics\nPhD
	# todo: check if title in desc string, and if that's in url
	return None

def get_twitter_urls_by_unames(unames_dict):
	uname_keys = list(unames_dict.keys())
	all_unames = chunks(uname_keys, 100)
	urls_dict = {un: None for un in uname_keys}

	for unames_group in all_unames:
		users = self.api.UsersLookup(screen_name=unames_group)

		# check similarity bc of discrepancy in screen name + actual name
		for user in users:
			closest_key = most_similar_key(user.screen_name, uname_keys)
			print('CLOSEST KEY to {} is {}'.format(user.screen_name, closest_key))
			urls_dict[closest_key] = user.url

	return urls_dict

def scrape_urls_from_descriptions(users_dict):
	unames_dict = defaultdict(list)
	all_floating_urls = []

	# get all existing urls in descs + all @
	for uid in users_dict.keys():
		desc = users_dict[uid]['description']

		# get all "@" links
		split_desc = fmt_description(desc)
		tlinks = [get_probable_tlink(split_desc)]
		tlinks = [tl for tl in tlinks if tl is not None]
		tlinks = [tl[1:] for tl in tlinks if len(tl) > 1]
		tlinks = [tl for tl in tlinks if tl not in SCHOOLS]
		print('PRINTED DESCRIPTION', split_desc)

		# store "@" links in dict to search with twitter api
		for tlink in tlinks:
			if tlink is not None:
				unames_dict[tlink].append(uid)


		# retrieve and store any floating urls
		all_floating_urls = []
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
def pull_users_by_keywords_list(keywords_list, user_count=250):
	users_dict = defaultdict(int)

	for kw_str in keywords_list:
		pages = range(int(user_count/TWITTER_USER_SEARCH_PAGE_SIZE))

		for page_num in pages:
			search = self.api.GetUsersSearch(term=kw_str, 
				count=user_count, page=page_num, include_entities=True)

			for user in search:
				uid = str(user.id)
				if users_dict[uid] == 0:
					users_dict[uid] = (user, kw_str)
				else:
					print('duplicate:', uid)

	# format users dict: get data we want
	formatted_users = {}
	for uid in users_dict.keys():
		user_obj, kwd_str = users_dict[uid]

		# todo: filtering step. Name + Description
		if not is_user_valid(user_obj):
			continue

		data_dict = {
		'name': rm_emojis(user_obj.name), 
		'profile_link': TWITTER_USER_LINK.format(user_obj.screen_name),
		'keywords_searched': kwd_str,
		'description': user_obj.description,
		'profile_url': user_obj.url,
		'description_urls': [],
		'valid_contact_emails': [],
		'checked_contact_domains': []
		}

		formatted_users[uid] = data_dict

	# parse redirect urls & update urls in fmt_dict
	raw_urls = []
	for uid in formatted_users.keys():
		url = formatted_users[uid]['profile_url']
		raw_urls.append((uid, url))

	urls_data = get_redirect_urls(raw_urls)
	for uid, url in urls_data:
		#print('URL', url)
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

	scrape_urls_from_descriptions(formatted_users)

	return formatted_users

if __name__ == '__main__':
	#keywords_list = gen_keyword_space()
	#users_data = pull_users_by_keywords_list(keywords_list[:10])
	#set_contact_emails_for_user(users_data)

