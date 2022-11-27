##########
##
##  SPDX-License-Identifier: MIT
##
##  Copyright (c) 2017-2022 James M. Putnam <putnamjm.design@gmail.com>
##
##########

##########
##
## NFC Tool
##
###########

from threading import Timer

import time
import json
import os
import sys
import signal

from server import Server

class NfcTool:
    """NfcTool class
    """
    
    VERSION = '0.0.1'

    _server = None
    _conf_dict = None

    def version(self):
        return self.VERSION

    def __init__(self, conf_dict):

        _conf_dict = []
        with open(os.path.join(os.path.dirname(__file__), './etc/conf.json'), 'r') as file:
            _conf_dict = json.load(file)

        self._server = Server(_conf_dict)

# main
if __name__ == '__main__':

    # this is for debugging
    signal.signal(signal.SIGINT, lambda s, args : os._exit(0))
    signal.signal(signal.SIGTERM, lambda s, args : os._exit(0))

    _conf_dict = []
    with open(os.path.join(os.path.dirname(__file__), './conf.json'), 'r') as file:
        _conf_dict = json.load(file)

    _server = Server(_conf_dict, True)
