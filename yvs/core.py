#!/usr/bin/env python3
# coding=utf-8

import json
import os
import os.path
import re
import unicodedata

# Unique identifier for the workflow
WORKFLOW_UID = 'com.calebevans.youversionsuggest'

# Path to the user's home directory
HOME_DIR_PATH = os.path.expanduser('~')
# Path to the directory where this workflow stores non-volatile local data
LOCAL_DATA_DIR_PATH = os.path.join(
    HOME_DIR_PATH, 'Library', 'Application Support', 'Alfred',
    'Workflow Data', WORKFLOW_UID)
# Path to the directory containing data files apart of the packaged workflow
PACKAGED_CODE_DIR_PATH = os.path.join(os.getcwd(), 'yvs')

# The template used to build the URL for a Bible reference
REF_URL_TEMPLATE = 'https://www.bible.com/bible/{ref}'


# Creates the directory (and any nonexistent parent directories) where this
# workflow stores non-volatile local data
def create_local_data_dir():

    try:
        os.makedirs(LOCAL_DATA_DIR_PATH)
    except OSError:
        pass


# Retrieves bible data object (books, versions, etc.) for the given language
def get_bible(language_id):

    bible_path = os.path.join(
        PACKAGED_CODE_DIR_PATH, 'data', 'bible',
        'bible-{}.json'.format(language_id))
    with open(bible_path, 'r') as bible_file:
        return json.load(bible_file)


# Retrieves metadata for every book of the Bible, including chapter counts
def get_book_metadata():

    book_metadata_path = os.path.join(
        PACKAGED_CODE_DIR_PATH, 'data', 'bible', 'book-metadata.json')
    with open(book_metadata_path, 'r') as book_metadata_file:
        return json.load(book_metadata_file)


# Retrieves name of first book whose id matches the given id
def get_book(books, book_id):

    for book in books:  # pragma: no branch
        if book['id'] == book_id:
            return book['name']


# Retrieves first version object whose id matches the given id
def get_version(versions, version_id):

    for version in versions:
        if version['id'] == version_id:
            return version


# Retrieves a list of all supported versions for the given language
def get_versions(language_id):

    bible = get_bible(language_id)
    return bible['versions']


# Retrieves a list of all supported languages
def get_languages():

    languages_path = os.path.join(
        PACKAGED_CODE_DIR_PATH, 'data', 'bible', 'languages.json')
    with open(languages_path, 'r') as languages_file:
        return json.load(languages_file)


# Build the object for a single result list feedback item
def get_result_list_feedback_item(result):

    item = result.copy()

    item['text'] = result.get('text', {}).copy()
    # Text copied to clipboard when cmd-c is invoked for this result
    item['text']['copy'] = item['text'].get('copy', result['title'])
    # Text shown when invoking Large Type for this result
    item['text']['largetype'] = item['text'].get('largetype', result['title'])

    # Use different args when different modifiers are pressed
    item['mods'] = result.get('mods', {}).copy()
    item['mods']['ctrl'] = item['mods'].get('ctrl', {'arg': result['title']})

    # Icon shown next to result text
    item['icon'] = {
        'path': 'icon.png'
    }
    return item


# Constructs an Alfred JSON string from the given result list
def get_result_list_feedback_str(results):

    return json.dumps({
        'items': [get_result_list_feedback_item(result) for result in results]
    })


# Functions for accessing/manipulating mutable preferences


# Retrieves the path to the workflow's default user preferences file
def get_default_user_prefs_path():

    return os.path.join(
        PACKAGED_CODE_DIR_PATH, 'preferences', 'defaults.json')


# Retrieves the default values for all workflow preferences
def get_default_user_prefs():

    with open(get_default_user_prefs_path(), 'r') as defaults_file:
        return json.load(defaults_file)


# Retrieves the path to the workflow's user preferences file
def get_user_prefs_path():

    return os.path.join(LOCAL_DATA_DIR_PATH, 'preferences.json')


# Overrwrites (or creates) user preferences using the given preferences object
def set_user_prefs(user_prefs):

    # Always ensure that the data directory (where prefrences reside) exists
    create_local_data_dir()
    with open(get_user_prefs_path(), 'w') as prefs_file:
        json.dump(user_prefs, prefs_file, indent=2, separators=(',', ': '))


