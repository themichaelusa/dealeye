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
UPDATE_ROW_STR = 'update {} set data = "{}" where ID = {};'
DELETE_ROW_STR = 'delete from {} where ID = {};'
ROW_EXISTS_STR = 'select count(*) from {} where ID = {};'

class DealEyeDB:
	def __init__(self, db_path):
		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()
		self.selected_table = None

	def __len__(self):
		pass

	### BASIC DB UTILITIES
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

	def row_exists(self, id):
		result = self.cursor.execute(
			ROW_EXISTS_STR.format(
			self.selected_table, id))
		return result.fetchone()[0] > 0

	### BASIC DB OPERATIONS (R/W/A/D)
	# if column=None, read row. if id is None, read_all
	def read(self, id=None, column=None):
		if id:
			if column:
				# read column from row with id
				result = self.cursor.execute(
					READ_JSON_KEY_STR.format(
					column, self.selected_table, id))

				result = result.fetchone()
				if result:
					return result[0]
				else:
					return None
			else:
				# read row with id
				result = self.cursor.execute(
					READ_JSON_ROW_STR.format(
					self.selected_table, id))

				result = result.fetchone()
				if result:
					return result[1]
				else:
					return None
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
			result = json.loads(result)
			result[column] = data
		else:
			result = data

		result = json.dumps(result)
	
		if self.row_exists(id):
			#print(UPDATE_ROW_STR.format(self.selected_table, result, id))
			"""
			self.cursor.execute(
			UPDATE_ROW_STR.format(
			self.selected_table, result, id))
			"""
			self.delete(id)
		
		#
		self.cursor.execute(
			WRITE_JSON_STR.format(
			self.selected_table), [id, result])

		self.conn.commit()

	def add(self, id, data):
		self.write(id, data=data)

	def delete(self, id=None):
		if id and self.row_exists(id):
			self.cursor.execute(
				DELETE_ROW_STR.format(
				self.selected_table, id))
		self.conn.commit()

class TwitterDataDB(DealEyeDB):
	def __init__(self):
		super(TwitterDataDB, self).__init__()
		self.selected_table = 'twitter_data'

if __name__ == '__main__':
	dealeye_db = DealEyeDB('dealeye.db')
	dealeye_db.selected_table = 'twitter_data'
	#rtest = dealeye_db.read()
	#dealeye_db.add(id='69', data={"name": "Emre Ertan", "profile_link": "https://twitter.com/emre_ertan", "keywords_searched": "gsb entrepreneur", "description": "Head of Growth at Slice and unroll.me, former entrepreneur, ocean lover, lucky basketball player, book enthusiast, GSB\'14.", "profile_url": None, "description_urls": [], "valid_contact_emails": [], "checked_contact_domains": [None]})
	print(dealeye_db.read(id='69'))
	#dealeye_db.delete('69')

	#dealeye_db.write(id='69', data='Boi Wassup', column='name')


	#print(rtest)
			