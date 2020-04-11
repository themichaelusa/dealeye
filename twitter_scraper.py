import json
import re  
import string  
import socket
import pandas as pd
import requests 
import twitter
from collections import defaultdict
from difflib import SequenceMatcher
from operator import itemgetter

import nltk
from nltk.corpus import stopwords

import concurrent.futures
from multiprocessing import cpu_count

schools = {'harvard', 'hbs', 'stanford', 'gsb', 'penn', 'upenn', 'penn_state'}
uni_contacts = ['harvard.edu']
csuite = ['ceo', 'cfo', 'cto']
status = ['founder', 'co-founder', 'entrepreneur']
modifiers = ['stealth', 'startup']
email_exclude = ['linkedin.com', 'tumblr.com', 'forbes.com', 'wordpress.com', 'instagram.com', 'twitter.com', 'amazon.com', 'medium.com', 'github.com', 'wikipedia.org', 'substack.com','youtube.com', 'reuters.com', 'bbc.co.uk', 'blogspot.com', 'google.com', 'microsoft.com', 'huffpost.com', 'apple.com', 'uber.com', 'inc.com', 'sony.com', 'yahoo.com', 'cisco.com', 'mckinsey.com', 'ge.com', 'jpmorgan.com', 'salesforce.com', 'yext.com', 'goldmansachs.com', 'facebook.com', 'midpennbank.com', 'ironmountain.com', 'gilead.com', 'airbnb.com', 'expedia.com', 'guinnessworldrecords.com', 'crossfit.com', 'mlb.com', 'sonypictures.com', 'philadelphiaeagles.com', 'corporate.comcast.com', 'nba.com', 'deloitte.com', 'accenture.com', 'accel.com', 'ralphlauren.com', 'nike.com', 'vmware.com', 'github.io', 'angel.co', 'ycombinator.com']
USER_SEARCH_PAGE_SIZE = 20

STOPWORDS = set(stopwords.words('english'))


# working query list

# harvard co-founder
# harvard ceo
# harvard founder
# stanford cto
# stanford ceo
# stanford founder
# stanford co-founder
# penn co-founder
# penn founder
# penn startup
# wharton founder
# wharton startup
# wharton co-founder

socket.setdefaulttimeout(5)
DEFAULT_WORKER_N = 5*cpu_count()
keywords_list = ['penn co-founder', 'penn founder', 'penn startup', 'penn ceo', 'penn cfo', 'penn cto', 'penn entrepreneur', 'wharton founder','wharton startup', 'wharton co-founder', 'wharton ceo', 'wharton cfo', 'wharton cto', 'penn entrepreneur', 'harvard startup', 'harvard co-founder', 'harvard founder', 'harvard ceo', 'harvard cfo', 'harvard cto', 'harvard entrepreneur', 'stanford startup', 'stanford co-founder', 'stanford founder', 'stanford cto', 'stanford ceo', 'stanford cto', 'stanford entrepreneur', 'hbs startup', 'hbs co-founder', 'hbs founder', 'hbs cto', 'hbs ceo', 'hbs cto', 'hbs entrepreneur', 'gsb startup', 'gsb co-founder', 'gsb founder', 'gsb cto', 'gsb ceo', 'gsb cto', 'gsb entrepreneur']
columns = ['Name', 'Profile Link', 'Keywords Searched', 'Description', 'Profile URL', 'Description URLS', 'Contact Email (Primary)', 'Contact Email (Secondary)']

rm_punc = string.punctuation
twitter_user_link = 'https://twitter.com/{}'

rm_emojis = lambda s: s.encode('ascii', 'ignore').decode('ascii')

def get_school(kwd):
	school = kwd.split(' ')[0]
	if school in ['penn', 'wharton']:
		return 'upenn.edu'
	elif school in ['harvard', 'hbs']:
		return 'harvard.edu'
	elif school in ['stanford', 'gsb']:
		return 'stanford.edu'

def get_domain(url):
	if url is not None:
		return url.split('://')[1].split('/')[0].replace('www.', '')

twitter_api = twitter.Api(consumer_key='lKkx9SdW7kmzvSzxuXtqAd4ke', 
	consumer_secret='KwiPcudgoT9EBRILa97x8mdxpckVmot1vUjACUun0elrTZrdt7', 
	access_token_key='1245431259679076354-rNiiYaSWoRrS6oC0bmvr7IGyDjDqD6', 
	access_token_secret='NFkAM70l7AUnywOQjJmsZTgnQFppvTlWmavChW4cWRhdX')

