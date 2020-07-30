#!/usr/bin/env python3
# coding=utf-8

import json

import nose.tools as nose
from unittest.mock import Mock, NonCallableMock, patch

import tests
import yvs.copy_ref as yvs
from tests.decorators import redirect_stdout, use_user_prefs

with open('tests/html/psa.23.html') as html_file:
    patch_urlopen = patch(
        'urllib.request.urlopen', return_value=NonCallableMock(
            read=Mock(return_value=html_file.read())))


def set_up():
    patch_urlopen.start()
    tests.set_up()


def tear_down():
    patch_urlopen.stop()
    tests.tear_down()


@nose.with_setup(set_up, tear_down)
def test_copy_chapter():
    """should copy reference content for chapter"""
    ref_content = yvs.get_copied_ref('111/psa.23')
    nose.assert_regexp_matches(ref_content, 'Lorem')
    nose.assert_regexp_matches(ref_content, 'nunc nulla')
    nose.assert_regexp_matches(ref_content, 'fermentum')


@nose.with_setup(set_up, tear_down)
def test_copy_verse():
    """should copy reference content for verse"""
    ref_content = yvs.get_copied_ref('111/psa.23.2')
    nose.assert_not_regexp_matches(ref_content, 'Lorem')
    nose.assert_regexp_matches(ref_content, 'nunc nulla')
    nose.assert_not_regexp_matches(ref_content, 'fermentum')


@nose.with_setup(set_up, tear_down)
def test_copy_verse_range():
    """should copy reference content for verse range"""
    ref_content = yvs.get_copied_ref('111/psa.23.1-2')
    nose.assert_regexp_matches(ref_content, 'Lorem')
    nose.assert_regexp_matches(ref_content, 'nunc nulla')
    nose.assert_not_regexp_matches(ref_content, 'fermentum')


@nose.with_setup(set_up, tear_down)
@use_user_prefs(
    {'language': 'eng', 'version': 59,
        'refformat': '"{content}"\n\n({name} {version})',
        'versenumbers': False})
def test_refformat():
    """should honor the chosen reference format"""
    ref_content = yvs.get_copied_ref('59/psa.23.6')
    nose.assert_equals(ref_content, '"Proin nulla orci,"\n\n(Psalms 23:6 ESV)')


@nose.with_setup(set_up, tear_down)
def test_header():
    """should prepend reference header to copied string"""
    ref_content = yvs.get_copied_ref('59/psa.23')
    nose.assert_regexp_matches(ref_content, r'^Psalms 23 \(ESV\)')


@nose.with_setup(set_up, tear_down)
@use_user_prefs(
    {'language': 'spa', 'version': 128,
        'refformat': '{name} ({version})\n\n{content}',
        'versenumbers': False})
def test_header_language():
    """reference header should reflect chosen language"""
    ref_content = yvs.get_copied_ref('128/psa.23')
    nose.assert_regexp_matches(ref_content, r'^Salmo 23 \(NVI\)')


@nose.with_setup(set_up, tear_down)
def test_whitespace_words():
    """should handle spaces appropriately"""
    ref_content = yvs.get_copied_ref('111/psa.23')
    nose.assert_regexp_matches(ref_content, 'adipiscing elit.',
                               'should respect content consisting of spaces')
    nose.assert_regexp_matches(ref_content, 'consectetur adipiscing',
                               'should collapse consecutive spaces')


@nose.with_setup(set_up, tear_down)
def test_whitespace_lines():
    """should add line breaks where appropriate"""
    ref_content = yvs.get_copied_ref('111/psa.23')
    nose.assert_regexp_matches(ref_content, r'Psalms 23 \(NIV\)\n\n\S',
                               'should add two line breaks after header')
    nose.assert_regexp_matches(ref_content, r'amet,\nconsectetur',
                               'should add newline before each p block')
    nose.assert_regexp_matches(ref_content, r'erat.\n\n\S',
                               'should add newline after each p block')
    nose.assert_regexp_matches(ref_content, r'orci,\ndapibus',
                               'should add newline between each qc block')
    nose.assert_regexp_matches(ref_content, r'nec\nfermentum',
                               'should add newline between each q block')
    nose.assert_regexp_matches(ref_content, r'elit.\n\nUt',
                               'should add newlines around each li1 block')
    nose.assert_regexp_matches(ref_content, r'leo,\n\nhendrerit',
                               'should add two newlines for each b block')


