#!/usr/bin/env python3
# coding=utf-8

import nose.tools as nose

import yvs.filter_refs as yvs
from tests import set_up, tear_down


@nose.with_setup(set_up, tear_down)
def test_basic():
    """should match verses"""
    results = yvs.get_result_list('luke 4:8')
    nose.assert_equal(results[0]['title'], 'Luke 4:8 (NIV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_ambiguous():
    """should match verses by ambiguous book reference"""
    results = yvs.get_result_list('a 3:2')
    nose.assert_equal(results[0]['title'], 'Amos 3:2 (NIV)')
    nose.assert_equal(results[1]['title'], 'Acts 3:2 (NIV)')
    nose.assert_equal(len(results), 2)


@nose.with_setup(set_up, tear_down)
def test_dot_separator():
    """should match verses preceded by dot"""
    results = yvs.get_result_list('luke 4.8')
    nose.assert_equal(results[0]['title'], 'Luke 4:8 (NIV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_space_separator():
    """should match verses preceded by space"""
    results = yvs.get_result_list('luke 4 8')
    nose.assert_equal(results[0]['title'], 'Luke 4:8 (NIV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_id():
    """should use correct ID for verses"""
    results = yvs.get_result_list('luke 4:8')
    nose.assert_equal(results[0]['uid'], 'yvs-111/luk.4.8')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_range():
    """should match verse ranges"""
    results = yvs.get_result_list('1 cor 13.4-7')
    nose.assert_equal(results[0]['title'], '1 Corinthians 13:4-7 (NIV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_range_id():
    """should use correct ID for verse ranges"""
    results = yvs.get_result_list('1 cor 13.4-7')
    nose.assert_equal(results[0]['uid'], 'yvs-111/1co.13.4-7')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_range_invalid():
    """should not match nonexistent ranges"""
    results = yvs.get_result_list('1 cor 13.4-3')
    nose.assert_equal(results[0]['title'], '1 Corinthians 13:4 (NIV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_zero_verse():
    """should interpret verse zero as verse one"""
    results = yvs.get_result_list('ps 23:0')
    nose.assert_equal(results[0]['title'], 'Psalms 23:1 (NIV)')
    nose.assert_equal(len(results), 1)
