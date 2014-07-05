#! /usr/bin/env python3
#
# Ben Osment
# Sat Jun 21 09:15:05 2014

"""
   Craigslist Alert
   Scraps Craigslist and alerts if any new posts (matching a set of critera) have
   been posted
"""

import requests
from bs4 import BeautifulSoup
import argparse


class Craigslist():
    def __init__(self, location='raleigh'):
        self.base_url = 'http://{}.craigslist.org'.format(location)

    def form_query(self, query, category):
        '''returns a URL for searching craigslist'''
        return self.base_url + '/search/' + category + '?query=' + '+'.join(query)

    def search(self, query, category='taa'):
        ''' Search for a given query on Craigslist.
        Returns a list of dictionaries representing the posts'''
        url = self.form_query(query, category)
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
                    post['link'] = self.base_url + link.get('href')
                    post['title'] = link.get_text()
                    # filter out any non-local posts
                    # local posts will have a relative URL like:
                    #   '/tag/4460564352.html'
                    # but 'nearby' posts will have a full URL like:
                    #   'http://greensboro.craigslist.org/tag/4519759135.html'
                    if 'http' not in link.get('href'):
                        posts.append(post)
        return posts

    

def parse_args():
    '''Builds parser and parses the CLI options'''
    parser = argparse.ArgumentParser(description='Scraps Craigslist and alerts if any' \
                                     ' new posts (matching a set of critera) have been posted')
    parser.add_argument('query', action='store', nargs='+',
                        help='search value')
    parser.add_argument('--location', help='what local Craigslist to search?',
                        action='store', required=False, default='raleigh')
    parser.add_argument('--category', help='what category to search?',
                        action='store', required=False, default='taa')
    parser.add_argument('--db', help='which database to use?',
                        action='store', required=False, default='results.db')
    return parser.parse_args()


def craigslist_alert(args):
    print(args)
    #cl = Craigslist(**args)

if __name__ == '__main__':
    args = parse_args()
    craigslist_alert(args)
    # Outline:
    #  - Search for the query (should be a separate function)
    #posts = search_craigslist(FULL_URL)
    #  - For each post, check if it is in the database, if not, add to send-list
    
    #  - Scrape the posts into a dict (should be a separate (this?) function)
    #  - if headline or body matches a key word, perhaps bold the entry? or send
    #    right away
    #  - if send list is non-zero, send an email
    