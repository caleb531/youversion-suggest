#!/usr/bin/env python

import webbrowser
import urllib
import re
import shared

base_url = 'https://www.google.com/search'


def get_full_ref(ref_uid):

    patt = '{version}/{book_id}\.{chapter}(?:\.{verses})?'.format(
        version='(\d+)',
        book_id='(\d?[a-z]+)',
        chapter='(\d+)',
        verses='(\d+(?:-\d+)?)')

    ref_uid_matches = re.match(patt, ref_uid)
    book_id = ref_uid_matches.group(2)
    chapter = ref_uid_matches.group(3)

    bible = shared.get_bible_data()
    book_name = shared.get_book(bible['books'], book_id)
    ref = '{book} {chapter}'.format(
        book=book_name,
        chapter=chapter)

    verses_match = ref_uid_matches.group(4)
    if verses_match:
        ref += ":{verses}".format(verses=verses_match)

    version_id = int(ref_uid_matches.group(1))
    version_name = shared.get_version(bible['versions'],
                                      version_id)['name']

    ref += " ({version})".format(version=version_name)

    return ref


def get_search_url(ref_uid):
    ref = get_full_ref(ref_uid)
    encoded_ref = urllib.quote_plus(ref)
    return '{base}?q={query_str}'.format(base=base_url, query_str=encoded_ref)


def open_search_url(ref_uid):
    webbrowser.open(get_search_url(ref_uid))


def main(ref_uid='{query}'):
    open_search_url(ref_uid)

if __name__ == '__main__':
    main()
