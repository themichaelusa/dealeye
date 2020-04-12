### IMPORTS
import json
import sqlite3

### CONSTANTS/GLOBALS
CREATE_TABLE_STR = "CREATE TABLE {} (id varchar, data json);"
WRITE_JSON_STR = "insert into {} values (?, ?);"
READ_JSON_KEY_STR = "select json_extract(data, '$.{}') from {} where ID = {};"
READ_JSON_ROW_STR = "select * from {} where ID = {};"
READ_ALL_JSON_KEYS_STR = "select json_extract(data, '$.{}') from {};"
READ_ALL_ROWS_STR = "select * from {};"
READ_ALL_IDS_STR = 'select ID from {}'

class DealEyeDB:
	def __init__(self, db_path):
		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()
		self.selected_table = None

	def __create_table(self, name):
		self.cursor.execute(CREATE_TABLE_STR.format(name))

	def get_all_table_ids(self, as_gen=False):
		result = self.cursor.execute(
			READ_ALL_IDS_STR.format(
			self.selected_table))

		if as_gen:
			return (id[0] for id in result.fetchall())
		else:
			return [id[0] for id in result.fetchall()]

	# if column=None, read row. if id is None, read_all
	def read(self, id=None, column=None):
		if id:
			if column:
				# read column from row with id
				result = self.cursor.execute(
					READ_JSON_KEY_STR.format(
					column, self.selected_table, id))
				return result.fetchone()[0]
			else:
				# read row with id
				result = self.cursor.execute(
					READ_JSON_ROW_STR.format(
					self.selected_table, id))
				return result.fetchone()[1]
		else:
			if column:
				# read column from all rows
				result = self.cursor.execute(
					READ_ALL_JSON_KEYS_STR.format(
					column, self.selected_table)).fetchall()

				all_ids = self.get_all_table_ids()
				return [(tid, data[0]) for tid, data in zip(
					all_ids, result)]
			else:
				# read all rows
				result = self.cursor.execute(
					READ_ALL_ROWS_STR.format(
						self.selected_table))
				return result.fetchall()

	# if column=None, read row. if id is None, read_all
	def write(self, id, column=None, data=None):
		if data is None:
			return

		# read in row + replace column, or replace row entirely
		result = None
	
		if column:
			result = self.cursor.execute(
				READ_JSON_ROW_STR.format(
				self.selected_table, id))
			result = result.fetchone()[1]
			result = json.load(result)
			result[column] = data
		else:
			result = data

class TwitterDataDB(DealEyeDB):
	def __init__(self):
		super(TwitterDataDB, self).__init__()
		self.selected_table = 'twitter_data'

if __name__ == '__main__':
	dealeye_db = DealEyeDB('dealeye.db')
	dealeye_db.selected_table = 'twitter_data'
	rtest = dealeye_db.read()
	print(rtest)
			