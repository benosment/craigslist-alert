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
    def __init__(self, location):
        self.base_url = 'http://{}.craigslist.org'.format(location)

    def form_query(self, query, category):
        '''returns a URL for searching craigslist'''
        return '{}/search/{}?query={}'.format(self.base_url, category, '+'.join(query))

    def search(self, query, category='taa'):
        ''' Search for a given query on Craigslist.'''
        search_result = requests.get(self.form_query(query, category))
        posts = self.parse_search_results(search_result.content)
        # TODO -- maybye just make list of links? Can get title from next page
        for post in posts:
            # TODO -- check if in database first (URL is assumed to be unique)
            # if not self.is_duplicate(post)
            p = self.parse_post((post['link']))
        
    def parse_search_results(self, search_results):
        '''Parse the search results into a list of dictionaries representing the post'''
        soup = BeautifulSoup(search_results)
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

    def parse_post(self, url):
        '''Parse an individual post'''
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
        id = self.url_to_id(url)
        title = soup.title.text
        description = soup.find_all('meta', {'name':'description'})
        #import pdb; pdb.set_trace()
        return Post(id, title, description)

    def is_duplicate(self, link):
        '''Returns True if the post already exists within the database,
           Returns False otherwise'''
        return False

    def url_to_id(self, url):
        '''URL is of the form: http://raleigh.craigslist.org/tag/4554496580.html
        The last portion is assumed to be a unique id
        '''
        last_segment = url.split('/')[-1]
        id = last_segment.split('.')[0]
        return int(id)

class Post():
    '''Represents an individual Craigslist post'''
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description

        
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
    cl = Craigslist(args.location)
    cl.search(args.query, args.category)

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
    