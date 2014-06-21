#! /usr/bin/env python3
#
# Ben Osment
# Sat Jun 21 09:15:05 2014

"""Craigslit Alert
   Scraps Craigslist and alerts if any new posts (matching a set of critera) have
   been posted
"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint

# base URL for Raleigh, NC
BASE_URL = 'http://raleigh.craigslist.org'

# category -- toys and games
CATEGORY = 'taa'

# what to search for
QUERY = 'lego'

# Should form something like the following:
#   http://raleigh.craigslist.org/search/taa?query=lego
FULL_URL = BASE_URL + '/search/' + CATEGORY + '?query=' + QUERY


def search_craigslist(url):
    """ Search for a given query on Craigslist.
        Returns a list of dictionaries representing the posts"""
    # get the raw HTML page
    response = requests.get(url)
    # parse the HTML
    soup = BeautifulSoup(response.content)
    ps = soup.find_all('p', {'class':'row'})
    posts = []
    for p in ps:
        links = p.find_all('a')
        for link in links:
            if not link.has_attr('class'):
                post = {}
                post['link'] = BASE_URL + link.get('href')
                post['title'] = link.get_text()
                # filter out any non-local posts
                # local posts will have a relative URL like:
                #   '/tag/4460564352.html'
                # but 'nearby' posts will have a full URL like:
                #   'http://greensboro.craigslist.org/tag/4519759135.html'
                if 'http' not in link.get('href'):
                    posts.append(post)
                # TODO - For each post, check if it is in the database, if not, add to send-list
                # TODO -- filter pattern? 
                    
    pprint(posts)
    return posts

if __name__ == '__main__':
    # Outline:
    #  - Search for the query (should be a separate function)
    posts_dict = search_craigslist(FULL_URL)
    #  - For each post, check if it is in the database, if not, add to send-list
    #  - Scrape the posts into a dict (should be a separate (this?) function)
    #  - if headline or body matches a key word, perhaps bold the entry? or send
    #    right away
    #  - if send list is non-zero, send an email
    