from aiocache import cached
import importlib
from os import listdir
from os.path import dirname, basename

import rates_lists


@cached(60*60)
async def rates_list():
    result = []
    rates_lists_dir = dirname(rates_lists.__file__)
    module_files = listdir(rates_lists_dir)
    for module_file in module_files:
        if not module_file.endswith('.py') or module_file.endswith('__init__.py'):
            continue

        module = importlib.import_module(basename(rates_lists_dir) + '.' + module_file[:-3])
        result += await module.rates_list()

    return result