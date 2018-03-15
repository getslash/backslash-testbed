import sys

from pathlib import Path


def env_binary(binary_name):
    return Path(sys.executable).resolve().parent / binary_name

def repo_path(relpath):
    return Path(__file__).parent.parent.resolve() / relpath
