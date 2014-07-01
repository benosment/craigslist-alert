#! /usr/bin/env python
#
# Ben Osment
# Tue Jul  1 08:03:06 EDT 2014

"""Unit tests for craigslist_aleart.py"""

import unittest
import sys
import os

current_dir = os.getcwd()
src_dir = os.path.join(current_dir, 'craigslist_alert')
tests_dir = os.path.join(current_dir, 'tests')

# add the source directory to the load path
sys.path.append(src_dir)

import craigslist_alert


"""
Pre-Test
 - store a sample HTML page, use mock to point to that object
 - store a slightly modified page

Tests
 - verify count of posts returned
 - verify headline of post
 - verify link of posts
 - verify non-local?
 - verify zero posts
 - verify 404 exception path
 - verify no results path
 - verify download link
 - verify content of downloaded link
 - verify entry into database
 - verify filtered entry into database
 - verify non-filtered entry into database
 - verify email with new posts
 - verify no email with no new posts
 - verify bold email for certain keywords
"""

class TestCraigslist(unittest.TestCase):

    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()

