#!/usr/bin/env python3
# coding=utf-8

import nose.tools as nose

import yvs.filter_refs as yvs
from tests import set_up, tear_down


@nose.with_setup(set_up, tear_down)
def test_basic():
    """should match chapters"""
    results = yvs.get_result_list('matthew 5')
    nose.assert_equal(results[0]['title'], 'Matthew 5 (NIV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_ambiguous():
    """should match chapters by ambiguous book name"""
    results = yvs.get_result_list('a 3')
    nose.assert_equal(results[0]['title'], 'Amos 3 (NIV)')
    nose.assert_equal(results[1]['title'], 'Acts 3 (NIV)')
    nose.assert_equal(len(results), 2)


@nose.with_setup(set_up, tear_down)
def test_id():
    """should use correct ID for chapters"""
    results = yvs.get_result_list('luke 4')
    nose.assert_equal(results[0]['uid'], 'yvs-111/luk.4')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_zero_chapter():
    """should interpret chapter zero as chapter one"""
    results = yvs.get_result_list('ps 0')
    nose.assert_equal(results[0]['title'], 'Psalms 1 (NIV)')
    nose.assert_equal(len(results), 1)
