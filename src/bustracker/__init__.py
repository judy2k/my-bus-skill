#!/usr/bin/env python

from datetime import datetime
import hashlib
from os import getenv
import logging

import requests
from kylie import Model, Relation, Attribute
from flask import Flask, jsonify

from . import env

LOG = logging.getLogger('my_next_bus')

API_KEY = getenv('BUSTRACKER_API_KEY')
MY_BUS_STOP = getenv('BUS_STOP_ID')


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


def get_times(stop_number):
    now = datetime.utcnow().strftime('%Y%m%d%H')
    m = hashlib.md5()
    m.update(API_KEY.encode('ascii'))
    m.update(now.encode('ascii'))
    params = {
        'module': 'json',
        'key': m.hexdigest(),
        'function': 'getBusTimes',
        'stopId': stop_number,
    }
    data = requests.get('http://ws.mybustracker.co.uk/', params=params).json()
    return parse_response(data)


def filter_bus_times(bus_times):
    acceptable_bus_times = {
        bus: [t for t in times if t > 2] for (bus, times) in bus_times.items()
        }
    return {
        bus: times for (bus, times) in acceptable_bus_times.items() if times
        }


def to_human(bus_times):
    # <say-as interpret-as="spell-out">X</say-as>31
    bus_times = filter_bus_times(bus_times)
    buses = [(bus, times[0]) for (bus, times) in bus_times.items() if bus in ('31', 'X31', 'N31')]
    buses.sort(key=lambda b: b[1])
    if buses:
        return ''.join(
            "The next {bus} is in {time} minutes. ".format(bus=bus, time=time) for (bus, time) in buses
        ).strip()
    else:
        return 'There are no buses. You may need to get a taxi.'


app = Flask(__name__)


@app.route("/alexa", methods=['POST'])
def alexa():
    message = to_human(get_times(MY_BUS_STOP))
    LOG.debug(message)
    return jsonify({
        "version": "1.0",
        "response": {
            "outputSpeech": {"type": "PlainText", "text": message},
            "card": {
                "type": "Simple",
                "title": "Next Bus",
                "content": to_human(get_times(MY_BUS_STOP)),
            }
        }
    })


def main():
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True)


if __name__ == "__main__":
    main()
