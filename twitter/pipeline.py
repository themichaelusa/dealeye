### STDLIB IMPORTS
import sys

## INIT COMMANDS
sys.path.append('..')

### LOCAL IMPORTS
from scrape import TwitterScraper
from extract import TwitterDataExtractor
from db import TwitterDataDB

### PACKAGE IMPORTS
pass

### CONSTANTS
from constants import STATUS
from constants import SCHOOLS

### MACROS/LAMBDAS/GLOBALS
pass

### MAIN ###
def main():
	tw_db = TwitterDataDB('../dealeye.db')
	all_rows = tw_db.read(column='keywords_searched')

	new_rows_ids = []
	new_rows_ids.extend([id for id, kw_str in all_rows if 'building' in kw_str])
	new_rows_ids.extend([id for id, kw_str in all_rows if 'leading' in kw_str])
	new_rows_ids.extend([id for id, kw_str in all_rows if 'growth' in kw_str])

	full_rows = {}
	for row_id in new_rows_ids:
		full_rows[row_id] = tw_db.read(id=row_id)

	tde = TwitterDataExtractor(full_rows)
	for id, row in full_rows.items():
		fmt_desc = tde.fmt_description(row['description'])
		print(tde.get_probable_tlink(fmt_desc))

	#print(full_rows)

	"""
	tw_scraper = TwitterScraper()
	status = {'building', 'leading', 'growth'}
	#tw_scraper.gen_keyword_space(SCHOOLS, STATUS)
	tw_scraper.gen_keyword_space(status, SCHOOLS)
	tw_scraper.keyword_space = tw_scraper.keyword_space
	
	users_dict = tw_scraper.pull_users_by_keywords_space()
	tw_data = TwitterDataExtractor(users_dict)
	data_dicts = tw_data.gen_default_data_dicts()

	for uid, data in data_dicts:
		tw_db.add(str(uid), data)
	"""

if __name__ == '__main__':
	#exit()
	main()