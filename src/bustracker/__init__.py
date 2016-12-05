#!/usr/bin/env python

import logging

from bustracker.buses import BusTracker
from flask import Flask, jsonify
from flask_ask import Ask, statement

from . import env

LOG = logging.getLogger('my_next_bus')


class MyAppConfiguration(env.Config):
    api_key = env.EnvVar(env_var_name='BUSTRACKER_API_KEY')
    bus_stop_id = env.EnvVar()
    debug = env.BoolVar(default=False)

    def __str__(self):
        return """
api_key: {api_key}
bus_stop_id: {bus_stop_id}
debug: {debug}""".format(api_key=self.api_key, bus_stop_id=self.bus_stop_id, debug=self.debug)


config = MyAppConfiguration()


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
ask = Ask(app, '/alexa')

bus_tracker = BusTracker(config.api_key)


@ask.intent('BusTracker')
def alexa():
    message = to_human(bus_tracker.get_times(config.bus_stop_id))
    LOG.debug(message)
    return statement(message).simple_card("Bus Times", message)


def main():
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=config.debug)


if __name__ == "__main__":
    main()
