#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from unittestzero import Assert
import pytest
from bs4 import BeautifulSoup
import requests

@pytest.mark.skip_selenium
@pytest.mark.nondestructive
class TestSnippets:

    test_data = [
        ('/1/Firefox/default/default/default/en-US/release/default/default/default/'),
        ('/1/Firefox/default/default/default/en-US/aurora/default/default/default/'),
        ('/1/Firefox/default/default/default/en-US/beta/default/default/default/')]

    _user_agent_firefox = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:10.0.1) Gecko/20100101 Firefox/10.0.1'

    def _get_redirect(self, url, user_agent=_user_agent_firefox, locale='en-US'):

        headers = {'user-agent': user_agent,
                   'accept-language': locale}

        # verify=False ignores invalid certificate
        return requests.get(url, headers=headers, verify=False, timeout=5)

    def assert_valid_url(self, url, path, user_agent=_user_agent_firefox, locale='en-US'):
        """Checks if a URL returns a 200 OK response."""
        headers = {'user-agent': user_agent,
                   'accept-language': locale}

        # HEAD doesn't return page body.
        r = requests.head(url, headers=headers, timeout=5, allow_redirects=True, verify=False)
        return Assert.equal(r.status_code, requests.codes.ok,
                            'Bad URL %s found in %s' % (url, path))

    def _parse_response(self, content):
        return BeautifulSoup(content)

    @pytest.mark.parametrize(('path'), test_data)
    def test_snippets_present(self, mozwebqa, path):
        full_url = mozwebqa.base_url + path

        r = self._get_redirect(full_url)
        Assert.equal(r.status_code, requests.codes.ok, "URL %s failed with status code: %s" %(full_url, r.status_code))

        soup = self._parse_response(r.content)
        snippets = soup.select("div.snippet")

        Assert.greater(len(snippets), 0, "No snippets found")

    @pytest.mark.parametrize(('path'), test_data)
    def test_all_links(self, mozwebqa, path):
        full_url = mozwebqa.base_url + path

        soup = self._parse_response(self._get_redirect(full_url).content)
        snippet_links = soup.select("a")

        Assert.greater(len(snippet_links), 0, "No links found")

        for link in snippet_links:
            self.assert_valid_url(link['href'], path)
