import pytest

import bustracker


def test_filter_times():
    bustracker.fil

def test_to_human():
    ''' Ensure short times are removed.
    '''
    assert bustracker.to_human({
        '31': [2, 4, 8]
    }) == "The next 31 is in 4 minutes."