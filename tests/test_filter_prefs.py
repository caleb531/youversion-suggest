#!/usr/bin/env python3
# coding=utf-8

import glob
import json

import nose.tools as nose

import yvs.filter_prefs as yvs
from tests import set_up, tear_down
from tests.decorators import redirect_stdout, use_user_prefs


@nose.with_setup(set_up, tear_down)
def test_show_languages():
    """should show all languages if no value is given"""
    results = yvs.get_result_list('language')
    nose.assert_equal(
        len(results), len(glob.glob('yvs/data/bible/bible-*.json')))


@nose.with_setup(set_up, tear_down)
def test_filter_languages():
    """should filter available languages if value is given"""
    results = yvs.get_result_list('language esp')
    nose.assert_equal(results[0]['uid'], 'yvs-language-spa')
    nose.assert_equal(
        results[0]['title'], 'Español (América Latina)')
    nose.assert_equal(results[0].get('valid', True), True)
    nose.assert_equal(len(results), 2)
    nose.assert_equal(results[0]['variables'], {
        'pref_id': 'language',
        'pref_name': 'language',
        'value_id': '"spa"',
        'value_name': 'Español (América Latina)'
    })


@nose.with_setup(set_up, tear_down)
def test_filter_languages_non_latin():
    """should filter non-latin language names"""
    results = yvs.get_result_list('language 繁')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['uid'], 'yvs-language-zho_tw')
    nose.assert_equal(results[0]['title'], '繁體中文')
    nose.assert_equal(results[0].get('valid', True), True)
    nose.assert_equal(results[0]['variables'], {
        'pref_id': 'language',
        'pref_name': 'language',
        'value_id': '"zho_tw"',
        'value_name': '繁體中文'
    })


@nose.with_setup(set_up, tear_down)
@use_user_prefs(
    {'language': 'spa', 'version': 128, 'refformat': '{name}\n{content}'})
def test_show_versions():
    """should show all versions if no value is given"""
    results = yvs.get_result_list('version')
    nose.assert_greater(len(results), 10)


@nose.with_setup(set_up, tear_down)
def test_filter_versions():
    """should filter available versions if value is given"""
    results = yvs.get_result_list('version ni')
    nose.assert_equal(len(results), 3)
    nose.assert_equal(results[0]['uid'], 'yvs-version-110')
    nose.assert_equal(results[0]['title'],
                      'New International Reader’s Version (NIRV)')
    nose.assert_equal(results[0].get('valid', True), True)
    nose.assert_equal(results[0]['variables'], {
        'pref_id': 'version',
        'pref_name': 'version',
        'value_id': '110',
        'value_name': 'New International Reader’s Version (NIRV)'
    })


@nose.with_setup(set_up, tear_down)
@use_user_prefs(
    {'language': 'spa', 'version': 128, 'refformat': '{name}\n{content}'})
def test_show_refformats():
    """should show all refformats if no value is given"""
    results = yvs.get_result_list('refformat')
    nose.assert_greater(len(results), 3)


@nose.with_setup(set_up, tear_down)
def test_filter_refformats():
    """should filter available refformats if value is given"""
    results = yvs.get_result_list('refformat http')
    result_title = '"Jesus wept." ¬ John 11:35 NIV ¬ {url}'.format(
        url=yvs.core.get_ref_url('111/jhn.11.35'))
    result_format_id = '"{content}"\n{name} {version}\n{url}'
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['uid'],
                      'yvs-refformat-{id}'.format(id=result_format_id))
    nose.assert_equal(results[0]['title'], result_title)
    nose.assert_equal(results[0].get('valid', True), True)
    nose.assert_equal(results[0]['variables'], {
        'pref_id': 'refformat',
        'pref_name': 'reference format',
        'value_id': json.dumps(result_format_id),
        'value_name': result_title
    })


@nose.with_setup(set_up, tear_down)
@use_user_prefs({'language': 'eng', 'version': 59, 'refformat': 'Z {content}'})
def test_show_current_refformat():
    """should show current refformat as an available value"""
    results = yvs.get_result_list('refformat Z')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['uid'], 'yvs-refformat-Z {content}')
    nose.assert_equal(results[0]['title'], 'Z Jesus wept.')
    nose.assert_equal(results[0]['valid'], False)
    nose.assert_equal(results[0]['variables'], {
        'pref_id': 'refformat',
        'pref_name': 'reference format',
        'value_id': '"Z {content}"',
        'value_name': 'Z Jesus wept.'
    })


@nose.with_setup(set_up, tear_down)
def test_nonexistent_pref():
    """should not match nonexistent preference"""
    results = yvs.get_result_list('xyz')
    nose.assert_equal(len(results), 0)


@nose.with_setup(set_up, tear_down)
def test_nonexistent_value():
    """should return null result for nonexistent value"""
    results = yvs.get_result_list('language xyz')
    nose.assert_regexp_matches(results[0]['title'], 'No Results')
    nose.assert_equal(results[0]['valid'], False)
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_current_value():
    """should not make preference's current value actionable"""
    results = yvs.get_result_list('language english')
    nose.assert_equal(results[0]['title'], 'English')
    nose.assert_equal(results[0]['valid'], False)
    nose.assert_equal(len(results), 1)


