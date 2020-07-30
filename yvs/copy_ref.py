#!/usr/bin/env python3
# coding=utf-8

import json
import sys

import yvs.core as core
import yvs.cache as cache
import yvs.web as web
from yvs.yv_parser import YVParser


# An HTML parser which receives HTML from the page for a YouVersion
# Bible reference and parses it to construct a shareable plain text reference
class ReferenceParser(YVParser):

    # Elements that should be surrounded by blank lines
    block_elems = {'b', 'p', 'm'}
    # Elements that should trigger a line break
    break_elems = {'li1', 'q1', 'q2', 'qc', 'qm1', 'qm2'}

    # Associates the given reference object with this parser instance
    def __init__(self, ref, include_verse_numbers=False):
        YVParser.__init__(self)
        if 'verse' in ref:
            # If reference is a verse or verse range, set the correct range of
            # verses to copy
            self.verse_start = ref['verse']
            self.verse_end = ref.get('endverse', self.verse_start)
        else:
            # Otherwise, assume reference is a chapter
            self.verse_start = 1
            self.verse_end = None
        self.include_verse_numbers = include_verse_numbers

    # Resets parser variables (implicitly called when parser is instantiated)
    def reset(self):
        YVParser.reset(self)
        self.depth = 0
        self.in_block = False
        self.in_verse = False
        self.in_verse_label = False
        self.in_verse_content = False
        self.in_verse_note = False
        self.block_depth = 0
        self.verse_depth = 0
        self.label_depth = 0
        self.content_depth = 0
        self.verse_nums = []
        self.content_parts = []

    # Returns True if parser is currently within the a verse to include
    # (otherwise, returns False)
    def is_in_verse(self):
        return any(self.in_verse and
                   (verse_num >= self.verse_start and
                    (not self.verse_end or verse_num <= self.verse_end))
                   for verse_num in self.verse_nums)

    # Returns True if parser is currently within the content of a verse to
    # include
    def is_in_verse_content(self):
        return (self.is_in_verse() and self.in_verse_content
                and not self.in_verse_note)

    # Returns True if parser is currently within the label of a verse to
    # include (otherwise, returns False)
    def is_in_verse_label(self):
        return (self.is_in_verse() and self.include_verse_numbers and
                self.in_verse_label and not self.in_verse_note)

    # Detects the start of blocks, breaks, verses, and verse content
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # Keep track of element depth throughout entire document
        self.depth += 1
        if 'class' in attrs:
            elem_class = attrs['class']
            elem_class_names = elem_class.split(' ')
            # Detect paragraph breaks between verses
            if elem_class in self.block_elems:
                self.in_block = True
                self.block_depth = self.depth
                self.content_parts.append('\n\n')
            # Detect line breaks within a single verse
            if elem_class in self.break_elems:
                self.content_parts.append('\n')
            # Detect beginning of a single verse (may include footnotes)
            if 'verse' in elem_class_names:
                self.in_verse = True
                self.verse_depth = self.depth
                self.verse_nums = [int(class_name[1:])
                                   for class_name in elem_class_names[1:]]
            # Detect label containing the associated verse number(s)
            if elem_class == 'label':
                self.in_verse_label = True
                self.label_depth = self.depth
            # Detect beginning of verse content (excludes footnotes)
            if elem_class == 'content':
                self.in_verse_content = True
                self.content_depth = self.depth
            # Detect footnotes and cross-references
            if 'note' in elem_class:
                self.in_verse_note = True
                self.note_depth = self.depth

    # Detects the end of blocks, breaks, verses, and verse content
    def handle_endtag(self, tag):
        if self.in_block and self.depth == self.block_depth:
            self.in_block = False
            self.content_parts.append('\n')
        elif self.in_verse and self.depth == self.verse_depth:
            self.in_verse = False
        elif self.in_verse_label and self.depth == self.label_depth:
            self.in_verse_label = False
        elif self.in_verse_content and self.depth == self.content_depth:
            self.in_verse_content = False
        elif self.in_verse_note and self.depth == self.note_depth:
            self.in_verse_note = False
        self.depth -= 1

    # Handles verse labels and content
    def handle_data(self, data):
        if self.is_in_verse_label():
            self.content_parts.append(' {} '.format(data.strip()))
        if self.is_in_verse_content():
            self.content_parts.append(data)


# Retrieves the UID of the chapter to which this reference belongs
def get_ref_chapter_uid(ref):

    return '{version}/{book}.{chapter}'.format(
        version=ref['version_id'],
        book=ref['book_id'],
        chapter=ref['chapter'])


# Retrieves HTML for of the chapter to which the reference belongs
def get_chapter_html(ref):

    chapter_uid = get_ref_chapter_uid(ref)
    url = core.get_ref_url(ref_uid=chapter_uid)

    entry_key = '{}.html'.format(chapter_uid)
    chapter_html = cache.get_cache_entry_content(entry_key)
    if not chapter_html:
        chapter_html = web.get_url_content(url)
        cache.add_cache_entry(entry_key, chapter_html)

    return chapter_html


# Parses actual reference content from chapter HTML
def get_ref_content(ref, ref_format, include_verse_numbers):

    chapter_html = get_chapter_html(ref)
    parser = ReferenceParser(ref, include_verse_numbers)
    parser.feed(chapter_html)
    # Format reference content by removing superfluous whitespace and such
    ref_content = core.normalize_ref_content(
        ''.join(parser.content_parts))

    if ref_content:
        copied_content = ref_format.format(
            name=core.get_basic_ref_name(ref),
            version=ref['version'],
            content=ref_content,
            url=core.get_ref_url(ref['uid']))
        return copied_content
    else:
        return ''


# Retrieves reference content using the given reference object and preferences
def get_copied_ref_from_object(ref, user_prefs):
    return get_ref_content(
        ref,
        ref_format=user_prefs['refformat'],
        include_verse_numbers=user_prefs['versenumbers'])


# Retrieves entire reference (header and content) to be copied
def get_copied_ref(ref_uid):

    user_prefs = core.get_user_prefs()
    ref = core.get_ref(ref_uid, user_prefs)
    return get_copied_ref_from_object(ref, user_prefs)


def main(ref_uid):

    user_prefs = core.get_user_prefs()
    ref = core.get_ref(ref_uid, user_prefs)
    print(json.dumps({
        'alfredworkflow': {
            'arg': ref_uid,
            'variables': {
                'copied_ref': get_copied_ref_from_object(ref, user_prefs),
                'full_ref_name': core.get_full_ref_name(ref)
            }
        }
    }))


if __name__ == '__main__':
    main(sys.argv[1])
