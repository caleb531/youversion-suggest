#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import time
import shared


def query_matches_ref(query, ref):

    conditions = 1
    true_conditions = 0

    for i in xrange(len(query['book']), 0, -1):
        if shared.query_matches_book(query['book'][:i], ref['book'].lower()):
            true_conditions += 1
            break

    if 'chapter' in query:

        conditions += 1
        if str(ref['chapter']).startswith(str(query['chapter'])):
            true_conditions += 1

        if 'verse' in query and 'verse' in ref:

            conditions += 1
            if str(ref['verse']).startswith(str(query['verse'])):
                true_conditions += 1

            if 'endverse' in query and 'endverse' in ref:

                conditions += 1
                if str(ref['endverse']).startswith(str(query['endverse'])):
                    true_conditions += 1

        if 'version' in query:

            conditions += 1
            for i in xrange(len(query['version']), 0, -1):
                if ref['version'].startswith(query['version'][:i]):
                    true_conditions += 1
                    break

    return conditions == true_conditions


def get_result_list(query_str, prefs=None):

    query_str = shared.format_query_str(query_str)
    query = shared.get_query_object(query_str)
    results = []
    recent_refs = shared.get_recent_refs()

    for ref_uid in recent_refs:

        ref = shared.get_ref_object(ref_uid, prefs)
        if not query or query_matches_ref(query, ref):
            full_ref = shared.get_full_ref(ref)
            result = {
                'arg': ref_uid,
                'title': full_ref,
                'subtitle': 'View on YouVersion',
                'valid': 'yes'
            }
            results.append(result)

    return results


def main(query_str='{query}', prefs=None):

    results = get_result_list(query_str, prefs)

    if not results:
        results = [{
            'uid': 'yvs-norecent',
            'title': 'No Results',
            'subtitle': 'No recent references matching \'{}\''
            .format(query_str),
            'valid': 'no'
        }]

    print(shared.get_result_list_xml(results))

if __name__ == '__main__':
    main()