import os
import requests
import sys
import yaml
from os.path import isfile, join, isdir

from selectorlib import Extractor
from lxml.html import fromstring


class Scraper:
    def __init__(self, url=None, file_input=None, selector_dirs=None, sanitize=True):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = []
        self.success_count = 0
        self.total = 0
        self.sanitize = sanitize
        self.selectors_dir = selector_dirs or os.path.join(self.base_dir, 'selectors')
        self.url = url
        self.file_input = file_input

        if self.url:
            self.extract(url)

        if self.file_input:
            with open(self.file_input,'r') as urllist:
                for url in urllist.read().splitlines():
                    self.extract(url)

        if self.sanitize:
            print(self.sanitize_results())
        print(self.results)

    @classmethod
    def scrape_url(cls, url):
        return cls(url=url)

    @classmethod
    def scrape_from_file(cls, file):
        return cls(file_input=file)

    def get_selectors(self):
        if not isdir(self.selectors_dir):
            sys.exit('selector_dirs is not a valid directory.')

        selectors = []
        for file in os.listdir(self.selectors_dir):
            if isfile(join(self.selectors_dir, file)):
                try:
                    file_path = os.path.join(self.selectors_dir, file)
                    config_dict = yaml.safe_load(file_path)
                    print(f"[VALID] {file_path}")
                    selectors.append(file_path)
                except:
                    print(f"[INVALID] {file_path}")

        if not selectors:
            sys.exit('Could not find selectors.')

        return selectors

    def get_proxies(self):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies = set()
        for i in parser.xpath('//tbody/tr')[:10]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies.add(proxy)
        return proxies

    def extract(self, url):
        headers = {
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.amazon.com/',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }

        try:
            res = requests.get(url, headers=headers, proxies=self.get_proxies())
            if not res.status_code == 200:
                return None
        except requests.ConnectionError as exception:
            print("Could not load URL")

        for selector in self.get_selectors():
            ext = Extractor.from_yaml_file(selector)
            self.results.append(ext.extract(res.text))

    def sanitize_results(self):
        # TODO: remove empty objects
        return self.results

value = input("Enter Url to scrape: ")
Scraper.scrape_url(value)

# TODO: enable file input
# value = input("Enter file path: ")
# Scraper.scrape_from_file(value)
