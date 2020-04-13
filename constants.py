### STDLIB IMPORTS
from multiprocessing import cpu_count

### LOCAL IMPORTS

### PACKAGE IMPORTS
from nltk.corpus import stopwords

### CONSTANTS

### GENERAL DB CONSTANTS ###
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

### NLP CONSTANTS
ENGLISH_STOPWORDS = set(stopwords.words('english'))

### PERFORMANCE CONSTANTS
DEFAULT_WORKER_N = 5*cpu_count()

### TWITTER SCRAPER CONSTANTS
SCHOOLS = {'harvard', 'hbs', 'stanford', 'gsb', 'penn', 'upenn', 'wharton'}
STATUS = {'founder', 'co-founder', 'cofounder', 'entrepreneur', 'ceo', 'cfo', 'cto', 'coo'}
MODIFIERS = {'stealth', 'startup'}
EMAIL_BLACKLIST = {'linkedin.com', 'tumblr.com', 'forbes.com', 'wordpress.com', 'instagram.com', 'twitter.com', 'amazon.com', 'medium.com', 'github.com', 'wikipedia.org', 'substack.com','youtube.com', 'reuters.com', 'bbc.co.uk', 'blogspot.com', 'google.com', 'microsoft.com', 'huffpost.com', 'apple.com', 'uber.com', 'inc.com', 'sony.com', 'yahoo.com', 'cisco.com', 'mckinsey.com', 'ge.com', 'jpmorgan.com', 'salesforce.com', 'yext.com', 'goldmansachs.com', 'facebook.com', 'midpennbank.com', 'ironmountain.com', 'gilead.com', 'airbnb.com', 'expedia.com', 'guinnessworldrecords.com', 'crossfit.com', 'mlb.com', 'sonypictures.com', 'philadelphiaeagles.com', 'corporate.comcast.com', 'nba.com', 'deloitte.com', 'accenture.com', 'accel.com', 'ralphlauren.com', 'nike.com', 'vmware.com', 'github.io', 'angel.co', 'ycombinator.com'}
TWITTER_DB_COLUMNS = ['name', 'profile_link', 'keywords_searched', 'description', 'profile_url', 'description_urls', 'valid_contact_emails', 'checked_contact_domains']

### API KEYS + API CONSTANTS

### HUNTER.IO
HUNTER_API_KEY = '32226a108c7f659fffbb25d08343f9cf00f6d359'

### TWITTER
TWITTER_CONSUMER_KEY = 'lKkx9SdW7kmzvSzxuXtqAd4ke'
TWITTER_CONSUMER_SECRET = 'KwiPcudgoT9EBRILa97x8mdxpckVmot1vUjACUun0elrTZrdt7'
TWITTER_ACCESS_TOKEN_KEY = '1245431259679076354-rNiiYaSWoRrS6oC0bmvr7IGyDjDqD6'
TWITTER_ACCESS_TOKEN_SECRET = 'NFkAM70l7AUnywOQjJmsZTgnQFppvTlWmavChW4cWRhdX'
TWITTER_USER_SEARCH_PAGE_SIZE = 20
TWITTER_USER_LINK = 'https://twitter.com/{}'
