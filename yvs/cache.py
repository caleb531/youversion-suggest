#!/usr/bin/env python3
# coding=utf-8

import hashlib
import os
import os.path
import shutil

import yvs.core as core

# Path to the directory where this workflow stores volatile local data
LOCAL_CACHE_DIR_PATH = os.path.join(
    core.HOME_DIR_PATH, 'Library', 'Caches',
    'com.runningwithcrayons.Alfred', 'Workflow Data', core.WORKFLOW_UID)

# The maximum number of cache entries to store
MAX_NUM_CACHE_ENTRIES = 100


# Creates the directory (and any nonexistent parent directories) where this
# workflow stores volatile local data (i.e. cache data)
def create_local_cache_dirs():

    try:
        os.makedirs(get_cache_entry_dir_path())
    except OSError:
        pass


# Calculates the unique SHA1 checksum used as the filename for a cache entry
def get_cache_entry_checksum(entry_key):

    return hashlib.sha1(entry_key.encode('utf-8')).hexdigest()


# Retrieves the local filepath for a cache entry
def get_cache_entry_path(entry_key):

    entry_checksum = get_cache_entry_checksum(entry_key)
    return os.path.join(get_cache_entry_dir_path(), entry_checksum)


# Retrieves the path to the directory where all cache entries are stored
def get_cache_entry_dir_path():

    return os.path.join(LOCAL_CACHE_DIR_PATH, 'entries')


# Retrieves the path to the manifest file listing all cache entries
def get_cache_manifest_path():

    return os.path.join(LOCAL_CACHE_DIR_PATH, 'manifest.txt')


# Purge all expired entries in the cache
def purge_expired_cache_entries(manifest_file):
    # Read checksums from manifest; splitlines(True) preserves newlines
    manifest_file.seek(0)
    entry_checksums = manifest_file.read().splitlines(True)
    # Purge the oldest entry if the cache is too large
    if len(entry_checksums) > MAX_NUM_CACHE_ENTRIES:
        old_entry_checksum = entry_checksums[0].rstrip()
        manifest_file.truncate(0)
        manifest_file.seek(0)
        manifest_file.writelines(entry_checksums[1:])
        os.remove(os.path.join(
            get_cache_entry_dir_path(), old_entry_checksum))


# Adds to the cache a new entry with the given content
def add_cache_entry(entry_key, entry_content):

    create_local_cache_dirs()

    # Write entry content to entry file
    entry_path = get_cache_entry_path(entry_key)
    with open(entry_path, 'w') as entry_file:
        entry_file.write(entry_content)

    entry_checksum = os.path.basename(entry_path)
    cache_manifest_path = get_cache_manifest_path()
    with open(cache_manifest_path, 'a+') as manifest_file:
        # Write the new entry checksum to manifest file
        manifest_file.write(entry_checksum)
        manifest_file.write('\n')
        purge_expired_cache_entries(manifest_file)


# Retrieves the unmodified content of a cache entry
def get_cache_entry_content(entry_key):

    create_local_cache_dirs()
    entry_path = get_cache_entry_path(entry_key)
    try:
        with open(entry_path, 'r') as entry_file:
            return entry_file.read()
    except IOError:
        return None


# Removes all cache entries and the directory itself
def clear_cache():

    try:
        shutil.rmtree(LOCAL_CACHE_DIR_PATH)
    except OSError:
        pass
