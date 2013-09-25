#!/usr/bin/env python
import sys


def runtests(args=None):
    import pytest
    args = args or []

    sys.exit(pytest.main(args))


if __name__ == '__main__':
    runtests(sys.argv)
