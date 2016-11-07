import pytest

import bustracker

def test_to_human():
    assert bustracker.to_human({
        '31': [2, 4, 8]
    }) == "The next 31 bus is in 2 minutes"