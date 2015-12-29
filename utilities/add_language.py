# utilities.add_language

# This language utility adds support for a language to YouVersion Suggest by
# gathering and parsing data from the YouVersion website to create all needed
# language files; this utility can also be used to update any Bible data for an
# already-supported language

from __future__ import unicode_literals
import argparse
import io
import itertools
import json
import os
import re
import yvs.shared as yvs
from operator import itemgetter
from pyquery import PyQuery


# Parameters for structuring JSON data
JSON_PARAMS = {
    'indent': 2,
    'separators': (',', ': '),
    'ensure_ascii': False,
    'sort_keys': True
}


# Parses the language name from the given category header string
def get_language_name(text):

    patt = r'^\s*(.+?)(?:\s*\((\d+)\)\s*)$'
    matches = re.search(patt, text, flags=re.UNICODE)
    if matches:
        return matches.group(1)
    else:
        return None


# Constructs an object representing a Bible version
def get_version(version_elem):

    link_elem = version_elem.find('a')
    url = link_elem.get('href')
    patt = r'(?<=/versions/)(\d+)-([a-z]+\d*)'
    matches = re.search(patt, url, flags=re.UNICODE)
    return {
        'id': int(matches.group(1)),
        'name': matches.group(2).upper(),
    }


# Retrieves list of HTML elements, each corresponding to a Bible version
def get_version_elems(language_id):

    d = PyQuery(
        url='https://www.bible.com/{}/versions'.format(
            language_id.replace('_', '-')),
        opener=yvs.get_url_content)

    category_elems = d('article > ul > li')
    version_elems = None
    language_name = None

    if category_elems:

        category_elem = category_elems[0]
        version_elems = d(category_elem).find('li')

        text = category_elem.text
        language_name = get_language_name(text)

    if not language_name:
        raise RuntimeError('Language name cannot be determined. Aborting.')

    return version_elems, language_name


# Returns a copy of the given version list, sorted and with duplicates removed
def get_unique_versions(versions):

    unique_versions = []
    for name, group in itertools.groupby(versions, key=itemgetter('name')):
        # When duplicates are encountered, favor the version with the lowest ID
        version = min(group, key=itemgetter('id'))
        unique_versions.append(version)

    return unique_versions


# Retrieves a list of dictionaries representing Bible versions
def get_versions(language_id, max_version_id):

    print('Retrieving version data...')

    versions = []

    version_elems, language_name = get_version_elems(language_id)

    if not version_elems:
        raise RuntimeError('Cannot find the given language. Aborting.')

    for version_elem in version_elems:
        version = get_version(version_elem)
        # Only add version if ID does not exceed a certain limit (if defined)
        if not max_version_id or version['id'] <= max_version_id:
            versions.append(version)

    versions.sort(key=itemgetter('name'))
    unique_versions = get_unique_versions(versions)

    return unique_versions, language_name


# Constructs an object representing a book of the Bible
def get_book(book_elem):

    return {
        'id': book_elem.get('data-book'),
        'name': book_elem.text.strip()
    }


# Retrieves a list of chapter counts for each book
def get_chapter_data():

    chapter_data_path = os.path.join('yvs', 'data', 'bible', 'chapters.json')
    with open(chapter_data_path, 'r') as chapter_data_file:
        chapter_data = json.load(chapter_data_file)

    return chapter_data


# Retrieves a list of books available in this language
def get_books(default_version):

    print('Retrieving book data...')

    books = []
    chapter_data = get_chapter_data()

    d = PyQuery(
        url='https://www.bible.com/bible/{}/jhn.1'.format(default_version),
        opener=yvs.get_url_content)

    book_elems = d('a[data-book]')

    if not book_elems:
        raise RuntimeError('Cannot retrieve book data. Aborting.')

    for book_elem in book_elems:
        book = get_book(book_elem)
        # Only add book to list if a chapter count exists for that book
        if book['id'] in chapter_data:
            books.append(book)

    return books


# Constructs object representing all Bible data for a particular version
# This data includes the list of books, list of versions, and default version
def get_bible_data(language_id, default_version, max_version_id):

    bible = {}
    bible['versions'], language_name = get_versions(
        language_id,
        max_version_id)

    # If no explicit default version is given, use version with smallest ID
    if not default_version:
        default_version = min(bible['versions'], key=itemgetter('id'))['id']
    elif not any(version['id'] == default_version for version in
                 bible['versions']):
        raise RuntimeError(
            'Given default version does not exist in language. Aborting.')

    bible['default_version'] = default_version
    bible['books'] = get_books(default_version)
    return bible, language_name


# Writes the given JSON data to a file as Unicode
def write_json_unicode(json_object, json_file):

    json_str = json.dumps(json_object, **JSON_PARAMS)
    json_file.write(json_str)
    json_file.write('\n')


# Constructs the Bible data object and save it to a JSON file
def save_bible_data(language_id, bible):

    bible_path = os.path.join(
        'yvs', 'data', 'bible',
        'language-{}.json'.format(language_id))
    with io.open(bible_path, 'w', encoding='utf-8') as bible_file:
        write_json_unicode(bible, bible_file)


# Adds this language's details (name, code) to the list of supported languages
def update_language_list(language_id, language_name):

    print('Updating language list...')

    langs_path = os.path.join('yvs', 'data', 'languages.json')
    with io.open(langs_path, 'r+', encoding='utf-8') as langs_file:
        langs = json.load(langs_file)
        # If language does not already exist in list of supported languages
        if not any(lang['id'] == language_id for lang in langs):
            langs.append({
                'id': language_id,
                'name': language_name
            })
            langs.sort(key=itemgetter('id'))
            langs_file.truncate(0)
            langs_file.seek(0)
            write_json_unicode(langs, langs_file)


# Adds to the worklow support for the language with the given parameters
def add_language(language_id, default_version, max_version_id):

    bible, language_name = get_bible_data(
        language_id,
        default_version,
        max_version_id)
    save_bible_data(language_id, bible)
    update_language_list(language_id, language_name)


# Parses all command-line arguments
def parse_cli_args():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'language_id',
        metavar='code',
        help='the ISO 639-1 code of the language')
    parser.add_argument(
        '--default-version',
        type=int,
        help='the default version to use for this language')
    parser.add_argument(
        '--max-version-id',
        type=int,
        help='the upper limit to which Bible version IDs are constrained')

    return parser.parse_args()


def main():

    cli_args = parse_cli_args()
    print('Adding language support...')
    add_language(
        cli_args.language_id.replace('-', '_'),
        cli_args.default_version,
        cli_args.max_version_id)
    print('Support for {} has been successfully added.'.format(
        cli_args.language_id.replace('_', '-')))

if __name__ == '__main__':
    main()
