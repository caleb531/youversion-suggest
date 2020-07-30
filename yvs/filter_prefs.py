#!/usr/bin/env python3
# coding=utf-8

import json
import re
import sys
from operator import itemgetter

import yvs.core as core


# Returns a list of definition objects for all available preferences
def get_pref_defs(user_prefs):

    return [
        {
            'id': 'language',
            'name': 'Language',
            'short_name': 'language',
            'values': core.get_languages(),
            'description': 'Set your preferred language for Bible content'
        },
        {
            'id': 'version',
            'name': 'Version',
            'short_name': 'version',
            'values': [get_version_value(version) for version in sorted(
                       core.get_versions(user_prefs['language']),
                       key=itemgetter('name'))],
            'description': 'Set your preferred version for Bible content'
        },
        {
            'id': 'refformat',
            'name': 'Reference Format',
            'short_name': 'reference format',
            'values': get_ref_format_values(user_prefs),
            'description': 'Set your preferred format for copied Bible'
                           ' content'
        },
        {
            'id': 'versenumbers',
            'name': 'Include Verse Numbers?',
            'short_name': 'verse numbers setting',
            'values': get_include_verse_numbers_values(),
            'description': 'Choose whether to include verse numbers in copied'
                           ' Bible content'
        },
        {
            'id': 'copybydefault',
            'name': 'Copy By Default?',
            'short_name': 'copy setting',
            'values': get_copy_by_default_values(),
            'description': 'Choose whether to copy references to the clipboard'
                           'without pressing the command key'
        }
    ]


# Convert the given version object to a value object for use in the preferences
# UI
def get_version_value(version):
    return {
        'id': version['id'],
        # The title as displayed in the Alfred UI should be the full name of
        # the version followed by its abbreviation
        'name': '{} ({})'.format(version['full_name'], version['name'])
    }


# Get a list of all available ref formats
def get_ref_format_values(user_prefs):

    ref = core.get_ref(
        '111/jhn.11.35', core.get_default_user_prefs())
    ref_formats = [
        '{name} ({version})\n\n{content}',
        '{name} {version}\n\n{content}',
        '{content}\n({name} {version})',
        '"{content}"\n{name} {version}',
        '"{content}"\n{name} {version}\n{url}'
    ]
    # Display the user's current preference in the list
    if user_prefs['refformat'] not in ref_formats:
        ref_formats.append(user_prefs['refformat'])

    return [get_ref_format_value(ref_format, ref)
            for ref_format in ref_formats]


def get_ref_format_value(ref_format, ref):

    return {
        'id': ref_format,
        'name': ref_format.format(
            name=core.get_basic_ref_name(ref),
            version=ref['version'],
            content='Jesus wept.',
            url=core.get_ref_url(ref['uid']))
        .replace('\n', ' ¬ ')
        # Since the above substitution adds whitespace to both sides of the
        # return symbol, the whitespace needs to be collapsed in the case of
        # consecutive return symbols
        .replace('  ', ' ')
    }


# Get a list of all available values for including verse numbers in copied
# Bible content
def get_include_verse_numbers_values():

    return [
        {
            'id': True,
            'name': 'Yes (include in copied content)'
        },
        {
            'id': False,
            'name': 'No (do not include in copied content)'
        }
    ]


# Get a list of all available values for the "Copy By Default" preference
def get_copy_by_default_values():

    return [
        {
            'id': True,
            'name': 'Yes (make Enter key copy to clipboard)'
        },
        {
            'id': False,
            'name': 'No (make Cmd-Enter copy to clipboard)'
        }
    ]


# Get the value object with the given ID for the given preference
def get_pref_value(pref_def, value_id):

    values = pref_def['values']
    for value in values:
        if value['id'] == value_id:
            return value
    return None