from pyhunter import PyHunter

### CONSTANTS
HUNTER_API_KEY = '32226a108c7f659fffbb25d08343f9cf00f6d359'
HUNTER_CLIENT = PyHunter(HUNTER_API_KEY)


### MISC HELPERS
def to_json_file(path, data):
	with open(path, 'w+') as jf:
		json.dump(data, jf)

def from_json_file(path):
	with open(path, 'r') as jf:
		return json.load(jf)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def most_similar_key(phrase, keys):
	matches = [(k, similar(phrase, k)) for k in keys]
	return max(matches,key=itemgetter(1))[0] 

def chunks(l, n): 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

"""
def gen_keyword_space():
	pass
"""

def get_redirect_url(data):
	uid, url = data
	redirect_url = None

	if url is not None:
		redirect_url = requests.get(url, timeout=20).url


	print('For ID: {} URL retrieved: {}'.format(
		uid, redirect_url))

	return uid, redirect_url

def get_redirect_urls(data, workers=DEFAULT_WORKER_N):
	resp_err, resp_ok = 0, 0
	urls_data = []

	# verify emails conncurrently
	with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
	    future_to_smtp = {executor.submit(get_redirect_url, d): d for d in data}

	    for future in concurrent.futures.as_completed(future_to_smtp):

	        try:
	            data = future.result()
	            #print("PARSE DONE: {}".format(data))
	            urls_data.append(data)
	        except Exception as exc:
	        	# todo: add loggers here
	            resp_err = resp_err + 1
	        else:
	            resp_ok = resp_ok + 1

	return (d for d in urls_data)

# filter by username, 
def is_user_valid(user_obj):
	uname = user_obj.name
	udesc = user_obj.description

	# check if school is in name. todo: figure out when school in name, but they went to that school
	if 'Penn' in uname:
		return False
	elif 'Penn_State' in udesc or 'Penn State' in udesc:
		return False

	return True

def is_blocked_url(url):
	if url is not None:
		for blocked_url in email_exclude:
			if blocked_url in url:
				return True
	return False

def fmt_description(desc):
	raw_desc = rm_emojis(desc)
	raw_desc = [d.lower() for d in raw_desc.split(' ') if d != '']
	return [d for d in raw_desc if d not in STOPWORDS]

# todo: also check profile url
def get_probable_tlink(desc):
	titles = {'ceo', 'cfo', 'cto', 'founder', 'co-founder', 'cofounder'}
	for idx, word in enumerate(desc):
		for title in titles:
			if title in word:
				for word_pos in range(idx, len(desc)):
					if desc[word_pos][0] == '@':
						return desc[word_pos]

	# todo: check for examples like these : @cryptonomics\nPhD
	# todo: check if title in desc string, and if that's in url
	return None

def get_twitter_urls_by_unames(unames_dict):
	uname_keys = list(unames_dict.keys())
	all_unames = chunks(uname_keys, 100)
	urls_dict = {un: None for un in uname_keys}

	for unames_group in all_unames:
		users = twitter_api.UsersLookup(screen_name=unames_group)

		# check similarity bc of discrepancy in screen name + actual name
		for user in users:
			closest_key = most_similar_key(user.screen_name, uname_keys)
			print('CLOSEST KEY to {} is {}'.format(user.screen_name, closest_key))
			urls_dict[closest_key] = user.url

	return urls_dict