@nose.with_setup(set_up, tear_down)
@use_user_prefs(
    {'language': 'eng', 'version': 111,
        'refformat': '{name} ({version})\n\n{content}',
        'versenumbers': True})
def test_versenumbers():
    """should honor the versenumbers preference"""
    ref_content = yvs.get_copied_ref('111/psa.23')
    nose.assert_regexp_matches(ref_content, r'5 fermentum')
    nose.assert_not_regexp_matches(ref_content, r'#')


@nose.with_setup(set_up, tear_down)
@use_user_prefs(
    {'language': 'eng', 'version': 97,
        'refformat': '{name} ({version})\n\n{content}',
        'versenumbers': True})
def test_versenumbers_range():
    """should handle verse range labels (used by versions like the MSG)"""
    ref_content = yvs.get_copied_ref('111/psa.23.7-9')
    nose.assert_regexp_matches(ref_content, r'7-9 dapibus et augue in,')
    nose.assert_not_regexp_matches(ref_content, r'#')


@nose.with_setup(set_up, tear_down)
@use_user_prefs(
    {'language': 'eng', 'version': 97,
        'refformat': '{name} ({version})\n\n{content}',
        'versenumbers': True})
def test_versenumbers_range_start():
    """should handle range labels when verse at start of range is given"""
    ref_content = yvs.get_copied_ref('111/psa.23.7')
    nose.assert_regexp_matches(ref_content, r'7-9 dapibus et augue in,')
    nose.assert_not_regexp_matches(ref_content, r'#')


@nose.with_setup(set_up, tear_down)
@use_user_prefs(
    {'language': 'eng', 'version': 97,
        'refformat': '{name} ({version})\n\n{content}',
        'versenumbers': True})
def test_versenumbers_range_end():
    """should handle range labels when verse at end of range is given"""
    ref_content = yvs.get_copied_ref('111/psa.23.9')
    nose.assert_regexp_matches(ref_content, r'7-9 dapibus et augue in,')
    nose.assert_not_regexp_matches(ref_content, r'#')


@nose.with_setup(set_up, tear_down)
@use_user_prefs(
    {'language': 'eng', 'version': 97,
        'refformat': '{name} ({version})\n\n{content}',
        'versenumbers': True})
def test_versenumbers_range_middle():
    """should handle range labels when verse in middle of range is given"""
    ref_content = yvs.get_copied_ref('111/psa.23.8')
    nose.assert_regexp_matches(ref_content, r'7-9 dapibus et augue in,')
    nose.assert_not_regexp_matches(ref_content, r'#')


@nose.with_setup(set_up, tear_down)
@patch('yvs.web.get_url_content', return_value='abc')
def test_url_always_chapter(get_url_content):
    """should always fetch HTML from chapter URL"""
    yvs.get_copied_ref('59/psa.23.2')
    get_url_content.assert_called_once_with(
        'https://www.bible.com/bible/59/PSA.23')


@nose.with_setup(set_up, tear_down)
def test_cache_url_content():
    """should cache chapter URL content after first fetch"""
    yvs.get_copied_ref('59/psa.23.2')
    with patch('urllib.request.Request') as request:
        yvs.get_copied_ref('59/psa.23.3')
        request.assert_not_called()


@nose.with_setup(set_up, tear_down)
def test_nonexistent_verse():
    """should return empty string for nonexistent verses"""
    ref_content = yvs.get_copied_ref('111/psa.23.13')
    nose.assert_equal(ref_content, '')


@nose.with_setup(set_up, tear_down)
def test_unicode_content():
    """should return copied reference content as Unicode"""
    ref_content = yvs.get_copied_ref('111/psa.23')
    nose.assert_is_instance(ref_content, str)


@nose.with_setup(set_up, tear_down)
@redirect_stdout
def test_main(out):
    """main function should output copied reference content"""
    ref_uid = '59/psa.23'
    ref_content = yvs.get_copied_ref(ref_uid)
    yvs.main(ref_uid)
    main_json = json.loads(out.getvalue())
    nose.assert_equal(main_json, {
        'alfredworkflow': {
            'arg': ref_uid,
            'variables': {
                'copied_ref': ref_content,
                'full_ref_name': 'Psalms 23 (ESV)'
            }
        }
    })
