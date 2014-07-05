#! /usr/bin/env python3
#
# Ben Osment
# Tue Jul  1 08:03:06 EDT 2014

"""Unit tests for craigslist_aleart.py"""

import unittest
from unittest.mock import patch, Mock
import sys
import os

current_dir = os.getcwd()
src_dir = os.path.join(current_dir, 'craigslist-alert')
tests_dir = os.path.join(current_dir, 'tests')

# add the source directory to the load path
sys.path.append(src_dir)

from craigslist_alert import Craigslist


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

with open(os.path.join(tests_dir, 'sample-query.html'), 'rb') as f:
    good_response = f.read()
    
with open(os.path.join(tests_dir, 'no-results.html'), 'rb') as f:
    no_results_response = f.read()

good_mock = Mock()
good_mock.content = good_response

bad_mock = Mock()
bad_mock.content = no_results_response

class TestQuery(unittest.TestCase):
    def setUp(self):
        cl = Craigslist(location='raleigh')
        
    def test_basic_query(self):
        ''' Verify query formation with a single word'''
        self.assertEquals(cl.form_query('lego', category='taa'),
                          'http://raleigh.craigslist.org/search/taa?query=lego')
    
    def test_advanced_query(self):
        ''' Verify query formation with more than one word'''
        self.assertEquals(cl.form_query('lego 10225', category='taa'),
                          'http://raleigh.craigslist.org/search/taa?query=lego+10225')

    
class TestSearch(unittest.TestCase):
    
    @patch('requests.get', return_value=good_mock)
    def setUp(self, mock_requests_get):
        cl = Craigslist(location='raleigh')
        self.posts = cl.search('')

    def test_post_count(self):
        ''' Verify count of posts returned'''
        self.assertEqual(len(self.posts), 86)

    def test_post_headline(self):
        ''' Verify post headline'''
        self.assertEqual(self.posts[0]['title'], 'Buy, Sell, Trade & RENT Lego!')

    def test_post_link(self):
        ''' Verify post link'''
        self.assertEqual(self.posts[0]['link'],
                         'http://raleigh.craigslist.org/tad/4515121161.html')

    def test_advanced_query(self):
        ''' verify query formation with more than one word'''
        pass

class TestSearchNegative(unittest.TestCase):

    @patch('requests.get', return_value=bad_mock)
    def setUp(self, mock_requests_get):
        cl = Craigslist(location='raleigh')
        self.posts = cl.search('')

    def test_post_count(self):
        ''' Verify no posts returned'''
        self.assertEqual(len(self.posts), 0)


class TestPost(unittest.TestCase):
    '''Verify content of post'''
    pass
    
class TestAdd(unittest.TestCase):
    '''Verify post gets added to DB'''
    pass
    
if __name__ == '__main__':
    unittest.main()

