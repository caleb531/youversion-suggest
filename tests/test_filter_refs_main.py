#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import nose.tools as nose
import yv_suggest.filter_refs as yvs
from xml.etree import ElementTree as ET
from context_managers import redirect_stdout
import inspect
import sys


def test_output():
    """should output ref result list XML"""
    query_str = 'genesis 50:20'
    with redirect_stdout() as out:
        yvs.main(query_str, prefs={})
        output = out.getvalue().strip()
        results = yvs.get_result_list(query_str, prefs={})
        xml = yvs.shared.get_result_list_xml(results).strip()
        nose.assert_equal(output, xml)


def test_null_result():
    """should output "No Results" XML item for empty ref result lists"""
    query_str = 'xyz'
    with redirect_stdout() as out:
        yvs.main(query_str, prefs={})
        xml = out.getvalue().strip()
        root = ET.fromstring(xml)
        item = root.find('item')
        nose.assert_is_not_none(item, '<item> element is missing')
        nose.assert_equal(item.get('valid'), 'no')
        title = item.find('title')
        nose.assert_equal(title.text, 'No Results')


def test_query_param():
    """should use typed Alfred query as default query string"""
    spec = inspect.getargspec(yvs.main)
    default_query_str = spec.defaults[0]
    nose.assert_equal(default_query_str, '{query}')


def test_source_only():
    """should run script assuming script is not a file"""
    yvs.shared.sys.argv[0] = yvs.shared.__file__
    del yvs.shared.__file__
    results = yvs.get_result_list('e', prefs={})
    nose.assert_equal(len(results), 6)
    yvs.shared.__file__ = yvs.shared.sys.argv[0]
