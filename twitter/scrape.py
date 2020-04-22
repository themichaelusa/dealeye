### STDLIB IMPORTS
import sys
import time
from itertools import product
from collections import defaultdict

## INIT COMMANDS
sys.path.append('..')

### LOCAL IMPORTS
from utils import chunks
from utils import most_similar_key

### PACKAGE IMPORTS
import twitter

### CONSTANTS
from constants import TWITTER_CONSUMER_KEY
from constants import TWITTER_CONSUMER_SECRET
from constants import TWITTER_ACCESS_TOKEN_KEY
from constants import TWITTER_ACCESS_TOKEN_SECRET

from constants import STATUS
from constants import SCHOOLS
from constants import TWITTER_USER_SEARCH_PAGE_SIZE
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

		self.keyword_space = None

	### GENERAL UTILITIES
	def gen_keyword_space(self, location, modifier):
		kw_space = list(product(location, modifier))
		kw_space = [' '.join(kw_pair) for kw_pair in kw_space]
		self.keyword_space = kw_space

	def is_duplicate_search_page(self, prev_page, curr_page):
		if prev_page is None:
			return False

		for prev_user, curr_user in zip(prev_page, curr_page):
			if str(prev_user.id) != str(curr_user.id):
				return False

		return True

	# todo: look behind, and see if current page is duplicate of prev page
	def pull_users_by_keywords_space(self, user_count=200, dup_check=False):
		users_dict = defaultdict(int)

		for kw_str in self.keyword_space:
			pages = range(int(user_count/TWITTER_USER_SEARCH_PAGE_SIZE))
			prev_page = None

			for page_num in pages:
				search = self.api.GetUsersSearch(term=kw_str, 
				page=page_num, include_entities=True)

				#print(kw_str, search)

				# check if page is duplicate, to avoid extra api calls
				if dup_check:
					if self.is_duplicate_search_page(prev_page, search):
						prev_page = None
						break
					else:
						prev_page = search

				for user in search:
					uid = str(user.id)
					if users_dict[uid] == 0:
						users_dict[uid] = (user, kw_str)
					else:
						print('duplicate:', uid)
						pass

			time.sleep(5)

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

if __name__ == '__main__':
	pass

