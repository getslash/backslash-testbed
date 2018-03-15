import asyncio

class Suite:

    def __init__(self):
        self.tests = [

            Test('tests/test_microwave_sanity', 'test_sanity')
        ]

class Test:

    def __init__(self, filename, name):
        self.filename = filename
        self.name = name

    async def sleep(self):
        await asyncio.sleep(0.1)
