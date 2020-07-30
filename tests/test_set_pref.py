#!/usr/bin/env python3
# coding=utf-8

import json
import os
import os.path

import nose.tools as nose

import yvs.set_pref as yvs
from tests import set_up, tear_down
from tests.decorators import redirect_stdout


@nose.with_setup(set_up, tear_down)
def test_set_language():
    """should set preferred language"""
    yvs.set_pref('language', 'spa')
    user_prefs = yvs.core.get_user_prefs()
    nose.assert_equal(user_prefs['language'], 'spa')
    bible = yvs.core.get_bible(user_prefs['language'])
    nose.assert_equal(user_prefs['version'], bible['default_version'])


@nose.with_setup(set_up, tear_down)
def test_set_version():
    """should set preferred version"""
    yvs.set_pref('version', 59)
    user_prefs = yvs.core.get_user_prefs()
    nose.assert_equal(user_prefs['version'], 59)


@nose.with_setup(set_up, tear_down)
def test_set_nonexistent():
    """should discard nonexistent preferences"""
    yvs.set_pref('foo', 'bar')
    user_prefs = yvs.core.get_user_prefs()
    nose.assert_not_in('foo', user_prefs)


@nose.with_setup(set_up, tear_down)
def test_set_language_clear_cache():
    """should clear cache when setting language"""
    nose.assert_true(
        os.path.exists(yvs.cache.LOCAL_CACHE_DIR_PATH),
        'local cache directory does not exist')
    yvs.cache.add_cache_entry('foo', 'blah blah')
    yvs.set_pref('language', 'spa')
    nose.assert_false(
        os.path.exists(yvs.cache.LOCAL_CACHE_DIR_PATH),
        'local cache directory exists')


@nose.with_setup(set_up, tear_down)
@redirect_stdout
def test_main(out):
    """should pass preference data to setter"""
    alfred_variables = {
        'pref_id': 'version',
        'pref_name': 'version',
        'value_id': '107',
        'value_name': 'New English Translation'
    }
    yvs.main(alfred_variables)
    alfred_json = json.loads(out.getvalue())
    nose.assert_equals(
        alfred_json['alfredworkflow']['variables'], alfred_variables)
    user_prefs = yvs.core.get_user_prefs()
    nose.assert_equals(user_prefs['version'], 107)
