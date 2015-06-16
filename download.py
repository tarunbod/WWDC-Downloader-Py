#!/usr/bin/env python3

import sys, os, os.path
import urllib.request
import json
import re

class WWDCDownloader(object):

	WWDC_LIBRARIES = [{
						'base': 'https://developer.apple.com/library/prerelease/ios',
						'lib': '/navigation/library.json'
					  },
                      {
                      	'base': 'https://developer.apple.com/library/prerelease/mac',
                      	'lib': '/navigation/library.json'
                      }]

	def __init__(self, dl_dir):
		self.dl_dir = dl_dir
		self.downloaded_files = []

	def mkdir(self, dir_name):
		if os.path.exists(dir_name):
			return False
		else:
			os.mkdir(dir_name)
			return True

	def read_url(self, url):
		print('URL: ' + url)
		request = urllib.request.urlopen(url)
		if request.getcode() == 200:
			return request.read()
	
	def download_sample_code_from_book_json(self, book_json_url, code_base_url, dest_dir, duplicates_ok):
		did_download = False
		response = self.read_url(book_json_url).decode('utf-8')
		if response:
			if response[0] == '<':
				print("Sorry, this sample code is available yet: %s/book.json" % code_base_url)
			else:
				book_res = json.loads(response)
				filename = book_res['sampleCode']
				url = '%s/%s' % (code_base_url, filename)
				did_download = self.download_file(url, filename, dest_dir, duplicates_ok)

		return did_download

	def download_file(self, url, filename, dest_dir, duplicates_ok = True):
		did_download = False
		if duplicates_ok or (url not in self.downloaded_files):
			self.downloaded_files.append(url)
			print("Downloading %s" % url)
			try:
				downloaded_file = self.read_url(url)
				with open(dest_dir + '/' + filename, 'wb') as dest_file:
					dest_file.write(downloaded_file)
				did_download = True
			except Exception as e:
				print("\n\nError:%s\n\n" % e)
		elif not duplicates_ok:
			print("File already downloaded, skipping.")
		return did_download

	def load(self):
		self.mkdir(self.dl_dir)

		print("\nScraping the WWDC libraries...")
		for lib_hash in self.WWDC_LIBRARIES:
			lib = '%s%s' % (lib_hash['base'], lib_hash['lib'])
			body = self.read_url(lib).decode('utf-8')
			# print('BODY:', body)
			body = body.replace("''", '""')
			res = json.loads(body)

			docs = res['documents']

			if len(docs) > 0:
				for doc in docs:
					if doc[2] == 5:
						title = doc[0]
						print("Sample code '%s'" % title)

						dirname = '%s/%s' % (self.dl_dir, re.sub('\/|&|!|:', '', title))
						print('Creating %s' % dirname)
						did_create_dir = self.mkdir(dirname)

						segments = doc[9].split('/')
						url = '%s/samplecode/%s/book.json' % (lib_hash['base'], segments[2])

						print(url)
						did_download = self.download_sample_code_from_book_json(url, '%s/samplecode/%s' % (lib_hash['base'], segments[2]), dirname, False)
						if not did_download and did_create_dir:
							os.rmdir(dirname)
			else:
				print("No code samples :(")
		print("Done.")


w = WWDCDownloader('wwdc2015-assets')
w.load()
