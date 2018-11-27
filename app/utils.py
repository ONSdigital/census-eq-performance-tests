import os
import random
import re
import time

import backoff

r = random.Random()


class QuestionnaireMixins:
    client = None
    csrftoken = None

    def fill_in_page(self, url, name, data, user_wait_time=None):
        # always use the last part of the url as the name
        assert url.endswith(name), f'{url} does not end with {name}'

        group_instance = _extract_group_instance(url)
        if group_instance is not None:
            name = f'/{group_instance}{name}'

        self.get(url, name=name)

        response = self.post(url, data=data, name=name)

        if response.status_code != 302:
            raise Exception(f'Got a non-302 ({response.status_code}) back when posting page: {url}')

        redirect_location = response.headers['Location']

        if user_wait_time is None:
            user_wait_time = int(os.getenv('USER_WAIT_TIME_SECONDS', 15))

        time.sleep(r.randrange(user_wait_time, user_wait_time+5))

        return redirect_location

    @backoff.on_predicate(backoff.constant, lambda res: res.status_code == 0, interval=5)
    def get(self, *args, **kwargs):
        allow_redirects = kwargs.pop('allow_redirects', False)

        response = self.client.get(allow_redirects=allow_redirects, *args, **kwargs)
        if response.content:
            self.csrftoken = _extract_csrf_token(response.content.decode('utf8'))
        return response

    @backoff.on_predicate(backoff.constant, lambda res: res.status_code == 0, interval=5)
    def post(self, *args, **kwargs):
        data = kwargs.pop('data', {})
        allow_redirects = kwargs.pop('allow_redirects', False)

        data['csrf_token'] = self.csrftoken
        response = self.client.post(allow_redirects=allow_redirects, data=data, *args, **kwargs)
        return response


CSRF_REGEX = re.compile(r'<input id="csrf_token" name="csrf_token" type="hidden" value="(.+?)">')
def _extract_csrf_token(html):
    match = CSRF_REGEX.search(html)
    if match:
        return match.group(1)


GROUP_INSTANCE_REGEX = re.compile(r'/questionnaire/census/household/[\w-]+/[\w-]+/(\d)+/[\w-]+')
def _extract_group_instance(url):
    match = GROUP_INSTANCE_REGEX.search(url)
    if match:
        return match.group(1)


def chain_page_calls(first_fn_url, *page_call_fns):
    last_url = first_fn_url
    for fn in page_call_fns:
        last_url = fn(last_url)

    return last_url
