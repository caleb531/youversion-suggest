#!/usr/bin/env python3
# coding=utf-8

import os
import os.path
import shutil

import nose.tools as nose

import yvs.clear_cache as yvs
from tests import set_up, tear_down


@nose.with_setup(set_up, tear_down)
def test_clear_cache():
    """should remove cache directory when cache is cleared"""
    yvs.main()
    nose.assert_false(
        os.path.exists(yvs.cache.LOCAL_CACHE_DIR_PATH),
        'local cache directory exists')


@nose.with_setup(set_up, tear_down)
def test_clear_cache_silent_fail():
    """should fail silently if cache directory does not exist"""
    shutil.rmtree(yvs.cache.LOCAL_CACHE_DIR_PATH)
    yvs.main()
    nose.assert_false(
        os.path.exists(yvs.cache.LOCAL_CACHE_DIR_PATH),
        'local cache directory exists')
