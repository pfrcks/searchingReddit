import requests
from bs4 import BeautifulSoup
import time
import re
import os.path
import base64
from base64 import b16encode


_r_learnprogramming_url =re.compile(r'http://(www.)?reddit.com/r/learnprogramming')

def downloadRedditUrl(url):
  assert _r_learnprogramming_url.match(url)
  headers = {'User-Agent': 'searchingReddit bot version 0.1'}
  r = requests.get(url, headers=headers)
  if r.status_code != 200:
    raise Exception("Non-OK status code! {}".format(r.status_code))
  return r.text

def parseRedditPost(html):
  bs = BeautifulSoup(html)
  return bs.select("div.usertext-body")[1].text

def find_next_url(page):
  curs = page.find('rel="nofollow next" ')
  page = page[:curs-2]
  curs = page.rfind('href')
  page = page[curs+6:]
  if page.find('?amp'):
    s = page.find('?amp')
    p = page.find(';count')
    page = page[:s+1] + page[p+1:]
  return page
    

class Crawler(object):
  def __init__(self, start_url, storage_dir):
    self.start_url = start_url
    self.storage_dir = storage_dir

  @staticmethod
  def _make_absolute_url(url):
    return 'http://reddit.com'+url

  def crawl(self):
    current_page_url = self.start_url
    while True :
      current_page = downloadRedditUrl(current_page_url)
      bs=BeautifulSoup(current_page)
      all_posts_links = bs.findAll('a', attrs = {'class':'title'});
      post_links = [Crawler._make_absolute_url(link['href']) for link in all_posts_links]
      for post_link in post_links:
	html = downloadRedditUrl(post_link)
	stored_text_file_name = os.path.join(self.storage_dir, b16encode(post_link))
	stored_text_file = open(stored_text_file_name, "w")
	stored_text_file.write(html.encode('utf8'))
	time.sleep(2)
      next_page_url=find_next_url(current_page)
      current_page_url = next_page_url
      time.sleep(2)
      