# Extends user preferences with any missing keys
def extend_user_prefs(user_prefs, default_user_prefs):

    # Add any missing preferences
    for pref_key in default_user_prefs:
        if pref_key not in user_prefs:
            user_prefs[pref_key] = default_user_prefs[pref_key]

    # Remove any obsolete preferences
    for pref_key in list(user_prefs.keys()):
        if pref_key not in default_user_prefs:
            del user_prefs[pref_key]

    return user_prefs


# Retrieves map of user preferences
def get_user_prefs():

    default_user_prefs = get_default_user_prefs()
    try:
        with open(get_user_prefs_path(), 'r') as prefs_file:
            return extend_user_prefs(
                json.load(prefs_file), default_user_prefs)
    except IOError:
        # If user preferences don't exist, create them
        set_user_prefs(default_user_prefs)
        return default_user_prefs


# Query-related functions


# Normalizes the format of the query string
def normalize_query_str(query_str):

    # Normalize all Unicode characters
    query_str = unicodedata.normalize('NFC', query_str)
    query_str = query_str.lower()
    # Remove all non-alphanumeric characters
    query_str = re.sub(r'[\W_]', ' ', query_str, flags=re.UNICODE)
    # Remove extra whitespace
    query_str = query_str.strip()
    query_str = re.sub(r'\s+', ' ', query_str)

    return query_str


# Parses the given reference UID into a dictionary representing that reference
def get_ref(ref_uid, user_prefs):

    patt = r'^{version}/{book_id}\.{chapter}(?:\.{verse}{endverse})?$'.format(
        version=r'(\d+)',
        book_id=r'(\d?[a-z]+)',
        chapter=r'(\d+)',
        verse=r'(\d+)',
        endverse=r'(?:-(\d+))?')

    ref_uid_match = re.match(patt, ref_uid)
    ref = {
        'uid': ref_uid,
        'book_id': ref_uid_match.group(2),
        'version_id': int(ref_uid_match.group(1)),
        'chapter': int(ref_uid_match.group(3))
    }

    # Include book name using book ID and currently-set language
    bible = get_bible(user_prefs['language'])
    book_name = get_book(bible['books'], ref['book_id'])
    ref['book'] = book_name

    # Include verse number if it exists
    verse_match = ref_uid_match.group(4)
    if verse_match:
        ref['verse'] = int(verse_match)

    # Include end verse number if it exists
    endverse_match = ref_uid_match.group(5)
    if endverse_match:
        ref['endverse'] = int(endverse_match)

    # Include full version name (acronym) if it exists
    version_name = get_version(bible['versions'], ref['version_id'])['name']
    ref['version'] = version_name

    return ref


# Retrieves the basic reference name without the version abbreviation
def get_basic_ref_name(ref):

    ref_name = '{book} {chapter}'.format(
        book=ref['book'],
        chapter=ref['chapter'])

    if 'verse' in ref:
        ref_name += ':{verse}'.format(verse=ref['verse'])

    if 'endverse' in ref:
        ref_name += '-{endverse}'.format(endverse=ref['endverse'])

    return ref_name


# Retrieves the full reference name with the version abbreviation
def get_full_ref_name(ref):

    return '{name} ({version})'.format(
        name=get_basic_ref_name(ref),
        version=ref['version'])


# Builds the URL used to view the reference with the given UID
def get_ref_url(ref_uid):
    return REF_URL_TEMPLATE.format(ref=ref_uid.upper())


# Normalizes format of reference content by removing superfluous whitespace
def normalize_ref_content(ref_content):

    # Collapse consecutive spaces into a single space
    ref_content = re.sub(r' {2,}', ' ', ref_content)
    # Collapse sequences of three or more newlines into two
    ref_content = re.sub(r'\n{3,}', '\n\n', ref_content)
    # Strip leading/trailing whitespace for entire reference
    ref_content = ref_content.strip()
    # Strip leading/trailing whitespace for each paragraph
    ref_content = re.sub(r' ?\n ?', '\n', ref_content)
    return ref_content
