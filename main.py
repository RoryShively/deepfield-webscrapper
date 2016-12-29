#!/usr/bin/env python

#
# Web scraping
# ASNs (Autonomous System Numbers) are one of the building blocks of the
# Internet. This project is to create a mapping from each ASN in use to the
# company that owns it. For example, ASN 36375 is used by the University of
# Michigan - http://bgp.he.net/AS36375
# 
# The site http://bgp.he.net/ has lots of useful information about ASNs. 
# Starting at http://bgp.he.net/report/world crawl and scrape the linked country
# reports to make a structure mapping each ASN to info about that ASN.
# Sample structure:
#   {3320: {'Country': 'DE',
#     'Name': 'Deutsche Telekom AG',
#     'Routes v4': 13547,
#     'Routes v6': 268},
#    36375: {'Country': 'US',
#     'Name': 'University of Michigan',
#     'Routes v4': 14,
#     'Routes v6': 1}}
#
# When done, output the collected data to a json file.
#
# Use any python libraries. One suggestion, a good one for scraping is
# BeautifulSoup:
# http://www.crummy.com/software/BeautifulSoup/bs4/doc/
#
import os
import urllib2
from collections import deque

import bs4
import time

BASE_URL = 'http://bgp.he.net'


# To help get you started, here is a function to fetch and parse a page.
# Given url, return soup.
def url_to_soup(url):
    # bgp.he.net filters based on user-agent.
    req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib2.urlopen(req).read()
    soup = bs4.BeautifulSoup(html, 'html.parser')
    return soup


def parse_country_urls(soup):
    url_deque = deque()
    tbody = soup.find(id='table_countries').tbody

    for anchor in tbody.findAll('a'):
        a = anchor
        url_deque.append(BASE_URL + a.attrs['href'])

    return url_deque


def get_country_urls():
    url = BASE_URL + '/report/world'
    soup = url_to_soup(url)
    country_urls = parse_country_urls(soup)

    return country_urls


def distribute_compute(urls):
    while len(urls) > 0:
        url = urls.popleft()
        country = url.split('/')[-1]

        print "Downloading {}...".format(url)
        soup = url_to_soup(url)
        scrape(soup, country)


def scrape(soup, country):
    try:
        tbody = soup.find(id='asns').tbody

    except AttributeError:
        pass

    else:
        for tr in tbody.findAll('tr'):
            write_to_file(tr, country)


def write_to_file(tr, country):
    tds = tr.findAll('td')

    with open_file() as f:
        f.write(((u'  %s: {\n'
                  u'    "County": "%s",\n'
                  u'    "Name": "%s",\n'
                  u'    "Routes v4": %s,\n'
                  u'    "Routes v6": %s\n'
                  u'  },\n') % (
                     tds[0].text[2:],
                     country,
                     tds[1].text,
                     tds[3].text,
                     tds[5].text)).encode('ascii', 'ignore'))


def open_file():
    file = open('data.json', mode='a')
    return file


def initialize_file():
    with open('data.json', mode='w') as f:
        f.write('{\n')


def close_file():
    with open('data.json', 'rb+') as f:
        f.seek(-2, os.SEEK_END)
        f.truncate()

    with open('data.json', mode='a') as f:
        f.write('\n}\n')


if __name__ == '__main__':

    start_time = time.time()
    print 'Starting...'

    initialize_file()

    urls = get_country_urls()
    distribute_compute(urls)

    close_file()
    print 'Finished in {} seconds'.format(round(time.time() - start_time, 3))
