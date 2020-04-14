### STDLIB IMPORTS
import sys

## INIT COMMANDS
sys.path.append('..')

### LOCAL IMPORTS
from scrape import TwitterScraper
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
	tw_scraper = TwitterScraper()
	tw_scraper.gen_keyword_space(SCHOOLS, STATUS)
	users_dict_no_check = tw_scraper.pull_users_by_keywords_space()
	
if __name__ == '__main__':
	main()