def scrape_urls_from_descriptions(users_dict):
	unames_dict = defaultdict(list)
	all_floating_urls = []

	# get all existing urls in descs + all @
	for uid in users_dict.keys():
		desc = users_dict[uid]['Description']

		# get all "@" links
		split_desc = fmt_description(desc)
		#print("DESC:", split_desc)
		tlinks = [get_probable_tlink(split_desc)]
		tlinks = [tl for tl in tlinks if tl is not None]
		tlinks = [tl[1:] for tl in tlinks if len(tl) > 1]
		tlinks = [re.sub(r'\W+', '', tl) for tl in tlinks]
		tlinks = [tl for tl in tlinks if tl not in schools]

		#tlinks = [tl for tl in split_desc if tl[0] == '@']
		#tlinks = [tl[1:] for tl in tlinks if len(tl) > 1]
		#tlinks = [re.sub(r'\W+', '', tl) for tl in tlinks]

		# store "@" links in dict to search with twitter api
		for tlink in tlinks:
			if tlink is not None:
				unames_dict[tlink].append(uid)

		#if len(tlinks) == 0:
		# todo: 
		#print("P TLINK: ", tlinks)


		# retrieve and store any floating urls
		"""
		raw_urls = [d for d in split_desc if 'https://t.co' in d]
		raw_urls = [d.split('https://')[1][:15] for d in raw_urls]
		for url in raw_urls:
			all_floating_urls.append((uid, url))
		"""

	urls_dict = get_twitter_urls_by_unames(unames_dict)
	urls_final = []
	#urls_final = all_floating_urls 

	for uname, uids in unames_dict.items():
		url = urls_dict[uname] 
		if url is not None:
			urls_final.extend([(uid, url) for uid in uids])

	# resolve all redirectable urls + save them in the users dict
	for uid, url in get_redirect_urls(urls_final):
		final_url = get_domain(url)
		# todo: apply filter to final url

		if '.edu' in final_url or '.mil' in final_url or '.gov' in final_url:
			continue

		if '.org' in final_url or '.net' in final_url:
			continue

		if is_blocked_url(url):
			continue

		users_dict[uid]['Description URLS'].append(final_url)

# todo: look ahead, and see if next page is duplicate of prev page
def pull_users_by_keywords_list(keywords_list, user_count=250):
	users_dict = defaultdict(int)

	for kw_str in keywords_list:
		pages = range(int(user_count/USER_SEARCH_PAGE_SIZE))

		for page_num in pages:
			search = twitter_api.GetUsersSearch(term=kw_str, 
				count=user_count, page=page_num, include_entities=True)

			for user in search:
				uid = str(user.id)
				if users_dict[uid] == 0:
					users_dict[uid] = (user, kw_str)
				else:
					print('duplicate:', uid)

	# format users dict: get data we want
	formatted_users = {}
	for uid in users_dict.keys():
		user_obj, kwd_str = users_dict[uid]

		# todo: filtering step. Name + Description
		if not is_user_valid(user_obj):
			continue
	 
		data_dict = {
		'Name': rm_emojis(user_obj.name), 
		'Profile Link': twitter_user_link.format(user_obj.screen_name),
		'Keywords Searched': kwd_str,
		'Description': user_obj.description,
		'Profile URL': user_obj.url,
		'Description URLS': [],
		'Contact Email (Primary)': None, 
		'Contact Email (Secondary)': None,
		'Valid Contact Emails': [],
		'Contact Domains (Checked)': []
		}

		#get_school(kwd_str)
		#print('raw url:', user_obj.url)
		#print('profile url:', data_dict['Profile URL'])
		formatted_users[uid] = data_dict

	# parse redirect urls & update urls in fmt_dict
	raw_urls = []
	for uid in formatted_users.keys():
		url = formatted_users[uid]['Profile URL']
		raw_urls.append((uid, url))

	urls_data = get_redirect_urls(raw_urls)
	for uid, url in urls_data:
		#print('URL', url)
		# apply filter here
		local_url = get_domain(url)
		if url is None:
			local_url = None
		elif is_blocked_url(url):
			local_url = None
		elif '.net' in url or '.org' in url:
			local_url = None
		elif len(url) > 50:
			local_url = None
		elif '.edu' in url or '.mil' in url or '.gov' in url:
			local_url = None

		formatted_users[uid]['Profile URL'] = local_url

	for k,v in formatted_users.items():
		url = v['Profile URL']
		# todo, do a recursive resolution here
		if url is not None and '://t.co' in url:
			v['Profile URL'] = None

	scrape_urls_from_descriptions(formatted_users)

	return formatted_users

def get_contact_email_from_domain(domain):
	emails = None

	try:
		emails_data = HUNTER_CLIENT.domain_search(domain=domain, emails_type='personal', limit=2)
		#print('email: {} | csc: {}'.format(email, csc))
		emails = [e['value'] for e in emails_data['emails']]
	except Exception as e:
		print("ERROR: ", e)

	return emails

