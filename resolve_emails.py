class HunterEmailResolver:
	
	def __init__(self, arg):
		self.client = PyHunter(HUNTER_API_KEY)

		
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

	#f = open("contact_file.txt", "a+")
	#results_dict = defaultdict(list)

	for uid in users_data.keys():
		prof_url = users_data[uid]['profile_url']
		desc_urls = users_data[uid]['description_urls']
		users_data[uid]['checked_contact_domains'].append(prof_url)
		users_data[uid]['checked_contact_domains'].extend(desc_urls)
		desc_urls_len = len(desc_urls)

		print('PROF URL:', prof_url)
		print('DESC_URLs', desc_urls)

		run_urls = [prof_url] # if we only have a prof url or have both, but they are the same
		
		# no valid urls for this user
		if desc_urls_len == 0 and prof_url is None:
			print('CAUSE OF: desc_urls_len == 0 and prof_url is None', run_urls)
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
				#results_dict[uid].extend(contact_emails)
				users_data[uid]['valid_contact_emails'].extend(contact_emails)

		print('ID: {} -> Valid Contact Emails:'.format(uid), users_data[uid]['valid_contact_emails'])

	#f.close()
	to_json_file('contact_save.json', users_data)

	# procedure:
	# check for individual name first 
	# check for 5 personal emails from startup
	# check for 2 general emails from startup
	#pass