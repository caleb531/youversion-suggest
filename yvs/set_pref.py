#!/usr/bin/env python3
# coding=utf-8

import json
import os

import yvs.core as core
import yvs.cache as cache


# Set the YouVersion Suggest preference with the given key
def set_pref(pref_id, value_id):

    user_prefs = core.get_user_prefs()
    user_prefs[pref_id] = value_id

    # If new language is set, ensure that preferred version is updated also
    if pref_id == 'language':
        bible = core.get_bible(language_id=value_id)
        user_prefs['version'] = bible['default_version']
        cache.clear_cache()

    core.set_user_prefs(user_prefs)


def main(variables):

    # value_id needs to be parsed as JSON so we can preserve type data for
    # proper serialization to the preferences file
    set_pref(variables['pref_id'], json.loads(variables['value_id']))
    print(json.dumps({
        'alfredworkflow': {
            'variables': variables
        }
    }))


if __name__ == '__main__':
    main({
        'pref_id': os.environ['pref_id'],
        'pref_name': os.environ['pref_name'],
        'value_id': os.environ['value_id'],
        'value_name': os.environ['value_name']
    })
