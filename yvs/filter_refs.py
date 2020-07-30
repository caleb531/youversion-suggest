#!/usr/bin/env python3
# coding=utf-8

import re
import sys
from operator import itemgetter

import yvs.core as core


# Parses the given query string into components of a Bible reference
def get_ref_match(query_str):

    # Pattern for parsing any bible reference
    patt = '^{book}(?:{chapter}(?:{verse}{endverse})?{version})?$'.format(
        book=r'(\d?(?:[^\W\d_]|\s)+|\d)\s?',
        chapter=r'(\d+)\s?',
        verse=r'(\d+)\s?',
        endverse=r'(\d+)?\s?',
        version=r'([^\W\d_](?:[^\W\d_]\d*|\s)*)?.*?')
    return re.search(patt, query_str, flags=re.UNICODE)


def normalize_query_str(query_str):

    query_str = core.normalize_query_str(query_str)
    # Parse shorthand reference notation
    query_str = re.sub(r'(\d)(?=[a-z])', '\\1 ', query_str)
    query_str = re.sub(r'\s+', ' ', query_str)
    query_str = query_str.strip()

    return query_str


# Builds the query object from the given query string
def get_query_object(query_str):

    # Match section of the bible based on query
    ref_match = get_ref_match(query_str)

    if not ref_match:
        return None

    # Create query object for storing query data
    query = {}

    book_match = ref_match.group(1)
    query['book'] = book_match.rstrip()

    chapter_match = ref_match.group(2)
    if chapter_match:
        query['chapter'] = max(1, int(chapter_match))

    verse_match = ref_match.group(3)
    if verse_match:
        query['verse'] = max(1, int(verse_match))

    endverse_match = ref_match.group(4)
    if endverse_match:
        query['endverse'] = int(endverse_match)

    version_match = ref_match.group(5)
    if version_match:
        query['version'] = normalize_query_str(version_match)

    return query


# Finds a version which best matches the given version query
def guess_version(versions, version_query):

    # Chop off character from version query until matching version can be
    # found (if a matching version even exists)
    for i in range(len(version_query), 0, -1):
        for version in versions:
            if (normalize_query_str(
                  version['name']).startswith(version_query[:i])):
                return version

    return None


# Formats book name by removing non-alphanumeric characters
def normalize_book_name(book_name):

    book_name = book_name.lower()
    # Remove all non-alphanumeric characters
    book_name = re.sub(r'[\W_]', ' ', book_name, flags=re.UNICODE)
    # Remove extra whitespace
    book_name = book_name.strip()
    book_name = re.sub(r'\s+', ' ', book_name)

    return book_name


# Split the given book name into substrings
def split_book_name_into_parts(book_name):

    book_words = normalize_book_name(book_name).split(' ')
    return (' '.join(book_words[w:]) for w in range(len(book_words)))


# Retrieves list of books matching the given query
def get_matching_books(books, query):

    matching_books = []
    book_metadata = core.get_book_metadata()

    for b, book in enumerate(books):
        book_name_words = split_book_name_into_parts(book['name'])
        for w, book_word in enumerate(book_name_words):
            if book_word.startswith(query['book']):
                matching_books.append({
                    'id': book['id'],
                    'name': book['name'],
                    # Give more priority to book names that are matched sooner
                    # (e.g. if the query matched the first word of a book name,
                    # as opposed to the second or third word)
                    'priority': ((w + 1) * 100) + b,
                    # Store the metadata for the respective book (e.g. chapter
                    # count) on this matching book object for convenience
                    'metadata': book_metadata[book['id']]
                })
                break

    matching_books.sort(key=itemgetter('priority'))
    return matching_books


# Chooses most appropriate version based on current parameters
def choose_best_version(user_prefs, bible, query):

    chosen_version = None

    if 'version' in query:
        chosen_version = guess_version(bible['versions'], query['version'])

    if not chosen_version and 'version' in user_prefs:
        chosen_version = core.get_version(
            bible['versions'], user_prefs['version'])

    return chosen_version


# Builds a single result item
def get_result(book, query, chosen_version, user_prefs):

    chapter = min(query['chapter'], book['metadata']['chapters'])
    last_verse = book['metadata']['verses'][chapter - 1]

    result = {}

    # Find chapter if given
    result['uid'] = '{book}.{chapter}'.format(
        book=book['id'],
        chapter=chapter)
    result['title'] = '{book} {chapter}'.format(
        book=book['name'],
        chapter=chapter)

    if 'verse' in query:
        verse = min(query['verse'], last_verse)
        result['uid'] += '.{verse}'.format(verse=verse)
        result['title'] += ':{verse}'.format(verse=verse)

    if 'endverse' in query:
        endverse = min(query['endverse'], last_verse)
        if endverse > verse:
            result['uid'] += '-{endverse}'.format(endverse=endverse)
            result['title'] += '-{endverse}'.format(endverse=endverse)

    result['arg'] = '{version}/{uid}'.format(
        version=chosen_version['id'],
        uid=result['uid'])
    result['variables'] = {
        'ref_url': core.get_ref_url(result['arg']),
        'copybydefault': str(user_prefs['copybydefault'])
    }
    result['quicklookurl'] = result['variables']['ref_url']
    result['uid'] = 'yvs-{}'.format(result['arg'])
    result['title'] += ' ({version})'.format(
        version=chosen_version['name'])
    result['subtitle'] = 'View on YouVersion'
    result['mods'] = {
        'cmd': {
            'subtitle': 'Copy content to clipboard'
        }
    }

    # Make "Copy" the default action (instead of "View") when the copybydefault
    # preference is set to true
    if user_prefs['copybydefault']:
        result['subtitle'], result['mods']['cmd']['subtitle'] = \
            result['mods']['cmd']['subtitle'], result['subtitle']

    return result


# Retrieves search resylts matching the given query
def get_result_list(query_str):

    query_str = normalize_query_str(query_str)
    query = get_query_object(query_str)

    if not query:
        return []

    user_prefs = core.get_user_prefs()
    bible = core.get_bible(user_prefs['language'])

    if 'chapter' not in query:
        query['chapter'] = 1

    chosen_version = choose_best_version(user_prefs, bible, query)

    # Build and return result list from books matching the query
    return [get_result(book, query, chosen_version, user_prefs)
            for book in get_matching_books(bible['books'], query)]


def main(query_str):

    results = get_result_list(query_str)
    if not results:
        results.append({
            'title': 'No Results',
            'subtitle': 'No references matching \'{}\''.format(query_str),
            'valid': False
        })

    print(core.get_result_list_feedback_str(results))


if __name__ == '__main__':
    main(sys.argv[1])
