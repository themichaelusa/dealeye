import pandas as pd
from utils import to_json_file
from utils import from_json_file

def users_to_xlsx(wpath, data, colns=TWITTER_DB_COLUMNS):
	df = pd.DataFrame(data, columns=colns)
	df.to_excel(wpath)  

def xlsx_to_users(rpath):
	return pd.read_excel(rpath)