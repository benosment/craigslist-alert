#! /usr/bin/env python3
#
# Ben Osment
# Tue Jul  1 08:03:06 EDT 2014

"""Unit tests for craigslist_aleart.py"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
import sqlalchemy

current_dir = os.getcwd()
src_dir = os.path.join(current_dir, 'craigslist-alert')
tests_dir = os.path.join(current_dir, 'tests')

# add the source directory to the load path
sys.path.append(src_dir)

from craigslist_alert import Craigslist, Post


"""
Pre-Test
 - store a sample HTML page, use mock to point to that object
 - store a slightly modified page

Tests
 - verify 404 exception path
 - verify download link
 - verify content of downloaded link
 - verify entry into database
 - verify filtered entry into database
 - verify non-filtered entry into database
 - verify email with new posts
 - verify no email with no new posts
 - verify bold email for certain keywords
"""

class TestQuery(unittest.TestCase):
    def setUp(self):
        self.cl = Craigslist(location='raleigh')
        
    def test_basic_query(self):
        ''' Verify query formation with a single word'''
        self.assertEqual(self.cl.form_query(['lego'], category='taa'),
                          'http://raleigh.craigslist.org/search/taa?query=lego')
    
    def test_advanced_query(self):
        ''' Verify query formation with more than one word'''
        self.assertEqual(self.cl.form_query(['lego', '10225'], category='taa'),
                          'http://raleigh.craigslist.org/search/taa?query=lego+10225')

    
class TestSearchResults(unittest.TestCase):
    
    def setUp(self):
        with open(os.path.join(tests_dir,
                               'sample-query-results.html'), 'rb') as f:
            sample_results = f.read()
        cl = Craigslist(location='raleigh')
        self.posts = cl.parse_search_results(sample_results)

    def test_post_count(self):
        ''' Verify count of posts returned'''
        self.assertEqual(len(self.posts), 86)

    def test_post_link(self):
        ''' Verify post link'''
        self.assertEqual(self.posts[0],
                         'http://raleigh.craigslist.org/tad/4515121161.html')


class TestSearchResultsNegative(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(tests_dir,
                               'sample-no-results.html'), 'rb') as f:
            no_results = f.read()
        cl = Craigslist(location='raleigh')
        self.posts = cl.parse_search_results(no_results)

    def test_post_count(self):
        ''' Verify no posts returned'''
        self.assertEqual(len(self.posts), 0)


class TestPost(unittest.TestCase):

    with open(os.path.join(tests_dir,
                           'sample-post.html'), 'rb') as f:
        sample_post = f.read()

    page_mock = Mock()
    page_mock.content = sample_post

    @patch('requests.get', return_value=page_mock)
    def setUp(self, page_mock):
        cl = Craigslist(location='raleigh')
        self.post = cl.parse_post('http://raleigh.craigslist.org/tag/4510309330.html')

    def test_post_id(self):
        '''Verify post's ID'''
        self.assertEqual(self.post.id, '4510309330')

    def test_post_title(self):
        '''Verify post's title'''
        self.assertEqual(self.post.title, "LEGO Quatro Megablocks ")

    def test_post_description(self):        
        self.assertEqual(self.post.description,
                         'Box of LEGO Quatro Megablocks. Great for all ages, keeps children quiet and busy for a long time. ')
    
class TestAdd(unittest.TestCase):

    def setUp(self):
        # create a sample file with an entry
        with open('test-history', 'w') as f:
            f.write('4510309329\n')
        self.cl = Craigslist(location='raleigh', history='test-history')
        self.posts = [Post('4510309329', 'Lego Star Wars', '', ''),
                      Post('4510309330', 'Lego R2-D2', '', ''),
                      Post('4510309331', 'Megablocks for sell', '', '')]

    def test_filter_old(self):
        '''Verify old posts are filtered out'''
        new_posts = self.posts[1:] # don't include first item
        self.assertEqual(self.cl.filter_old(self.posts), new_posts)

    def test_filter_blacklist(self):
        '''Verify a post that contains certain words is filtered out'''
        filtered_posts = self.posts[:-1] # don't include last item
        self.assertEqual(self.cl.filter_blacklist(self.posts), filtered_posts)

    def test_history(self):
        '''Verify non-blacklist items are written to history file'''
        self.cl.save_history(self.cl.filter_blacklist(self.posts))
        with open(self.cl.history_filename) as f:
            content = []
            for line in f.readlines():
                content.append(line.strip())
        self.assertEqual(content, ['4510309329', '4510309330'])
    
    
if __name__ == '__main__':
    unittest.main()

