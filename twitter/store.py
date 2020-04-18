### STDLIB IMPORTS
import sys

## INIT COMMANDS
sys.path.append('..')

### LOCAL IMPORTS
from db import DealEyeDB

### PACKAGE IMPORTS
pass

### CONSTANTS
from constants import STATUS
from constants import SCHOOLS


class TwitterDataDB(DealEyeDB):
	def __init__(self, db_path):
		super(TwitterDataDB, self).__init__(db_path)
		self.selected_table = 'twitter_data'

	def get_all_users_as_dict(self):
		return {id:data for id, data in self.read()}

	def get_description(self, id):
		return self.read(id=id, column='description')

	def get_descriptions(self):
		return self.read(column='description')

if __name__ == '__main__':
	pass