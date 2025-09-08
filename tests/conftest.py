"""Test configuration to handle async test functions without external plugins."""

import inspect
import pytest


def pytest_collection_modifyitems(config, items):
    """Automatically mark async tests to run with anyio."""
    for item in items:
        test_func = getattr(item, "obj", None)
        if test_func and inspect.iscoroutinefunction(test_func):
            item.add_marker(pytest.mark.anyio)


def pytest_pyfunc_call(pyfuncitem):
    """Run async test functions via ``asyncio.run`` if no plugin handles them."""

    test_func = getattr(pyfuncitem, "function", None)
    if test_func and inspect.iscoroutinefunction(test_func):
        import asyncio

        asyncio.run(test_func(**pyfuncitem.funcargs))
        return True
