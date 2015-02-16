#!/usr/bin/env python

import nose.tools as nose
import yv_suggest.open as yvs
import inspect


class WebbrowserMock(object):
    """mock the builtin webbrowser module"""

    def open(self, url):
        """mock the webbrowser.open() function"""
        self.url = url


def test_url():
    """should build correct URL to Bible reference"""
    url = yvs.get_ref_url('esv/jhn.3.16')
    nose.assert_equal(url, 'https://www.bible.com/bible/esv/jhn.3.16')


def test_query_param():
    """should use received query parameter as default ref ID"""
    spec = inspect.getargspec(yvs.main)
    default_query_str = spec.defaults[0]
    nose.assert_equal(default_query_str, '{query}')


def test_url_open():
    """should attempt to open URL using webbrowser module"""
    mock = WebbrowserMock()
    yvs.webbrowser = mock
    yvs.main('nlt/jhn.3.17')
    nose.assert_equal(mock.url, 'https://www.bible.com/bible/nlt/jhn.3.17')
