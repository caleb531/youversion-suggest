#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import nose.tools as nose
import yv_suggest.filter_refs as yvs


def test_numbered():
    """should match versions ending in number by partial name"""
    results = yvs.get_result_list('lucas 4:8 rvr1', prefs={
        'language': 'es'
    })
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], 'Lucas 4:8 (RVR1960)')


def test_case():
    """should match versions irrespective of case"""
    query = 'e 4:8 esv'
    results = yvs.get_result_list(query, prefs={})
    results_lower = yvs.get_result_list(query.lower(), prefs={})
    results_upper = yvs.get_result_list(query.upper(), prefs={})
    nose.assert_equal(len(results), 6)
    nose.assert_list_equal(results_lower, results)
    nose.assert_list_equal(results_upper, results)


def test_whitespace():
    """should match versions irrespective of surrounding whitespace"""
    results = yvs.get_result_list('1 peter 5:7    esv', prefs={})
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], '1 Peter 5:7 (ESV)')


def test_partial():
    """should match versions by partial name"""
    results = yvs.get_result_list('luke 4:8 e', prefs={})
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], 'Luke 4:8 (ESV)')


def test_partial_ambiguous():
    """should match versions by ambiguous partial name"""
    results = yvs.get_result_list('luke 4:8 c', prefs={})
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], 'Luke 4:8 (CEB)')


def test_closest_match():
    """should try to find closest match for nonexistent versions"""
    results = yvs.get_result_list('hosea 6:3 nlab', prefs={})
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], 'Hosea 6:3 (NLT)')


def test_nonexistent():
    """should use default version for nonexistent versions with no matches"""
    results = yvs.get_result_list('hosea 6:3 xyz', prefs={})
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], 'Hosea 6:3 (NIV)')


def test_id():
    """should use correct ID for versions"""
    results = yvs.get_result_list('malachi 3:2 esv', prefs={})
    nose.assert_equal(results[0]['uid'], 'yvs-59/mal.3.2')