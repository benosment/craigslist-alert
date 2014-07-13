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
import re
from bs4 import BeautifulSoup
import argparse
import smtplib
import os

class Craigslist():
    def __init__(self, location, history='history', blacklist='blacklist'):
        self.base_url = 'http://{}.craigslist.org'.format(location)
        self.history_filename = history
        self.history = []
        self.blacklist = []        
        try:
            with open(history, 'r') as f:
                for line in f.readlines():
                    self.history.append(line.strip())
        except FileNotFoundError:
            # may occur the first time the program is being run
            pass
        try:                
            with open(blacklist, 'r') as f:
                for line in f.readlines():
                    self.blacklist.append(line.strip())
        except FileNotFoundError:
            pass
            
    def form_query(self, query, category):
        '''returns a URL for searching craigslist'''
        return '{}/search/{}?query={}'.format(self.base_url, category, '+'.join(query))

    def search(self, query, category='taa'):
        ''' Search for a given query on Craigslist.'''
        search_result = requests.get(self.form_query(query, category))
        links = self.parse_search_results(search_result.content)
        posts = []
        for link in links:
            posts.append(self.parse_post(link))
        # Posts will contain all the posts.
        # We want to filter out any posts that have words in the blacklist first.
        posts = self.filter_blacklist(posts)
        # Then we check if any are new (by comparing the history from the last run)
        new_posts = self.filter_old(posts)
        # If any are new, we want to send an email with all the new posts
        if new_posts:
            self.send_email(new_posts)
        # Regardless, write all of the filtered posts to the history file for next time
        self.save_history(posts)
            
    def parse_search_results(self, search_results):
        '''Parse the search results into a list of links'''
        soup = BeautifulSoup(search_results)
        ps = soup.find_all('p', {'class':'row'})
        links = []
        for p in ps:
            _as = p.find_all('a')
            for a in _as:
                if not a.has_attr('class'):
                    # filter out any non-local posts
                    # local posts will have a relative URL like:
                    #   '/tag/4460564352.html'
                    # but 'nearby' posts will have a full URL like:
                    #   'http://greensboro.craigslist.org/tag/4519759135.html'
                    if 'http' not in a.get('href'):
                        links.append(self.base_url + a.get('href'))
        return links

    def parse_post(self, url):
        '''Parse an individual post'''
        page = requests.get(url)
        soup = BeautifulSoup(page.content)
        id = self.url_to_id(url)
        title = soup.title.text
        description = self.extract_description(soup.find_all('meta', {'name':'description'}))
        return Post(id, title, description, url)

    def filter_blacklist(self, posts):
        filtered_posts = []
        for post in posts:
            for item in self.blacklist:
                if item in post.title.lower():
                    break
            else:
                filtered_posts.append(post)
        return filtered_posts

    def filter_old(self, posts):
        filtered_posts = []
        for post in posts:
            if not post.id in self.history:
                filtered_posts.append(post)
        return filtered_posts

    def send_email(self, posts):
        body = ""
        for p in posts:
            body += "%s\n%s\n%s\n\n" % (p.title, p.description, p.link)
        gmail_user = os.environ.get('MAIL_USERNAME')
        gmail_password = os.environ.get('MAIL_PASSWORD')
        subject = 'Craigslist Alert'
        message = 'From: %s\nTo: %s\nSubject: %s\n\n%s' % (gmail_user, gmail_user, subject, body)
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, gmail_user, message)
            server.close()
        except:
            print("Failed to send mail")

    def save_history(self, posts):
        with open(self.history_filename, 'w') as f:
            for p in posts:
                f.write('%s\n' % p.id)

    def url_to_id(self, url):
        '''URL is of the form: http://raleigh.craigslist.org/tag/4554496580.html
        The last portion is assumed to be a unique id
        '''
        # split to the last segment of the URL
        last_segment = url.split('/')[-1]
        # remove the trailing .html
        id = last_segment.split('.')[0]
        return id

    def extract_description(self, meta_tag):
        '''BS4 returns a value like:
            <meta content="Box of LEGO Quatro Megablocks. Great for all ages, keeps children quiet and busy for a long time. " name="description"/>

        Return just the value in the content section
        '''
        pattern = re.compile(r'.*content=\"(?P<desc>.*)\" ')
        match = re.match(pattern, str(meta_tag))
        return match.group('desc')


class Post():
    '''Represents an individual Craigslist post'''
    def __init__(self, id, title, description, link):
        self.id = id
        self.title = title
        self.description = description
        self.link = link
        
    def __repr__(self):
        return 'Post %s: %s' % (self.id, self.title)


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
    