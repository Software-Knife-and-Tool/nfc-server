##########
##
##  SPDX-License-Identifier: MIT
##
##  Copyright (c) 2017-2022 James M. Putnam <putnamjm.design@gmail.com>
##
##########

##########
##
## NFC reader controller
##
###########
"""Manage reader device

Classes:

    NfcLib

"""

import json
import time
import os
import base64

from pprint import pprint

import nfc
from nfc.clf import RemoteTarget

from event import Event

class NfcLib:
    """NFC controller utilities
    """

    _event = None
    _conf_dict = None
    _clf = None
    _target = None
    _tags = None

    _verbose = None
    _status = None

    _connect_event = None
    _disconnect_event = None

    _rdwr_options = None
    
    def to_json(self, record):
        if hasattr(record, '_text'):
            return vars(record)

        if hasattr(record, '_iri'):
            return vars(record)
        
        if hasattr(record, '_data'):
            b64_data = str(base64.b64encode(record._data))

            rec = '{ "_data": "' + b64_data + '", "_name": "' + record._name + '", "_type": "' + record._type + '" }'
            return json.loads(rec)
            
        return None

    def media_status(self):
        return self._status

    def disconnect(self):
        if not self._clf.sense(*[nfc.clf.RemoteTarget(target) for target in self._rdwr_options['targets']]):
            self._status = { 'reader': '',
                             'target': '',
                             'media': '',
                             'records': '',
                            }

            self._event.send(self._disconnect_event)

    def connect(self):
        started = time.time()
        self._clf.connect(rdwr=self._rdwr_options, terminate=lambda: time.time() - started > .5)

    def _on_connect(self, tags):
        self._target = self._clf.sense(*[nfc.clf.RemoteTarget(target) for target in self._rdwr_options['targets']])
        self._tags = tags
        
        if self._verbose:
            pprint(vars(self._clf), indent=2)
            pprint(vars(self._target), indent=2)
            # pprint(vars(self._tags), indent=2)
            # pprint(vars(self._tags.ndef), indent=2)
            # pprint(self._tags.ndef.records, indent=2)

            for record in self._tags.ndef.records:
                print(self.to_json(record))

        self._status = { 'reader': str(self._clf),
                         'target': str(self._target),
                         'media': self._tags._product,
                         'records': self._tags.ndef.records,
                        }

        self._event.send(self._connect_event)
        return False

    def __init__(self, event, conf_dict, verbose):
        """initialize the NFC module
        """

        self._verbose = verbose
        self._event = event
        self._conf_dict = conf_dict;

        self._discover_event = self._event.event('discover', None)
        self._connect_event = self._event.event('connect', None)
        self._disconnect_event = self._event.event('disconnect', None)
        
        self._clf = nfc.ContactlessFrontend('usb')

        self._status = { 'reader': '',
                         'target': '',
                         'media': '',
                         'records': '',
                        }

        self._rdwr_options = {
            'targets': ('106A', '106B', '212F'),
            'on-connect': self._on_connect,
        }