# Retrieves Alfred result object for this preference
def get_pref_def_result(pref_def, user_prefs):

    value = get_pref_value(pref_def, user_prefs[pref_def['id']])
    result = {}

    result['uid'] = 'yvs-{}'.format(pref_def['id'])
    result['title'] = pref_def['name']
    result['subtitle'] = pref_def['description']
    if value is not None:
        result['subtitle'] += ' (currently {})'.format(value['name'])
    result['autocomplete'] = '{} '.format(pref_def['id'].replace('_', ''))
    result['valid'] = False

    return result


# Get the result object for a single preference value
def get_value_result(value, user_prefs, pref_def):

    result = {
        'uid': 'yvs-{}-{}'.format(pref_def['id'], value['id']),
        'variables': {
            'pref_id': pref_def['id'],
            'pref_name': pref_def['short_name'],
            'value_id': json.dumps(value['id']),
            'value_name': value['name']
        },
        'title': value['name']
    }

    if value['id'] == user_prefs[pref_def['id']]:
        # If this value is the current value, indicate such
        result['subtitle'] = 'This is already your preferred {}'.format(
            pref_def.get('short_name'))
        result['valid'] = False
    else:
        result['subtitle'] = 'Set this as your preferred {}'.format(
            pref_def.get('short_name'))

    return result


# Return True of the given query string matches the given preference field;
# otherwise, return False
def if_query_str_matches(pref_field, query_str):
    pref_field = core.normalize_query_str(pref_field)
    # Match preference field if every word in query string matches field name
    # at some word boundary
    return all(re.search(r'(^|\s){}'.format(
               re.escape(word)), pref_field, flags=re.UNICODE | re.IGNORECASE)
               for word in query_str.split(' '))


# Retrieves Alfred result list of all available values for this preference
def get_value_result_list(user_prefs, pref_def, query_str):

    results = [get_value_result(value, user_prefs, pref_def)
               for value in pref_def['values']
               if not query_str
               or if_query_str_matches(value['name'], query_str)]

    if not results:
        results.append({
            'title': 'No Results',
            'subtitle': 'No values matching {}'.format(query_str),
            'valid': False
        })

    return results


# Parses a preference key and optional value from the given query string
def get_pref_match(query_str):

    patt = r'^{key}{value}.*?$'.format(
        key=r'(\w+)',
        value=r'(?:\s?(.+))?')
    return re.search(patt, query_str, flags=re.UNICODE)


# Retrieves result list of available preferences, filtered by the given query
def get_pref_result_list(user_prefs, pref_defs, pref_key_query=''):

    return [get_pref_def_result(pref_def, user_prefs) for pref_def in pref_defs
            if if_query_str_matches(pref_def['id'], pref_key_query)
            or if_query_str_matches(pref_def['name'], pref_key_query)]


# Retrieves result list of preferences or their respective values (depending on
# the given query string)
def get_result_list(query_str):

    user_prefs = core.get_user_prefs()
    pref_defs = get_pref_defs(user_prefs)
    query_str = core.normalize_query_str(query_str)
    pref_match = get_pref_match(query_str)
    results = []

    if pref_match:

        pref_key_query = pref_match.group(1)
        pref_value_query = pref_match.group(2)

        for pref_def in pref_defs:
            # If key name in query exactly match a preference key name
            if core.normalize_query_str(pref_def['id']) == pref_key_query:
                # Get list of available values for the given preference
                results = get_value_result_list(
                    user_prefs, pref_def, pref_value_query)
                break
        # If no exact match, filter list of available preferences by query
        if not results:
            results = get_pref_result_list(
                user_prefs, pref_defs, pref_key_query)

    else:

        # Should show all available preferences if query is empty
        # or if query does not match
        results = get_pref_result_list(user_prefs, pref_defs)

    return results


def main(query_str):

    results = get_result_list(query_str)
    if not results:
        results.append({
            'title': 'No Results',
            'subtitle': 'No preferences matching \'{}\''.format(query_str),
            'valid': False
        })

    print(core.get_result_list_feedback_str(results))


if __name__ == '__main__':
    main(sys.argv[1])
