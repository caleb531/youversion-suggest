# tests.test_filter_refs_book

from __future__ import unicode_literals
import nose.tools as nose
import yvs.filter_refs as yvs
from tests import set_up, tear_down


@nose.with_setup(set_up, tear_down)
def test_partial():
    """should match books by partial name"""
    results = yvs.get_result_list('luk')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], 'Luke 1 (NIV)')


@nose.with_setup(set_up, tear_down)
def test_case():
    """should match books irrespective of case"""
    query_str = 'Matthew'
    results = yvs.get_result_list(query_str)
    results_lower = yvs.get_result_list(query_str.lower())
    results_upper = yvs.get_result_list(query_str.upper())
    nose.assert_equal(len(results), 1)
    nose.assert_list_equal(results_lower, results)
    nose.assert_list_equal(results_upper, results)


@nose.with_setup(set_up, tear_down)
def test_partial_ambiguous():
    """should match books by ambiguous partial name"""
    results = yvs.get_result_list('r')
    nose.assert_equal(len(results), 3)
    nose.assert_equal(results[0]['title'], 'Ruth 1 (NIV)')
    nose.assert_equal(results[1]['title'], 'Romans 1 (NIV)')
    nose.assert_equal(results[2]['title'], 'Revelation 1 (NIV)')


@nose.with_setup(set_up, tear_down)
def test_numbered_partial():
    """should match numbered books by partial numbered name"""
    results = yvs.get_result_list('1 cor')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], '1 Corinthians 1 (NIV)')


@nose.with_setup(set_up, tear_down)
def test_number_only():
    """should match single number query"""
    results = yvs.get_result_list('2')
    nose.assert_equal(len(results), 8)


@nose.with_setup(set_up, tear_down)
def test_nonnumbered_partial():
    """should match only non-numbered books by partial non-numbered name"""
    results = yvs.get_result_list('joh')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], 'John 1 (NIV)')


@nose.with_setup(set_up, tear_down)
def test_id():
    """should use correct ID for books"""
    results = yvs.get_result_list('philippians')
    nose.assert_equal(results[0]['uid'], 'yvs-111/php.1')


@nose.with_setup(set_up, tear_down)
def test_closest_match():
    """should try to find closest match for nonexistent books"""
    results = yvs.get_result_list('relevations')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['title'], 'Revelation 1 (NIV)')


@nose.with_setup(set_up, tear_down)
def test_nonexistent():
    """should not match nonexistent books"""
    results = yvs.get_result_list('xyz')
    nose.assert_equal(len(results), 0)