def set_contact_emails_for_user(users_data):
	# py hunter

	# meta-procedure:
	# todo: check if name is a valid name 
	# check Profile URL first if valid

	f = open("contact_file.txt", "a+")
	results_dict = defaultdict(list)

	for uid in users_data.keys():
		prof_url = users_data[uid]['Profile URL']
		desc_urls = users_data[uid]['Description URLS']
		users_data[uid]['Contact Domains (Checked)'].append(prof_url)
		users_data[uid]['Contact Domains (Checked)'].extend(desc_urls)
		desc_urls_len = len(desc_urls)

		print('PROF URL:', prof_url)
		print('DESC_URLs', desc_urls)

		run_urls = [prof_url] # if we only have a prof url or have both, but they are the same
		
		# no valid urls for this user
		if desc_urls_len == 0 and prof_url is None:
			print('CAUSE OF: desc_urls_len == 0 and prof_url is None', run_urls)
			results_dict[uid] = []
			continue

		# if we only have a desc url
		elif desc_urls_len > 0 and prof_url is None:
			run_urls = [desc_urls[0]]
			print('RESPONSE TO: desc_urls_len > 0 and prof_url is None', run_urls)

		# if we have both, but both are different 
		elif desc_urls_len > 0 and prof_url != desc_urls[0]:
			run_urls.append(desc_urls[0])
			print('RESPONSE TO: desc_urls_len > 0 and prof_url != desc_urls[0', run_urls)
		
		for url in run_urls:
			contact_emails = get_contact_email_from_domain(url)
			if contact_emails is not None:
				results_dict[uid].extend(contact_emails)
				users_dict[uid]['Valid Contact Emails'].extend(contact_emails)
				for email in contact_emails:
					f.write('{},{}\n'.format(uid, email))  
			else:
				results_dict[uid] = []

		"""
		# if we have a valid description url
		if desc_urls_len > 0 and prof_url not in desc_urls:
			print('desc_urls_len > 0 and prof_url not in desc_urls', desc_urls[0])
			run_url = desc_urls[0]
		else:
			print('desc_urls_len == 0 or prof_url in desc_urls', prof_url)

		### TODO do work
		res = get_contact_email_from_domain(run_url)

		# profile url failed, no desc url, move on
		if res_prof is None and run_url == prof_url and desc_urls_len == 0:
			results.append((uid, res))
			continue
		elif res_prof is None and run_url == prof_url and desc_urls_len > 0:
			if 

		if res_prof is None and desc_urls_len:
			run_url = prof_url
			res2 = get_contact_email_from_domain(run_url)
			results_sublist

		re
		"""

		### TODO do work again

		"""
		uname = users_data[uid]['Name'] 
		school_domain = users_data[uid]['Description URLS'][0]

		email = 'NONE'
		try:
			email, csc = HUNTER_CLIENT.email_finder(school_domain, full_name=uname)
			print('email: {} | csc: {}'.format(email, csc))
		except Exception as e:
			pass

		users_data[uid]['Contact Email (Primary)'] = email
		"""

	print(results_dict)
	f.close()
	#to_json_file('contact_save.json', users_data)


	#email, confidence_score = HUNTER_CLIENT.email_finder('instragram.com', full_name='KS')
	# check Description URLS second if there's a match

	# procedure:
	# check for individual name first 
	# check for 5 personal emails from startup
	# check for 2 general emails from startup
	pass

def users_to_xlsx(wpath, data, colns=columns):
	df = pd.DataFrame(data, columns=colns)
	df.to_excel(wpath)  

def xlsx_to_users(rpath):
	return pd.read_excel(rpath)

if __name__ == '__main__':
	#keywords_list = gen_keyword_space()
	users_data = pull_users_by_keywords_list(keywords_list[:1])
	set_contact_emails_for_user(users_data)
	exit()
	for uid, data in users_data.items():
		#print('DESC:', data['Description'])
		print('NAME: ', data['Name'])
		print('ID {} -> PROFILE URL', data['Profile URL'])
		print('DESC URLS', data['Description URLS'])
	#print(users_data)
	#set_contact_emails_for_user(users_data)

	#users_data = from_json_file('contact_save.json')
	#users_to_xlsx('test_final.xlsx', users_data.values())