@nose.with_setup(set_up, tear_down)
def test_invalid_query():
    """should show all available preferences for invalid preference name"""
    results = yvs.get_result_list('!@#')
    nose.assert_not_equal(len(results), 0)


@nose.with_setup(set_up, tear_down)
def test_show_all_preferences():
    """should show all available preferences if query is empty"""
    results = yvs.get_result_list('')
    nose.assert_not_equal(len(results), 0)


@nose.with_setup(set_up, tear_down)
def test_preferences_autocompletion():
    """autocompletion should be functioning for all preference results"""
    results = yvs.get_result_list('')
    for result in results:
        nose.assert_in('autocomplete', result)
        nose.assert_in('valid', result)
        nose.assert_equal(result['valid'], False)


@nose.with_setup(set_up, tear_down)
def test_filter_preferences_id():
    """should filter available preferences if partial pref ID is given"""
    results = yvs.get_result_list('reff')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['uid'], 'yvs-refformat')
    nose.assert_equal(results[0]['title'], 'Reference Format')


@nose.with_setup(set_up, tear_down)
def test_filter_preferences_name():
    """should filter available preferences if partial pref name is given"""
    results = yvs.get_result_list('refe')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['uid'], 'yvs-refformat')
    nose.assert_equal(results[0]['title'], 'Reference Format')


@nose.with_setup(set_up, tear_down)
def test_filter_preferences_name_partial():
    """should match partial pref name at word boundaries"""
    results = yvs.get_result_list('version en st')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['uid'], 'yvs-version-59')
    nose.assert_equal(results[0]['title'], 'English Standard Version (ESV)')


@nose.with_setup(set_up, tear_down)
def test_filter_preferences_show_current():
    """should show current values for all preferences"""
    results = yvs.get_result_list('')
    nose.assert_equal(len(results), 5)
    nose.assert_in('English', results[0]['subtitle'])
    nose.assert_in('NIV', results[1]['subtitle'])


@nose.with_setup(set_up, tear_down)
@use_user_prefs({
    'language': 'eng', 'version': 999, 'refformat':
    '{name}\n\n{content}', 'versenumbers': False, 'copybydefault': False})
def test_filter_preferences_show_current_valid_only():
    """should not show invalid current preference values"""
    results = yvs.get_result_list('')
    nose.assert_equal(len(results), 5)
    nose.assert_in('currently', results[0]['subtitle'])
    nose.assert_not_in('currently', results[1]['subtitle'])


@nose.with_setup(set_up, tear_down)
def test_filter_preference_entire_query():
    """should match available preference values using entire query string"""
    results = yvs.get_result_list('language español (españa)')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['uid'], 'yvs-language-spa_es')
    nose.assert_equal(results[0]['title'], 'Español (España)')
    nose.assert_equal(results[0].get('valid', True), True)
    nose.assert_equal(results[0]['variables'], {
        'pref_id': 'language',
        'pref_name': 'language',
        'value_id': '"spa_es"',
        'value_name': 'Español (España)'
    })


@nose.with_setup(set_up, tear_down)
def test_filter_preference_ignore_special():
    """should ignore special characters when matching preference values"""
    results = yvs.get_result_list('language 繁體中文$$')
    nose.assert_equal(len(results), 1)
    nose.assert_equal(results[0]['uid'], 'yvs-language-zho_tw')
    nose.assert_equal(results[0]['title'], '繁體中文')
    nose.assert_equal(results[0].get('valid', True), True)
    nose.assert_equal(results[0]['variables'], {
        'pref_id': 'language',
        'pref_name': 'language',
        'value_id': '"zho_tw"',
        'value_name': '繁體中文'
    })


@nose.with_setup(set_up, tear_down)
@redirect_stdout
def test_main_output(out):
    """should output pref result list JSON"""
    query_str = 'language'
    yvs.main(query_str)
    output = out.getvalue().rstrip()
    results = yvs.get_result_list(query_str)
    feedback = yvs.core.get_result_list_feedback_str(results).rstrip()
    nose.assert_equal(output, feedback)


@nose.with_setup(set_up, tear_down)
@redirect_stdout
def test_null_result(out):
    """should output "No Results" JSON item for empty pref result list"""
    query_str = 'xyz'
    yvs.main(query_str)
    feedback_str = out.getvalue()
    feedback = json.loads(feedback_str)
    nose.assert_equal(len(feedback['items']), 1, 'result item is missing')
    item = feedback['items'][0]
    nose.assert_equal(item['title'], 'No Results')
    nose.assert_equal(item['valid'], False)


@nose.with_setup(set_up, tear_down)
@redirect_stdout
def test_feedback_show_all(out):
    """should output JSON for all results if query is empty"""
    yvs.main('')
    output = out.getvalue().rstrip()
    results = yvs.get_result_list('')
    feedback = yvs.core.get_result_list_feedback_str(results).rstrip()
    nose.assert_equal(output, feedback)
