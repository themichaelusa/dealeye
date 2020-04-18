### STDLIB IMPORTS
import json
import sqlite3

### LOCAL IMPORTS
import constants as cst

### PACKAGE IMPORTS

### CONSTANTS/GLOBALS

class DealEyeDB:
	def __init__(self, db_path):
		self.conn = sqlite3.connect(db_path)
		self.cursor = self.conn.cursor()
		self.selected_table = None

	def __len__(self):
		pass

	### BASIC DB UTILITIES
	def __create_table(self, name):
		self.cursor.execute(cst.CREATE_TABLE_STR.format(name))

	def get_all_table_ids(self, as_gen=False):
		result = self.cursor.execute(
		cst.READ_ALL_IDS_STR.format(
		self.selected_table))

		if as_gen:
			return (id[0] for id in result.fetchall())
		else:
			return [id[0] for id in result.fetchall()]

	def row_exists(self, id):
		#print(type(id), id)
		result = self.cursor.execute(
		cst.ROW_EXISTS_STR.format(
		self.selected_table, id))
		return result.fetchone()[0] > 0

	### BASIC DB OPERATIONS (R/W/A/D)
	# if column=None, read row. if id is None, read_all
	# todo: add multi column read
	def read(self, id=None, column=None):
		if id:
			if column:
				# read column from row with id
				result = self.cursor.execute(
				cst.READ_JSON_KEY_STR.format(
				column, self.selected_table, id))

				result = result.fetchone()
				if result:
					return result[0]
				else:
					return None
			else:
				# read row with id
				result = self.cursor.execute(
				cst.READ_JSON_ROW_STR.format(
				self.selected_table, id))

				result = result.fetchone()
				if result:
					return json.loads(result[1])
				else:
					return None
		else:
			if column:
				# read column from all rows
				result = self.cursor.execute(
				cst.READ_ALL_JSON_KEYS_STR.format(
				column, self.selected_table)).fetchall()

				all_ids = self.get_all_table_ids()
				return [(tid, data[0]) for tid, data in zip(
					all_ids, result)]
			else:
				# read all rows
				result = self.cursor.execute(
				cst.READ_ALL_ROWS_STR.format(
				self.selected_table))

				result = result.fetchall()
				return [(id, json.loads(r)) for id, r in result]

	# if column=None, read row. if id is None, read_all
	def write(self, id, column=None, data=None):
		if data is None:
			return

		# read in row + replace column, or replace row entirely
		result = None
	
		if column:
			result = self.cursor.execute(
			cst.READ_JSON_ROW_STR.format(
			self.selected_table, id))

			result = result.fetchone()[1]
			result = json.loads(result)
			result[column] = data
		else:
			result = data

		result = json.dumps(result)
		
		# if row exists, delete it, otherwise just write to it
		# todo: figure out how update call actually works
		if self.row_exists(id):
			self.delete(id)
		
		self.cursor.execute(
		cst.WRITE_JSON_STR.format(
		self.selected_table), [id, result])

		self.conn.commit()

	def add(self, id, data):
		if not self.row_exists(id):
			self.write(id, data=data)
		else:
			print('ID {} exists'.format(id))

	def delete(self, id=None):
		if id and self.row_exists(id):
			self.cursor.execute(
			cst.DELETE_ROW_STR.format(
			self.selected_table, id))
		self.conn.commit()

	def save(self):
		self.conn.commit()

if __name__ == '__main__':
	pass
			