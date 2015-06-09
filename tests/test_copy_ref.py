#!/usr/bin/env python

import nose.tools as nose
import yv_suggest.copy_ref as yvs
import context_managers as ctx
from mock import patch, mock_open, Mock


with open('tests/files/psa.23.html') as html_file:
    TEST_REF_HTML = html_file.read()


def before_each():
    yvs.urllib2.urlopen = Mock()
    yvs.urllib2.urlopen.return_value.read = Mock(return_value=TEST_REF_HTML)


def after_each():
    pass


@nose.with_setup(before_each, after_each)
def test_copy_chapter():
    '''should copy reference content for chapter'''
    with open('tests/files/psa.23.txt') as text_file:
        with ctx.redirect_stdout() as out:
            yvs.main('111/psa.23')
            nose.assert_equal(out.getvalue().strip(),
                              text_file.read().strip())


@nose.with_setup(before_each, after_each)
def test_copy_verse():
    '''should copy reference content for verse'''
    with open('tests/files/psa.23.2.txt') as text_file:
        with ctx.redirect_stdout() as out:
            yvs.main('111/psa.23.2')
            nose.assert_equal(out.getvalue().strip(),
                              text_file.read().strip())


@nose.with_setup(before_each, after_each)
def test_copy_verse_range():
    '''should copy reference content for verse range'''
    with open('tests/files/psa.23.1-2.txt') as text_file:
        with ctx.redirect_stdout() as out:
            yvs.main('111/psa.23.1-2')
            nose.assert_equal(out.getvalue().strip(),
                              text_file.read().strip())


@nose.with_setup(before_each, after_each)
def test_language():
    '''should copy reference content in another language'''
    with open('tests/files/psa.23.txt') as text_file:
        with ctx.redirect_stdout() as out:
            yvs.main('128/psa.23', prefs={
                'language': 'es'
            })
            ref_text = text_file.read().strip()
            ref_text = ref_text.replace('Psalm', 'Salmos')
            ref_text = ref_text.replace('NIV', 'NVI')
            nose.assert_equal(out.getvalue().strip(),
                              ref_text)
