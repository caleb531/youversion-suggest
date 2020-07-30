#!/usr/bin/env python3
# coding=utf-8

import nose.tools as nose

import yvs.filter_refs as yvs
from tests import set_up, tear_down
from tests.decorators import use_user_prefs


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'spa', 'version': 128, 'copybydefault': False})
def test_numbered():
    """should match versions ending in number by partial name"""
    results = yvs.get_result_list('lucas 4:8 rvr1')
    nose.assert_equal(results[0]['title'], 'Lucas 4:8 (RVR1960)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'zho_tw', 'version': 46, 'copybydefault': False})
def test_non_ascii():
    """should match versions containing non-ASCII characters"""
    results = yvs.get_result_list('路加 4:8 cunp-上')
    nose.assert_equal(results[0]['title'], '路加福音 4:8 (CUNP-上帝)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_case():
    """should match versions irrespective of case"""
    query = 'e 4:8 esv'
    results = yvs.get_result_list(query)
    results_lower = yvs.get_result_list(query.lower())
    results_upper = yvs.get_result_list(query.upper())
    nose.assert_list_equal(results_lower, results)
    nose.assert_list_equal(results_upper, results)
    nose.assert_equal(len(results), 6)


@nose.with_setup(set_up, tear_down)
def test_whitespace():
    """should match versions irrespective of surrounding whitespace"""
    results = yvs.get_result_list('1 peter 5:7    esv')
    nose.assert_equal(results[0]['title'], '1 Peter 5:7 (ESV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_partial():
    """should match versions by partial name"""
    results = yvs.get_result_list('luke 4:8 es')
    nose.assert_equal(results[0]['title'], 'Luke 4:8 (ESV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_partial_ambiguous():
    """should match versions by ambiguous partial name"""
    results = yvs.get_result_list('luke 4:8 c')
    nose.assert_equal(results[0]['title'], 'Luke 4:8 (CEB)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_closest_match():
    """should try to find closest match for nonexistent versions"""
    results = yvs.get_result_list('hosea 6:3 nlab')
    nose.assert_equal(results[0]['title'], 'Hosea 6:3 (NLT)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_nonexistent():
    """should use default version for nonexistent versions with no matches"""
    results = yvs.get_result_list('hosea 6:3 xyz')
    nose.assert_equal(results[0]['title'], 'Hosea 6:3 (NIV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_id():
    """should use correct ID for versions"""
    results = yvs.get_result_list('malachi 3:2 esv')
    nose.assert_equal(results[0]['uid'], 'yvs-59/mal.3.2')
    nose.assert_equal(len(results), 1)
