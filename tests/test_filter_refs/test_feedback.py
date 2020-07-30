#!/usr/bin/env python3
# coding=utf-8

import json

import nose.tools as nose

import yvs.filter_refs as yvs
from tests import set_up, tear_down


@nose.with_setup(set_up, tear_down)
def test_validity():
    """should return syntactically-valid JSON"""
    results = yvs.get_result_list('john 3:16')
    feedback_str = yvs.core.get_result_list_feedback_str(results)
    nose.assert_is_instance(json.loads(feedback_str), dict)


@nose.with_setup(set_up, tear_down)
def test_structure():
    """JSON should match result list"""
    results = yvs.get_result_list('matthew 6:34')
    result = results[0]
    feedback_str = yvs.core.get_result_list_feedback_str(results)
    feedback = json.loads(feedback_str)
    nose.assert_in('items', feedback, 'feedback object must have result items')
    item = feedback['items'][0]
    nose.assert_equal(item['uid'], result['uid'])
    nose.assert_equal(item['arg'], result['arg'])
    nose.assert_equal(
        item['quicklookurl'], 'https://www.bible.com/bible/111/MAT.6.34')
    nose.assert_equal(item['title'], 'Matthew 6:34 (NIV)')
    nose.assert_equal(item['text']['copy'], result['title'])
    nose.assert_equal(item['text']['largetype'], result['title'])
    nose.assert_equal(item['subtitle'], result['subtitle'])
    nose.assert_equal(item['icon']['path'], 'icon.png')
