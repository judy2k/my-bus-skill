import hashlib
from datetime import datetime

import requests
from kylie import Model, Attribute, Relation


class TimeData(Model):
    minutes = Attribute()


class BusTimes(Model):
    service_number = Attribute('mnemoService')
    times = Relation(TimeData, struct_name='timeDatas', sequence=True)


class ResponseObject(Model):
    bus_times = Relation(BusTimes, struct_name='busTimes', sequence=True)


def parse_response(data):
    result = {}
    ro = ResponseObject.deserialize(data)
    for bus in ro.bus_times:
        for time in bus.times:
            result.setdefault(bus.service_number, []).append(time.minutes)
    return result


class BusTracker(object):
    def __init__(self, api_key):
        self._api_key = api_key

    def get_times(self, stop_number):
        now = datetime.utcnow().strftime('%Y%m%d%H')
        m = hashlib.md5()
        m.update(self._api_key.encode('ascii'))
        m.update(now.encode('ascii'))
        params = {
            'module': 'json',
            'key': m.hexdigest(),
            'function': 'getBusTimes',
            'stopId': stop_number,
        }
        data = requests.get('http://ws.mybustracker.co.uk/', params=params).json()
        return parse_response(data)