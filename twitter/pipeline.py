### STDLIB IMPORTS
import sys

## INIT COMMANDS
sys.path.append('../')

### LOCAL IMPORTS
import export
from store import TwitterDataDB
from scrape import TwitterScraper
from extract import TwitterDataExtractor
from url_utils import RedirectURLResolver
from email_utils import HunterEmailResolver

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
CONTACT_EMAIL_SCRAPER = HunterEmailResolver()

### MAIN ###
def scrape_users(location, status):
	TW_SCRAPER.gen_keyword_space(location, status)
	users_dict = TW_SCRAPER.pull_users_by_keywords_space()

	TW_CLEANER.set_target(users_dict)
	data_dicts = TW_CLEANER.gen_default_data_dicts()

	for uid, data in data_dicts:
		tw_db.add(str(uid), data)

def extract_user_contact_links():
	users_dict = TW_DB.get_all_users_as_dict()
	TW_CLEANER.set_target(users_dict)
 
	### resolve profile urls
	raw_profile_urls = TW_CLEANER.get_all_users_profile_urls()
	profile_urls = REDIR_URL_RESOLVER(raw_profile_urls)
	TW_CLEANER.filter_profile_urls(profile_urls)

	### get valid twitter accounts from user acct descriptions
	descs_data = TW_CLEANER.get_twitter_accounts_from_desc()
	unames_dict, all_floating_urls = descs_data
	urls_dict = TW_SCRAPER.get_twitter_urls_by_unames(unames_dict)

	### prep all urls for redirect resolution + run resolver
	urls_final = TW_CLEANER.get_all_desc_urls(*descs_data, urls_dict)
	redir_urls = REDIR_URL_RESOLVER(urls_final)
	TW_CLEANER.filter_desc_urls(redir_urls)

	### after all data engineering --> store in DB
	for id, data in TW_CLEANER.get_target().items():
		TW_DB.write(id=id, data=data)

def extract_contact_emails_for_users():
	users_dict = TW_DB.get_all_users_as_dict()
	CONTACT_EMAIL_SCRAPER.set_target(users_dict)

	## filter which emails to parse 
	ids_to_parse = []
	for id, data in users_dict.items():
		if len(data['description_urls']):
			if not len(data['valid_contact_emails']):
				ids_to_parse.append(id)

	CONTACT_EMAIL_SCRAPER.scrape_contact_emails_for_users(
		set(ids_to_parse))
	for id, data in CONTACT_EMAIL_SCRAPER.get_target().items():
		TW_DB.write(id=id, data=data)

def export_db_to_excel(ex_path):
	users_dict = TW_DB.get_all_users_as_dict()

	for id, data in users_dict.items():
		data['valid_contact_emails'] = set(data['valid_contact_emails'])
		try:
			if not len(data['valid_contact_emails']):
				data['valid_contact_emails'] = None
		except Exception as e:
			pass
	
		data['checked_contact_domains'] = set(data['checked_contact_domains'])
		try:
			if not len(data['valid_contact_emails']):
				data['checked_contact_domains'] = None
		except Exception as e:
			pass
		
		users_dict[id] = data

	export.users_to_xlsx(ex_path, users_dict.values())

if __name__ == '__main__':
	#export_db_to_excel('../broader_terms.xlsx')
	extract_user_contact_links()