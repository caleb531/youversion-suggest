#!/usr/bin/env python3
# coding=utf-8

import os.path

import nose.tools as nose

import yvs.filter_refs as yvs
from tests import set_up, tear_down
from tests.decorators import use_user_prefs


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'eng', 'version': 59, 'copybydefault': False})
def test_version_persistence():
    """should remember version preferences"""
    results = yvs.get_result_list('mat 4')
    nose.assert_equal(results[0]['title'], 'Matthew 4 (ESV)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'spa', 'version': 128, 'copybydefault': False})
def test_language_persistence():
    """should remember language preferences"""
    results = yvs.get_result_list('gá 4')
    nose.assert_equal(results[0]['title'], 'Gálatas 4 (NVI)')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_missing_prefs():
    """should supply missing preferences with defaults"""
    yvs.core.set_user_prefs({})
    results = yvs.get_result_list('mat 5.3')
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'eng', 'version': 999, 'copybydefault': False})
def test_invalid_user_version():
    """should raise exception when invalid version is set"""
    with nose.assert_raises(Exception):
        yvs.get_result_list('ph 4')


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'eng', 'version': 111, 'copybydefault': False})
def test_copy_by_default_false():
    """should export correct data when "Copy By Default?" setting is false"""
    results = yvs.get_result_list('mat 5.3')
    nose.assert_equal(results[0]['variables']['copybydefault'], 'False')
    nose.assert_equal(results[0]['subtitle'], 'View on YouVersion')
    nose.assert_equal(
        results[0]['mods']['cmd']['subtitle'], 'Copy content to clipboard')


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'eng', 'version': 111, 'copybydefault': True})
def test_copy_by_default_true():
    """should export correct data when "Copy By Default?" setting is true"""
    results = yvs.get_result_list('mat 5.3')
    nose.assert_equal(results[0]['variables']['copybydefault'], 'True')
    nose.assert_equal(results[0]['subtitle'], 'Copy content to clipboard')
    nose.assert_equal(
        results[0]['mods']['cmd']['subtitle'], 'View on YouVersion')


@nose.with_setup(set_up, tear_down)
def test_create_local_data_dir_silent_fail():
    """should silently fail if local data directory already exists"""
    yvs.core.create_local_data_dir()
    yvs.core.create_local_data_dir()
    nose.assert_true(
        os.path.exists(yvs.core.LOCAL_DATA_DIR_PATH),
        'local data directory does not exist')


@nose.with_setup(set_up, tear_down)
def test_prettified_prefs_json():
    yvs.core.set_user_prefs({
        'language': 'spa',
        'version': 128,
        'refformat': '{name}\n{content}'
    })
    with open(yvs.core.get_user_prefs_path(), 'r') as user_prefs_file:
        user_prefs_json = user_prefs_file.read()
        nose.assert_in('\n  ', user_prefs_json,
                       'User prefs JSON is not prettified')
