#!/usr/bin/env python

import nose.tools as nose
import yv_suggest.search as yvs


def test_book():
    """should recognize shorthand book syntax"""
    results = yvs.get_result_list('1c')
    nose.assert_equal(len(results), 2)
    nose.assert_equal(results[0]['title'], '1 Chronicles')
    nose.assert_equal(results[1]['title'], '1 Corinthians')


def test_chapter():
    """should recognize shorthand chapter syntax"""
    results = yvs.get_result_list('1co13')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], '1 Corinthians 13')


def test_version():
    """should recognize shorthand version syntax"""
    results = yvs.get_result_list('1co13esv')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], '1 Corinthians 13')
    nose.assert_equal(results[0]['subtitle'], 'ESV')
