##########
##
##  SPDX-License-Identifier: MIT
##
##  Copyright (c) 2017-2022 James M. Putnam <putnamjm.design@gmail.com>
##
##########

##########
##
## server environment
##
###########
"""NDEF server

Classes:

    Server

Functions:

    media_status()

Misc variables:

    _conf_dict
    _event
    _nfclib
"""

import base64
import json
import time
import os

from datetime import datetime
from time import localtime, strftime, mktime
from threading import Timer

from event import Event
from nfclib import NfcLib

class RepeatTimer(Timer):
    def __init__(self, interval, f, *args, **kwargs):
        self.interval = interval
        self.f = f
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def callback(self):
        self.f(*self.args, **self.kwargs)
        self.start()

    def cancel(self):
        self.timer.cancel()

    def start(self):
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()

class Server:
    """utilities
    """

    VERSION = '0.0.1'
    media_status = None

    _media_status = None
    _conf_dict = None
    _event = None
    _nfclib = None
    _state = None
    _state_machine = None
    _tick_event = None
    _sec_timer = None
    _app = None
    
    def ndef_format(self, record):
        # print(type(record))
        # print(vars(record))

        json = self._nfclib.to_json(record)
        if hasattr(record, '_iri'):
            # return ['URI', 'uri', json['_iri']]
            return ['URI', json['_iri'].split(':')[0], json['_iri']]
        if hasattr(record, '_data'):
            data = json['_data']
            info = (data[:20] + '...') if len(data) > 20 else data
            return ['DATA', json['_type'], info]

        if hasattr(record, '_text'):
            return ['TEXT', 'text', json['_text']]

        return [None, None, None]
    
    def media_status(self):
        return self._nfclib.media_status()

    def to_json(self, records):
        return json.dumps([self._nfclib.to_json(x) for x in records])

    def write_json(self, records, fn):
        data = [self._nfclib.to_json(x) for x in records]
        with open('user.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # simple state machine
    def state_machine(self, event):
        key = list(event.keys())[0]
        # print(self._state, end=" ")
        # print(event)
        self._state_machine[self._state][key][0](self)
        self._state = self._state_machine[self._state][key][1]

    # main event loop
    def event_loop(self):
        while True:
            event = self._event.wait()
            self.state_machine(event)

    def __init__(self, App, conf_dict, verbose):
        """initialize the server module
        """

        self._app = App
        self._conf_dict = conf_dict

        self._state = 'open'
        self._state_machine = {
            'open': dict([
                ( 'connect',     [ lambda event: None, 'connect' ] ),
                ( 'disconnect',  [ lambda event: None, 'open' ] ),
                ( 'tick',        [ lambda event: self._nfclib.connect(), 'connect' ] ),
            ]),
            'connect': dict([
                ( 'connect',     [ lambda event: None, 'connect' ] ),
                ( 'disconnect',  [ lambda event: None, 'open' ] ),     
                ( 'tick',        [ lambda event: self._nfclib.disconnect(), 'connect' ] ),
            ]),
        }

        self._event = Event()
        self._tick_event = self._event.event('tick', None)
        
        self._nfclib = NfcLib(self._event, conf_dict, verbose)
        
        # seconds timer
        self._sec_timer = RepeatTimer(1, lambda: self._event.send(self._tick_event))
        self._sec_timer.start()
        
