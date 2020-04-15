### STDLIB IMPORTS
import sys

## INIT COMMANDS
sys.path.append('..')

### LOCAL IMPORTS
from db import TwitterDataDB
from scrape import TwitterScraper
from extract import TwitterDataExtractor
from url_utils import RedirectURLResolver

### PACKAGE IMPORTS
pass

### CONSTANTS
from constants import STATUS
from constants import SCHOOLS

### MACROS/LAMBDAS/GLOBALS
TW_DB = TwitterDataDB('../dealeye.db')
TW_SCRAPER = TwitterScraper()
TW_CLEANER = TwitterDataExtractor()
REDIR_URL_RESOLVER = RedirectURLResolver()

### MAIN ###
def scrape_users(location, status):
	TW_SCRAPER.gen_keyword_space(location, status)
	users_dict = TW_SCRAPER.pull_users_by_keywords_space()

	TW_CLEANER.set_target(users_dict)
	data_dicts = TW_CLEANER.gen_default_data_dicts()

	for uid, data in data_dicts:
		tw_db.add(str(uid), data)

def extract_user_contact_links():
	users_dict = {id:data for id,data in TW_DB.read()}
	TW_CLEANER.set_target(users_dict)
	print(TW_CLEANER.users_dict)

	### resolve profile urls
	raw_profile_urls = TW_CLEANER.get_all_users_profile_urls()
	profile_urls = REDIR_URL_RESOLVER(raw_profile_urls)
	TW_CLEANER.filter_profile_urls(profile_urls)

	### get valid twitter accounts from user acct descriptions
	descs_data = TW_CLEANER.get_twitter_accounts_from_desc()
	unames_dict, all_floating_urls = descs_data
	urls_dict = TW_SCRAPER.get_twitter_urls_by_unames(unames_dict)

	### prep all urls for redirect resolution + run resolver
	urls_final = TW_CLEANER.get_urls_to_redirect_check(
	*descs_data, urls_dict)
	redir_urls = REDIR_URL_RESOLVER(urls_final)

	### apply filter to our scraped users + store in DB
	TW_CLEANER.filter_user_urls(redir_urls)
	for id, data in TW_CLEANER.get_target().items():
		TW_DB.write(id=id, data=data)

def test():
	#pass

if __name__ == '__main__':
	pass

