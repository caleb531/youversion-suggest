# tests.test_add_language.test_main
# coding=utf-8

from __future__ import unicode_literals

import nose.tools as nose
from mock import patch

import utilities.add_language as add_lang
from tests.test_add_language import set_up, tear_down
from tests.test_add_language.decorators import redirect_stdout


@nose.with_setup(set_up, tear_down)
@patch('utilities.add_language.update_language_list')
@patch('utilities.add_language.save_bible_data')
@patch('utilities.add_language.get_bible_data', return_value={})
@patch('utilities.add_language.get_language_name', return_value='Swedish')
@redirect_stdout
def test_add_language(out, get_language_name, get_bible_data, save_bible_data,
                      update_language_list):
    """should perform all necessary steps to add a language"""
    language_id = 'swe'
    default_version = 33
    max_version_id = 500
    add_lang.add_language(
        language_id, default_version, max_version_id)
    get_language_name.assert_called_once_with(language_id)
    get_bible_data.assert_called_once_with(
        language_id, default_version, max_version_id)
    update_language_list.assert_called_once_with(
        language_id, get_language_name.return_value)


@patch('sys.argv', [add_lang.__file__, 'swe',
                    '--default-version', '33', '--max-version-id', '500'])
def test_parse_cli_args():
    """should parse command line arguments"""
    cli_args = add_lang.parse_cli_args()
    nose.assert_equal(cli_args.language_id, 'swe')
    nose.assert_equal(cli_args.default_version, 33)
    nose.assert_equal(cli_args.max_version_id, 500)


@patch('sys.argv', [add_lang.__file__, 'swe',
                    '--default-version', '33', '--max-version-id', '500'])
@patch('utilities.add_language.add_language')
@redirect_stdout
def test_main(out, add_language):
    """main function should pass correct arguments to add_language"""
    add_lang.main()
    add_language.assert_called_once_with('swe', 33, 500)


@patch('sys.argv', [add_lang.__file__, 'spa-es'])
@patch('utilities.add_language.add_language')
@redirect_stdout
def test_main_format_language_id_dash(out, add_language):
    """main function should properly format language IDs containing dashes"""
    add_lang.main()
    add_language.assert_called_once_with('spa_es', None, None)


@patch('utilities.add_language.add_language', side_effect=KeyboardInterrupt)
@patch('utilities.add_language.parse_cli_args')
@redirect_stdout
def test_main_keyboardinterrupt(out, parse_cli_args, add_language):
    """main function should quit gracefully when ^C is pressed"""
    nose.assert_is_none(add_lang.main())
