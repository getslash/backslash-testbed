import aiohttp
import functools


class BackslashClient:

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.api = API(self)


class API:

    def __init__(self, client):
        self.client = client
        self._session = aiohttp.ClientSession(
            headers={
                'X-Backslash-run-token': self.client.token,
                'X-Backslash-client-version': '2.33.1',
            })

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(attr)
        return functools.partial(self.call, attr)

    async def call(self, api_name, **params):
        async with self._session.post(self.client.url / 'api' / api_name, json=params) as response:
            if response.status != 200:
                text = await response.text()
                raise APIException(f'API {api_name!r} failed with {response.status}: {text}')
            return (await response.json())['result']

class APIException(Exception):
    pass
