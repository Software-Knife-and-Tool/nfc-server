###
#
# ndef-server main
#
###
import gc
import time
import os
import json

from datetime import datetime

from bottle import template, route, run, static_file
from threading import Thread

import jyserver.Bottle as js

from server import Server
from event import Event

_server = None

@js.use
class App():
    # templating
    def expand_template(self, fn):
        with open('/home/putnamjm/ndef-server/static/template/' + fn) as f: html = f.read()
        records = [_server.ndef_format(x) for x in _server.media_status()['records']]
        return template(html, records=records)

    # buttons
    def rewrite(self):
        print("rewrite me")

    def edit(self):
        print("edit")

    def to_json(self):
        _server.write_json(_server.media_status(None)['records'], './user.json')

    def reboot(self):
        print("say goodnight, gracie")
        os.system("sudo reboot");

    @js.task
    def update(self):
        self.js.dom.version.innerHTML = '0.0.1'
        self.js.dom.media_status.innerHTML = _server.media_status()['media']
        self.js.dom.nrecords.innerHTML = str(len(_server.media_status()['records']))
        self.js.dom.reader.innerHTML = _server.media_status()['reader']
        self.js.dom.records.innerHTML = self.expand_template('table.tpl')

@route('/')
def static():
    with open('/home/putnamjm/ndef-server/static/html/index.html') as f: html = f.read()

    App.update()
    return App.render(html)

@route('/records')
def static():

    App.update()
    return _server.to_json(_server.media_status()['records'])

@route('/records/edit')
def static():
    with open('/home/putnamjm/ndef-server/static/html/edit.html') as f: html = f.read()

    return App.render(html)

# Static Routes
@route("/static/css/<filepath:re:.*\.css>")
def css(filepath):
    return static_file(filepath, root="static/css")

@route("/static/font/<filepath:re:.*\.(eot|otf|svg|ttf|woff|woff2?)>")
def font(filepath):
    return static_file(filepath, root="static/font")

@route("/static/image/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
    return static_file(filepath, root="static/image")

@route("/static/js/<filepath:re:.*\.js>")
def js(filepath):
    return static_file(filepath, root="static/js")

# @route('/<dir>/<file>')
# def static(dir, file):
#    return static_file(os.path.join(dir, file), root='/home/putnamjm/ndef-server/static')
#
# @route('/static/<dir>/<file>')
# def static(dir, file):
#    return static_file(os.path.join(dir, file), root='/home/putnamjm/ndef-server/static')

# state
up_since = datetime.now()

conf_dict = []
with open(os.path.join(os.path.dirname(__file__), './conf.json'), 'r') as file:
    conf_dict = json.load(file)

_server = Server(App, conf_dict, False)
event_thread = Thread(group=None, target=_server.event_loop, name=None, args=(), kwargs={})

event_thread.start()

run(host='vortex', port=8080, debug=False, quiet=True)
