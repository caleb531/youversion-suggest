#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function, unicode_literals

import nose.tools as nose
from mock import Mock, NonCallableMock, patch

import tests
from yvs.yv_parser import YVParser

with open('tests/html/psa.23.html') as html_file:
    patch_urlopen = patch(
        'urllib2.urlopen', return_value=NonCallableMock(
            read=Mock(return_value=html_file.read())))


def set_up():
    patch_urlopen.start()
    tests.set_up()


def tear_down():
    patch_urlopen.stop()
    tests.tear_down()


@nose.with_setup(set_up, tear_down)
@patch('yvs.yv_parser.YVParser.handle_data')
def test_charref_name(handle_data):
    """should evaluate named character references"""
    parser = YVParser()
    parser.feed('&deg;')
    handle_data.assert_called_once_with('°')


@nose.with_setup(set_up, tear_down)
@patch('yvs.yv_parser.YVParser.handle_data')
def test_charref_dec(handle_data):
    """should evaluate decimal character references"""
    parser = YVParser()
    parser.feed('&#176;')
    handle_data.assert_called_once_with('°')


@nose.with_setup(set_up, tear_down)
@patch('yvs.yv_parser.YVParser.handle_data')
def test_charref_hex(handle_data):
    """should evaluate hexadecimal character references"""
    parser = YVParser()
    parser.feed('&#x00b0;')
    handle_data.assert_called_once_with('°')
