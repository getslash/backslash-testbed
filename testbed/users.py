import random
import json
import logbook
import requests
from pathlib import Path
from yarl import URL

from . import config
from .client import BackslashClient
from .suite import Suite

_USER_EMAILS = ['john@getslash.org', 'roy@getslash.org']
_available = list(_USER_EMAILS)

_HOSTS = [f'run-machine-{i:02}' for i in range(5)]

_logger = logbook.Logger(__name__)


def get_user():
    backslash_url = URL(config.root.backslash_url)
    email = _available.pop()
    session = requests.Session()

    session.post(backslash_url / 'login', json={'username': email, 'password': ''}).raise_for_status()
    token = _get_user_token(session, backslash_url, email)

    _logger.debug('Got user token for {}: {}', email, token)

    return User(email, token)

def _get_user_token(session, backslash_url, email):
    token = _get_existing_token(email)
    if token is None:
        resp = session.get(backslash_url / 'runtoken' / 'request' / 'new')
        resp.raise_for_status()
        json = resp.json()
        request_id = json['complete'].split('/')[-2]
        url = json['url']

        session.post(backslash_url / 'runtoken' / 'request' / request_id / 'complete', json={}).raise_for_status()

        resp = session.get(url)
        resp.raise_for_status()
        token = resp.json()['token']
        _save_existing_token(email, token)
    return token

_TOKEN_STORAGE = Path('~/.config/backslash-testbed/tokens.json').expanduser().resolve()

def _get_existing_token(email):
    if not _TOKEN_STORAGE.exists():
        return None
    print(_TOKEN_STORAGE)
    with _TOKEN_STORAGE.open() as f:
        return json.load(f).get(email, None)

def _save_existing_token(email, token):
    if _TOKEN_STORAGE.exists():
        with _TOKEN_STORAGE.open() as f:
            existing = json.load(f)
    else:
        existing = {}

    existing[email] = token
    if not _TOKEN_STORAGE.parent.exists():
        _TOKEN_STORAGE.parent.mkdir(parents=True)
    with _TOKEN_STORAGE.open('w') as f:
        json.dump(existing, f)


class User:

    def __init__(self, email, token):
        self.client = BackslashClient(URL(config.root.backslash_url), token)

    async def run(self):
        while True:
            suite = Suite()
            session_id = await self._session_start(suite)
            for test in suite.tests:
                await self._run_test(session_id, test)
            await self._session_end(session_id)

    async def _session_start(self, suite):
        result = await self.client.api.report_session_start(
            hostname=random.choice(_HOSTS),
            ttl_seconds=24 * 60 * 60 * 7,
            keepalive_interval=60,
        )
        return result['id']

    async def _run_test(self, session_id, test):
        test_id = (await self.client.api.report_test_start(
            session_id=session_id,
            name=test.name, file_name=test.filename))['id']
        await test.sleep()
        await self.client.api.report_test_end(id=test_id)


    async def _session_end(self, session_id):
        await self.client.api.report_session_end(id=session_id)
