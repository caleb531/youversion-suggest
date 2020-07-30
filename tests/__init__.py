#!/usr/bin/env python3
# coding=utf-8

import os
import os.path
import shutil
import tempfile

from unittest.mock import patch

import yvs.core as core
import yvs.cache as cache

temp_dir = tempfile.gettempdir()
local_data_dir_patcher = patch(
    'yvs.core.LOCAL_DATA_DIR_PATH',
    os.path.join(temp_dir, 'yvs-data'))
local_cache_dir_patcher = patch(
    'yvs.cache.LOCAL_CACHE_DIR_PATH',
    os.path.join(temp_dir, 'yvs-cache'))


def set_up():
    local_data_dir_patcher.start()
    try:
        os.mkdir(core.LOCAL_DATA_DIR_PATH)
    except OSError:
        pass
    local_cache_dir_patcher.start()
    try:
        os.mkdir(cache.LOCAL_CACHE_DIR_PATH)
    except OSError:
        pass


def tear_down():
    try:
        shutil.rmtree(cache.LOCAL_CACHE_DIR_PATH)
    except OSError:
        pass
    local_cache_dir_patcher.stop()
    try:
        shutil.rmtree(core.LOCAL_DATA_DIR_PATH)
    except OSError:
        pass
    local_data_dir_patcher.stop()
