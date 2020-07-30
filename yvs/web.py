#!/usr/bin/env python3
# coding=utf-8

import urllib.request
from gzip import GzipFile
from io import BytesIO

# The user agent used for HTTP requests sent to the YouVersion website
USER_AGENT = 'YouVersion Suggest'
# The number of seconds to wait before timing out an HTTP request connection
REQUEST_CONNECTION_TIMEOUT = 5


# Retrieves HTML contents of the given URL as a Unicode string
def get_url_content(url):

    request = urllib.request.Request(url, headers={
        'User-Agent': USER_AGENT,
        'Accept-Encoding': 'gzip, deflate'
    })
    response = urllib.request.urlopen(request, timeout=REQUEST_CONNECTION_TIMEOUT)
    url_content = response.read()

    # Decompress response body if gzipped
    if response.info().get('Content-Encoding') == 'gzip':
        str_buf = BytesIO(url_content)
        with GzipFile(fileobj=str_buf, mode='rb') as gzip_file:
            url_content = gzip_file.read().decode('utf-8')

    return url_content
