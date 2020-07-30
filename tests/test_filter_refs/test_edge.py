#!/usr/bin/env python3
# coding=utf-8

import nose.tools as nose

import yvs.filter_refs as yvs
from tests import set_up, tear_down
from tests.decorators import use_user_prefs


@nose.with_setup(set_up, tear_down)
def test_empty():
    """should not match empty input"""
    results = yvs.get_result_list('')
    nose.assert_equal(len(results), 0)


@nose.with_setup(set_up, tear_down)
def test_non_alphanumeric():
    """should not match entirely non-alphanumeric input"""
    results = yvs.get_result_list('!!!')
    nose.assert_equal(len(results), 0)


@nose.with_setup(set_up, tear_down)
def test_whitespace():
    """should ignore excessive whitespace"""
    results = yvs.get_result_list('  romans  8  28  nl  ')
    nose.assert_equal(results[0]['title'], 'Romans 8:28 (NLT)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_littered():
    """should ignore non-alphanumeric characters"""
    results = yvs.get_result_list('!1@co#13$4^7&es*')
    nose.assert_equal(results[0]['title'], '1 Corinthians 13:4-7 (ESV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_trailing_alphanumeric():
    """should ignore trailing non-matching alphanumeric characters"""
    results = yvs.get_result_list('2 co 3 x y z 1 2 3')
    nose.assert_equal(results[0]['title'], '2 Corinthians 3 (NIV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'spa', 'version': 128, 'copybydefault': False})
def test_unicode_accented():
    """should recognize accented Unicode characters"""
    results = yvs.get_result_list('é 3')
    nose.assert_equal(results[0]['title'], 'Éxodo 3 (NVI)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_unicode_normalization():
    """should normalize Unicode characters"""
    results = yvs.get_result_list('e\u0301')
    nose.assert_equal(len(results), 0)


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'deu', 'version': 51, 'copybydefault': False})
def test_numbered_puncuation():
    """should match numbered books even if book name contains punctuation """
    results = yvs.get_result_list('1 ch')
    nose.assert_equal(results[0]['title'], '1. Chronik 1 (DELUT)')
    nose.assert_equal(len(results), 1)
