import atb
import numpy as np
from gl_utils import draw_gl_polyline_norm
from ctypes import c_float,c_int,create_string_buffer

import cv2
import zmq
from plugin import Plugin

class Pupil_Server(Plugin):
    """Calibration results visualization plugin"""
    def __init__(self, g_pool, atb_pos=(500,300)):
        Plugin.__init__(self)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.address = create_string_buffer("tcp://127.0.0.1:5000",512)
        self.set_server(self.address)

        help_str = "Pupil Message server: Using ZMQ and the *Publish-Subscribe* scheme"

        self._bar = atb.Bar(name = self.__class__.__name__, label='Server',
            help=help_str, color=(50, 50, 50), alpha=100,
            text='light', position=atb_pos,refresh=.3, size=(300, 100))
        self._bar.define("valueswidth=170")
        self._bar.add_var("server address",self.address, getter=lambda:self.address, setter=self.set_server)
        self._bar.add_button("close", self.close, key="x", help="close calibration results visualization")

    def set_server(self,address):
        try:
            self.socket.bind(address.value)
            self.address.value = address.value
        except zmq.ZMQError:
            print "Could not set Socket."

    def update(self,img,recent_pupil_positions):
        for p in recent_pupil_positions:
            msg = "Pupil"
            for key,value in p.iteritems():
                msg += key+":"+str(value)
            self.socket.send( msg )

    def close(self):
        self.alive = False

    def cleanup(self):
        """gets called when the plugin get terminated.
           either volunatily or forced.
        """
        self._bar.destroy()
        del self.context
