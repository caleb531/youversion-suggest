#!/usr/bin/env python3
# coding=utf-8

from __future__ import unicode_literals

import nose.tools as nose

import yvs.filter_refs as yvs
from tests import set_up, tear_down


@nose.with_setup(set_up, tear_down)
def test_chapter_overflow():
    """should constrain specified chapter to last chapter if too high"""
    results = yvs.get_result_list('a 25:2')
    nose.assert_equal(results[0]['title'], 'Amos 9:2 (NIV)')
    nose.assert_equal(results[1]['title'], 'Acts 25:2 (NIV)')
    nose.assert_equal(len(results), 2)


@nose.with_setup(set_up, tear_down)
def test_verse_overflow():
    """should constrain specified verse to last verse if too high"""
    results = yvs.get_result_list('a 2:50')
    nose.assert_equal(results[0]['title'], 'Amos 2:16 (NIV)')
    nose.assert_equal(results[1]['title'], 'Acts 2:47 (NIV)')
    nose.assert_equal(len(results), 2)


@nose.with_setup(set_up, tear_down)
def test_endverse_overflow():
    """should constrain specified endverse to last endverse if too high"""
    results = yvs.get_result_list('a 2:4-51')
    nose.assert_equal(results[0]['title'], 'Amos 2:4-16 (NIV)')
    nose.assert_equal(results[1]['title'], 'Acts 2:4-47 (NIV)')
    nose.assert_equal(len(results), 2)


@nose.with_setup(set_up, tear_down)
def test_verse_and_endverse_overflow():
    """should revert to single verse if verse and endverse are too high"""
    results = yvs.get_result_list('ps 23.7-9')
    nose.assert_equal(results[0]['title'], 'Psalms 23:6 (NIV)')
    nose.assert_equal(len(results), 1)
