# test_update_language_list

from __future__ import unicode_literals

import json
import os
import os.path

import nose.tools as nose

import yvs.shared as yvs
import utilities.add_language as add_lang
from tests.test_add_language import set_up, tear_down


@nose.with_setup(set_up, tear_down)
def test_update_languge_list_add():
    """should add new languages to language list"""
    new_language_id = 'kln'
    new_language_name = 'Klingon'
    langs_path = os.path.join(yvs.PACKAGED_DATA_DIR_PATH, 'languages.json')
    with open(langs_path, 'r') as langs_file:
        langs = json.load(langs_file)
        orig_num_langs = len(langs)
    add_lang.update_language_list(new_language_id, new_language_name)
    with open(langs_path, 'r') as langs_file:
        langs = json.load(langs_file)
        num_langs = len(langs)
        nose.assert_equal(num_langs, orig_num_langs + 1)
        new_lang = None
        for lang in langs:
            if lang['id'] == new_language_id:
                new_lang = lang
        nose.assert_is_not_none(new_lang)
        nose.assert_equal(new_lang['name'], new_language_name)
