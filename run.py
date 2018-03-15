#! /usr/bin/env fades -d slash -d backslash -d yarl -d requests
import asyncio
import aiohttp # fades
import click # fades
import functools
import logbook # fades

from testbed import config
from testbed.users import get_user

_logger = logbook.Logger(__name__)


def coro(func):
    @functools.wraps(func)
    def callable(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return callable


@click.command()
@click.option('--backslash-url', default='http://127.0.0.1:8800')
@click.option('--num-users', type=int, default=1)
@coro
async def main(backslash_url, num_users):
    logbook.StderrHandler(level='DEBUG').push_application()
    config.root.backslash_url = backslash_url
    users = [get_user() for _ in range(num_users)]

    await asyncio.gather(*[user.run() for user in users])


if __name__ == '__main__':
    main()
