# tests.test_shared

from __future__ import unicode_literals
import gzip
import tests
import yvs.shared as yvs
import nose.tools as nose
from StringIO import StringIO
from mock import Mock, NonCallableMock, patch

with open('tests/html/psa.23.html') as html_file:
    html_content = html_file.read()
    patch_urlopen = patch(
        'urllib2.urlopen', return_value=NonCallableMock(
            read=Mock(return_value=html_content)))


def set_up():
    patch_urlopen.start()
    tests.set_up()


def tear_down():
    patch_urlopen.stop()
    tests.tear_down()


@nose.with_setup(set_up, tear_down)
@patch('urllib2.Request')
def test_get_url_content(request):
    """should fetch uncompressed URL content"""
    url = 'https://www.bible.com/bible/59/psa.23'
    yvs.get_url_content(url)
    request.assert_called_once_with(url, headers={
        'User-Agent': 'YouVersion Suggest',
        'Accept-Encoding': 'gzip, deflate'
    })


@nose.with_setup(set_up, tear_down)
@patch('urllib2.Request')
def test_get_url_content_compressed(request):
    """should automatically decompress compressed URL content"""
    url = 'https://www.bible.com/bible/59/psa.23'
    gzip_buf = StringIO()
    with gzip.GzipFile(fileobj=gzip_buf, mode='wb') as gzip_file:
        gzip_file.write(html_content)
    gzipped_content = gzip_buf.getvalue()
    response_mock = NonCallableMock(
        read=Mock(return_value=gzipped_content),
        info=Mock(return_value=NonCallableMock(
            get=Mock(return_value='gzip'))))
    with patch('urllib2.urlopen', return_value=response_mock):
        url_content = yvs.get_url_content(url).encode('utf-8')
        nose.assert_equal(url_content, html_content)
