# yvs.filter_prefs

from __future__ import unicode_literals
import re
import yvs.shared as shared
from functools import partial
from operator import itemgetter


prefs = shared.get_prefs()


class Preference(object):

    def __init__(self, key, name, title, values):

        # Store key name, preference name and result title for this preference
        self.key = key
        self.name = name
        self.title = title
        # Store reference to function that will produce
        # a list of all possible values for this preference
        self.values = values

    # Retrieve Alfred result object for this preference
    def get_pref_result(self):

        return {
            'title': self.title,
            'subtitle': 'Set your preferred {}'.format(self.title.lower()),
            'autocomplete': '{} '.format(self.key),
            'valid': 'no'
        }

    # Retrieve list of available values for this preference
    def get_values(self):

        return self.values()

    # Retrieve the null result for when the given value can't be found
    def get_value_null_result(self):

        return {
            'title': 'No Results for {}'.format(self.title),
            'subtitle': 'Could not find a {} matching the query'.format(
                self.name),
            'valid': 'no'
        }

    # Retrieve Alfred result list of all available values for this preference
    def get_value_result_list(self, query_str):

        values = self.get_values()
        results = []

        for value in values:

            result = {
                'arg': '{}:{}'.format(self.key, value['id']),
                'title': value['name']
            }

            if value['id'] == prefs[self.key]:
                # If this value is the current value, indicate such
                result['subtitle'] = ('This is already your preferred {}'
                                      .format(self.name))
                result['valid'] = 'no'
            else:
                result['subtitle'] = 'Set this as your preferred {}'.format(
                    self.name)

            # Show all results if query string is empty
            # Otherwise, only show results whose titles begin with query
            if not query_str or result['title'].lower().startswith(query_str):
                results.append(result)

        if not results:
            results.append(self.get_value_null_result())

        return results


# Delineate all available workflow preferences
PREFERENCES = {
    Preference(
        key='language', name='language', title='Language',
        values=shared.get_languages),
    Preference(
        key='version', name='version', title='Version',
        values=partial(shared.get_versions, prefs['language'])),
    Preference(
        key='searchEngine', name='search engine', title='Search Engine',
        values=shared.get_search_engines)
}


def get_pref_matches(query_str):

    patt = r'^{key}{value}.*?$'.format(
        key=r'(\w+)',
        value=r'(?:\s?(\w+))?')
    return re.search(patt, query_str, flags=re.UNICODE)


# Retrieve result list of available preferences, filtered by the given query
def get_pref_result_list(query_str):

    return [pref.get_pref_result() for pref in
            PREFERENCES if pref.key.lower().startswith(query_str)]


def get_result_list(query_str):

    query_str = shared.format_query_str(query_str)
    pref_matches = get_pref_matches(query_str)
    results = []

    if pref_matches:

        pref_key = pref_matches.group(1)
        pref_value = pref_matches.group(2)

        for pref in PREFERENCES:
            # If key name in query exactly matches a preference key name
            if pref.key.lower() == pref_key:
                # Get list of available values for the given preference
                results = pref.get_value_result_list(pref_value)
                break
        # If no exact matches, filter list of available preferences by query
        if not results:
            results = get_pref_result_list(query_str)

    else:

        results = get_pref_result_list(query_str)

    # Always sort results by title in this case
    results.sort(key=itemgetter('title'))

    return results


def main(query_str):

    results = get_result_list(query_str)

    if not results:
        results = [{
            'uid': 'yvs-noprefs',
            'title': 'Invalid preference name or value',
            'subtitle': 'Please enter a valid name or value to set',
            'valid': 'no'
        }]

    print(shared.get_result_list_xml(results))


if __name__ == '__main__':
    main('{query}')
