#!/usr/bin/env python3
# coding=utf-8

import json

import nose.tools as nose
from unittest.mock import Mock, NonCallableMock, patch

import tests
import yvs.search_refs as yvs
from tests.decorators import redirect_stdout, use_user_prefs

with open('tests/html/search.html') as html_file:
    patch_urlopen = patch(
        'urllib.request.urlopen', return_value=NonCallableMock(
            read=Mock(return_value=html_file.read())))


def set_up():
    patch_urlopen.start()
    tests.set_up()


def tear_down():
    patch_urlopen.stop()
    tests.tear_down()


@nose.with_setup(set_up, tear_down)
def test_result_titles():
    """should correctly parse result titles from HTML"""
    results = yvs.get_result_list('love others')
    nose.assert_regexp_matches(results[0]['title'], r'^Romans 13:8 \(NIV\)')
    nose.assert_regexp_matches(results[1]['title'], r'^John 15:12 \(NIV\)')
    nose.assert_regexp_matches(results[2]['title'], r'^1 Peter 4:8 \(NIV\)')
    nose.assert_equal(len(results), 3)


@nose.with_setup(set_up, tear_down)
def test_result_subtitles():
    """should correctly parse result subtitles from HTML"""
    results = yvs.get_result_list('love others')
    nose.assert_regexp_matches(results[0]['subtitle'], 'Lorem')
    nose.assert_regexp_matches(results[1]['subtitle'], 'consectetur')
    nose.assert_regexp_matches(results[2]['subtitle'], 'Ut aliquam')
    nose.assert_equal(len(results), 3)


@nose.with_setup(set_up, tear_down)
def test_result_arg():
    """should correctly parse result UID arguments from HTML"""
    results = yvs.get_result_list('love others')
    nose.assert_equal(results[0]['arg'], '111/rom.13.8')
    nose.assert_equal(results[1]['arg'], '111/jhn.15.12')
    nose.assert_equal(results[2]['arg'], '111/1pe.4.8')
    nose.assert_equal(len(results), 3)


@nose.with_setup(set_up, tear_down)
@patch('yvs.web.get_url_content', return_value='abc')
def test_unicode_input(get_url_content):
    """should correctly handle non-ASCII characters in query string"""
    yvs.get_result_list('é')
    get_url_content.assert_called_once_with(
        'https://www.bible.com/search/bible?q=%C3%A9&version_id=111')


@nose.with_setup(set_up, tear_down)
def test_cache_url_content():
    """should cache search URL content after first fetch"""
    yvs.get_result_list('love others')
    with patch('urllib.request.Request') as request:
        yvs.get_result_list('love others')
        request.assert_not_called()


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'eng', 'version': 111, 'copybydefault': False})
def test_copy_by_default_false():
    """should export correct data when "Copy By Default?" setting is false"""
    results = yvs.get_result_list('love others')
    nose.assert_equal(results[0]['variables']['copybydefault'], 'False')
    nose.assert_equal(
        results[0]['subtitle'], '» “Lorem ipsum” dolor sit amet,')
    nose.assert_equal(
        results[0]['mods']['cmd']['subtitle'], 'Copy content to clipboard')


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'eng', 'version': 111, 'copybydefault': True})
def test_copy_by_default_true():
    """should export correct data when "Copy By Default?" setting is true"""
    results = yvs.get_result_list('love others')
    nose.assert_equal(results[0]['variables']['copybydefault'], 'True')
    nose.assert_equal(
        results[0]['subtitle'], '» “Lorem ipsum” dolor sit amet,')
    nose.assert_equal(
        results[0]['mods']['cmd']['subtitle'], 'View on YouVersion')


@nose.with_setup(set_up, tear_down)
def test_structure():
    """JSON should match result list"""
    results = yvs.get_result_list('love others')
    result = results[0]
    feedback_str = yvs.core.get_result_list_feedback_str(results)
    feedback = json.loads(feedback_str)
    nose.assert_in('items', feedback, 'feedback object must have result items')
    item = feedback['items'][0]
    nose.assert_not_in('uid', item)
    nose.assert_equal(item['arg'], result['arg'])
    nose.assert_equal(
        item['quicklookurl'], 'https://www.bible.com/bible/111/ROM.13.8')
    nose.assert_equal(item['title'], 'Romans 13:8 (NIV) ♥')
    nose.assert_equal(item['text']['copy'], result['title'])
    nose.assert_equal(item['text']['largetype'], result['title'])
    nose.assert_equal(item['subtitle'], result['subtitle'])
    nose.assert_equal(item['icon']['path'], 'icon.png')


@nose.with_setup(set_up, tear_down)
@redirect_stdout
def test_output(out):
    """should output result list JSON"""
    query_str = 'love others'
    yvs.main(query_str)
    output = out.getvalue().rstrip()
    results = yvs.get_result_list(query_str)
    feedback = yvs.core.get_result_list_feedback_str(results).rstrip()
    nose.assert_equal(output, feedback)


@nose.with_setup(set_up, tear_down)
@redirect_stdout
@patch('yvs.search_refs.get_result_list', return_value=[])
def test_null_result(out, get_result_list):
    """should output "No Results" JSON item for empty result list"""
    query_str = 'xyz'
    yvs.main(query_str)
    feedback_str = out.getvalue()
    feedback = json.loads(feedback_str)
    nose.assert_equal(len(feedback['items']), 1, 'result item is missing')
    item = feedback['items'][0]
    nose.assert_equal(item['valid'], False)
    nose.assert_equal(item['title'], 'No Results')
