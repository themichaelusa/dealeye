### STDLIB IMPORTS
import json
from operator import itemgetter

## INIT COMMANDS

### LOCAL IMPORTS

### PACKAGE IMPORTS
from difflib import SequenceMatcher

### MISC HELPERS
def to_json_file(path, data):
	with open(path, 'w+') as jf:
		json.dump(data, jf)

def from_json_file(path):
	with open(path, 'r') as jf:
		return json.load(jf)

### PROCESSING UTILS
def chunks(l, n): 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

### STRING UTILS
rm_emojis = lambda s: s.encode('ascii', 'ignore').decode('ascii')

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def most_similar_key(phrase, keys):
	matches = [(k, similar(phrase, k)) for k in keys]
	return max(matches,key=itemgetter(1))[0] 

### URL UTILS
def get_domain(url):
	if url is not None:
		return url.split('://')[1].split('/')[0].replace('www.', '')