### STDLIB IMPORTS
pass

## INIT COMMANDS
pass

### LOCAL IMPORTS
pass

### PACKAGE IMPORTS
from pyhunter import PyHunter

### CONSTANTS
from constants import HUNTER_API_KEY

class HunterEmailResolver:
	def __init__(self):
		self.client = PyHunter(HUNTER_API_KEY)
		self.users_dict = None

	### GENERAL UTIL FUNCS
	def get_target(self):
		return self.users_dict

	def set_target(self, users_dict):
		self.users_dict = users_dict
		
	def get_contact_email_from_domain(self, domain):
		emails = None

		try:
			emails_data = self.client.domain_search(
				domain=domain, emails_type='personal', limit=2)
			#print('email: {} | csc: {}'.format(email, csc))
			emails = [e['value'] for e in emails_data['emails']]
			print("SCRAPED EMAILS:", emails)
		except Exception as e:
			print("ERROR: ", e)

		return emails

	def scrape_contact_emails_for_users(self, ids_to_parse):
		# meta-procedure:
		# todo: check if name is a valid name 
		# check Profile URL first if valid

		for uid in self.users_dict.keys():
			if uid not in ids_to_parse:
				continue

			prof_url = self.users_dict[uid]['profile_url']
			desc_urls = self.users_dict[uid]['description_urls']
			self.users_dict[uid]['checked_contact_domains'].append(prof_url)
			self.users_dict[uid]['checked_contact_domains'].extend(desc_urls)
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
				contact_emails = self.get_contact_email_from_domain(url)
				if contact_emails is not None:
					#results_dict[uid].extend(contact_emails)
					self.users_dict[uid]['valid_contact_emails'].extend(contact_emails)

			print('ID: {} -> Valid Contact Emails:'.format(uid), self.users_dict[uid]['valid_contact_emails'])
