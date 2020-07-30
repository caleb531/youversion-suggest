#!/usr/bin/env python3
# coding=utf-8

import json

import nose.tools as nose

import yvs.filter_refs as yvs
from tests import set_up, tear_down
from tests.decorators import redirect_stdout


@nose.with_setup(set_up, tear_down)
@redirect_stdout
def test_output(out):
    """should output ref result list JSON"""
    query_str = 'genesis 50:20'
    yvs.main(query_str)
    output = out.getvalue().rstrip()
    results = yvs.get_result_list(query_str)
    feedback = yvs.core.get_result_list_feedback_str(results).rstrip()
    nose.assert_equal(output, feedback)


@nose.with_setup(set_up, tear_down)
@redirect_stdout
def test_null_result(out):
    """should output "No Results" JSON item for empty ref result list"""
    query_str = 'xyz'
    yvs.main(query_str)
    feedback_str = out.getvalue()
    feedback = json.loads(feedback_str)
    nose.assert_equal(len(feedback['items']), 1, 'result item is missing')
    item = feedback['items'][0]
    nose.assert_equal(item['title'], 'No Results')
    nose.assert_equal(item['valid'], False)
