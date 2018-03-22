import asyncio
import gzip
from io import TextIOWrapper
import json
import random
import tempfile
from yarl import URL

from .utils import repo_path


def _tests(filename, *test_names):
    for test_name in test_names:
        yield Test(filename, test_name)


class Suite:

    def __init__(self):
        self.tests = [

            *_tests('tests/test_microwave_sanity.py', 'test_sanity', 'test_power_display', 'test_status_button'),
            *_tests('tests/test_cooking_power.py', 'test_cooking_power_default', 'test_cooking_power_minimum', 'test_cooking_power_maximum'),
            Test('tests/test_abuse.py', 'test_plug_pull_out', failrate=0.1),
        ]

class Test:

    def __init__(self, filename, name, failrate=0):
        self.filename = filename
        self.name = name
        self.failrate = failrate

    async def sleep(self):
        await asyncio.sleep(0.1)

    async def run(self, client, session_id):
        test_id = (await client.api.report_test_start(
            session_id=session_id,
            name=self.name, file_name=self.filename))['id']
        await self.sleep()
        if self.failrate and random.random() < self.failrate:
            await self._add_error(client, test_id)
        await client.api.report_test_end(id=test_id)

    async def _add_error(self, client, test_id):

        with open(repo_path('testbed/tracebacks/tb1.json')) as f:
            traceback_raw = f.read()

        traceback_raw = traceback_raw.replace('__TEST_FILENAME__', self.filename).replace('__TEST_NAME__', self.name)

        result = await client.api.add_error(message="AssertionError", exception_type="AssertionError", test_id=test_id)
        url = client.url / f'rest/errors/{result["id"]}/traceback'

        with tempfile.TemporaryFile(mode='w+b') as traceback_file:
            try:
                with gzip.GzipFile(fileobj=traceback_file, mode='w+b') as compressed_file_raw:
                    with TextIOWrapper(compressed_file_raw) as compressed_file:
                        compressed_file.write(traceback_raw)
            except IOError:
                _logger.error('Unable to compress traceback on disk. Reporting error without traceback', exc_info=True)
                return

            traceback_file.seek(0)

            async with client.api.session.put(url, data=traceback_file) as resp:
                assert resp.status == 200
