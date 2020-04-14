### STDLIB IMPORTS
import concurrent.futures
from constants import DEFAULT_WORKER_N

TIMEOUT_LEN = 20

class RedirectURLResolver:
	def __init__(self):
		pass

	def __call__(self, urls_data):
		return get_redirect_urls(urls_data)

	def __get_redirect_url(self, url_data):
		uid, url = url_data
		redirect_url = None

		if url is not None:
			redirect_url = requests.get(url, 
				timeout=TIMEOUT_LEN).url

		print('For ID: {} URL retrieved: {}'.format(
			uid, redirect_url))

		return uid, redirect_url

	def get_redirect_urls(data, workers=DEFAULT_WORKER_N):
		urls_data = []

		# verify emails conncurrently
		with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
		    future_to_smtp = {executor.submit(self.__get_redirect_url, d): d for d in data}

		    for future in concurrent.futures.as_completed(future_to_smtp):
		        try:
		            data = future.result()
		            urls_data.append(data)
		        except Exception as exc:
		        	# todo: add loggers here
		           	pass

		return (d for d in urls_data)
		